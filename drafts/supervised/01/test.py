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

    lstm_data_x.append(train_x)
    lstm_data_y.append(train_y)
  return lstm_data_x, lstm_data_y

# Example usage
data = [
    [1,2,3,4,5,6],
    [7,8,9,10,11,12],
    [13,14,15,16,17,18],
    [19,20,21,22,23,24],
    [25,26,27,28,29,30],
    [31,32,33,34,35,36],
    [37,38,39,40,41,42],
    [43,44,45,46,47,48],
    [49,50,51,52,53,54],
    [55,56,57,58,59,60],
]

lstm_window = 3
train_x, train_y = toLstm(data, lstm_window)

print(train_x)
print(train_y)
