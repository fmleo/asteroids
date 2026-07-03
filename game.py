import glob
import random

import pygame

from asteroid import Asteroid, AsteroidSize
from bullet import Bullet
from player import Player
from powerup import PowerUp, PowerUpType
from scene import Scene
from settings import (
    BULLET_RADIUS,
    CORNERS,
    MIDDLE_H,
    MIDDLE_W,
    MULTI_SHOT_DURATION,
    PLAYER_RADIUS,
    POWERUP_DROP_CHANCE,
    POWERUP_RADIUS,
    RAPID_FIRE_DURATION,
    RAPID_FIRE_SHOT_DELAY,
    SCREEN_W,
    SHIELD_DURATION,
    SHOT_DELAY,
)
from utils import circles_collide


class GameScene(Scene):
    def __init__(self):
        super().__init__()

        self.ship_img = pygame.image.load("./assets/spaceship_scaled.png")
        self.asteroid_imgs = [
            pygame.image.load(path) for path in glob.glob("./assets/asteroids/*.png")
        ]
        self.background_img = pygame.image.load("./assets/background.png")

        pygame.mixer.music.load("./assets/music/background.mp3")
        pygame.mixer.music.set_volume(0.2)

        self.lose_sound = pygame.mixer.Sound("./assets/music/lose.mp3")
        self.lose_sound.set_volume(0.3)

        self.explosion_sound = pygame.mixer.Sound("./assets/music/explosion.mp3")
        self.explosion_sound.set_volume(0.1)

        self.powerup_font = pygame.font.Font("assets/BlockBlueprint.ttf", 16)

        pygame.mixer.stop()
        self.reset_state()
        pygame.mixer.music.play(-1)

    def reset_state(self):
        self.player = Player(self.ship_img)
        self.bullets: list[Bullet] = []
        self.asteroids: list[Asteroid] = []
        self.powerups: list[PowerUp] = []
        self.last_shot_tick = 0
        self.level = 0
        self.lives = 3

    # -- -- Update

    def update(self):
        keys = pygame.key.get_pressed()

        self.player.handle_input(keys)
        self.player.tick()

        self._handle_shooting(keys)
        self._update_bullets()
        self._spawn_asteroids()
        self._update_asteroids()
        self._update_powerups()
        self._check_collisions()
        self._check_player_powerup_collisions()
        self._cleanup_objects()

    def _handle_shooting(self, keys):
        if keys[pygame.K_SPACE]:
            delay = RAPID_FIRE_SHOT_DELAY if self.player.rapid_fire_timer > 0 else SHOT_DELAY
            if pygame.time.get_ticks() - self.last_shot_tick > delay:
                self.last_shot_tick = pygame.time.get_ticks()
                if self.player.multi_shot_timer > 0:
                    for offset in (0, 15, -15):
                        self.bullets.append(
                            Bullet(
                                x=self.player.x,
                                y=self.player.y,
                                angle=self.player.rotation + offset,
                            )
                        )
                else:
                    self.bullets.append(
                        Bullet(
                            x=self.player.x,
                            y=self.player.y,
                            angle=self.player.rotation,
                        )
                    )

    def _update_bullets(self):
        for bullet in self.bullets:
            bullet.tick()

    def _spawn_asteroids(self):
        if len(self.asteroids) == 0:
            self.level += 1
            for i in range(self.level * 4):
                x, y = CORNERS[i % 4]
                self.asteroids.append(Asteroid(size=AsteroidSize.LARGE, x=x, y=y))

    def _update_asteroids(self):
        for asteroid in self.asteroids:
            asteroid.tick()

    def _check_collisions(self):
        self._bullets_to_remove: set[Bullet] = set()
        self._asteroids_to_remove: list[Asteroid] = []
        self._asteroids_to_add: list[Asteroid] = []

        for bullet in self.bullets:
            if bullet.lifetime <= 0:
                self._bullets_to_remove.add(bullet)

        self._check_bullet_asteroid_collisions()
        self._check_player_asteroid_collisions()

    def _check_bullet_asteroid_collisions(self):
        for b in self.bullets:
            if b in self._bullets_to_remove:
                continue
            for a in self.asteroids:
                if a in self._asteroids_to_remove:
                    continue
                if circles_collide(b.x, b.y, BULLET_RADIUS, a.x, a.y, a.radius):
                    self.explosion_sound.play()
                    self._bullets_to_remove.add(b)
                    self._asteroids_to_remove.append(a)
                    self.score += a.score
                    self._asteroids_to_add.extend(a.explode())
                    if random.random() < POWERUP_DROP_CHANCE:
                        self.powerups.append(PowerUp(x=a.x, y=a.y))

    def _check_player_asteroid_collisions(self):
        if self.player.is_invincible:
            return

        for a in self.asteroids:
            if a in self._asteroids_to_remove:
                continue
            if circles_collide(
                self.player.x, self.player.y, PLAYER_RADIUS, a.x, a.y, a.radius
            ):
                self.lives -= 1
                self.player.x = MIDDLE_W
                self.player.y = MIDDLE_H
                self.player.respawn_timer = 120

                if self.lives <= 0:
                    pygame.mixer.music.stop()
                    self.lose_sound.play()
                    self.active = False
                break

    def _cleanup_objects(self):
        for a in self._asteroids_to_remove:
            self.asteroids.remove(a)
        for b in self._bullets_to_remove:
            self.bullets.remove(b)
        self.asteroids.extend(self._asteroids_to_add)

    def _update_powerups(self):
        self._powerups_to_remove: list[PowerUp] = []
        for p in self.powerups:
            p.tick()
            if p.lifetime <= 0:
                self._powerups_to_remove.append(p)
        for p in self._powerups_to_remove:
            self.powerups.remove(p)

    def _check_player_powerup_collisions(self):
        collected: list[PowerUp] = []
        for p in self.powerups:
            if circles_collide(
                self.player.x, self.player.y, PLAYER_RADIUS,
                p.x, p.y, POWERUP_RADIUS,
            ):
                self.explosion_sound.play()
                if p.type == PowerUpType.SHIELD:
                    self.player.shield_timer = SHIELD_DURATION
                elif p.type == PowerUpType.RAPID_FIRE:
                    self.player.rapid_fire_timer = RAPID_FIRE_DURATION
                elif p.type == PowerUpType.MULTI_SHOT:
                    self.player.multi_shot_timer = MULTI_SHOT_DURATION
                elif p.type == PowerUpType.EXTRA_LIFE:
                    self.lives += 1
                collected.append(p)
        for p in collected:
            self.powerups.remove(p)

    # -- -- Draw

    def draw(self):
        self._draw_background()
        self._draw_bullets()
        self._draw_asteroids()
        self._draw_powerups()
        self.player.draw(self.display)
        self._draw_hud()

    def _draw_background(self):
        self.display.blit(self.background_img, (0, 0))

    def _draw_bullets(self):
        for bullet in self.bullets:
            pygame.draw.circle(self.display, "red", (bullet.x, bullet.y), BULLET_RADIUS)

    def _draw_asteroids(self):
        for asteroid in self.asteroids:
            img = self.asteroid_imgs[asteroid.img_index]
            scaled = pygame.transform.rotozoom(
                img, -asteroid.rotation_angle, asteroid.radius * 2 / img.get_width()
            )
            rect = scaled.get_rect(center=(asteroid.x, asteroid.y))
            self.display.blit(scaled, rect)

    def _draw_powerups(self):
        for p in self.powerups:
            p.draw(self.display, self.powerup_font)

    def _draw_hud(self):
        lives_text = self.font.render(f"Vidas: {self.lives}", True, "white")
        self.display.blit(lives_text, (10, 10))
        level_text = self.font.render(f"Nível: {self.level}", True, "white")
        self.display.blit(level_text, (10, 50))

        score_text = self.font.render(f"{self.score:06}", True, "white")
        score_rect = score_text.get_rect(topright=(SCREEN_W - 10, 10))
        self.display.blit(score_text, score_rect)

        self._draw_powerup_hud()

    def _draw_powerup_hud(self):
        timers = [
            (PowerUpType.SHIELD, self.player.shield_timer),
            (PowerUpType.RAPID_FIRE, self.player.rapid_fire_timer),
            (PowerUpType.MULTI_SHOT, self.player.multi_shot_timer),
        ]
        y = 90
        for ptype, timer in timers:
            if timer > 0:
                secs = timer // 60 + 1
                text = self.font.render(f"{ptype.name}: {secs}s", True, "white")
                self.display.blit(text, (10, y))
                y += 36
