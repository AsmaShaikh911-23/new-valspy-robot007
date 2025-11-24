import RPi.GPIO as GPIO
import time

class UltrasonicSensor:
    def __init__(self):
        """
        Supports 2 ultrasonic sensors.
        Pin names kept same structure, only S3 removed.
        """

        # Sensor 1 Pins
        self.S1_TRIG = 23
        self.S1_ECHO = 24

        # Sensor 2 Pins
        self.S2_TRIG = 27
        self.S2_ECHO = 22

        self.setup_done = False
        
        # Safety thresholds (in cm)
        self.STOP_DISTANCE = 20
        self.WARNING_DISTANCE = 40
        
    def setup(self):
        """Initialize both ultrasonic sensors"""
        try:
            GPIO.setmode(GPIO.BCM)

            # Sensor 1
            GPIO.setup(self.S1_TRIG, GPIO.OUT)
            GPIO.setup(self.S1_ECHO, GPIO.IN)

            # Sensor 2
            GPIO.setup(self.S2_TRIG, GPIO.OUT)
            GPIO.setup(self.S2_ECHO, GPIO.IN)

            self.setup_done = True
            print("✅ Two ultrasonic sensors initialized")
            
        except Exception as e:
            print(f"❌ Ultrasonic sensor error: {e}")
    
    def read_sensor(self, TRIG, ECHO):
        """Reads one sensor and returns distance in cm"""
        try:
            GPIO.output(TRIG, False)
            time.sleep(0.01)
            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)
            
            pulse_start = time.time()
            timeout = pulse_start + 0.1
            
            while GPIO.input(ECHO) == 0 and pulse_start < timeout:
                pulse_start = time.time()
            
            pulse_end = time.time()
            while GPIO.input(ECHO) == 1 and pulse_end < timeout:
                pulse_end = time.time()
            
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance, 2)
            
            if 2 < distance < 400:
                return distance
            else:
                return 100
        
        except:
            return 100
    
    def get_distance(self):
        """Returns minimum distance among the 2 sensors"""
        if not self.setup_done:
            return 100

        d1 = self.read_sensor(self.S1_TRIG, self.S1_ECHO)
        d2 = self.read_sensor(self.S2_TRIG, self.S2_ECHO)

        return min(d1, d2)
    
    def is_obstacle_detected(self):
        """Check if any sensor detects obstacle within STOP_DISTANCE"""
        distance = self.get_distance()
        return distance < self.STOP_DISTANCE
    
    def is_obstacle_near(self):
        """Check if any sensor detects obstacle within WARNING_DISTANCE"""
        distance = self.get_distance()
        return distance < self.WARNING_DISTANCE
