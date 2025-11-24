# Advanced Robot Configuration Settings

ROBOT_CONFIG = {
    # System Settings
    'advanced_features_enabled': True,
    'log_level': 'INFO',
    
    # Motor Configuration
    'motor': {
        'left_pins': [17, 18, 27],
        'right_pins': [22, 23, 24],
        'pwm_frequency': 1000,
        'default_speed': 50,
        'turn_speed': 60
    },
    
    # Sensor Configuration
    'ultrasonic': {
        'trigger_pin': 5,
        'echo_pin': 6,
        'stop_distance': 20,  # cm
        'warning_distance': 40,  # cm
        'sample_rate': 10  # Hz
    },
    
    # Camera Configuration
    'camera': {
        'resolution': (640, 480),
        'framerate': 30,
        'rotation': 0,
        'face_detection_scale': 1.1,
        'face_min_neighbors': 5,
        'face_min_size': (30, 30)
    },
    
    # Personality Configuration
    'personality': {
        'default_emotion': 'curious',
        'mood_shift_interval': 30,  # seconds
        'boredom_threshold': 60,  # seconds
        'interaction_memory': 10  # number of interactions to remember
    },
    
    # Audio Configuration
    'audio': {
        'chunk_size': 1024,
        'sample_rate': 16000,
        'channels': 1,
        'record_seconds': 5,
        'wake_word_sensitivity': 0.7
    },
    
    # Face Recognition
    'face_recognition': {
        'confidence_threshold': 70,
        'face_size': (200, 200),
        'max_faces': 10
    },
    
    # OpenAI Configuration
    'openai': {
        'model': 'gpt-3.5-turbo',
        'max_tokens': 150,
        'temperature': 0.7,
        'max_history': 6
    }
}