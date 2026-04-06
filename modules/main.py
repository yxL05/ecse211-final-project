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

NAVIGATION4_DISTANCE1 = 1450

SEARCH_INTO_ROOM_DISTANCE = -1050
SEARCH_RESET_AT_DOOR_DISTANCE = 1000
SEARCH_OUT_OF_DOOR_DISTANCE = 200
SEARCH_UNTIL_DOOR_DISTANCE = -700
SEARCH_HORIZONTAL_DISTANCE = -100

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

            # Pick up medication
            suck_forward()

            # Navigation: go to big room
            global_turn("left", -90)
            straight(NAVIGATION_OUT_OF_SPAWN, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("left", -180)
            straight(NAVIGATION_TO_BIG_ROOM, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("right", -90)
            
            i = 0
            while i < 5:
            # Search: snake pattern in big room
                straight(SEARCH_UNTIL_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)
                detected = search(SEARCH_INTO_ROOM_DISTANCE, SEARCH_RESET_AT_DOOR_DISTANCE)
                if i != 4:
                    straight(SEARCH_OUT_OF_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                    global_turn("left", -180)

                    if detected == GREEN:
                        straight(3 * SEARCH_HORIZONTAL_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                        i += 1
                    else:
                        straight(SEARCH_HORIZONTAL_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                    global_turn("right", -90)
                i += 1

            # Navigation: out of big room -> go to room 2
            straight(NAVIGATION_OUT_OF_BIG_ROOM, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("left", -180)
            straight(NAVIGATION_TO_ROOM_2, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("left", -270)
            straight(NAVIGATION_ROOM_2_TO_DOOR, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

            # Search: room 2
            search(SEARCH_INTO_ROOM_DISTANCE, SEARCH_RESET_AT_DOOR_DISTANCE)

            # Navigation: go to room 1
            straight(NAVIGATION3_DISTANCE1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("left", -360)
            straight(NAVIGATION3_DISTANCE2, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            global_turn("right", -270)
            straight(NAVIGATION3_DISTANCE3, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

            # Search: room 1
            search(SEARCH_INTO_ROOM_DISTANCE, SEARCH_RESET_AT_DOOR_DISTANCE)

            # Navigation: straight line to spawn -> play victory sound
            straight(NAVIGATION4_DISTANCE1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            play_sound()

    except Exception as e:
        stop_all()
        print(f"{e}")
        sys.exit(1)