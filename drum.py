from utils.brick import Motor

# Drum motor initialization
FIRST_MOTOR = Motor("A")
SECOND_MOTOR = Motor("B")

# Drum state
POWER = 50

def start_drum(direction=1, power=POWER):
    FIRST_MOTOR.set_power(power * direction)
    SECOND_MOTOR.set_power(power * direction)


def stop_drum():
    FIRST_MOTOR.set_power(0)
    SECOND_MOTOR.set_power(0)


def update_drum(drum_on, direction=1, power=POWER):
    if drum_on:
        start_drum(direction, power)
    else:
        stop_drum()
