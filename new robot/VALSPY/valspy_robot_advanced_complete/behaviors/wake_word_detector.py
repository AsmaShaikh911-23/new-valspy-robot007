import pvporcupine
import pyaudio
import struct
import threading
import time
import os

class WakeWordDetector:
    def __init__(self, access_key, keyword_paths=None):
        self.access_key = access_key
        self.keyword_paths = keyword_paths
        self.detector = None
        self.audio_stream = None
        self.audio = None
        self.listening = False
        self.callback = None
        self.thread = None
        
        # Ensure keyword files exist
        if self.keyword_paths:
            self._check_keyword_files()
    
    def _check_keyword_files(self):
        """Check if wake word model files exist"""
        for path in self.keyword_paths:
            if not os.path.exists(path):
                print(f"⚠️ Wake word model not found: {path}")
                print("💡 Download wake word models from Picovoice Console")
    
    def setup(self):
        """Initialize wake word detection"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs('models/wake_words', exist_ok=True)
            
            self.detector = pvporcupine.create(
                access_key=self.access_key,
                keyword_paths=self.keyword_paths
            )
            
            self.audio = pyaudio.PyAudio()
            
            self.audio_stream = self.audio.open(
                rate=self.detector.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.detector.frame_length,
                input_device_index=None  # Use default device
            )
            
            print("✅ Wake word detector ready")
            return True
            
        except Exception as e:
            print(f"❌ Wake word setup error: {e}")
            print("💡 Make sure you have a valid Porcupine access key")
            return False
    
    def start_listening(self, callback):
        """Start listening for wake words"""
        if not self.detector:
            print("❌ Wake word detector not initialized")
            return False
            
        self.callback = callback
        self.listening = True
        
        self.thread = threading.Thread(target=self._listen_loop, name="WakeWordListener")
        self.thread.daemon = True
        self.thread.start()
        
        print("👂 Wake word detection active")
        return True
    
    def _listen_loop(self):
        """Main listening loop"""
        print("🎯 Listening for 'Hey Valspy'...")
        
        while self.listening:
            try:
                pcm = self.audio_stream.read(self.detector.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.detector.frame_length, pcm)
                
                keyword_index = self.detector.process(pcm)
                
                if keyword_index >= 0:
                    print("🎯 Wake word detected!")
                    if self.callback:
                        self.callback()
                    # Brief pause to prevent multiple detections
                    time.sleep(1)
                    
            except Exception as e:
                if self.listening:  # Only print error if we're supposed to be listening
                    print(f"Wake word listening error: {e}")
                break
    
    def stop_listening(self):
        """Stop wake word detection"""
        self.listening = False
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        if self.detector:
            self.detector.delete()
        
        print("✅ Wake word detector stopped")