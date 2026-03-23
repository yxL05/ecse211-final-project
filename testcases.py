import sys
import time
from test_gyro import (
    go_forward_target_slow,
    turn,
    BUTTON,
    EMERGENCY_BUTTON,
    check_emergency,
    safe_sleep,
    stop_all,
    global_turn,
)

DISTANCE = 400
MAX_POWER = 40
MIN_POWER = 10
SLOWDOWN_DIST = 10
KP_HEADING = 1.2

def straight_test():
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)

def turnstraight_test():
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)
    turn("left")
    safe_sleep(1)
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)
    turn("right")
    safe_sleep(1)
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)

def left_square_test():
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)
    turn("left")
    safe_sleep(1)
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)
    turn("left")
    safe_sleep(1)
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)
    turn("left")
    safe_sleep(1)
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)
    turn("left")
    safe_sleep(1)

def right_square_test():
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)
    turn("right")
    safe_sleep(1)
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)
    turn("right")
    safe_sleep(1)
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)
    turn("right")
    safe_sleep(1)
    go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
    safe_sleep(1)
    turn("right")
    safe_sleep(1)

def global_turn_test():
    global_turn("right", 90)
    safe_sleep(1)
    global_turn("right", 180)
    safe_sleep(1)
    global_turn("right", 270)
    safe_sleep(1)
    global_turn("right", 360)
    safe_sleep(1)
    global_turn("left", 270)
    safe_sleep(1)
    global_turn("left", 180)
    safe_sleep(1)
    global_turn("left", 0)
    safe_sleep(1)
    global_turn("left", -90)
    safe_sleep(1)
    global_turn("left", -180)
    safe_sleep(1)
    global_turn("right", 0)
    safe_sleep(1)

if __name__ == "__main__":
    try:
        start = False
        while True:
            check_emergency()

            if BUTTON.is_pressed():
                start = True
                safe_sleep(0.3)

            if start:
                straight_test()

                start = False

            safe_sleep(0.01)

    except Exception as e:
        stop_all()
        print(f"{e}")
        sys.exit(1)