from all_types_and_consts import (
    MAX_ATTACK,
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
    Foods,
    Species,
)
from gymnasium import spaces
import numpy as np

# Team: up to 5 animals
# Represented as a dictionary of parallel arrays for clarity.
# Each animal: ID, Attack, Health, Level
team_space = spaces.Dict(
    {
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
    }
)
shop_linked_animals_space = spaces.Dict(
    {
        # Create a space for each shop slot
        "species1": spaces.MultiDiscrete([len(Species)] * MAX_SHOP_LINKED_SLOTS),
        "species2": spaces.MultiDiscrete([len(Species)] * MAX_SHOP_LINKED_SLOTS),
        "attacks": spaces.Box(
            low=MIN_ATTACK,
            high=MAX_ATTACK,
            shape=(MAX_SHOP_LINKED_SLOTS,),
            dtype=np.int32,
        ),
        "healths": spaces.Box(
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
