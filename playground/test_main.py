import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.main import SEARCH_HORIZONTAL_DISTANCE, SEARCH_INTO_ROOM_DISTANCE, SEARCH_OUT_OF_DOOR_DISTANCE, SEARCH_RESET_AT_DOOR_DISTANCE, SEARCH_UNTIL_DOOR_DISTANCE
from modules.containment import KP_HEADING, MAX_POWER, MIN_POWER, ORANGE, SLOWDOWN_DIST, search, suck_forward
from modules.hardware import GYRO
from utils.brick import wait_ready_sensors

from modules.locomotion import global_turn, straight, turn
from modules.stop import check_emergency, safe_sleep, stop_all

if __name__ == "__main__":
    wait_ready_sensors()
    
    try:
        suck_forward()
         # Search: snake pattern in big room
        for i in range(5):
            straight(SEARCH_UNTIL_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)
            search(SEARCH_INTO_ROOM_DISTANCE, SEARCH_RESET_AT_DOOR_DISTANCE)
            if i != 4:
                straight(SEARCH_OUT_OF_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                global_turn("left", -90)
                straight(SEARCH_HORIZONTAL_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                global_turn("right", 0)
    except Exception as e:
        stop_all()
        print(f"{e}")
        sys.exit(1)