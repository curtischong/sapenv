from gymnasium import spaces

from all_types_and_consts import MAX_SHOP_LINKED_SLOTS, MAX_SHOP_SLOTS, MAX_TEAM_SIZE

reorder_team_space = spaces.Dict(
    {
        "start_idx": spaces.MultiBinary(MAX_TEAM_SIZE),
        "end_idx": spaces.MultiBinary(MAX_TEAM_SIZE),
    }
)

combine_pets_space = spaces.Dict(
    {
        "pet1_idx": spaces.MultiBinary(MAX_TEAM_SIZE),
        "pet2_idx": spaces.MultiBinary(MAX_TEAM_SIZE),
    }
)

buy_pet_space = spaces.Dict(
    {
        "slot_idx": spaces.MultiBinary(MAX_SHOP_SLOTS),
        "target_team_idx": spaces.MultiBinary(MAX_TEAM_SIZE),
    }
)

buy_linked_pet_space = spaces.Dict(
    {
        "linked_slot_idx": spaces.MultiBinary(MAX_SHOP_LINKED_SLOTS),
        "is_pet1_bought": spaces.MultiBinary(2),
        "target_team_idx": spaces.MultiBinary(MAX_TEAM_SIZE),
    }
)
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
        "buy_linked_pet": buy_pet_space,
        "sell_pet": sell_pet_space,
        "roll_shop": roll_shop_space,
        "toggle_freeze_slot": toggle_freeze_slot_space,
        "freeze_pet_at_linked_slot": freeze_pet_at_linked_slot_space,
        "end_turn": end_turn_space,
    }
)
