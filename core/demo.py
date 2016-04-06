from typing import List

import pygame
import sys

from core.common import Environment, MatchMaker, Game, Queuer, max_mmr_diff
from core.engine import Engine, OnGameFinishedListener, OnLobbyFoundListener

TEAM_SIZE = 5


class Demo(OnGameFinishedListener, OnLobbyFoundListener):

    def on_lobby_found(self, team_1: List[Queuer], team_2: List[Queuer]) -> None:
        self.num_playing += TEAM_SIZE * 2
        print("New game! max mmr-diff: " + str(max_mmr_diff([q.player for q in team_1], [q.player for q in team_2])))

    def on_game_finished(self, game: Game) -> None:
        self.num_playing -= TEAM_SIZE * 2

    def __init__(self, width=800, height=600, bar_height=10, wait_ms=100, bg_color=(50, 50, 50), text_color=(255, 255, 255)):
        pygame.init()
        self.width = width
        self.height = height
        self.bar_height = bar_height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.engine = None
        self.wait_ms = wait_ms
        self.bg_color = bg_color
        self.font = pygame.font.Font(None, 22)
        self.text_color = text_color
        self.num_playing = 0

    def run(self, match_maker: MatchMaker, environment: Environment):
        self.engine = Engine(match_maker, environment)
        self.engine._on_game_finished_listeners.append(self)
        self.engine._on_lobby_found_listeners.append(self)
        self.engine.add_players(87)
        self._main_loop()

    def _main_loop(self):
        self._render()
        pygame.time.wait(1000)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        if self.wait_ms == 0:
                            self.wait_ms = 2
                        else:
                            self.wait_ms = int(self.wait_ms * 1.5)
                    elif event.key == pygame.K_UP:
                        self.wait_ms = int(self.wait_ms / 1.5)
            self.engine.one_round()
            pygame.time.wait(self.wait_ms)
            self._render()

    def _render(self):
        pygame.draw.rect(self.screen, self.bg_color, (0, 0, self.width, self.height))
        for i, queuer in enumerate(self.engine.queue()):
            w = queuer.player.mmr / 8
            x = 10
            space = 1
            top_space = 50
            y = top_space + i * (self.bar_height + space)
            rect = (x, y, w, self.bar_height)
            if queuer.waited < 255:
                color = (queuer.waited, 0, 255-queuer.waited)
            else:
                color = (255, 0, 0)
            pygame.draw.rect(self.screen, color, rect)

        longest_wait = 0
        if len(self.engine.queue()) > 0:
            longest_wait = self.engine.queue()[0].waited

        self._render_text(str(len(self.engine.queue())) + " queueing", 10)
        self._render_text("longest: " + str(longest_wait) + "s", 150)
        self._render_text(str(len(self.engine._data_store.replays)) + " games played", 310)
        self._render_text(str(self.wait_ms) + "ms / round", 450)
        self._render_text(str(self.num_playing) + " playing", 610)

        pygame.display.flip()

    def _render_text(self, msg, x):
        text = self.font.render(msg, 1, self.text_color)
        textpos = text.get_rect()
        textpos.x = x
        textpos.y = 10
        self.screen.blit(text, textpos)