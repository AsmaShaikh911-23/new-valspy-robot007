import subprocess
import os
import threading
import tempfile
import time

class PiperTTS:
    def __init__(self, model_path="models/piper_models/en_US-lessac-medium.onnx"):
        self.model_path = model_path
        self.is_speaking = False
        self.available = self._check_piper_available()
        
    def _check_piper_available(self):
        """Check if Piper TTS is available"""
        try:
            result = subprocess.run(['which', 'piper'], 
                                  capture_output=True, text=True)
            return result.returncode == 0 and os.path.exists(self.model_path)
        except:
            return False
    
    def speak(self, text, blocking=False):
        """Convert text to speech using Piper"""
        if not self.available or self.is_speaking:
            return False
            
        def _speak_thread():
            self.is_speaking = True
            try:
                # Create temporary WAV file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                print(f"🔊 Piper TTS: {text}")
                
                # Use Piper to generate speech
                cmd = [
                    'piper', '--model', self.model_path,
                    '--output_file', temp_path
                ]
                
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Send text to Piper
                process.communicate(input=text)
                
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    # Play the generated audio
                    subprocess.run(['aplay', '-q', temp_path])
                else:
                    print("❌ Piper failed to generate audio")
                
                # Cleanup
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
            except Exception as e:
                print(f"❌ TTS error: {e}")
                # Fallback to espeak
                subprocess.run(['espeak', '-s', '150', text])
            finally:
                self.is_speaking = False
        
        if blocking:
            _speak_thread()
        else:
            thread = threading.Thread(target=_speak_thread)
            thread.daemon = True
            thread.start()
        
        return True
    
    def wait_until_done(self):
        """Wait until current speech is done"""
        while self.is_speaking:
            time.sleep(0.1)