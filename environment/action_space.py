from gymnasium import spaces

from all_types_and_consts import MAX_SHOP_LINKED_SLOTS, MAX_SHOP_SLOTS, MAX_TEAM_SIZE
from player import Player

# moves the pet from start_idx to end_idx
reorder_team_space = spaces.MultiBinary([MAX_TEAM_SIZE, MAX_TEAM_SIZE])

combine_pets_space = spaces.MultiBinary([MAX_TEAM_SIZE, MAX_TEAM_SIZE])

buy_pet_space = spaces.MultiBinary([MAX_SHOP_SLOTS, MAX_TEAM_SIZE])

buy_linked_pet_space = spaces.MultiBinary([MAX_SHOP_LINKED_SLOTS, 2, MAX_TEAM_SIZE])
sell_pet_space = spaces.MultiBinary(MAX_TEAM_SIZE)  # index of pet you're selling

roll_shop_space = spaces.MultiBinary(1)
toggle_freeze_slot_space = spaces.MultiBinary(MAX_SHOP_SLOTS)
freeze_pet_at_linked_slot_space = spaces.MultiBinary(MAX_SHOP_LINKED_SLOTS)
end_turn_space = spaces.MultiBinary(1)

env_action_space = spaces.Dict(
    {
        "reorder_team": reorder_team_space,
        "combine_pets": combine_pets_space,
        "buy_pet": buy_pet_space,
        "buy_linked_pet": buy_linked_pet_space,
        "sell_pet": sell_pet_space,
        "roll_shop": roll_shop_space,
        "toggle_freeze_slot": toggle_freeze_slot_space,
        "freeze_pet_at_linked_slot": freeze_pet_at_linked_slot_space,
        "end_turn": end_turn_space,
    }
)


def get_action_masks(player: Player):
    return {
        "reorder_team": player.reorder_team_action_mask(),
        "combine_pets": player.combine_pets_action_mask(),
        "buy_pet": player.buy_pet_action_mask(),
        "buy_linked_pet": player.buy_linked_pet_action_mask(),
        "sell_pet": player.sell_pet_action_mask(),
        "roll_shop": player.roll_shop_action_mask(),
        "toggle_freeze_slot": player.toggle_freeze_slot_action_mask(),
        "freeze_pet_at_linked_slot": player.freeze_pet_at_linked_slot_action_mask(),
        "end_turn": player.end_turn_action_mask(),
    }
