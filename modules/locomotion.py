import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.hardware import (
    LEFT_LOCOMOTION_MOTOR,
    RIGHT_LOCOMOTION_MOTOR,
    GYRO,
    COLOR, 
    BUTTON, 
    EMERGENCY_BUTTON, 
    LEFT_CONTAINMENT_MOTOR, 
    RIGHT_CONTAINMENT_MOTOR,
)

import time
