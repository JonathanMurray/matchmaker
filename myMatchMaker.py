from typing import List

from core.common import MatchMaker, Queuer


class MyMatchMaker(MatchMaker):
    def find_lobbies(self, queue: List[Queuer], found_lobby_callback) -> None:
        if len(queue) < 10:
            return []
        found_lobby_callback(queue[:5], queue[5:10])
