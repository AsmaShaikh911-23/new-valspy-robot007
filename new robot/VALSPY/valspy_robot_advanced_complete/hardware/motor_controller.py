import RPi.GPIO as GPIO
import time

class MotorController:
    def __init__(self):
        # L298N Motor Driver Controls TWO channels:
        # LEFT SIDE  = 2 motors (front-left + rear-left)
        # RIGHT SIDE = 2 motors (front-right + rear-right)

        self.MOTOR_LEFT_PINS = {
            'IN1': 17,  # GPIO17
            'IN2': 18,  # GPIO18
            'ENA': 27   # GPIO27 (PWM)
        }
        
        self.MOTOR_RIGHT_PINS = {
            'IN3': 22,  # GPIO22
            'IN4': 23,  # GPIO23
            'ENB': 24   # GPIO24 (PWM)
        }
        
        self.PWM_FREQ = 1000  # 1kHz
        self.setup_done = False
        
    def setup(self):
        """Initialize motor controller"""
        try:
            GPIO.setmode(GPIO.BCM)
            
            # Setup left side pins
            GPIO.setup(self.MOTOR_LEFT_PINS['IN1'], GPIO.OUT)
            GPIO.setup(self.MOTOR_LEFT_PINS['IN2'], GPIO.OUT)
            GPIO.setup(self.MOTOR_LEFT_PINS['ENA'], GPIO.OUT)
            
            # Setup right side pins
            GPIO.setup(self.MOTOR_RIGHT_PINS['IN3'], GPIO.OUT)
            GPIO.setup(self.MOTOR_RIGHT_PINS['IN4'], GPIO.OUT)
            GPIO.setup(self.MOTOR_RIGHT_PINS['ENB'], GPIO.OUT)
            
            # Setup PWM
            self.left_pwm = GPIO.PWM(self.MOTOR_LEFT_PINS['ENA'], self.PWM_FREQ)
            self.right_pwm = GPIO.PWM(self.MOTOR_RIGHT_PINS['ENB'], self.PWM_FREQ)
            
            self.left_pwm.start(0)
            self.right_pwm.start(0)
            
            self.setup_done = True
            print("✅ Motor controller initialized (4 motors → 2 channels)")
            
        except Exception as e:
            print(f"❌ Motor setup error: {e}")
    
    def move_forward(self, speed=50):
        """Move robot forward"""
        if not self.setup_done:
            return
            
        self._left_motor_forward(speed)
        self._right_motor_forward(speed)
    
    def move_backward(self, speed=50):
        """Move robot backward"""
        if not self.setup_done:
            return
            
        self._left_motor_backward(speed)
        self._right_motor_backward(speed)
    
    def turn_left(self, speed=60):
        """Turn left"""
        if not self.setup_done:
            return
            
        self._left_motor_backward(speed)
        self._right_motor_forward(speed)
    
    def turn_right(self, speed=60):
        """Turn right"""
        if not self.setup_done:
            return
            
        self._left_motor_forward(speed)
        self._right_motor_backward(speed)
    
    def stop(self):
        """Stop all motors"""
        if not self.setup_done:
            return
            
        self.left_pwm.ChangeDutyCycle(0)
        self.right_pwm.ChangeDutyCycle(0)
    
    def _left_motor_forward(self, speed):
        GPIO.output(self.MOTOR_LEFT_PINS['IN1'], GPIO.HIGH)
        GPIO.output(self.MOTOR_LEFT_PINS['IN2'], GPIO.LOW)
        self.left_pwm.ChangeDutyCycle(speed)
    
    def _left_motor_backward(self, speed):
        GPIO.output(self.MOTOR_LEFT_PINS['IN1'], GPIO.LOW)
        GPIO.output(self.MOTOR_LEFT_PINS['IN2'], GPIO.HIGH)
        self.left_pwm.ChangeDutyCycle(speed)
    
    def _right_motor_forward(self, speed):
        GPIO.output(self.MOTOR_RIGHT_PINS['IN3'], GPIO.HIGH)
        GPIO.output(self.MOTOR_RIGHT_PINS['IN4'], GPIO.LOW)
        self.right_pwm.ChangeDutyCycle(speed)
    
    def _right_motor_backward(self, speed):
        GPIO.output(self.MOTOR_RIGHT_PINS['IN3'], GPIO.LOW)
        GPIO.output(self.MOTOR_RIGHT_PINS['IN4'], GPIO.HIGH)
        self.right_pwm.ChangeDutyCycle(speed)
    
    def cleanup(self):
        """Cleanup GPIO"""
        self.stop()
        if self.setup_done:
            self.left_pwm.stop()
            self.right_pwm.stop()
            GPIO.cleanup()
