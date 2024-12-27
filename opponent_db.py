import sqlite3
import random

from gen_opponent import get_horse_team
from team import Team
from utils import compress_team, decompress_team


class OpponentDB:
    """
    The goal of this database is to store teams the model created. The model will then play against these teams as a form a self-play
    """

    def __init__(
        self,
        db_file="",
    ):
        self.conn = sqlite3.connect(db_file)
        self._init_tables()

    def _init_tables(self):
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS opponents (team TEXT, num_wins INT, num_games_played INT, num_lives_remaining INT)"
        )
        team = get_horse_team(round_number=1)
        compressed_team = compress_team(team)
        cursor = self.conn.execute(
            "SELECT 1 FROM opponents WHERE team = ?", (compressed_team,)
        )
        if cursor.fetchone() is None:  # No rows returned means the team doesn't exist
            self.insert_to_db(team, 0, 0, 5)

    def insert_to_db(
        self, team: Team, wins: int, games_played: int, lives_remaining: int
    ):
        self.conn.execute(
            "INSERT INTO opponents VALUES (?, ?, ?, ?)",
            (compress_team(team), wins, games_played, lives_remaining),
        )

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
        target_lives_remaining = num_lives_remaining
        while len(opponents_with_similar_strength) == 0:
            while (
                len(opponents_with_similar_strength) == 0 and target_lives_remaining > 0
            ):
                opponents_with_similar_strength = self.conn.execute(
                    "SELECT * FROM opponents WHERE num_games_played == ? AND num_lives_remaining == ?",
                    (target_games_played, target_lives_remaining),
                ).fetchall()
                target_lives_remaining -= 1
            target_games_played -= 1
        selected_opponent = random.choice(opponents_with_similar_strength)
        return decompress_team(selected_opponent[0])
