import math

from settings import SCREEN_H, SCREEN_W


def get_cos_sin(rotation: int) -> tuple[float, float]:
    return (
        math.cos(math.radians(rotation)),
        math.sin(math.radians(rotation)),
    )


def wrap(x: float, y: float) -> tuple[float, float]:
    return (x % SCREEN_W, y % SCREEN_H)


def circles_collide(x1, y1, r1, x2, y2, r2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    distance = (dx**2 + dy**2) ** 0.5
    return distance <= r1 + r2
