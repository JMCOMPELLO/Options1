import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import json

class StrategyConfigTab:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg="#f0f0f0")
        self.param_widgets = {}
        self.indicator_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        # Create scrollable main container
        main_canvas = tk.Canvas(self.frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=main_canvas.yview)
        scrollable = tk.Frame(main_canvas, bg="#f0f0f0")
        
        scrollable.bind("<Configure>", 
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        
        main_canvas.create_window((0, 0), window=scrollable, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling - improved for Mac trackpad
        def _on_mousewheel(event):
            # For Mac trackpad
            main_canvas.yview_scroll(int(-1*(event.delta)), "units")
        
        def _on_mousewheel_linux(event):
            # For Linux/Windows
            if event.num == 4:
                main_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                main_canvas.yview_scroll(1, "units")
        
        # Bind both types of scroll events
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        main_canvas.bind_all("<Button-4>", _on_mousewheel_linux)
        main_canvas.bind_all("<Button-5>", _on_mousewheel_linux)
        
        # Header
        header = tk.Frame(scrollable, bg="#1a1a1a", height=90)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="STRATEGY CONFIGURATION", fg="#32CD32", 
                bg="#1a1a1a", font=("Arial", 26, "bold")).pack(pady=5)
        tk.Label(header, text="Configure your options strategy parameters and indicators", 
                fg="white", bg="#1a1a1a", font=("Arial", 12)).pack()
        
        main_content = tk.Frame(scrollable, bg="#f0f0f0")
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Left column - Strategy Selection
        left_col = tk.Frame(main_content, bg="#f0f0f0")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_strategy_selection(left_col)
        self.create_entry_indicators(left_col)
        self.create_risk_management(left_col)
        
        # Right column - Parameters
        right_col = tk.Frame(main_content, bg="#f0f0f0")
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.create_parameters_panel(right_col)
        self.create_backtest_config(right_col)
        
        # Bottom - Control buttons
        self.create_control_panel(scrollable)
        
    def create_strategy_selection(self, parent):
        """Strategy selection panel"""
        panel = tk.LabelFrame(parent, text=" 📊 OPTIONS STRATEGY ", 
                             bg="white", fg="black", font=("Arial", 13, "bold"), bd=3)
        panel.pack(fill=tk.X, pady=(0, 15))
        
        inner = tk.Frame(panel, bg="white")
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tk.Label(inner, text="Select Strategy Type:", bg="white", 
                font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        
        self.strategy_var = tk.StringVar(value="Iron Condor")
        
        # Categorize strategies
        strategies = {
            "🐂 BULLISH": [
                "Long Call", "Cash-Secured Put", "Bull Call Spread", 
                "Bull Put Spread", "Call Diagonal Spread", "Call Ratio Backspread"
            ],
            "🐻 BEARISH": [
                "Long Put", "Bear Put Spread", "Bear Call Spread", "Put Ratio Backspread"
            ],
            "⚖️ NEUTRAL/INCOME": [
                "Covered Call", "Protective Put", "Collar", "Iron Condor", 
                "Iron Butterfly", "Short Strangle", "Short Straddle"
            ],
            "🔀 VOLATILITY": [
                "Long Straddle", "Long Strangle", "Calendar Spread"
            ]
        }
        
        for category, strats in strategies.items():
            tk.Label(inner, text=category, bg="white", fg="#1976D2",
                    font=("Arial", 10, "bold")).pack(anchor='w', pady=(8, 2))
            
            for strat in strats:
                rb = tk.Radiobutton(inner, text=strat, variable=self.strategy_var,
                                   value=strat, command=self.on_strategy_change,
                                   bg="white", font=("Arial", 10), 
                                   activebackground="#e3f2fd")
                rb.pack(anchor='w', padx=15, pady=1)
        
        # Strategy description
        desc_frame = tk.LabelFrame(panel, text=" Strategy Info ", 
                                   bg="#fffde7", fg="#827717", font=("Arial", 10, "bold"))
        desc_frame.pack(fill=tk.X, padx=15, pady=(10, 10))
        
        self.desc_text = tk.Text(desc_frame, height=4, wrap=tk.WORD, bg="#fffde7",
                                font=("Arial", 9), relief=tk.FLAT, fg="black")
        self.desc_text.pack(padx=8, pady=8)
        self.desc_text.config(state=tk.DISABLED)
    
    def create_entry_indicators(self, parent):
        """Entry signal indicators"""
        panel = tk.LabelFrame(parent, text=" 📈 ENTRY INDICATORS (Optional) ", 
                             bg="white", fg="black", font=("Arial", 13, "bold"), bd=3)
        panel.pack(fill=tk.X, pady=(0, 15))
        
        inner = tk.Frame(panel, bg="white")
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tk.Label(inner, text="Add technical indicators to filter entry signals:", 
                bg="white", font=("Arial", 10, "italic")).pack(anchor='w', pady=(0, 8))
        
        indicators = [
            ("SMA Crossover", "Short SMA > Long SMA (bullish) or vice versa"),
            ("RSI Filter", "Only enter when RSI is in specified range"),
            ("MACD Signal", "Enter when MACD crosses signal line"),
            ("Bollinger Bands", "Enter when price touches bands"),
            ("Volume Filter", "Require minimum volume spike"),
            ("ATR Filter", "Enter during high/low volatility"),
            ("IV Rank Filter", "Enter based on implied volatility rank"),
            ("Momentum", "Enter based on price momentum")
        ]
        
        for indicator, desc in indicators:
            var = tk.BooleanVar()
            self.indicator_vars[indicator] = var
            
            cb = tk.Checkbutton(inner, text=indicator, variable=var,
                              bg="white", font=("Arial", 10, "bold"),
                              command=self.update_indicator_params)
            cb.pack(anchor='w', pady=2)
            
            tk.Label(inner, text=f"  └ {desc}", bg="white", fg="gray",
                    font=("Arial", 9, "italic")).pack(anchor='w', padx=20)
    
    def create_risk_management(self, parent):
        """Risk management settings"""
        panel = tk.LabelFrame(parent, text=" 🛡️ RISK MANAGEMENT ", 
                             bg="white", fg="black", font=("Arial", 13, "bold"), bd=3)
        panel.pack(fill=tk.X, pady=(0, 15))
        
        inner = tk.Frame(panel, bg="white")
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Stop loss
        self.use_stop_loss = tk.BooleanVar()
        tk.Checkbutton(inner, text="Enable Stop Loss", variable=self.use_stop_loss,
                      bg="white", font=("Arial", 10, "bold")).pack(anchor='w', pady=3)
        
        sl_frame = tk.Frame(inner, bg="white")
        sl_frame.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(sl_frame, text="Stop Loss %:", bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.stop_loss_pct = tk.Entry(sl_frame, width=10)
        self.stop_loss_pct.insert(0, "50")
        self.stop_loss_pct.pack(side=tk.LEFT)
        tk.Label(sl_frame, text="(% of max loss)", bg="white", fg="gray",
                font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Profit target
        self.use_profit_target = tk.BooleanVar()
        tk.Checkbutton(inner, text="Enable Profit Target", variable=self.use_profit_target,
                      bg="white", font=("Arial", 10, "bold")).pack(anchor='w', pady=(8, 3))
        
        pt_frame = tk.Frame(inner, bg="white")
        pt_frame.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(pt_frame, text="Profit Target %:", bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.profit_target_pct = tk.Entry(pt_frame, width=10)
        self.profit_target_pct.insert(0, "50")
        self.profit_target_pct.pack(side=tk.LEFT)
        tk.Label(pt_frame, text="(% of max profit)", bg="white", fg="gray",
                font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Trailing stop
        self.use_trailing_stop = tk.BooleanVar()
        tk.Checkbutton(inner, text="Enable Trailing Stop", variable=self.use_trailing_stop,
                      bg="white", font=("Arial", 10, "bold")).pack(anchor='w', pady=(8, 3))
        
        ts_frame = tk.Frame(inner, bg="white")
        ts_frame.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(ts_frame, text="Trailing Stop %:", bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.trailing_stop_pct = tk.Entry(ts_frame, width=10)
        self.trailing_stop_pct.insert(0, "25")
        self.trailing_stop_pct.pack(side=tk.LEFT)
        
        # Max DTE filter
        tk.Label(inner, text="\nDays to Expiration:", bg="white",
                font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 3))
        
        dte_frame = tk.Frame(inner, bg="white")
        dte_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(dte_frame, text="Min DTE:", bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.min_dte = tk.Entry(dte_frame, width=8)
        self.min_dte.insert(0, "30")
        self.min_dte.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(dte_frame, text="Max DTE:", bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.max_dte = tk.Entry(dte_frame, width=8)
        self.max_dte.insert(0, "60")
        self.max_dte.pack(side=tk.LEFT)
    
    def create_parameters_panel(self, parent):
        """Dynamic parameters panel"""
        panel = tk.LabelFrame(parent, text=" ⚙️ STRATEGY PARAMETERS ", 
                             bg="white", fg="black", font=("Arial", 13, "bold"), bd=3)
        panel.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.param_frame = tk.Frame(panel, bg="white")
        self.param_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Will be populated dynamically
        self.on_strategy_change()
    
    def create_backtest_config(self, parent):
        """Backtest configuration"""
        panel = tk.LabelFrame(parent, text=" 📅 BACKTEST CONFIGURATION ", 
                             bg="white", fg="black", font=("Arial", 13, "bold"), bd=3)
        panel.pack(fill=tk.X)
        
        inner = tk.Frame(panel, bg="white")
        inner.pack(fill=tk.X, padx=15, pady=15)
        
        # Date range
        tk.Label(inner, text="Date Range:", bg="white", 
                font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=4, 
                                                 sticky='w', pady=(0, 8))
        
        tk.Label(inner, text="Start:", bg="white").grid(row=1, column=0, sticky='e', padx=5)
        self.start_date = tk.Entry(inner, width=12, font=("Arial", 10))
        self.start_date.insert(0, "2023-01-01")
        self.start_date.grid(row=1, column=1, padx=5)
        
        tk.Label(inner, text="End:", bg="white").grid(row=1, column=2, sticky='e', padx=5)
        self.end_date = tk.Entry(inner, width=12, font=("Arial", 10))
        self.end_date.insert(0, "2024-12-31")
        self.end_date.grid(row=1, column=3, padx=5)
        
        # Trading frequency
        tk.Label(inner, text="\nTrading Frequency:", bg="white",
                font=("Arial", 11, "bold")).grid(row=2, column=0, columnspan=4, 
                                                 sticky='w', pady=(10, 5))
        
        self.trade_freq = tk.StringVar(value="On Signal")
        frequencies = [
            ("On Signal", "Enter whenever indicators trigger"),
            ("Daily", "Check for entries every day"),
            ("Weekly", "Check for entries once per week"),
            ("Monthly", "Check for entries once per month")
        ]
        
        for idx, (freq, desc) in enumerate(frequencies):
            tk.Radiobutton(inner, text=f"{freq} - {desc}", variable=self.trade_freq,
                          value=freq, bg="white", font=("Arial", 9)).grid(
                              row=3+idx, column=0, columnspan=4, sticky='w', pady=1)
        
        # Max concurrent positions
        tk.Label(inner, text="\nPosition Limits:", bg="white",
                font=("Arial", 11, "bold")).grid(row=7, column=0, columnspan=4, 
                                                 sticky='w', pady=(10, 5))
        
        pos_frame = tk.Frame(inner, bg="white")
        pos_frame.grid(row=8, column=0, columnspan=4, sticky='w', pady=3)
        
        tk.Label(pos_frame, text="Max Concurrent Positions:", 
                bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.max_positions = tk.Entry(pos_frame, width=8)
        self.max_positions.insert(0, "10")
        self.max_positions.pack(side=tk.LEFT)
        
        # Capital allocation
        cap_frame = tk.Frame(inner, bg="white")
        cap_frame.grid(row=9, column=0, columnspan=4, sticky='w', pady=3)
        
        tk.Label(cap_frame, text="Capital per Trade:", 
                bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.capital_per_trade = tk.Entry(cap_frame, width=10)
        self.capital_per_trade.insert(0, "1000")
        self.capital_per_trade.pack(side=tk.LEFT)
        tk.Label(cap_frame, text="USD", bg="white", fg="gray").pack(side=tk.LEFT, padx=5)
    
    def create_control_panel(self, parent):
        """Control buttons"""
        panel = tk.Frame(parent, bg="#f0f0f0")
        panel.pack(fill=tk.X, padx=20, pady=20)
        
        # Progress
        self.progress_label = tk.Label(panel, text="Ready to run backtest", 
                                       bg="#f0f0f0", font=("Arial", 12), fg="#666")
        self.progress_label.pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(panel, bg="#f0f0f0")
        btn_frame.pack()
        
        tk.Button(btn_frame, text="⬅ BACK", bg="#757575", fg="white",
                 font=("Arial", 14, "bold"), command=lambda: self.app.notebook.select(0),
                 padx=30, pady=15, cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="🚀 RUN BACKTEST", bg="#4CAF50", fg="white",
                 font=("Arial", 16, "bold"), command=self.run_backtest,
                 padx=50, pady=18, cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="💾 SAVE CONFIG", bg="#2196F3", fg="white",
                 font=("Arial", 14, "bold"), command=self.save_config,
                 padx=30, pady=15, cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def on_strategy_change(self):
        """Update UI when strategy changes"""
        strategy = self.strategy_var.get()
        
        # Clear existing parameters
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.param_widgets.clear()
        
        # Update description
        descriptions = {
            "Iron Condor": "Sell OTM call spread + OTM put spread. Profit from low volatility. Limited risk & reward.",
            "Long Call": "Buy a call option. Profit from strong upside. Limited risk (premium), unlimited upside.",
            "Long Put": "Buy a put option. Profit from sharp decline. Defined risk, leveraged downside.",
            "Bull Call Spread": "Buy call, sell higher call. Lower cost bullish position. Limited risk & profit.",
            "Bear Put Spread": "Buy put, sell lower put. Lower cost bearish position. Limited risk & profit.",
            "Iron Butterfly": "Sell ATM straddle, buy OTM strangle. Max profit if price stays at strike.",
            "Long Straddle": "Buy ATM call + put. Profit from large move in either direction.",
            "Short Straddle": "Sell ATM call + put. Max profit if price barely moves. High risk.",
            "Calendar Spread": "Sell near-term, buy far-term same strike. Profit from time decay differences.",
            "Covered Call": "Own stock + sell call. Generate income. Caps upside.",
            # Add more descriptions as needed...
        }
        
        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, descriptions.get(strategy, "Configure parameters below."))
        self.desc_text.config(state=tk.DISABLED)
        
        # Create strategy-specific parameters
        self.create_strategy_params(strategy)
    
    def create_strategy_params(self, strategy):
        """Create parameters for selected strategy"""
        
        # Common parameters for most strategies
        self.add_param("Delta Range (Short Leg)", "0.20,0.35", 
                      "Target delta range for sold options (e.g., 0.20,0.35)")
        
        self.add_param("Delta Range (Long Leg)", "0.05,0.15",
                      "Target delta range for bought options (protection)")
        
        self.add_param("Min IV Rank", "30",
                      "Minimum IV Rank to enter trade (0-100)")
        
        self.add_param("Max IV Rank", "80",
                      "Maximum IV Rank to enter trade (0-100)")
        
        self.add_param("Min Open Interest", "100",
                      "Minimum open interest for liquidity")
        
        self.add_param("Min Volume", "50",
                      "Minimum daily volume for liquidity")
        
        # Strategy-specific parameters
        if "Spread" in strategy or "Condor" in strategy or "Butterfly" in strategy:
            self.add_param("Spread Width ($)", "5,10",
                          "Width of spread in dollars (min,max)")
            
            self.add_param("Credit/Debit Ratio", "0.25,0.40",
                          "Min/max ratio of credit to spread width")
        
        if strategy == "Iron Condor":
            self.add_param("Profit Zone Width", "0.10,0.20",
                          "Profit zone as % of stock price (0.10 = ±10%)")
        
        if strategy == "Calendar Spread":
            self.add_param("Front Month DTE", "30,45",
                          "Days to expiration for short-term leg")
            self.add_param("Back Month DTE", "60,90",
                          "Days to expiration for long-term leg")
        
        if "Straddle" in strategy or "Strangle" in strategy:
            self.add_param("Strike Selection", "ATM",
                          "ATM (at-the-money) or OTM offset %")
        
        # Greeks filters
        tk.Label(self.param_frame, text="\nGreeks Filters (Optional):", 
                bg="white", font=("Arial", 11, "bold")).pack(anchor='w', pady=(15, 5))
        
        self.add_param("Min Theta (per day)", "-0.10",
                      "Minimum daily theta decay")
        
        self.add_param("Max Vega", "0.50",
                      "Maximum vega exposure")
        
        self.add_param("Max Gamma", "0.05",
                      "Maximum gamma exposure")
    
    def add_param(self, label, default, tooltip):
        """Add a parameter input field"""
        frame = tk.Frame(self.param_frame, bg="white")
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(frame, text=label + ":", bg="white", 
                font=("Arial", 10, "bold"), width=25, anchor='e').pack(side=tk.LEFT, padx=(0, 10))
        
        entry = tk.Entry(frame, font=("Arial", 10), width=20)
        entry.insert(0, default)
        entry.pack(side=tk.LEFT)
        
        self.param_widgets[label] = entry
        
        tk.Label(frame, text=f"ℹ️ {tooltip}", bg="white", fg="gray",
                font=("Arial", 8, "italic")).pack(side=tk.LEFT, padx=10)
    
    def update_indicator_params(self):
        """Show/hide indicator parameters based on selection"""
        # This would create additional parameter fields for selected indicators
        pass
    
    def save_config(self):
        """Save configuration to file"""
        config = self.get_config()
        try:
            with open("backtest_config.json", "w") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved to backtest_config.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def get_config(self):
        """Get current configuration as dictionary"""
        config = {
            "strategy": self.strategy_var.get(),
            "start_date": self.start_date.get(),
            "end_date": self.end_date.get(),
            "trade_frequency": self.trade_freq.get(),
            "max_positions": int(self.max_positions.get()),
            "capital_per_trade": float(self.capital_per_trade.get()),
            "min_dte": int(self.min_dte.get()),
            "max_dte": int(self.max_dte.get()),
            "risk_management": {
                "stop_loss_enabled": self.use_stop_loss.get(),
                "stop_loss_pct": float(self.stop_loss_pct.get()) if self.use_stop_loss.get() else None,
                "profit_target_enabled": self.use_profit_target.get(),
                "profit_target_pct": float(self.profit_target_pct.get()) if self.use_profit_target.get() else None,
                "trailing_stop_enabled": self.use_trailing_stop.get(),
                "trailing_stop_pct": float(self.trailing_stop_pct.get()) if self.use_trailing_stop.get() else None,
            },
            "indicators": {k: v.get() for k, v in self.indicator_vars.items()},
            "parameters": {k: v.get() for k, v in self.param_widgets.items()}
        }
        return config
    
    def run_backtest(self):
        """Execute the backtest"""
        try:
            if not self.app.api_key:
                messagebox.showerror("API Error", "Massive API key not configured")
                return
            
            if not self.app.selected_tickers:
                messagebox.showerror("Error", "No stocks selected")
                return
            
            # Validate dates
            start = datetime.strptime(self.start_date.get(), "%Y-%m-%d")
            end = datetime.strptime(self.end_date.get(), "%Y-%m-%d")
            
            if start >= end:
                messagebox.showerror("Error", "Start date must be before end date")
                return
            
            self.progress_label.config(text="Initializing backtest engine...", fg="#FF9800")
            self.frame.update()
            
            # Import and run backtest engine
            from backtest_engine import OptionsBacktestEngine
            
            config = self.get_config()
            
            engine = OptionsBacktestEngine(
                api_key=self.app.api_key,
                tickers=list(self.app.selected_tickers),
                config=config,
                progress_callback=self.update_progress
            )
            
            self.progress_label.config(text="Running backtest... This may take several minutes.", 
                                      fg="#FF9800")
            self.frame.update()
            
            results = engine.run_backtest()
            
            if not results or len(results.get('trades', [])) == 0:
                messagebox.showwarning("No Trades", 
                    "Backtest completed but generated no trades. Try adjusting parameters.")
                self.progress_label.config(text="Complete - No trades generated", fg="#666")
                return
            
            # Store results
            self.app.backtest_results = results
            
            # Enable analysis tabs
            self.app.enable_analysis_tabs()
            
            # Populate equity curve
            self.app.equity_tab.display_results(results)
            
            # Populate detailed results
            self.app.results_tab.display_results(results)
            
            # Switch to equity curve
            self.app.notebook.select(2)
            
            total_trades = len(results['trades'])
            self.progress_label.config(
                text=f"✓ Backtest complete! Generated {total_trades} trades.", 
                fg="#4CAF50")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format: {e}")
            self.progress_label.config(text="Error occurred", fg="red")
        except Exception as e:
            messagebox.showerror("Error", f"Backtest failed: {e}")
            self.progress_label.config(text="Error occurred", fg="red")
            import traceback
            traceback.print_exc()
    
    def update_progress(self, message):
        """Update progress label"""
        self.progress_label.config(text=message, fg="#FF9800")
        self.frame.update()
