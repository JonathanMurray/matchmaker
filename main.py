import random
import numpy
import matplotlib.pyplot as plt

# DEFINITIONS
# --------------------------

TEAM_SIZE = 5


class Player:
    def __init__(self, name, mmr):
        self.name = str(name)
        self.mmr = int(mmr)
        self.replays = []

    def __str__(self):
        return self.name + "(" + str(self.mmr) + ")"

    def __repr__(self):
        return self.__str__()


class Replay:
    def __init__(self, team_1, team_2, winner):
        self.team_1 = team_1
        self.team_2 = team_2
        self.mmr_diff = avg_mmr(team_2) - avg_mmr(team_1)
        self.winner = winner
        self.replays = []

    def __repr__(self):
        return "mmr diff: " + str(self.mmr_diff)


# HELPERS
# --------------------------

def avg_mmr(players):
    return sum([p.mmr for p in players]) / len(players)


def play_and_save_replay(team_1, team_2, replays):
    winner = play(team_1, team_2)
    replay = Replay(team_1, team_2, winner)
    replays.append(replay)
    for i in range(2):
        team = [team_1, team_2][i]
        for p in team:
            p.replays.append(replay)


def player_replay_str(p_replay):
    replay = p_replay.replay
    team_number = p_replay.team_number
    victory = team_number == replay.winner
    mmr_diff = replay.mmr_diff if team_number == 2 else - replay.mmr_diff
    return ("Victory" if victory else "Defeat") + " [mmr diff: " + str(mmr_diff) + "]"


def debug(msg):
    if DEBUG:
        print(msg)


def plot(players, vals_by_name, ylabel):
    mmrs = [p.mmr for p in players]
    yvals = [vals_by_name[p.name] for p in players]
    plt.xlabel('MMR')
    plt.ylabel(ylabel)
    plt.title('Players')
    plt.plot(mmrs, yvals, 'ro')
    plt.grid(True)
    plt.show()


def get_random_slice(array, slice_size):
    copy = list(array)
    random.shuffle(copy)
    return copy[0: slice_size]


# ENVIRONMENT
# -------------------------

def random_player(name):
    mmr = numpy.random.normal(2200, 600)
    return Player(name, mmr)


def create_players(num):
    arr = [random_player("p" + str(i)) for i in range(num)]
    return dict([(p.name, p) for p in arr])


def player_happiness(p_replay, replays):
    replay = replays[p_replay.replay_index]
    victory = p_replay.team_number == replay.winner
    unfairness = min(1, replay.mmr_diff / 500.0)
    if victory:
        return 100 * (1 - unfairness)
    else:
        return - 100 * unfairness


def is_victory(p_replay, replays):
    index = p_replay.replay_index
    replay = replays[index]
    return p_replay.team_number == replay.winner


def player_winrate(name, histories, replays):
    h = histories[name]
    return sum([1 if is_victory(pr, replays) else 0 for pr in h]) / float(len(h))


def total_player_happiness(name, histories, replays):
    if name not in histories:
        return 0
    h = histories[name]
    return sum([player_happiness(pr, replays) for pr in h])


def play(team_1, team_2):
    mmr1 = avg_mmr(team_1)
    mmr2 = avg_mmr(team_2)
    debug(str(mmr1) + " VS " + str(mmr2))
    diff = mmr2 - mmr1
    rnd = numpy.random.normal(0, 100)
    if rnd < diff:
        return 2
    return 1


# ENGINE
# -------------------------

def pick_teams_random(players):
    picked_players = get_random_slice(players, TEAM_SIZE * 2)
    team_1 = picked_players[0: TEAM_SIZE]
    team_2 = picked_players[TEAM_SIZE: TEAM_SIZE * 2]
    return team_1, team_2


def pick_teams_unfair(players):
    picked_players = get_random_slice(players, TEAM_SIZE * 2)
    picked_players.sort(key=lambda p: p.mmr)
    team_1 = picked_players[0: TEAM_SIZE]
    team_2 = picked_players[TEAM_SIZE: TEAM_SIZE * 2]
    return team_1, team_2


# MAIN
# -------------------------

DEBUG = False
NUM_PLAYERS = 100
NUM_GAMES = 100


def main():
    players = create_players(NUM_PLAYERS)
    print("Player MMRs: " + str(sorted([p.mmr for p in players.values()])))

    replays = []
    player_histories = {}

    for i in range(NUM_GAMES):
        teams = pick_teams_random(players.values())
        play_and_save_replay(teams[0], teams[1], replays)

    active_players = [p for p in players.values() if p.name in player_histories]
    winrate_map = dict([(p.name, player_winrate(p.name, player_histories, replays)) for p in active_players])
    plot(active_players, winrate_map, "Win-rate")


main()
