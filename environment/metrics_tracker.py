from collections import defaultdict
from all_types_and_consts import BattleResult, GameResult, SelectedAction
from environment.action_space import ActionName


class MetricsTracker:
    def __init__(self):
        self.pets_bought = defaultdict(int)

    def add_step_metrics(
        self,
        selected_action: SelectedAction,
        action_result: None | tuple[GameResult, BattleResult],
    ):
        action_name = ActionName(selected_action.path_key[1:])

        match action_name:
            case ActionName.BUY_PET:
                slot_idx = selected_action.params[0]
                pet = 
                self.pets_bought[selected_action.params[0]] += 1
