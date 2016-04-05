from typing import List

import matplotlib.pyplot as plt
from common import Player, Queuer, Replay, Game, debug
from matchmaker import MatchMaker, advanced_matchmaker2, fair_matchmaker
from environment import Environment


class Engine:

    def __init__(self, match_maker: MatchMaker, environment: Environment):
        self.queue = []
        self.wait_times = dict()
        self.game_lengths = dict()
        self.games = []
        self.afk_players = []
        self.replays = []
        self.match_maker = match_maker
        self.environment = environment
        self.environment.add_player_to_queue = self.add_to_queue
        self._players = dict()

    def add_players(self):
        self._players = self.environment.create_players(NUM_PLAYERS)
        debug("Player MMRs: " + str(sorted([p.mmr for p in self._players.values()])))
        self.queue = [Queuer(p, 0) for p in self._players.values()]

    def one_round(self):
        for queuer in self.queue:
            queuer.waited += 1
        lobbies = self.match_maker.find_lobbies(self.queue, self._on_found_lobby)
        for l in lobbies:
            self.games.append(self.environment.new_game(l.team_1, l.team_2))
            debug("Found game")
            debug(l.team_1)
            debug(l.team_2)
        debug("Queue size: " + str(len(self.queue)))
        debug("...")
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
        array = Engine._put_if_absent(the_dict, key, [])
        array.append(value)

    @staticmethod
    def _put_if_absent(the_dict: dict, key, default):
        if key in the_dict:
            return the_dict[key]
        the_dict[key] = default
        return default

    def active_players(self):
        return [p for p in self._players.values() if len(p.replays) > 0]

    @staticmethod
    def plot(title: str, x_label: str, x_vals: list, y_label: str, y_vals) -> None:
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.plot(x_vals, y_vals, 'ro')
        plt.grid(True)

    @staticmethod
    def player_winrate(p: Player) -> float:
        victories = [1 if p in r.winner_team else 0 for r in p.replays]
        return sum(victories) / float(len(p.replays))

    def players_with_min_mmr(self, mmr):
        return [p for p in self._players.values() if p.mmr > mmr]

    def statistics(self, players: List[Player]):
        replays = [r for r in self.replays if Engine._replay_contains_some_player(r, players)]
        wait_time_lists = [v for (k, v) in self.wait_times.items() if k in players]
        game_length_lists = [v for (k, v) in self.game_lengths.items() if k in players]
        active = [p for p in players if p in self.active_players()]

        mmr_diffs = [r.max_mmr_diff for r in replays]
        wait_times = [w for sub in wait_time_lists for w in sub]
        game_lengths = [l for sub in game_length_lists for l in sub]
        win_rates = [Engine.player_winrate(p) for p in active]

        print("-----------------------------------------------")
        print("-------------- SIMULATION IS OVER -------------")
        print("-----------------------------------------------")
        print("Number of games: " + str(len(self.replays)))
        print("Avg queue time: " + str(sum(wait_times) / len(wait_times)))
        print("Avg max mmr diff: " + str(sum(mmr_diffs) / len(mmr_diffs)))
        print("Avg game length: " + str(sum(game_lengths) / len(game_lengths)))
        print("Queue state: " + str(self.queue))
        print("Stats players: " + str(players))
        print("Active: " + str(active))


        return Statistics(mmr_diffs, wait_times, game_lengths, win_rates)

    @staticmethod
    def _replay_contains_some_player(replay: Replay, players: List[Player]):
        return any(p in (replay.team_1 + replay.team_2) for p in players)


NUM_PLAYERS = 95
NUM_ROUNDS = 2000


class Statistics:
    def __init__(self, mmr_diffs, wait_times, game_lengths, win_rates):
        self.mmr_diffs = mmr_diffs
        self.wait_times = wait_times
        self.game_lengths = game_lengths
        self.win_rates = win_rates


def run_and_plot(plot_index, num_plots, match_maker, environment):
    engine = Engine(match_maker, environment)
    engine.add_players()
    for i in range(NUM_ROUNDS):
        engine.one_round()
    target_players = engine.players_with_min_mmr(0)
    plot(plot_index, num_plots, engine.statistics(target_players))


def plot(plot_index, num_plots, statistics: Statistics):
    ver = 2
    hor = 2
    diagrams = ver * hor

    bins = 20

    plt.subplot(ver * num_plots, hor, 1 + plot_index*diagrams)
    plt.title("max MMR-diff")
    plt.hist(statistics.mmr_diffs, range=[0, 3500], bins=bins)

    plt.subplot(ver * num_plots, hor, 2 + plot_index*diagrams)
    plt.title("queue time")
    plt.hist(statistics.wait_times, range=[0, 50], bins=bins)

    plt.subplot(ver * num_plots, hor, 3 + plot_index*diagrams)
    plt.title("game length")
    plt.hist(statistics.game_lengths, range=[0, 40], bins=bins)

    plt.subplot(ver * num_plots, hor, 4 + plot_index*diagrams)
    plt.title("win-rate")
    plt.hist(statistics.win_rates, range=[0, 1], bins=bins)

NUM_PLOTS = 2
run_and_plot(0, NUM_PLOTS, fair_matchmaker, Environment())
run_and_plot(1, NUM_PLOTS, advanced_matchmaker2, Environment())
plt.show()
