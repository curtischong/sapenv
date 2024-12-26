"""
Methods for performing training of RL models, also support finetuning
"""

from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.evaluation import evaluate_policy
from sb3_contrib.common.maskable.utils import get_action_masks
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.logger import configure
from tqdm import tqdm
import numpy as np
import os
import sys
import logging as log
from environment.flatten_action import FlattenAction

from environment.environment import SuperAutoPetsEnv
from environment.flatten_observation import FlattenObservation
import wandb
from wandb.integration.sb3 import WandbCallback
from torch import nn
from stable_baselines3.common.callbacks import BaseCallback
from utils import require_consent


custom_network = dict(
    activation_fn=nn.SiLU,
    net_arch=dict(pi=[128, 128, 128, 128, 128, 128, 128], vf=[128, 128, 128, 128]),
)


class CustomWandbCallback(BaseCallback):
    """
    Custom callback to log additional metrics like loss to Weights & Biases.
    """

    def __init__(self, wandb_run, verbose=0):
        super(CustomWandbCallback, self).__init__(verbose)
        self.wandb_run = wandb_run

    def _on_step(self) -> bool:
        if "loss" in self.locals:
            # Log the loss value
            loss = self.locals["loss"]
            self.wandb_run.log({"loss": loss, "time_steps": self.num_timesteps})
        return True


def train_with_masks(ret):
    # Initialize wandb
    run = wandb.init(
        project="sap-ai",  # Choose an appropriate project name
        config={},
    )

    # initialize environment
    # env = FlattenAction(FlattenObservation(SuperAutoPetsEnv()))
    env = FlattenAction(FlattenObservation(SuperAutoPetsEnv(wandb_run=run)))

    # eval_env = SuperAutoPetsEnv(opponent_generator, valid_actions_only=True)  # need separate eval env for
    # EvalCallback (this is the wrong env - not working)

    # create folder to save log
    history_path = "./history/history_" + ret.model_name + "/"
    if not os.path.exists(history_path):
        os.makedirs(history_path, exist_ok=True)

    # setup logger - log should be linked to model
    # logger = configure("./history/sb3_log/")
    logger = configure(history_path)

    # create models directory if it does not exist
    if not os.path.exists("./models/"):
        os.makedirs("./models/")

    # setup model checkpoint callback, to save model after a specific #iters
    checkpoint_callback = CheckpointCallback(
        save_freq=ret.save_freq, save_path="./models/", name_prefix=ret.model_name
    )

    custom_callback = CustomWandbCallback(wandb_run=run)

    # save best model, using deterministic eval
    # eval_callback = EvalCallback(eval_env, best_model_save_path='./models/', log_path='./logs/', eval_freq=1000,
    #                              deterministic=True, render=False)

    if ret.finetune is not None:
        # check if current python version differ from the one the model is trained with
        vals = ret.infer_pversion.split(".")
        newer_python_version = (
            sys.version_info.major != vals[0] or sys.version_info.minor != vals[1]
        )
        custom_objects = {}
        if newer_python_version:
            custom_objects = {
                "learning_rate": ret.learning_rate,
                "batch_size": ret.batch_size,
                "clip_range": lambda _: 0.2,
                "gamma": ret.gamma,
            }

        log.info("Finetuning...")
        model = MaskablePPO.load(ret.finetune, custom_objects=custom_objects)
        model.set_env(env)
    else:
        log.info("Training from scratch...")
        model = MaskablePPO(
            "MlpPolicy",
            env,
            verbose=0,
            policy_kwargs=custom_network,
            batch_size=ret.batch_size,
            learning_rate=ret.learning_rate,
            gamma=ret.gamma,
        )
        # require the user to say yes if the path already exists: "./models/" + ret.model_name
        path = f"./models/{ret.model_name}.zip"
        if os.path.exists(path):
            require_consent(
                f"The path '{path}' already exists. Do you want to proceed? (yes/no): "
            )

    # train
    log.info("Starting training...")
    for episode in range(ret.nb_games):
        # reset environment before starting to train (useful when retrying)
        obs, info = env.reset()

        # setup trainer and start learning
        model.set_logger(logger)
        model.learn(
            total_timesteps=ret.nb_steps,
            log_interval=4,
            callback=[
                checkpoint_callback,
                custom_callback,
                # WandbCallback(
                #     # gradient_save_freq=100,
                #     model_save_path=f"models/{run.id}",
                #     verbose=2,
                #     log_loss=True,
                # ),
            ],
        )
        env.env.render()
        # evaluate_policy(model, env, n_eval_episodes=100, reward_threshold=0, warn=False)
        obs, info = env.reset()

        # log.info("One full iter is done")
        if episode % 10 == 0:
            model.save("./models/" + ret.model_name)

    # Close wandb run when done
    run.finish()


def eval_model(ret):
    env = FlattenAction(FlattenObservation(SuperAutoPetsEnv()))
    # load model
    trained_model = MaskablePPO.load("./models/" + ret.model_name)

    # predict
    rewards = []
    for i in tqdm(range(ret.nb_games), "Games:"):
        print("Game:", i)
        obs, info = env.reset()
        # run the episode
        while True:
            # Predict outcome with model
            action_masks = get_action_masks(env)
            env.env.render()

            # using deterministic=False helps it get stuck out of local minima: https://stackoverflow.com/questions/76510709/ppo-model-learns-well-then-predicts-only-negative-actions
            action, _states = trained_model.predict(
                obs, action_masks=action_masks, deterministic=False
            )
            env.readable_action_mask()
            print("actionname", env.action(action))
            print("-----------------------------------")

            obs, reward, done, truncated, info = env.step(action)
            if truncated:
                log.info("Episode truncated")
                break
            if done:
                log.info("Episode finished", info)
                rewards.append(reward)
                break
    # log.info(" ".join([str(sum(rewards)), str(len(rewards)), str(np.mean(rewards))]))
    print(f"sum rewards: {sum(rewards)}")
    print(f"len rewards: {len(rewards)}")
    print(f"mean rewards: {np.mean(rewards)}")
    env.close()
