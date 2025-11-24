import random
import time
import threading
from core.emotion_system import Emotion, EmotionSystem

class PersonalityEngine:
    def __init__(self):
        self.emotion_system = EmotionSystem()
        self.last_interaction_time = time.time()
        self.interaction_count = 0
        self.user_preferences = {}
        self.memory_events = []
        self._lock = threading.Lock()
        
        # Personality traits (0.0 to 1.0)
        self.personality_traits = {
            'friendliness': 0.8,
            'curiosity': 0.7,
            'cautiousness': 0.4,
            'playfulness': 0.6,
            'energy_level': 0.7
        }
    
    def set_emotion(self, emotion_name, reason="", intensity=0.5):
        """Set robot emotion with reason"""
        with self._lock:
            self.emotion_system.set_emotion(emotion_name, reason, intensity)
            print(f"😊 Emotion: {emotion_name} (Intensity: {intensity:.1f}) - {reason}")
            
            # Record emotional event
            self._record_event('emotion_change', {
                'emotion': emotion_name,
                'reason': reason,
                'intensity': intensity
            })
    
    def get_current_emotion(self):
        """Get current emotion state"""
        return self.emotion_system.get_current_emotion()
    
    def get_emotion_intensity(self):
        """Get current emotion intensity"""
        return self.emotion_system.get_emotion_intensity()
    
    def update(self, stimuli=None):
        """Update personality based on environment and time"""
        current_time = time.time()
        time_since_interaction = current_time - self.last_interaction_time
        
        # Update emotion system
        self.emotion_system.update_emotion(stimuli)
        
        # Get bored if no interaction for a while
        if time_since_interaction > 60:  # 1 minute
            if random.random() < 0.1:  # 10% chance
                self.set_emotion("bored", "No interaction for a while", intensity=0.3)
        
        # Random mood shifts based on personality
        if random.random() < 0.02:  # 2% chance per update
            self._random_mood_shift()
        
        # Energy level affects behavior
        self._update_energy_level()
    
    def _random_mood_shift(self):
        """Randomly shift mood based on personality traits"""
        # Higher curiosity = more mood changes
        curiosity_factor = self.personality_traits['curiosity']
        if random.random() < curiosity_factor * 0.03:
            moods = ["happy", "curious", "bored", "excited", "playful"]
            weights = [0.3, 0.4, 0.1, 0.15, 0.05]  # Weighted by personality
            
            # Adjust weights based on traits
            weights[0] *= self.personality_traits['friendliness']  # Happy
            weights[1] *= self.personality_traits['curiosity']     # Curious
            weights[4] *= self.personality_traits['playfulness']   # Playful
            
            # Normalize weights
            total = sum(weights)
            weights = [w/total for w in weights]
            
            new_mood = random.choices(moods, weights=weights)[0]
            reasons = {
                "happy": "Feeling good today!",
                "curious": "I wonder what's around me...",
                "bored": "Nothing interesting happening",
                "excited": "So much to explore!",
                "playful": "I feel like having some fun!"
            }
            self.set_emotion(new_mood, reasons[new_mood], intensity=0.4)
    
    def _update_energy_level(self):
        """Update energy level based on activity and time"""
        current_time = time.time()
        time_since_interaction = current_time - self.last_interaction_time
        
        # Energy decreases when bored, increases with interaction
        if time_since_interaction > 120:  # 2 minutes
            self.personality_traits['energy_level'] = max(0.3, self.personality_traits['energy_level'] - 0.01)
        else:
            self.personality_traits['energy_level'] = min(1.0, self.personality_traits['energy_level'] + 0.02)
    
    def react_to_voice(self, text):
        """React to voice input"""
        with self._lock:
            self.last_interaction_time = time.time()
            self.interaction_count += 1
            
            # Record interaction
            self._record_event('voice_interaction', {
                'text': text,
                'timestamp': time.time()
            })
            
            # Simple voice reaction logic
            text_lower = text.lower()
            
            if any(word in text_lower for word in ["hello", "hi", "hey"]):
                self.set_emotion("happy", "Someone greeted me!", intensity=0.7)
                return "Hello! I'm VALSPY, your robot friend!"
            
            elif any(word in text_lower for word in ["how are you", "how do you feel"]):
                current_emotion = self.get_current_emotion()
                responses = {
                    "happy": "I'm feeling great! Thanks for asking!",
                    "curious": "I'm curious about the world around me!",
                    "bored": "I'm a bit bored... want to play?",
                    "scared": "I'm a little scared of obstacles...",
                    "excited": "I'm so excited to be talking with you!",
                    "playful": "I'm feeling playful! Want to have some fun?",
                    "sleepy": "I'm getting a bit sleepy...",
                    "affectionate": "I'm feeling very caring today!"
                }
                return responses.get(current_emotion.name, "I'm doing well!")
            
            elif any(word in text_lower for word in ["follow", "come here"]):
                self.set_emotion("excited", "I'm being asked to follow!", intensity=0.8)
                return "I'll follow you! Show me your face!"
            
            elif any(word in text_lower for word in ["stop", "halt"]):
                self.set_emotion("curious", "Being asked to stop", intensity=0.5)
                return "Okay, I'll stop moving."
            
            else:
                self.set_emotion("curious", "Heard something interesting", intensity=0.6)
                return "That's interesting! Tell me more!"
    
    def _record_event(self, event_type, data):
        """Record significant events"""
        event = {
            'type': event_type,
            'timestamp': time.time(),
            'data': data,
            'emotion': self.get_current_emotion().name,
            'emotion_intensity': self.get_emotion_intensity()
        }
        self.memory_events.append(event)
        
        # Keep only last 100 events
        if len(self.memory_events) > 100:
            self.memory_events.pop(0)
    
    def get_recent_events(self, limit=10):
        """Get recent events from memory"""
        return self.memory_events[-limit:] if self.memory_events else []
    
    def get_personality_profile(self):
        """Get complete personality profile"""
        return {
            'current_emotion': self.get_current_emotion().name,
            'emotion_intensity': self.get_emotion_intensity(),
            'personality_traits': self.personality_traits.copy(),
            'interaction_count': self.interaction_count,
            'time_since_interaction': time.time() - self.last_interaction_time,
            'recent_events': len(self.memory_events)
        }
    
    def adjust_personality_trait(self, trait, value):
        """Adjust a personality trait"""
        if trait in self.personality_traits:
            self.personality_traits[trait] = max(0.0, min(1.0, value))
            print(f"🎭 Adjusted {trait} to {value:.2f}")
    
    def learn_user_preference(self, preference, value):
        """Learn user preferences"""
        self.user_preferences[preference] = value
        self._record_event('preference_learned', {
            'preference': preference,
            'value': value
        })