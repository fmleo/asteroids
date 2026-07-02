import pygame
from scene import Scene
from settings import MIDDLE_H, MIDDLE_W


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
        w, h = title.get_size()
        self.display.blit(title, (MIDDLE_W - w // 2, (MIDDLE_H - h // 2) - 40))

        text = self.font.render("Aperte enter para jogar", True, "white")
        w, h = text.get_size()
        self.display.blit(text, (MIDDLE_W - w // 2, (MIDDLE_H - h // 2) + 40))
