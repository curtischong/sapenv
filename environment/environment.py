import gymnasium as gym
from all_types_and_consts import (
    MAX_ACTIONS_IN_TURN,
    ActionReturn,
    BattleResult,
    GameResult,
    SelectedAction,
)
from environment.metrics_tracker import MetricsTracker
from environment.metrics_tracker_eval import MetricsTrackerEval
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
from opponent_db import OpponentDB

# from opponent_db2 import OpponentDBInMemory
from opponent_db2 import OpponentDBInMemory
from opponent_db_eval import OpponentDBEval
from pet_callback import set_pet_callbacks
from player import Player


class SuperAutoPetsEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        opponent_db: OpponentDB | OpponentDBInMemory | OpponentDBEval,
        metrics_tracker: MetricsTracker | MetricsTrackerEval,
    ):
        self.observation_space = env_observation_space
        self.action_space = env_action_space
        set_pet_callbacks()
        self.opponent_db = opponent_db
        self.player = Player.init_starting_player(self.opponent_db)
        self.metrics_tracker = metrics_tracker
        self.step_num = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.player = Player.init_starting_player(self.opponent_db)
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

        if (
            action_name == ActionName.END_TURN
            and self.player.num_actions_taken_in_turn <= MAX_ACTIONS_IN_TURN
            and self.player.turn_number
            == 0  # only insert BEFORE the battle on the first turn
        ):
            self.opponent_db.insert_to_db(
                self.player.team,
                self.player.num_wins,
                self.player.num_actions_taken_in_turn,
                self.player.hearts,
            )
        action_result = action.perform_action(self.player, selected_action.params)
        observation = get_observation(self.player)

        if action_name == ActionName.END_TURN:
            game_result = action_result[ActionReturn.GAME_RESULT]
            battle_result = action_result[ActionReturn.BATTLE_RESULT]

            reward = self.get_reward_from_battle_result(battle_result)

            # perform cleanup tasks how that the turn ended
            self.player.num_actions_taken_in_turn = 0
            self.opponent_db.insert_to_db(
                self.player.team,
                self.player.num_wins,
                self.player.num_actions_taken_in_turn,
                self.player.hearts,
            )
        else:
            game_result = GameResult.CONTINUE
            reward = -1 / MAX_ACTIONS_IN_TURN
            self.player.num_actions_taken_in_turn += 1
        # print(
        #     f"turn: {self.player.turn_number}, action: {action_name}, result: {game_result}"
        # )
        self.metrics_tracker.add_step_metrics(selected_action, action_result, reward)

        self.step_num += 1
        if self.step_num % 10000 == 0:
            self.step_num = 0
            self.opponent_db.flush()

        if (
            game_result == GameResult.TRUNCATED
            or self.player.num_actions_taken_in_turn > MAX_ACTIONS_IN_TURN
        ):
            done = False
            truncated = True
            info = {}
            # if reward > 0:
            #     reward = reward / 2
            slowness_penalty = (
                self.player.num_actions_taken_in_turn / MAX_ACTIONS_IN_TURN
            )
            reward = -10 - slowness_penalty
            self.metrics_tracker.log_episode_metrics(is_truncated=True)
            return observation, reward, done, truncated, info

        # Determine if the game is done based on the result
        done = game_result == GameResult.WIN or game_result == GameResult.LOSE
        if done:
            self.metrics_tracker.log_episode_metrics(
                is_truncated=False, player=self.player
            )

        truncated = False
        info = {}
        return observation, reward, done, truncated, info

    def get_reward_from_battle_result(self, battle_result: BattleResult):
        slowness_penalty = self.player.num_actions_taken_in_turn / MAX_ACTIONS_IN_TURN
        if battle_result == BattleResult.TEAM1_WIN:
            return self.gentle_exponential(self.player.num_wins)
        elif battle_result == BattleResult.TEAM2_WIN:
            return 1 - slowness_penalty
        elif battle_result == BattleResult.TIE:
            return 0.5 * self.gentle_exponential(self.player.num_wins)
        else:
            raise ValueError(f"Unknown battle result: {battle_result}")

    def render(self):
        # Render environment for human viewing
        print(self.player)
        print(f"shop: {self.player.shop}")
        print("----------------------------------")
