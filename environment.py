import gymnasium as gym
from gymnasium import spaces
import numpy as np
from all_types_and_consts import (
    MAX_ATTACK,
    MAX_HEALTH,
    MAX_PET_EXPERIENCE,
    MAX_PET_LEVEL,
    MAX_SHOP_FOOD_SLOTS,
    MAX_TEAM_SIZE,
    MAX_TOTAL_SHOP_SLOTS,
    MIN_ATTACK,
    MIN_HEALTH,
    MIN_PET_EXPERIENCE,
    MIN_PET_LEVEL,
    FoodKind,
    Species,
)


class SuperAutoPetsEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        # Maximum IDs and attribute ranges (example values)

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
                "species": spaces.MultiDiscrete([len(Species)] * MAX_TOTAL_SHOP_SLOTS),
                "attacks": spaces.Box(
                    low=MIN_ATTACK,
                    high=MAX_ATTACK,
                    shape=(MAX_TOTAL_SHOP_SLOTS,),
                    dtype=np.int32,
                ),
                "healths": spaces.Box(
                    low=MIN_HEALTH,
                    high=MAX_HEALTH,
                    shape=(MAX_TOTAL_SHOP_SLOTS,),
                    dtype=np.int32,
                ),
            }
        )

        # Shop foods: up to 2 foods, each identified by an ID
        shop_foods_space = (
            spaces.MultiDiscrete([len(FoodKind)] * MAX_SHOP_FOOD_SLOTS),
        )

        # Combine into a single observation space
        self.observation_space = spaces.Dict(
            {
                "team": team_space,
                "shop_animals": shop_animals_space,
                "shop_foods": shop_foods_space,
            }
        )

        # Define action space as needed for your gameplay logic.
        # For example, if actions correspond to indices in the shop or team:
        # self.action_space = spaces.Discrete(...)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        # Initialize a starting observation

        # init all None pets
        species_arr = np.zeros(len(Species) * MAX_TEAM_SIZE, dtype=np.int32)
        for ith_pet in range(MAX_TEAM_SIZE):
            species_arr[ith_pet * MAX_TEAM_SIZE + Species.NONE.value] = 1

        observation = {
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
            },
            "shop_foods": np.zeros(
                (2,), dtype=np.int32
            ),  # todo: this is wrong. we need to init, but one hot encode
        }
        # Return observation and possibly some additional info
        return observation, {}

    def step(self, action):
        # Implement your logic for applying the action and transitioning to the next state
        observation = self._get_observation()  # Implement this method
        reward = 0.0
        done = False
        info = {}
        return observation, reward, done, info

    def _get_observation(self):
        # Return a valid observation dictionary
        # Typically you'd return the current state of the team and shop
        return {
            "team": {
                "ids": np.zeros((5,), dtype=np.int32),
                "attacks": np.zeros((5,), dtype=np.int32),
                "healths": np.zeros((5,), dtype=np.int32),
                "levels": np.ones((5,), dtype=np.int32),
            },
            "shop_animals": {
                "ids": np.zeros((3,), dtype=np.int32),
                "attacks": np.zeros((3,), dtype=np.int32),
                "healths": np.zeros((3,), dtype=np.int32),
                "tiers": np.ones((3,), dtype=np.int32),
            },
            "shop_foods": np.zeros((2,), dtype=np.int32),
        }

    def render(self):
        # Render environment for human viewing
        pass
