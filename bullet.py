from settings import BULLET_LIFETIME, BULLET_SPEED
from utils import get_cos_sin, wrap


class Bullet:
    x: float
    y: float
    angle: int
    lifetime: int

    def __init__(self, x: float, y: float, angle: int) -> None:
        self.x = x
        self.y = y
        self.angle = angle
        self.lifetime = BULLET_LIFETIME

    def tick(self):
        cos, sin = get_cos_sin(self.angle)
        self.x += sin * BULLET_SPEED
        self.y += cos * BULLET_SPEED

        self.x, self.y = wrap(self.x, self.y)

        self.lifetime -= 1

    def __repr__(self):
        return f"({self.x}, {self.y}) {self.angle:>3}"
