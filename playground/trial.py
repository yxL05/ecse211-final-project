D10 = 1450
D1 = 1450
D2 = 1450
D3 = 250

import sys
from pathlib import Path

import time

from kalangyro import *

DISTANCE = 880
MAX_POWER = 40
MIN_POWER = 25
SLOWDOWN_DIST = 300
KP_HEADING = 1.2

def straight_test():
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)

def backward_test():
    go_forward_target_slow(-DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)


def orange_test():
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, "orange")
    safe_sleep(1)

def backward_orange_test():
    go_forward_target_slow(-DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, "orange")
    safe_sleep(1)

def bed_test():
    detected_color = go_forward_target_slow(-DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST, "bed")
    print(f"Detected color: {detected_color}")
    safe_sleep(1)
    return detected_color
    


if __name__ == "__main__":
    try:
        start = False
        while True:
            check_emergency()
            if BUTTON.is_pressed():
                start = True

                safe_sleep(0.3)

            if start:
                #go_forward_target_slow(D10)
                #turn("right")
                color_test()
                grab_in_forward(move_power=10)
                turn("left")
                go_forward_target_slow(D1, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                turn("right")

                go_forward_target_slow(D2, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                turn("left")
                
                backward_orange_test()
                for i in (range(3)):
                    bed = bed_test()
                    print(bed)
                    if bed == "green":
                        play_sound()
                    if bed == "red":
                        #exit code here
                        print("found red")
                    orange_test()
                    turn("right")
                    go_forward_target_slow(D3, MAX_POWER * 0.8, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                    turn("left")
                    backward_orange_test()



                orange_test()
                bed_test()

                start = False

            safe_sleep(0.01)

    except Exception as e:
        stop_all()
        print(f"{e}")
        sys.exit(1)
