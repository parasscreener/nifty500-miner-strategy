#!/usr/bin/env python3
"""
Fibonacci Price and Time Calculations
Based on Robert Miner's methodology
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_fib_levels(high, low, config):
    """"""
    Calculate Fibonacci retracement and extension levels

    Args:
        high: Recent high price
        low: Recent low price
        config: Fibonacci configuration dict

    Returns:
        dict: Fibonacci levels
    """"""
    try:
        diff = high - low

        levels = {
            'high': round(high, 2),
            'low': round(low, 2),
            'range': round(diff, 2)
        }

        # Internal retracements (corrections)
        levels['retracements'] = {}
        for ratio in config['internal_retracements']:
            level_price = high - (diff * ratio)
            levels['retracements'][f'{ratio*100:.1f}%'] = round(level_price, 2)

        # External retracements (extensions)
        levels['extensions'] = {}
        for ratio in config['external_retracements']:
            level_price = high - (diff * ratio)
            levels['extensions'][f'{ratio*100:.1f}%'] = round(level_price, 2)

        # Alternate Price Projections
        levels['projections'] = {}
        for ratio in config['projections']:
            proj_price = low + (diff * ratio)
            levels['projections'][f'{ratio*100:.1f}%'] = round(proj_price, 2)

        return levels

    except Exception as e:
        logger.error(f""Error calculating Fibonacci levels: {e}"")
        return {}

def find_confluence_zones(fib_levels, tolerance=0.02):
    """"""
    Find price zones where multiple Fibonacci levels converge

    Args:
        fib_levels: Dict of Fibonacci levels
        tolerance: Price tolerance as percentage (default 2%)

    Returns:
        list: Confluence zones with price and count
    """"""
    try:
        all_levels = []

        # Collect all price levels
        if 'retracements' in fib_levels:
            all_levels.extend(fib_levels['retracements'].values())
        if 'extensions' in fib_levels:
            all_levels.extend(fib_levels['extensions'].values())
        if 'projections' in fib_levels:
            all_levels.extend(fib_levels['projections'].values())

        if not all_levels:
            return []

        all_levels.sort()
        confluence_zones = []

        # Find clusters of levels
        for i, price in enumerate(all_levels):
            nearby = [p for p in all_levels if abs(p - price) / price <= tolerance]
            if len(nearby) >= 2:  # At least 2 levels close together
                avg_price = sum(nearby) / len(nearby)
                confluence_zones.append({
                    'price': round(avg_price, 2),
                    'count': len(nearby),
                    'levels': nearby
                })

        # Remove duplicates
        unique_zones = []
        for zone in confluence_zones:
            if not any(abs(zone['price'] - z['price']) / z['price'] < tolerance 
                      for z in unique_zones):
                unique_zones.append(zone)

        # Sort by confluence strength
        unique_zones.sort(key=lambda x: x['count'], reverse=True)

        return unique_zones

    except Exception as e:
        logger.error(f""Error finding confluence zones: {e}"")
        return []

def calculate_time_projections(data, swing_points):
    """"""
    Calculate time-based Fibonacci projections

    Args:
        data: Price DataFrame with DatetimeIndex
        swing_points: List of swing point dictionaries

    Returns:
        dict: Time projection dates
    """"""
    try:
        if len(swing_points) < 2:
            return {}

        # Get last two swings
        swing1 = swing_points[-2]
        swing2 = swing_points[-1]

        # Calculate time duration
        time_diff = (swing2['date'] - swing1['date']).days

        # Project forward using Fibonacci ratios
        projections = {}
        fib_ratios = [0.382, 0.5, 0.618, 1.0, 1.618]

        for ratio in fib_ratios:
            days_forward = int(time_diff * ratio)
            proj_date = swing2['date'] + pd.Timedelta(days=days_forward)
            projections[f'{ratio*100:.1f}%'] = proj_date.strftime('%Y-%m-%d')

        return projections

    except Exception as e:
        logger.error(f""Error calculating time projections: {e}"")
        return {}
