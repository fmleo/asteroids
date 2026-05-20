import enum
import math
import random

ROTATION_SPEED = 5

THRUSTER_ACCELERATION = 0.15
FRICTION = 0.99
MAX_SPEED = 6

BULLET_SPEED = 6
BULLET_RADIUS = 5

SCREEN_W, SCREEN_H = 1280, 720

PLAYER_W, PLAYER_H = 30, 40
PLAYER_RADIUS = 15

SHOT_DELAY = 300  # ticks

BULLET_LIFETIME = 120  # 120 frames ~ 2 segundos


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
        pass

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
