#!/usr/bin/env python3
"""
Risk Management and Position Sizing
Based on Robert Miner's methodology
"""

import logging

logger = logging.getLogger(__name__)

def calculate_position_size(account_size, risk_per_share, max_risk_pct=0.03):
    """
    Calculate position size based on account risk

    Formula: Position Size = (Account Ã— Risk%) / Risk per Share

    Args:
        account_size: Total account equity
        risk_per_share: Distance between entry and stop
        max_risk_pct: Maximum risk as decimal (default 3%)

    Returns:
        int: Number of shares to trade
    """
    try:
        if risk_per_share <= 0:
            logger.warning(""Invalid risk_per_share, returning 0"")
            return 0

        max_risk_amount = account_size * max_risk_pct
        position_size = int(max_risk_amount / risk_per_share)

        # Ensure minimum of 1 share
        position_size = max(1, position_size)

        return position_size

    except Exception as e:
        logger.error(f""Error calculating position size: {e}"")
        return 0

def validate_risk_limits(positions, config):
    """
    Validate that total portfolio risk doesn't exceed limits

    Args:
        positions: List of position dicts with 'total_risk'
        config: Configuration dict with risk limits

    Returns:
        tuple: (bool: valid, float: total_risk_pct)
    """
    try:
        total_risk = sum(pos.get('total_risk', 0) for pos in positions)
        account_size = config['trading']['default_account_size']
        max_total_risk = config['trading']['max_total_risk']

        total_risk_pct = total_risk / account_size

        is_valid = total_risk_pct <= max_total_risk

        return is_valid, total_risk_pct

    except Exception as e:
        logger.error(f""Error validating risk limits: {e}"")
        return False, 0.0

def calculate_reward_risk_ratio(entry, stop, target):
    """
    Calculate reward-to-risk ratio

    Args:
        entry: Entry price
        stop: Stop loss price
        target: Target price

    Returns:
        float: Reward/Risk ratio
    """
    try:
        risk = abs(entry - stop)
        reward = abs(target - entry)

        if risk <= 0:
            return 0.0

        return round(reward / risk, 2)

    except Exception as e:
        logger.error(f""Error calculating R:R ratio: {e}"")
        return 0.0
