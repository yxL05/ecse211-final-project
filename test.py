from utils.brick import (
    TouchSensor,
    EV3UltrasonicSensor,
    EV3ColorSensor,
    Motor,
    wait_ready_sensors
)
from utils import sound
import time

DELAY = 0.3

# Drum motor initialization
FIRST_MOTOR = Motor("A")
SECOND_MOTOR = Motor("B")
LEFT_MOTOR = Motor("C")
RIGHT_MOTOR = Motor("D")

# Drum state
drum_on = False
direction = 1
POWER = 50

# Sensor initialization
BUTTON1 = TouchSensor(3)
BUTTON2 = TouchSensor(4)

# Turning constants
TURNING_ENCODER_TARGET = 305     
TURNING_ENCODER_TARGET_RIGHT = 310
CORRECTION_FACTOR = 0.6
MAX_CORRECTION = 8              

wait_ready_sensors()

def clamp(value, low, high):
    return max(low, min(high, value))

def stop_drive():
    LEFT_MOTOR.set_power(0)
    RIGHT_MOTOR.set_power(0)

def get_turn_power(progress, target):
    if progress < target * 0.7:
        return 35
    elif progress < target * 0.9:
        return 20
    elif progress < target:
        return 10
    else:
        return 0


def turn_90(direction, target=TURNING_ENCODER_TARGET):
    if direction not in ("left", "right"):
        raise ValueError("direction must be 'left' or 'right'")

    LEFT_MOTOR.reset_encoder()
    RIGHT_MOTOR.reset_encoder()

    while True:
        left = abs(LEFT_MOTOR.get_encoder())
        right = abs(RIGHT_MOTOR.get_encoder())

        # Average amount turned so far
        progress = (left + right) / 2

        if progress >= target:
            break

        base_power = get_turn_power(progress, target)

        # Keep both wheels rotating by similar amounts
        error = left - right
        correction = clamp(error * CORRECTION_FACTOR, -MAX_CORRECTION, MAX_CORRECTION)

        if direction == "right":
            # left forward, right backward
            left_power = base_power - correction
            right_power = -(base_power + correction)
        else:
            # left backward, right forward
            left_power = -(base_power - correction)
            right_power = base_power + correction

        LEFT_MOTOR.set_power(left_power)
        RIGHT_MOTOR.set_power(right_power)

        print(f"left: {left}")
        print(f"right: {right}")

        time.sleep(0.01)

    stop_drive()


def go_forward(duration=1.0, power=40):
    LEFT_MOTOR.set_power(power)
    RIGHT_MOTOR.set_power(power)
    time.sleep(duration)
    stop_drive()

# Experimenting
if __name__ == "__main__":
    while True:
        # Toggle spinning
        if BUTTON1.is_pressed():
            drum_on = not drum_on
            time.sleep(0.3)

        # Change direction
        if BUTTON2.is_pressed():
            direction *= -1
            time.sleep(0.3)

        # Control motors A and B
        if drum_on:
            FIRST_MOTOR.set_power(POWER * direction)
            SECOND_MOTOR.set_power(POWER * direction)
        else:
            FIRST_MOTOR.set_power(0)
            SECOND_MOTOR.set_power(0)

        turn_90("left")
        turn_90("right", TURNING_ENCODER_TARGET_RIGHT) 
        
        time.sleep(0.01)
