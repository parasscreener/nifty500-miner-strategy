#!/usr/bin/env python3
"""
Email Report Generator and Sender
Sends formatted HTML email with trading signals
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def send_email_report(results, config):
    """
    Generate and send email report with trading signals

    Args:
        results: Scan results dict
        config: Configuration dict
    """
    try:
        # Get email credentials from environment
        sender_email = os.environ.get('EMAIL_USER')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        recipient_email = os.environ.get('RECIPIENT_EMAIL', 'paras.m.parmar@gmail.com')

        if not sender_email or not sender_password:
            logger.error("Email credentials not found in environment variables")
            return False

        # Generate HTML content
        html_content = generate_html_report(results, config)

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Miner Strategy Report - {results['scan_date'].strftime('%B %d, %Y')}"
        msg['From'] = f"{config['email']['sender_name']} <{sender_email}>"
        msg['To'] = recipient_email

        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(config['email']['smtp_server'], config['email']['smtp_port']) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def generate_html_report(results, config):
    """
    Generate HTML formatted email report

    Returns:
        str: HTML content
    """

    bullish = results.get('bullish_setups', [])
    bearish = results.get('bearish_setups', [])
    scan_date = results['scan_date'].strftime('%B %d, %Y at %I:%M %p IST')

    html = f""""""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 20px; text-align: center; }}
        .summary {{ background: #f4f4f4; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .summary-stats {{ display: flex; justify-content: space-around; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .stat-label {{ font-size: 14px; color: #666; }}
        .section {{ margin: 30px 0; }}
        .section-title {{ color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .setup-card {{ background: white; border: 1px solid #ddd; border-radius: 5px; 
                      padding: 15px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .setup-header {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
        .long {{ border-left: 4px solid #10b981; }}
        .short {{ border-left: 4px solid #ef4444; }}
        .metrics {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
        .metric {{ background: #f9f9f9; padding: 8px; border-radius: 3px; }}
        .metric-label {{ font-size: 12px; color: #666; }}
        .metric-value {{ font-size: 16px; font-weight: bold; }}
        .disclaimer {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; 
                      margin-top: 30px; border-radius: 5px; font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th {{ background: #667eea; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <div class=""header"">
        <h1>ðŸŽ¯ Miner Strategy Trading Report</h1>
        <p>{scan_date}</p>
    </div>

    <div class=""summary"">
        <div class=""summary-stats"">
            <div class=""stat"">
                <div class=""stat-value"">{results['total_scanned']}</div>
                <div class=""stat-label"">Stocks Scanned</div>
            </div>
            <div class=""stat"">
                <div class=""stat-value"" style=""color: #10b981;"">{len(bullish)}</div>
                <div class=""stat-label"">Bullish Setups</div>
            </div>
            <div class=""stat"">
                <div class=""stat-value"" style=""color: #ef4444;"">{len(bearish)}</div>
                <div class=""stat-label"">Bearish Setups</div>
            </div>
        </div>
    </div>
""""
    # Bullish Setups Section
    if bullish:
        html += """"""
    <div class=""section"">
        <h2 class=""section-title"">ðŸ“ˆ Top Bullish Opportunities</h2>
"""
        for i, setup in enumerate(bullish[:5], 1):
            html += generate_setup_card(setup, 'LONG', i)

        html += """"""
    </div>
"""

    # Bearish Setups Section
    if bearish:
        html += """"""
    <div class=""section"">
        <h2 class=""section-title"">ðŸ“‰ Top Bearish Opportunities</h2>
""""
    for i, setup in enumerate(bearish[:5], 1):
            html += generate_setup_card(setup, 'SHORT', i)

        html += """"""
    </div>
"""

    # Disclaimer
    html += """"""
    <div class=""disclaimer"">
        <strong>âš ï¸ DISCLAIMER:</strong> This report is for educational purposes only and does not 
        constitute financial advice. Trading involves substantial risk of loss. Past performance 
        does not guarantee future results. Always consult with a qualified financial advisor and 
        do your own research before making any trading decisions.
    </div>

    <div style=""text-align: center; margin-top: 30px; color: #666; font-size: 12px;"">
        <p>Generated by Miner Strategy Scanner</p>
        <p>Based on Robert C. Miner's High Probability Trading Strategies</p>
    </div>
</body>
</html>
""""""

    return html

def generate_setup_card(setup, direction, rank):
    """"""Generate HTML for individual setup card""""""

    card_class = 'long' if direction == 'LONG' else 'short'
    direction_emoji = 'ðŸŸ¢' if direction == 'LONG' else 'ðŸ”´'

    backtest = setup.get('backtest', {})
    bt_summary = f""""""
        Win Rate: {backtest.get('win_rate', 0)}% | 
        Sharpe: {backtest.get('sharpe_ratio', 0)} | 
        Max DD: {backtest.get('max_drawdown', 0)}%
    """""" if backtest else ""No backtest data""

    html = f""""""
    <div class=""setup-card {card_class}"">
        <div class=""setup-header"">
            {direction_emoji} #{rank} {setup['symbol'].replace('.NS', '')} - {direction}
        </div>

        <div class=""metrics"">
            <div class=""metric"">
                <div class=""metric-label"">Current Price</div>
                <div class=""metric-value"">â‚¹{setup['current_price']}</div>
            </div>
            <div class=""metric"">
                <div class=""metric-label"">Entry Price</div>
                <div class=""metric-value"">â‚¹{setup['entry']}</div>
            </div>
            <div class=""metric"">
                <div class=""metric-label"">Stop Loss</div>
                <div class=""metric-value"">â‚¹{setup['stop']}</div>
            </div>
            <div class=""metric"">
                <div class=""metric-label"">Position Size (3% risk)</div>
                <div class=""metric-value"">{setup['position_size']} shares</div>
            </div>
        </div>

        <p><strong>Daily Momentum:</strong> Stoch {setup['daily_stoch']}, RSI {setup['daily_rsi']}, MACD {setup['daily_macd']}</p>
        <p><strong>Pattern:</strong> {setup.get('pattern', {}).get('pattern', 'N/A')}</p>
        <p><strong>10Y Backtest:</strong> {bt_summary}</p>
        <p><strong>Risk:</strong> â‚¹{setup['total_risk']} ({(setup['total_risk']/1000000*100):.2f}% of â‚¹10L account)</p>
    </div>
"""

    return html
