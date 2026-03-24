import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.hardware import *

import time
from modules.stop import *

start = False
emergency_stop = False

IN_POWER = 50
OUT_POWER = 30
OUT_POWER_2 = 50
IN_TIME = 5
OUT_TIME = 0.3
OUT_TIME_2 = 5

# Gyro turning constants
TURN_FAST_POWER = 30
TURN_MEDIUM_POWER = 18
TURN_SLOW_POWER = 10
TURN_FINE_POWER = 7
TURN_MIN_POWER = 10
TURN_TOLERANCE = 0.2

GYRO_SETTLE_TIME = 0.1
GYRO_START_SAMPLES = 7
GYRO_LOOP_SAMPLES = 3
GYRO_SAMPLE_DELAY = 0.005

# Encoder-based translation correction during turns
# For a perfect in-place turn:
#   left_encoder + right_encoder ~= 0
TURN_TRANSLATION_KP = 0.08
TURN_TRANSLATION_MAX = 10

# Stall detection / recovery
STALL_ANGLE_EPS = 0.5
STALL_ENCODER_EPS = 3
STALL_TIME = 0.30
STALL_BOOST_POWER = 14
STALL_MAX_BOOSTS = 3

def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def _get_gyro_angle():
    reading = GYRO.get_both_measure()
    if reading is None:
        return None
    return reading[0]


def _get_stable_gyro_angle(samples=GYRO_START_SAMPLES, delay=GYRO_SAMPLE_DELAY):
    values = []

    for _ in range(samples):
        check_emergency()
        angle = _get_gyro_angle()
        if angle is not None:
            values.append(angle)
        time.sleep(delay)

    if not values:
        return None

    return sum(values) / len(values)

def _get_turn_power_from_error(error):
    error = abs(error)

    if error > 40:
        return TURN_FAST_POWER
    elif error > 20:
        return TURN_MEDIUM_POWER
    elif error > 8:
        return TURN_SLOW_POWER
    elif error > TURN_TOLERANCE:
        return TURN_FINE_POWER
    else:
        return 0


def _set_turn_power(direction, base_power, translation_correction):
    """
    Apply turning power plus a forward/backward correction to keep
    the robot rotating more nearly in place.

    translation_correction:
        positive  -> bias both wheels slightly backward
        negative  -> bias both wheels slightly forward
    """
    if direction == "right":
        left_power = base_power - translation_correction
        right_power = -base_power - translation_correction
    else:
        left_power = -base_power - translation_correction
        right_power = base_power - translation_correction

    left_power = _clamp(left_power, -100, 100)
    right_power = _clamp(right_power, -100, 100)

    LEFT_LOCOMOTION_MOTOR.set_power(left_power)
    RIGHT_LOCOMOTION_MOTOR.set_power(right_power)

    return left_power, right_power

def _is_color(color, r, g, b):
    if color == "red":
        return r > 140 and r > (g * 6) and r > (b * 7)

    elif color == "green":
        return g > 180 and g > (r * 1.5) and g > (b * 5.5)

    elif color == "orange":
        return r > 200 and g < 100 and r > (b * 3) and g > (b * 2)

    else:
        return False


def turn(direction, angle=90):
    if direction not in ("left", "right"):
        raise ValueError("direction must be 'left' or 'right'")
    if angle <= 0:
        raise ValueError("angle must be positive")

    check_emergency()
    stop_drive()

    # Reset encoders so turn-centering correction starts from zero
    LEFT_LOCOMOTION_MOTOR.reset_encoder()
    RIGHT_LOCOMOTION_MOTOR.reset_encoder()

    # Let the gyro settle before sampling the start angle
    safe_sleep(GYRO_SETTLE_TIME)

    start_angle = _get_stable_gyro_angle(samples=GYRO_START_SAMPLES)
    if start_angle is None:
        raise RuntimeError("Gyro reading unavailable")

    if direction == "right":
        target_angle = start_angle + angle
    else:
        target_angle = start_angle - angle

    turn_start_time = time.time()
    loop_count = 0
    exit_reason = "unknown"

    # Stall tracking
    last_progress_time = time.time()
    last_progress_angle = start_angle
    last_left_enc = 0
    last_right_enc = 0
    stall_boosts_used = 0


    while True:
        check_emergency()
        loop_count += 1

        current_angle = _get_stable_gyro_angle(
            samples = GYRO_LOOP_SAMPLES,
            delay = GYRO_SAMPLE_DELAY
        )


        angle_error = target_angle - current_angle

        if abs(angle_error) <= TURN_TOLERANCE:
            exit_reason = "tolerance"
            break

        base_power = _get_turn_power_from_error(angle_error)
        base_power = max(base_power, TURN_MIN_POWER)

        left_enc = LEFT_LOCOMOTION_MOTOR.get_encoder()
        right_enc = RIGHT_LOCOMOTION_MOTOR.get_encoder()

        # Progress detection: either gyro changed, or encoders changed
        angle_progress = abs(current_angle - last_progress_angle)
        encoder_progress = max(abs(left_enc - last_left_enc), abs(right_enc - last_right_enc))

        if angle_progress >= STALL_ANGLE_EPS or encoder_progress >= STALL_ENCODER_EPS:
            last_progress_time = time.time()
            last_progress_angle = current_angle
            last_left_enc = left_enc
            last_right_enc = right_enc

        stalled = (time.time() - last_progress_time) > STALL_TIME

        # Ideal in-place turn: left_enc + right_enc ~= 0
        translation_error = left_enc + right_enc

        translation_correction = _clamp(
            translation_error * TURN_TRANSLATION_KP,
            -TURN_TRANSLATION_MAX,
            TURN_TRANSLATION_MAX
        )

        # If stuck, temporarily boost power to break static friction
        applied_base_power = base_power
        if stalled and stall_boosts_used < STALL_MAX_BOOSTS:
            applied_base_power = max(base_power, STALL_BOOST_POWER)
            stall_boosts_used += 1
            last_progress_time = time.time()


        left_cmd, right_cmd = _set_turn_power(
            direction,
            applied_base_power,
            translation_correction
        )

        # If still stalled after several boosts, give up cleanly
        if stalled and stall_boosts_used >= STALL_MAX_BOOSTS:
            exit_reason = "stall"

            break

        time.sleep(0.01)

    stop_drive()
    safe_sleep(0.05)

def go_forward_target_slow(
    target_degrees,
    max_power=40,
    kp_heading=1.2,
    min_power=25,
    slowdown_distance=200,
    target_color=None
):
    check_emergency()

    LEFT_LOCOMOTION_MOTOR.reset_encoder()
    RIGHT_LOCOMOTION_MOTOR.reset_encoder()

    # Determine direction
    direction = 1 if target_degrees >= 0 else -1
    target_degrees = abs(target_degrees)

    # Lock initial heading
    safe_sleep(GYRO_SETTLE_TIME)
    target_angle = _get_stable_gyro_angle()
    if target_angle is None:
        raise RuntimeError("Gyro unavailable")
    
    DETECTED_COLOR = None

    while True:
        check_emergency()
       
        ############ COLOR STUFF
        if target_color is not None:
            (r, g, b) = COLOR.get_rgb()
     
            if target_color == "bed":
                if _is_color("red", r, g, b):
                    print("Target color detected: red")
                    DETECTED_COLOR = "red"
                    break
                if _is_color("green", r, g, b):
                    print("Target color detected: green")
                    DETECTED_COLOR = "green"
                    break

            elif _is_color("orange", r, g, b):
                print("Target color detected: orange")
                break

        left_enc = LEFT_LOCOMOTION_MOTOR.get_encoder()
        right_enc = RIGHT_LOCOMOTION_MOTOR.get_encoder()

        # Use absolute encoder distance for progress tracking
        avg_enc = abs((left_enc + right_enc) / 2)

        remaining = target_degrees - avg_enc

        if remaining <= 0:
            break

        # --- Slowdown logic ---
        if remaining < slowdown_distance:
            power = max(min_power, max_power * (remaining / slowdown_distance))
        else:
            power = max_power

        # Apply direction (THIS enables backward motion)
        power *= direction

        # --- Gyro heading correction ---
        current_angle = _get_gyro_angle()
        if current_angle is None:
            continue
        heading_error = target_angle - current_angle
        correction = kp_heading * heading_error * 0.90
        left_power = _clamp(power + correction, -100, 100)
        right_power = _clamp(power - correction, -100, 100)

        LEFT_LOCOMOTION_MOTOR.set_power(left_power)
        RIGHT_LOCOMOTION_MOTOR.set_power(right_power)

        time.sleep(0.01)

    stop_drive()
    return DETECTED_COLOR
