import sys

import pygame

from game import GameScene
from menu import MenuScene
from name_entry import NameEntryScene
from over import GameOverScene
from scene import Scene
from settings import SCREEN_H, SCREEN_W


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()

        pygame.display.set_caption("Asteroides")

        self.display = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.scene = "menu"
        self.current_scene: Scene = MenuScene()

    def run(self):
        while True:
            self.handle_transitions()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.current_scene.events(event)

            self.current_scene.update()
            self.display.fill("black")
            self.current_scene.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_transitions(self):
        if self.scene == "menu" and not self.current_scene.active:
            self.scene = "game"
            self.current_scene = GameScene()
        elif self.scene == "game" and not self.current_scene.active:
            score = self.current_scene.score
            self.scene = "name_entry"
            self.current_scene = NameEntryScene(score)
        elif self.scene == "name_entry" and not self.current_scene.active:
            score = self.current_scene.score
            self.scene = "over"
            self.current_scene = GameOverScene(score)
        elif self.scene == "over" and not self.current_scene.active:
            self.scene = "menu"
            self.current_scene = MenuScene()


if __name__ == "__main__":
    game = Game()
    game.run()
