import pygame

from settings import (
    FRICTION,
    MAX_SPEED,
    MIDDLE_H,
    MIDDLE_W,
    PLAYER_H,
    PLAYER_RADIUS,
    PLAYER_W,
    ROTATION_SPEED,
    THRUSTER_ACCELERATION,
)
from utils import get_cos_sin, wrap


class Player:
    def __init__(self, ship_img: pygame.Surface) -> None:
        self.ship_img = ship_img
        self.reset()

    def reset(self):
        self.x = MIDDLE_W
        self.y = MIDDLE_H
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.rotation = 180
        self.respawn_timer = 0

    @property
    def radius(self) -> int:
        return PLAYER_RADIUS

    @property
    def is_invincible(self) -> bool:
        return self.respawn_timer > 0

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.rotation = (self.rotation + ROTATION_SPEED) % 360

        if keys[pygame.K_RIGHT]:
            self.rotation = (self.rotation - ROTATION_SPEED) % 360

        if keys[pygame.K_UP]:
            cos, sin = get_cos_sin(self.rotation)
            self.velocity_x += sin * THRUSTER_ACCELERATION
            self.velocity_y += cos * THRUSTER_ACCELERATION

            speed = (self.velocity_x**2 + self.velocity_y**2) ** 0.5
            if speed > MAX_SPEED:
                self.velocity_x = self.velocity_x / speed * MAX_SPEED
                self.velocity_y = self.velocity_y / speed * MAX_SPEED

    def tick(self):
        self.velocity_x *= FRICTION
        self.velocity_y *= FRICTION

        self.x += self.velocity_x
        self.y += self.velocity_y
        self.x, self.y = wrap(self.x, self.y)

        self.respawn_timer -= 1

    def draw(self, surface: pygame.Surface):
        player_surf = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
        if not (self.respawn_timer > 0 and self.respawn_timer % 10 < 5):
            player_surf.blit(self.ship_img, (0, 0))
        rotated_surf = pygame.transform.rotate(player_surf, self.rotation)
        rotated_rect = rotated_surf.get_rect(center=(self.x, self.y))
        surface.blit(rotated_surf, rotated_rect)
