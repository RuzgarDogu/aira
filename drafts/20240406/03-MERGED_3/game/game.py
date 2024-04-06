import numpy as np


class Game:
    def __init__(self, data, agent, conf):
        self.data = data
        self.agent = agent
        self.config = conf
        self.current_state_index = 0
        self.timeline = []
        self.result = {
            "balance": 0,
            "log": [],
        }

    def reset(self):
        self.agent.reset()
        self.timeline = self.create_timeline(self.config.timeline_size)
        self.current_state_index = 0
        return self.timeline[self.current_state_index]

    def create_timeline(self, length=1000, start_index=0):
        return self.data
        # buffer = len(self.data) - (length + 100)
        # if buffer < 0:
        #     return self.data
        # start_index = np.random.randint(0, buffer)

        # return self.data[start_index:start_index+length]

    def check_done(self):
        cond_timeline_ended = self.current_state_index >= len(self.timeline) - 1
        cond_balance_zero = self.agent.balance <= 0
        return cond_timeline_ended or cond_balance_zero

    def update_state(self, action):
        previous_state = self.timeline[self.current_state_index]
        previous_close = previous_state[self.config.close_index]
        fee_spending = 0
        self.current_state_index += 1
        current_state = self.timeline[self.current_state_index]
        current_close = current_state[self.config.close_index]

        active_position = self.agent.active_position
        current_profit = 0

        stop_loss = self.config.stop_loss
        take_profit = self.config.take_profit

        self.log("current_position", self.config.action_keys[active_position["index"]])

        if active_position["index"] == 0:
            if action == 0:
                pass
            elif action == 1:
                current_profit = current_close - previous_close
                active_position["index"] = 1
                active_position["price"] = previous_close
                self.agent.balance -= self.config.transaction_fee
                fee_spending = self.config.transaction_fee
            elif action == 2:
                current_profit = previous_close - current_close
                active_position["index"] = 2
                active_position["price"] = previous_close
                self.agent.balance -= self.config.transaction_fee
                fee_spending = self.config.transaction_fee

        elif active_position["index"] == 1:
            if action == 0:
                current_profit = current_close - previous_close
                pass
            elif action == 1:
                current_profit = current_close - previous_close
                pass
            elif action == 2:
                active_position["index"] = 0
                active_position["price"] = None

        elif active_position["index"] == 2:
            if action == 0:
                current_profit = previous_close - current_close
                pass
            elif action == 1:
                active_position["index"] = 0
                active_position["price"] = None
            elif action == 2:
                current_profit = previous_close - current_close
                pass

        self.log("action", self.config.action_keys[action])
        self.log("current_balance", round(self.agent.balance, 2))
        self.log("close", previous_close)
        self.log("next_close", current_close)

        reward = current_profit - fee_spending

        upper_bound = take_profit - active_position["total_profit"]
        lower_bound = active_position["total_profit"] + stop_loss

        take_profit_activated = current_profit >= upper_bound
        stop_loss_activated = current_profit <= -lower_bound

        if take_profit_activated:
            self.log("SLTP", "Take Profit")
            current_profit = upper_bound
            active_position["index"] = 0
            active_position["price"] = None
            active_position["total_profit"] = 0
            active_position["current_profit"] = 0
        elif stop_loss_activated:
            self.log("SLTP", "Stop Loss")
            current_profit = -lower_bound
            active_position["index"] = 0
            active_position["price"] = None
            active_position["total_profit"] = 0
            active_position["current_profit"] = 0
        else:
            self.log("SLTP", "-")
            active_position["current_profit"] = current_profit
            active_position["total_profit"] = (
                active_position["total_profit"] + current_profit
                if current_profit != 0
                else 0
            )

        self.agent.balance += current_profit

        self.log("current_profit", round(current_profit, 2))
        self.log("total_profit", active_position["total_profit"], output=False)
        self.log("balance", round(self.agent.balance, 2))
        self.log("active_position", active_position["index"])

        return reward

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
                action = self.agent.act(self.current_state_index)
                next_state, reward, done = self.step(action)
                state = next_state

        self.result["balance"] = self.agent.balance

        if not self.config.use_trained_model:
            self.agent.model.save("model.keras")

        return self.result

    def log(self, key, val, output=True, print_log=False):
        if print_log or self.config.print_log:
            print("{}: {}".format(key, val))
        if len(self.result["log"]) < self.current_state_index:
            self.result["log"].append({})
            if self.config.print_log:
                print("----------------------------------")
        if output:
            self.result["log"][self.current_state_index - 1][key] = val
