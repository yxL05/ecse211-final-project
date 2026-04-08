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
NAVIGATION_TO_BIG_ROOM = -1525
NAVIGATION_BIG_ROOM_TO_DOOR = -500

NAVIGATION_OUT_OF_BIG_ROOM = 300
NAVIGATION_ROOM_2_PREFLIGHT = -1500
NAVIGATION_TO_ROOM_2 = 1550
NAVIGATION_ROOM_2_TO_DOOR = -700
NAVIGATION2_DISTANCE4 = 0

NAVIGATION3_DISTANCE1 = 300
NAVIGATION_TO_ROOM_1 = -1300
NAVIGATION3_DISTANCE3 = -700

NAVIGATION_BACK_TO_SPAWN = 1650

SEARCH_INTO_ROOM_DISTANCE = -1050
SEARCH_RESET_AT_DOOR_DISTANCE = 1500
SEARCH_OUT_OF_DOOR_DISTANCE = 300
SEARCH_UNTIL_DOOR_DISTANCE = -2000
SEARCH_HORIZONTAL_DISTANCE = -131
SEARCH_IGNORE_DISTANCE = 200

LEFT = "left"
RIGHT = "right"
ORANGE = "orange"
GREEN = "green"
RED = "red"
BED = "bed"

BIG_ROOM_ITERATIONS = 5
EXTRA_TURN = False

wait_ready_sensors()

if __name__ == "__main__":
    try:
        check_emergency()

        # Pick up medication
        suck_forward()

        # Navigation: go to big room
        global_turn("left", -90)
        straight(NAVIGATION_OUT_OF_SPAWN, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
        global_turn("left", -180)
        straight(NAVIGATION_TO_BIG_ROOM, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
        global_turn("right", -90)
        
        # Search: snake pattern in big room
        search_room = True
        i = 0
        while i < BIG_ROOM_ITERATIONS:
            straight(SEARCH_UNTIL_DOOR_DISTANCE, MAX_POWER * 0.5, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)
            if search_room:
                detected = search(SEARCH_INTO_ROOM_DISTANCE)
                if detected == RED:
                    straight(SEARCH_IGNORE_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                straight(SEARCH_RESET_AT_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

                if i != BIG_ROOM_ITERATIONS - 1:
                    straight(SEARCH_OUT_OF_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                    multiplier = 3 if i < 4 else 1.5
                    global_turn("left", -180 - i * multiplier)
                    # turn("left", 90)
                    # if detected == GREEN:
                    #     if i < BIG_ROOM_ITERATIONS - 2:
                    #         # If not at iteration before last, move more distance to avoid touching the bed on next search
                    #         # Skip an iteration
                    #         straight(SEARCH_HORIZONTAL_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                    #         straight(SEARCH_HORIZONTAL_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)

                    #         i += 1
                    #     else:
                    #         # If at iteration before last, move to ending position at door entrance but do not go inside room 
                    #         straight(SEARCH_HORIZONTAL_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                    #         search_room = False
                    # else:
                    # if i == 3:
                    #     straight(SEARCH_HORIZONTAL_DISTANCE - 30, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                    # else: 
                    straight(SEARCH_HORIZONTAL_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                    global_turn("right", -90 - i * multiplier)
                    # turn("right", 90)
                    if i == BIG_ROOM_ITERATIONS // 2:
                        EXTRA_TURN = False
            i += 1
            safe_sleep(1)

        # Navigation: out of big room -> go to room 2
        straight(NAVIGATION_OUT_OF_BIG_ROOM, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
        # global_turn("left", -184)
        turn("left", 90)
        straight(NAVIGATION_ROOM_2_PREFLIGHT, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
        straight(NAVIGATION_TO_ROOM_2, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
        # global_turn("left", -274)
        turn("left", 90)
        straight(NAVIGATION_ROOM_2_TO_DOOR, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

        # Search: room 2
        i = 1
        while i <= 2:
            detected = search(SEARCH_INTO_ROOM_DISTANCE)
            straight(SEARCH_RESET_AT_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)
            if detected != None:
                break
            if i != 2:
                straight(SEARCH_OUT_OF_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                # global_turn("left", -364)
                turn("left", 90)
                straight(SEARCH_HORIZONTAL_DISTANCE + 30, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                # global_turn("right", -274)
                turn("right", 90)
                straight(SEARCH_UNTIL_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)
            i += 1

        if i == 0:
            # global_turn("left", -364)
            turn("left", 90)
            straight(SEARCH_HORIZONTAL_DISTANCE + 30, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            straight(SEARCH_HORIZONTAL_DISTANCE + 30, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
        if i == 1:
            # global_turn("left", -364)
            turn("left", 90)
            straight(SEARCH_HORIZONTAL_DISTANCE + 30, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    

        # Navigation: go to room 1
        straight(NAVIGATION3_DISTANCE1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
        # global_turn("left", -364)
        turn("left", 90)
        straight(NAVIGATION_TO_ROOM_1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
        # global_turn("right", -274)
        turn("right", 90)
        turn("left", 15)
        straight(NAVIGATION3_DISTANCE3, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

        # Search: room 1
        search(SEARCH_INTO_ROOM_DISTANCE)
        straight(SEARCH_RESET_AT_DOOR_DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

        # Navigation: straight line to spawn -> play victory sound
        turn("left", 15)
        straight(NAVIGATION_BACK_TO_SPAWN, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
        play_sound()
    except Exception as e:
        stop_all()
        print(f"{e}")
        sys.exit(1)
