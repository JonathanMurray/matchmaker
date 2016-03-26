# ENGINE
# -------------------------

from common import Queuer, Player, Lobby
from typing import Iterable, List
import random

TEAM_SIZE = 5


def _get_random_slice(array: Iterable, slice_size: int) -> list:
    copy = list(array)
    random.shuffle(copy)
    return copy[0: slice_size]


def _pick_teams_random(queuers: Iterable[Queuer]) -> (List[Player], List[Player]):
    picked_queuers = _get_random_slice(queuers, TEAM_SIZE * 2)
    team_1 = picked_queuers[0: TEAM_SIZE]
    team_2 = picked_queuers[TEAM_SIZE: TEAM_SIZE * 2]
    return team_1, team_2


def _pick_teams_unfair(queuers: Iterable[Queuer]) -> (List[Player], List[Player]):
    picked_queuers = _get_random_slice(queuers, TEAM_SIZE * 2)
    picked_queuers.sort(key=lambda p: p.mmr)
    team_1 = picked_queuers[0: TEAM_SIZE]
    team_2 = picked_queuers[TEAM_SIZE: TEAM_SIZE * 2]
    return team_1, team_2


def _pick_teams_advanced(queue: List[Queuer]) -> (List[Queuer], List[Queuer]):
    copy = list(queue)
    ind = random.randint(0, len(copy) - TEAM_SIZE*2)
    copy.sort(key=lambda q: q.player.mmr)
    t1 = []
    t2 = []
    for i in range(TEAM_SIZE):
        t1.append(copy[(ind + 2*i) % len(copy)])
        t2.append(copy[(ind + 2*i + 1) % len(copy)])
    return [(t1, t2)]


def _pick_teams_simple(queue: List[Queuer]):
    t1 = queue[0: TEAM_SIZE]
    t2 = queue[TEAM_SIZE: TEAM_SIZE*2]
    return [(t1, t2)]


def pick_games(queue: List[Queuer], wait_times: dict) -> List[Lobby]:
    matches = _pick_teams_advanced(queue)
    for t1, t2 in matches:
        for queuer in t1 + t2:
            p_wait_times = _put_if_absent(wait_times, queuer.player, [])
            p_wait_times.append(queuer.waited)
            queue.remove(queuer)
    return [Lobby([q.player for q in t1], [q.player for q in t2]) for (t1, t2) in matches]


def _put_if_absent(the_dict: dict, key, default):
    if key in the_dict:
        return the_dict[key]
    the_dict[key] = default
    return default
