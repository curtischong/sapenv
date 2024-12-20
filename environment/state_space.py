from all_types_and_consts import (
    MAX_ATTACK,
    MAX_HEALTH,
    MAX_PET_EXPERIENCE,
    MAX_SHOP_FOOD_SLOTS,
    MAX_SHOP_LINKED_SLOTS,
    MAX_SHOP_SLOTS,
    MAX_TEAM_SIZE,
    MIN_ATTACK,
    MIN_HEALTH,
    MIN_PET_EXPERIENCE,
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
            low=1,
            high=3,
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
        "is_frozen": spaces.MultiBinary(MAX_SHOP_LINKED_SLOTS),
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
    species_arr = np.zeros(len(Species) * MAX_TEAM_SIZE, dtype=np.int32)
    for ith_pet in range(MAX_TEAM_SIZE):
        species_arr[ith_pet * MAX_TEAM_SIZE + Species.NONE.value] = 1

    # TODO: we should also store turn number, the shop tier, any extra "permanent stat increases" the shop has
    return {
        "team": {
            "species": species_arr,
            "attacks": np.zeros((MAX_TEAM_SIZE,), dtype=np.int32),
            "healths": np.zeros((MAX_TEAM_SIZE,), dtype=np.int32),
            "levels": np.ones((MAX_TEAM_SIZE,), dtype=np.int32),
            "experiences": np.zeros((MAX_TEAM_SIZE,), dtype=np.int32),
        },
        # todo: init shop
        "shop_animals": {
            "species": np.zeros((3,), dtype=np.int32),
            "attacks": np.zeros((3,), dtype=np.int32),
            "healths": np.zeros((3,), dtype=np.int32),
            "is_frozen": np.zeros((3,), dtype=np.bool),
        },
        "shop_linked_animals_space": {
            "species1": np.zeros((len(Species), MAX_SHOP_LINKED_SLOTS), dtype=np.int32),
            "species2": np.zeros((len(Species), MAX_SHOP_LINKED_SLOTS), dtype=np.int32),
            "attacks": np.zeros((MAX_SHOP_LINKED_SLOTS,), dtype=np.int32),
            "healths": np.zeros((MAX_SHOP_LINKED_SLOTS,), dtype=np.int32),
            "is_frozen": np.zeros((MAX_SHOP_LINKED_SLOTS,), dtype=np.bool),
        },
        "shop_num_foods": np.zeros(
            (2,), dtype=np.int32
        ),  # todo: this is wrong. we need to init, but one hot encode
    }
