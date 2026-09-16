import pandas as pd
import numpy as np

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates technical indicators for a given OHLCV DataFrame.
    Expected columns: ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    """
    df = df.copy()
    
    # Ensure sorted chronologically
    if 'Date' in df.columns:
        df = df.sort_values(by='Date').reset_index(drop=True)
        
    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']
    
    # 1. Simple Moving Averages (SMA)
    df['SMA20'] = close.rolling(window=20, min_periods=1).mean()
    df['SMA50'] = close.rolling(window=50, min_periods=1).mean()
    df['SMA200'] = close.rolling(window=200, min_periods=1).mean()
    
    # 2. Exponential Moving Averages (EMA)
    df['EMA12'] = close.ewm(span=12, adjust=False).mean()
    df['EMA26'] = close.ewm(span=26, adjust=False).mean()
    
    # 3. Relative Strength Index (RSI 14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / (loss.replace(0, 1e-9))
    df['RSI14'] = 100 - (100 / (1 + rs))
    # Replace NaN or invalid initial values
    df['RSI14'] = df['RSI14'].fillna(50.0)
    
    # 4. MACD (12, 26, 9)
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # 5. Bollinger Bands (20, 2)
    bb_std = close.rolling(window=20, min_periods=1).std().fillna(0)
    df['BB_Middle'] = df['SMA20']
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # 6. Average True Range (ATR 14)
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['ATR14'] = tr.rolling(window=14, min_periods=1).mean().fillna(close * 0.02)
    
    # 7. Volume Moving Average
    df['Vol_SMA20'] = volume.rolling(window=20, min_periods=1).mean()
    
    # Round float values for clean JSON outputs
    float_cols = ['SMA20', 'SMA50', 'SMA200', 'EMA12', 'EMA26', 'RSI14', 
                  'MACD', 'MACD_Signal', 'MACD_Hist', 'BB_Middle', 'BB_Upper', 'BB_Lower', 'ATR14', 'Vol_SMA20']
    for col in float_cols:
        df[col] = df[col].round(2)
        
    return df
