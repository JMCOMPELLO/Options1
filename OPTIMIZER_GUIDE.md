# Parameter Optimizer Guide

## Overview
The Parameter Optimizer is a goal-seeking function that automatically tests different combinations of strategy parameters to find the configuration that maximizes your **Total Return %** (Equity Return Total Value %).

## How to Use

### Step 1: Navigate to Strategy Configuration
1. Launch the application
2. Select your stocks from the Stock Selection tab
3. Go to the "Strategy Configuration" tab

### Step 2: Open the Optimizer
Click the **"🎯 OPTIMIZE PARAMETERS"** button at the bottom of the Strategy Configuration page.

### Step 3: Configure Optimization Settings
In the Optimizer window:
- **Number of Combinations**: Use the slider to select how many parameter combinations to test
  - **10-30**: Quick optimization (1-2 minutes)
  - **50-100**: Balanced optimization (3-5 minutes) - **RECOMMENDED**
  - **100-200**: Thorough optimization (5-10 minutes)

### Step 4: Run Optimization
1. Click **"🚀 START OPTIMIZATION"**
2. Watch the progress bar as the optimizer tests different combinations
3. The optimizer will display:
   - Current progress (X/Y combinations tested)
   - Best result found so far
   - Real-time updates in the results window

### Step 5: Review Results
When optimization completes, you'll see:
- **Best Total Return %** achieved
- **All optimized parameters** that produced this result
- **Performance metrics**: win rate, total P&L, profit factor, Sharpe ratio, etc.

### Step 6: Apply Best Parameters
Click **"✓ APPLY BEST PARAMETERS"** to automatically update all strategy settings with the optimal configuration.

### Step 7: Run Backtest
Return to the Strategy Configuration tab and click **"🚀 RUN BACKTEST"** to see the full results with the optimized parameters.

## Parameters That Get Optimized

The optimizer automatically tests different values for:

### Risk Management
- **Stop Loss %**: Exit losing trades at different levels (25%, 50%, 75%, 100%)
- **Profit Target %**: Take profits at different levels (25%, 50%, 75%, 100%)
- **Trailing Stop %**: Trail winners at different levels (15%, 25%, 35%, 50%)

### Days to Expiration
- **Min DTE**: Minimum days before expiration (20, 30, 45, 60)
- **Max DTE**: Maximum days before expiration (45, 60, 75, 90)

### Option Selection
- **Delta Ranges**: Both short and long leg delta targets
- **IV Rank Range**: Implied volatility rank filters (min/max)
- **Liquidity Filters**: Minimum open interest and volume requirements

### Position Management
- **Max Concurrent Positions**: How many trades to hold at once (5, 10, 15, 20)
- **Capital per Trade**: Investment amount per position ($500, $1000, $2000, $5000)

## How It Works

### Optimization Algorithm
1. **Smart Sampling**: Instead of testing every possible combination (which could be millions), the optimizer:
   - Tests all combinations of critical parameters (stop loss, profit target, DTE)
   - Randomly samples other parameters to create diverse test scenarios
   - Ensures parameter constraints are maintained (e.g., min < max)

2. **Backtesting**: For each parameter combination:
   - Applies the parameters to your strategy
   - Runs a full backtest simulation
   - Calculates the Total Return %
   - Tracks all performance metrics

3. **Goal Seeking**:
   - Compares each result
   - Keeps track of the best performing combination
   - Returns the parameters that maximize Total Return %

### Total Return Calculation
```
Total Return % = (Total P&L / Starting Capital) × 100
```
- Starting Capital: $20,000 (default)
- Total P&L: Sum of all trade profits and losses
- Example: $3,000 profit on $20,000 = 15% total return

## Tips for Best Results

### 1. Start with Reasonable Strategy Settings
Before optimizing:
- Select a proven options strategy (Iron Condor, Bull Put Spread, etc.)
- Choose appropriate stocks/tickers
- Set a reasonable date range (at least 1 year of data)

### 2. Use Balanced Optimization (50-100 combinations)
- Too few (< 30): May miss optimal settings
- Too many (> 150): Diminishing returns, takes longer
- Sweet spot: 50-100 combinations

### 3. Consider Your Trading Style
After optimization, review the suggested parameters:
- **Aggressive traders**: Lower stop losses, higher position sizes
- **Conservative traders**: May want to adjust optimized values to be more defensive
- **Income traders**: Focus on results with higher win rates

### 4. Validate Results
- After applying optimized parameters, review the full backtest
- Check if the win rate and risk/reward align with your goals
- Consider running optimization multiple times to confirm consistency

### 5. Indicator Impact
- Enabled indicators improve trade quality (win rate) but don't reduce trade quantity
- The optimizer works with whatever indicators you have enabled
- Each indicator adds ~4% to win rate in the optimization

## Understanding the Results

### Key Metrics to Watch
- **Total Return %**: Primary optimization goal - higher is better
- **Win Rate**: Should be > 50% for most strategies
- **Profit Factor**: Ratio of wins to losses - > 1.5 is good
- **Max Drawdown**: Largest peak-to-trough decline - lower is better
- **Sharpe Ratio**: Risk-adjusted return - > 1.0 is good, > 2.0 is excellent

### Interpreting Parameter Recommendations
- **High Stop Loss %**: Strategy tolerates more loss before exiting
- **Low Profit Target %**: Takes profits quickly (scalping approach)
- **High DTE Range**: Prefers longer-dated options
- **Low Delta**: Prefers far out-of-the-money options

## Advanced Usage

### Refining Optimization
If you want even better results:
1. Run initial optimization (50 combinations)
2. Note the best parameter ranges
3. Manually adjust the `get_parameter_ranges()` in `optimizer.py` to focus on those ranges
4. Run optimization again with narrower ranges

### Comparing Strategies
1. Optimize parameters for Strategy A
2. Note the best Total Return %
3. Switch to Strategy B
4. Optimize again
5. Compare results to see which strategy performs better

### Multi-Indicator Optimization
1. Enable different combinations of indicators
2. Run optimization for each indicator set
3. Compare which indicator combinations produce the best results

## Troubleshooting

### "No trades generated"
- Date range may be too short
- Parameters may be too restrictive
- Try with fewer indicators or looser parameter ranges

### Optimization is slow
- Reduce number of combinations
- Close other applications to free up CPU
- Consider running overnight for 150+ combinations

### Results seem inconsistent
- Add more combinations for more robust results
- Ensure you have enough historical data (1+ year)
- Check that your stock selection includes liquid symbols

## Example Workflow

Here's a complete example:

1. **Select Stocks**: Choose 5-10 liquid stocks (SPY, QQQ, AAPL, etc.)
2. **Choose Strategy**: Iron Condor
3. **Enable Indicators**: RSI Filter + IV Rank Filter
4. **Set Date Range**: 2023-01-01 to 2024-12-31
5. **Open Optimizer**: Click "🎯 OPTIMIZE PARAMETERS"
6. **Set Combinations**: 75 (balanced approach)
7. **Start**: Click "🚀 START OPTIMIZATION"
8. **Wait**: ~4 minutes
9. **Review**: Best result: 18.5% total return
10. **Apply**: Click "✓ APPLY BEST PARAMETERS"
11. **Backtest**: Run full backtest to see trade details
12. **Analyze**: Review equity curve and individual trades

## Technical Details

### File Location
- Module: `/Users/jkm/Desktop/Options 1/optimizer.py`
- Integration: `/Users/jkm/Desktop/Options 1/tab_strategy_config.py`

### Dependencies
- Uses existing backtest engine
- Leverages `generate_indicator_filtered_backtest()` method
- Thread-based execution for responsive UI

### Customization
To customize the optimizer, edit `optimizer.py`:
- `get_parameter_ranges()`: Modify parameter ranges to test
- `create_parameter_combinations()`: Change sampling strategy
- `max_combinations`: Default is 100, can be adjusted

---

**Happy optimizing! May your Total Returns be ever increasing! 📈🎯**
