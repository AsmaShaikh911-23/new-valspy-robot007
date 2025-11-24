import pyaudio
import wave
import threading
import time
import os
import subprocess
from hardware.piper_tts import PiperTTS

class AudioSystem:
    def __init__(self):
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 5
        
        self.audio = pyaudio.PyAudio()
        self.recording = False
        self.last_audio_time = 0
        self.piper_tts = None
        
    def setup(self):
        """Initialize audio system"""
        try:
            # Test audio output
            subprocess.run(['aplay', '--version'], capture_output=True)
            print("✅ Audio system initialized")
            return True
        except Exception as e:
            print(f"❌ Audio setup error: {e}")
            return False
    
    def initialize_piper_tts(self):
        """Initialize Piper TTS system"""
        self.piper_tts = PiperTTS()
        if self.piper_tts.available:
            print("✅ Piper TTS initialized")
        else:
            print("⚠️ Piper TTS not available, using espeak fallback")
    
    def record_audio(self, filename="temp_audio.wav"):
        """Record audio from Boya microphone"""
        try:
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            print("🎤 Recording...")
            frames = []
            
            for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                data = stream.read(self.CHUNK)
                frames.append(data)
            
            print("✅ Recording finished")
            
            stream.stop_stream()
            stream.close()
            
            # Save to file
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            self.last_audio_time = time.time()
            return True
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return False
    
    def text_to_speech(self, text):
        """Convert text to speech using Piper or espeak"""
        print(f"🗣️ VALSPY says: {text}")
        
        if self.piper_tts and self.piper_tts.available:
            return self.piper_tts.speak(text)
        else:
            # Fallback to espeak
            try:
                subprocess.run(['espeak', '-s', '150', text])
                return True
            except:
                print("❌ TTS failed")
                return False
    
    def play_audio(self, filename):
        """Play audio through speaker"""
        try:
            if not os.path.exists(filename):
                return False
                
            subprocess.run(['aplay', '-q', filename])
            return True
            
        except Exception as e:
            print(f"❌ Playback error: {e}")
            return False
    
    def cleanup(self):
        """Cleanup audio resources"""
        if self.audio:
            self.audio.terminate()