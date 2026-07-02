import enum
import random

from utils import get_cos_sin, wrap


class AsteroidSize(enum.Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3


ASTEROID_SIZE_CONFIG = {
    AsteroidSize.SMALL: {"radius": 20, "speed": 4.5, "score": 100},
    AsteroidSize.MEDIUM: {"radius": 40, "speed": 3.0, "score": 50},
    AsteroidSize.LARGE: {"radius": 80, "speed": 1.5, "score": 20},
}


class Asteroid:
    size: AsteroidSize
    x: float
    y: float
    angle: int

    rotation_angle: float

    radius: int
    speed: float
    score: int

    def __init__(self, size: AsteroidSize, x: float, y: float) -> None:
        self.size = size
        self.x = x
        self.y = y
        self.angle = random.randint(0, 360)

        self.rotation_angle = random.randint(0, 360)

        self.img_index = random.randrange(0, 9)

        for key, value in ASTEROID_SIZE_CONFIG[size].items():
            setattr(self, key, value)

    def tick(self):
        cos, sin = get_cos_sin(self.angle)
        self.x += sin * self.speed
        self.y += cos * self.speed

        self.x, self.y = wrap(self.x, self.y)

        self.rotation_angle = (self.rotation_angle + self.speed) % 360

    def explode(self) -> list["Asteroid"]:
        if self.size == AsteroidSize.LARGE:
            return [
                Asteroid(size=AsteroidSize.MEDIUM, x=self.x, y=self.y) for _ in range(2)
            ]
        elif self.size == AsteroidSize.MEDIUM:
            return [
                Asteroid(size=AsteroidSize.SMALL, x=self.x, y=self.y) for _ in range(2)
            ]
        else:
            return []
