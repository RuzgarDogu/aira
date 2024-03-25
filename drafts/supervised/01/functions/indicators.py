import numpy as np
import pandas as pd

# Create a rsi indicator
def rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Function to calculate Williams Vix Fix (WVF)
def wvf(close, pd):
    return ((np.max(close.iloc[-pd:]) - close) / np.max(close.iloc[-pd:]) * 100)

# Function to calculate the sma
def sma(df, period=14):
    return df.rolling(period).mean()

# Function to calculate the ema
def ema(df, period=14):
    return df.ewm(span=period, adjust=False).mean()

# Function to calculate the macd
def macd(df, period1=12, period2=26, period3=9):
    ema1 = df.ewm(span=period1, adjust=False).mean()
    ema2 = df.ewm(span=period2, adjust=False).mean()
    macd = ema1 - ema2
    signal = macd.ewm(span=period3, adjust=False).mean()
    return macd, signal

# Function to calculate the atr
def atr(df, period=14):
    tr0 = df['high'] - df['low']
    tr1 = abs(df['high'] - df['close'].shift())
    tr2 = abs(df['low'] - df['close'].shift())
    tr = pd.DataFrame({'tr0': tr0, 'tr1': tr1, 'tr2': tr2}).max(axis=1)
    return tr.rolling(period).mean()

# Function to calculate the bollinger bands
def bollinger_bands(df, period=20):
    sma = df.rolling(period).mean()
    std = df.rolling(period).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return sma, upper_band, lower_band

# Function to calculate the stochastic oscillator
def stochastic_oscillator(df, period=14):
    l14 = df['low'].rolling(period).min()
    h14 = df['high'].rolling(period).max()
    return (df['close'] - l14) / (h14 - l14) * 100

# Function to calculate the relative vigor index
def rvi(df, period=14):
    close = df['close']
    open = df['open']
    high = df['high']
    low = df['low']
    rvi = (close - open) / (high - low)
    return rvi.rolling(period).mean()

# Function to calculate the differance between close and both sides of the bollinger bands
def bb_diff(df, period=20):
    sma, upper_band, lower_band = bollinger_bands(df['close'], period)
    return df['close'] - sma, df['close'] - upper_band, df['close'] - lower_band