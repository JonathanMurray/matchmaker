import random
from typing import List
import numpy
from core.common import Player, Replay, avg_mmr, debug, Game, Environment


class BaseEnvironment(Environment):

    def __init__(self):
        self._inactive_players = []
        self._human_index = 1
        self._humans = dict()
        self._add_to_queue = lambda x: None
        self._remove_from_queue = lambda x: None
        self._round = 0

    def register_callbacks(self, add_to_queue, remove_from_queue):
        self._add_to_queue = add_to_queue
        self._remove_from_queue = remove_from_queue

    def one_round(self):
        self._round += 1
        self._add_new_humans()
        self._add_players_that_took_a_break()
        self._remove_tired_players_from_queue()

    def _add_new_humans(self):
        if self._round == 1:
            initial = random.randint(30, 50)
            for i in range(initial):
                self._add_new_human()
        if random.randint(1, 100) < 10:
            self._add_new_human()

    def _add_new_human(self):
        new_human = self._create_human()
        self._humans[new_human.name] = new_human
        self._add_to_queue(Player(new_human.name, new_human.mmr))

    def _add_players_that_took_a_break(self):
        for inactive in list(self._inactive_players):
            if inactive.time_until_play == 0:
                self._inactive_players.remove(inactive)
                self._add_to_queue(inactive.player)
            else:
                inactive.time_until_play -= 1

    def _remove_tired_players_from_queue(self):
        pass #TODO

    def _give_player_a_break(self, player: Player, time_until_queue_again: int):
        self._inactive_players.append(InactivePlayer(player, time_until_queue_again))

    def on_game_finished(self, game: Game) -> None:
        for p in game.team_1 + game.team_2:
            human = self._humans[p.name]
            if len(p.replays) > human.max_games:
                del self._humans[p.name]
            else:
                break_until_next_game = int(numpy.abs(numpy.random.normal(0, 8)))
                self._give_player_a_break(p, break_until_next_game)

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
        game_length = abs(int(numpy.random.normal(20, 2)) - int(easy_win/70))
        debug("New game [" + str(game_length) + "]")
        return Game(game_length, team_1, team_2, win_ind)

    def player_happiness(self, player: Player) -> float:
        return sum([BaseEnvironment._match_happiness(player, r) for r in player.replays])

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

    def _create_human(self):
        max_games = random.randint(1,5)
        max_time_queue=random.randint(120, 1200)
        name = "p-" + str(self._human_index)
        self._human_index += 1
        mmr = numpy.random.normal(2200, 600)
        return Human(max_games, max_time_queue, name, mmr)


class InactivePlayer:
    def __init__(self, player: Player, time_until_play):
        self.player = player
        self.time_until_play = time_until_play

    def __repr__(self):
        return self.player.__repr__() + "[" + str(self.time_until_play) + "]"


class Human:
    def __init__(self, max_games: int, max_time_queue: int, name: str, mmr: int):
        self.max_games = max_games
        self.max_time_queue = max_time_queue
        self.name = name
        self.mmr = mmr
