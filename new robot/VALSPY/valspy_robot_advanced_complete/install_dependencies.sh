#!/bin/bash
echo "🤖 Installing VALSPY Advanced Robot Dependencies..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install python3-pip python3-picamera python3-opencv -y
sudo apt install portaudio19-dev libatlas-base-dev espeak -y
sudo apt install libcblas-dev libhdf5-dev libhdf5-serial-dev -y
sudo apt install libatlas-base-dev libjasper-dev libqtgui4 libqt4-test -y
sudo apt install aplay python3-psutil -y

# Install Piper TTS
echo "📥 Installing Piper TTS..."
if [ ! -f "/usr/local/bin/piper" ]; then
    wget -O piper_arm64.tar.gz https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz
    tar xzf piper_arm64.tar.gz
    sudo mv piper /usr/local/bin/
    rm piper_arm64.tar.gz
    echo "✅ Piper TTS installed"
else
    echo "✅ Piper TTS already installed"
fi

# Create directories
mkdir -p models/piper_models
mkdir -p models/wake_words
mkdir -p faces/known_faces
mkdir -p logs

# Download Piper voice model
echo "📥 Downloading Piper voice model..."
if [ ! -f "models/piper_models/en_US-lessac-medium.onnx" ]; then
    wget -O models/piper_models/en_US-lessac-medium.onnx https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en_US-lessac-medium.onnx
    echo "✅ Piper voice model downloaded"
else
    echo "✅ Piper voice model already exists"
fi

# Install Python packages
echo "📦 Installing Python packages..."
pip3 install -r requirements.txt

# Enable camera interface
echo "📷 Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# Set audio output (3.5mm jack)
echo "🔊 Configuring audio..."
amixer cset numid=3 1

# Add user to audio group
sudo usermod -a -G audio $USER

echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy config/api_keys.py.template to config/api_keys.py"
echo "2. Add your OpenAI and Picovoice API keys"
echo "3. Download wake word model from Picovoice Console:"
echo "   - Go to: https://console.picovoice.ai/"
echo "   - Create 'Hey Valspy' wake word"
echo "   - Download for Linux and save as: models/wake_words/hey-valspy_linux.ppn"
echo "4. Train face recognition: python3 utils/face_trainer.py"
echo "5. Run the robot: python3 main.py"
echo ""
echo "🔧 For advanced setup, run: ./setup_advanced_features.sh"