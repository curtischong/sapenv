from gymnasium import spaces

from all_types_and_consts import MAX_SHOP_LINKED_SLOTS, MAX_SHOP_SLOTS, MAX_TEAM_SIZE

reorder_space = spaces.Dict(
    {
        "start_idx": spaces.MultiBinary(MAX_TEAM_SIZE),
        "end_idx": spaces.MultiBinary(MAX_TEAM_SIZE),
    }
)
sell_space = spaces.MultiBinary(MAX_TEAM_SIZE)  # index of pet you're selling

buy_space = spaces.Dict(
    {
        "start_idx": spaces.MultiBinary(MAX_SHOP_LINKED_SLOTS + MAX_SHOP_SLOTS),
        "end_idx": spaces.MultiBinary(MAX_TEAM_SIZE),
    }
)

env_action_space = spaces.Dict(
    {
        "action_type": spaces.Discrete(6),
        # "target_1": spaces.Discrete(self.shop_size),  # 0-6
        # "target_2": spaces.Discrete(self.shop_size),  # 0-6
    }
)
