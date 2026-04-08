import sys
from pathlib import Path
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.hardware import *

class EmergencyStop(Exception):
    pass

def safe_sleep(duration, interval=0.01):
    end_time = time.time() + duration
    while time.time() < end_time:
        check_emergency()
        remaining = end_time - time.time()
        if remaining <= 0:
            break
        time.sleep(min(interval, remaining))

def stop_drive():
    LEFT_LOCOMOTION_MOTOR.set_power(0)
    RIGHT_LOCOMOTION_MOTOR.set_power(0)


def stop_grab():
    LEFT_CONTAINMENT_MOTOR.set_power(0)
    RIGHT_CONTAINMENT_MOTOR.set_power(0)


def stop_all():
    stop_drive()
    stop_grab()

def check_emergency():
    if EMERGENCY_BUTTON.is_pressed():
        stop_all()
        raise EmergencyStop("Emergency stop pressed")
