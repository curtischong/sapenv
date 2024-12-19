import gymnasium as gym
from gymnasium import spaces
import numpy as np

class CustomEnv(gym.Env):
    def __init__(self):
        super(CustomEnv, self).__init__()
        # Define action and observation space
        # Example: Discrete action space with 2 actions
        self.action_space = spaces.Discrete(2)

        # Example: Continuous observation space with shape (3,)
        self.observation_space = spaces.Box(low=0, high=1, shape=(3,), dtype=np.float32)

        # Environment-specific variables
        self.state = None
        self.done = False