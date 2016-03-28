from typing import List

import matplotlib.pyplot as plt
from common import Player, Queuer, Replay, Game
from matchmaker import MatchMaker
from environment import Environment


def plot(title: str, x_label: str, x_vals: list, y_label: str, y_vals) -> None:
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.plot(x_vals, y_vals, 'ro')
    plt.grid(True)


def player_winrate(p: Player) -> float:
    victories = [1 if p in r.winner_team else 0 for r in p.replays]
    return sum(victories) / float(len(p.replays))


class Main:

    def __init__(self):
        self.queue = []
        self.wait_times = dict()
        self.game_lengths = dict()
        self.games = []
        self.afk_players = []
        self.replays = []
        self.match_maker = MatchMaker()
        self.environment = Environment(self.add_to_queue)
        self._players = dict()

    def add_players(self):
        self._players = self.environment.create_players(NUM_PLAYERS)
        print("Player MMRs: " + str(sorted([p.mmr for p in self._players.values()])))
        self.queue = [Queuer(p, 0) for p in self._players.values()]

    def one_round(self):
        for queuer in self.queue:
            queuer.waited += 1
        lobbies = self.match_maker.find_lobbies(self.queue, self._on_found_lobby)
        for l in lobbies:
            self.games.append(self.environment.new_game(l.team_1, l.team_2))
            print("Found game")
            print(l.team_1)
            print(l.team_2)
        print("Queue size: " + str(len(self.queue)))
        print("...")
        for g in list(self.games):
            g.time_left -= 1
            if g.time_left == 0:
                self._on_game_finished(g)
        self.environment.one_round()

    def add_to_queue(self, player: Player):
        self.queue.append(Queuer(player, 0))

    def _on_game_finished(self, game: Game) -> None:
        self.environment.on_game_finished(game.team_1 + game.team_2)
        self.games.remove(game)
        replay = Replay(game.team_1, game.team_2, game.winner_index)
        self.replays.append(replay)
        for p in game.team_1 + game.team_2:
            p.replays.append(replay)
            self._add_mapping(self.game_lengths, p, game.length)

    def _on_found_lobby(self, queuers: List[Queuer]):
        for queuer in queuers:
            self._add_mapping(self.wait_times, queuer.player, queuer.waited)
            self.queue.remove(queuer)

    @staticmethod
    def _add_mapping(the_dict: dict, key, value):
        array = Main._put_if_absent(the_dict, key, [])
        array.append(value)

    @staticmethod
    def _put_if_absent(the_dict: dict, key, default):
        if key in the_dict:
            return the_dict[key]
        the_dict[key] = default
        return default

    def active_players(self):
        return [p for p in self._players.values() if len(p.replays) > 0]





DEBUG = True
NUM_PLAYERS = 95
NUM_ROUNDS = 150

main = Main()
main.add_players()
for i in range(NUM_ROUNDS):
    main.one_round()

winrate_map = dict([(p.name, player_winrate(p)) for p in main.active_players()])

mmr_diffs = [r.max_mmr_diff for r in main.replays]

plt.subplot(221)
plt.title("max MMR-diff")
plt.hist(mmr_diffs)
print(mmr_diffs)
plt.subplot(222)
all_wait_times = [w for sub in main.wait_times.values() for w in sub]
plt.title("queue time")
plt.hist(all_wait_times)
plt.subplot(223)
all_lengths = [l for sub in main.game_lengths.values() for l in sub]
plt.title("game length")
plt.hist(all_lengths)

plt.show()
print("done")
