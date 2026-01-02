# Quick Start Guide

## Step 1: Installation (5 minutes)

1. **Get a Massive (Polygon.io) API Key**
   - Go to https://polygon.io/
   - Sign up for free (or paid plan for historical data)
   - Copy your API key

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   - Copy `.env.example` to `.env`
   - Replace `your_polygon_api_key_here` with your actual API key
   ```
   MASSIVE_API_KEY=pk_your_actual_key_here
   ```

## Step 2: Run Your First Backtest (5 minutes)

1. **Launch the Application**
   ```bash
   python options_backtester.py
   ```

2. **Select Stocks**
   - Click "TOP 50 BY MARKET CAP" for a quick test
   - Or search for specific stocks like "AAPL", "TSLA", "SPY"
   - Click "NEXT: CONFIGURE OPTIONS STRATEGY →"

3. **Configure Strategy**
   - Select "Iron Condor" from dropdown
   - Keep default parameters for first test:
     - DTE: 30,45 days
     - Short Delta: 0.10,0.20
     - Spread Width: 5,10
   - Set date range: 2024-01-01 to 2024-12-31
   - Click "RUN BACKTEST 🚀"

4. **View Results**
   - Equity Curve tab shows visual performance
   - Analysis tab shows all trades
   - Double-click any trade for full details

## Step 3: Customize Your Strategy (10 minutes)

### Try Different Strategies

**For Bullish Market:**
```
Strategy: Bull Call Spread
DTE: 30,60
Long Strike Delta: 0.50
Short Strike Delta: 0.30
Max Debit: $300
```

**For Income:**
```
Strategy: Iron Condor
DTE: 30,45
Short Delta Range: 0.15,0.25
Spread Width: 10
Min Credit Ratio: 0.30
Stop Loss: 50%
Profit Target: 50%
```

**For Volatility:**
```
Strategy: Long Straddle
DTE: 30,45
Strike Selection: ATM
Max Premium: $1000
Use Technical Indicators: Yes
RSI Threshold: 40,60
```

### Add Technical Filters

1. Set "Use Technical Indicators" to "Yes"
2. Configure:
   - RSI Threshold: 30,70 (buy when oversold)
   - SMA Cross: 20,50 (trend confirmation)
   - Bollinger Bands: Yes (volatility)

### Risk Management

Enable these for better risk control:
- ✅ Stop Loss: 50% (exit if down 50%)
- ✅ Profit Target: 50% (exit if up 50%)
- ✅ Trailing Stop: 25% (lock in profits)

## Step 4: Analyze Results

### Key Metrics to Watch

1. **Win Rate**: Should be 50-70% for credit strategies
2. **Profit Factor**: Should be > 1.5
3. **Max Drawdown**: Keep under 20%
4. **Sharpe Ratio**: Higher is better (> 1.0 is good)

### Export and Share

- Click "Export to CSV" in Analysis tab
- Share results with team
- Import into Excel for further analysis

## Common Starting Strategies

### Conservative Income (Iron Condor)
```
Stock Selection: SPY, QQQ, IWM (index ETFs)
DTE: 30,45
Short Delta: 0.10,0.15 (far OTM)
Spread Width: 10
Min Credit Ratio: 0.25
Stop Loss: 50%
Max Trades/Day: 1
```
Expected: 60-70% win rate, steady income

### Aggressive Directional (Long Call)
```
Stock Selection: High growth stocks (NVDA, TSLA, etc.)
DTE: 30,60
Strike: delta:0.60 (slightly ITM)
Max Premium: $500
Use Indicators: Yes
RSI: 30,70
Stop Loss: 40%
Profit Target: 100%
```
Expected: 40-50% win rate, larger wins

### Volatility Play (Straddle)
```
Stock Selection: Stocks with earnings
DTE: 7,14 (near-term)
Strike: ATM
Max Premium: $1000
Exit: Before expiration (day of earnings)
```
Expected: High risk, high reward

## Tips for Better Results

1. **Start Small**
   - Test with 5-10 stocks first
   - Use shorter date ranges (3-6 months)
   - Single strategy at a time

2. **Focus on Liquid Options**
   - Min Volume: 50+
   - Min Open Interest: 100+
   - Max Spread: 5%

3. **Use Realistic Parameters**
   - Don't overfit to past data
   - Test multiple time periods
   - Compare to buy-and-hold

4. **Risk Management is Key**
   - Always use stop losses
   - Don't risk more than 2% per trade
   - Diversify across symbols

5. **Iterate and Improve**
   - Try different DTE ranges
   - Test various delta selections
   - Compare strategies side-by-side

## Troubleshooting

**No trades generated?**
- Loosen liquidity filters (lower volume/OI)
- Widen delta ranges
- Expand DTE range
- Check date range includes trading days

**Backtest running slow?**
- Reduce number of stocks (start with 10)
- Shorten date range
- Limit max trades per day

**API errors?**
- Verify API key in .env file
- Check API quota/limits
- Ensure stable internet connection

## Next Steps

1. **Compare Strategies**
   - Run same stocks through multiple strategies
   - Compare results side-by-side
   - Find what works best for your risk tolerance

2. **Optimize Parameters**
   - Try different DTE ranges
   - Test various delta selections
   - Experiment with stop loss levels

3. **Build Your Portfolio**
   - Combine multiple strategies
   - Diversify across sectors
   - Balance risk/reward

4. **Paper Trade**
   - Test your best strategy in real-time
   - Track actual vs. predicted results
   - Refine before live trading

## Resources

- Massive API Docs: https://polygon.io/docs
- Options Education: https://www.optionseducation.org/
- Python pandas: https://pandas.pydata.org/docs/

---

**Remember:** This is a backtesting tool. Historical results don't guarantee future performance. Always practice with paper trading before risking real capital!
