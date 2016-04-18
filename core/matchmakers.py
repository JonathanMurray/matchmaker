# ENGINE
# -------------------------

import random
from typing import Iterable, List
from core.common import Queuer, Player, max_mmr, min_mmr, Lobby, MatchMaker

TEAM_SIZE = 5


class CompositeMatchmaker(MatchMaker):

    def __init__(self, find_lobby):
        self._find_lobby = find_lobby

    def find_lobbies(self, queue: List[Queuer], found_lobby_callback) -> None:
        found = self._find_lobby(queue)
        while found is not None:
            t1, t2 = found
            found_lobby_callback(t1, t2)
            found = self._find_lobby(queue)


def find_by_sorted_mmr(queue: List[Queuer]) -> (List[Queuer], List[Queuer]):
    if len(queue) < TEAM_SIZE*2:
        return None
    copy = sorted_queue(queue)
    ind = random.randint(0, len(copy) - TEAM_SIZE*2)
    t1 = []
    t2 = []
    for i in range(TEAM_SIZE):
        t1.append(copy[(ind + 2*i) % len(copy)])
        t2.append(copy[(ind + 2*i + 1) % len(copy)])
    return t1, t2


def sorted_queue(queue):
    copy = list(queue)
    copy.sort(key=lambda q: q.player.mmr)
    return copy


def max_mmr_diff(mmr_boundary):
    return lambda t1, t2: _max_mmr_diff_filter(t1, t2, mmr_boundary)


def _max_mmr_diff_filter(t1, t2, mmr_diff_boundary):
    players = [q.player for q in t1+t2]
    diff = abs(max_mmr(players) - min_mmr(players))
    return diff < mmr_diff_boundary


def max_mmr_diff_or_long_wait(mmr_diff_boundary, wait_boundary):
    return lambda t1, t2: _max_mmr_diff_filter(t1, t2, mmr_diff_boundary) or _long_wait_filter(t1, t2, wait_boundary)


def _long_wait_filter(t1, t2, wait_boundary):
    return any(q.waited > wait_boundary for q in t1 + t2)


def filtered_find_by_sorted_mmr(num_tries: int, lobby_filter) -> Lobby:
    return lambda queue: _filtered_find_by_sorted_mmr(queue, num_tries, lobby_filter)


def fair_method(queue: List[Queuer]) -> (List[Queuer], List[Queuer]):
    if len(queue) < TEAM_SIZE*2:
        return None
    num_tries = min(100, len(queue))
    for i in range(num_tries):
        queuer = queue[i]
        found = find_lobby_for(queuer, queue)
        if found is not None:
            return found
    return None


def find_lobby_for(queuer: Queuer, queue: List[Queuer]) -> (List[Queuer], List[Queuer]):
    sorted_by_mmr = sorted_queue(queue)
    ind = index_of(queuer, sorted_by_mmr)
    pick_right = len(queue) - ind
    if pick_right >= TEAM_SIZE*2:
        picked = sorted_by_mmr[ind: ind+TEAM_SIZE*2]
    else:
        pick_left = TEAM_SIZE*2 - pick_right
        picked = sorted_by_mmr[ind - pick_left: ind + pick_right]
    t1, t2 = [], []
    for i in range(TEAM_SIZE):
        t1.append(picked[2*i])
        t2.append(picked[2*i+1])
    return (t1, t2) if _is_good_enough(t1, t2) else None


def _is_good_enough(t1, t2):
    if _max_wait(t1, t2) < 300:
        mmr_boundary = 100 + _max_wait(t1, t2)
    else:
        mmr_boundary = 100 + _max_wait(t1, t2) * 2
    return _max_mmr_diff_filter(t1, t2, mmr_boundary)


def _max_wait(t1, t2):
    return max(q.waited for q in t1 + t2)


def index_of(el, arr):
    return [i for i, x in enumerate(arr) if x == el][0]


def _filtered_find_by_sorted_mmr(queue: List[Queuer], num_tries: int, lobby_filter) -> Lobby:
    if len(queue) < TEAM_SIZE*2:
        return None
    for i in range(num_tries):
        t1, t2 = find_by_sorted_mmr(queue)
        valid_lobby = lobby_filter(t1, t2)
        if valid_lobby:
            return t1, t2
    return None


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


def _pick_teams_simple(queue: List[Queuer]):
    t1 = queue[0: TEAM_SIZE]
    t2 = queue[TEAM_SIZE: TEAM_SIZE*2]
    return [(t1, t2)]


simple_matchmaker = CompositeMatchmaker(find_by_sorted_mmr)
advanced_matchmaker = CompositeMatchmaker(filtered_find_by_sorted_mmr(50, max_mmr_diff(300)))
advanced_matchmaker2 = CompositeMatchmaker(filtered_find_by_sorted_mmr(50, max_mmr_diff_or_long_wait(300, 60*5)))
fair_matchmaker = CompositeMatchmaker(fair_method)
