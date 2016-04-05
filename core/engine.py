from typing import List, Any
from core.common import Player, Queuer, Replay, Game, debug, MatchMaker, Environment, Statistics, Lobby


class DataStore:
    def __init__(self):
        self.wait_times = dict()
        self.replays = []

    def store_replay(self, replay):
        self.replays.append(replay)

    def store_wait_time(self, player, wait_time):
        self._add_mapping(self.wait_times, player, wait_time)

    @staticmethod
    def _add_mapping(the_dict: dict, key, value):
        array = DataStore._put_if_absent(the_dict, key, [])
        array.append(value)

    @staticmethod
    def _put_if_absent(the_dict: dict, key, default):
        if key in the_dict:
            return the_dict[key]
        the_dict[key] = default
        return default


class Engine:

    def __init__(self, match_maker: MatchMaker, environment: Environment):
        self._match_maker = match_maker
        self._environment = environment
        self._environment.add_player_to_queue = self._add_to_queue
        self._queue = []
        self._games = []
        self._lobbies = []
        self._players = dict()
        self._data_store = DataStore()

    def queue(self):
        return self._queue

    def add_players(self, num_players):
        self._players = self._environment.create_players(num_players)
        debug("Player MMRs: " + str(sorted([p.mmr for p in self._players.values()])))
        self._queue = [Queuer(p, 0) for p in self._players.values()]

    def one_round(self):
        for queuer in self._queue:
            queuer.waited += 1
        self._find_lobbies_and_start_games()
        debug("Queue size: " + str(len(self._queue)))
        debug("...")
        self._progress_games()
        self._environment.one_round()

    def _find_lobbies_and_start_games(self):
        self._match_maker.find_lobbies(self._queue, self._on_found_lobby)
        for l in self._lobbies:
            self._games.append(self._environment.new_game(l.team_1, l.team_2))
            debug("Found game")
            debug(l.team_1)
            debug(l.team_2)
        self._lobbies = []

    def _add_to_queue(self, player: Player):
        self._queue.append(Queuer(player, 0))

    def _on_game_finished(self, game: Game) -> None:
        self._environment.on_game_finished(game.team_1 + game.team_2)
        self._games.remove(game)
        replay = Replay(game.team_1, game.team_2, game.winner_index, game.length)
        self._data_store.store_replay(replay)
        for p in game.team_1 + game.team_2:
            p.replays.append(replay)

    def _on_found_lobby(self, team_1: List[Queuer], team_2: List[Queuer]):
        lobby = Lobby([q.player for q in team_1], [q.player for q in team_2])
        self._lobbies.append(lobby)
        for queuer in team_1 + team_2:
            self._data_store.store_wait_time(queuer.player, queuer.waited)
            self._queue.remove(queuer)

    def _progress_games(self):
        for g in list(self._games):
            g.time_left -= 1
            if g.time_left == 0:
                self._on_game_finished(g)

    def active_players(self):
        return [p for p in self._players.values() if len(p.replays) > 0]

    @staticmethod
    def player_winrate(p: Player) -> float:
        victories = [1 if p in r.winner_team else 0 for r in p.replays]
        return sum(victories) / float(len(p.replays))

    def players_with_mmr_between(self, min_mmr, max_mmr):
        return [p for p in self._players.values() if min_mmr <= p.mmr <= max_mmr]

    def statistics(self, players: List[Player]):
        relevant_replays = [r for r in self._data_store.replays if Engine._replay_contains_some_of(r, players)]
        wait_time_lists = [v for (k, v) in self._data_store.wait_times.items() if k in players]
        active = [p for p in players if p in self.active_players()]

        mmr_diffs = [r.max_mmr_diff for r in relevant_replays]
        wait_times = [w for sub in wait_time_lists for w in sub]
        game_lengths = [r.game_length for r in relevant_replays]
        win_rates = [Engine.player_winrate(p) for p in active]

        num_games = len(self._data_store.replays)
        avg_queue_time = avg(wait_times) if len(wait_times) > 0 else -1
        avg_max_mmr_diff = avg(mmr_diffs) if len(mmr_diffs) > 0 else -1
        avg_game_length = avg(game_lengths) if len(game_lengths) > 0 else -1

        return Statistics(mmr_diffs, wait_times, game_lengths, win_rates, num_games, avg_queue_time,
                          avg_max_mmr_diff, avg_game_length, self._queue)

    @staticmethod
    def _replay_contains_some_of(replay: Replay, players: List[Player]):
        return any(p in (replay.team_1 + replay.team_2) for p in players)


def avg(arr: List[Any]):
    return sum(arr) / len(arr)
