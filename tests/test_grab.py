import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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

# Buttons
BUTTON = TouchSensor(3)

# Grab state
grab_on = False

IN_POWER = 50
OUT_POWER = 30
OUT_POWER_2 = 50
IN_TIME = 5
OUT_TIME = 0.3
OUT_TIME_2 = 5

# Turning constants
TURNING_ENCODER_TARGET = 305     
TURNING_ENCODER_TARGET_RIGHT = 310
CORRECTION_FACTOR = 0.6
MAX_CORRECTION = 8              

wait_ready_sensors()

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def stop_drive():
    LEFT_MOTOR.set_power(0)
    RIGHT_MOTOR.set_power(0)

def stop_grab():
    FIRST_MOTOR.set_power(0)
    SECOND_MOTOR.set_power(0)

def grab_in_forward(move_power, grab_power=IN_POWER, t=IN_TIME):    
    FIRST_MOTOR.set_power(grab_power)
    SECOND_MOTOR.set_power(grab_power)

    LEFT_MOTOR.set_power(move_power)
    RIGHT_MOTOR.set_power(move_power)

    time.sleep(t) 

    stop_drive()
    stop_grab()

def grab_in(grab_power=IN_POWER, t=IN_TIME):    
    FIRST_MOTOR.set_power(grab_power)
    SECOND_MOTOR.set_power(grab_power)

    time.sleep(t)

    stop_grab()

def grab_out(power=OUT_POWER, t=OUT_TIME):
    FIRST_MOTOR.set_power(power * -1)
    SECOND_MOTOR.set_power(power * -1)

    time.sleep(t) 

    stop_grab()

def go_forward(duration, power):
    LEFT_MOTOR.set_power(power)
    RIGHT_MOTOR.set_power(power)
    time.sleep(duration)
    stop_drive()

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

if __name__ == "__main__":
    while True:
        if BUTTON.is_pressed():
            grab_on = not grab_on
            time.sleep(0.3)

        if grab_on:
            grab_in_forward(move_power=10)
            time.sleep(3)
            grab_out()
            time.sleep(3)
            grab_out(OUT_POWER_2, OUT_TIME_2)
            grab_on = False
        else:
            FIRST_MOTOR.set_power(0)
            SECOND_MOTOR.set_power(0)
            stop_drive()

        time.sleep(0.01)
