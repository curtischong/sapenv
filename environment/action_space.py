from dataclasses import dataclass
from enum import Enum
from typing import Callable
from gymnasium import spaces
import numpy as np

from all_types_and_consts import (
    MAX_SHOP_LINKED_SLOTS,
    MAX_SHOP_SLOTS,
    MAX_TEAM_SIZE,
    ActionResult,
    foods_that_apply_globally,
    foods_for_pet,
    MAX_SHOP_FOOD_SLOTS,
)
from player import Player

# moves the pet from start_idx to end_idx
reorder_team_space = spaces.MultiBinary([MAX_TEAM_SIZE, MAX_TEAM_SIZE])  # 25

combine_pets_space = spaces.MultiBinary([MAX_TEAM_SIZE, MAX_TEAM_SIZE])  # 25

buy_pet_space = spaces.MultiBinary([MAX_SHOP_SLOTS, MAX_TEAM_SIZE])  # 35

buy_linked_pet_space = spaces.MultiBinary(
    [MAX_SHOP_LINKED_SLOTS, 2, MAX_TEAM_SIZE]
)  # 50

buy_food_space = spaces.MultiBinary([MAX_SHOP_FOOD_SLOTS])
buy_food_for_pet_space = spaces.MultiBinary([MAX_SHOP_FOOD_SLOTS, MAX_TEAM_SIZE])

sell_pet_space = spaces.MultiBinary(MAX_TEAM_SIZE)  # index of pet you're selling # 5

roll_shop_space = spaces.MultiBinary(1)  # 1
toggle_freeze_slot_space = spaces.MultiBinary(MAX_SHOP_SLOTS)  # 7
freeze_pet_at_linked_slot_space = spaces.MultiBinary([MAX_SHOP_LINKED_SLOTS, 2])  # 10
toggle_freeze_food_slot_space = spaces.MultiBinary(MAX_SHOP_FOOD_SLOTS)
end_turn_space = spaces.MultiBinary(1)  # 1


class ActionName(Enum):
    REORDER_TEAM = "reorder_team"
    COMBINE_PETS = "combine_pets"
    BUY_PET = "buy_pet"
    BUY_LINKED_PET = "buy_linked_pet"
    BUY_FOOD = "buy_food"
    BUY_FOOD_FOR_PET = "buy_food_for_pet"
    SELL_PET = "sell_pet"
    ROLL_SHOP = "roll_shop"
    TOGGLE_FREEZE_SLOT = "toggle_freeze_slot"
    FREEZE_PET_AT_LINKED_SLOT = "freeze_pet_at_linked_slot"
    TOGGLE_FREEZE_FOOD_SLOT = "toggle_freeze_food_slot"
    END_TURN = "end_turn"


@dataclass
class Action:
    space: spaces.Space
    get_mask: Callable[[Player], np.ndarray]
    perform_action: Callable[[Player, tuple[int, ...]], ActionResult]


actions_dict: dict[ActionName, Action] = {
    ActionName.REORDER_TEAM: Action(
        space=reorder_team_space,
        get_mask=lambda player: player.reorder_team_action_mask(),
        perform_action=lambda player, params: player.reorder_team_action(*params),
    ),
    ActionName.COMBINE_PETS: Action(
        space=combine_pets_space,
        get_mask=lambda player: player.combine_pets_action_mask(),
        perform_action=lambda player, params: player.combine_pets_action(*params),
    ),
    ActionName.BUY_PET: Action(
        space=buy_pet_space,
        get_mask=lambda player: player.buy_pet_action_mask(),
        perform_action=lambda player, params: player.buy_pet_action(*params),
    ),
    ActionName.BUY_LINKED_PET: Action(
        space=buy_linked_pet_space,
        get_mask=lambda player: player.buy_linked_pet_action_mask(),
        perform_action=lambda player, params: player.buy_linked_pet_action(*params),
    ),
    ActionName.BUY_FOOD: Action(
        space=buy_food_space,
        get_mask=lambda player: player.buy_food_action_mask(),
        perform_action=lambda player, params: player.buy_food_action(*params),
    ),
    ActionName.BUY_FOOD_FOR_PET: Action(
        space=buy_food_for_pet_space,
        get_mask=lambda player: player.buy_food_for_pet_action_mask(),
        perform_action=lambda player, params: player.buy_food_for_pet_action(*params),
    ),
    ActionName.SELL_PET: Action(
        space=sell_pet_space,
        get_mask=lambda player: player.sell_pet_action_mask(),
        perform_action=lambda player, params: player.sell_pet_action(*params),
    ),
    ActionName.ROLL_SHOP: Action(
        space=roll_shop_space,
        get_mask=lambda player: player.roll_shop_action_mask(),
        perform_action=lambda player, params: player.roll_shop_action(*params),
    ),
    ActionName.TOGGLE_FREEZE_SLOT: Action(
        space=toggle_freeze_slot_space,
        get_mask=lambda player: player.toggle_freeze_slot_action_mask(),
        perform_action=lambda player, params: player.toggle_freeze_slot_action(*params),
    ),
    ActionName.FREEZE_PET_AT_LINKED_SLOT: Action(
        space=freeze_pet_at_linked_slot_space,
        get_mask=lambda player: player.freeze_pet_at_linked_slot_action_mask(),
        perform_action=lambda player, params: player.freeze_pet_at_linked_slot_action(
            *params
        ),
    ),
    ActionName.TOGGLE_FREEZE_FOOD_SLOT: Action(
        space=toggle_freeze_food_slot_space,
        get_mask=lambda player: player.toggle_freeze_food_slot_action_mask(),
        perform_action=lambda player, params: player.toggle_freeze_food_slot_action(
            *params
        ),
    ),
    ActionName.END_TURN: Action(
        space=end_turn_space,
        get_mask=lambda player: player.end_turn_action_mask(),
        perform_action=lambda player, params: player.end_turn_action(*params),
    ),
}


env_action_space = spaces.Dict(
    {action_name.value: action.space for action_name, action in actions_dict.items()}
)


def get_action_masks(player: Player) -> dict[ActionName, np.ndarray]:
    return {
        action_name.value: action.get_mask(player)
        for action_name, action in actions_dict.items()
    }
