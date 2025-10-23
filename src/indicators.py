"#!/usr/bin/env python3
""""""
Technical Indicator Calculations
Implements Stochastic, RSI, and MACD as per Miner's specifications
""""""

import pandas as pd
import numpy as np
import pandas_ta as ta
import logging

logger = logging.getLogger(__name__)

def calculate_indicators(data, config):
    """"""
    Calculate all technical indicators for Miner strategy

    Args:
        data: DataFrame with OHLC data
        config: Indicator configuration dict

    Returns:
        DataFrame with calculated indicators
    """"""
    try:
        if data is None or data.empty or len(data) < 50:
            return None

        df = data.copy()

        # Stochastic Oscillator (14-3-3)
        stoch_config = config['stochastic']
        stoch = ta.stoch(
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            k=stoch_config['period'],
            d=stoch_config['smooth_d'],
            smooth_k=stoch_config['smooth_k']
        )

        if stoch is not None and not stoch.empty:
            df['stoch_k'] = stoch[f'STOCHk_{stoch_config[""period""]}_{stoch_config[""smooth_d""]}_{stoch_config[""smooth_k""]}']
            df['stoch_d'] = stoch[f'STOCHd_{stoch_config[""period""]}_{stoch_config[""smooth_d""]}_{stoch_config[""smooth_k""]}']
        else:
            logger.warning(""Stochastic calculation failed"")
            return None

        # RSI (14-period)
        rsi_config = config['rsi']
        df['rsi'] = ta.rsi(df['Close'], length=rsi_config['period'])

        # MACD (12-26-9)
        macd_config = config['macd']
        macd = ta.macd(
            df['Close'],
            fast=macd_config['fast'],
            slow=macd_config['slow'],
            signal=macd_config['signal']
        )

        if macd is not None and not macd.empty:
            df['macd'] = macd[f'MACD_{macd_config[""fast""]}_{macd_config[""slow""]}_{macd_config[""signal""]}']
            df['macd_signal'] = macd[f'MACDs_{macd_config[""fast""]}_{macd_config[""slow""]}_{macd_config[""signal""]}']
            df['macd_hist'] = macd[f'MACDh_{macd_config[""fast""]}_{macd_config[""slow""]}_{macd_config[""signal""]}']
        else:
            logger.warning(""MACD calculation failed"")
            return None

        # Drop NaN rows
        df = df.dropna()

        if len(df) < 20:
            return None

        return df

    except Exception as e:
        logger.error(f""Error calculating indicators: {e}"")
        return None

def is_overbought(stoch_k, threshold=80):
    """"""Check if stochastic is overbought""""""
    return stoch_k > threshold

def is_oversold(stoch_k, threshold=20):
    """"""Check if stochastic is oversold""""""
    return stoch_k < threshold

def detect_crossover(series1, series2, lookback=2):
    """"""
    Detect if series1 crossed above series2

    Returns:
        bool: True if crossover detected
    """"""
    if len(series1) < lookback or len(series2) < lookback:
        return False

    # Previous: series1 was below series2
    # Current: series1 is above series2
    prev_below = series1.iloc[-lookback] <= series2.iloc[-lookback]
    curr_above = series1.iloc[-1] > series2.iloc[-1]

    return prev_below and curr_above

def detect_crossunder(series1, series2, lookback=2):
    """"""
    Detect if series1 crossed below series2

    Returns:
        bool: True if crossunder detected
    """"""
    if len(series1) < lookback or len(series2) < lookback:
        return False

    # Previous: series1 was above series2
    # Current: series1 is below series2
    prev_above = series1.iloc[-lookback] >= series2.iloc[-lookback]
    curr_below = series1.iloc[-1] < series2.iloc[-1]

    return prev_above and curr_below
"
