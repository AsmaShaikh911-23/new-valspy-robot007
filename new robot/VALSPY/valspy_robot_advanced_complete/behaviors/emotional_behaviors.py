import time
import random
import threading

class EmotionalBehaviors:
    def __init__(self, personality, motors):
        self.personality = personality
        self.motors = motors
        self.last_behavior_time = time.time()
        self.behavior_active = False
        self.current_behavior = None
        
        # Behavior patterns
        self.behaviors = {
            'happy': ['dance', 'wiggle', 'explore'],
            'curious': ['look_around', 'approach_slowly', 'scan'],
            'bored': ['sigh', 'look_around', 'sleepy_movement'],
            'playful': ['dance', 'circle', 'quick_moves'],
            'sleepy': ['slow_move', 'rest', 'minimal_movement'],
            'affectionate': ['approach_gently', 'circle_slowly']
        }
    
    def update(self):
        """Update emotional behaviors based on current state"""
        current_time = time.time()
        current_emotion = self.personality.get_current_emotion().name
        
        # Don't interrupt existing behaviors too frequently
        if self.behavior_active and (current_time - self.last_behavior_time < 10):
            return
        
        # Random chance to trigger behavior
        if random.random() < 0.3:  # 30% chance per check
            self._trigger_emotional_behavior(current_emotion)
    
    def _trigger_emotional_behavior(self, emotion):
        """Trigger behavior based on emotion"""
        self.behavior_active = True
        self.last_behavior_time = time.time()
        
        if emotion in self.behaviors:
            behavior = random.choice(self.behaviors[emotion])
            self.current_behavior = behavior
            
            print(f"🎭 Emotional behavior: {emotion} -> {behavior}")
            
            # Execute behavior in separate thread
            thread = threading.Thread(target=self._execute_behavior, args=(behavior, emotion))
            thread.daemon = True
            thread.start()
    
    def _execute_behavior(self, behavior, emotion):
        """Execute the specific behavior"""
        try:
            if behavior == 'dance':
                self._dance_behavior()
            elif behavior == 'look_around':
                self._look_around_behavior()
            elif behavior == 'explore':
                self._explore_behavior()
            elif behavior == 'wiggle':
                self._wiggle_behavior()
            elif behavior == 'circle':
                self._circle_behavior()
            elif behavior == 'sleepy_movement':
                self._sleepy_behavior()
                
        except Exception as e:
            print(f"Behavior execution error: {e}")
        finally:
            self.behavior_active = False
            self.current_behavior = None
    
    def _dance_behavior(self):
        """Happy dance behavior"""
        for i in range(3):
            self.motors.turn_left(40)
            time.sleep(0.5)
            self.motors.turn_right(40)
            time.sleep(0.5)
        self.motors.stop()
    
    def _look_around_behavior(self):
        """Curious looking around"""
        self.motors.turn_left(30)
        time.sleep(2)
        self.motors.turn_right(30)
        time.sleep(2)
        self.motors.stop()
    
    def _explore_behavior(self):
        """Happy exploration"""
        self.motors.move_forward(30)
        time.sleep(3)
        self.motors.stop()
    
    def _wiggle_behavior(self):
        """Playful wiggling"""
        for i in range(4):
            self.motors.turn_left(20)
            time.sleep(0.3)
            self.motors.turn_right(20)
            time.sleep(0.3)
        self.motors.stop()
    
    def _circle_behavior(self):
        """Playful circling"""
        self.motors.turn_left(40)
        time.sleep(4)
        self.motors.stop()
    
    def _sleepy_behavior(self):
        """Sleepy, slow movements"""
        self.motors.move_forward(15)
        time.sleep(1)
        self.motors.stop()