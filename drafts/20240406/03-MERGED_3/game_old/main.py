from game.config import Config
from game.game import Game
from game.agent import Agent
import pandas as pd
from tqdm import tqdm


# # Load JSON file
# df = pd.read_json('testdata.json')

# # Export to CSV
# df.to_excel('testdata.xlsx', index=False)


# exit()

config = Config("01.json")
datasheet = pd.read_csv("data/FOREXCOM_NSXUSD_M5.csv")
datasheet = datasheet.sort_values("Bar_Time_UNIX", ascending=True)
datasheet["time"] = pd.to_datetime(datasheet["Bar_Time_UNIX"] / 1000, unit="s")
datasheet = datasheet.filter(items=config.state_keys)

data = datasheet.to_numpy()
agent = Agent(config)

print("Game started.....................{}".format(config.capital))
success = 0
fail = 0


"""
    En optimum take profit ve stop loss değerlerini bulmak için
"""
# results = {}
# with tqdm(total=62500, desc="Testing Success Rate With Commission ...") as pbar:
#     for tp in range(5, 30):
#         for sl in range(5, 30):
#             config.take_profit = tp
#             config.stop_loss = sl
#             success = 0
#             fail = 0
#             for i in range(100):
#                 game = Game(data, agent, config)
#                 game.play()
#                 if game.result["balance"] > config.capital:
#                     success += 1
#                 else:
#                     fail += 1
#             pbar.update(1)
#             success_rate = (success / (success + fail)) * 100
#             results[(tp, sl)] = success_rate

# # Sort results by success rate in descending order and get the top 5
# top_5 = sorted(results.items(), key=lambda x: x[1], reverse=True)[:5]

# for tp_sl, success_rate in top_5:
#     print(f"TP: {tp_sl[0]}, SL: {tp_sl[1]}, Success rate: {success_rate}%")


total_steps = 1000
description = "Testing Success Rate With ${} Commission Fee ...".format(
    config.transaction_fee
)
with tqdm(total=total_steps, desc=description) as pbar:
    for i in range(total_steps):
        game = Game(data, agent, config)
        game.play()
        if game.result["balance"] > config.capital:
            success += 1
        else:
            fail += 1
        pbar.update(1)

print("Success: {} | Fail: {}".format(success, fail))
print(
    "Success rate with ${} fee: {}%".format(
        config.transaction_fee, (success / (success + fail)) * 100
    )
)

# game = Game(data, agent, config)
# game.play()
# result = game.result["balance"]
# log = game.result["log"]

# df = pd.DataFrame(log)
# df.to_csv("log.csv", index=False)

# print(result)
# print("Game finished.....................")
