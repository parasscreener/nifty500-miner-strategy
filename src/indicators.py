#!/usr/bin/env python3
"""
Technical Indicator Calculations
Manual implementation of Stochastic, RSI, and MACD
No external dependencies except pandas and numpy
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_indicators(data, config):
    """
    Calculate all technical indicators for Miner strategy

    Args:
        data: DataFrame with OHLC data
        config: Indicator configuration dict

    Returns:
        DataFrame with calculated indicators
    """
    try:
        if data is None or data.empty or len(data) < 50:
            return None

        df = data.copy()

        # Stochastic Oscillator (14-3-3)
        stoch_config = config['stochastic']
        df = calculate_stochastic(
            df,
            period=stoch_config['period'],
            smooth_k=stoch_config['smooth_k'],
            smooth_d=stoch_config['smooth_d']
        )

        if 'stoch_k' not in df.columns or df['stoch_k'].isna().all():
            logger.warning("Stochastic calculation failed")
            return None

        # RSI (14-period)
        rsi_config = config['rsi']
        df['rsi'] = calculate_rsi(df['Close'], period=rsi_config['period'])

        if df['rsi'].isna().all():
            logger.warning("RSI calculation failed")
            return None

        # MACD (12-26-9)
        macd_config = config['macd']
        df = calculate_macd(
            df,
            fast=macd_config['fast'],
            slow=macd_config['slow'],
            signal=macd_config['signal']
        )

        if 'macd' not in df.columns or df['macd'].isna().all():
            logger.warning("MACD calculation failed")
            return None

        # Drop NaN rows
        df = df.dropna()

        if len(df) < 20:
            return None

        return df

    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return None

def calculate_stochastic(df, period=14, smooth_k=3, smooth_d=3):
    """
    Calculate Stochastic Oscillator

    Formula:
    %K = 100 * (Close - Low_n) / (High_n - Low_n)
    %D = SMA(%K, smooth_d)

    Args:
        df: DataFrame with High, Low, Close
        period: Lookback period (default 14)
        smooth_k: Smoothing period for %K (default 3)
        smooth_d: Smoothing period for %D (default 3)

    Returns:
        DataFrame with stoch_k and stoch_d columns
    """
    try:
        # Calculate rolling high and low
        low_min = df['Low'].rolling(window=period).min()
        high_max = df['High'].rolling(window=period).max()

        # Calculate %K
        stoch_raw = 100 * (df['Close'] - low_min) / (high_max - low_min)

        # Smooth %K
        df['stoch_k'] = stoch_raw.rolling(window=smooth_k).mean()

        # Calculate %D (SMA of %K)
        df['stoch_d'] = df['stoch_k'].rolling(window=smooth_d).mean()

        return df

    except Exception as e:
        logger.error(f"Error calculating Stochastic: {e}")
        df['stoch_k'] = np.nan
        df['stoch_d'] = np.nan
        return df

def calculate_rsi(series, period=14):
    """
    Calculate Relative Strength Index (RSI)

    Formula:
    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss

    Args:
        series: Price series (typically Close)
        period: Lookback period (default 14)

    Returns:
        Series with RSI values
    """
    try:
        # Calculate price changes
        delta = series.diff()

        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Calculate average gain and loss using exponential moving average
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        return pd.Series([np.nan] * len(series), index=series.index)

def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)

    Formula:
    MACD Line = EMA(fast) - EMA(slow)
    Signal Line = EMA(MACD Line, signal)
    Histogram = MACD Line - Signal Line

    Args:
        df: DataFrame with Close prices
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line EMA period (default 9)

    Returns:
        DataFrame with macd, macd_signal, macd_hist columns
    """
    try:
        # Calculate EMAs
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()

        # Calculate MACD line
        df['macd'] = ema_fast - ema_slow

        # Calculate signal line
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()

        # Calculate histogram
        df['macd_hist'] = df['macd'] - df['macd_signal']

        return df

    except Exception as e:
        logger.error(f"Error calculating MACD: {e}")
        df['macd'] = np.nan
        df['macd_signal'] = np.nan
        df['macd_hist'] = np.nan
        return df

def is_overbought(stoch_k, threshold=80):
    """Check if stochastic is overbought"""
    return stoch_k > threshold

def is_oversold(stoch_k, threshold=20):
    """Check if stochastic is oversold"""
    return stoch_k < threshold

def detect_crossover(series1, series2, lookback=2):
    """
    Detect if series1 crossed above series2

    Args:
        series1: First series (e.g., fast line)
        series2: Second series (e.g., slow line)
        lookback: Number of bars to check (default 2)

    Returns:
        bool: True if crossover detected
    """
    try:
        if len(series1) < lookback or len(series2) < lookback:
            return False

        # Previous: series1 was below or equal to series2
        # Current: series1 is above series2
        prev_below = series1.iloc[-lookback] <= series2.iloc[-lookback]
        curr_above = series1.iloc[-1] > series2.iloc[-1]

        return prev_below and curr_above

    except Exception as e:
        logger.error(f"Error detecting crossover: {e}")
        return False

def detect_crossunder(series1, series2, lookback=2):
    """
    Detect if series1 crossed below series2

    Args:
        series1: First series (e.g., fast line)
        series2: Second series (e.g., slow line)
        lookback: Number of bars to check (default 2)

    Returns:
        bool: True if crossunder detected
    """
    try:
        if len(series1) < lookback or len(series2) < lookback:
            return False

        # Previous: series1 was above or equal to series2
        # Current: series1 is below series2
        prev_above = series1.iloc[-lookback] >= series2.iloc[-lookback]
        curr_below = series1.iloc[-1] < series2.iloc[-1]

        return prev_above and curr_below

    except Exception as e:
        logger.error(f"Error detecting crossunder: {e}")
        return False

# Test function
def test_indicators():
    """Test indicator calculations with sample data"""
    import yfinance as yf

    print("Testing indicator calculations...")

    # Download sample data
    data = yf.download("RELIANCE.NS", period="1y", progress=False)

    if data.empty:
        print("Failed to download test data")
        return

    # Test configuration
    config = {
        'stochastic': {'period': 14, 'smooth_k': 3, 'smooth_d': 3, 'overbought': 80, 'oversold': 20},
        'rsi': {'period': 14, 'overbought': 70, 'oversold': 30},
        'macd': {'fast': 12, 'slow': 26, 'signal': 9}
    }

    # Calculate indicators
    result = calculate_indicators(data, config)

    if result is not None:
        print("\nIndicator calculation successful!")
        print(f"Data shape: {result.shape}")
        print("\nLatest values:")
        print(f"Stochastic K: {result['stoch_k'].iloc[-1]:.2f}")
        print(f"Stochastic D: {result['stoch_d'].iloc[-1]:.2f}")
        print(f"RSI: {result['rsi'].iloc[-1]:.2f}")
        print(f"MACD: {result['macd'].iloc[-1]:.2f}")
        print(f"MACD Signal: {result['macd_signal'].iloc[-1]:.2f}")
        print("\n✅ All indicators working correctly!")
    else:
        print("❌ Indicator calculation failed")

if __name__ == "__main__":
    test_indicators()
