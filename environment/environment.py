import gymnasium as gym
from all_types_and_consts import (
    MAX_ACTIONS_IN_TURN,
    BattleResult,
    GameResult,
    SelectedAction,
)
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

    def gentle_exponential(self, x: float) -> float:
        # https://www.desmos.com/calculator/tayqvz7cxl
        assert 0 <= x <= 10

        # Base slightly greater than 1 for a gentle curve
        base = 1.1
        # Scale the exponential to fit the range [0, 10]
        scale_factor = 10 / (base**10 - 1)

        # Calculate the exponential value
        value = scale_factor * (base**x - 1)

        return value

    def step(self, selected_action: SelectedAction):
        action_name = ActionName(selected_action.path_key[1:])
        action = actions_dict[action_name]
        action_result = action.perform_action(self.player, selected_action.params)
        observation = get_observation(self.player)

        slowness_penalty = self.player.num_actions_taken_in_turn / MAX_ACTIONS_IN_TURN

        if action_name == ActionName.END_TURN:
            game_result, battle_result = action_result
            if battle_result == BattleResult.TEAM1_WIN:
                reward = self.gentle_exponential(self.player.num_wins)
            elif battle_result == BattleResult.TEAM2_WIN:
                reward = 1 - slowness_penalty
            elif battle_result == BattleResult.TIE:
                reward = 0.5 * self.gentle_exponential(self.player.num_wins)
            else:
                raise ValueError(f"Unknown battle result: {battle_result}")
            self.player.num_actions_taken_in_turn = 0
        else:
            game_result = GameResult.CONTINUE
            reward = -1 / MAX_ACTIONS_IN_TURN
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
            self.reset()
            info = {}
            # if reward > 0:
            #     reward = reward / 2
            reward = -10 - slowness_penalty
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
        done = game_result == GameResult.WIN or game_result == GameResult.LOSE
        if self.wandb_run:
            self.wandb_run.log({"reward": reward, "is_truncated": 0})
        if done:
            self.wandb_run.log({"num_wins": self.player.num_wins, "num_hearts": self.player.hearts})

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
