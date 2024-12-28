from collections import defaultdict
from typing import Any
from all_types_and_consts import ActionReturn, SelectedAction
from environment.action_space import ActionName
from wandb.sdk.wandb_run import Run

from player import Player


class MetricsTracker:
    def __init__(self, wandb_run: Run):
        self.stats = defaultdict(int)
        self.wandb_run: Run = wandb_run

    def add_step_metrics(
        self,
        selected_action: SelectedAction,
        action_result: None | dict[ActionReturn, Any],
        reward: float,
    ):
        if self.wandb_run is None:
            # this is empty during inference
            return

        self.wandb_run.log({"reward": reward})
        self.stats["total_reward"] += reward

        action_name = ActionName(selected_action.path_key[1:])

        match action_name:
            case ActionName.BUY_PET:
                pet_species = action_result[ActionReturn.BOUGHT_PET_SPECIES]
                key = f"pets_bought/{pet_species}"
                self.stats[key] += 1
                self.stats["buy_pet"] += 1
            case ActionName.END_TURN:
                pass
            case ActionName.SELL_PET:
                pet_species = action_result[ActionReturn.SOLD_PET_SPECIES]
                key = f"pets_sold/{pet_species}"
                self.stats[key] += 1
                self.stats["sell_pet"] += 1
            case ActionName.ROLL_SHOP:
                self.stats["roll_shop"] += 1
            case ActionName.TOGGLE_FREEZE_SLOT:
                self.stats["toggle_freeze_slot"] += 1
            case ActionName.FREEZE_PET_AT_LINKED_SLOT:
                self.stats["freeze_pet_at_linked_slot"] += 1
            case ActionName.COMBINE_PETS:
                self.stats["combine_pets"] += 1
            case ActionName.REORDER_TEAM:
                self.stats["reorder_team"] += 1
            case ActionName.BUY_LINKED_PET:
                self.stats["buy_linked_pet"] += 1

    def log_episode_metrics(self, is_truncated: bool, player: Player = None):
        if is_truncated:
            self.wandb_run.log(
                self.stats
                | {
                    "is_truncated": 1,
                }
            )
        else:
            self.wandb_run.log(
                self.stats
                | {
                    "is_truncated": 0,
                    "num_wins": player.num_wins,
                    "num_hearts": player.hearts,
                }
            )
        self.stats.clear()
