from typing import Dict, Union
import gymnasium as gym
# https://gist.github.com/colllin/1172e042edf267d5ec667fa9802673cf


class FlattenAction(gym.ActionWrapper):
    """Action wrapper that flattens the action."""

    def __init__(self, env):
        super(FlattenAction, self).__init__(env)
        # self.action_space = gym.spaces.flatten_space(self.env.action_space)
        self.action_ranges, num_actions = self.return_flattened_action_ranges(
            0, self.env.action_space
        )  # TODO: binary search for which bucket you're in
        print(self.action_ranges)
        self.action_space = gym.spaces.MultiBinary(num_actions)

    def return_flattened_action_ranges(
        self,
        start_idx: int,
        action_dict: dict[str, Union[dict | gym.spaces.MultiBinary]],
    ):
        actions_ranges = []  # list of tuple: (action_name, start_idx, end_idx])
        for key, value in action_dict.items():
            if type(value) is gym.spaces.Dict:
                flattened_ranges, start_idx = self.return_flattened_action_ranges(
                    start_idx, value
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
