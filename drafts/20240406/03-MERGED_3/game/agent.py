import random
import numpy as np


class Agent:
    def __init__(self, conf, model, states):
        self.config = conf
        self.model = model
        self.states = states
        self.balance = conf.capital
        self.active_position = {
            "index": 0,
            "price": None,
            "current_profit": 0.0,  # reward of the current time step
            "total_profit": 0.0,  # total reward of the active position
        }

    def reset(self):
        self.balance = self.config.capital

    def act(self, state_index):
        if self.config.use_random_action:
            action = random.choice(self.config.action_keys)
            action_index = self.config.action_keys.index(action)
            return action_index
        else:
            state = self.states[state_index]
            state = np.expand_dims(state, axis=0)
            predictions = self.model.predict(state)[0]
            normalized_predictions = predictions / np.sum(predictions)

            action_index = 0
            if (
                normalized_predictions[0] / normalized_predictions[1]
                > self.config.position_decision_ratio
            ):
                action_index = 1
            elif (
                normalized_predictions[1] / normalized_predictions[0]
                > self.config.position_decision_ratio
            ):
                action_index = 2

            return action_index
