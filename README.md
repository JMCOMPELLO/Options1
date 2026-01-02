# Advanced Options Strategy Backtester

A comprehensive options backtesting platform using Massive API (Polygon.io) for historical options data. Supports 20+ options strategies with advanced risk management, technical indicators, and detailed performance analytics.

## 🚀 Features

### Supported Strategies

**🐂 Bullish Strategies:**
- Long Call
- Cash-Secured Put
- Bull Call Spread
- Bull Put Spread
- Call Diagonal Spread
- Call Ratio Backspread

**🐻 Bearish Strategies:**
- Long Put
- Bear Put Spread
- Bear Call Spread
- Put Ratio Backspread

**⚖️ Neutral/Income Strategies:**
- Covered Call
- Protective Put
- Collar
- Iron Condor ⭐
- Iron Butterfly
- Short Strangle
- Short Straddle

**🔀 Volatility Strategies:**
- Long Straddle
- Long Strangle
- Calendar Spread

### Advanced Features

✅ **Risk Management**
- Stop Loss (% of max loss)
- Profit Targets (% of max profit)
- Trailing Stops
- Position Sizing

✅ **Technical Indicators for Entry Filtering**
- SMA Crossover
- RSI Filter
- MACD Signal
- Bollinger Bands
- Volume Filter
- ATR Filter
- IV Rank Filter
- Momentum

✅ **Greeks Filtering**
- Delta range selection
- Theta minimum
- Vega maximum
- Gamma maximum

✅ **Comprehensive Analytics**
- Equity curve visualization
- Win rate & profit factor
- Maximum drawdown
- Sharpe ratio
- Per-symbol breakdown
- Detailed trade history

## 📋 Prerequisites

1. **Massive API Key** (formerly Polygon.io)
   - Sign up at https://polygon.io/
   - Get your API key from the dashboard

2. **Python 3.9+**

## 🛠️ Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key

Create a `.env` file in the project directory:

```bash
MASSIVE_API_KEY=your_api_key_here
```

### Step 3: Run the Application

```bash
python options_backtest_app.py
```

## 📖 Usage Guide

### 1. Stock Selection Tab

- **Select Stocks**: Choose from S&P 500 universe
- **Bulk Selection**: Select all, by sector, or individual stocks
- **Search**: Filter by ticker, company name, or sector

### 2. Strategy Configuration Tab

#### A. Select Strategy
Choose from 20+ options strategies organized by market outlook (bullish, bearish, neutral, volatility)

#### B. Configure Entry Indicators (Optional)
Enable technical indicators to filter entry signals:
- **SMA Crossover**: Enter when short SMA crosses long SMA
- **RSI Filter**: Only enter when RSI in specified range
- **MACD Signal**: Enter on MACD crossovers
- **IV Rank**: Enter based on implied volatility rank
- And more...

#### C. Set Strategy Parameters
Configure strategy-specific parameters:
- **Delta Ranges**: Target delta for short/long legs
- **IV Rank**: Min/max implied volatility rank
- **Liquidity**: Minimum volume and open interest
- **Spread Width**: Min/max width for spreads
- **Greeks Filters**: Theta, vega, gamma thresholds

#### D. Risk Management
- **Stop Loss**: Exit at X% of max loss
- **Profit Target**: Exit at X% of max profit  
- **Trailing Stop**: Lock in profits
- **DTE Filters**: Min/max days to expiration

#### E. Backtest Configuration
- **Date Range**: Set start and end dates
- **Trading Frequency**: Daily, weekly, monthly, or on signal
- **Position Limits**: Max concurrent positions
- **Capital Allocation**: USD per trade

### 3. Run Backtest

Click "RUN BACKTEST" - the engine will:
1. Fetch historical underlying prices
2. Fetch historical options chains
3. Apply your strategy logic and filters
4. Simulate trades day-by-day
5. Apply risk management rules
6. Calculate comprehensive statistics

### 4. View Results

#### Equity Curve Tab
- Visual equity curve chart
- Performance summary metrics
- Export functionality

#### Detailed Results Tab
- Complete trade history
- Filter by winner/loser/symbol
- Double-click for trade details
- Export to CSV

## 🔧 Configuration Options

### Strategy Parameters

Each strategy has customizable parameters. Example for Iron Condor:

```python
{
  "Delta Range (Short Leg)": "0.20,0.35",  # Target delta for sold options
  "Delta Range (Long Leg)": "0.05,0.15",   # Target delta for protection
  "Min IV Rank": "30",                      # Minimum IV to enter
  "Max IV Rank": "80",                      # Maximum IV to enter
  "Min Open Interest": "100",               # Liquidity requirement
  "Min Volume": "50",                       # Liquidity requirement
  "Spread Width ($)": "5,10",               # Width in dollars
  "Credit/Debit Ratio": "0.25,0.40",       # Credit as % of width
  "Profit Zone Width": "0.10,0.20"         # ±% from current price
}
```

### Risk Management Example

```python
{
  "stop_loss_enabled": True,
  "stop_loss_pct": 50,        # Exit at 50% of max loss
  "profit_target_enabled": True,
  "profit_target_pct": 50,    # Exit at 50% of max profit
  "trailing_stop_enabled": True,
  "trailing_stop_pct": 25     # Trail by 25%
}
```

## 📊 Understanding Results

### Key Metrics

- **Total Trades**: Number of completed trades
- **Win Rate**: Percentage of profitable trades
- **Total P&L**: Cumulative profit/loss
- **Avg P&L**: Average profit/loss per trade
- **Profit Factor**: Avg win / Avg loss
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return metric

### Trade Details

Each trade includes:
- Entry/exit dates and prices
- Days held
- P&L in dollars and percentage
- Exit reason (expiration, stop loss, profit target, etc.)
- Underlying price movement

## 🎯 Backtesting Best Practices

1. **Start Simple**: Begin with basic strategies and add complexity gradually

2. **Sufficient Data**: Use at least 1 year of data for meaningful results

3. **Liquidity Filters**: Always require minimum volume and open interest

4. **Risk Management**: Always use stop losses to limit downside

5. **Diversification**: Test on multiple underlying symbols

6. **Parameter Sensitivity**: Try different parameters to avoid overfitting

7. **Market Conditions**: Test across different volatility regimes

## 🔍 Historical Data Limitations

**Important**: The Massive API provides historical options data, but there are some limitations:

- Historical options chains may have data gaps
- Bid/ask spreads and Greeks might not be available for all dates
- Very old data (5+ years) may be incomplete
- Intraday pricing is available but increases API usage

The backtest engine handles missing data gracefully and will skip dates where data is unavailable.

## 💡 Example Workflows

### Example 1: Conservative Iron Condor Strategy

1. Select: SPY, QQQ (liquid underlyings)
2. Strategy: Iron Condor
3. Parameters:
   - DTE: 30-45 days
   - Delta: 0.15-0.25 (far OTM)
   - Min IV Rank: 40
   - Stop Loss: 50% of max loss
   - Profit Target: 50% of max profit
4. Run backtest over 2 years

### Example 2: Aggressive Bull Call Spread

1. Select: High-growth tech stocks
2. Strategy: Bull Call Spread
3. Indicators: RSI < 40 (oversold)
4. Parameters:
   - DTE: 45-60 days
   - Delta (long): 0.50-0.60
   - Stop Loss: 30% of max loss
5. Run backtest

## 🐛 Troubleshooting

### "API Key Not Found"
- Ensure `.env` file exists in project directory
- Verify `MASSIVE_API_KEY=your_key` format
- No quotes around the key

### "No Trades Generated"
- Loosen your filter criteria
- Expand date range
- Check liquidity requirements aren't too strict
- Verify API key has access to options data

### "Slow Performance"
- Reduce number of symbols
- Shorten date range
- Increase DTE minimum (fewer expirations to check)
- The engine uses concurrent API calls but there are rate limits

## 📝 Saving/Loading Configurations

Click "SAVE CONFIG" to export your strategy configuration as JSON. You can edit and reuse these configurations.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Options trading carries significant risk. Past performance does not guarantee future results. Always do your own research and consider consulting a financial advisor.

## 📧 Support

For Massive API questions: https://polygon.io/docs

## 🔄 Roadmap

- [ ] More strategies (synthetic positions, box spreads, etc.)
- [ ] Options Greeks visualization
- [ ] Monte Carlo simulation
- [ ] Portfolio optimization
- [ ] Live paper trading mode
- [ ] Machine learning signal generation
- [ ] Multi-leg adjustment strategies
- [ ] Commissions and slippage modeling

---

**Version**: 1.0  
**License**: MIT
