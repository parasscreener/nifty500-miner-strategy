#!/usr/bin/env python3
"""
Robust Stock Scanner with Multiple Fallback Strategies
Handles network issues, rate limiting, and API failures
"""

import yfinance as yf
import pandas as pd
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_session():
    """Create a requests session with retry logic and custom headers"""
    session = requests.Session()

    # Add retries
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Custom headers to avoid blocking
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    })

    return session


def fetch_stock_data_robust(symbol, period="1y", session=None):
    """
    Fetch stock data with multiple fallback methods

    Method 1: yf.download() with session
    Method 2: yf.Ticker() with session
    Method 3: Direct API call fallback
    """

    if session is None:
        session = create_session()

    # Method 1: Try yf.download (most reliable)
    try:
        logger.info(f"Attempting Method 1 (download): {symbol}")
        data = yf.download(
            symbol, 
            period=period, 
            progress=False,
            session=session,
            timeout=10
        )

        if data is not None and not data.empty and len(data) > 10:
            logger.info(f"✓ Method 1 success: {symbol} ({len(data)} rows)")
            return data
        else:
            logger.warning(f"Method 1 returned insufficient data for {symbol}")

    except Exception as e:
        logger.warning(f"Method 1 failed for {symbol}: {str(e)[:80]}")

    # Small delay before next method
    time.sleep(0.5)

    # Method 2: Try yf.Ticker with session
    try:
        logger.info(f"Attempting Method 2 (Ticker): {symbol}")
        ticker = yf.Ticker(symbol, session=session)
        data = ticker.history(period=period)

        if data is not None and not data.empty and len(data) > 10:
            logger.info(f"✓ Method 2 success: {symbol} ({len(data)} rows)")
            return data
        else:
            logger.warning(f"Method 2 returned insufficient data for {symbol}")

    except Exception as e:
        logger.warning(f"Method 2 failed for {symbol}: {str(e)[:80]}")

    # Method 3: Try alternative exchange suffix
    if symbol.endswith('.NS'):
        alt_symbol = symbol.replace('.NS', '.BO')
        try:
            logger.info(f"Attempting Method 3 (alt exchange): {alt_symbol}")
            data = yf.download(alt_symbol, period=period, progress=False, session=session)

            if data is not None and not data.empty and len(data) > 10:
                logger.info(f"✓ Method 3 success: {alt_symbol} ({len(data)} rows)")
                return data

        except Exception as e:
            logger.warning(f"Method 3 failed for {alt_symbol}: {str(e)[:80]}")

    # All methods failed
    logger.error(f"✗ All methods failed for {symbol}")
    return None


def scan_nifty500_robust(csv_file='nifty500_symbols.csv', batch_size=10):
    """
    Scan Nifty 500 stocks with robust error handling and batching

    Args:
        csv_file: Path to CSV with stock symbols
        batch_size: Number of stocks to process before pause
    """

    # Read symbols
    try:
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded {len(df)} symbols from {csv_file}")

        # Ensure .NS suffix
        if 'Symbol' in df.columns:
            symbols = df['Symbol'].tolist()
            symbols = [s if s.endswith('.NS') else f"{s}.NS" for s in symbols]
        else:
            logger.error("CSV must have 'Symbol' column")
            return None, None

    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")
        return None, None

    # Create session
    session = create_session()

    # Results storage
    successful_data = {}
    failed_symbols = []

    # Process in batches
    total = len(symbols)

    for i, symbol in enumerate(symbols, 1):
        logger.info(f"\n[{i}/{total}] Processing: {symbol}")

        # Fetch data
        data = fetch_stock_data_robust(symbol, period="1y", session=session)

        if data is not None:
            successful_data[symbol] = data
        else:
            failed_symbols.append(symbol)

        # Pause after each batch to avoid rate limiting
        if i % batch_size == 0:
            logger.info(f"Completed batch {i//batch_size}. Pausing 3 seconds...")
            time.sleep(3)
        else:
            # Small delay between individual requests
            time.sleep(0.3)

        # Progress update
        if i % 50 == 0:
            success_rate = (len(successful_data) / i) * 100
            logger.info(f"Progress: {i}/{total} | Success rate: {success_rate:.1f}%")

    # Final summary
    logger.info("\n" + "=" * 70)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total symbols: {total}")
    logger.info(f"Successful: {len(successful_data)} ({len(successful_data)/total*100:.1f}%)")
    logger.info(f"Failed: {len(failed_symbols)} ({len(failed_symbols)/total*100:.1f}%)")

    if failed_symbols:
        logger.warning(f"\nFailed symbols ({len(failed_symbols)}):")
        for sym in failed_symbols[:20]:  # Show first 20
            logger.warning(f"  - {sym}")
        if len(failed_symbols) > 20:
            logger.warning(f"  ... and {len(failed_symbols) - 20} more")

    return successful_data, failed_symbols


if __name__ == "__main__":
    # Test with a small sample first
    logger.info("Starting Nifty 500 scan...")

    # Uncomment to test with small sample first:
    # test_symbols = pd.DataFrame({'Symbol': ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']})
    # test_symbols.to_csv('test_symbols.csv', index=False)
    # data, failed = scan_nifty500_robust('test_symbols.csv', batch_size=5)

    # Full scan:
    data, failed = scan_nifty500_robust('nifty500_symbols.csv', batch_size=10)

    if data:
        logger.info(f"\n✓ Successfully fetched data for {len(data)} stocks")
        logger.info("You can now proceed with your analysis...")
