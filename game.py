import glob

import pygame

from asteroid import Asteroid, AsteroidSize
from bullet import Bullet
from scene import Scene
from settings import (
    BULLET_RADIUS,
    CORNERS,
    FRICTION,
    MAX_SPEED,
    MIDDLE_H,
    MIDDLE_W,
    PLAYER_H,
    PLAYER_RADIUS,
    PLAYER_W,
    ROTATION_SPEED,
    SCREEN_W,
    SHOT_DELAY,
    THRUSTER_ACCELERATION,
)
from utils import circles_collide, get_cos_sin, wrap


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

        pygame.mixer.stop()
        self.reset_state()
        pygame.mixer.music.play(-1)

    def reset_state(self):
        self.player_rotation = 180
        self.player_x = MIDDLE_W
        self.player_y = MIDDLE_H
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.bullets: list[Bullet] = []
        self.asteroids: list[Asteroid] = []
        self.last_shot_tick = 0
        self.level = 0
        self.score = 0
        self.lives = 3
        self.respawn_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()

        # -- Ações do jogador
        # -- -- girar para a direita
        if keys[pygame.K_LEFT]:
            self.player_rotation = (self.player_rotation + ROTATION_SPEED) % 360

        # -- -- girar para a esquerda
        if keys[pygame.K_RIGHT]:
            self.player_rotation = (self.player_rotation - ROTATION_SPEED) % 360

        # -- -- Aceleração (thrust)
        if keys[pygame.K_UP]:
            cos, sin = get_cos_sin(self.player_rotation)
            self.velocity_x += sin * THRUSTER_ACCELERATION
            self.velocity_y += cos * THRUSTER_ACCELERATION

            # limitar velocidade máxima
            speed = (self.velocity_x**2 + self.velocity_y**2) ** 0.5
            if speed > MAX_SPEED:
                self.velocity_x = self.velocity_x / speed * MAX_SPEED
                self.velocity_y = self.velocity_y / speed * MAX_SPEED

        # -- Movimentação, calculada quando o jogador não está acelerando
        # -- -- cálculo do atrito
        self.velocity_x *= FRICTION
        self.velocity_y *= FRICTION

        # -- -- movimentação do jogador
        self.player_x += self.velocity_x
        self.player_y += self.velocity_y
        self.player_x, self.player_y = wrap(self.player_x, self.player_y)

        # -- Diminuir timer de invencibilidade
        self.respawn_timer -= 1

        # -- Tiros
        # -- -- atirar
        if keys[pygame.K_SPACE]:
            # se o tick atual - o tick do ultimo tiro for maior que o delay definido, o jogador pode atirar
            if pygame.time.get_ticks() - self.last_shot_tick > SHOT_DELAY:
                self.last_shot_tick = pygame.time.get_ticks()
                self.bullets.append(
                    Bullet(x=self.player_x, y=self.player_y, angle=self.player_rotation)
                )

        # -- -- movimentação do tiro
        for bullet in self.bullets:
            bullet.tick()

        # -- Asteroides
        # -- -- spawn
        if len(self.asteroids) == 0:
            self.level += 1

            for i in range(self.level * 4):
                x, y = CORNERS[i % 4]
                asteroid = Asteroid(size=AsteroidSize.LARGE, x=x, y=y)
                self.asteroids.append(asteroid)

        # -- -- movimentação dos asteroides
        for asteroid in self.asteroids:
            asteroid.tick()

        # -- Remoção de objetos
        bullets_to_remove = set()
        # -- -- remoção de tiros
        for bullet in self.bullets:
            if bullet.lifetime <= 0:
                bullets_to_remove.add(bullet)

        # -- Colisões
        # -- -- tiro-asteroide
        asteroids_to_add = []
        asteroids_to_remove = []
        for b in self.bullets:
            if b in bullets_to_remove:
                continue
            for a in self.asteroids:
                if a in asteroids_to_remove:
                    continue
                if circles_collide(b.x, b.y, BULLET_RADIUS, a.x, a.y, a.radius):
                    self.explosion_sound.play()

                    bullets_to_remove.add(b)
                    asteroids_to_remove.append(a)

                    self.score += a.score

                    asteroids_to_add.extend(a.explode())

        # -- -- nave-asteroide
        # se for <= 0, player pode tomar dano
        if self.respawn_timer <= 0:
            for a in self.asteroids:
                if a in asteroids_to_remove:
                    continue
                if circles_collide(
                    self.player_x, self.player_y, PLAYER_RADIUS, a.x, a.y, a.radius
                ):
                    self.lives -= 1

                    self.player_x = MIDDLE_W
                    self.player_y = MIDDLE_H

                    self.respawn_timer = 120  # 2 segundos

                    if self.lives <= 0:
                        pygame.mixer.music.stop()
                        self.lose_sound.play()
                        self.active = False

        # -- Remoção de objetos
        for a in asteroids_to_remove:
            self.asteroids.remove(a)
        for b in bullets_to_remove:
            self.bullets.remove(b)

        # -- Adição dos novos asteroides adicionados
        self.asteroids.extend(asteroids_to_add)

    def draw(self):
        # -- Preencher tela com o plano de fundo
        self.display.blit(self.background_img, (0, 0))

        # -- desenhar cada bala
        for bullet in self.bullets:
            pygame.draw.circle(self.display, "red", (bullet.x, bullet.y), BULLET_RADIUS)

        # -- desenhar cada asteroide
        for asteroid in self.asteroids:
            img = self.asteroid_imgs[asteroid.img_index]
            # rotozoom usa antialiasing para escalonar e rotacionar imagens
            scaled = pygame.transform.rotozoom(
                img, -asteroid.rotation_angle, asteroid.radius * 2 / img.get_width()
            )
            rect = scaled.get_rect(center=(asteroid.x, asteroid.y))
            self.display.blit(scaled, rect)

        # -- cria uma superfície pois só superfícies podem ser rotacionadas
        # -- após isso renderiza o objeto do player
        player_surf = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
        # animação piscando para representar invincibilidade
        if not (self.respawn_timer > 0 and self.respawn_timer % 10 < 5):
            player_surf.blit(self.ship_img, (0, 0))
        rotated_surf = pygame.transform.rotate(player_surf, self.player_rotation)
        rotated_rect = rotated_surf.get_rect(center=(self.player_x, self.player_y))
        self.display.blit(rotated_surf, rotated_rect)

        # -- HUD
        lives_text = self.font.render(f"Vidas: {self.lives}", True, "white")
        self.display.blit(lives_text, (10, 10))

        score_text = self.font.render(f"{self.score:06}", True, "white")
        score_rect = score_text.get_rect(topright=(SCREEN_W - 10, 10))
        self.display.blit(score_text, score_rect)
