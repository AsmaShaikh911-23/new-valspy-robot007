import picamera
import picamera.array
import numpy as np
import cv2
import threading
import time

class CameraManager:
    def __init__(self):
        self.camera = None
        self.current_frame = None
        self.running = False
        self.thread = None
        self.frame_lock = threading.Lock()
        
    def start(self):
        """Start camera capture"""
        try:
            self.camera = picamera.PiCamera()
            self.camera.resolution = (640, 480)
            self.camera.framerate = 30
            time.sleep(2)  # Camera warm-up
            
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()
            
            print("✅ Camera started")
            
        except Exception as e:
            print(f"❌ Camera error: {e}")
    
    def _capture_loop(self):
        """Continuous capture loop"""
        with picamera.array.PiRGBArray(self.camera) as output:
            for frame in self.camera.capture_continuous(
                output, format="bgr", use_video_port=True):
                
                if not self.running:
                    break
                    
                with self.frame_lock:
                    self.current_frame = frame.array.copy()
                
                output.truncate(0)
    
    def get_frame(self):
        """Get current frame"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None
    
    def stop(self):
        """Stop camera"""
        self.running = False
        if self.camera:
            self.camera.close()
        print("✅ Camera stopped")