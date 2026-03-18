from utils.brick import (
    TouchSensor,
    EV3UltrasonicSensor,
    EV3ColorSensor,
    Motor,
    wait_ready_sensors
)
from utils import sound
import time

DELAY = 0.3

# Drum motor initialization
FIRST_MOTOR = Motor("A")
SECOND_MOTOR = Motor("B")
LEFT_MOTOR = Motor("C")
RIGHT_MOTOR = Motor("D")

# Drum state
drum_on = False
direction = 1
POWER = 50

# Sensor initialization
BUTTON1 = TouchSensor(3)
BUTTON2 = TouchSensor(4)

# Turning constants
TURNING_ENCODER_TARGET = 305
TURNING_ENCODER_TARGET_RIGHT = 310
TURN_POWER = 35
FORWARD_POWER = 40

wait_ready_sensors()


def stop_drive():
    LEFT_MOTOR.set_power(0)
    RIGHT_MOTOR.set_power(0)


def turn_90(direction, target=TURNING_ENCODER_TARGET):
    if direction not in ("left", "right"):
        raise ValueError("direction must be 'left' or 'right'")

    LEFT_MOTOR.reset_encoder()
    RIGHT_MOTOR.reset_encoder()

    while True:
        left = abs(LEFT_MOTOR.get_encoder())
        right = abs(RIGHT_MOTOR.get_encoder())
        progress = (left + right) / 2

        if progress >= target:
            break

        if direction == "right":
            LEFT_MOTOR.set_power(TURN_POWER)
            RIGHT_MOTOR.set_power(-TURN_POWER)
        else:
            LEFT_MOTOR.set_power(-TURN_POWER)
            RIGHT_MOTOR.set_power(TURN_POWER)

        print(f"left: {left}")
        print(f"right: {right}")

        time.sleep(0.01)

    stop_drive()


def go_forward(duration=1.0, power=FORWARD_POWER):
    LEFT_MOTOR.set_power(power)
    RIGHT_MOTOR.set_power(power)
    time.sleep(duration)
    stop_drive()

# Experimenting
if __name__ == "__main__":
    while True:
        # Toggle spinning
        if BUTTON1.is_pressed():
            drum_on = not drum_on
            time.sleep(0.3)

        # Change direction
        if BUTTON2.is_pressed():
            direction *= -1
            time.sleep(0.3)

        # Control motors A and B
        if drum_on:
            FIRST_MOTOR.set_power(POWER * direction)
            SECOND_MOTOR.set_power(POWER * direction)
        else:
            FIRST_MOTOR.set_power(0)
            SECOND_MOTOR.set_power(0)

        turn_90("left")
        turn_90("right", TURNING_ENCODER_TARGET_RIGHT)

        time.sleep(0.01)
