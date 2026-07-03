import pygame

from scene import Scene
from settings import MIDDLE_H, MIDDLE_W


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
        w, h = text_over.get_size()
        self.display.blit(text_over, (MIDDLE_W - w // 2, (MIDDLE_H - h // 2) - 80))

        text_score = self.font.render(f"Pontuação: {self.score:06}", True, "green")
        w, h = text_score.get_size()
        self.display.blit(text_score, (MIDDLE_W - w // 2, (MIDDLE_H - h // 2) - 40))

        instructions = self.font.render("[q] sair ou [r] repetir", True, "white")
        w, h = instructions.get_size()
        self.display.blit(instructions, (MIDDLE_W - w // 2, (MIDDLE_H - h // 2) + 40))
