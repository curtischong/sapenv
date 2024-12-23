from typing import Union
import gymnasium as gym
import numpy as np

# https://gist.github.com/colllin/1172e042edf267d5ec667fa9802673cf
from dataclasses import dataclass


@dataclass
class FlattenObservationData:
    normalization_shift: float = 0.0  # if an observation point ranges from 1 to 5, we need to shift it to 0 to 4 first then normalize to [0, 1]
    normalization_amount: float = 1.0
    start_idx: int = 0
    size: int = 0


class FlattenObservation(gym.ObservationWrapper):
    """Action wrapper that flattens the action."""

    def __init__(self, env):
        super(FlattenObservation, self).__init__(env)
        # self.action_space = gym.spaces.flatten_space(self.env.action_space)
        self.action_ranges, num_actions = self.return_flatten_observation_data(
            self.env.action_space
        )

        # for each obs, I need to divide by the range (so it's normalized between 0 and 1)
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=self.env.observation_space.shape, dtype=np.float32
        )

    # we need 2 functions: one to flatten the env into a box env to define the gym environment
    # and one to flatten dictionaries of the box env
    def return_flatten_observation_data(
        self,
        observation_dict: dict[str, Union[dict | gym.spaces.MultiBinary]],
        start_idx=0,
    ) -> tuple[list[tuple[FlattenObservationData]], int]:
        actions_ranges = []  # list of tuple: (action_name, start_idx, end_idx])
        for key, value in observation_dict.items():
            if type(value) is gym.spaces.Dict:
                flattened_ranges, start_idx = self.return_flatten_observation_data(
                    value, start_idx
                )
                actions_ranges.extend(flattened_ranges)
            else:
                action_space = value
                actions_ranges.append((key, start_idx, start_idx + action_space.n))
                start_idx += action_space.n
        return actions_ranges, start_idx

    def action(self, action):
        return gym.spaces.unflatten(self.env.action_space, action)

    def reverse_action(self, action):
        return gym.spaces.flatten(self.env.action_space, action)
