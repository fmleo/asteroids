import enum
import random

import pygame

from settings import POWERUP_LIFETIME, POWERUP_RADIUS, POWERUP_SPEED
from utils import get_cos_sin, wrap


class PowerUpType(enum.Enum):
    SHIELD = 0
    RAPID_FIRE = 1
    MULTI_SHOT = 2
    EXTRA_LIFE = 3


POWERUP_CONFIG = {
    PowerUpType.SHIELD: {"color": (0, 180, 255), "letter": "S"},
    PowerUpType.RAPID_FIRE: {"color": (255, 200, 0), "letter": "R"},
    PowerUpType.MULTI_SHOT: {"color": (255, 80, 80), "letter": "M"},
    PowerUpType.EXTRA_LIFE: {"color": (80, 255, 80), "letter": "L"},
}


class PowerUp:
    def __init__(self, x: float, y: float) -> None:
        self.type = random.choice(list(PowerUpType))
        self.x = x
        self.y = y
        self.angle = random.randint(0, 360)
        self.lifetime = POWERUP_LIFETIME

    def tick(self):
        cos, sin = get_cos_sin(self.angle)
        self.x += sin * POWERUP_SPEED
        self.y += cos * POWERUP_SPEED

        self.x, self.y = wrap(self.x, self.y)

        self.lifetime -= 1

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        config = POWERUP_CONFIG[self.type]
        pygame.draw.circle(surface, config["color"], (self.x, self.y), POWERUP_RADIUS)
        pygame.draw.circle(surface, "white", (self.x, self.y), POWERUP_RADIUS, 2)
        letter_surf = font.render(config["letter"], True, "white")
        letter_rect = letter_surf.get_rect(center=(self.x, self.y))
        surface.blit(letter_surf, letter_rect)
