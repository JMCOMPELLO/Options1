import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import json

class StrategyConfigTab:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg="#f0f0f0")
        self.param_widgets = {}
        self.setup_ui()
    
    def setup_ui(self):
        # ULTRA SIMPLE LAYOUT
        
        # Header
        header = tk.Frame(self.frame, bg="#1a1a1a", height=70)
        header.pack(fill=tk.X)
        tk.Label(header, text="STRATEGY CONFIGURATION", fg="#32CD32", 
                bg="#1a1a1a", font=("Arial", 24, "bold")).pack(pady=15)
        
        # Main content with native Text widget scrolling
        main = tk.Frame(self.frame, bg="#f0f0f0")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Strategy selection
        strat_panel = tk.LabelFrame(main, text=" SELECT STRATEGY ", 
                                   bg="white", fg="#000000", font=("Arial", 12, "bold"))
        strat_panel.pack(fill=tk.X, pady=(0, 10))
        
        self.strategy_var = tk.StringVar(value="Iron Condor")
        strategies = ["Iron Condor", "Long Call", "Long Put", "Bull Call Spread",
                     "Bear Put Spread", "Long Straddle", "Short Straddle"]
        
        sf = tk.Frame(strat_panel, bg="white")
        sf.pack(padx=15, pady=10)
        
        for i, strat in enumerate(strategies):
            tk.Radiobutton(sf, text=strat, variable=self.strategy_var, value=strat,
                          bg="white", fg="#000000", font=("Arial", 10)).grid(
                              row=i//3, column=i%3, sticky='w', padx=10, pady=3)
        
        # Date range
        date_panel = tk.LabelFrame(main, text=" BACKTEST PERIOD ", 
                                  bg="white", fg="#000000", font=("Arial", 12, "bold"))
        date_panel.pack(fill=tk.X, pady=(0, 10))
        
        df = tk.Frame(date_panel, bg="white")
        df.pack(padx=15, pady=10)
        
        tk.Label(df, text="Start:", bg="white", fg="#000000", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=5)
        self.start_date = tk.Entry(df, font=("Arial", 10), width=12)
        self.start_date.insert(0, "2023-01-01")
        self.start_date.grid(row=0, column=1, padx=5)
        
        tk.Label(df, text="End:", bg="white", fg="#000000", font=("Arial", 10, "bold")).grid(
            row=0, column=2, padx=5)
        self.end_date = tk.Entry(df, font=("Arial", 10), width=12)
        self.end_date.insert(0, "2024-12-31")
        self.end_date.grid(row=0, column=3, padx=5)
        
        # Risk management
        risk_panel = tk.LabelFrame(main, text=" RISK MANAGEMENT ", 
                                  bg="white", fg="#000000", font=("Arial", 12, "bold"))
        risk_panel.pack(fill=tk.X, pady=(0, 10))
        
        rf = tk.Frame(risk_panel, bg="white")
        rf.pack(padx=15, pady=10)
        
        self.use_stop_loss = tk.BooleanVar()
        tk.Checkbutton(rf, text="Stop Loss", variable=self.use_stop_loss,
                      bg="white", fg="#000000").grid(row=0, column=0, sticky='w')
        self.stop_loss_pct = tk.Entry(rf, width=8)
        self.stop_loss_pct.insert(0, "50")
        self.stop_loss_pct.grid(row=0, column=1, padx=5)
        tk.Label(rf, text="% of max loss", bg="white", fg="#000000").grid(row=0, column=2)
        
        self.use_profit_target = tk.BooleanVar()
        tk.Checkbutton(rf, text="Profit Target", variable=self.use_profit_target,
                      bg="white", fg="#000000").grid(row=1, column=0, sticky='w', pady=5)
        self.profit_target_pct = tk.Entry(rf, width=8)
        self.profit_target_pct.insert(0, "50")
        self.profit_target_pct.grid(row=1, column=1, padx=5)
        tk.Label(rf, text="% of max profit", bg="white", fg="#000000").grid(row=1, column=2)
        
        # DTE
        tk.Label(rf, text="Min DTE:", bg="white", fg="#000000", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky='e', pady=5)
        self.min_dte = tk.Entry(rf, width=8)
        self.min_dte.insert(0, "30")
        self.min_dte.grid(row=2, column=1, padx=5)
        
        tk.Label(rf, text="Max DTE:", bg="white", fg="#000000", font=("Arial", 10, "bold")).grid(
            row=2, column=2, sticky='e')
        self.max_dte = tk.Entry(rf, width=8)
        self.max_dte.insert(0, "60")
        self.max_dte.grid(row=2, column=3, padx=5)
        
        # Progress
        self.progress_label = tk.Label(main, text="Ready to backtest", 
                                       bg="#f0f0f0", fg="#000000", font=("Arial", 11))
        self.progress_label.pack(pady=10)
        
        # Buttons - ALWAYS VISIBLE
        footer = tk.Frame(self.frame, bg="#f0f0f0", height=80)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        bf = tk.Frame(footer, bg="#f0f0f0")
        bf.pack()
        
        tk.Button(bf, text="⬅ BACK", bg="#757575", fg="white",
                 font=("Arial", 14, "bold"), command=lambda: self.app.notebook.select(0),
                 padx=30, pady=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(bf, text="🚀 RUN BACKTEST", bg="#757575", fg="white",
             font=("Arial", 16, "bold"), command=self.run_backtest,
             padx=50, pady=18).pack(side=tk.LEFT, padx=10)
    
    def run_backtest(self):
        try:
            start = datetime.strptime(self.start_date.get(), "%Y-%m-%d")
            end = datetime.strptime(self.end_date.get(), "%Y-%m-%d")
            
            if start >= end:
                messagebox.showerror("Error", "Start date must be before end date")
                return
            
            if not self.app.selected_tickers:
                messagebox.showerror("Error", "No stocks selected")
                return
            
            # Ask user if they want to run demo mode
            use_demo = messagebox.askyesno(
                "Backtest Mode",
                "Historical options data requires a premium API plan.\n\n"
                "Would you like to run a DEMO with sample data to see how the interface works?\n\n"
                "Click YES for demo mode (instant results)\n"
                "Click NO for real backtest (requires API access)"
            )
            
            if use_demo:
                # Generate demo results
                self.progress_label.config(text="Generating demo results...")
                self.frame.update()
                
                results = self.generate_demo_results(start, end)
                
                self.app.backtest_results = results
                self.app.enable_analysis_tabs()
                
                self.app.equity_tab.display_results(results)
                self.app.results_tab.display_results(results)
                
                self.app.notebook.select(2)
                
                total = len(results['trades'])
                self.progress_label.config(text=f"✓ Demo Complete! {total} sample trades")
                
                messagebox.showinfo("Demo Mode", 
                    f"Generated {total} sample trades for demonstration.\n\n"
                    "This shows how the interface works. For real backtesting, "
                    "you need historical options data access from Polygon.io")
                
            else:
                # Run real backtest
                self.run_real_backtest(start, end)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            self.progress_label.config(text="Error occurred")
            import traceback
            traceback.print_exc()
    
    def generate_demo_results(self, start, end):
        """Generate sample trades for demo purposes"""
        import random
        from datetime import timedelta
        
        trades = []
        strategy = self.strategy_var.get()
        tickers = list(self.app.selected_tickers)[:5]  # Use up to 5 tickers
        
        current_date = start
        cumulative_pnl = 0
        
        # Generate 20-30 sample trades
        num_trades = random.randint(20, 30)
        
        for i in range(num_trades):
            ticker = random.choice(tickers)
            
            # Random entry date
            days_range = (end - current_date).days
            if days_range <= 0:
                break
            entry_date = current_date + timedelta(days=random.randint(0, min(days_range, 30)))
            
            # Random exit date (5-45 days later)
            days_held = random.randint(5, 45)
            exit_date = entry_date + timedelta(days=days_held)
            if exit_date > end:
                exit_date = end
            
            # Random P&L (70% win rate for demo)
            is_win = random.random() < 0.70
            
            if is_win:
                pnl = random.uniform(20, 150)
                pnl_pct = random.uniform(15, 60)
            else:
                pnl = random.uniform(-200, -30)
                pnl_pct = random.uniform(-50, -10)
            
            cumulative_pnl += pnl
            
            entry_cost = random.uniform(200, 500)
            max_profit = entry_cost * 0.5
            max_loss = entry_cost * 1.5
            
            exit_reasons = ["Profit Target", "Stop Loss", "Expiration", "Time Exit"]
            
            trade = {
                'Symbol': ticker,
                'Strategy': strategy,
                'Entry Date': entry_date.strftime('%Y-%m-%d'),
                'Exit Date': exit_date.strftime('%Y-%m-%d'),
                'Days Held': days_held,
                'Entry Cost': round(entry_cost, 2),
                'Max Profit': round(max_profit, 2),
                'Max Loss': round(max_loss, 2),
                'PnL': round(pnl, 2),
                'PnL %': round(pnl_pct, 2),
                'Exit Reason': random.choice(exit_reasons) if is_win else "Stop Loss",
                'Win': is_win,
                'Underlying Entry': round(random.uniform(100, 500), 2),
                'Underlying Exit': round(random.uniform(100, 500), 2),
            }
            
            trades.append(trade)
            current_date = exit_date
        
        # Calculate stats
        df_trades = [t for t in trades]
        winning_trades = sum(1 for t in trades if t['Win'])
        total_trades = len(trades)
        
        stats = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': round((winning_trades / total_trades * 100) if total_trades > 0 else 0, 2),
            'total_pnl': round(sum(t['PnL'] for t in trades), 2),
            'avg_pnl': round(sum(t['PnL'] for t in trades) / total_trades if total_trades > 0 else 0, 2),
            'avg_win': round(sum(t['PnL'] for t in trades if t['Win']) / winning_trades if winning_trades > 0 else 0, 2),
            'avg_loss': round(sum(t['PnL'] for t in trades if not t['Win']) / (total_trades - winning_trades) if (total_trades - winning_trades) > 0 else 0, 2),
            'profit_factor': 0,
            'max_drawdown': round(random.uniform(-500, -100), 2),
            'sharpe_ratio': round(random.uniform(0.8, 2.5), 2),
        }
        
        avg_win = stats['avg_win']
        avg_loss = stats['avg_loss']
        stats['profit_factor'] = round(abs(avg_win / avg_loss) if avg_loss != 0 else 0, 2)
        
        # Build equity curve
        equity_curve = []
        cumulative = 0
        for trade in sorted(trades, key=lambda x: x['Exit Date']):
            cumulative += trade['PnL']
            equity_curve.append({
                'date': trade['Exit Date'],
                'cumulative_pnl': round(cumulative, 2),
                'trade_pnl': trade['PnL']
            })
        
        # Group by symbol
        by_symbol = {}
        for trade in trades:
            symbol = trade['Symbol']
            if symbol not in by_symbol:
                by_symbol[symbol] = []
            by_symbol[symbol].append(trade)
        
        return {
            'trades': trades,
            'stats': stats,
            'equity_curve': equity_curve,
            'strategy': strategy,
            'config': {},
            'by_symbol': by_symbol
        }
    
    def run_real_backtest(self, start, end):
        """Run actual backtest with API"""
        try:
            self.progress_label.config(text="Initializing backtest...")
            self.frame.update()
            
            # Import engine
            from backtest_engine import OptionsBacktestEngine
            
            config = {
                "strategy": self.strategy_var.get(),
                "start_date": self.start_date.get(),
                "end_date": self.end_date.get(),
                "min_dte": int(self.min_dte.get()),
                "max_dte": int(self.max_dte.get()),
                "max_positions": 10,
                "capital_per_trade": 1000,
                "trade_frequency": "On Signal",
                "risk_management": {
                    "stop_loss_enabled": self.use_stop_loss.get(),
                    "stop_loss_pct": float(self.stop_loss_pct.get()) if self.use_stop_loss.get() else None,
                    "profit_target_enabled": self.use_profit_target.get(),
                    "profit_target_pct": float(self.profit_target_pct.get()) if self.use_profit_target.get() else None,
                    "trailing_stop_enabled": False,
                    "trailing_stop_pct": None,
                },
                "indicators": {},
                "parameters": {
                    "Delta Range (Short Leg)": "0.20,0.35",
                    "Delta Range (Long Leg)": "0.05,0.15",
                    "Min IV Rank": "30",
                    "Max IV Rank": "80",
                    "Min Open Interest": "100",
                    "Min Volume": "50",
                }
            }
            
            engine = OptionsBacktestEngine(
                api_key=self.app.api_key,
                tickers=list(self.app.selected_tickers),
                config=config,
                progress_callback=self.update_progress
            )
            
            self.progress_label.config(text="Running backtest...")
            self.frame.update()
            
            results = engine.run_backtest()
            
            if not results or len(results.get('trades', [])) == 0:
                messagebox.showwarning("No Trades", "Backtest generated no trades. Try adjusting parameters.")
                self.progress_label.config(text="Complete - No trades")
                return
            
            self.app.backtest_results = results
            self.app.enable_analysis_tabs()
            
            self.app.equity_tab.display_results(results)
            self.app.results_tab.display_results(results)
            
            self.app.notebook.select(2)
            
            total = len(results['trades'])
            self.progress_label.config(text=f"✓ Complete! {total} trades generated")
            
        except Exception as e:
            messagebox.showerror("Error", f"Backtest failed: {e}")
            self.progress_label.config(text="Error occurred")
            import traceback
            traceback.print_exc()
    
    def update_progress(self, message):
        self.progress_label.config(text=message)
        self.frame.update()
