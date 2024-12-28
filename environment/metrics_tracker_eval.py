from collections import defaultdict
from typing import Any
from all_types_and_consts import ActionReturn, SelectedAction
from environment.action_space import ActionName
from wandb.sdk.wandb_run import Run

from player import Player


class MetricsTrackerEval:
    def __init__(self, wandb_run: Run, player: Player = None):
        self.stats = defaultdict(int)
        self.wandb_run: Run = wandb_run
        self.player: Player = player

    def add_step_metrics(
        self,
        selected_action: SelectedAction,
        action_result: None | dict[ActionReturn, Any],
        reward: float,
    ):
        action_name = ActionName(selected_action.path_key[1:])

        match action_name:
            case ActionName.END_TURN:
                assert action_result is not None
                battle_result = action_result[ActionReturn.BATTLE_RESULT]
                if battle_result == ActionReturn.TEAM1_WIN:
                    self.stats["team1_win"] += 1
                elif battle_result == ActionReturn.TEAM2_WIN:
                    self.stats["team2_win"] += 1
                elif battle_result == ActionReturn.TIE:
                    self.stats["tie"] += 1

    def log_episode_metrics(self, is_truncated: bool):
        self.wandb_run.log(self.stats)
        self.stats.clear()
