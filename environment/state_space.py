from all_types_and_consts import (
    MAX_ATTACK,
    MAX_GAMES_LENGTH,
    MAX_HEALTH,
    MAX_PET_EXPERIENCE,
    MAX_PET_LEVEL,
    MAX_SHOP_FOOD_SLOTS,
    MAX_SHOP_LINKED_SLOTS,
    MAX_SHOP_SLOTS,
    MAX_TEAM_SIZE,
    MIN_ATTACK,
    MIN_HEALTH,
    MIN_PET_EXPERIENCE,
    MIN_PET_LEVEL,
    NUM_WINS_TO_WIN,
    STARTING_HEARTS,
    Species,
    MAX_GOLD,
    Foods,
)
from gymnasium import spaces
import numpy as np

from player import Player

# Team: up to 5 animals
# Represented as a dictionary of parallel arrays for clarity.
# Each animal: ID, Attack, Health, Level
team_space = spaces.Dict(
    {
        #     species_space = spaces.Discrete(len(Species))  # Each species is represented by an integer
        # team_space = spaces.Tuple([species_space] * MAX_TEAM_SIZE)
        "species": spaces.MultiDiscrete([len(Species)] * MAX_TEAM_SIZE),
        "attacks": spaces.Box(
            low=MIN_ATTACK,
            high=MAX_ATTACK,
            shape=(MAX_TEAM_SIZE,),
            dtype=np.int32,
        ),
        "healths": spaces.Box(
            low=MIN_HEALTH,
            high=MAX_HEALTH,
            shape=(MAX_TEAM_SIZE,),
            dtype=np.int32,
        ),
        "levels": spaces.Box(
            low=MIN_PET_LEVEL,
            high=MAX_PET_LEVEL,
            shape=(MAX_TEAM_SIZE,),
            dtype=np.int32,
        ),
        "experiences": spaces.Box(
            low=MIN_PET_EXPERIENCE,
            high=MAX_PET_EXPERIENCE,
            shape=(MAX_TEAM_SIZE,),
            dtype=np.int32,
        ),
    }
)

# Each: ID, Attack, Health, Tier
shop_animals_space = spaces.Dict(
    {
        # Create a space for each shop slot
        "species": spaces.MultiDiscrete([len(Species)] * MAX_SHOP_SLOTS),
        "attacks": spaces.Box(
            low=MIN_ATTACK,
            high=MAX_ATTACK,
            shape=(MAX_SHOP_SLOTS,),
            dtype=np.int32,
        ),
        "healths": spaces.Box(
            low=MIN_HEALTH,
            high=MAX_HEALTH,
            shape=(MAX_SHOP_SLOTS,),
            dtype=np.int32,
        ),
        "is_frozen": spaces.MultiBinary(MAX_SHOP_SLOTS),
    }
)
shop_linked_animals_space = spaces.Dict(
    {
        # Create a space for each shop slot
        "species1": spaces.MultiDiscrete([len(Species)] * MAX_SHOP_LINKED_SLOTS),
        "species2": spaces.MultiDiscrete([len(Species)] * MAX_SHOP_LINKED_SLOTS),
        "attacks1": spaces.Box(
            low=MIN_ATTACK,
            high=MAX_ATTACK,
            shape=(MAX_SHOP_LINKED_SLOTS,),
            dtype=np.int32,
        ),
        "attacks2": spaces.Box(
            low=MIN_ATTACK,
            high=MAX_ATTACK,
            shape=(MAX_SHOP_LINKED_SLOTS,),
            dtype=np.int32,
        ),
        "healths1": spaces.Box(
            low=MIN_HEALTH,
            high=MAX_HEALTH,
            shape=(MAX_SHOP_LINKED_SLOTS,),
            dtype=np.int32,
        ),
        "healths2": spaces.Box(
            low=MIN_HEALTH,
            high=MAX_HEALTH,
            shape=(MAX_SHOP_LINKED_SLOTS,),
            dtype=np.int32,
        ),
    }
)

# since the shop foods are ALWAYS the same. we can represent it like this:
# For each food type, specify the number of that kind we can buy
shop_num_foods_space = spaces.Box(
    low=0,
    high=MAX_SHOP_FOOD_SLOTS,
    shape=(len(Foods),),
    dtype=np.int32,
)

shop_gold_space = spaces.Box(low=0, high=MAX_GOLD, shape=(1,), dtype=np.int32)
turn_number_space = spaces.Box(low=0, high=MAX_GAMES_LENGTH, shape=(1,), dtype=np.int32)
num_wins_space = spaces.Box(low=0, high=NUM_WINS_TO_WIN, shape=(1,), dtype=np.int32)

# TODO: On the very last round, the player can have 0 hearts. To avoid potential problems, I set it to low=0. not low=1
num_hearts_space = spaces.Box(low=0, high=STARTING_HEARTS, shape=(1,), dtype=np.int32)

env_observation_space = spaces.Dict(
    {
        "team": team_space,
        "shop_animals": shop_animals_space,
        "shop_linked_animals_space": shop_linked_animals_space,
        "shop_gold": shop_gold_space,
        "turn_number": turn_number_space,
        "num_wins": num_wins_space,
        "num_hearts": num_hearts_space,
        # "shop_num_foods": shop_num_foods_space,
    }
)


def get_observation(player: Player):
    # TODO: we should also any extra "permanent stat increases" the shop has, or temporary buffs pets have
    return {
        "team": player.team.get_observation()
        | player.shop.get_observation()
        | {
            "shop_gold": np.array([player.shop.gold], dtype=np.int32),
            "turn_number": np.array([player.turn_number], dtype=np.int32),
            "num_wins": np.array([player.num_wins], dtype=np.int32),
            "num_hearts": np.array([player.hearts], dtype=np.int32),
        }
    }
