from dataclasses import dataclass
from typing import Union
import gymnasium as gym

from environment.action_space import get_action_masks
# https://gist.github.com/colllin/1172e042edf267d5ec667fa9802673cf


@dataclass
class FlattenActionDefinition:
    path_key: str  # path to the action (in the dictionary)
    start_idx: int = 0
    size: int = 0


class FlattenAction(gym.ActionWrapper):
    """Action wrapper that flattens the action."""

    def __init__(self, env):
        super(FlattenAction, self).__init__(env)
        # self.action_space = gym.spaces.flatten_space(self.env.action_space)
        self.action_def_map = {}
        num_actions = self.return_flattened_action_ranges(
            self.env.action_space, action_def_map=self.action_def_map
        )  # TODO: binary search for which bucket you're in
        print(self.action_ranges)
        self.action_space = gym.spaces.MultiBinary(num_actions)

    def get_action_masks(self):
        # given the dictionary action mask of the environment, return a flattened version of it
        dict_action_mask = get_action_masks(self.env.player)

        for key, value in dict_action_mask.items():
            pass

    def return_flattened_action_ranges(
        self,
        action_dict: dict[str, Union[dict | gym.spaces.MultiBinary]],
        action_def_map: dict[str, FlattenActionDefinition],
        root_path: str = "",
        start_idx=0,
    ):
        for key, value in action_dict.items():
            path_key = root_path + "_" + key
            if type(value) is gym.spaces.Dict:
                start_idx = self.return_flattened_action_ranges(
                    action_dict=value,
                    action_def_map=action_def_map,
                    root_path=path_key,
                    start_idx=start_idx,
                )
            else:
                action_def_map[path_key] = FlattenActionDefinition(
                    path_key=path_key, start_idx=start_idx, size=len(value.n)
                )
                start_idx += value.n
        return start_idx

    def action(self, action):
        return gym.spaces.unflatten(self.env.action_space, action)

    def reverse_action(self, action):
        return gym.spaces.flatten(self.env.action_space, action)
