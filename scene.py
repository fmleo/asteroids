import pygame


class Scene:
    def __init__(self):
        self.display = pygame.display.get_surface()
        self.active = True
        self.font = pygame.font.Font(None, 50)
        self.score = 0

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.active = False

    def draw(self):
        pass

    def update(self):
        pass
