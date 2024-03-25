import random

class Agent:
    def __init__(self, conf):
        self.config = conf
        self.balance = conf.capital
        self.active_position = {
            "index": 0,
            "price": None,
            "current_profit": 0.0, # reward of the current time step
            "total_profit": 0.0, # total reward of the active position
            }

    def reset(self):
        self.balance = self.config.capital

    def act(self):
        action = random.choice(self.config.action_keys)
        action_index = self.config.action_keys.index(action)
        return action_index