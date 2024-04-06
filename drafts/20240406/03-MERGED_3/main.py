from config.config import Config
from train.model import Model
import pandas as pd
import numpy as np
from functions.utils import split_data, prepareData, create_dataset
from game.game import Game
from game.agent import Agent

config = Config("config_test.json")
gameConfig = Config("game_config.json")
data_file = "data/FOREXCOM_NSXUSD_M15.csv"

data = pd.read_csv(data_file)

data = prepareData(data)

_x, _y, ref = create_dataset(data, config)

train_x, test_x = split_data(_x, config.split_ratio)
train_y, test_y = split_data(_y, config.split_ratio)
_, ref = split_data(ref, config.split_ratio)


model = Model(config, train_x, train_y)

if gameConfig.use_trained_model:
    model.load("model.keras")
else:
    model.train()
    res = model.evaluate(test_x, test_y)
    print("res: ", res)

""" GAME """
agent = Agent(conf=gameConfig, model=model, states=test_x)
ref = ref.reshape(-1, 1)
game = Game(data=ref, agent=agent, conf=gameConfig)
test = game.play()

print("------------------------------------")
print("------------------------------------")
print("------------------------------------")
print("test: ", test["balance"])

exit()
