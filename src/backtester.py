#!/usr/bin/env python3
"""
Backtesting Engine for Miner Strategy
Simplified backtesting to evaluate historical performance
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def run_backtest(symbol, data, direction, config, lookback_years=10):
    """
    Run simplified backtest on historical data

    Args:
        symbol: Stock symbol
        data: Historical OHLC DataFrame
        direction: 'LONG' or 'SHORT'
        config: Configuration dict
        lookback_years: Years of data to backtest

    Returns:
        dict: Backtest performance metrics
    """
    try:
        if data is None or data.empty or len(data) < 252:  # Min 1 year
            return None

        # Limit to specified lookback period
        start_date = datetime.now() - timedelta(days=lookback_years*365)
        test_data = data[data.index >= start_date].copy()

        if len(test_data) < 100:
            return None

        # Simple moving average strategy for backtest
        test_data['SMA_50'] = test_data['Close'].rolling(50).mean()
        test_data['SMA_200'] = test_data['Close'].rolling(200).mean()
        test_data = test_data.dropna()

        if len(test_data) < 50:
            return None

        # Simulate trades
        trades = simulate_trades(test_data, direction, config)

        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0
            }

        # Calculate metrics
        metrics = calculate_metrics(trades, config)

        return metrics

    except Exception as e:
        logger.error(f""Error in backtest for {symbol}: {e}"")
        return None

def simulate_trades(data, direction, config):
    """
    Simulate trades based on simple rules

    Returns:
        list: List of trade dicts with entry, exit, P&L
    """
    trades = []

    try:
        position = None

        for i in range(50, len(data)):
            current = data.iloc[i]
            prev = data.iloc[i-1]

            # Entry signal (simplified)
            if position is None:
                if direction == 'LONG':
                    # Golden cross
                    if prev['SMA_50'] <= prev['SMA_200'] and current['SMA_50'] > current['SMA_200']:
                        position = {
                            'entry_date': current.name,
                            'entry_price': current['Close'],
                            'direction': 'LONG',
                            'stop': current['Close'] * 0.97  # 3% stop
                        }
                elif direction == 'SHORT':
                    # Death cross
                    if prev['SMA_50'] >= prev['SMA_200'] and current['SMA_50'] < current['SMA_200']:
                        position = {
                            'entry_date': current.name,
                            'entry_price': current['Close'],
                            'direction': 'SHORT',
                            'stop': current['Close'] * 1.03  # 3% stop
                        }

            # Exit signal
            elif position is not None:
                exit_triggered = False
                exit_price = current['Close']

                # Stop loss
                if position['direction'] == 'LONG':
                    if current['Low'] <= position['stop']:
                        exit_triggered = True
                        exit_price = position['stop']
                    # Target (5% profit)
                    elif current['High'] >= position['entry_price'] * 1.05:
                        exit_triggered = True
                        exit_price = position['entry_price'] * 1.05

                elif position['direction'] == 'SHORT':
                    if current['High'] >= position['stop']:
                        exit_triggered = True
                        exit_price = position['stop']
                    # Target (5% profit)
                    elif current['Low'] <= position['entry_price'] * 0.95:
                        exit_triggered = True
                        exit_price = position['entry_price'] * 0.95

                if exit_triggered:
                    # Calculate P&L
                    if position['direction'] == 'LONG':
                        pnl = (exit_price - position['entry_price']) / position['entry_price']
                    else:
                        pnl = (position['entry_price'] - exit_price) / position['entry_price']

                    trades.append({
                        'entry_date': position['entry_date'],
                        'entry_price': position['entry_price'],
                        'exit_date': current.name,
                        'exit_price': exit_price,
                        'direction': position['direction'],
                        'pnl_pct': pnl * 100,
                        'pnl_amount': pnl
                    })

                    position = None

        return trades

    except Exception as e:
        logger.error(f""Error simulating trades: {e}"")
        return []

def calculate_metrics(trades, config):
    """
    Calculate performance metrics from trade list

    Returns:
        dict: Performance metrics
    """
    try:
        if not trades:
            return {}

        df = pd.DataFrame(trades)

        # Win rate
        wins = df[df['pnl_pct'] > 0]
        losses = df[df['pnl_pct'] <= 0]
        win_rate = len(wins) / len(df) * 100 if len(df) > 0 else 0

        # Average win/loss
        avg_win = wins['pnl_pct'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['pnl_pct'].mean()) if len(losses) > 0 else 0

        # Total return
        total_return = df['pnl_pct'].sum()

        # Profit factor
        gross_profit = wins['pnl_pct'].sum() if len(wins) > 0 else 0
        gross_loss = abs(losses['pnl_pct'].sum()) if len(losses) > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Sharpe ratio (simplified)
        returns = df['pnl_pct'].values
        sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0

        # Maximum drawdown
        cumulative = (1 + df['pnl_amount']).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max * 100
        max_dd = abs(drawdown.min()) if len(drawdown) > 0 else 0

        return {
            'total_trades': len(trades),
            'win_rate': round(win_rate, 1),
            'total_return': round(total_return, 1),
            'sharpe_ratio': round(sharpe, 2),
            'max_drawdown': round(max_dd, 1),
            'profit_factor': round(profit_factor, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2)
        }

    except Exception as e:
        logger.error(f""Error calculating metrics: {e}"")
        return {}
