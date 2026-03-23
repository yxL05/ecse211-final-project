from ..utils.brick import (
    TouchSensor,
    EV3UltrasonicSensor,
    EV3ColorSensor,
    EV3GyroSensor,
    Motor,
    wait_ready_sensors
)
from ..utils import sound
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
TURN_FAST_POWER = 35
TURN_MEDIUM_POWER = 20
TURN_SLOW_POWER = 12
TURN_FINE_POWER = 8
TURN_TOLERANCE = 1.5
GYRO_SETTLE_TIME = 0.1
GYRO_START_SAMPLES = 7
GYRO_LOOP_SAMPLES = 3
GYRO_SAMPLE_DELAY = 0.005

wait_ready_sensors()


class EmergencyStop(Exception):
    pass


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


def turn_90(direction, angle=90):
    if direction not in ("left", "right"):
        raise ValueError("direction must be 'left' or 'right'")
    if angle <= 0:
        raise ValueError("angle must be positive")

    check_emergency()
    stop_drive()

    # Let the gyro settle before sampling the start angle
    safe_sleep(GYRO_SETTLE_TIME)

    start_angle = get_stable_gyro_angle(samples=GYRO_START_SAMPLES)
    if start_angle is None:
        raise RuntimeError("Gyro reading unavailable")

    if direction == "right":
        target_angle = start_angle + angle
    else:
        target_angle = start_angle - angle

    while True:
        check_emergency()

        current_angle = get_stable_gyro_angle(
            samples=GYRO_LOOP_SAMPLES,
            delay=GYRO_SAMPLE_DELAY
        )
        if current_angle is None:
            continue

        error = target_angle - current_angle

        if abs(error) <= TURN_TOLERANCE:
            break

        power = get_turn_power_from_error(error)

        if direction == "right":
            LEFT_MOTOR.set_power(power)
            RIGHT_MOTOR.set_power(-power)
        else:
            LEFT_MOTOR.set_power(-power)
            RIGHT_MOTOR.set_power(power)

        time.sleep(0.01)

    stop_drive()
    safe_sleep(0.05)


if __name__ == "__main__":
    try:
        while True:
            check_emergency()

            if BUTTON.is_pressed():
                start = not start
                safe_sleep(0.3)

            if start:
                grab_in_forward(move_power=10)
                safe_sleep(3)

                turn_90("right")
                safe_sleep(3)

                turn_90("left")
                safe_sleep(3)

                grab_out()
                safe_sleep(3)

                grab_out(OUT_POWER_2, OUT_TIME_2)
                start = False
            else:
                stop_all()

            safe_sleep(0.01)

    except EmergencyStop:
        stop_all()
        print("EMERGENCY STOP ACTIVATED")
        sys.exit(1)