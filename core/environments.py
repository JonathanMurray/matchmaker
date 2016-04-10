import random
from typing import List
import numpy
from core.common import Player, Replay, debug, Game, Environment, avg


class AdvancedEnvironment(Environment):

    def __init__(self, num_players: int = 1000, num_active_from_start: int = 200):
        self._inactive_players = []
        self._human_index = 1
        self._humans = dict()
        self._create_humans(num_players, num_active_from_start)
        self._add_to_queue = lambda x: None
        self._remove_from_queue = lambda x: None

    def _create_humans(self, num_humans, num_active_from_start):
        for i in range(num_humans):
            h = self._create_human()
            self._humans[h.name] = h
            if i < num_active_from_start:
                self._give_player_short_break(h.name)
            else:
                self._give_player_long_break(h.name)

    def register_callbacks(self, add_to_queue, remove_from_queue):
        self._add_to_queue = add_to_queue
        self._remove_from_queue = remove_from_queue

    def get_player_skill(self, player_name):
        return self._humans[player_name].skill

    def one_round(self):
        self._add_players_that_took_a_break()
        self._remove_tired_players_from_queue()

    def _add_new_human(self):
        new_human = self._create_human()
        self._humans[new_human.name] = new_human
        self._add_to_queue(new_human.name)

    def _add_players_that_took_a_break(self):
        for inactive in list(self._inactive_players):
            if inactive.time_until_play == 0:
                self._inactive_players.remove(inactive)
                self._add_to_queue(inactive.player_name)
            else:
                inactive.time_until_play -= 1

    def _remove_tired_players_from_queue(self):
        pass #TODO

    def _give_player_a_break(self, player_name: str, time_until_queue_again: int):
        self._inactive_players.append(InactivePlayer(player_name, time_until_queue_again))

    def on_game_finished(self, game: Game) -> None:
        for p in game.team_1 + game.team_2:
            human = self._humans[p.name]
            done_for_now = len(p.replays) > human.max_games
            self._give_player_long_break(p.name) if done_for_now else self._give_player_short_break(p.name)

    def _give_player_short_break(self, player_name: str):
        break_until_next_game = int(numpy.abs(numpy.random.normal(0, 8 * 60)))
        self._give_player_a_break(player_name, break_until_next_game)

    def _give_player_long_break(self, player_name: str):
        break_until_next_game = random.randint(60, 240) * 60
        self._give_player_a_break(player_name, break_until_next_game)

    def new_game(self, team_1: List[Player], team_2: List[Player]) -> Game:
        diff = self.avg_skill_diff(team_1, team_2)
        rnd = numpy.random.normal(0, 300)
        if rnd < diff:
            win_ind = 1
        else:
            win_ind = 0
        easy_win = numpy.abs(diff - rnd)
        game_length = abs(int(numpy.random.normal(20, 2)) - int(easy_win/70)) * 60
        debug("New game [" + str(game_length) + "]")
        return Game(game_length, team_1, team_2, win_ind)

    def player_happiness(self, player: Player) -> float:
        return sum([AdvancedEnvironment._match_happiness(player, r) for r in player.replays])

    @staticmethod
    def _match_happiness(player: Player, replay: Replay) -> float:
        victory = player in replay.winner_team
        unfairness = min(1, replay.mmr_diff / float(500.0))
        if victory:
            return 100 * (1 - unfairness)
        return - 100 * unfairness

    def _create_human(self):
        max_games = random.randint(1,5)
        max_time_queue = random.randint(120, 1200)
        name = "p-" + str(self._human_index)
        self._human_index += 1
        skill = int(numpy.random.normal(2200, 600))
        return Human(max_games, max_time_queue, name, skill)

    def avg_skill_diff(self, team_1: List[Player], team_2: List[Player]):
        h_1 = [self._humans[p.name] for p in team_1]
        h_2 = [self._humans[p.name] for p in team_2]
        return avg([h.skill for h in h_2]) - avg([h.skill for h in h_1])


class InactivePlayer:
    def __init__(self, player_name: str, time_until_play):
        self.player_name = player_name
        self.time_until_play = time_until_play

    def __repr__(self):
        return self.player.__repr__() + "[" + str(self.time_until_play) + "]"


class Human:
    def __init__(self, max_games: int, max_time_queue: int, name: str, skill: int):
        self.max_games = max_games
        self.max_time_queue = max_time_queue
        self.name = name
        self.skill = skill


def max_skill_diff(team_1: List[Human], team_2: List[Human]):
    return abs(min([h.skill for h in team_1 + team_2]) - max([h.skill for h in team_1 + team_2]))


class SimpleEnvironment(Environment):

    def __init__(self):
        self._add_to_queue = lambda x: None
        self._remove_from_queue = lambda x: None
        self.round = 0
        self._skills = dict()

    def register_callbacks(self, add_to_queue, remove_from_queue):
        self._add_to_queue = add_to_queue
        self._remove_from_queue = remove_from_queue

    def new_game(self, team_1: List[Player], team_2: List[Player]) -> Game:
        avg_mmr_1 = avg([p.mmr for p in team_1])
        avg_mmr_2 = avg([p.mmr for p in team_2])
        if avg_mmr_1 > avg_mmr_2:
            return Game(20, team_1, team_2, 0)
        return Game(20, team_1, team_2, 1)

    def on_game_finished(self, game: Game) -> None:
        for name in [p.name for p in game.team_1 + game.team_2]:
            self._add_to_queue(name)

    def player_happiness(self, player: Player) -> float:
        pass

    def one_round(self) -> None:
        self.round += 1
        if self.round == 1:
            for i in range(100):
                name = "p-" + str(i+1)
                skill = int(numpy.random.normal(2200, 200))
                self._skills[name] = skill
                self._add_to_queue(name)

    def get_player_skill(self, player_name: str) -> int:
        return self._skills[player_name]