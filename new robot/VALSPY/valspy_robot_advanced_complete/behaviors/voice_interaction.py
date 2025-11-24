import time
import threading
from hardware.audio_system import AudioSystem

class VoiceInteraction:
    def __init__(self, audio, personality, motors):
        self.audio = audio
        self.personality = personality
        self.motors = motors
        
        self.listening = False
        self.last_voice_time = 0
        
    def update(self):
        """Update voice interaction behavior"""
        current_time = time.time()
        
        # Listen for voice commands periodically
        if current_time - self.last_voice_time > 10:  # Check every 10 seconds
            self._listen_for_commands()
    
    def _listen_for_commands(self):
        """Listen and process voice commands"""
        print("👂 Listening for commands...")
        
        # Record audio
        if self.audio.record_audio("command.wav"):
            # TODO: Integrate speech-to-text here
            # For now, simulate voice input
            simulated_commands = [
                "hello valspy",
                "how are you",
                "follow me",
                "stop",
                "what can you do"
            ]
            
            # Simulate receiving a command
            import random
            simulated_text = random.choice(simulated_commands)
            print(f"🎯 Heard: {simulated_text}")
            
            self._process_command(simulated_text)
            
        self.last_voice_time = time.time()
    
    def _process_command(self, text):
        """Process voice command text"""
        response = self.personality.react_to_voice(text)
        
        # Speak response
        self.audio.text_to_speech(response)
        
        # Execute actions based on command
        text_lower = text.lower()
        
        if "stop" in text_lower:
            self.motors.stop()
        elif "follow" in text_lower:
            self.personality.set_emotion("excited", "Following command!")
        elif "come here" in text_lower:
            self.motors.move_forward(40)
            time.sleep(2)
            self.motors.stop()