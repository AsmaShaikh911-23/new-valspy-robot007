#!/usr/bin/env python3
import cv2
import os
import pickle
import numpy as np
import time
from hardware.camera_manager import CameraManager
from faces import face_db, KNOWN_FACES_DIR

class FaceTrainer:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.camera = None
        
    def capture_face_samples(self, name: str, num_samples: int = 20) -> bool:
        """Capture face samples for training"""
        print(f"📸 Capturing {num_samples} samples for {name}...")
        
        self.camera = CameraManager()
        self.camera.start()
        
        samples_captured = 0
        save_path = os.path.join(KNOWN_FACES_DIR, name)
        os.makedirs(save_path, exist_ok=True)
        
        cv2.namedWindow('Face Capture - Press Q to quit', cv2.WINDOW_NORMAL)
        
        try:
            while samples_captured < num_samples:
                frame = self.camera.get_frame()
                if frame is not None:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    for (x, y, w, h) in faces:
                        # Extract face region
                        face_roi = gray[y:y+h, x:x+w]
                        
                        # Save face sample to database
                        success = face_db.add_face(name, face_roi)
                        if success:
                            # Also save as image file
                            filename = f"{save_path}/{samples_captured:03d}.jpg"
                            cv2.imwrite(filename, face_roi)
                            
                            samples_captured += 1
                            print(f"✅ Captured sample {samples_captured}/{num_samples}")
                        
                        # Draw rectangle on frame
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, f'{name}: {samples_captured}/{num_samples}', 
                                  (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        
                        break  # Only process one face per frame
                
                # Show preview
                cv2.imshow('Face Capture - Press Q to quit', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                time.sleep(0.1)  # Small delay between captures
            
            # Train the recognizer with new data
            if samples_captured > 0:
                print("🧠 Training face recognizer with new data...")
                face_db.train_recognizer()
                face_db.save_face_data()
            
            print(f"✅ Successfully captured {samples_captured} samples for {name}")
            return samples_captured > 0
            
        except Exception as e:
            print(f"❌ Error during face capture: {e}")
            return False
        finally:
            if self.camera:
                self.camera.stop()
            cv2.destroyAllWindows()
    
    def list_known_faces(self):
        """List all known faces in the database"""
        stats = face_db.get_face_statistics()
        print("\n📊 Face Database Statistics:")
        print(f"👥 Known people: {stats['total_people']}")
        print(f"📷 Total faces: {stats['total_faces']}")
        print(f"🎯 Trained: {stats['is_trained']}")
        print(f"💾 Database size: {stats['database_size_mb']} MB")
        
        if stats['known_people']:
            print("\n👤 Known people:")
            for person in stats['known_people']:
                print(f"  - {person}")
        else:
            print("\nℹ️ No known faces in database")
    
    def test_face_recognition(self):
        """Test face recognition with live camera"""
        print("🎭 Testing face recognition...")
        
        self.camera = CameraManager()
        self.camera.start()
        
        cv2.namedWindow('Face Recognition Test - Press Q to quit', cv2.WINDOW_NORMAL)
        
        try:
            while True:
                frame = self.camera.get_frame()
                if frame is not None:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    for (x, y, w, h) in faces:
                        face_roi = gray[y:y+h, x:x+w]
                        
                        # Recognize face
                        name, confidence = face_db.recognize_face(face_roi)
                        
                        # Draw results
                        color = (0, 255, 0) if name else (0, 0, 255)
                        label = f"{name} ({confidence:.1f})" if name else f"Unknown ({confidence:.1f})"
                        
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        cv2.putText(frame, label, (x, y-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                cv2.imshow('Face Recognition Test - Press Q to quit', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            if self.camera:
                self.camera.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    trainer = FaceTrainer()
    
    print("🎭 VALSPY Face Trainer")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Add new face")
        print("2. List known faces")
        print("3. Test recognition")
        print("4. Exit")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == '1':
            name = input("Enter person's name: ").strip()
            if name:
                samples = input("Number of samples to capture (default 20): ").strip()
                num_samples = int(samples) if samples.isdigit() else 20
                trainer.capture_face_samples(name, num_samples)
            else:
                print("❌ No name provided!")
        
        elif choice == '2':
            trainer.list_known_faces()
        
        elif choice == '3':
            if face_db.is_trained:
                trainer.test_face_recognition()
            else:
                print("❌ Face recognizer not trained! Add faces first.")
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option!")