from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

camera_servo_hor = None
camera_servo_ver = None

# --- Control Variables ---
DEAD_ZONE = 3    # New: Ignore joystick values between -5 and 5. This "saves" the position.
SMOOTH_FACTOR = 0.03  # New: Lower value = smoother/slower movement (e.g., 0.1 to 0.5)

# bottom vertical limit
Y_LIMIT_TOP = -1
Y_LIMIT_BOTTOM = 0.2

Y_AXIS_INVERT = True
X_AXIS_INVERT = True

# Initialize current servo positions to prevent jumping on startup
current_x_value = 0.0 # Servo value range: -1.0 to 1.0 (center)
current_y_value = 0.0 # Servo value range: -1.0 to 1.0 (center)

def setup():
    global camera_servo_hor, camera_servo_ver
    
    factory = PiGPIOFactory()
    camera_servo_hor = AngularServo(21, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)  
    camera_servo_ver = AngularServo(20, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)

def set_servo_input(hor_pos, ver_pos):
    global current_x_value, current_y_value, camera_servo_hor, camera_servo_ver
    
    # Apply inversion settings
    if X_AXIS_INVERT:
        hor_pos = -hor_pos
    
    if Y_AXIS_INVERT:
        ver_pos = -ver_pos
    
    # --- X-Axis Logic ---
    if abs(hor_pos) >= DEAD_ZONE:
        # Map joystick [-100,100] to servo value [-1.0,1.0]
        target_x_value = hor_pos / 100.0
        # Smooth interpolation
        current_x_value += (target_x_value - current_x_value) * SMOOTH_FACTOR
    
    # --- Y-Axis Logic ---
    if abs(ver_pos) >= DEAD_ZONE:
        target_y_value = ver_pos / 100.0
        # Smooth interpolation
        current_y_value += (target_y_value - current_y_value) * SMOOTH_FACTOR
        # Apply vertical limit
        if current_y_value > Y_LIMIT_BOTTOM:
            current_y_value = Y_LIMIT_BOTTOM
    
    # Clamp values to [-1.0, 1.0] range
    current_x_value = max(-1.0, min(1.0, current_x_value))
    current_y_value = max(-1.0, min(1.0, current_y_value))
    
    # Apply to servos
    camera_servo_hor.value = current_x_value
    camera_servo_ver.value = current_y_value
