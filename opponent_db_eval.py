from gen_opponent import get_pig_team
from team import Team


class OpponentDBEval:
    """
    Eval how the model is doing by fighting against worthy opponents
    """

    def __init__(
        self,
    ):
        pass

    def insert_to_db(
        self, team: Team, wins: int, games_played: int, lives_remaining: int
    ):
        pass

    def get_opponent_similar_in_stregth(
        self,
        *,
        team: Team,
        num_wins: int,
        num_games_played: int,
        num_lives_remaining: int,
    ) -> Team:
        return get_pig_team(round_number=1)

    def flush(self):
        pass
