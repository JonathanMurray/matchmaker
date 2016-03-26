import matplotlib.pyplot as plt
from typing import List
from common import Player, Queuer, Game, Replay
from engine import pick_games
from environment import play, create_players


def play_and_save_replay(team_1: List[Player], team_2: List[Player], replays: List[Replay]) -> None:
    winner_ind = play(team_1, team_2)
    replay = Replay(team_1, team_2, winner_ind)
    replays.append(replay)
    for i in range(2):
        team = (team_1, team_2)[i]
        for p in team:
            p.replays.append(replay)


def plot(title: str, x_label: str, x_vals: list, y_label: str, y_vals) -> None:
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.plot(x_vals, y_vals, 'ro')
    plt.grid(True)


def player_winrate(p: Player) -> float:
    victories = [1 if p in r.winner_team else 0 for r in p.replays]
    return sum(victories) / float(len(p.replays))


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
    plt.hist(mmr_diffs)

    print(mmr_diffs)

    plt.subplot(122)

    all_wait_times = [w for sub in wait_times.values() for w in sub]
    plt.hist(all_wait_times)

    plt.show()
    print("done")


main()
