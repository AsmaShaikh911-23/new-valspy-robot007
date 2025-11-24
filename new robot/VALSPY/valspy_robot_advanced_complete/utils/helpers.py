import os
import sys
import logging
import json
import time
import subprocess
import psutil
from typing import Dict, Any, Optional

def setup_logging(log_level='INFO', log_file='logs/valspy_robot.log'):
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce verbosity for some noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate robot configuration"""
    required_sections = ['motor', 'ultrasonic', 'camera', 'personality']
    
    for section in required_sections:
        if section not in config:
            logging.error(f"Missing required config section: {section}")
            return False
    
    # Validate motor pins
    motor_pins = config['motor']
    required_pins = ['left_pins', 'right_pins']
    for pins in required_pins:
        if pins not in motor_pins or len(motor_pins[pins]) != 3:
            logging.error(f"Invalid motor pins configuration for {pins}")
            return False
    
    # Validate sensor distances
    ultrasonic = config['ultrasonic']
    if ultrasonic['stop_distance'] >= ultrasonic['warning_distance']:
        logging.error("Stop distance should be less than warning distance")
        return False
    
    return True

def get_system_info() -> Dict[str, Any]:
    """Get Raspberry Pi system information"""
    try:
        # CPU temperature
        temp = None
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
        except:
            temp = 0.0
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Battery (if available)
        battery = None
        try:
            battery = psutil.sensors_battery()
        except:
            pass
        
        system_info = {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'temperature': temp,
            'disk_usage': disk.percent,
            'battery_level': battery.percent if battery else 100.0,
            'boot_time': psutil.boot_time(),
            'uptime': time.time() - psutil.boot_time()
        }
        
        return system_info
        
    except Exception as e:
        logging.error(f"Error getting system info: {e}")
        return {}

def check_camera_available() -> bool:
    """Check if camera is available"""
    try:
        import picamera
        with picamera.PiCamera() as camera:
            return True
    except:
        return False

def check_audio_available() -> bool:
    """Check if audio system is available"""
    try:
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_gpio_available() -> bool:
    """Check if GPIO is available"""
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        return True
    except:
        return False

def get_network_info() -> Dict[str, str]:
    """Get network information"""
    try:
        hostname = os.uname().nodename
        
        # Get IP address
        ip_result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        ip_address = ip_result.stdout.strip().split(' ')[0] if ip_result.returncode == 0 else 'Unknown'
        
        return {
            'hostname': hostname,
            'ip_address': ip_address
        }
    except:
        return {'hostname': 'Unknown', 'ip_address': 'Unknown'}

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def safe_json_load(filepath: str, default: Any = None) -> Any:
    """Safely load JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return default

def safe_json_save(data: Any, filepath: str) -> bool:
    """Safely save data to JSON file"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON to {filepath}: {e}")
        return False

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def is_raspberry_pi() -> bool:
    """Check if running on Raspberry Pi"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            return 'Raspberry Pi' in cpuinfo
    except:
        return False

def get_pi_model() -> str:
    """Get Raspberry Pi model"""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip().replace('\x00', '')
            return model
    except:
        return "Unknown"

def cleanup_resources():
    """Cleanup system resources"""
    try:
        import RPi.GPIO as GPIO
        GPIO.cleanup()
    except:
        pass
    
    try:
        import pygame
        pygame.quit()
    except:
        pass

class PerformanceTimer:
    """Context manager for performance timing"""
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        logging.debug(f"⏱️ {self.name} took {elapsed:.3f}s")