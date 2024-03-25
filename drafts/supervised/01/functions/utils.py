from functions.indicators import *
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def split_data(data, ratio):
    split_data = int(len(data) * ratio)
    test_data = data[:split_data]
    train_data = data[split_data:]
    return train_data, test_data

def toLstm(data, lstm_window):
    """
    This function creates LSTM data with separate inputs and targets.

    Args:
        data: A list of lists representing the original data.
        lstm_window: The number of elements to consider in each LSTM sequence.

    Returns:
        A tuple containing two elements:
            - train_x: A list of lists, where each inner list represents an LSTM sequence
                        excluding the last two columns (targets).
            - train_y: A list of lists, where each inner list contains the last two columns
                        (targets) of the corresponding sequence in train_x.
    """
    lstm_data_x = []
    lstm_data_y = []
    for i in range(len(data) - lstm_window + 1):
        # Separate input and target data
        sequence = data[i:i+lstm_window]
        train_x = [item[:-2] for item in sequence]  # Exclude last two columns for input
        train_y = sequence[-1][-2:]  # Get last two columns from the last element of the sequence

        lstm_data_x.append(np.array(train_x))
        lstm_data_y.append(np.array(train_y))
    return np.array(lstm_data_x), np.array(lstm_data_y)

def add_extreme_values(data, config):
    window_size = config.look_ahead
    extreme_values = []
    data.reset_index(drop=True, inplace=True)  # Reset the index to ensure it starts from 0
    for i in range(len(data)):
        remaining_rows = len(data) - i - 1
        if remaining_rows >= window_size:
            next_rows = data.iloc[i+1:i+window_size+1]  # Select the next `window_size` rows
        else:
            next_rows = data.iloc[i+1:]  # Select remaining rows
        if not next_rows.empty:
            highest_high = next_rows['high'].max()  # Assuming the column names are 'high' and 'low'
            lowest_low = next_rows['low'].min()
            close_value = data.loc[i, 'close']  # Assuming the close value is in a column named 'close'
            highest_long = highest_high - close_value
            highest_short = close_value - lowest_low
            extreme_values.append([highest_long, highest_short])
        else:
            extreme_values.append([float('nan'), float('nan')])  # No future data available
    extreme_values_df = pd.DataFrame(extreme_values, columns=['highest_long', 'highest_short'])
    # Concatenate extreme values DataFrame with original data DataFrame
    result_df = pd.concat([data, extreme_values_df], axis=1)
    return result_df

def normalize(data):
    scaler = MinMaxScaler()
    return scaler.fit_transform(data)

def create_dataset(data, config):
    data = add_extreme_values(data, config)
    data = data.dropna()
    data = data[config.state_keys]
    # data.to_csv('check_data.csv', index=False)
    data = data.to_numpy()

    if config.normalize:
        data = normalize(data)

    if config.lstm_window_size > 1:
        x,y = toLstm(data, config.lstm_window_size)
    else:
        x = data[:, :-2]  # all rows, all columns except the last two
        y = data[:, -2:]  # all rows, only the last two columns
    return x, y

def prepareData(data):
    data['rsi'] = rsi(data, 14)
    data['wvf'] = wvf(data['close'], 14)
    data['sma14'] = sma(data['close'], 14)
    data['sma100'] = sma(data['close'], 100)
    _, data['diff_upper'], data['diff_lower'] = bb_diff(data, 20)
    data = data.drop(['Bar_Time_UNIX'], axis=1)
    data = data.dropna()
    return data
