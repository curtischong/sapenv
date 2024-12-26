import gymnasium as gym
from all_types_and_consts import MAX_ACTIONS_IN_TURN, GameResult, SelectedAction
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

    def __init__(self, wandb_run=None):
        self.observation_space = env_observation_space
        self.action_space = env_action_space
        self.player = Player.init_starting_player()
        self.wandb_run = wandb_run

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
        action_result = action.perform_action(self.player, selected_action.params)
        observation = get_observation(self.player)

        if action_name == ActionName.END_TURN:
            self.player.num_actions_taken_in_turn = 0
            game_result = action_result
        else:
            game_result = GameResult.CONTINUE
            self.player.num_actions_taken_in_turn += 1
            if self.wandb_run:
                if self._roll_but_no_shop_pets_to_combine_with(action_name):
                    self.wandb_run.log({"roll_but_no_shop_pets_to_combine_with": 1})
                else:
                    self.wandb_run.log({"roll_but_no_shop_pets_to_combine_with": 0})
        # print(
        #     f"turn: {self.player.turn_number}, action: {action_name}, result: {game_result}"
        # )

        if (
            game_result == GameResult.TRUNCATED
            or self.player.num_actions_taken_in_turn > MAX_ACTIONS_IN_TURN
        ):
            done = True
            truncated = True
            info = {}
            reward = -100 + self.player.num_wins * 10
            if self.wandb_run:
                self.wandb_run.log(
                    {
                        "reward": reward,
                        "is_truncated": 1,
                    }
                )
            return observation, reward, done, truncated, info

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
        if done:
            if self.wandb_run:
                self.wandb_run.log({"reward": reward, "is_truncated": 0})

        truncated = False
        return observation, reward, done, truncated, info

    def _roll_but_no_shop_pets_to_combine_with(self, action_name: ActionName):
        if action_name != ActionName.ROLL_SHOP:
            return False
        my_pet_species = [pet.species for pet in self.player.team.pets]
        # Note: we don't need to compare with linked pets since on roll, they disappear
        for shop_pet in self.player.shop.slots:
            if shop_pet.pet.species in my_pet_species:
                return False
        return True

    def render(self):
        # Render environment for human viewing
        print(self.player)
        print(f"shop: {self.player.shop}")
        print("----------------------------------")
