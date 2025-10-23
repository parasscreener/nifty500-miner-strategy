# Robert Miner High Probability Trading Strategy - Nifty 500

## ðŸŽ¯ Overview

Automated trading strategy scanner implementing **Robert C. Miner's High Probability Trading Strategies** for the Indian Nifty 500 stock universe. Runs daily via GitHub Actions and emails detailed reports.

## ðŸŒŸ Key Features

âœ… **Dual Time Frame Momentum Analysis** (Daily + 60-minute)  
âœ… **Automated Daily Scans** at 9:30 AM IST  
âœ… **10-Year Backtesting** for validation  
âœ… **Email Reports** with actionable setups  
âœ… **Pattern Recognition** (Elliott Wave)  
âœ… **Fibonacci Price & Time Projections**  
âœ… **Systematic Risk Management** (3% per trade)  
âœ… **Free Deployment** (GitHub Actions)  

## ðŸ“Š Strategy Components

### 1. Dual Time Frame Momentum
- **Larger Timeframe (Daily)**: Identifies overall trend direction
- **Smaller Timeframe (60-min)**: Provides precise entry/exit signals

### 2. Technical Indicators
- **Stochastic Oscillator**: 14-3-3 (OB: 80, OS: 20)
- **RSI**: 14-period (OB: 70, OS: 30)
- **MACD**: 12-26-9 (Momentum confirmation)

### 3. Entry Rules

#### Long Setup
- Daily: Stoch > 50, RSI > 50, MACD > Signal (not OB)
- 60-min: Stoch crosses above 20 + MACD bullish cross
- Price at 50-61.8% Fibonacci support

#### Short Setup
- Daily: Stoch < 50, RSI < 50, MACD < Signal (not OS)
- 60-min: Stoch crosses below 80 + MACD bearish cross
- Price at resistance zone

### 4. Risk Management
- Max risk per trade: **3%** of account
- Max total portfolio risk: **6%**
- Position sizing: (Account Ã— 3%) / (Entry - Stop)

## ðŸš€ Quick Start

### Prerequisites
- GitHub account
- Gmail account for notifications

### Setup (5 minutes)

1. **Fork/Clone this repository**
```bash
git clone https://github.com/YOUR_USERNAME/nifty500-miner-strategy.git
cd nifty500-miner-strategy
```

2. **Configure GitHub Secrets**

Go to: Repository â†’ Settings â†’ Secrets and variables â†’ Actions

Add two secrets:
- `EMAIL_USER`: Your Gmail address
- `EMAIL_PASSWORD`: Gmail App-specific password

**How to get Gmail App Password:**
1. Google Account â†’ Security
2. Enable 2-Step Verification
3. Search ""App passwords""
4. Create password for ""Mail""
5. Copy 16-character code

3. **Enable GitHub Actions**

Go to: Actions tab â†’ Enable workflows

4. **Test Run**

Actions â†’ ""Nifty 500 Miner Strategy Scanner"" â†’ Run workflow

âœ… Done! You'll receive daily emails at 9:30 AM IST.

## ðŸ“ Project Structure

```
nifty500-miner-strategy/
â”œâ”€â”€ .github/
â”‚   â””â”€â”€ workflows/
â”‚       â””â”€â”€ daily_scan.yml          # GitHub Actions workflow
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ strategy_scanner.py         # Main orchestrator
â”‚   â”œâ”€â”€ indicators.py               # Technical indicators
â”‚   â”œâ”€â”€ pattern_recognition.py      # Elliott Wave analysis
â”‚   â”œâ”€â”€ fibonacci.py                # Fib calculations
â”‚   â”œâ”€â”€ risk_management.py          # Position sizing
â”‚   â”œâ”€â”€ backtester.py               # Backtesting engine
â”‚   â””â”€â”€ email_notifier.py           # Email reports
â”œâ”€â”€ config/
â”‚   â””â”€â”€ config.yaml                 # Configuration
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ nifty500_symbols.csv        # Stock universe
â”‚   â””â”€â”€ cache/                      # Cached data
â”œâ”€â”€ results/                        # Scan results
â”œâ”€â”€ logs/                           # Execution logs
â”œâ”€â”€ requirements.txt                # Dependencies
â””â”€â”€ README.md                       # This file
```

## ðŸ“§ Email Report Contents

Each daily report includes:

1. **Executive Summary**
   - Total stocks scanned
   - Number of setups found
   - Market conditions

2. **Top 5 Bullish Setups**
   - Entry/stop/target prices
   - Position size for 3% risk
   - 10-year backtest results
   - Pattern analysis

3. **Top 5 Bearish Setups**
   - Similar details as bullish

4. **Performance Metrics**
   - Win rate, Sharpe ratio
   - Maximum drawdown
   - Profit factor

## ðŸ”§ Configuration

Edit `config/config.yaml` to customize:

```yaml
trading:
  max_risk_per_trade: 0.03  # 3%
  max_total_risk: 0.06      # 6%
  default_account_size: 1000000  # â‚¹10 Lakhs

indicators:
  stochastic:
    period: 14
    overbought: 80
    oversold: 20
```

## ðŸ“ˆ Backtesting

The system backtests each strategy over 10 years (2015-2025) and calculates:

- Total Returns
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Profit Factor
- Average Win/Loss Ratio

## âš™ï¸ Manual Testing

Test locally before deployment:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export EMAIL_USER=""your.email@gmail.com""
export EMAIL_PASSWORD=""your-app-password""
export RECIPIENT_EMAIL=""paras.m.parmar@gmail.com""

# Run scanner
python src/strategy_scanner.py
```

## ðŸ” Troubleshooting

### Workflow not running?
- Verify cron time (4:00 AM UTC = 9:30 AM IST)
- Check Actions tab for errors
- Manually trigger to test

### No email received?
- Verify GitHub Secrets configured
- Check Gmail App Password (not regular password)
- Review logs in Actions

### Data download issues?
- NSE stocks need `.NS` suffix
- yfinance may have rate limits
- Cache is used to minimize API calls

## ðŸ“š Resources

- **Book**: ""High Probability Trading Strategies"" by Robert C. Miner
- **Data Source**: Yahoo Finance (yfinance)
- **Universe**: Nifty 500 Index stocks

## âš ï¸ Disclaimer

**FOR EDUCATIONAL PURPOSES ONLY**

This system does NOT constitute financial advice. Trading involves substantial risk of loss. Past performance does not guarantee future results. Users must:

- Understand all risks involved
- Consult qualified financial advisors
- Comply with SEBI regulations
- Start with paper trading
- Never risk more than they can afford to lose

## ðŸ“„ License

MIT License - See LICENSE file

## ðŸ¤ Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Submit pull request

## ðŸ“ž Support

For issues:
1. Check existing GitHub Issues
2. Create new issue with details
3. Include error logs

---

**Developed based on Robert C. Miner's methodology**  
**Adapted for Indian markets (Nifty 500)**  

â­ Star this repo if you find it useful!

Last Updated: October 2025
