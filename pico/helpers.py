from machine import PWM
from time import sleep_ms


def ease_in_out_cubic(x: float) -> float:
    if x < 0.5:
        return 4 * x * x * x
    return 1 - pow(-2 * x + 2, 3) / 2


def pulse_pwm(pwm: PWM, count=1, duration=500, steps=50) -> None:
    step_size = 1 / steps
    step_duration = int(duration / (steps * 2))

    for pulse in range(count):
        for step in range(steps):
            x = ease_in_out_cubic(step * step_size)
            pwm.duty_u16(int(x * (2 ** 16 - 1)))
            sleep_ms(step_duration)

        for step in range(steps, 0, -1):
            x = ease_in_out_cubic(step * step_size)
            pwm.duty_u16(int(x * (2 ** 16 - 1)))
            sleep_ms(step_duration)


def get_config(file: str) -> dict[str, str]:
    config = dict()

    with open(file, mode="r") as f:
        for line in f:
            line: str = line

            if line.strip().startswith("#"):
                continue

            try:
                key, value = line.split("=")
                config[key] = value.strip()
            except ValueError:
                continue

    return config
