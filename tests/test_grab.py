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
LEFT_CONTAINMENT_MOTOR = Motor("A")
RIGHT_CONTAINMENT_MOTOR = Motor("B")
LEFT_LOCOMOTION_MOTOR = Motor("C")
RIGHT_LOCOMOTION_MOTOR = Motor("D")

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

def _stop_drive():
    LEFT_LOCOMOTION_MOTOR.set_power(0)
    RIGHT_LOCOMOTION_MOTOR.set_power(0)

def _stop_grab():
    LEFT_CONTAINMENT_MOTOR.set_power(0)
    RIGHT_CONTAINMENT_MOTOR.set_power(0)

def _suck_forward(move_power, grab_power=IN_POWER, t=IN_TIME):    
    LEFT_CONTAINMENT_MOTOR.set_power(grab_power)
    RIGHT_CONTAINMENT_MOTOR.set_power(grab_power)

    LEFT_LOCOMOTION_MOTOR.set_power(move_power)
    RIGHT_LOCOMOTION_MOTOR.set_power(move_power)

    time.sleep(t) 

    _stop_drive()
    _stop_grab()

def _blow(power=OUT_POWER, t=OUT_TIME):
    LEFT_CONTAINMENT_MOTOR.set_power(power * -1)
    RIGHT_CONTAINMENT_MOTOR.set_power(power * -1)

    time.sleep(t) 

    _stop_grab()

def suck_forward():
    _suck_forward(move_power=10)

def blow_1():
    _blow()

def blow_2():
    _blow(OUT_POWER_2, OUT_TIME_2)

if __name__ == "__main__":
    while True:
        if BUTTON.is_pressed():
            grab_on = not grab_on
            time.sleep(0.3)

        if grab_on:
            _suck_forward(move_power=10)
            time.sleep(3)
            _blow()
            time.sleep(3)
            _blow(OUT_POWER_2, OUT_TIME_2)
            grab_on = False
        else:
            LEFT_CONTAINMENT_MOTOR.set_power(0)
            RIGHT_CONTAINMENT_MOTOR.set_power(0)
            _stop_drive()

        time.sleep(0.01)
