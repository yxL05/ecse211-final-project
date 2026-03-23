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

from hardware import *
from stop import *

IN_POWER = 50
OUT_POWER = 30
OUT_POWER_2 = 50
IN_TIME = 5
OUT_TIME = 0.3
OUT_TIME_2 = 5             

wait_ready_sensors()


def _suck_forward(move_power, grab_power=IN_POWER, t=IN_TIME):    
    LEFT_CONTAINMENT_MOTOR.set_power(grab_power)
    RIGHT_CONTAINMENT_MOTOR.set_power(grab_power)

    LEFT_LOCOMOTION_MOTOR.set_power(move_power)
    RIGHT_LOCOMOTION_MOTOR.set_power(move_power)

    time.sleep(t) 

    stop_drive()
    stop_grab()

def _blow(power=OUT_POWER, t=OUT_TIME):
    LEFT_CONTAINMENT_MOTOR.set_power(power * -1)
    RIGHT_CONTAINMENT_MOTOR.set_power(power * -1)

    time.sleep(t) 

    stop_grab()

def suck_forward():
    _suck_forward(move_power=10)

def blow_1():
    _blow()

def blow_2():
    _blow(OUT_POWER_2, OUT_TIME_2)

if __name__ == "__main__":
    while True:
        _suck_forward(move_power=10)
        time.sleep(3)
        _blow()
        time.sleep(3)
        _blow(OUT_POWER_2, OUT_TIME_2)
        time.sleep(0.01)
