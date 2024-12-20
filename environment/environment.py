import gymnasium as gym
import numpy as np
from all_types_and_consts import MAX_SHOP_LINKED_SLOTS, MAX_TEAM_SIZE, Species
from environment.state_space import env_observation_space, get_initial_observation
from environment.action_space import env_action_space
from player import Player


class SuperAutoPetsEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        # Maximum IDs and attribute ranges (example values)

        # Combine into a single observation space
        self.observation_space = env_observation_space
        self.action_space = env_action_space
        self.player = Player.init_starting_player()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        # Initialize a starting observation

        # Return observation and possibly some additional info
        return get_initial_observation(), {}

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
