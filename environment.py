import gymnasium as gym
from gymnasium import spaces
import numpy as np
from all_types_and_consts import (
    MAX_ATTACK,
    MAX_HEALTH,
    MAX_PET_EXPERIENCE,
    MAX_PET_LEVEL,
    MAX_TEAM_SIZE,
    MIN_ATTACK,
    MIN_HEALTH,
    MIN_PET_EXPERIENCE,
    MIN_PET_LEVEL,
    Species,
)


class SuperAutoPetsEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        # Maximum IDs and attribute ranges (example values)
        max_food_id = 20
        max_shop_slots = 6
        max_shop_linked_slots = MAX_TEAM_SIZE  # you can promote as most this many pets
        max_total_shop_slots = max_shop_linked_slots + max_shop_slots

        max_species_id = len(Species) - 1  # -1 since high is inclusive

        # Team: up to 5 animals
        # Represented as a dictionary of parallel arrays for clarity.
        # Each animal: ID, Attack, Health, Level
        team_space = spaces.Dict(
            {
                "species": spaces.Box(
                    low=0,
                    high=max_species_id,
                    shape=(MAX_TEAM_SIZE,),
                    dtype=np.int32,
                ),
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
                "species": spaces.Box(
                    low=0,
                    high=max_species_id,
                    shape=(max_total_shop_slots,),
                    dtype=np.int32,
                ),
                "attacks": spaces.Box(
                    low=MIN_ATTACK,
                    high=MAX_ATTACK,
                    shape=(max_total_shop_slots,),
                    dtype=np.int32,
                ),
                "healths": spaces.Box(
                    low=MIN_HEALTH,
                    high=MAX_HEALTH,
                    shape=(max_total_shop_slots,),
                    dtype=np.int32,
                ),
            }
        )

        # Shop foods: up to 2 foods, each identified by an ID
        shop_foods_space = spaces.Box(
            low=0, high=max_food_id, shape=(2,), dtype=np.int32
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
        # Initialize a starting observation; for example:
        observation = {
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
