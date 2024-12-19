import numpy as np

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


# Define the observation spaces
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

shop_animals_space = spaces.Dict(
    {
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

shop_num_foods_space = spaces.Box(
    low=0,
    high=MAX_SHOP_FOOD_SLOTS,
    shape=(len(Foods),),
    dtype=np.int32,
)

env_observation_space = spaces.Dict(
    {
        "team": team_space,
        "shop_animals": shop_animals_space,
        "shop_linked_animals_space": shop_linked_animals_space,
        "shop_num_foods": shop_num_foods_space,
    }
)


def get_initial_observation():
    # init all None pets
    species_arr = np.zeros((MAX_TEAM_SIZE,), dtype=np.int32)
    # Assuming we want the 'NONE' species to fill all team slots:
    species_none_value = Species.NONE.value
    species_arr.fill(species_none_value)

    return {
        "team": {
            "species": species_arr,
            "attacks": np.zeros((MAX_TEAM_SIZE,), dtype=np.int32),
            "healths": np.zeros((MAX_TEAM_SIZE,), dtype=np.int32),
            "levels": np.ones((MAX_TEAM_SIZE,), dtype=np.int32),
            "experiences": np.zeros((MAX_TEAM_SIZE,), dtype=np.int32),
        },
        "shop_animals": {
            "species": np.zeros((MAX_SHOP_SLOTS,), dtype=np.int32),
            "attacks": np.zeros((MAX_SHOP_SLOTS,), dtype=np.int32),
            "healths": np.zeros((MAX_SHOP_SLOTS,), dtype=np.int32),
        },
        "shop_linked_animals_space": {
            "species1": np.zeros((MAX_SHOP_LINKED_SLOTS,), dtype=np.int32),
            "species2": np.zeros((MAX_SHOP_LINKED_SLOTS,), dtype=np.int32),
            "attacks": np.zeros((MAX_SHOP_LINKED_SLOTS,), dtype=np.int32),
            "healths": np.zeros((MAX_SHOP_LINKED_SLOTS,), dtype=np.int32),
        },
        "shop_num_foods": np.zeros((len(Foods),), dtype=np.int32),
    }
