import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.hardware import * 
from utils.brick import wait_ready_sensors
from modules.locomotion import *
from modules.containment import *

DROP1 = True
DROP2 = True

NAVIGATION1_DISTANCE1 = 1450
NAVIGATION1_DISTANCE2 = -1450
NAVIGATION1_DISTANCE3 = -500

NAVIGATION2_DISTANCE1 = 300
NAVIGATION2_DISTANCE2 = 1450
NAVIGATION2_DISTANCE3 = -500
NAVIGATION2_DISTANCE4 = 0

NAVIGATION3_DISTANCE1 = 300
NAVIGATION3_DISTANCE2 = -1450
NAVIGATION3_DISTANCE3 = -500
NAVIGATION3_DISTANCE4 = 0

NAVIGATION4_DISTANCE1 = 0

SEARCH_DISTANCE1 = -890
SEARCH_DISTANCE2 = 950
SEARCH_DISTANCE3 = -300

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
            turn("left")
            go_forward_target_slow(NAVIGATION1_DISTANCE1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            turn("left")
            go_forward_target_slow(NAVIGATION1_DISTANCE2, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            turn("right")
            go_forward_target_slow(NAVIGATION1_DISTANCE3, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

            #SEARCH1
            for i in range(3):
                DROP1, DROP2 = search(SEARCH_DISTANCE1)
                go_forward_target_slow(SEARCH_DISTANCE2, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)
                turn("left")
                go_forward_target_slow(SEARCH_DISTANCE3, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                turn("right")

            #NAVIGATION2
            go_forward_target_slow(NAVIGATION2_DISTANCE1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            turn("left")
            go_forward_target_slow(NAVIGATION2_DISTANCE2, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            turn("left")
            go_forward_target_slow(NAVIGATION2_DISTANCE3, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

            #SEARCH2
            DROP1, DROP2 = search()

            #NAVIGATION3
            go_forward_target_slow(NAVIGATION3_DISTANCE1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            turn("left")
            go_forward_target_slow(NAVIGATION3_DISTANCE2, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            turn("right")
            go_forward_target_slow(NAVIGATION3_DISTANCE3, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, ORANGE)

            #SEARCH3
            DROP1, DROP2 = search()

            #NAVIGATION4
            go_forward_target_slow(NAVIGATION4_DISTANCE1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
            play_sound()

    except Exception as e:
        stop_all()
        print(f"{e}")
        sys.exit(1)