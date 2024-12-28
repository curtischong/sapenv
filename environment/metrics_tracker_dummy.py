from collections import defaultdict
from typing import Any
from all_types_and_consts import ActionReturn, BattleResult, SelectedAction
from environment.action_space import ActionName
from wandb.sdk.wandb_run import Run

from player import Player


class MetricsTrackerDummy:
    def __init__(self):
        self.stats = defaultdict(int)

    def add_step_metrics(
        self,
        selected_action: SelectedAction,
        action_result: None | dict[ActionReturn, Any],
        reward: float,
    ):
        pass

    def log_episode_metrics(self, is_truncated: bool, player: Player = None):
        pass
