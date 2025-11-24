#!/bin/bash
echo "🔧 Setting up VALSPY Advanced Features..."

# Create necessary directories
mkdir -p faces/known_faces
mkdir -p models/piper_models
mkdir -p models/wake_words
mkdir -p logs

# Set permissions for audio
sudo usermod -a -G audio $USER

# Create API keys file if it doesn't exist
if [ ! -f "config/api_keys.py" ]; then
    cp "config/api_keys.py.template" "config/api_keys.py"
    echo "⚠️  Please edit config/api_keys.py with your actual API keys"
fi

# Test camera
echo "📷 Testing camera..."
python3 -c "import picamera; camera = picamera.PiCamera(); camera.close(); print('Camera OK')"

# Test audio
echo "🔊 Testing audio..."
aplay -l > /dev/null 2>&1 && echo "Audio output OK" || echo "Audio output may need setup"

echo "✅ Advanced features setup complete!"
echo "🎯 To train face recognition: python3 utils/face_trainer.py"
echo "🎯 To test wake word: python3 -c 'from behaviors.wake_word_detector import WakeWordDetector; print(\"Wake word system ready\")'"