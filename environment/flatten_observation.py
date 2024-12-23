from typing import Union
import gymnasium as gym
import numpy as np

# https://gist.github.com/colllin/1172e042edf267d5ec667fa9802673cf
from dataclasses import dataclass


@dataclass
class FlattenObservationDefinition:
    path_key: str  # path to the observation (in the dictionary)
    normalization_shift: float = 0.0  # if an observation point ranges from 1 to 5, we need to shift it to 0 to 4 first then normalize to [0, 1]
    normalization_amount: float = 1.0
    start_idx: int = 0
    size: int = 0


class FlattenObservation(gym.ObservationWrapper):
    """Action wrapper that flattens the action."""

    def __init__(self, env):
        super(FlattenObservation, self).__init__(env)
        self.observation_ranges, observation_space_size = (
            self.return_flatten_observation_defs(self.env.observation_space)
        )

        # for each obs, I need to divide by the range (so it's normalized between 0 and 1)
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(observation_space_size,), dtype=np.float32
        )

    # we need 2 functions: one to flatten the env into a box env to define the gym environment
    # and one to flatten dictionaries of the box env
    def return_flatten_observation_defs(
        self,
        observation_dict: dict[str, Union[dict | gym.spaces.MultiBinary]],
        root_path: str = "",
        start_idx=0,
    ) -> tuple[list[FlattenObservationDefinition], int]:
        observation_defs = []  # list of tuple: (action_name, start_idx, end_idx])
        for key, value in observation_dict.items():
            if type(value) is gym.spaces.Dict:
                flattened_ranges, start_idx = self.return_flatten_observation_defs(
                    value, root_path + "_" + key, start_idx
                )
                observation_defs.extend(flattened_ranges)
            else:
                path_key = root_path + "_" + key
                observation_size = np.sum(value.shape)
                if type(value) is gym.spaces.MultiBinary:
                    observation_defs.append(
                        FlattenObservationDefinition(
                            path_key=path_key,
                            normalization_shift=0,
                            normalization_amount=1.0,
                            start_idx=start_idx,
                            size=observation_size,
                        )
                    )
                elif type(value) is gym.spaces.Box:
                    # TODO: handle if it's binary or box
                    observation_defs.append(
                        FlattenObservationDefinition(
                            path_key=path_key,
                            normalization_shift=-value.low[0],
                            normalization_amount=value.high[0] + 1 - value.low[0],
                            start_idx=start_idx,
                            size=observation_size,
                        )
                    )
                else:
                    raise ValueError(f"Unknown type {type(value)}")
                start_idx += observation_size
        return observation_defs, start_idx

    def action(self, action):
        return gym.spaces.unflatten(self.env.action_space, action)

    def reverse_action(self, action):
        return gym.spaces.flatten(self.env.action_space, action)
