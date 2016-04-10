from core.common import MmrEngine, Game


class BaseMmrEngine(MmrEngine):

    def on_game_finished(self, game: Game):
        teams = [game.team_1, game.team_2] if game.winner_index == 0 else [game.team_2, game.team_1]
        for winner in teams[0]:
            winner.mmr += 100
        for loser in teams[1]:
            loser.mmr -= 100

    def initial_mmr(self):
        return 2200
