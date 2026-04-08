import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.main import BIG_ROOM_ITERATIONS, SEARCH_HORIZONTAL_DISTANCE, SEARCH_INTO_ROOM_DISTANCE, SEARCH_OUT_OF_DOOR_DISTANCE, SEARCH_RESET_AT_DOOR_DISTANCE, SEARCH_UNTIL_DOOR_DISTANCE

from modules.containment import BED, GREEN, KP_HEADING, MAX_POWER, MIN_POWER, ORANGE, SLOWDOWN_DIST, search, suck_forward
from modules.hardware import COLOR, GYRO
from utils.brick import EV3GyroSensor, wait_ready_sensors

from modules.locomotion import _get_stable_gyro_angle, _is_color, global_turn, straight, turn
from modules.stop import check_emergency, safe_sleep, stop_all

if __name__ == "__main__":
    wait_ready_sensors()
    
    try:
        straight(-2000, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, BED)
        while True:
            print(f"Color sensor RGB: {COLOR.get_rgb()}")
            safe_sleep(1)
    except Exception as e:
        stop_all()
        print(f"{e}")
        sys.exit(1)