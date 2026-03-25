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
EMERGENCY_BUTTON = TouchSensor(2)

# Sounds
SOUND = sound.Sound(duration=0.3, pitch="A4", volume=100)
def play_sound():
    SOUND.play()
    SOUND.wait_done()
