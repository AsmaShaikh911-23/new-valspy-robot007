import cv2
import time

class FaceTracker:
    def __init__(self, camera, motors, display):
        self.camera = camera
        self.motors = motors
        self.display = display
        
        # Load face detection classifier
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.last_face_time = 0
        self.face_lost_time = 0
        self.tracking = False
        
    def update(self):
        """Update face tracking behavior"""
        frame = self.camera.get_frame()
        if frame is None:
            return
            
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        if len(faces) > 0:
            self._process_faces(faces, frame)
        else:
            self._no_face_detected()
    
    def _process_faces(self, faces, frame):
        """Process detected faces"""
        x, y, w, h = faces[0]  # Track largest face
        self.last_face_time = time.time()
        
        # Calculate face center
        frame_center_x = frame.shape[1] // 2
        face_center_x = x + w // 2
        
        # Face following logic
        offset = face_center_x - frame_center_x
        dead_zone = 50  # pixels
        
        if abs(offset) > dead_zone:
            if offset > 0:
                self.motors.turn_right(40)
            else:
                self.motors.turn_left(40)
        else:
            # Face is centered, move forward slowly
            self.motors.move_forward(30)
        
        self.tracking = True
        self.face_lost_time = 0
        
        # Draw face rectangle on display
        self._draw_face_overlay(frame, x, y, w, h)
    
    def _no_face_detected(self):
        """Handle no face detected"""
        current_time = time.time()
        
        if self.tracking:
            if self.face_lost_time == 0:
                self.face_lost_time = current_time
            
            # If face lost for more than 2 seconds, stop
            if current_time - self.face_lost_time > 2:
                self.motors.stop()
                self.tracking = False
        else:
            # Random search behavior
            if current_time - self.last_face_time > 5:
                self._search_for_faces()
    
    def _search_for_faces(self):
        """Search for faces by rotating"""
        search_time = time.time()
        
        # Alternate left and right searching
        if int(search_time) % 4 < 2:
            self.motors.turn_left(30)
        else:
            self.motors.turn_right(30)
    
    def _draw_face_overlay(self, frame, x, y, w, h):
        """Draw face detection overlay on display"""
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        self.display.update_frame(frame)