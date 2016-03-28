from typing import List

DEBUG = True


class Player:
    def __init__(self, name: str, mmr: int):
        self.name = name
        self.mmr = int(mmr)
        self.replays = []

    def __repr__(self):
        return self.name + "(" + str(self.mmr) + ")"


class Replay:
    def __init__(self, team_1: list, team_2: list, winner_ind: int):
        self.team_1 = team_1
        self.team_2 = team_2
        self.winner_team = (team_1, team_2)[winner_ind]
        self.mmr_diff = avg_mmr(team_2) - avg_mmr(team_1)
        self.max_mmr_diff = abs(max_mmr(team_1 + team_2) - min_mmr(team_1 + team_2))
        self.winner_ind = winner_ind

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


def avg_mmr(players: List[Player]) -> float:
    return sum([p.mmr for p in players]) / float(len(players))


def max_mmr(players: List[Player]) -> int:
    return max([p.mmr for p in players])


def min_mmr(players: List[Player]) -> int:
    return min([p.mmr for p in players])


def debug(msg):
    if DEBUG:
        print(msg)
