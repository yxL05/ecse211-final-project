from utils.brick import Motor
import time

LEFT_MOTOR = Motor("C")
RIGHT_MOTOR = Motor("D")

# Turning constants
TURNING_ENCODER_TARGET = 305
TURNING_ENCODER_TARGET_RIGHT = 310
CORRECTION_FACTOR = 0.6
MAX_CORRECTION = 8


def clamp(value, low, high):
    return max(low, min(high, value))


def stop_drive():
    LEFT_MOTOR.set_power(0)
    RIGHT_MOTOR.set_power(0)


def get_turn_power(progress, target):
    if progress < target * 0.7:
        return 35
    elif progress < target * 0.9:
        return 20
    elif progress < target:
        return 10
    else:
        return 0


def turn_90(direction, target=TURNING_ENCODER_TARGET):
    if direction not in ("left", "right"):
        raise ValueError("direction must be 'left' or 'right'")

    LEFT_MOTOR.reset_encoder()
    RIGHT_MOTOR.reset_encoder()

    while True:
        left = abs(LEFT_MOTOR.get_encoder())
        right = abs(RIGHT_MOTOR.get_encoder())

        # Average amount turned so far
        progress = (left + right) / 2

        if progress >= target:
            break

        base_power = get_turn_power(progress, target)

        # Keep both wheels rotating by similar amounts
        error = left - right
        correction = clamp(error * CORRECTION_FACTOR, -MAX_CORRECTION, MAX_CORRECTION)

        if direction == "right":
            # left forward, right backward
            left_power = base_power - correction
            right_power = -(base_power + correction)
        else:
            # left backward, right forward
            left_power = -(base_power - correction)
            right_power = base_power + correction

        LEFT_MOTOR.set_power(left_power)
        RIGHT_MOTOR.set_power(right_power)

        print(f"left: {left}")
        print(f"right: {right}")

        time.sleep(0.01)

    stop_drive()


def go_forward(duration=1.0, power=40):
    LEFT_MOTOR.set_power(power)
    RIGHT_MOTOR.set_power(power)
    time.sleep(duration)
    stop_drive()
