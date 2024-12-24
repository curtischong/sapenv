from enum import Enum, auto
from gymnasium import spaces

from all_types_and_consts import MAX_SHOP_LINKED_SLOTS, MAX_SHOP_SLOTS, MAX_TEAM_SIZE
from player import Player

# moves the pet from start_idx to end_idx
reorder_team_space = spaces.MultiBinary([MAX_TEAM_SIZE, MAX_TEAM_SIZE])  # 25

combine_pets_space = spaces.MultiBinary([MAX_TEAM_SIZE, MAX_TEAM_SIZE])  # 25

buy_pet_space = spaces.MultiBinary([MAX_SHOP_SLOTS, MAX_TEAM_SIZE])  # 35

buy_linked_pet_space = spaces.MultiBinary(
    [MAX_SHOP_LINKED_SLOTS, 2, MAX_TEAM_SIZE]
)  # 50
sell_pet_space = spaces.MultiBinary(MAX_TEAM_SIZE)  # index of pet you're selling # 5

roll_shop_space = spaces.MultiBinary(1)  # 1
toggle_freeze_slot_space = spaces.MultiBinary(MAX_SHOP_SLOTS)  # 7
freeze_pet_at_linked_slot_space = spaces.MultiBinary(MAX_SHOP_LINKED_SLOTS)  # 5
end_turn_space = spaces.MultiBinary(1)  # 1


class ActionName(Enum):
    REORDER_TEAM = auto()
    COMBINE_PETS = auto()
    BUY_PET = auto()
    BUY_LINKED_PET = auto()
    SELL_PET = auto()
    ROLL_SHOP = auto()
    TOGGLE_FREEZE_SLOT = auto()
    FREEZE_PET_AT_LINKED_SLOT = auto()
    END_TURN = auto()


env_action_space = spaces.Dict(
    {
        ActionName.REORDER_TEAM: reorder_team_space,
        ActionName.COMBINE_PETS: combine_pets_space,
        ActionName.BUY_PET: buy_pet_space,
        ActionName.BUY_LINKED_PET: buy_linked_pet_space,
        ActionName.SELL_PET: sell_pet_space,
        ActionName.ROLL_SHOP: roll_shop_space,
        ActionName.TOGGLE_FREEZE_SLOT: toggle_freeze_slot_space,
        ActionName.FREEZE_PET_AT_LINKED_SLOT: freeze_pet_at_linked_slot_space,
        ActionName.END_TURN: end_turn_space,
    }
)


def get_action_masks(player: Player):
    return {
        ActionName.REORDER_TEAM: player.reorder_team_action_mask(),
        ActionName.COMBINE_PETS: player.combine_pets_action_mask(),
        ActionName.BUY_PET: player.buy_pet_action_mask(),
        ActionName.BUY_LINKED_PET: player.buy_linked_pet_action_mask(),
        ActionName.SELL_PET: player.sell_pet_action_mask(),
        ActionName.ROLL_SHOP: player.roll_shop_action_mask(),
        ActionName.TOGGLE_FREEZE_SLOT: player.toggle_freeze_slot_action_mask(),
        ActionName.FREEZE_PET_AT_LINKED_SLOT: player.freeze_pet_at_linked_slot_action_mask(),
        ActionName.END_TURN: player.end_turn_action_mask(),
    }
