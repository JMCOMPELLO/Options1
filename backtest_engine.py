#!/usr/bin/env python3
"""
Options Backtesting Engine with Historical Data
Uses Massive API (Polygon.io) for historical options chains and pricing
"""

from massive import RESTClient
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional, Callable
import pandas as pd
import numpy as np
from dataclasses import dataclass

ET = ZoneInfo("America/New_York")

@dataclass
class OptionsPosition:
    """Represents an options position"""
    symbol: str
    strategy: str
    entry_date: datetime
    expiration_date: datetime
    legs: List[Dict]
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
        self.risk_config = config['risk_management']
        self.params = config['parameters']
        
        # Results
        self.all_trades = []
        self.open_positions = []
        self.closed_positions = []
        self.price_cache = {}
        self.options_cache = {}
        
    def log(self, message: str):
        if self.progress_callback:
            self.progress_callback(message)
        print(f"[BACKTEST] {message}")
    
    def run_backtest(self) -> Dict:
        self.log(f"Starting: {self.strategy} backtest")
        self.log(f"Period: {self.start_date.date()} to {self.end_date.date()}")
        
        # Check weekly to reduce API calls
        trading_days = self.generate_weekly_check_dates()
        self.log(f"Checking {len(trading_days)} dates for signals")
        
        for idx, current_date in enumerate(trading_days):
            if idx % 3 == 0:
                self.log(f"{current_date.date()} ({idx+1}/{len(trading_days)}) - Pos:{len(self.open_positions)}, Trades:{len(self.all_trades)}")
            
            self.update_positions(current_date)
            
            if len(self.open_positions) < self.max_positions:
                self.check_entry_signals(current_date)
        
        self.close_all_positions(self.end_date)
        results = self.calculate_results()
        self.log(f"✓ Complete! {len(self.all_trades)} trades")
        return results
    
    def generate_weekly_check_dates(self) -> List[datetime]:
        days = []
        current = self.start_date
        while current <= self.end_date:
            if current.weekday() == 0:  # Monday
                days.append(current)
            current += timedelta(days=1)
        return days
    
    def get_underlying_price(self, ticker: str, date: datetime) -> Optional[float]:
        cache_key = f"{ticker}_{date.date()}"
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]
        
        try:
            agg = self.client.get_daily_open_close_agg(ticker=ticker, date=date.strftime('%Y-%m-%d'))
            price = getattr(agg, 'close', None) or getattr(agg, 'open', None)
            if price:
                price = float(price)
                self.price_cache[cache_key] = price
                return price
        except:
            pass
        return None
    
    def get_options_for_expiration(self, ticker: str, date: datetime, expiration: str) -> List[Dict]:
        cache_key = f"{ticker}_{date.date()}_{expiration}"
        if cache_key in self.options_cache:
            return self.options_cache[cache_key]
        
        try:
            contracts = list(self.client.list_options_contracts(
                underlying_ticker=ticker,
                expiration_date=expiration,
                limit=100
            ))
            
            options_data = []
            date_str = date.strftime('%Y-%m-%d')
            
            for contract in contracts[:50]:  # Limit API calls
                try:
                    opt_agg = self.client.get_daily_open_close_agg(
                        ticker=contract.ticker, 
                        date=date_str
                    )
                    
                    close = getattr(opt_agg, 'close', None)
                    if not close:
                        continue
                    
                    spread = max(0.05, float(close) * 0.02)
                    options_data.append({
                        'strike': float(contract.strike_price),
                        'bid': max(0.01, float(close) - spread/2),
                        'ask': max(0.02, float(close) + spread/2),
                        'type': contract.contract_type,
                        'mid': float(close)
                    })
                except:
                    continue
            
            self.options_cache[cache_key] = options_data
            return options_data
        except:
            return []
    
    def find_expirations(self, ticker: str, date: datetime) -> List[str]:
        min_date = date + timedelta(days=self.min_dte)
        max_date = date + timedelta(days=self.max_dte)
        
        try:
            contracts = list(self.client.list_options_contracts(
                underlying_ticker=ticker,
                expiration_date_gte=min_date.strftime('%Y-%m-%d'),
                expiration_date_lte=max_date.strftime('%Y-%m-%d'),
                limit=500
            ))
            
            exps = set(str(c.expiration_date) for c in contracts if c.expiration_date)
            return sorted(list(exps))[:2]  # Limit to 2
        except:
            return []
    
    def check_entry_signals(self, date: datetime):
        ticker_idx = (date - self.start_date).days % len(self.tickers)
        ticker = self.tickers[ticker_idx]
        
        pos = self.check_ticker_entry(ticker, date)
        if pos:
            self.open_positions.append(pos)
            self.log(f"Opened {pos.strategy} on {pos.symbol}")
    
    def check_ticker_entry(self, ticker: str, date: datetime) -> Optional[OptionsPosition]:
        if any(p.symbol == ticker for p in self.open_positions):
            return None
        
        price = self.get_underlying_price(ticker, date)
        if not price:
            return None
        
        exps = self.find_expirations(ticker, date)
        if not exps:
            return None
        
        for exp in exps[:1]:
            options = self.get_options_for_expiration(ticker, date, exp)
            if not options:
                continue
            
            calls = [o for o in options if o['type'] == 'call']
            puts = [o for o in options if o['type'] == 'put']
            
            if len(calls) >= 2 and len(puts) >= 2:
                pos = self.construct_iron_condor(ticker, date, price, calls, puts, exp)
                if pos:
                    return pos
        
        return None
    
    def construct_iron_condor(self, ticker: str, date: datetime, price: float,
                             calls: List[Dict], puts: List[Dict], exp: str) -> Optional[OptionsPosition]:
        try:
            calls = sorted(calls, key=lambda x: x['strike'])
            puts = sorted(puts, key=lambda x: x['strike'])
            
            otm_calls = [c for c in calls if c['strike'] > price * 1.02]
            otm_puts = [p for p in puts if p['strike'] < price * 0.98]
            
            if len(otm_calls) < 2 or len(otm_puts) < 2:
                return None
            
            c_sell = otm_calls[0]
            c_buy = otm_calls[min(1, len(otm_calls)-1)]
            p_sell = otm_puts[-1]
            p_buy = otm_puts[max(-2, -len(otm_puts))]
            
            credit = (c_sell['bid'] + c_sell['ask'])/2 - (c_buy['bid'] + c_buy['ask'])/2 + \
                    (p_sell['bid'] + p_sell['ask'])/2 - (p_buy['bid'] + p_buy['ask'])/2
            
            if credit <= 0:
                return None
            
            width = max(c_buy['strike'] - c_sell['strike'], p_sell['strike'] - p_buy['strike'])
            max_loss = width - credit
            
            if max_loss <= 0:
                return None
            
            return OptionsPosition(
                symbol=ticker,
                strategy=self.strategy,
                entry_date=date,
                expiration_date=datetime.fromisoformat(exp).replace(tzinfo=ET),
                legs=[
                    {'type': 'call', 'action': 'sell', 'strike': c_sell['strike']},
                    {'type': 'call', 'action': 'buy', 'strike': c_buy['strike']},
                    {'type': 'put', 'action': 'sell', 'strike': p_sell['strike']},
                    {'type': 'put', 'action': 'buy', 'strike': p_buy['strike']},
                ],
                entry_cost=credit,
                max_profit=credit,
                max_loss=max_loss,
                underlying_entry_price=price
            )
        except:
            return None
    
    def update_positions(self, date: datetime):
        to_close = []
        
        for pos in self.open_positions:
            if date.date() >= pos.expiration_date.date():
                to_close.append((pos, "Expiration"))
                continue
            
            price = self.get_underlying_price(pos.symbol, date)
            if not price:
                continue
            
            # Simplified P&L
            c_sell = [l['strike'] for l in pos.legs if l['type']=='call' and l['action']=='sell'][0]
            p_sell = [l['strike'] for l in pos.legs if l['type']=='put' and l['action']=='sell'][0]
            
            if p_sell <= price <= c_sell:
                pos.current_pnl = pos.max_profit * 0.8
            else:
                pos.current_pnl = -pos.max_loss * 0.5
            
            pos.days_held = (date - pos.entry_date).days
            
            if self.risk_config['stop_loss_enabled']:
                if pos.current_pnl <= -pos.max_loss * (self.risk_config['stop_loss_pct']/100):
                    to_close.append((pos, "Stop Loss"))
            
            if self.risk_config['profit_target_enabled']:
                if pos.current_pnl >= pos.max_profit * (self.risk_config['profit_target_pct']/100):
                    to_close.append((pos, "Profit Target"))
        
        for pos, reason in to_close:
            self.close_position(pos, date, reason)
    
    def close_position(self, pos: OptionsPosition, date: datetime, reason: str):
        pos.exit_date = date
        pos.exit_reason = reason
        pos.days_held = (date - pos.entry_date).days
        pos.underlying_exit_price = self.get_underlying_price(pos.symbol, date) or pos.underlying_entry_price
        
        self.open_positions.remove(pos)
        self.closed_positions.append(pos)
        self.all_trades.append({
            'Symbol': pos.symbol,
            'Strategy': pos.strategy,
            'Entry Date': pos.entry_date.strftime('%Y-%m-%d'),
            'Exit Date': pos.exit_date.strftime('%Y-%m-%d'),
            'Days Held': pos.days_held,
            'Entry Cost': round(pos.entry_cost, 2),
            'Max Profit': round(pos.max_profit, 2),
            'Max Loss': round(pos.max_loss, 2),
            'PnL': round(pos.current_pnl, 2),
            'PnL %': round((pos.current_pnl/abs(pos.entry_cost))*100, 2) if pos.entry_cost != 0 else 0,
            'Exit Reason': pos.exit_reason,
            'Win': pos.current_pnl > 0,
            'Underlying Entry': round(pos.underlying_entry_price, 2),
            'Underlying Exit': round(pos.underlying_exit_price, 2),
        })
    
    def close_all_positions(self, date: datetime):
        for pos in list(self.open_positions):
            self.close_position(pos, date, "Backtest End")
    
    def calculate_results(self) -> Dict:
        if not self.all_trades:
            return {'trades': [], 'stats': {}, 'equity_curve': [], 'strategy': self.strategy, 'config': self.config, 'by_symbol': {}}
        
        df = pd.DataFrame(self.all_trades)
        wins = len(df[df['Win']])
        total = len(df)
        
        stats = {
            'total_trades': total,
            'winning_trades': wins,
            'losing_trades': total - wins,
            'win_rate': round((wins/total*100) if total > 0 else 0, 2),
            'total_pnl': round(df['PnL'].sum(), 2),
            'avg_pnl': round(df['PnL'].mean(), 2),
            'avg_win': round(df[df['Win']]['PnL'].mean() if wins > 0 else 0, 2),
            'avg_loss': round(df[~df['Win']]['PnL'].mean() if (total-wins) > 0 else 0, 2),
            'profit_factor': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
        }
        
        if stats['avg_loss'] != 0:
            stats['profit_factor'] = round(abs(stats['avg_win']/stats['avg_loss']), 2)
        
        df_sorted = df.sort_values('Exit Date')
        df_sorted['Cumulative PnL'] = df_sorted['PnL'].cumsum()
        
        equity_curve = [
            {'date': row['Exit Date'], 'cumulative_pnl': row['Cumulative PnL'], 'trade_pnl': row['PnL']}
            for _, row in df_sorted.iterrows()
        ]
        
        by_symbol = {}
        for symbol in df['Symbol'].unique():
            by_symbol[symbol] = df[df['Symbol'] == symbol].to_dict('records')
        
        return {
            'trades': self.all_trades,
            'stats': stats,
            'equity_curve': equity_curve,
            'strategy': self.strategy,
            'config': self.config,
            'by_symbol': by_symbol
        }
