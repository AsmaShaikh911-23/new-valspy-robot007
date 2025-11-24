import time
import random

class ObstacleAvoidance:
    def __init__(self, ultrasonic, motors, personality):
        self.ultrasonic = ultrasonic
        self.motors = motors
        self.personality = personality
        
        self.last_obstacle_time = 0
        self.avoidance_state = "clear"
        
    def update(self):
        """Update obstacle avoidance behavior"""
        distance = self.ultrasonic.get_distance()
        
        if self.ultrasonic.is_obstacle_detected():
            self._handle_obstacle(distance)
        elif self.ultrasonic.is_obstacle_near():
            self._handle_near_obstacle(distance)
        else:
            self._handle_clear_path()
    
    def _handle_obstacle(self, distance):
        """Handle immediate obstacle"""
        print(f"🚨 Obstacle detected! Distance: {distance}cm")
        self.motors.stop()
        
        # React emotionally
        if time.time() - self.last_obstacle_time > 10:  # Only react every 10s
            self.personality.set_emotion("scared", f"Obstacle too close! {distance}cm")
        
        # Avoidance maneuver
        if random.choice([True, False]):
            self.motors.turn_left(60)
            time.sleep(0.5)
        else:
            self.motors.turn_right(60)
            time.sleep(0.5)
            
        self.motors.stop()
        self.last_obstacle_time = time.time()
        self.avoidance_state = "avoiding"
    
    def _handle_near_obstacle(self, distance):
        """Handle nearby obstacle"""
        if self.avoidance_state != "near":
            print(f"⚠️ Obstacle nearby: {distance}cm")
            self.personality.set_emotion("curious", f"Something is nearby: {distance}cm")
            
        # Slow down and proceed with caution
        self.motors.move_forward(20)
        self.avoidance_state = "near"
    
    def _handle_clear_path(self):
        """Handle clear path"""
        if self.avoidance_state != "clear":
            self.personality.set_emotion("happy", "Path is clear now!")
            self.avoidance_state = "clear"