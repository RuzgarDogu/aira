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

    def calculate_reward(self):
        if self.current_state_index == 0:
            return 0

        action = self.agent.active_position['index']
        close_index = self.config.close_index
        close = self.timeline[self.current_state_index][close_index]
        last_close = self.timeline[self.current_state_index-1][close_index]
        active_reward = self.agent.active_position['active_reward']
        stop_loss = self.config.stop_loss
        take_profit = self.config.take_profit
        new_active_reward = 0
        profit = close - last_close if action == 1 else last_close - close if action == 2 else 0
        new_active_reward = profit + active_reward

        if new_active_reward >= take_profit:
            new_active_reward = take_profit - active_reward
            self.agent.active_position['index'] = 0
            self.agent.active_position['price'] = None
            self.agent.active_position['active_reward'] = 0
        elif new_active_reward <= -stop_loss:
            new_active_reward = -stop_loss - active_reward
            self.agent.active_position['index'] = 0
            self.agent.active_position['price'] = None
            self.agent.active_position['active_reward'] = 0
        else:
            self.agent.active_position['active_reward'] = new_active_reward

        self.agent.balance += new_active_reward

        return profit

    """
        Burada şöyle bir durum söz konusu:
        Eğer agent long olan bir pozisyonda düşeceğini düşünüp short pozisyon alırsa
        O zaman posizyon kapanıyor. Ve posizyonsuz bir state oluşuyor.
        Bu durumda agent doğru bir karar vermiş olsa bile ona reward verilmiyor.
        Bu yüzden update position ile calculate reward fonksiyonları arasında bir bağlantı olmalı.
        Belki de bunlar birleştirilmeli.
    """

    def update_position(self, action):
        if self.agent.active_position['index'] == 0 and action != 0:
            close_price = self.timeline[self.current_state_index][self.config.close_index]
            self.agent.active_position['index'] = action
            self.agent.active_position['price'] = close_price
        else:
            if action != 0 and action != self.agent.active_position['index']:
                self.agent.active_position['index'] = 0
                self.agent.active_position['price'] = None
                self.agent.active_position['active_reward'] = 0


    def step(self, action):
        print("Action: {} {}".format(action, self.config.action_keys[action]))
        print(self.timeline[self.current_state_index][self.config.close_index])
        self.update_position(action)
        print("Active Position: {}".format(self.agent.active_position))        
        print("--------------------")
        self.current_state_index += 1
        next_state = self.timeline[self.current_state_index]
        reward = self.calculate_reward()
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