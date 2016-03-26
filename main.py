import random
import numpy
import matplotlib.pyplot as plt
from typing import List, Iterable, Sized, Mapping

# DEFINITIONS
# --------------------------

TEAM_SIZE = 5


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


class Match:
    def __init__(self, team_1: List[Player], team_2: List[Player]):
        self.team_1 = team_1
        self.team_2 = team_2


class Game:
    def __init__(self, time_left: int, team_1: List[Player], team_2: List[Player]):
        self.time_left = time_left
        self.team_1 = team_1
        self.team_2 = team_2

# HELPERS
# --------------------------


def avg_mmr(players: List[Player]) -> float:
    return sum([p.mmr for p in players]) / float(len(players))


def max_mmr(players: List[Player]) -> int:
    return max([p.mmr for p in players])


def min_mmr(players: List[Player]) -> int:
    return min([p.mmr for p in players])


def play_and_save_replay(team_1: List[Player], team_2: List[Player], replays: List[Replay]) -> None:
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


def buckets(x_vals: list) -> None:
    plt.hist(x_vals)


def get_random_slice(array: Iterable, slice_size: int) -> list:
    copy = list(array)
    random.shuffle(copy)
    return copy[0: slice_size]


# ENVIRONMENT
# -------------------------

def random_player(name: str) -> Player:
    mmr = numpy.random.normal(2200, 600)
    return Player(name, mmr)


def create_players(num: int) -> Mapping[str, Player]:
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


def play(team_1: List[Player], team_2: List[Player]) -> int:
    mmr1 = avg_mmr(team_1)
    mmr2 = avg_mmr(team_2)
    debug("Avg  " + str(mmr1) + " VS " + str(mmr2))
    diff = mmr2 - mmr1
    rnd = numpy.random.normal(0, 300)
    if rnd < diff:
        return 1
    return 0


# ENGINE
# -------------------------

def pick_teams_random(queuers: Iterable[Queuer]) -> (List[Player], List[Player]):
    picked_queuers = get_random_slice(queuers, TEAM_SIZE * 2)
    team_1 = picked_queuers[0: TEAM_SIZE]
    team_2 = picked_queuers[TEAM_SIZE: TEAM_SIZE * 2]
    return team_1, team_2


def pick_teams_unfair(queuers: Iterable[Queuer]) -> (List[Player], List[Player]):
    picked_queuers = get_random_slice(queuers, TEAM_SIZE * 2)
    picked_queuers.sort(key=lambda p: p.mmr)
    team_1 = picked_queuers[0: TEAM_SIZE]
    team_2 = picked_queuers[TEAM_SIZE: TEAM_SIZE * 2]
    return team_1, team_2


def pick_teams_advanced(queue: List[Queuer]) -> (List[Queuer], List[Queuer]):
    copy = list(queue)
    ind = random.randint(0, len(copy) - TEAM_SIZE*2)
    copy.sort(key=lambda q: q.player.mmr)
    t1 = []
    t2 = []
    for i in range(TEAM_SIZE):
        t1.append(copy[(ind + 2*i)% len(copy)])
        t2.append(copy[(ind + 2*i + 1) % len(copy)])
    return [(t1, t2)]


def pick_teams_from_queue(queue: List[Queuer]):
    t1 = queue[0: TEAM_SIZE]
    t2 = queue[TEAM_SIZE: TEAM_SIZE*2]
    return [(t1, t2)]


def pick_games(queue: List[Queuer], wait_times: dict) -> List[Match]:
    matches = pick_teams_advanced(queue)
    for t1, t2 in matches:
        for queuer in t1 + t2:
            p_wait_times = put_if_absent(wait_times, queuer.player, [])
            p_wait_times.append(queuer.waited)
            queue.remove(queuer)
    return [Match([q.player for q in t1], [q.player for q in t2]) for (t1, t2) in matches]


def put_if_absent(the_dict: dict, key, default):
    if key in the_dict:
        return the_dict[key]
    the_dict[key] = default
    return default

# MAIN
# -------------------------

DEBUG = True
NUM_PLAYERS = 100
NUM_GAMES = 100


def main():
    players = create_players(NUM_PLAYERS)
    print("Player MMRs: " + str(sorted([p.mmr for p in players.values()])))

    replays = []
    queue = [Queuer(p, 0) for p in players.values()]
    games = []
    wait_times = dict()

    for i in range(10):
        print(i)
        for queuer in queue:
            queuer.waited += 1
        matches = pick_games(queue, wait_times)
        for m in matches:
            games.append(Game(5, m.team_1, m.team_2))
            print("Found game")
            print(m.team_1)
            print(m.team_2)
            print(".......")
        for g in list(games):
            g.time_left -= 1
            if g.time_left == 0:
                play_and_save_replay(g.team_1, g.team_2, replays)
                queue.extend([Queuer(p, 0) for p in g.team_1 + g.team_2])
                games.remove(g)

    active_players = [p for p in players.values() if len(p.replays) > 0]
    winrate_map = dict([(p.name, player_winrate(p)) for p in active_players])

    mmr_diffs = [r.max_mmr_diff for r in replays]

    plt.subplot(121)
    # plot("", "MMR-diff", mmr_diffs, "...", [1] * len(mmr_diffs))
    # plt.subplot(122)
    # plot("", "Queue time", list(wait_times.values()), "...", [1] * len(wait_times))
    # plt.show()
    buckets(mmr_diffs)

    print(mmr_diffs)

    plt.subplot(122)

    all_wait_times = [w for sub in wait_times.values() for w in sub]
    buckets(all_wait_times)

    plt.show()
    print("done")


main()
