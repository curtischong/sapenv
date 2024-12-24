import gymnasium as gym
from all_types_and_consts import GameResult, SelectedAction
from battle import battle
from environment.state_space import (
    env_observation_space,
    get_observation,
)
from environment.action_space import (
    ActionName,
    env_action_space,
    get_action_masks,
    actions_dict,
)
from player import Player


class SuperAutoPetsEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        self.observation_space = env_observation_space
        self.action_space = env_action_space
        self.player = Player.init_starting_player()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.player = Player.init_starting_player()
        obs = get_observation(self.player)
        return obs, {}

    def action_masks(self):
        return get_action_masks(self.player)

    def step(self, selected_action: SelectedAction):
        action_name = ActionName(selected_action.path_key[1:])
        action = actions_dict[action_name]
        action.perform_action(self.player, selected_action.params)
        observation = get_observation(self.player)

        if action_name == ActionName.END_TURN:
            game_result = (
                self.player.end_turn_action()
            )  # Get the game result after the action
        else:
            game_result = GameResult.CONTINUE
        # print(
        #     f"turn: {self.player.turn_number}, action: {action_name}, result: {game_result}"
        # )

        # Determine if the game is done based on the result
        info = {"game_result": game_result}
        reward = 0
        done = False
        if game_result == GameResult.WIN:
            reward = 100
            done = True
        elif game_result == GameResult.LOSE:
            # the more wins you have, less the penalty
            reward = -100 + self.player.num_wins * 10
            done = True

        truncated = False  # if they don't wain the game in max number of turns, the model obviously isn't good enough
        return observation, reward, truncated, done, info

    def render(self):
        # Render environment for human viewing
        print(self.player)
        print(f"shop: {self.player.shop}")
