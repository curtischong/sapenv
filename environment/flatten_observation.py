from typing import Dict, Union
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
        observation_ranges, self.observation_space_size = (
            self.return_flatten_observation_defs(self.env.observation_space)
        )

        self.observation_normalization: dict[str, FlattenObservationDefinition] = {}
        for obs_def in observation_ranges:
            self.observation_normalization[obs_def.path_key] = obs_def

        # for each obs, I need to divide by the range (so it's normalized between 0 and 1)
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(self.observation_space_size,), dtype=np.float32
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
            path_key = root_path + "|" + key
            if type(value) is gym.spaces.Dict:
                flattened_ranges, start_idx = self.return_flatten_observation_defs(
                    value, path_key, start_idx
                )
                observation_defs.extend(flattened_ranges)
            else:
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
                print(path_key, observation_size)
                start_idx += observation_size
        return observation_defs, start_idx

    def observation(self, obs: Dict[str, Dict | np.ndarray]):
        obs_arr = np.ndarray(self.observation_space.shape, dtype=np.float32)
        obs_size = self._recursively_flatten_obs(obs, obs_arr)
        assert (
            obs_size == self.observation_space_size
        ), "The defined observation size does not match the observation size the environment produces"
        return obs_arr

    def _recursively_flatten_obs(
        self,
        obs: Dict[str, Dict | np.ndarray],
        obs_arr: np.ndarray,
        root_path: str = "",
    ):
        obs_size = 0
        for key, value in obs.items():
            path_key = root_path + "|" + key
            if type(value) is dict:
                obs_size += self._recursively_flatten_obs(
                    value, obs_arr, root_path=path_key
                )
            else:
                observation_def = self.observation_normalization[path_key]
                start_idx = observation_def.start_idx
                end_idx = observation_def.start_idx + observation_def.size
                flattened_value = value.flatten()
                obs_arr[start_idx:end_idx] = (
                    flattened_value + observation_def.normalization_shift
                ) / observation_def.normalization_amount
                assert np.all(obs_arr[start_idx:end_idx] != np.nan)
                obs_size += end_idx - start_idx
        return obs_size
