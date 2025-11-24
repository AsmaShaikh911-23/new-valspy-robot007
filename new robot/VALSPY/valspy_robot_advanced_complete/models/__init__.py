"""
Models package for VALSPY Robot
Handles AI models, wake word models, and TTS voice models.
"""

import os
import logging
from typing import Dict, Any, Optional

# Model paths
PIPER_MODELS_DIR = os.path.join(os.path.dirname(__file__), 'piper_models')
WAKE_WORD_MODELS_DIR = os.path.join(os.path.dirname(__file__), 'wake_words')

# Default model files
DEFAULT_PIPER_MODEL = os.path.join(PIPER_MODELS_DIR, 'en_US-lessac-medium.onnx')
DEFAULT_WAKE_WORD_MODEL = os.path.join(WAKE_WORD_MODELS_DIR, 'hey-valspy_linux.ppn')

def check_models_available() -> Dict[str, bool]:
    """
    Check which models are available in the system.
    
    Returns:
        Dict with model availability status
    """
    models_status = {
        'piper_tts': os.path.exists(DEFAULT_PIPER_MODEL),
        'wake_word': os.path.exists(DEFAULT_WAKE_WORD_MODEL),
        'piper_models_dir': os.path.exists(PIPER_MODELS_DIR),
        'wake_word_models_dir': os.path.exists(WAKE_WORD_MODELS_DIR)
    }
    
    return models_status

def get_available_models() -> Dict[str, Any]:
    """
    Get list of all available models with their paths.
    
    Returns:
        Dict containing available models information
    """
    available_models = {
        'piper_models': [],
        'wake_word_models': []
    }
    
    # Check Piper TTS models
    if os.path.exists(PIPER_MODELS_DIR):
        for file in os.listdir(PIPER_MODELS_DIR):
            if file.endswith('.onnx'):
                available_models['piper_models'].append({
                    'name': file.replace('.onnx', ''),
                    'path': os.path.join(PIPER_MODELS_DIR, file),
                    'size': os.path.getsize(os.path.join(PIPER_MODELS_DIR, file)) if os.path.exists(os.path.join(PIPER_MODELS_DIR, file)) else 0
                })
    
    # Check wake word models
    if os.path.exists(WAKE_WORD_MODELS_DIR):
        for file in os.listdir(WAKE_WORD_MODELS_DIR):
            if file.endswith('.ppn'):
                available_models['wake_word_models'].append({
                    'name': file.replace('.ppn', ''),
                    'path': os.path.join(WAKE_WORD_MODELS_DIR, file),
                    'size': os.path.getsize(os.path.join(WAKE_WORD_MODELS_DIR, file)) if os.path.exists(os.path.join(WAKE_WORD_MODELS_DIR, file)) else 0
                })
    
    return available_models

def download_default_models() -> bool:
    """
    Download default models if they don't exist.
    
    Returns:
        bool: True if successful or models already exist
    """
    try:
        import requests
        import urllib.request
    except ImportError:
        logging.error("Requests library not available for downloading models")
        return False
    
    # Create directories if they don't exist
    os.makedirs(PIPER_MODELS_DIR, exist_ok=True)
    os.makedirs(WAKE_WORD_MODELS_DIR, exist_ok=True)
    
    models_downloaded = 0
    
    # Download Piper model if not exists
    if not os.path.exists(DEFAULT_PIPER_MODEL):
        try:
            piper_url = "https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en_US-lessac-medium.onnx"
            logging.info(f"Downloading Piper model from {piper_url}...")
            
            urllib.request.urlretrieve(piper_url, DEFAULT_PIPER_MODEL)
            
            if os.path.exists(DEFAULT_PIPER_MODEL):
                logging.info("✅ Piper model downloaded successfully")
                models_downloaded += 1
            else:
                logging.error("❌ Failed to download Piper model")
                
        except Exception as e:
            logging.error(f"Error downloading Piper model: {e}")
    
    # Note: Wake word models require manual download from Picovoice Console
    if not os.path.exists(DEFAULT_WAKE_WORD_MODEL):
        logging.warning("⚠️ Wake word model not found.")
        logging.info("💡 Download wake word model from: https://console.picovoice.ai/")
        logging.info("💡 Save as: models/wake_words/hey-valspy_linux.ppn")
    
    return models_downloaded > 0 or check_models_available()['piper_tts']

def validate_model_path(model_type: str, model_path: str) -> bool:
    """
    Validate if a model path exists and is accessible.
    
    Args:
        model_type: Type of model ('piper', 'wake_word')
        model_path: Path to the model file
        
    Returns:
        bool: True if model is valid
    """
    if not os.path.exists(model_path):
        logging.error(f"Model file not found: {model_path}")
        return False
    
    if model_type == 'piper' and not model_path.endswith('.onnx'):
        logging.error("Piper model must be .onnx file")
        return False
    
    if model_type == 'wake_word' and not model_path.endswith('.ppn'):
        logging.error("Wake word model must be .ppn file")
        return False
    
    # Check file size (basic validation)
    file_size = os.path.getsize(model_path)
    if file_size == 0:
        logging.error(f"Model file is empty: {model_path}")
        return False
    
    if model_type == 'piper' and file_size < 1000000:  # 1MB
        logging.warning(f"Piper model file seems very small: {file_size} bytes")
    
    return True

def get_model_info(model_path: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a model file.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        Dict with model information or None if error
    """
    if not os.path.exists(model_path):
        return None
    
    try:
        file_stats = os.stat(model_path)
        model_info = {
            'path': model_path,
            'size_bytes': file_stats.st_size,
            'size_mb': round(file_stats.st_size / (1024 * 1024), 2),
            'modified_time': file_stats.st_mtime,
            'file_type': os.path.splitext(model_path)[1].lower()
        }
        
        # Add model-specific info
        if model_info['file_type'] == '.onnx':
            model_info['type'] = 'piper_tts'
            model_info['description'] = 'Piper Text-to-Speech Voice Model'
        elif model_info['file_type'] == '.ppn':
            model_info['type'] = 'wake_word'
            model_info['description'] = 'Picovoice Wake Word Model'
        else:
            model_info['type'] = 'unknown'
            model_info['description'] = 'Unknown Model Type'
        
        return model_info
        
    except Exception as e:
        logging.error(f"Error getting model info for {model_path}: {e}")
        return None

def cleanup_models() -> Dict[str, int]:
    """
    Clean up corrupted or invalid model files.
    
    Returns:
        Dict with cleanup statistics
    """
    cleanup_stats = {
        'removed_files': 0,
        'total_cleaned_size': 0
    }
    
    # Check all model directories
    model_dirs = [PIPER_MODELS_DIR, WAKE_WORD_MODELS_DIR]
    
    for model_dir in model_dirs:
        if os.path.exists(model_dir):
            for file in os.listdir(model_dir):
                file_path = os.path.join(model_dir, file)
                try:
                    # Remove empty files
                    if os.path.getsize(file_path) == 0:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        cleanup_stats['removed_files'] += 1
                        cleanup_stats['total_cleaned_size'] += file_size
                        logging.info(f"Removed empty model file: {file}")
                        
                    # Remove files with invalid extensions
                    elif not (file.endswith('.onnx') or file.endswith('.ppn')):
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        cleanup_stats['removed_files'] += 1
                        cleanup_stats['total_cleaned_size'] += file_size
                        logging.info(f"Removed invalid model file: {file}")
                        
                except Exception as e:
                    logging.error(f"Error cleaning up model file {file}: {e}")
    
    return cleanup_stats

# Initialize models directory structure on import
def initialize_models_directory():
    """Initialize the models directory structure"""
    directories = [PIPER_MODELS_DIR, WAKE_WORD_MODELS_DIR]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create .gitkeep to preserve empty directories in git
        gitkeep_file = os.path.join(directory, '.gitkeep')
        if not os.path.exists(gitkeep_file):
            with open(gitkeep_file, 'w') as f:
                f.write('# This file ensures the directory is preserved in git\n')

# Run initialization
initialize_models_directory()

# Export public functions
__all__ = [
    'PIPER_MODELS_DIR',
    'WAKE_WORD_MODELS_DIR',
    'DEFAULT_PIPER_MODEL',
    'DEFAULT_WAKE_WORD_MODEL',
    'check_models_available',
    'get_available_models',
    'download_default_models',
    'validate_model_path',
    'get_model_info',
    'cleanup_models'
]