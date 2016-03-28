from common import Player, Replay, avg_mmr, debug, Game
from typing import Mapping, List
import numpy


class Environment:

    def __init__(self, add_player_to_queue):
        self._add_player_to_queue = add_player_to_queue
        self._inactive_players = []

    def one_round(self):
        for inactive in list(self._inactive_players):
            if inactive.time_until_play == 0:
                self._inactive_players.remove(inactive)
                self._add_player_to_queue(inactive.player)
            else:
                inactive.time_until_play -= 1

    def on_game_finished(self, players: List[Player]) -> None:
        for p in players:
            time_until_play = int(numpy.abs(numpy.random.normal(0, 8)))
            self._inactive_players.append(InactivePlayer(p, time_until_play))

    @staticmethod
    def create_players(num: int) -> Mapping[str, Player]:
        arr = [Environment._new_player("p" + str(i)) for i in range(num)]
        return dict([(p.name, p) for p in arr])

    def new_game(self, team_1: List[Player], team_2: List[Player]) -> Game:
        mmr1 = avg_mmr(team_1)
        mmr2 = avg_mmr(team_2)
        diff = mmr2 - mmr1
        rnd = numpy.random.normal(0, 300)
        if rnd < diff:
            win_ind = 1
        else:
            win_ind = 0
        easy_win = numpy.abs(diff - rnd)
        game_length = int(numpy.random.normal(20, 2)) - int(easy_win/100)
        debug("New game [" + str(game_length) + "]")
        return Game(game_length, team_1, team_2, win_ind)

    @staticmethod
    def player_happiness(player: Player) -> float:
        return sum([Environment._match_happiness(player, r) for r in player.replays])

    @staticmethod
    def _new_player(name: str) -> Player:
        mmr = numpy.random.normal(2200, 600)
        return Player(name, mmr)

    @staticmethod
    def _match_happiness(player: Player, replay: Replay) -> float:
        victory = player in replay.winner_team
        unfairness = min(1, replay.mmr_diff / float(500.0))
        if victory:
            return 100 * (1 - unfairness)
        return - 100 * unfairness


class InactivePlayer:
    def __init__(self, player: Player, time_until_play):
        self.player = player
        self.time_until_play = time_until_play

    def __repr__(self):
        return self.player.__repr__() + "[" + str(self.time_until_play) + "]"
