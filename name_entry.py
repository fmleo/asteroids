import pygame

from leaderboard import save_score
from scene import Scene
from settings import MIDDLE_H, MIDDLE_W


class NameEntryScene(Scene):
    def __init__(self, score: int = 0):
        super().__init__()
        self.score = score
        self.name = ""

    def events(self, event):
        super().events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.name) == 3:
                save_score(self.name, self.score)
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.unicode.isalpha() and len(self.name) < 3:
                self.name += event.unicode.upper()

    def draw(self):
        prompt = self.font.render("DIGITE SUAS INICIAIS", True, "white")
        pw, ph = prompt.get_size()
        self.display.blit(prompt, (MIDDLE_W - pw // 2, MIDDLE_H - ph // 2 - 60))

        name = self.font.render(self.name.ljust(3, "_"), True, "yellow")
        nw, nh = name.get_size()
        self.display.blit(name, (MIDDLE_W - nw // 2, MIDDLE_H - nh // 2))

        hint = self.font.render("Enter para confirmar", True, "gray")
        hw, hh = hint.get_size()
        self.display.blit(hint, (MIDDLE_W - hw // 2, MIDDLE_H - hh // 2 + 60))
