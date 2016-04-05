from typing import List, Tuple
import matplotlib.pyplot as plt
from core.common import MatchMaker, Environment, Statistics, debug
from core.engine import Engine


class Runner:

    def __init__(self, num_players=95, num_rounds=2000, min_mmr=0, max_mmr=100000):
        self.num_players = num_players
        self.num_rounds = num_rounds
        self.min_mmr = min_mmr
        self.max_mmr = max_mmr

    def run_and_plot(self, runs: List[Tuple[str, MatchMaker, Environment]]) -> None:
        for i, run in enumerate(runs):
            (name, match_maker, environment) = run
            debug("Running " + name + " ...")
            self._run_and_plot(i, len(runs), name, match_maker, environment)
        plt.show()

    def _run_and_plot(self, plot_index, num_plots, name, match_maker, environment):
        engine = Engine(match_maker, environment)
        engine.add_players(self.num_players)
        for i in range(self.num_rounds):
            engine.one_round()
        target_players = engine.players_with_mmr_between(self.min_mmr, self.max_mmr)
        stats = engine.statistics(target_players)
        Runner._print_stats(name, stats)
        Runner._plot(plot_index, num_plots, stats)

    @staticmethod
    def _print_stats(name, stats):
        print("")
        print(name)
        print("--------------------------")
        print("Number of games: " + str(stats.num_games))
        print("Avg queue time: " + str(stats.avg_queue_time))
        print("Avg max mmr diff: " + str(stats.avg_max_mmr_diff))
        print("Avg game length: " + str(stats.avg_game_length))
        print("Queue state: " + str(stats.queue))

    @staticmethod
    def _plot(plot_index, num_plots, statistics: Statistics):
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
