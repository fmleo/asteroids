import pygame

import leaderboard
from scene import Scene
from settings import MIDDLE_W


class MenuScene(Scene):
    def __init__(self):
        super().__init__()

    def events(self, event):
        super().events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.active = False

    def draw(self):
        title = self.font.render("ASTEROIDES", True, "white")
        w, _ = title.get_size()
        self.display.blit(title, (MIDDLE_W - w // 2, 60))

        text = self.font.render("Aperte enter para jogar", True, "white")
        w, _ = text.get_size()
        self.display.blit(text, (MIDDLE_W - w // 2, 120))

        leaderboard.draw(self.display, MIDDLE_W, 200)
