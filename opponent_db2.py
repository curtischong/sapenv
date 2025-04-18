from collections import defaultdict
import random

from gen_opponent import get_horse_team
from team import Team
from utils import compress_team, decompress_team


class OpponentDBInMemory:
    """
    The goal of this database is to store teams the model created. The model will then play against these teams as a form a self-play
    """

    def __init__(
        self,
    ):
        self._init_tables()

    def _init_tables(self):
        # maps (num_games_played, lives_remaining) -> list[compressed_team]
        self.teams: dict[tuple[int, int], list[str]] = defaultdict(list)
        team = get_horse_team(round_number=1)
        # compressed_team = compress_team(team)
        self.insert_to_db(team, 0, 0, 5)

    def insert_to_db(
        self, team: Team, wins: int, games_played: int, lives_remaining: int
    ):
        self.teams[(games_played, lives_remaining)].append(compress_team(team))

    def get_opponent_similar_in_stregth(
        self,
        *,
        team: Team,
        num_wins: int,
        num_games_played: int,
        num_lives_remaining: int,
    ) -> Team:
        opponents_with_similar_strength = []
        target_games_played = num_games_played
        while len(opponents_with_similar_strength) == 0 and target_games_played > 0:
            target_lives_remaining = num_lives_remaining
            while (
                len(opponents_with_similar_strength) == 0 and target_lives_remaining > 0
            ):
                opponents_with_similar_strength = self.teams[
                    (target_games_played, target_lives_remaining)
                ]
                target_lives_remaining -= 1
            target_games_played -= 1

        # sometimes when the db is flushed, the opponent is not found. In this case, we just return the horse team
        if target_games_played == 0:
            return get_horse_team(round_number=1)

        selected_opponent = random.choice(opponents_with_similar_strength)
        return decompress_team(selected_opponent)

    def flush(self):
        self._init_tables()
