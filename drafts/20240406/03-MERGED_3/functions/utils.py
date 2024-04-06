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
    lstm_data_ref = []
    for i in range(len(data) - lstm_window + 1):
        # Separate input and target data
        sequence = data[i : i + lstm_window]
        train_x = [item[:-3] for item in sequence]  # Exclude last two three for input
        train_y = sequence[-1][
            -3:-1
        ]  # Get the third and second last columns from the last element of the sequence
        data_ref = sequence[-1][
            -1
        ]  # Get the last column from the last element of the sequence

        lstm_data_x.append(np.array(train_x))
        lstm_data_y.append(np.array(train_y))
        lstm_data_ref.append(np.array(data_ref))
    return np.array(lstm_data_x), np.array(lstm_data_y), np.array(lstm_data_ref)


def add_extreme_values(data, config):
    window_size = config.look_ahead
    extreme_values = []
    data.reset_index(
        drop=True, inplace=True
    )  # Reset the index to ensure it starts from 0
    for i in range(len(data)):
        remaining_rows = len(data) - i - 1
        if remaining_rows >= window_size:
            next_rows = data.iloc[
                i + 1 : i + window_size + 1
            ]  # Select the next `window_size` rows
        else:
            next_rows = data.iloc[i + 1 :]  # Select remaining rows
        if not next_rows.empty:
            highest_high = next_rows[
                "high"
            ].max()  # Assuming the column names are 'high' and 'low'
            lowest_low = next_rows["low"].min()
            close_value = data.loc[
                i, "close"
            ]  # Assuming the close value is in a column named 'close'
            highest_long = highest_high - close_value
            highest_short = close_value - lowest_low
            extreme_values.append([highest_long, highest_short])
        else:
            extreme_values.append(
                [float("nan"), float("nan")]
            )  # No future data available
    extreme_values_df = pd.DataFrame(
        extreme_values, columns=["highest_long", "highest_short"]
    )
    # Concatenate extreme values DataFrame with original data DataFrame
    result_df = pd.concat([data, extreme_values_df], axis=1)
    return result_df


def normalize(data, keys):
    scaler = MinMaxScaler()
    # fit the scaler on the data except from the last column
    scaler.fit(data[:, :-1])
    data[:, :-1] = scaler.transform(data[:, :-1])
    return data


def create_dataset(data, config):
    data = add_extreme_values(data, config)
    data = data.dropna()

    data = data[config.state_keys]
    data["ref"] = data["close"]

    data = data.to_numpy()

    if config.normalize:
        data = normalize(data, config.state_keys)

    x, y, ref = toLstm(data, config.lstm_window_size)
    return x, y, ref


def prepareData(data):
    data["rsi"] = rsi(data, 14)
    data["wvf"] = wvf(data["close"], 14)
    data["sma14"] = sma(data["close"], 14)
    data["sma100"] = sma(data["close"], 100)
    _, data["diff_upper"], data["diff_lower"] = bb_diff(data, 20)
    data = data.drop(["Bar_Time_UNIX"], axis=1)
    data = data.dropna()
    return data
