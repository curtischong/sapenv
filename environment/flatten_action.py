from dataclasses import dataclass
from typing import Union
import gymnasium as gym
import numpy as np

from all_types_and_consts import SelectedAction

# https://gist.github.com/colllin/1172e042edf267d5ec667fa9802673cf


@dataclass
class FlattenActionDefinition:
    path_key: str  # path to the action (in the dictionary)
    start_idx: int
    size: int
    shape: tuple[
        int, ...
    ]  # if the action has multiple indices, this shape is important to determine WHICH INDEX the model chose to use (e.g. swap pets at index 1 and 3)


class FlattenAction(gym.ActionWrapper):
    """Action wrapper that flattens the action."""

    def __init__(self, env):
        super(FlattenAction, self).__init__(env)
        # self.action_space = gym.spaces.flatten_space(self.env.action_space)
        self.action_def_map: dict[str, FlattenActionDefinition] = {}
        num_actions = self.return_flattened_action_ranges(
            self.env.action_space, action_def_map=self.action_def_map
        )  # TODO: binary search for which bucket you're in
        print(self.action_def_map)
        self.action_space: gym.spaces.Discrete = gym.spaces.Discrete(num_actions)

    def action_masks(self) -> np.ndarray:
        # given the dictionary action mask of the environment, return a flattened version of it
        dict_action_mask = self.env.env.action_masks()
        num_actions = self.action_space.n

        mask = np.empty((num_actions,), dtype=bool)
        self.build_action_mask(
            action_mask=mask,
            action_dict=dict_action_mask,
        )

        assert not np.all(mask == 0)
        return mask

    def build_action_mask(
        self,
        action_mask: np.ndarray,
        action_dict: dict[str, Union[dict | gym.spaces.MultiBinary]],
        root_path: str = "",
    ):
        for key, value in action_dict.items():
            path_key = root_path + "|" + key
            if type(value) is dict:
                self.build_action_mask(
                    action_mask=action_mask,
                    action_dict=value,
                    root_path=path_key,
                )
            else:
                flatten_action_def = self.action_def_map[path_key]
                start_idx = flatten_action_def.start_idx
                end_idx = start_idx + flatten_action_def.size
                action_mask[start_idx:end_idx] = value.flatten()

    def return_flattened_action_ranges(
        self,
        action_dict: dict[str, Union[dict | gym.spaces.MultiBinary]],
        action_def_map: dict[str, FlattenActionDefinition],
        root_path: str = "",
        start_idx=0,
    ):
        for key, value in action_dict.items():
            path_key = root_path + "|" + key
            if type(value) is gym.spaces.Dict:
                start_idx = self.return_flattened_action_ranges(
                    action_dict=value,
                    action_def_map=action_def_map,
                    root_path=path_key,
                    start_idx=start_idx,
                )
            else:
                size = np.prod(value.shape)
                action_def_map[path_key] = FlattenActionDefinition(
                    path_key=path_key, start_idx=start_idx, size=size, shape=value.shape
                )
                start_idx += size
        return start_idx

    def action(self, action: np.int64) -> SelectedAction:
        action_idx = action.item()
        for path_key, action_def in self.action_def_map.items():
            start_idx = action_def.start_idx
            end_idx = start_idx + action_def.size
            if start_idx <= action_idx < end_idx:
                if action_def.size == 1:
                    return SelectedAction(path_key=path_key, params=[])
                else:
                    corresponding_indices = np.unravel_index(
                        action_idx - start_idx, action_def.shape
                    )
                    return SelectedAction(
                        path_key=path_key, params=corresponding_indices
                    )
        raise ValueError(f"Invalid action index {action_idx}")
