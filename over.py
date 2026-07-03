import pygame

import leaderboard
from scene import Scene
from settings import MIDDLE_W, SCREEN_H


class GameOverScene(Scene):
    def __init__(self, score: int = 0):
        super().__init__()
        self.score = score

    def events(self, event):
        super().events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.active = False

    def draw(self):
        text_over = self.font.render("GAME OVER", True, "white")
        w, _ = text_over.get_size()
        self.display.blit(text_over, (MIDDLE_W - w // 2, 60))

        text_score = self.font.render(f"Pontuação: {self.score:06}", True, "green")
        w, _ = text_score.get_size()
        self.display.blit(text_score, (MIDDLE_W - w // 2, 120))

        leaderboard.draw(self.display, MIDDLE_W, 200)

        instructions = self.font.render("[r] repetir  [q] sair", True, "white")
        w, h = instructions.get_size()
        self.display.blit(instructions, (MIDDLE_W - w // 2, SCREEN_H - 80))
