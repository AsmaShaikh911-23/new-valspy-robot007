#!/usr/bin/env python3
import time
import threading
import signal
import sys
from core.personality_engine import PersonalityEngine
from core.state_manager import RobotState
from hardware.camera_manager import CameraManager
from hardware.motor_controller import MotorController
from hardware.ultrasonic_sensor import UltrasonicSensor
from hardware.display_manager import DisplayManager
from hardware.audio_system import AudioSystem
from behaviors.face_tracking import FaceTracker
from behaviors.obstacle_avoidance import ObstacleAvoidance
from behaviors.voice_interaction import VoiceInteraction
from behaviors.openai_chat import OpenAIChat
from behaviors.wake_word_detector import WakeWordDetector
from behaviors.gesture_recognition import GestureRecognizer
from behaviors.emotional_behaviors import EmotionalBehaviors
from config.robot_config import ROBOT_CONFIG
from config.api_keys import API_KEYS
# Add this import at the top
from faces import face_db, initialize_face_system

# In the ValspyRobot.__init__ method, add:
self.face_db = face_db

# In the start method, after hardware initialization, add:
# Initialize face recognition system
if not initialize_face_system():
    print("⚠️ Face system initialization failed, continuing without face recognition")
else:
    print("✅ Face recognition system ready")
class ValspyRobot:
    def __init__(self):
        print("🤖 VALSPY Advanced Robot Booting...")
        
        # Initialize core systems
        self.personality = PersonalityEngine()
        self.state = RobotState()
        
        # Initialize hardware
        self.camera = CameraManager()
        self.motors = MotorController()
        self.ultrasonic = UltrasonicSensor()
        self.display = DisplayManager()
        self.audio = AudioSystem()
        
        # Initialize advanced features
        self.openai_chat = OpenAIChat(API_KEYS['openai'], self.personality)
        self.gesture_recognizer = GestureRecognizer()
        self.emotional_behaviors = EmotionalBehaviors(self.personality, self.motors)
        
        # Initialize behaviors
        self.face_tracker = FaceTracker(self.camera, self.motors, self.display, self.personality)
        self.obstacle_avoidance = ObstacleAvoidance(self.ultrasonic, self.motors, self.personality)
        self.voice_interaction = VoiceInteraction(self.audio, self.personality, self.motors, self.openai_chat)
        
        # Wake word detector
        # Wake word detector
        self.wake_detector = WakeWordDetector(
    access_key=API_KEYS['porcupine'],
    keyword_paths=[
        "VALSPY/models/modelswake_wordshey-valspy_linux/wakeword.ppn"
    ]
)

        # Thread management
        self.running = False
        self.threads = []
        self.advanced_features_enabled = ROBOT_CONFIG['advanced_features_enabled']
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def start(self):
        """Start all robot systems"""
        print("🚀 Starting VALSPY Advanced Robot Systems...")
        self.running = True
        
        try:
            # Start hardware
            self.camera.start()
            self.motors.setup()
            self.ultrasonic.setup()
            self.display.start()
            self.audio.setup()
            
            # Start advanced features if enabled
            if self.advanced_features_enabled:
                self._start_advanced_features()
            
            # Start behavior threads
            threads = [
                threading.Thread(target=self._face_tracking_loop, name="FaceTracking"),
                threading.Thread(target=self._obstacle_avoidance_loop, name="ObstacleAvoidance"),
                threading.Thread(target=self._voice_interaction_loop, name="VoiceInteraction"),
                threading.Thread(target=self._personality_loop, name="Personality"),
                threading.Thread(target=self._emotional_behavior_loop, name="EmotionalBehaviors"),
            ]
            
            # Add gesture recognition if camera available
            if self.camera.available:
                threads.append(threading.Thread(target=self._gesture_recognition_loop, name="GestureRecognition"))
            
            for thread in threads:
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
            
            print("✅ VALSPY Advanced Robot Fully Operational!")
            self.personality.set_emotion("excited", "All systems ready!")
            self.audio.text_to_speech("Hello! I'm Valspy, your advanced robot companion!")
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"❌ Error: {e}")
            self.stop()
    
    def _start_advanced_features(self):
        """Start advanced features"""
        print("🔧 Starting advanced features...")
        
        # Start wake word detection
        if self.wake_detector.setup():
            self.wake_detector.start_listening(self._on_wake_word_detected)
            print("✅ Wake word detection active - Say 'Hey Valspy'")
        
        # Load face recognition models
        self.face_tracker.load_known_faces()
        
        # Initialize Piper TTS
        self.audio.initialize_piper_tts()
    
    def _on_wake_word_detected(self):
        """Handle wake word detection"""
        print("🎯 Wake word detected!")
        self.personality.set_emotion("excited", "Heard wake word!")
        self.display.show_emotion(self.personality.get_current_emotion())
        
        # Listen for command
        self.voice_interaction.listen_for_command()
    
    def _face_tracking_loop(self):
        """Face tracking behavior loop"""
        while self.running:
            try:
                self.face_tracker.update()
                time.sleep(0.1)
            except Exception as e:
                print(f"Face tracking error: {e}")
                time.sleep(1)
    
    def _obstacle_avoidance_loop(self):
        """Obstacle avoidance behavior loop"""
        while self.running:
            try:
                self.obstacle_avoidance.update()
                time.sleep(0.05)
            except Exception as e:
                print(f"Obstacle avoidance error: {e}")
                time.sleep(1)
    
    def _voice_interaction_loop(self):
        """Voice interaction behavior loop"""
        while self.running:
            try:
                self.voice_interaction.update()
                time.sleep(0.2)
            except Exception as e:
                print(f"Voice interaction error: {e}")
                time.sleep(1)
    
    def _gesture_recognition_loop(self):
        """Gesture recognition behavior loop"""
        while self.running:
            try:
                frame = self.camera.get_frame()
                if frame is not None:
                    gestures, annotated_frame = self.gesture_recognizer.detect_gestures(frame)
                    if gestures:
                        self._process_gestures(gestures)
                    self.display.update_frame(annotated_frame)
                time.sleep(0.3)
            except Exception as e:
                print(f"Gesture recognition error: {e}")
                time.sleep(1)
    
    def _emotional_behavior_loop(self):
        """Emotional behavior updates"""
        while self.running:
            try:
                self.emotional_behaviors.update()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"Emotional behavior error: {e}")
                time.sleep(1)
    
    def _personality_loop(self):
        """Personality and emotion updates"""
        while self.running:
            try:
                self.personality.update()
                current_emotion = self.personality.get_current_emotion()
                self.display.show_emotion(current_emotion)
                time.sleep(2)
            except Exception as e:
                print(f"Personality error: {e}")
                time.sleep(1)
    
    def _process_gestures(self, gestures):
        """Process detected gestures"""
        for gesture in gestures:
            print(f"👋 Gesture detected: {gesture}")
            
            if gesture == 'open_palm':
                self.motors.stop()
                self.personality.set_emotion("curious", "Saw stop gesture")
                self.audio.text_to_speech("Stopping as requested!")
                
            elif gesture == 'thumbs_up':
                self.personality.set_emotion("happy", "Got thumbs up!")
                self.audio.text_to_speech("Thank you! I'm glad you're happy!")
                
            elif gesture == 'pointing':
                self.personality.set_emotion("excited", "Being directed to follow")
                self.audio.text_to_speech("I'll follow where you point!")
                self.motors.move_forward(40)
                
            elif gesture == 'victory':
                self.personality.set_emotion("playful", "Saw victory sign!")
                self.audio.text_to_speech("Victory! We did it!")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def stop(self):
        """Safely stop all systems"""
        print("🛑 Shutting down VALSPY Advanced Robot...")
        self.running = False
        
        # Stop systems in order
        self.wake_detector.stop_listening()
        self.motors.stop()
        self.camera.stop()
        self.display.stop()
        self.audio.cleanup()
        
        print("✅ VALSPY Advanced Robot safely shut down")

if __name__ == "__main__":
    robot = ValspyRobot()
    robot.start()