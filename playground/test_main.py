import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.containment import search
from modules.hardware import GYRO
from utils.brick import wait_ready_sensors

from modules.locomotion import global_turn, straight, turn
from modules.stop import check_emergency, safe_sleep, stop_all

if __name__ == "__main__":
    wait_ready_sensors()
    
    try:
        while True:
            check_emergency()
            global_turn("left", -360)
            safe_sleep(2)
            global_turn("left", -720)
            safe_sleep(2)
            global_turn("right", 0)
            safe_sleep(2)

    except Exception as e:
        stop_all()
        print(f"{e}")
        sys.exit(1)