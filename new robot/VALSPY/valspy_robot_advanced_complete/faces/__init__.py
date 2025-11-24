"""
Faces package for VALSPY Robot
Handles face recognition data, training, and known faces database.
"""

import os
import pickle
import cv2
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple

# Face recognition paths
KNOWN_FACES_DIR = os.path.join(os.path.dirname(__file__), 'known_faces')
FACE_RECOGNIZER_FILE = os.path.join(os.path.dirname(__file__), 'face_recognizer.yml')
FACE_DATA_FILE = os.path.join(os.path.dirname(__file__), 'face_data.pkl')

# Face recognition settings
FACE_SIZE = (200, 200)  # Standard size for face images
CONFIDENCE_THRESHOLD = 70  # Lower confidence = more strict recognition
MAX_FACES_TO_STORE = 1000  # Maximum number of faces to store in database

class FaceDatabase:
    """Manager for face recognition database"""
    
    def __init__(self):
        self.known_faces = {}
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.is_trained = False
        
    def load_face_data(self) -> bool:
        """
        Load face recognition data from disk.
        
        Returns:
            bool: True if data loaded successfully
        """
        try:
            # Load face recognizer
            if os.path.exists(FACE_RECOGNIZER_FILE):
                self.face_recognizer.read(FACE_RECOGNIZER_FILE)
                self.is_trained = True
            else:
                logging.warning("Face recognizer model not found")
                self.is_trained = False
            
            # Load face data
            if os.path.exists(FACE_DATA_FILE):
                with open(FACE_DATA_FILE, 'rb') as f:
                    data = pickle.load(f)
                    self.known_faces = data.get('known_faces', {})
                    logging.info(f"Loaded {len(self.known_faces)} known faces from database")
                return True
            else:
                logging.warning("Face data file not found")
                self.known_faces = {}
                return False
                
        except Exception as e:
            logging.error(f"Error loading face data: {e}")
            self.known_faces = {}
            self.is_trained = False
            return False
    
    def save_face_data(self) -> bool:
        """
        Save face recognition data to disk.
        
        Returns:
            bool: True if data saved successfully
        """
        try:
            # Save face recognizer
            if self.is_trained:
                self.face_recognizer.write(FACE_RECOGNIZER_FILE)
            
            # Save face data
            data = {
                'known_faces': self.known_faces,
                'total_faces': len(self.known_faces),
                'face_size': FACE_SIZE
            }
            
            with open(FACE_DATA_FILE, 'wb') as f:
                pickle.dump(data, f)
            
            logging.info(f"Saved {len(self.known_faces)} known faces to database")
            return True
            
        except Exception as e:
            logging.error(f"Error saving face data: {e}")
            return False
    
    def add_face(self, name: str, face_image: np.ndarray, confidence: float = 1.0) -> bool:
        """
        Add a face to the database.
        
        Args:
            name: Name of the person
            face_image: Grayscale face image
            confidence: Confidence score for this face
            
        Returns:
            bool: True if face added successfully
        """
        try:
            # Resize face to standard size
            face_image = cv2.resize(face_image, FACE_SIZE)
            
            if name not in self.known_faces:
                self.known_faces[name] = {
                    'faces': [],
                    'embeddings': [],
                    'confidence_scores': [],
                    'last_seen': None,
                    'total_sightings': 0
                }
            
            # Add face data
            self.known_faces[name]['faces'].append(face_image)
            self.known_faces[name]['confidence_scores'].append(confidence)
            self.known_faces[name]['last_seen'] = np.datetime64('now')
            self.known_faces[name]['total_sightings'] += 1
            
            # Limit stored faces per person
            if len(self.known_faces[name]['faces']) > 50:  # Keep last 50 faces per person
                self.known_faces[name]['faces'] = self.known_faces[name]['faces'][-50:]
                self.known_faces[name]['confidence_scores'] = self.known_faces[name]['confidence_scores'][-50:]
            
            logging.info(f"Added face for {name} (total: {self.known_faces[name]['total_sightings']})")
            return True
            
        except Exception as e:
            logging.error(f"Error adding face for {name}: {e}")
            return False
    
    def recognize_face(self, face_image: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Recognize a face from the database.
        
        Args:
            face_image: Grayscale face image to recognize
            
        Returns:
            Tuple of (name, confidence) or (None, 100) if unknown
        """
        if not self.is_trained or not self.known_faces:
            return None, 100.0
        
        try:
            # Resize face to standard size
            face_image = cv2.resize(face_image, FACE_SIZE)
            
            # Predict using face recognizer
            label, confidence = self.face_recognizer.predict(face_image)
            
            # Convert label to name
            if confidence < CONFIDENCE_THRESHOLD:
                # Find name for this label
                for name, data in self.known_faces.items():
                    # This is simplified - in real implementation you'd need proper label mapping
                    if hash(name) % 1000 == label % 1000:  # Simple hash-based mapping
                        return name, confidence
                return "Unknown", confidence
            else:
                return None, confidence
                
        except Exception as e:
            logging.error(f"Error recognizing face: {e}")
            return None, 100.0
    
    def train_recognizer(self) -> bool:
        """
        Train the face recognizer with current face data.
        
        Returns:
            bool: True if training successful
        """
        try:
            if not self.known_faces:
                logging.warning("No face data available for training")
                return False
            
            faces = []
            labels = []
            label_map = {}
            current_label = 0
            
            # Prepare training data
            for name, data in self.known_faces.items():
                if data['faces']:
                    label_map[current_label] = name
                    for face in data['faces']:
                        faces.append(face)
                        labels.append(current_label)
                    current_label += 1
            
            if not faces:
                logging.warning("No valid face images for training")
                return False
            
            # Train the recognizer
            self.face_recognizer.train(faces, np.array(labels))
            self.is_trained = True
            
            logging.info(f"Face recognizer trained with {len(faces)} images and {len(label_map)} people")
            return True
            
        except Exception as e:
            logging.error(f"Error training face recognizer: {e}")
            self.is_trained = False
            return False
    
    def get_face_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the face database.
        
        Returns:
            Dict with face database statistics
        """
        total_faces = 0
        total_people = len(self.known_faces)
        trained_status = self.is_trained
        
        for name, data in self.known_faces.items():
            total_faces += len(data['faces'])
        
        return {
            'total_people': total_people,
            'total_faces': total_faces,
            'is_trained': trained_status,
            'known_people': list(self.known_faces.keys()),
            'database_size_mb': self._get_database_size()
        }
    
    def _get_database_size(self) -> float:
        """Get the size of face database in MB"""
        total_size = 0
        if os.path.exists(FACE_RECOGNIZER_FILE):
            total_size += os.path.getsize(FACE_RECOGNIZER_FILE)
        if os.path.exists(FACE_DATA_FILE):
            total_size += os.path.getsize(FACE_DATA_FILE)
        if os.path.exists(KNOWN_FACES_DIR):
            for dirpath, dirnames, filenames in os.walk(KNOWN_FACES_DIR):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
        
        return round(total_size / (1024 * 1024), 2)
    
    def cleanup_old_faces(self, max_age_days: int = 30) -> int:
        """
        Remove old face data from database.
        
        Args:
            max_age_days: Maximum age of faces to keep in days
            
        Returns:
            Number of faces removed
        """
        # This is a placeholder - actual implementation would need
        # timestamp tracking for each face
        logging.info("Face cleanup would remove faces older than {max_age_days} days")
        return 0

# Global face database instance
face_db = FaceDatabase()

def initialize_face_system() -> bool:
    """
    Initialize the face recognition system.
    
    Returns:
        bool: True if initialization successful
    """
    try:
        # Create directories
        os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
        
        # Load existing face data
        success = face_db.load_face_data()
        
        if success:
            logging.info("✅ Face system initialized successfully")
        else:
            logging.info("ℹ️ Face system initialized (no existing data)")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Error initializing face system: {e}")
        return False

def get_known_faces_list() -> List[str]:
    """
    Get list of known face names.
    
    Returns:
        List of known face names
    """
    return list(face_db.known_faces.keys())

def is_face_known(name: str) -> bool:
    """
    Check if a face name exists in the database.
    
    Args:
        name: Name to check
        
    Returns:
        bool: True if face is known
    """
    return name in face_db.known_faces

def export_face_data(export_path: str) -> bool:
    """
    Export face database to a file.
    
    Args:
        export_path: Path where to export the data
        
    Returns:
        bool: True if export successful
    """
    try:
        export_data = {
            'known_faces': face_db.known_faces,
            'face_size': FACE_SIZE,
            'export_timestamp': np.datetime64('now')
        }
        
        with open(export_path, 'wb') as f:
            pickle.dump(export_data, f)
        
        logging.info(f"Face data exported to {export_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error exporting face data: {e}")
        return False

def import_face_data(import_path: str) -> bool:
    """
    Import face database from a file.
    
    Args:
        import_path: Path to import file
        
    Returns:
        bool: True if import successful
    """
    try:
        if not os.path.exists(import_path):
            logging.error(f"Import file not found: {import_path}")
            return False
        
        with open(import_path, 'rb') as f:
            import_data = pickle.load(f)
        
        face_db.known_faces = import_data.get('known_faces', {})
        face_db.save_face_data()
        
        logging.info(f"Face data imported from {import_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error importing face data: {e}")
        return False

# Initialize face system on import
initialize_face_system()

# Export public functions and classes
__all__ = [
    'KNOWN_FACES_DIR',
    'FACE_RECOGNIZER_FILE',
    'FACE_DATA_FILE',
    'FACE_SIZE',
    'CONFIDENCE_THRESHOLD',
    'FaceDatabase',
    'face_db',
    'initialize_face_system',
    'get_known_faces_list',
    'is_face_known',
    'export_face_data',
    'import_face_data'
]