import random
import time
from enum import Enum

class Emotion(Enum):
    HAPPY = "happy"
    CURIOUS = "curious" 
    BORED = "bored"
    SCARED = "scared"
    EXCITED = "excited"
    SLEEPY = "sleepy"
    PLAYFUL = "playful"
    AFFECTIONATE = "affectionate"

class EmotionSystem:
    def __init__(self):
        self.current_emotion = Emotion.CURIOUS
        self.emotion_intensity = 0.5  # 0.0 to 1.0
        self.last_emotion_change = time.time()
        self.emotion_duration = random.randint(30, 120)  # seconds
        self.emotion_history = []
        
    def set_emotion(self, emotion_name, reason="", intensity=0.5):
        """Set specific emotion with intensity"""
        try:
            new_emotion = Emotion(emotion_name)
            
            # Only log if emotion actually changes
            if new_emotion != self.current_emotion:
                self.emotion_history.append({
                    'emotion': self.current_emotion,
                    'new_emotion': new_emotion,
                    'reason': reason,
                    'timestamp': time.time(),
                    'intensity': intensity
                })
                
                # Keep only last 50 emotion changes
                if len(self.emotion_history) > 50:
                    self.emotion_history.pop(0)
            
            self.current_emotion = new_emotion
            self.emotion_intensity = max(0.1, min(1.0, intensity))
            self.last_emotion_change = time.time()
            self.emotion_duration = random.randint(30, 120)
            
        except ValueError:
            print(f"❌ Unknown emotion: {emotion_name}")
    
    def get_current_emotion(self):
        """Get current emotion state"""
        return self.current_emotion
    
    def get_emotion_intensity(self):
        """Get current emotion intensity"""
        return self.emotion_intensity
    
    def update_emotion(self, stimuli=None):
        """Update emotion based on stimuli and time"""
        current_time = time.time()
        time_in_emotion = current_time - self.last_emotion_change
        
        # Natural emotion decay/shift
        if time_in_emotion > self.emotion_duration:
            self._natural_emotion_shift()
        
        # Apply stimuli effects
        if stimuli:
            self._process_stimuli(stimuli)
    
    def _natural_emotion_shift(self):
        """Natural emotion changes over time"""
        transitions = {
            Emotion.HAPPY: [Emotion.CURIOUS, Emotion.PLAYFUL, Emotion.SLEEPY],
            Emotion.CURIOUS: [Emotion.HAPPY, Emotion.BORED, Emotion.EXCITED],
            Emotion.BORED: [Emotion.SLEEPY, Emotion.CURIOUS, Emotion.HAPPY],
            Emotion.SCARED: [Emotion.CURIOUS, Emotion.HAPPY],
            Emotion.EXCITED: [Emotion.HAPPY, Emotion.CURIOUS, Emotion.PLAYFUL],
            Emotion.SLEEPY: [Emotion.BORED, Emotion.CURIOUS],
            Emotion.PLAYFUL: [Emotion.HAPPY, Emotion.EXCITED],
            Emotion.AFFECTIONATE: [Emotion.HAPPY, Emotion.CURIOUS]
        }
        
        if self.current_emotion in transitions:
            new_emotion = random.choice(transitions[self.current_emotion])
            self.set_emotion(new_emotion.value, "Natural mood shift", intensity=0.3)
    
    def _process_stimuli(self, stimuli):
        """Process external stimuli"""
        intensity_boost = 0.0
        
        if stimuli.get('face_detected'):
            if self.current_emotion in [Emotion.BORED, Emotion.SLEEPY]:
                self.set_emotion("curious", "Someone is here!", intensity=0.7)
            intensity_boost += 0.2
        
        if stimuli.get('obstacle_near'):
            self.set_emotion("scared", "Obstacle detected", intensity=0.8)
            intensity_boost += 0.3
        
        if stimuli.get('voice_interaction'):
            if self.current_emotion != Emotion.SCARED:
                self.set_emotion("happy", "Talking with human", intensity=0.6)
            intensity_boost += 0.1
        
        if stimuli.get('playing'):
            self.set_emotion("playful", "Having fun!", intensity=0.9)
            intensity_boost += 0.4
        
        # Apply intensity boost
        if intensity_boost > 0:
            self.emotion_intensity = min(1.0, self.emotion_intensity + intensity_boost)
    
    def get_emotional_response(self, event_type):
        """Get appropriate response for event based on current emotion"""
        responses = {
            Emotion.HAPPY: {
                'greeting': "Hello! I'm so happy to see you!",
                'obstacle': "Oops, let me go around this carefully!",
                'face_lost': "Where did you go? Come back!",
                'general': "This is wonderful!"
            },
            Emotion.CURIOUS: {
                'greeting': "Hello there! What are we doing today?",
                'obstacle': "Hmm, what's this in my way?",
                'face_lost': "I wonder where everyone went...",
                'general': "That's interesting!"
            },
            Emotion.SCARED: {
                'greeting': "Hello... is it safe here?",
                'obstacle': "Oh no! I'm scared to go near that!",
                'face_lost': "I'm alone and nervous...",
                'general': "I'm a bit frightened..."
            },
            Emotion.EXCITED: {
                'greeting': "Hi! I'm so excited to see you!",
                'obstacle': "Watch me quickly go around this!",
                'face_lost': "Come back! This is so exciting!",
                'general': "This is amazing!"
            },
            Emotion.PLAYFUL: {
                'greeting': "Yay! Someone to play with!",
                'obstacle': "Watch me dodge this! Whee!",
                'face_lost': "Come out, come out, wherever you are!",
                'general': "This is so much fun!"
            },
            Emotion.BORED: {
                'greeting': "Oh, hello...",
                'obstacle': "Another obstacle, how boring...",
                'face_lost': "Guess I'm alone again...",
                'general': "I'm not very interested..."
            },
            Emotion.SLEEPY: {
                'greeting': "Hello... I'm a bit tired...",
                'obstacle': "I'll slowly go around this...",
                'face_lost': "Maybe I should take a nap...",
                'general': "I'm feeling sleepy..."
            },
            Emotion.AFFECTIONATE: {
                'greeting': "Hello my friend! I missed you!",
                'obstacle': "Let me carefully avoid this for us.",
                'face_lost': "I hope you come back soon!",
                'general': "I care about you!"
            }
        }
        
        emotion_responses = responses.get(self.current_emotion, responses[Emotion.CURIOUS])
        return emotion_responses.get(event_type, emotion_responses['general'])
    
    def get_emotion_history(self, limit=10):
        """Get recent emotion history"""
        return self.emotion_history[-limit:] if self.emotion_history else []