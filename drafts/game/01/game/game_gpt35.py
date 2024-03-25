import numpy as np

class Game:
    def __init__(self, data, agent, conf):
        self.data = data
        self.agent = agent
        self.config = conf
        self.current_state_index = 0
        self.timeline = []
        self.result = {}

    def reset(self):
        self.agent.reset()
        self.timeline = self.create_timeline(self.config.timeline_size)
        self.current_state_index = 0
        return self.timeline[self.current_state_index]

    def create_timeline(self, length=1000, start_index=0):
        buffer = len(self.data) - (length + 100)
        if buffer < 0:
            return self.data
        start_index = np.random.randint(0, buffer)

        return self.data[start_index:start_index+length]

    def check_done(self):
        cond_timeline_ended = self.current_state_index >= len(self.timeline) - 1
        cond_balance_zero = self.agent.balance <= 0
        return cond_timeline_ended or cond_balance_zero


    def update_state(self, action):
        reward = 0

        if self.agent.active_position['index'] == 0:  # No active position
            if action != 0:  # Long or Short action
                current_price = self.timeline[self.current_state_index][self.config.close_index]
                self.agent.active_position = {"index": action, "price": current_price, "current_reward": 0, "total_reward": 0}

        else:  # Active position exists
            current_price = self.timeline[self.current_state_index][self.config.close_index]
            active_position = self.agent.active_position
            position_price = active_position['price']
            position_index = active_position['index']
            total_reward = active_position['total_reward']

            if action == 0:  # Hold action
                reward = current_price - position_price  # Reward based on price change
                active_position['current_reward'] = reward

            else:  # Long or Short action
                if action == position_index:  # Same action as active position
                    reward = current_price - position_price
                    active_position['current_reward'] = reward

                else:  # Opposite action
                    reward = self.calculate_reward_on_close(current_price)
                    active_position['total_reward'] += reward
                    self.agent.active_position = {"index": 0, "price": None, "current_reward": 0, "total_reward": 0}

        self.agent.balance += reward  # Update agent's balance
        self.current_state_index += 1  # Update current state index
        return reward


    def calculate_reward_on_close(self, current_price):
        active_position = self.agent.active_position
        position_price = active_position['price']
        position_index = active_position['index']
        total_reward = active_position['total_reward']
        take_profit = self.config.take_profit
        stop_loss = self.config.stop_loss

        if position_index == 1:  # Long position
            if current_price >= position_price + take_profit:
                reward = take_profit
            elif current_price <= position_price - stop_loss:
                reward = -stop_loss
            else:
                reward = current_price - position_price

        elif position_index == 2:  # Short position
            if current_price <= position_price - take_profit:
                reward = take_profit
            elif current_price >= position_price + stop_loss:
                reward = -stop_loss
            else:
                reward = position_price - current_price

        return reward





    def step(self, action):
        print("Action: {} {}".format(action, self.config.action_keys[action]))
        print(self.timeline[self.current_state_index][self.config.close_index])
        reward = self.update_state(action)
        print("Active Position: {}".format(self.agent.active_position))        
        print("--------------------")
        next_state = self.timeline[self.current_state_index]
        print("Reward: {}".format(reward))
        print("Balance: {}".format(self.agent.balance))
        done = self.check_done()
        return next_state, reward, done

    def play(self):
        self.reset()
        for e in range(self.config.episode_count):
            state = self.reset()
            done = False
            while not done:
                action = self.agent.act()
                next_state, reward, done = self.step(action)
                state = next_state
                
        
        self.result['balance'] = self.agent.balance
        return self.result