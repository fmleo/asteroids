import glob
from typing import Literal

import pygame
from utils import (
    BULLET_RADIUS,
    FRICTION,
    MAX_SPEED,
    PLAYER_H,
    PLAYER_RADIUS,
    PLAYER_W,
    ROTATION_SPEED,
    SCREEN_H,
    SCREEN_W,
    SHOT_DELAY,
    THRUSTER_ACCELERATION,
    Asteroid,
    AsteroidSize,
    Bullet,
    circles_collide,
    get_cos_sin,
    wrap,
)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()
flag = True
font = pygame.font.Font(None, 50)

ship_img = pygame.image.load("./assets/spaceship_scaled.png")
asteroid_imgs = [
    pygame.image.load(path) for path in glob.glob("./assets/asteroids/*.png")
]
background_img = pygame.image.load("./assets/background.png")

pygame.mixer.music.load("./assets/music/background.mp3")
pygame.mixer.music.set_volume(0.2)

lose_sound = pygame.mixer.Sound("./assets/music/lose.mp3")
lose_sound.set_volume(0.3)

explosion_sound = pygame.mixer.Sound("./assets/music/explosion.mp3")
explosion_sound.set_volume(0.1)

player_rotation = 180

MIDDLE_W = SCREEN_W // 2
MIDDLE_H = SCREEN_H // 2

player_x = MIDDLE_W
player_y = MIDDLE_H

velocity_x = 0.0
velocity_y = 0.0

bullets: list[Bullet] = []
asteroids: list[Asteroid] = []

last_shot_tick = 0

level = 0
score = 0
lives = 3

respawn_timer = 0

CORNERS = ((0, 0), (SCREEN_W, 0), (SCREEN_W, SCREEN_H), (0, SCREEN_H))

scene: Literal["MENU", "JOGO", "OVER"] = "MENU"

while flag:
    match scene:
        case "MENU":
            screen.fill("black")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    flag = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        player_rotation = 180

                        player_x = MIDDLE_W
                        player_y = MIDDLE_H

                        velocity_x = 0.0
                        velocity_y = 0.0

                        bullets: list[Bullet] = []
                        asteroids: list[Asteroid] = []

                        last_shot_tick = 0

                        level = 0
                        score = 0
                        lives = 3

                        pygame.mixer.music.play(-1)

                        scene = "JOGO"
                    if event.key == pygame.K_q:
                        flag = False

            title = font.render("ASTEROIDES", True, "white")
            w, h = title.get_size()
            screen.blit(title, (MIDDLE_W - w // 2, (MIDDLE_H - h // 2) - 40))

            text = font.render("Aperte enter para jogar", True, "white")
            w, h = text.get_size()
            screen.blit(text, (MIDDLE_W - w // 2, (MIDDLE_H - h // 2) + 40))

        case "OVER":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        flag = False
                    if event.key == pygame.K_r:
                        scene = "MENU"

            screen.fill("black")

            text_over = font.render("GAME OVER", True, "white")

            w, h = text_over.get_size()
            screen.blit(text_over, (MIDDLE_W - w // 2, (MIDDLE_H - h // 2) - 80))

            text_score = font.render(f"Pontuação: {score:06}", True, "green")

            w, h = text_score.get_size()
            screen.blit(text_score, (MIDDLE_W - w // 2, (MIDDLE_H - h // 2) - 40))

            instructions = font.render("[q] sair ou [r] repetir", True, "white")
            w, h = instructions.get_size()
            screen.blit(instructions, (MIDDLE_W - w // 2, (MIDDLE_H - h // 2) + 40))

        case "JOGO":
            # EVENTOS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    flag = False

            # INPUT
            keys = pygame.key.get_pressed()

            # LÓGICA DO JOGO
            # -- Ações do jogador
            # -- -- girar para a direita
            if keys[pygame.K_LEFT]:
                player_rotation = (player_rotation + ROTATION_SPEED) % 360

            # -- -- girar para a esquerda
            if keys[pygame.K_RIGHT]:
                player_rotation = (player_rotation - ROTATION_SPEED) % 360

            # -- -- Aceleração (thrust)
            if keys[pygame.K_UP]:
                cos, sin = get_cos_sin(player_rotation)
                velocity_x += sin * THRUSTER_ACCELERATION
                velocity_y += cos * THRUSTER_ACCELERATION

                # limitar velocidade máxima
                speed = (velocity_x**2 + velocity_y**2) ** 0.5
                if speed > MAX_SPEED:
                    velocity_x = velocity_x / speed * MAX_SPEED
                    velocity_y = velocity_y / speed * MAX_SPEED

            # -- Movimentação, calculada quando o jogador não está acelerando
            # -- -- cálculo do atrito
            velocity_x *= FRICTION
            velocity_y *= FRICTION

            # -- -- movimentação do jogador
            player_x += velocity_x
            player_y += velocity_y
            player_x, player_y = wrap(player_x, player_y)

            # -- Diminuir timer de invencibilidade
            respawn_timer -= 1

            # -- Tiros
            # -- -- atirar
            if keys[pygame.K_SPACE]:
                # se o tick atual - o tick do ultimo tiro for maior que o delay definido, o jogador pode atirar
                if pygame.time.get_ticks() - last_shot_tick > SHOT_DELAY:
                    last_shot_tick = pygame.time.get_ticks()
                    bullets.append(
                        Bullet(x=player_x, y=player_y, angle=player_rotation)
                    )

            # -- -- movimentação do tiro
            for bullet in bullets:
                bullet.tick()

            # -- Asteroides
            # -- -- spawn
            if len(asteroids) == 0:
                level += 1

                for i in range(level * 4):
                    x, y = CORNERS[i % 4]
                    asteroid = Asteroid(size=AsteroidSize.LARGE, x=x, y=y)
                    asteroids.append(asteroid)

            # -- -- movimentação dos asteroides
            for asteroid in asteroids:
                asteroid.tick()

            # -- Remoção de objetos
            bullets_to_remove = set()
            # -- -- remoção de tiros
            for bullet in bullets:
                if bullet.lifetime <= 0:
                    bullets_to_remove.add(bullet)

            # -- Colisões
            # -- -- tiro-asteroide
            asteroids_to_add = []
            asteroids_to_remove = []
            for b in bullets:
                if b in bullets_to_remove:
                    continue
                for a in asteroids:
                    if a in asteroids_to_remove:
                        continue
                    if circles_collide(b.x, b.y, BULLET_RADIUS, a.x, a.y, a.radius):
                        # explosion_sound.play()

                        bullets_to_remove.add(b)
                        asteroids_to_remove.append(a)

                        score += a.score

                        asteroids_to_add.extend(a.explode())

            # -- -- nave-asteroide
            # se for <= 0, player pode tomar dano
            if respawn_timer <= 0:
                for a in asteroids:
                    if a in asteroids_to_remove:
                        continue
                    if circles_collide(
                        player_x, player_y, PLAYER_RADIUS, a.x, a.y, a.radius
                    ):
                        lives -= 1

                        player_x = MIDDLE_W
                        player_y = MIDDLE_H

                        respawn_timer = 120  # 2 segundos

                        if lives <= 0:
                            pygame.mixer.music.stop()
                            lose_sound.play()
                            scene = "OVER"

            # -- Remoção de objetos
            for a in asteroids_to_remove:
                asteroids.remove(a)
            for b in bullets_to_remove:
                bullets.remove(b)

            # -- Adição dos novos asteroides adicionados
            asteroids.extend(asteroids_to_add)

            # RENDERIZAÇÃO

            # -- Preencher tela com o plano de fundo
            screen.blit(background_img, (0, 0))

            # -- desenhar cada bala
            for bullet in bullets:
                pygame.draw.circle(screen, "red", (bullet.x, bullet.y), BULLET_RADIUS)

            # -- desenhar cada asteroide
            for asteroid in asteroids:
                img = asteroid_imgs[asteroid.img_index]
                # rotozoom usa antialiasing para escalonar e rotacionar imagens
                scaled = pygame.transform.rotozoom(
                    img, -asteroid.rotation_angle, asteroid.radius * 2 / img.get_width()
                )
                rect = scaled.get_rect(center=(asteroid.x, asteroid.y))
                screen.blit(scaled, rect)

            # -- cria uma superfície pois só superfícies podem ser rotacionadas
            # -- após isso renderiza o objeto do player
            player_surf = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
            # animação piscando para representar invincibilidade
            if not (respawn_timer > 0 and respawn_timer % 10 < 5):
                player_surf.blit(ship_img, (0, 0))
            rotated_surf = pygame.transform.rotate(player_surf, player_rotation)
            rotated_rect = rotated_surf.get_rect(center=(player_x, player_y))
            screen.blit(rotated_surf, rotated_rect)

            # -- HUD
            lives_text = font.render(f"Vidas: {lives}", True, "white")
            screen.blit(lives_text, (10, 10))

            score_text = font.render(f"{score:06}", True, "white")
            score_rect = score_text.get_rect(topright=(SCREEN_W - 10, 10))
            screen.blit(score_text, score_rect)

    # -- flipar o display para colocar tudo que foi renderizado na tela
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
