import gymnasium as gym
from environment.state_space import (
    env_observation_space,
    get_observation,
)
from environment.action_space import env_action_space
from player import Player


class SuperAutoPetsEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        self.observation_space = env_observation_space
        self.action_space = env_action_space
        # self.player = Player.init_starting_player()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.player = Player.init_starting_player()
        return get_observation(self.player), {}

    def step(self, action):
        # Implement your logic for applying the action and transitioning to the next state
        observation = get_observation(self.player)  # Implement this method
        reward = 0.0
        done = False
        info = {}
        return observation, reward, done, info

    def render(self):
        # Render environment for human viewing
        pass
