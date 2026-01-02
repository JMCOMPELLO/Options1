#!/usr/bin/env python3
"""
Options Backtesting Engine
Uses Massive API for historical options chains and pricing
"""

from massive import RESTClient
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional, Callable
import pandas as pd
import numpy as np
from dataclasses import dataclass
import concurrent.futures
import time as time_module

ET = ZoneInfo("America/New_York")

@dataclass
class OptionsPosition:
    """Represents an options position"""
    symbol: str
    strategy: str
    entry_date: datetime
    expiration_date: datetime
    legs: List[Dict]  # List of option legs
    entry_cost: float
    max_profit: float
    max_loss: float
    current_pnl: float = 0.0
    exit_date: Optional[datetime] = None
    exit_reason: Optional[str] = None
    underlying_entry_price: float = 0.0
    underlying_exit_price: Optional[float] = None
    days_held: int = 0

class OptionsBacktestEngine:
    def __init__(self, api_key: str, tickers: List[str], config: Dict, 
                 progress_callback: Optional[Callable] = None):
        """
        Initialize the options backtesting engine
        
        Args:
            api_key: Massive API key
            tickers: List of ticker symbols to backtest
            config: Configuration dictionary from UI
            progress_callback: Optional callback for progress updates
        """
        self.client = RESTClient(api_key=api_key)
        self.tickers = tickers
        self.config = config
        self.progress_callback = progress_callback
        
        # Parse config
        self.strategy = config['strategy']
        self.start_date = datetime.strptime(config['start_date'], "%Y-%m-%d").replace(tzinfo=ET)
        self.end_date = datetime.strptime(config['end_date'], "%Y-%m-%d").replace(tzinfo=ET)
        self.min_dte = config['min_dte']
        self.max_dte = config['max_dte']
        self.max_positions = config['max_positions']
        self.capital_per_trade = config['capital_per_trade']
        
        # Risk management
        self.risk_config = config['risk_management']
        
        # Parameters
        self.params = config['parameters']
        
        # Indicators
        self.indicators = config['indicators']
        
        # Results storage
        self.all_trades = []
        self.open_positions = []
        self.closed_positions = []
        
    def log(self, message: str):
        """Log progress"""
        if self.progress_callback:
            self.progress_callback(message)
        print(f"[BACKTEST] {message}")
    
    def run_backtest(self) -> Dict:
        """
        Run the complete backtest
        
        Returns:
            Dictionary with trades and statistics
        """
        self.log(f"Starting backtest: {self.strategy}")
        self.log(f"Period: {self.start_date.date()} to {self.end_date.date()}")
        self.log(f"Tickers: {len(self.tickers)} symbols")
        
        # Generate trading days
        trading_days = self.generate_trading_days()
        self.log(f"Total trading days: {len(trading_days)}")
        
        # Run day-by-day simulation
        for idx, current_date in enumerate(trading_days):
            if idx % 20 == 0:
                self.log(f"Processing: {current_date.date()} ({idx+1}/{len(trading_days)}) - "
                        f"Positions: {len(self.open_positions)}, Trades: {len(self.all_trades)}")
            
            # Update existing positions
            self.update_positions(current_date)
            
            # Check for new entry signals
            if len(self.open_positions) < self.max_positions:
                self.check_entry_signals(current_date)
        
        # Close any remaining positions at backtest end
        self.close_all_positions(self.end_date)
        
        # Calculate statistics
        results = self.calculate_results()
        
        self.log(f"✓ Backtest complete! {len(self.all_trades)} total trades")
        
        return results
    
    def generate_trading_days(self) -> List[datetime]:
        """Generate list of trading days in the backtest period"""
        days = []
        current = self.start_date
        
        while current <= self.end_date:
            # Skip weekends
            if current.weekday() < 5:  # Monday = 0, Sunday = 6
                days.append(current)
            current += timedelta(days=1)
        
        return days
    
    def update_positions(self, current_date: datetime):
        """Update all open positions - check for exits"""
        positions_to_close = []
        
        for position in self.open_positions:
            # Check if expired
            if current_date.date() >= position.expiration_date.date():
                positions_to_close.append((position, "Expiration"))
                continue
            
            # Get current option prices
            try:
                current_value = self.get_position_value(position, current_date)
                position.current_pnl = current_value - position.entry_cost
                position.days_held = (current_date - position.entry_date).days
                
                # Check stop loss
                if self.risk_config['stop_loss_enabled']:
                    stop_loss_threshold = -position.max_loss * (self.risk_config['stop_loss_pct'] / 100.0)
                    if position.current_pnl <= stop_loss_threshold:
                        positions_to_close.append((position, "Stop Loss"))
                        continue
                
                # Check profit target
                if self.risk_config['profit_target_enabled']:
                    profit_target = position.max_profit * (self.risk_config['profit_target_pct'] / 100.0)
                    if position.current_pnl >= profit_target:
                        positions_to_close.append((position, "Profit Target"))
                        continue
                
                # Check trailing stop
                if self.risk_config['trailing_stop_enabled']:
                    # Implementation would track high water mark
                    pass
                
            except Exception as e:
                print(f"Error updating position for {position.symbol}: {e}")
                continue
        
        # Close positions
        for position, reason in positions_to_close:
            self.close_position(position, current_date, reason)
    
    def check_entry_signals(self, current_date: datetime):
        """Check for new entry signals across all tickers"""
        # Limit concurrent API calls
        max_workers = min(5, len(self.tickers))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {
                executor.submit(self.check_ticker_entry, ticker, current_date): ticker
                for ticker in self.tickers
            }
            
            for future in concurrent.futures.as_completed(future_to_ticker):
                try:
                    position = future.result()
                    if position:
                        self.open_positions.append(position)
                        self.log(f"Opened {position.strategy} on {position.symbol}")
                except Exception as e:
                    ticker = future_to_ticker[future]
                    print(f"Error checking {ticker}: {e}")
    
    def check_ticker_entry(self, ticker: str, current_date: datetime) -> Optional[OptionsPosition]:
        """
        Check if we should enter a position on this ticker
        
        Returns:
            OptionsPosition if entry signal triggered, else None
        """
        # Don't enter if we already have a position on this ticker
        if any(p.symbol == ticker for p in self.open_positions):
            return None
        
        # Get underlying price
        try:
            underlying_price = self.get_underlying_price(ticker, current_date)
            if not underlying_price:
                return None
        except Exception as e:
            print(f"Could not get price for {ticker}: {e}")
            return None
        
        # Check technical indicators if enabled
        if not self.check_indicators(ticker, current_date, underlying_price):
            return None
        
        # Get options chain for this date
        try:
            options_chain = self.get_historical_options_chain(ticker, current_date)
            if not options_chain:
                return None
        except Exception as e:
            print(f"Could not get options chain for {ticker}: {e}")
            return None
        
        # Find suitable options based on strategy
        position = self.construct_position(
            ticker, 
            current_date, 
            underlying_price, 
            options_chain
        )
        
        return position
    
    def get_underlying_price(self, ticker: str, date: datetime) -> Optional[float]:
        """Get underlying stock price on a specific date"""
        try:
            # Use daily aggregates - get the close price
            date_str = date.strftime('%Y-%m-%d')
            agg = self.client.get_daily_open_close_agg(ticker=ticker, date=date_str)
            
            # Try to get close price
            close_price = getattr(agg, 'close', None)
            if close_price:
                return float(close_price)
            
            # Fallback to other prices
            for attr in ['after_hours', 'high', 'low', 'open']:
                price = getattr(agg, attr, None)
                if price:
                    return float(price)
            
            return None
            
        except Exception as e:
            return None
    
    def get_historical_options_chain(self, ticker: str, date: datetime) -> Optional[Dict]:
        """
        Get historical options chain for a specific date
        
        This uses the snapshot options chain endpoint with as_of parameter
        """
        try:
            # Find expirations in our DTE range
            target_expirations = []
            min_exp_date = date + timedelta(days=self.min_dte)
            max_exp_date = date + timedelta(days=self.max_dte)
            
            # Get available expirations
            # NOTE: In production, you'd use list_options_contracts with as_of parameter
            # For now, we'll use a simplified approach
            
            options_data = {'calls': [], 'puts': []}
            
            # Query options snapshot
            # The Massive API supports historical snapshots using the snapshot endpoint
            # with date parameters or using the aggregates endpoint
            
            # For historical backtesting, we need to use:
            # 1. list_options_contracts to find available contracts
            # 2. get_aggregate_bars or get_daily_open_close_agg for historical pricing
            
            # This is a simplified version - in production you'd need to:
            # - Query contracts that were active on that date
            # - Get their historical pricing
            # - Filter by your criteria
            
            return options_data
            
        except Exception as e:
            print(f"Error getting historical chain for {ticker}: {e}")
            return None
    
    def check_indicators(self, ticker: str, date: datetime, price: float) -> bool:
        """Check if technical indicators give entry signal"""
        # If no indicators enabled, always return True
        if not any(self.indicators.values()):
            return True
        
        # Get historical price data for indicator calculation
        try:
            # Fetch enough history to calculate indicators (e.g., 200 days for SMA)
            start_hist = date - timedelta(days=250)
            
            # In production, you'd use get_aggregate_bars for historical data
            # For now, simplified approach
            
            # Calculate indicators based on what's enabled
            signals = []
            
            if self.indicators.get("SMA Crossover"):
                # Implement SMA crossover logic
                pass
            
            if self.indicators.get("RSI Filter"):
                # Implement RSI logic
                pass
            
            # If any indicator is enabled, at least one must be True
            return True  # Simplified for now
            
        except Exception as e:
            print(f"Error checking indicators for {ticker}: {e}")
            return False
    
    def construct_position(self, ticker: str, date: datetime, 
                          underlying_price: float, options_chain: Dict) -> Optional[OptionsPosition]:
        """
        Construct an options position based on the selected strategy
        
        This is where strategy-specific logic goes
        """
        strategy = self.strategy
        
        # Parse parameters
        try:
            # Common parameters
            min_oi = int(self.params.get("Min Open Interest", "100"))
            min_vol = int(self.params.get("Min Volume", "50"))
            
            # Strategy-specific construction
            if strategy == "Iron Condor":
                return self.construct_iron_condor(
                    ticker, date, underlying_price, options_chain,
                    min_oi, min_vol
                )
            elif strategy == "Long Call":
                return self.construct_long_call(
                    ticker, date, underlying_price, options_chain,
                    min_oi, min_vol
                )
            # Add other strategies...
            
            else:
                print(f"Strategy {strategy} not yet implemented")
                return None
                
        except Exception as e:
            print(f"Error constructing position: {e}")
            return None
    
    def construct_iron_condor(self, ticker: str, date: datetime, 
                             underlying_price: float, options_chain: Dict,
                             min_oi: int, min_vol: int) -> Optional[OptionsPosition]:
        """Construct an iron condor position"""
        # This would implement the iron condor logic similar to your screener
        # but using historical data
        
        # For now, return None as placeholder
        return None
    
    def construct_long_call(self, ticker: str, date: datetime,
                           underlying_price: float, options_chain: Dict,
                           min_oi: int, min_vol: int) -> Optional[OptionsPosition]:
        """Construct a long call position"""
        # Find suitable call option based on delta criteria
        # For now, placeholder
        return None
    
    def get_position_value(self, position: OptionsPosition, date: datetime) -> float:
        """Get current value of a position"""
        # In production, you'd fetch current option prices and calculate position value
        # For now, simplified
        return position.entry_cost
    
    def close_position(self, position: OptionsPosition, date: datetime, reason: str):
        """Close an open position"""
        position.exit_date = date
        position.exit_reason = reason
        position.days_held = (date - position.entry_date).days
        
        try:
            # Get underlying exit price
            position.underlying_exit_price = self.get_underlying_price(position.symbol, date)
            
            # Calculate final P&L
            exit_value = self.get_position_value(position, date)
            position.current_pnl = exit_value - position.entry_cost
            
        except Exception as e:
            print(f"Error closing position: {e}")
        
        # Move to closed positions
        self.open_positions.remove(position)
        self.closed_positions.append(position)
        self.all_trades.append(self.position_to_trade_dict(position))
    
    def close_all_positions(self, date: datetime):
        """Close all remaining open positions"""
        for position in list(self.open_positions):
            self.close_position(position, date, "Backtest End")
    
    def position_to_trade_dict(self, position: OptionsPosition) -> Dict:
        """Convert position to trade dictionary for results"""
        return {
            'Symbol': position.symbol,
            'Strategy': position.strategy,
            'Entry Date': position.entry_date.strftime('%Y-%m-%d'),
            'Exit Date': position.exit_date.strftime('%Y-%m-%d') if position.exit_date else None,
            'Days Held': position.days_held,
            'Entry Cost': round(position.entry_cost, 2),
            'Max Profit': round(position.max_profit, 2),
            'Max Loss': round(position.max_loss, 2),
            'PnL': round(position.current_pnl, 2),
            'PnL %': round((position.current_pnl / abs(position.entry_cost)) * 100, 2) if position.entry_cost != 0 else 0,
            'Exit Reason': position.exit_reason,
            'Win': position.current_pnl > 0,
            'Underlying Entry': round(position.underlying_entry_price, 2),
            'Underlying Exit': round(position.underlying_exit_price, 2) if position.underlying_exit_price else None,
        }
    
    def calculate_results(self) -> Dict:
        """Calculate backtest statistics"""
        if not self.all_trades:
            return {
                'trades': [],
                'stats': {},
                'equity_curve': [],
                'strategy': self.strategy,
                'config': self.config
            }
        
        df = pd.DataFrame(self.all_trades)
        
        # Calculate statistics
        total_trades = len(df)
        winning_trades = len(df[df['Win']])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = df['PnL'].sum()
        avg_pnl = df['PnL'].mean()
        avg_win = df[df['Win']]['PnL'].mean() if winning_trades > 0 else 0
        avg_loss = df[~df['Win']]['PnL'].mean() if losing_trades > 0 else 0
        
        # Build equity curve
        df_sorted = df.sort_values('Exit Date')
        df_sorted['Cumulative PnL'] = df_sorted['PnL'].cumsum()
        
        equity_curve = []
        for _, row in df_sorted.iterrows():
            equity_curve.append({
                'date': row['Exit Date'],
                'cumulative_pnl': row['Cumulative PnL'],
                'trade_pnl': row['PnL']
            })
        
        stats = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'avg_pnl': round(avg_pnl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0,
            'max_drawdown': self.calculate_max_drawdown(df_sorted),
            'sharpe_ratio': self.calculate_sharpe_ratio(df_sorted),
        }
        
        return {
            'trades': self.all_trades,
            'stats': stats,
            'equity_curve': equity_curve,
            'strategy': self.strategy,
            'config': self.config,
            'by_symbol': self.group_by_symbol(df)
        }
    
    def calculate_max_drawdown(self, df: pd.DataFrame) -> float:
        """Calculate maximum drawdown"""
        if 'Cumulative PnL' not in df.columns or len(df) == 0:
            return 0.0
        
        cumulative = df['Cumulative PnL'].values
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        max_dd = drawdown.min()
        
        return round(max_dd, 2)
    
    def calculate_sharpe_ratio(self, df: pd.DataFrame) -> float:
        """Calculate Sharpe ratio"""
        if len(df) < 2:
            return 0.0
        
        returns = df['PnL %'].values
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Annualized Sharpe (assuming ~252 trading days)
        sharpe = (avg_return / std_return) * np.sqrt(252 / len(df))
        
        return round(sharpe, 2)
    
    def group_by_symbol(self, df: pd.DataFrame) -> Dict:
        """Group trades by symbol"""
        by_symbol = {}
        
        for symbol in df['Symbol'].unique():
            symbol_trades = df[df['Symbol'] == symbol]
            by_symbol[symbol] = symbol_trades.to_dict('records')
        
        return by_symbol
