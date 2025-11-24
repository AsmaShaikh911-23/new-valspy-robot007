import cv2
import mediapipe as mp
import numpy as np

class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.gesture_commands = {
            'open_palm': 'stop',
            'thumbs_up': 'good',
            'pointing': 'follow',
            'fist': 'stay',
            'victory': 'happy',
            'rock': 'playful'
        }
        
        print("✅ Gesture recognizer initialized")
    
    def detect_gestures(self, frame):
        """Detect hand gestures in frame"""
        try:
            if frame is None:
                return [], frame
                
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            gestures_detected = []
            annotated_frame = frame.copy()
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_draw.draw_landmarks(
                        annotated_frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
                    )
                    
                    # Classify gesture
                    gesture = self._classify_gesture(hand_landmarks.landmark)
                    if gesture:
                        gestures_detected.append(gesture)
                        
                        # Add gesture label to frame
                        h, w, _ = annotated_frame.shape
                        x_min = min([lm.x for lm in hand_landmarks.landmark]) * w
                        y_min = min([lm.y for lm in hand_landmarks.landmark]) * h
                        
                        cv2.putText(annotated_frame, gesture, 
                                  (int(x_min), int(y_min - 10)),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            return gestures_detected, annotated_frame
            
        except Exception as e:
            print(f"Gesture detection error: {e}")
            return [], frame
    
    def _classify_gesture(self, landmarks):
        """Classify specific hand gestures"""
        try:
            # Get key points
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]
            pinky_tip = landmarks[20]
            
            wrist = landmarks[0]
            
            # Calculate finger extended states
            fingers_extended = []
            
            # Thumb (different logic)
            thumb_extended = thumb_tip.x < landmarks[3].x if thumb_tip.x < wrist.x else thumb_tip.x > landmarks[3].x
            
            # Other fingers
            for tip_idx, pip_idx in [(8, 6), (12, 10), (16, 14), (20, 18)]:
                fingers_extended.append(landmarks[tip_idx].y < landmarks[pip_idx].y)
            
            # Classify gestures
            if all(fingers_extended) and thumb_extended:  # All fingers extended
                return 'open_palm'
            elif thumb_extended and not any(fingers_extended):  # Only thumb
                return 'thumbs_up'
            elif fingers_extended[0] and not any(fingers_extended[1:]) and thumb_extended:  # Pointing
                return 'pointing'
            elif not any(fingers_extended) and not thumb_extended:  # No fingers extended
                return 'fist'
            elif fingers_extended[0] and fingers_extended[1] and not any(fingers_extended[2:]):  # Victory
                return 'victory'
            elif fingers_extended[0] and fingers_extended[3] and not fingers_extended[1] and not fingers_extended[2]:  # Rock
                return 'rock'
            
            return None
            
        except Exception as e:
            print(f"Gesture classification error: {e}")
            return None
    
    def cleanup(self):
        """Cleanup mediapipe resources"""
        if self.hands:
            self.hands.close()