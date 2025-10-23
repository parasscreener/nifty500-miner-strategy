#!/usr/bin/env python3
"""
Miner High Probability Trading Strategy Scanner
Scans Nifty 500 stocks for trading setups based on Robert C. Miner's methodology
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from pathlib import Path
import yaml
import warnings
warnings.filterwarnings('ignore')

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/scanner_{datetime.now().strftime("%y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import custom modules
from indicators import calculate_indicators
from pattern_recognition import analyze_pattern
from fibonacci import calculate_fib_levels
from risk_management import calculate_position_size
from email_notifier import send_email_report
from backtester import run_backtest

# Load configuration
config_path = Path('config/config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

def load_stock_symbols():
    """Load Nifty 500 symbols from CSV"""
    try:
        symbols_file = Path('data/nifty500_symbols.csv')
        if symbols_file.exists():
            df = pd.read_csv(symbols_file)
            symbols = [s + '.NS' if not s.endswith('.NS') else s for s in df['Symbol'].tolist()]
            logger.info(f"Loaded {len(symbols)} stock symbols from CSV")
            return symbols
        else:
            logger.warning("Symbols file not found, using default list")
            return get_default_symbols()
    except Exception as e:
        logger.error(f"Error loading symbols: {e}")
        return get_default_symbols()

def get_default_symbols():
    """Get default Nifty 500 symbols (top 50 for demo)"""
    return [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
        'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS',
        'WIPRO.NS', 'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'TITAN.NS', 'NESTLEIND.NS',
        'SUNPHARMA.NS', 'TECHM.NS', 'POWERGRID.NS', 'NTPC.NS', 'ONGC.NS',
        'M&M.NS', 'TATASTEEL.NS', 'ADANIPORTS.NS', 'COALINDIA.NS', 'BAJAJFINSV.NS',
        'HINDALCO.NS', 'INDUSINDBK.NS', 'DRREDDY.NS', 'GRASIM.NS', 'DIVISLAB.NS',
        'BRITANNIA.NS', 'EICHERMOT.NS', 'JSWSTEEL.NS', 'CIPLA.NS', 'HEROMOTOCO.NS',
        'SHREECEM.NS', 'APOLLOHOSP.NS', 'BPCL.NS', 'UPL.NS', 'TATAMOTORS.NS',
        'TATACONSUM.NS', 'ADANIENT.NS', 'SBILIFE.NS', 'HDFCLIFE.NS', 'PIDILITIND.NS'
    ]

def fetch_stock_data(symbol, period='10y', interval='1d'):
    """Fetch historical stock data with caching"""
    try:
        cache_dir = Path('data/cache')
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{symbol}_{interval}_{period}.pkl"

        # Check cache (refresh daily)
        if cache_file.exists():
            age_hours = (datetime.now().timestamp() - cache_file.stat().st_mtime) / 3600
            if age_hours < 24:
                logger.debug(f"Loading {symbol} from cache ({age_hours:.1f}h old)")
                return pd.read_pickle(cache_file)

        logger.info(f"Downloading {symbol} {interval} data...")

        # Download with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                data = yf.download(
                    symbol,
                    period=period,
                    interval=interval,
                    progress=False,
                    auto_adjust=True
                )

                if not data.empty and len(data) > 50:
                    data.to_pickle(cache_file)
                    logger.debug(f"  Downloaded {len(data)} bars")
                    return data
                else:
                    logger.warning(f"  Insufficient data for {symbol}")
                    return pd.DataFrame()

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"  Retry {attempt+1}/{max_retries} for {symbol}")
                    continue
                else:
                    raise

        return pd.DataFrame()

    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()

def scan_stock(symbol, daily_data, intraday_data):
    """
    Scan single stock for Miner strategy setup
    Returns: dict with setup details or None
    """
    try:
        if daily_data.empty or intraday_data.empty:
            return None

        if len(daily_data) < 50 or len(intraday_data) < 50:
            logger.debug(f"{symbol}: Insufficient data")
            return None

        # Calculate indicators
        daily_ind = calculate_indicators(daily_data, config['indicators'])
        intraday_ind = calculate_indicators(intraday_data, config['indicators'])

        if daily_ind is None or intraday_ind is None:
            return None

        # Get latest values
        d_stoch = daily_ind['stoch_k'].iloc[-1]
        d_rsi = daily_ind['rsi'].iloc[-1]
        d_macd = daily_ind['macd'].iloc[-1]
        d_macd_signal = daily_ind['macd_signal'].iloc[-1]

        # Check daily momentum direction
        daily_bullish = (
            d_stoch > 50 and d_rsi > 50 and
            d_macd > d_macd_signal and d_stoch < 80
        )
        daily_bearish = (
            d_stoch < 50 and d_rsi < 50 and
            d_macd < d_macd_signal and d_stoch > 20
        )

        if not (daily_bullish or daily_bearish):
            return None

        # Check 60m trigger
        if len(intraday_ind) < 2:
            return None

        i_stoch_prev = intraday_ind['stoch_k'].iloc[-2]
        i_stoch_curr = intraday_ind['stoch_k'].iloc[-1]
        i_macd_prev = intraday_ind['macd'].iloc[-2]
        i_macd_curr = intraday_ind['macd'].iloc[-1]
        i_macd_sig_prev = intraday_ind['macd_signal'].iloc[-2]
        i_macd_sig_curr = intraday_ind['macd_signal'].iloc[-1]

        # Bullish trigger
        bullish_trigger = (
            daily_bullish and
            i_stoch_prev <= 20 and i_stoch_curr > 20 and
            i_macd_curr > i_macd_sig_curr and i_macd_prev <= i_macd_sig_prev
        )

        # Bearish trigger
        bearish_trigger = (
            daily_bearish and
            i_stoch_prev >= 80 and i_stoch_curr < 80 and
            i_macd_curr < i_macd_sig_curr and i_macd_prev >= i_macd_sig_prev
        )

        if not (bullish_trigger or bearish_trigger):
            return None

        # Calculate entry, stop, position size
        current_price = daily_data['Close'].iloc[-1]

        if bullish_trigger:
            entry = intraday_data['High'].iloc[-1] * 1.001  # 0.1% above
            swing_low = daily_data['Low'].iloc[-5:].min()
            stop = swing_low * 0.999  # 0.1% below
            direction = 'LONG'
            target_1 = current_price * 1.05  # 5% quick profit
        else:
            entry = intraday_data['Low'].iloc[-1] * 0.999  # 0.1% below
            swing_high = daily_data['High'].iloc[-5:].max()
            stop = swing_high * 1.001  # 0.1% above
            direction = 'SHORT'
            target_1 = current_price * 0.95  # 5% quick profit

        risk_per_share = abs(entry - stop)

        if risk_per_share < 0.01:  # Minimum risk check
            return None

        position_size = calculate_position_size(
            config['trading']['default_account_size'],
            risk_per_share,
            config['trading']['max_risk_per_trade']
        )

        # Fibonacci levels
        recent_high = daily_data['High'].iloc[-20:].max()
        recent_low = daily_data['Low'].iloc[-20:].min()
        fib_levels = calculate_fib_levels(recent_high, recent_low, config['fibonacci'])

        # Pattern analysis
        pattern_result = analyze_pattern(daily_data)

        # Run quick backtest
        backtest_results = run_backtest(symbol, daily_data, direction, config)

        return {
            'symbol': symbol,
            'direction': direction,
            'current_price': round(current_price, 2),
            'entry': round(entry, 2),
            'stop': round(stop, 2),
            'target_1': round(target_1, 2),
            'risk_per_share': round(risk_per_share, 2),
            'position_size': position_size,
            'total_risk': round(position_size * risk_per_share, 2),
            'daily_stoch': round(d_stoch, 1),
            'daily_rsi': round(d_rsi, 1),
            'daily_macd': round(d_macd, 2),
            'pattern': pattern_result,
            'fib_levels': fib_levels,
            'backtest': backtest_results,
            'timestamp': datetime.now()
        }

    except Exception as e:
        logger.error(f"Error scanning {symbol}: {e}")
        return None

def main():
    """Main execution function"""
    logger.info("=" * 80)
    logger.info("MINER STRATEGY SCANNER STARTED")
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    logger.info("=" * 80)

    # Load stock symbols
    symbols = load_stock_symbols()
    logger.info(f"Total symbols to scan: {len(symbols)}")

    bullish_setups = []
    bearish_setups = []
    watchlist = []
    errors = []

    for i, symbol in enumerate(symbols, 1):
        logger.info(f"[{i}/{len(symbols)}] Scanning {symbol}...")

        try:
            # Fetch data
            daily_data = fetch_stock_data(symbol, period='10y', interval='1d')
            intraday_data = fetch_stock_data(symbol, period='60d', interval='60m')

            # Scan for setup
            result = scan_stock(symbol, daily_data, intraday_data)

            if result:
                if result['direction'] == 'LONG':
                    bullish_setups.append(result)
                    logger.info(f"  ✓ BULLISH SETUP: Entry {result['entry']}, Stop {result['stop']}")
                else:
                    bearish_setups.append(result)
                    logger.info(f"  ✓ BEARISH SETUP: Entry {result['entry']}, Stop {result['stop']}")

        except Exception as e:
            errors.append({'symbol': symbol, 'error': str(e)})
            logger.error(f"  ✖ Error: {e}")

    # Sort by backtest performance
    bullish_setups.sort(
        key=lambda x: x['backtest'].get('sharpe_ratio', 0) if x['backtest'] else 0,
        reverse=True
    )
    bearish_setups.sort(
        key=lambda x: x['backtest'].get('sharpe_ratio', 0) if x['backtest'] else 0,
        reverse=True
    )

    # Limit to top setups
    max_setups = config['reporting']['max_setups_per_direction']
    bullish_setups = bullish_setups[:max_setups]
    bearish_setups = bearish_setups[:max_setups]

    # Compile results
    results = {
        'scan_date': datetime.now(),
        'total_scanned': len(symbols),
        'bullish_setups': bullish_setups,
        'bearish_setups': bearish_setups,
        'watchlist': watchlist,
        'errors': errors,
        'config': config
    }

    # Save results
    results_dir = Path('results/daily_scans')
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
    pd.to_pickle(results, results_file)

    logger.info("=" * 80)
    logger.info("SCAN COMPLETE")
    logger.info(f"Bullish Setups: {len(bullish_setups)}")
    logger.info(f"Bearish Setups: {len(bearish_setups)}")
    logger.info(f"Errors: {len(errors)}")
    logger.info("=" * 80)

    # Send email report
    try:
        send_email_report(results, config)
        logger.info("Email report sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

    return results

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
