import time
import threading
from enum import Enum

class RobotState(Enum):
    BOOTING = "booting"
    READY = "ready"
    ACTIVE = "active"
    SLEEPING = "sleeping"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"

class StateManager:
    def __init__(self):
        self.current_state = RobotState.BOOTING
        self.previous_state = None
        self.state_start_time = time.time()
        self.state_history = []
        self._lock = threading.Lock()
        
        # System health metrics
        self.health_metrics = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'temperature': 0.0,
            'battery_level': 100.0,
            'uptime': 0.0
        }
        
        # Behavior states
        self.behavior_states = {
            'face_tracking': False,
            'obstacle_avoidance': False,
            'voice_listening': False,
            'wake_word_active': False,
            'following_person': False,
            'exploring': False
        }
        
        # Sensor states
        self.sensor_states = {
            'camera_available': False,
            'ultrasonic_available': False,
            'motors_available': False,
            'audio_available': False,
            'display_available': False
        }
    
    def set_state(self, new_state, reason="No reason provided"):
        """Change robot state with reason"""
        with self._lock:
            if new_state != self.current_state:
                self.previous_state = self.current_state
                self.current_state = new_state
                self.state_start_time = time.time()
                
                state_change = {
                    'previous_state': self.previous_state,
                    'new_state': self.current_state,
                    'reason': reason,
                    'timestamp': time.time(),
                    'uptime': self.health_metrics['uptime']
                }
                
                self.state_history.append(state_change)
                
                # Keep only last 100 state changes
                if len(self.state_history) > 100:
                    self.state_history.pop(0)
                
                print(f"🔀 State change: {self.previous_state.value} → {self.current_state.value} - {reason}")
    
    def get_current_state(self):
        """Get current robot state"""
        return self.current_state
    
    def get_state_duration(self):
        """Get how long we've been in current state"""
        return time.time() - self.state_start_time
    
    def set_behavior_state(self, behavior, active):
        """Set behavior state"""
        with self._lock:
            if behavior in self.behavior_states:
                old_state = self.behavior_states[behavior]
                self.behavior_states[behavior] = active
                if old_state != active:
                    print(f"🎭 Behavior {behavior}: {'activated' if active else 'deactivated'}")
    
    def get_behavior_state(self, behavior):
        """Get behavior state"""
        return self.behavior_states.get(behavior, False)
    
    def set_sensor_state(self, sensor, available):
        """Set sensor availability"""
        with self._lock:
            if sensor in self.sensor_states:
                old_state = self.sensor_states[sensor]
                self.sensor_states[sensor] = available
                if old_state != available:
                    status = "available" if available else "unavailable"
                    print(f"📡 Sensor {sensor}: {status}")
    
    def get_sensor_state(self, sensor):
        """Get sensor availability"""
        return self.sensor_states.get(sensor, False)
    
    def update_health_metrics(self, metrics):
        """Update system health metrics"""
        with self._lock:
            self.health_metrics.update(metrics)
            self.health_metrics['uptime'] = time.time() - self.state_history[0]['timestamp'] if self.state_history else 0
    
    def get_health_metrics(self):
        """Get current health metrics"""
        return self.health_metrics.copy()
    
    def get_system_summary(self):
        """Get comprehensive system summary"""
        active_behaviors = [behavior for behavior, active in self.behavior_states.items() if active]
        available_sensors = [sensor for sensor, available in self.sensor_states.items() if available]
        
        summary = {
            'current_state': self.current_state.value,
            'state_duration': self.get_state_duration(),
            'active_behaviors': active_behaviors,
            'available_sensors': available_sensors,
            'health_metrics': self.health_metrics,
            'total_state_changes': len(self.state_history)
        }
        
        return summary
    
    def is_system_healthy(self):
        """Check if system is generally healthy"""
        # Basic health check - at least camera and motors should be available
        critical_sensors = ['camera_available', 'motors_available']
        critical_available = all(self.sensor_states[sensor] for sensor in critical_sensors)
        
        # Check if temperature is within safe limits
        temp_safe = self.health_metrics.get('temperature', 0) < 80.0  # degrees Celsius
        
        # Check if battery is sufficient
        battery_ok = self.health_metrics.get('battery_level', 100) > 10.0
        
        return critical_available and temp_safe and battery_ok
    
    def get_state_history(self, limit=20):
        """Get recent state history"""
        return self.state_history[-limit:] if self.state_history else []