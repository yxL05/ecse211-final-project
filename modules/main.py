import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import modules.hardware as hardware
from utils.brick import wait_ready_sensors
from modules.locomotion import *
from modules.grab import *
from modules.containment import *

wait_ready_sensors()
