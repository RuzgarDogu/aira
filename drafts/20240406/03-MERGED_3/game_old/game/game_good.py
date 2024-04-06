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
        print("--------------------")
        previous_state = self.timeline[self.current_state_index]
        previous_close = previous_state[self.config.close_index]
        self.current_state_index += 1
        current_state = self.timeline[self.current_state_index]
        current_close = current_state[self.config.close_index]

        active_position = self.agent.active_position
        current_profit = 0


        print("Action: {} | {}".format(self.config.action_keys[action], previous_close))
        print("New Close: {}".format(current_close))


        if active_position['index'] == 0:
            if action == 0:
                pass
            elif action == 1:
                current_profit = current_close - previous_close
                active_position['index'] = 1
                active_position['price'] = previous_close
            elif action == 2:
                current_profit = previous_close - current_close
                active_position['index'] = 2
                active_position['price'] = previous_close

        elif active_position['index'] == 1:
            if action == 0:
                current_profit = current_close - previous_close
                pass
            elif action == 1:
                current_profit = current_close - previous_close
                pass
            elif action == 2:
                active_position['index'] = 0
                active_position['price'] = None

        elif active_position['index'] == 2:
            if action == 0:
                current_profit = previous_close - current_close
                pass
            elif action == 1:
                active_position['index'] = 0
                active_position['price'] = None
            elif action == 2:
                current_profit = previous_close - current_close
                pass
        
        
        self.agent.balance += current_profit
        self.agent.active_position['current_profit'] = current_profit
        self.agent.active_position['total_profit'] = self.agent.active_position['total_profit'] + current_profit if current_profit != 0 else 0
        
        print("Current Profit: {}".format(current_profit))
        print("Active Position: {}".format(self.agent.active_position))
        print("Total Profit: {}".format(self.agent.active_position['total_profit']))
        print("Balance: {}".format(self.agent.balance))

        return current_profit


    def step(self, action):
        reward = self.update_state(action)
        next_state = self.timeline[self.current_state_index]
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