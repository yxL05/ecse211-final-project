from utils.brick import (
    TouchSensor,
    EV3UltrasonicSensor,
    EV3ColorSensor,
    EV3GyroSensor,
    Motor,
    wait_ready_sensors
)
from utils import sound
import time
import sys

DELAY = 0.3

# Drum motor initialization
FIRST_MOTOR = Motor("A")
SECOND_MOTOR = Motor("B")
LEFT_MOTOR = Motor("C")
RIGHT_MOTOR = Motor("D")

# Sensors
GYRO = EV3GyroSensor(1, mode="both")

# Buttons
BUTTON = TouchSensor(3)
EMERGENCY_BUTTON = TouchSensor(4)

# Temp start trigger
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
TURN_TOLERANCE = 1.5

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

# Logging controls
ENABLE_TURN_LOG = True
TURN_LOG_EVERY_N_LOOPS = 5
TURN_LOG_FLUSH = True

wait_ready_sensors()


class EmergencyStop(Exception):
    pass


def log_turn(msg):
    if ENABLE_TURN_LOG:
        print(msg, flush=TURN_LOG_FLUSH)


def stop_drive():
    LEFT_MOTOR.set_power(0)
    RIGHT_MOTOR.set_power(0)


def stop_grab():
    FIRST_MOTOR.set_power(0)
    SECOND_MOTOR.set_power(0)


def stop_all():
    stop_drive()
    stop_grab()


def check_emergency():
    global emergency_stop
    if EMERGENCY_BUTTON.is_pressed():
        emergency_stop = True
        stop_all()
        raise EmergencyStop("Emergency stop pressed")


def safe_sleep(duration, interval=0.01):
    end_time = time.time() + duration
    while time.time() < end_time:
        check_emergency()
        remaining = end_time - time.time()
        time.sleep(min(interval, remaining))


def grab_in_forward(move_power, grab_power=IN_POWER, t=IN_TIME):
    check_emergency()

    FIRST_MOTOR.set_power(grab_power)
    SECOND_MOTOR.set_power(grab_power)
    LEFT_MOTOR.set_power(move_power)
    RIGHT_MOTOR.set_power(move_power)

    safe_sleep(t)

    stop_drive()
    stop_grab()


def grab_in(grab_power=IN_POWER, t=IN_TIME):
    check_emergency()

    FIRST_MOTOR.set_power(grab_power)
    SECOND_MOTOR.set_power(grab_power)

    safe_sleep(t)

    stop_grab()


def grab_out(power=OUT_POWER, t=OUT_TIME):
    check_emergency()

    FIRST_MOTOR.set_power(-power)
    SECOND_MOTOR.set_power(-power)

    safe_sleep(t)

    stop_grab()


def go_forward(duration, power):
    check_emergency()

    LEFT_MOTOR.set_power(power)
    RIGHT_MOTOR.set_power(power)

    safe_sleep(duration)

    stop_drive()


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def get_gyro_angle():
    reading = GYRO.get_both_measure()
    if reading is None:
        return None
    return reading[0]


def get_stable_gyro_angle(samples=GYRO_START_SAMPLES, delay=GYRO_SAMPLE_DELAY):
    values = []

    for _ in range(samples):
        check_emergency()
        angle = get_gyro_angle()
        if angle is not None:
            values.append(angle)
        time.sleep(delay)

    if not values:
        return None

    return sum(values) / len(values)


def get_turn_power_from_error(error):
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


def set_turn_power(direction, base_power, translation_correction):
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

    left_power = clamp(left_power, -100, 100)
    right_power = clamp(right_power, -100, 100)

    LEFT_MOTOR.set_power(left_power)
    RIGHT_MOTOR.set_power(right_power)

    return left_power, right_power


def turn(direction, angle=90):
    if direction not in ("left", "right"):
        raise ValueError("direction must be 'left' or 'right'")
    if angle <= 0:
        raise ValueError("angle must be positive")

    check_emergency()
    stop_drive()

    # Reset encoders so turn-centering correction starts from zero
    LEFT_MOTOR.reset_encoder()
    RIGHT_MOTOR.reset_encoder()

    # Let the gyro settle before sampling the start angle
    safe_sleep(GYRO_SETTLE_TIME)

    start_angle = get_stable_gyro_angle(samples=GYRO_START_SAMPLES)
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

    log_turn("")
    log_turn("=" * 80)
    log_turn(
        f"TURN START  direction={direction}  requested_angle={angle:.2f}  "
        f"start_angle={start_angle:.2f}  target_angle={target_angle:.2f}"
    )

    while True:
        check_emergency()
        loop_count += 1

        current_angle = get_stable_gyro_angle(
            samples=GYRO_LOOP_SAMPLES,
            delay=GYRO_SAMPLE_DELAY
        )
        if current_angle is None:
            if loop_count % TURN_LOG_EVERY_N_LOOPS == 0:
                log_turn(f"[loop {loop_count}] current_angle=None")
            continue

        angle_error = target_angle - current_angle

        if abs(angle_error) <= TURN_TOLERANCE:
            exit_reason = "tolerance"
            log_turn(
                f"TURN EXIT   reason={exit_reason}  loop={loop_count}  "
                f"current_angle={current_angle:.2f}  angle_error={angle_error:.2f}"
            )
            break

        base_power = get_turn_power_from_error(angle_error)
        base_power = max(base_power, TURN_MIN_POWER)

        left_enc = LEFT_MOTOR.get_encoder()
        right_enc = RIGHT_MOTOR.get_encoder()

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

        translation_correction = clamp(
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

            log_turn(
                f"STALL RECOVERY  loop={loop_count}  "
                f"curr={current_angle:.2f}  err={angle_error:.2f}  "
                f"base={base_power:.2f} -> boost={applied_base_power:.2f}  "
                f"Lenc={left_enc:.2f}  Renc={right_enc:.2f}"
            )

        left_cmd, right_cmd = set_turn_power(
            direction,
            applied_base_power,
            translation_correction
        )

        if loop_count % TURN_LOG_EVERY_N_LOOPS == 0:
            elapsed = time.time() - turn_start_time
            log_turn(
                f"[loop {loop_count:03d} | {elapsed:6.3f}s] "
                f"curr={current_angle:8.2f}  target={target_angle:8.2f}  "
                f"err={angle_error:7.2f}  base={base_power:5.2f}  "
                f"used={applied_base_power:5.2f}  "
                f"Lenc={left_enc:8.2f}  Renc={right_enc:8.2f}  "
                f"Terr={translation_error:8.2f}  Tcorr={translation_correction:6.2f}  "
                f"Lcmd={left_cmd:6.2f}  Rcmd={right_cmd:6.2f}"
            )

        # If still stalled after several boosts, give up cleanly
        if stalled and stall_boosts_used >= STALL_MAX_BOOSTS:
            exit_reason = "stall"
            log_turn(
                f"TURN EXIT   reason={exit_reason}  loop={loop_count}  "
                f"current_angle={current_angle:.2f}  angle_error={angle_error:.2f}"
            )
            break

        time.sleep(0.01)

    stop_drive()
    safe_sleep(0.05)

    final_angle = get_stable_gyro_angle(samples=GYRO_LOOP_SAMPLES, delay=GYRO_SAMPLE_DELAY)
    final_left_enc = LEFT_MOTOR.get_encoder()
    final_right_enc = RIGHT_MOTOR.get_encoder()
    final_translation_error = final_left_enc + final_right_enc

    log_turn(
        f"TURN END    reason={exit_reason}  loops={loop_count}  "
        f"final_angle={final_angle if final_angle is not None else 'None'}  "
        f"final_Lenc={final_left_enc:.2f}  final_Renc={final_right_enc:.2f}  "
        f"final_Terr={final_translation_error:.2f}"
    )
    log_turn("=" * 80)


def go_forward_target_slow(target_degrees, max_power=40, kp_heading=1.2, min_power=25, slowdown_distance=200):
    check_emergency()

    LEFT_MOTOR.reset_encoder()
    RIGHT_MOTOR.reset_encoder()

    # Lock initial heading
    safe_sleep(GYRO_SETTLE_TIME)
    target_angle = get_stable_gyro_angle()
    if target_angle is None:
        raise RuntimeError("Gyro unavailable")

    while True:
        check_emergency()

        left_enc = LEFT_MOTOR.get_encoder()
        right_enc = RIGHT_MOTOR.get_encoder()

        avg_enc = (left_enc + right_enc) / 2

        remaining = target_degrees - avg_enc

        if remaining <= 0:
            break

        # --- Slowdown logic ---
        if remaining < slowdown_distance:
            # Linear scaling of power
            power = max(min_power, max_power * (remaining / slowdown_distance))
        else:
            power = max_power

        # --- Gyro heading correction ---
        current_angle = get_gyro_angle()
        if current_angle is None:
            continue

        heading_error = target_angle - current_angle
        correction = kp_heading * heading_error

        left_power = clamp(power + correction, -100, 100)
        right_power = clamp(power - correction, -100, 100)

        LEFT_MOTOR.set_power(left_power)
        RIGHT_MOTOR.set_power(right_power)

        time.sleep(0.01)

    stop_drive()

# if __name__ == "__main__":
#     try:
#         while True:
#             check_emergency()

#             if BUTTON.is_pressed():
#                 start = not start
#                 safe_sleep(0.3)

#             if start:
#                 for i in range(10):
#                     log_turn(f"\n########## TURN PAIR {i + 1} ##########")
#                     turn("right")
#                     safe_sleep(3)

#                     turn("left")
#                     safe_sleep(3)

#                 start = False
#             else:
#                 stop_all()

#             safe_sleep(0.01)

#     except EmergencyStop:
#         stop_all()
#         print("EMERGENCY STOP ACTIVATED")
#         sys.exit(1)

if __name__ == "__main__":
    try:
        start = False

        while True:
            check_emergency()

            if BUTTON.is_pressed():
                start = True
                safe_sleep(0.3)

            if start:

                DISTANCE = 300        
                MAX_POWER = 40
                MIN_POWER = 10
                SLOWDOWN_DIST = 50
                KP_HEADING = 1.2

                go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                safe_sleep(1)
                turn("left")
                go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                safe_sleep(1)
                turn("right")
                go_forward_target_slow(DISTANCE, MAX_POWER, KP_HEADING, MIN_POWER, SLOWDOWN_DIST)
                safe_sleep(1)

                start = False  

            safe_sleep(0.01)

    except EmergencyStop:
        stop_all()
        print("EMERGENCY STOP ACTIVATED")
        sys.exit(1)