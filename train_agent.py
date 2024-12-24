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


def train_with_masks(ret):
    """
    method for performing agent training
    """
    # initialize environment
    # env = FlattenAction(FlattenObservation(SuperAutoPetsEnv()))
    env = FlattenAction(FlattenObservation(SuperAutoPetsEnv()))

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
            batch_size=ret.batch_size,
            learning_rate=ret.learning_rate,
            gamma=ret.gamma,
        )

    # train
    log.info("Starting training...")
    for episode in range(ret.nb_games):
        # reset environment before starting to train (useful when retrying)
        obs = env.reset()

        # setup trainer and start learning
        model.set_logger(logger)
        model.learn(total_timesteps=ret.nb_steps, callback=checkpoint_callback)
        env.env.render()
        # evaluate_policy(model, env, n_eval_episodes=100, reward_threshold=0, warn=False)
        obs = env.reset()

        log.info("One full iter is done")
        if episode % 10 == 0:
            model.save("./models/" + ret.model_name)


def eval_model(ret):
    env = FlattenAction(FlattenObservation(SuperAutoPetsEnv()))
    # load model
    trained_model = MaskablePPO.load("./models/" + ret.model_name)

    log.info("Predicting...")

    # predict
    obs = env.reset()
    rewards = []
    for i in tqdm(range(ret.nb_games), "Games:"):
        # Predict outcome with model
        action_masks = get_action_masks(env)
        action, _states = trained_model.predict(
            obs, action_masks=action_masks, deterministic=True
        )

        obs, reward, done, info = env.step(action)
        if done:
            obs = env.reset()
        rewards.append(reward)
    log.info(" ".join([str(sum(rewards)), str(len(rewards)), str(np.mean(rewards))]))
    env.close()
