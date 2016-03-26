from common import Player, Replay, avg_mmr, debug
from typing import Mapping, List
import numpy


def _random_player(name: str) -> Player:
    mmr = numpy.random.normal(2200, 600)
    return Player(name, mmr)


def create_players(num: int) -> Mapping[str, Player]:
    arr = [_random_player("p" + str(i)) for i in range(num)]
    return dict([(p.name, p) for p in arr])


def match_happiness(player: Player, replay: Replay) -> float:
    victory = player in replay.winner_team
    unfairness = min(1, replay.mmr_diff / float(500.0))
    if victory:
        return 100 * (1 - unfairness)
    return - 100 * unfairness


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
