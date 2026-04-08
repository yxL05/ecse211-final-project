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
SUCK_FORWARD_DISTANCE = 170
DISTANCE = 450
FALLBACK_DISTANCE = -100
MAX_POWER = 40
MIN_POWER = 20
SUCK_FORWARD_POWER = 10
SLOWDOWN_DIST = 300
KP_HEADING = 1.7

def _blow(power=OUT_POWER, t=OUT_TIME):
    straight(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    turn("left", 180)
    LEFT_CONTAINMENT_MOTOR.set_power(power * -1)
    RIGHT_CONTAINMENT_MOTOR.set_power(power * -1)
    safe_sleep(t)
    stop_grab()
    play_sound()
    straight(FALLBACK_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    turn("right", 180)
    straight(3 * FALLBACK_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)

def suck_forward():
    LEFT_CONTAINMENT_MOTOR.set_power(IN_POWER)
    RIGHT_CONTAINMENT_MOTOR.set_power(IN_POWER)

    straight(SUCK_FORWARD_DISTANCE, SUCK_FORWARD_POWER, KP_HEADING, SUCK_FORWARD_POWER, SLOWDOWN_DIST)

    stop_drive()
    stop_grab()

def search(SEARCH_DISTANCE):
    global BLOW1, BLOW2
    DETECTED = straight(SEARCH_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, BED)
    if DETECTED == GREEN:
        if BLOW1:
            _blow()
            BLOW1 = False
        else:
            _blow(OUT_POWER_2, OUT_TIME_2)
            BLOW2 = False
    return DETECTED
    
if __name__ == "__main__":
    while True:
        wait_ready_sensors()
        suck_forward()
        time.sleep(3)
        _blow()
        time.sleep(3)
        _blow(OUT_POWER_2, OUT_TIME_2)
        time.sleep(0.01)
