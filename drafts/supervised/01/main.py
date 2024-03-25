from config import Config
from model import Model
import pandas as pd
import numpy as np
from functions.utils import split_data, prepareData, create_dataset

config = Config('config.json')
data_file = 'data/FOREXCOM_NSXUSD_M15.csv'
data = pd.read_csv(data_file)

# get the first 50 rows

data = prepareData(data)
train_data, test_data = split_data(data, config.split_data)
train_x, train_y = create_dataset(train_data, config)
print("train_x: ", len(train_x))
print("train_y: ", len(train_y))

# exit()
model = Model(config, train_x, train_y)
model.train()
exit()