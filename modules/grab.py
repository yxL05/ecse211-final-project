import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.brick import TouchSensor, Motor
import time

DELAY = 0.3

# Drum motor initialization
FIRST_MOTOR = Motor("A")
SECOND_MOTOR = Motor("B")

# Drum state
POWER = 50
drum_on = False
direction = 1

# Sensor initialization
BUTTON1 = TouchSensor(3)
BUTTON2 = TouchSensor(4)


def handle_drum_inputs():
    global drum_on, direction

    # Toggle spinning
    if BUTTON1.is_pressed():
        drum_on = not drum_on
        time.sleep(DELAY)

    # Change direction
    if BUTTON2.is_pressed():
        direction *= -1
        time.sleep(DELAY)


def update_drum(power=POWER):
    if drum_on:
        FIRST_MOTOR.set_power(power * direction)
        SECOND_MOTOR.set_power(power * direction)
    else:
        FIRST_MOTOR.set_power(0)
        SECOND_MOTOR.set_power(0)
