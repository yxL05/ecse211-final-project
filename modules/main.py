import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.hardware import * 
from utils.brick import wait_ready_sensors
from modules.locomotion import *
from modules.containment import *

DROP1 = True
DROP2 = True

NAVIGATION_OUT_OF_SPAWN = 1300
NAVIGATION_TO_BIG_ROOM = -1550
NAVIGATION_BIG_ROOM_TO_DOOR = -500

NAVIGATION_OUT_OF_BIG_ROOM = 300
NAVIGATION_TO_ROOM_2 = 1250
NAVIGATION_ROOM_2_TO_DOOR = -700
NAVIGATION2_DISTANCE4 = 0

NAVIGATION3_DISTANCE1 = 300
NAVIGATION3_DISTANCE2 = -1350
NAVIGATION3_DISTANCE3 = -700
NAVIGATION3_DISTANCE4 = 0

NAVIGATION4_DISTANCE1 = 0

SEARCH_INTO_ROOM_DISTANCE = -1050
SEARCH_RESET_AT_DOOR_DISTANCE = 1500
SEARCH_OUT_OF_DOOR_DISTANCE = 200
SEARCH_UNTIL_DOOR_DISTANCE = -700
SEARCH_HORIZONTAL_DISTANCE = -300

LEFT = "left"
RIGHT = "right"
ORANGE = "orange"
GREEN = "green"
BED = "bed"

wait_ready_sensors()

if __name__ == "__main__":
    try:
        start = False
        while True:
            check_emergency()

            #GRABBING
            suck_forward()

            #NAVIGATION1
            global_turn("left", -90)
            go_forward_target_slow(NAVIGATION_OUT_OF_SPAWN, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("left", -180)
            go_forward_target_slow(NAVIGATION_TO_BIG_ROOM, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("right", -90)
            
            #SEARCH1
            for i in range(2):
                go_forward_target_slow(SEARCH_UNTIL_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)
                search(SEARCH_INTO_ROOM_DISTANCE)
                go_forward_target_slow(SEARCH_RESET_AT_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)
                if i != 2:
                    go_forward_target_slow(SEARCH_OUT_OF_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                    global_turn("left", -180)
                    go_forward_target_slow(SEARCH_HORIZONTAL_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                    global_turn("right", -90)

            #NAVIGATION2
            # Out of room after last snake iteration
            go_forward_target_slow(NAVIGATION_OUT_OF_BIG_ROOM, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("left", -180)
            go_forward_target_slow(NAVIGATION_TO_ROOM_2, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("left", -270)
            go_forward_target_slow(NAVIGATION_ROOM_2_TO_DOOR, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

            #SEARCH2
            search(SEARCH_INTO_ROOM_DISTANCE)
            go_forward_target_slow(SEARCH_RESET_AT_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

            #NAVIGATION3
            go_forward_target_slow(NAVIGATION3_DISTANCE1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("left", -360)
            go_forward_target_slow(NAVIGATION3_DISTANCE2, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("right", -270)
            go_forward_target_slow(NAVIGATION3_DISTANCE3, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

            #SEARCH3
            search(SEARCH_INTO_ROOM_DISTANCE)
            go_forward_target_slow(SEARCH_RESET_AT_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

            #NAVIGATION4
            go_forward_target_slow(NAVIGATION4_DISTANCE1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            play_sound()

    except Exception as e:
        stop_all()
        print(f"{e}")
        sys.exit(1)