from enum import Enum

class CarState(Enum):
    MANUAL_CONTROL = 0
    TOKYO_MODE = 1

# Speed limits per state (0.0 to 1.0)
STATE_SPEED_LIMITS = {
    CarState.MANUAL_CONTROL: 0.5,   # 50% max speed
    CarState.TOKYO_MODE: 1.0,       # 100% max speed
}

current_state = CarState.MANUAL_CONTROL

def switch_state():
    """Switch between MANUAL_CONTROL and TOKYO_MODE"""
    global current_state
    if current_state == CarState.MANUAL_CONTROL:
        transition_to(CarState.TOKYO_MODE)
    else:
        transition_to(CarState.MANUAL_CONTROL)

def transition_to(new_state):
    global current_state
    print(f"Transitioning: {current_state.name} -> {new_state.name}")
    current_state = new_state

def get_speed_limit():
    """Get speed limit based on current state"""
    return STATE_SPEED_LIMITS[current_state]  

def handle_state():
    """Main state dispatcher"""
    if current_state == CarState.MANUAL_CONTROL:
        handle_manual_control()
    elif current_state == CarState.TOKYO_MODE:
        handle_tokyo_mode()

def handle_manual_control():
    """Accept joystick input and control motors/camera"""
    # This is your current main loop behavior
    pass

def handle_tokyo_mode():
    """Execute Tokyo Drift maneuvers"""
    # Implement Tokyo Drift logic here
    pass