import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.brick import (
    TouchSensor,
    EV3UltrasonicSensor,
    EV3ColorSensor,
    EV3GyroSensor,
    Motor,
)
from utils import sound

# Drum motor initialization
LEFT_CONTAINMENT_MOTOR = Motor("A")
RIGHT_CONTAINMENT_MOTOR = Motor("B")
LEFT_LOCOMOTION_MOTOR = Motor("C")
RIGHT_LOCOMOTION_MOTOR = Motor("D")

# Sensors
GYRO = EV3GyroSensor(1, mode="both")
COLOR = EV3ColorSensor(2)

# Buttons
BUTTON = TouchSensor(3)
EMERGENCY_BUTTON = TouchSensor(4)
