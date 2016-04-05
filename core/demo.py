import pygame
import sys

from core.common import Environment, MatchMaker
from core.engine import Engine


class Demo:

    def __init__(self, width=640, height=480):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.engine = None

    def run(self, match_maker: MatchMaker, environment: Environment):
        self.engine = Engine(match_maker, environment)
        self.engine.add_players(87)
        self._main_loop()

    def _main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            self.engine.one_round()
            pygame.time.wait(60)
            self._render()

    def _render(self):
        bg = (100, 100, 100)
        pygame.draw.rect(self.screen, bg, (0, 0, self.width, self.height))
        for i, queuer in enumerate(self.engine.queue()):
            w = queuer.player.mmr / 8
            h = 4
            x = 10
            space = 1
            y = i * (h + space)
            rect = (x, y, w, h)
            if queuer.waited < 255:
                color = (queuer.waited, 0, 255-queuer.waited)
            else:
                color = (255, 0, 0)
            pygame.draw.rect(self.screen, color, rect)
        pygame.display.flip()
        if len(self.engine.queue()) > 0:
            print(self.engine.queue()[0].waited)

