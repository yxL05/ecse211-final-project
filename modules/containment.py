import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.brick import (
    TouchSensor,
    EV3UltrasonicSensor,
    EV3ColorSensor,
    Motor,
    wait_ready_sensors,
)
from utils import sound
import time

from modules.hardware import *
from modules.stop import *
from modules.locomotion import *

IN_POWER = 50
OUT_POWER = 30
OUT_POWER_2 = 50
IN_TIME = 2
OUT_TIME = 0.3
OUT_TIME_2 = 5             


GREEN = "green"
ORANGE = "orange"
BED = "bed"

BLOW1 = True
BLOW2 = True

# MOVEMENT CONSTANTS
DISTANCE = -290
MAX_POWER = 30
MIN_POWER = 15
SLOWDOWN_DIST = 300
KP_HEADING = 1.2

def _suck_forward(move_power, grab_power=IN_POWER, t=IN_TIME):    
    LEFT_CONTAINMENT_MOTOR.set_power(grab_power)
    RIGHT_CONTAINMENT_MOTOR.set_power(grab_power)

    LEFT_LOCOMOTION_MOTOR.set_power(move_power)
    RIGHT_LOCOMOTION_MOTOR.set_power(move_power)

    safe_sleep(t) 

    stop_drive()
    stop_grab()

def _blow(power=OUT_POWER, t=OUT_TIME):
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    turn("left", 180)
    LEFT_CONTAINMENT_MOTOR.set_power(power * -1)
    RIGHT_CONTAINMENT_MOTOR.set_power(power * -1)
    safe_sleep(t)
    stop_grab()
    turn("right", 180)
    safe_sleep(1)

def suck_forward():
    _suck_forward(move_power=10)

def search(SEARCH_DISTANCE):
    DETECTED = go_forward_target_slow(SEARCH_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, BED)
    if DETECTED == GREEN:
        play_sound()
        if BLOW1:
            _blow()
            BLOW1 = False
        else:
            _blow(OUT_POWER_2, OUT_TIME_2)
            BLOW2 = False
        return (BLOW1, BLOW2)
    
if __name__ == "__main__":
    while True:
        wait_ready_sensors()
        _suck_forward(move_power=10)
        time.sleep(3)
        _blow()
        time.sleep(3)
        _blow(OUT_POWER_2, OUT_TIME_2)
        time.sleep(0.01)
