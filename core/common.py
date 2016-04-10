from typing import List, Any
from abc import abstractmethod

DEBUG = False


class Player:
    def __init__(self, name: str, mmr: int):
        self.name = name
        self.mmr = int(mmr)
        self.replays = []

    def __repr__(self):
        return self.name + "(" + str(self.mmr) + ")"


class Replay:
    def __init__(self, team_1: list, team_2: list, winner_ind: int, game_length: int):
        self.team_1 = team_1
        self.team_2 = team_2
        self.winner_team = (team_1, team_2)[winner_ind]
        self.mmr_diff = avg_mmr(team_2) - avg_mmr(team_1)
        self.max_mmr_diff = max_mmr_diff(team_1, team_2)
        self.winner_ind = winner_ind
        self.game_length = game_length

    def __repr__(self):
        return "mmr diff: " + str(self.mmr_diff)


class Queuer:
    def __init__(self, player: Player, waited: int):
        self.player = player
        self.waited = waited

    def __repr__(self):
        return self.player.__repr__() + "[" + str(self.waited) + "s]"


class Game:
    def __init__(self, game_length: int, team_1: List[Player], team_2: List[Player], winner_index: int):
        self.length = game_length
        self.time_left = game_length
        self.team_1 = team_1
        self.team_2 = team_2
        self.winner_index = winner_index


class Lobby:
    def __init__(self, team_1: List[Player], team_2: List[Player]):
        self.team_1 = team_1
        self.team_2 = team_2

    def __repr__(self):
        return "Lobby: " + str(self.team_1) + " VS " + str(self.team_2)


class MatchMaker:
    @abstractmethod
    def find_lobbies(self, queue: List[Queuer], found_lobby_callback) -> None:
        pass


class Environment:

    @abstractmethod
    def register_callbacks(self, add_to_queue, remove_from_queue):
        pass

    @abstractmethod
    def one_round(self) -> None:
        pass

    @abstractmethod
    def on_game_finished(self, game: Game) -> None:
        pass

    @abstractmethod
    def new_game(self, team_1: List[Player], team_2: List[Player]) -> Game:
        pass

    @abstractmethod
    def player_happiness(self, player: Player) -> float:
        pass

    @abstractmethod
    def get_player_skill(self, player_name: str) -> int:
        pass


class MmrEngine:

    @abstractmethod
    def on_game_finished(self, game: Game):
        pass

    @abstractmethod
    def initial_mmr(self):
        pass


class Statistics:
    def __init__(self,
                 mmr_diffs: List[int],
                 wait_times: List[int],
                 game_lengths: List[int],
                 win_rates: List[float],
                 num_games: int,
                 avg_queue_time: float,
                 avg_max_mmr_diff: float,
                 avg_game_length: float,
                 queue: List[Queuer]):

        self.mmr_diffs = mmr_diffs
        self.wait_times = wait_times
        self.game_lengths = game_lengths
        self.win_rates = win_rates
        self.num_games = num_games
        self.avg_queue_time = avg_queue_time
        self.avg_max_mmr_diff = avg_max_mmr_diff
        self.avg_game_length = avg_game_length
        self.queue = queue


def avg_mmr(players: List[Player]) -> float:
    return sum([p.mmr for p in players]) / float(len(players))


def max_mmr(players: List[Player]) -> int:
    return max([p.mmr for p in players])


def min_mmr(players: List[Player]) -> int:
    return min([p.mmr for p in players])


def max_mmr_diff(team_1: List[Player], team_2: List[Player]) -> int:
    return abs(max_mmr(team_1 + team_2) - min_mmr(team_1 + team_2))

def debug(msg):
    if DEBUG:
        print(msg)


def avg(arr: List[Any]):
    return sum(arr) / len(arr)