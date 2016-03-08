import random
import numpy
import matplotlib.pyplot as plt
from typing import List, Iterable, Sized

# DEFINITIONS
# --------------------------

TEAM_SIZE = 5


class Player:
    def __init__(self, name: str, mmr: int):
        self.name = name
        self.mmr = int(mmr)
        self.replays = []

    def __str__(self):
        return self.name + "(" + str(self.mmr) + ")"

    def __repr__(self):
        return self.__str__()


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


# HELPERS
# --------------------------

def avg_mmr(players: list) -> float:
    return sum([p.mmr for p in players]) / float(len(players))


def max_mmr(players: list) -> int:
    return max([p.mmr for p in players])


def min_mmr(players: list) -> int:
    return min([p.mmr for p in players])


def play_and_save_replay(team_1: list, team_2: list, replays: list) -> None:
    winner_ind = play(team_1, team_2)
    replay = Replay(team_1, team_2, winner_ind)
    replays.append(replay)
    for i in range(2):
        team = (team_1, team_2)[i]
        for p in team:
            p.replays.append(replay)


def debug(msg):
    if DEBUG:
        print(msg)


def plot(title: str, x_label: str, x_vals: list, y_label: str, y_vals) -> None:
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.plot(x_vals, y_vals, 'ro')
    plt.grid(True)
    plt.show()


def get_random_slice(array: Iterable, slice_size: int) -> list:
    copy = list(array)
    random.shuffle(copy)
    return copy[0: slice_size]


# ENVIRONMENT
# -------------------------

def random_player(name: str) -> Player:
    mmr = numpy.random.normal(2200, 600)
    return Player(name, mmr)


def create_players(num: int) -> dict:
    arr = [random_player("p" + str(i)) for i in range(num)]
    return dict([(p.name, p) for p in arr])


def match_happiness(player: Player, replay: Replay) -> float:
    victory = player in replay.winner_team
    unfairness = min(1, replay.mmr_diff / float(500.0))
    if victory:
        return 100 * (1 - unfairness)
    return - 100 * unfairness


def player_winrate(p: Player) -> float:
    victories = [1 if p in r.winner_team else 0 for r in p.replays]
    return sum(victories) / float(len(p.replays))


def player_happiness(player: Player) -> float:
    return sum([match_happiness(player, r) for r in player.replays])


def play(team_1: list, team_2: list) -> int:
    mmr1 = avg_mmr(team_1)
    mmr2 = avg_mmr(team_2)
    debug(str(mmr1) + " VS " + str(mmr2))
    diff = mmr2 - mmr1
    rnd = numpy.random.normal(0, 300)
    if rnd < diff:
        return 1
    return 0


# ENGINE
# -------------------------

def pick_teams_random(players: Iterable) -> (list, list):
    picked_players = get_random_slice(players, TEAM_SIZE * 2)
    team_1 = picked_players[0: TEAM_SIZE]
    team_2 = picked_players[TEAM_SIZE: TEAM_SIZE * 2]
    return team_1, team_2


def pick_teams_unfair(players: Iterable) -> (list, list):
    picked_players = get_random_slice(players, TEAM_SIZE * 2)
    picked_players.sort(key=lambda p: p.mmr)
    team_1 = picked_players[0: TEAM_SIZE]
    team_2 = picked_players[TEAM_SIZE: TEAM_SIZE * 2]
    return team_1, team_2


def pick_teams(players: list) -> (list, list):
    copy = list(players)
    ind = random.randint(0, len(copy) - TEAM_SIZE*2)
    copy.sort(key=lambda p: p.mmr)
    t1 = []
    t2 = []
    for i in range(TEAM_SIZE):
        t1.append(copy[(ind + 2*1) % len(copy)])
        t2.append(copy[(ind + 2*1 + 1) % len(copy)])
    return t1, t2


# MAIN
# -------------------------

DEBUG = True
NUM_PLAYERS = 100
NUM_GAMES = 100


def main():
    players = create_players(NUM_PLAYERS)
    print("Player MMRs: " + str(sorted([p.mmr for p in players.values()])))

    replays = []

    for i in range(NUM_GAMES):
        teams = pick_teams(list(players.values()))
        play_and_save_replay(teams[0], teams[1], replays)

    active_players = [p for p in players.values() if len(p.replays) > 0]
    winrate_map = dict([(p.name, player_winrate(p)) for p in active_players])

    mmr_diffs = [r.max_mmr_diff for r in replays]
    plot("MMR Differences", "MMR-diff", mmr_diffs, "...", [1] * len(mmr_diffs))


main()
