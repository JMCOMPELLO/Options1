"""
Enhanced Parameter Optimization Module
Goal-seeking optimization to maximize equity return total value %
INCLUDES: All indicators, indicator parameters, and intraday trading frequency
"""

import tkinter as tk
from tkinter import ttk, messagebox
import itertools
from datetime import datetime
import threading
import json
import random


class EnhancedParameterOptimizer:
    """Optimizes ALL strategy parameters including indicators to maximize total return %"""

    def __init__(self, strategy_tab):
        self.strategy_tab = strategy_tab
        self.app = strategy_tab.app
        self.is_running = False
        self.best_result = None
        self.all_results = []

    def get_indicator_parameter_ranges(self):
        """Define parameter ranges for ALL indicators"""
        indicator_ranges = {
            'SMA Crossover': {
                'enabled': [True, False],
                'Short Period': [5, 10, 15, 20],
                'Long Period': [20, 50, 100, 200]
            },
            'RSI Filter': {
                'enabled': [True, False],
                'RSI Period': [7, 14, 21, 30],
                'Min RSI': [20, 30, 40],
                'Max RSI': [60, 70, 80]
            },
            'MACD Signal': {
                'enabled': [True, False],
                'Fast Period': [8, 12, 16],
                'Slow Period': [21, 26, 30],
                'Signal Period': [6, 9, 12]
            },
            'Bollinger Bands': {
                'enabled': [True, False],
                'Period': [10, 20, 30],
                'Std Dev': [1.5, 2.0, 2.5, 3.0]
            },
            'Volume Filter': {
                'enabled': [True, False],
                'Min Volume': [500000, 1000000, 2000000],
                'Volume Multiplier': [1.2, 1.5, 2.0, 2.5]
            },
            'ATR Filter': {
                'enabled': [True, False],
                'ATR Period': [10, 14, 20],
                'Min ATR': [0.3, 0.5, 1.0],
                'Max ATR': [3.0, 5.0, 10.0]
            },
            'IV Rank Filter': {
                'enabled': [True, False],
                'Min IV Rank': [20, 30, 40],
                'Max IV Rank': [70, 80, 90]
            },
            'Momentum': {
                'enabled': [True, False],
                'Period': [5, 10, 20],
                'Min Change %': [1.0, 2.0, 3.0, 5.0]
            }
        }
        return indicator_ranges

    def get_parameter_ranges(self):
        """Define parameter ranges for optimization"""
        ranges = {
            # Risk Management Parameters
            'stop_loss_pct': [25, 50, 75, 100],
            'profit_target_pct': [25, 50, 75, 100],
            'trailing_stop_pct': [15, 25, 35, 50],
            'min_dte': [20, 30, 45, 60],
            'max_dte': [45, 60, 75, 90],

            # Strategy Parameters
            'delta_short_min': [0.15, 0.20, 0.25, 0.30],
            'delta_short_max': [0.30, 0.35, 0.40, 0.45],
            'delta_long_min': [0.05, 0.10, 0.15],
            'delta_long_max': [0.10, 0.15, 0.20],
            'iv_rank_min': [20, 30, 40, 50],
            'iv_rank_max': [60, 70, 80, 90],
            'min_open_interest': [50, 100, 200, 500],
            'min_volume': [25, 50, 100, 200],

            # Position Management
            'max_positions': [5, 10, 15, 20, 30],
            'capital_per_trade': [500, 1000, 2000, 5000],

            # Trading Frequency (NEW - for intraday)
            'trade_frequency': ['Intraday (Multiple per day)', 'Daily', 'Weekly', 'On Signal'],
            'trades_per_day_limit': [1, 2, 3, 5, 10],  # Max trades per stock per day
            'min_time_between_trades': [0, 15, 30, 60, 120],  # Minutes between trades
        }

        return ranges

    def create_parameter_combinations(self, max_combinations=100, optimize_indicators=True):
        """
        Create parameter combinations to test

        Args:
            max_combinations: Maximum number of combinations to generate
            optimize_indicators: If True, includes indicator optimization
        """
        ranges = self.get_parameter_ranges()
        indicator_ranges = self.get_indicator_parameter_ranges()

        combinations = []

        # Strategy to generate diverse combinations:
        # 1. Test different indicator combinations (0-3 indicators enabled)
        # 2. For each indicator combo, test different parameter sets
        # 3. Combine with critical strategy parameters

        indicator_names = list(indicator_ranges.keys())

        for _ in range(max_combinations):
            combo = {}

            # === STRATEGY PARAMETERS ===
            combo['stop_loss_pct'] = random.choice(ranges['stop_loss_pct'])
            combo['profit_target_pct'] = random.choice(ranges['profit_target_pct'])
            combo['trailing_stop_pct'] = random.choice(ranges['trailing_stop_pct'])
            combo['min_dte'] = random.choice(ranges['min_dte'])
            combo['max_dte'] = random.choice(ranges['max_dte'])
            combo['delta_short_min'] = random.choice(ranges['delta_short_min'])
            combo['delta_short_max'] = random.choice(ranges['delta_short_max'])
            combo['delta_long_min'] = random.choice(ranges['delta_long_min'])
            combo['delta_long_max'] = random.choice(ranges['delta_long_max'])
            combo['iv_rank_min'] = random.choice(ranges['iv_rank_min'])
            combo['iv_rank_max'] = random.choice(ranges['iv_rank_max'])
            combo['min_open_interest'] = random.choice(ranges['min_open_interest'])
            combo['min_volume'] = random.choice(ranges['min_volume'])
            combo['max_positions'] = random.choice(ranges['max_positions'])
            combo['capital_per_trade'] = random.choice(ranges['capital_per_trade'])

            # === TRADING FREQUENCY (NEW) ===
            combo['trade_frequency'] = random.choice(ranges['trade_frequency'])
            combo['trades_per_day_limit'] = random.choice(ranges['trades_per_day_limit'])
            combo['min_time_between_trades'] = random.choice(ranges['min_time_between_trades'])

            # === INDICATOR OPTIMIZATION ===
            combo['indicators'] = {}

            if optimize_indicators:
                # Randomly enable 0-4 indicators
                num_indicators = random.choice([0, 1, 1, 2, 2, 3, 4])  # Weighted toward 1-2 indicators
                enabled_indicators = random.sample(indicator_names, num_indicators)

                for indicator_name in indicator_names:
                    indicator_config = {}
                    is_enabled = indicator_name in enabled_indicators
                    indicator_config['enabled'] = is_enabled

                    if is_enabled:
                        # Sample parameters for this indicator
                        ind_ranges = indicator_ranges[indicator_name]
                        for param_name, param_values in ind_ranges.items():
                            if param_name != 'enabled':
                                indicator_config[param_name] = random.choice(param_values)

                    combo['indicators'][indicator_name] = indicator_config

            # === VALIDATION: Ensure min < max ===
            if combo['min_dte'] >= combo['max_dte']:
                combo['max_dte'] = combo['min_dte'] + 15
            if combo['delta_short_min'] >= combo['delta_short_max']:
                combo['delta_short_min'], combo['delta_short_max'] = combo['delta_short_max'], combo['delta_short_min']
            if combo['delta_long_min'] >= combo['delta_long_max']:
                combo['delta_long_min'], combo['delta_long_max'] = combo['delta_long_max'], combo['delta_long_min']
            if combo['iv_rank_min'] >= combo['iv_rank_max']:
                combo['iv_rank_min'], combo['iv_rank_max'] = combo['iv_rank_max'], combo['iv_rank_min']

            # Validate indicator min/max ranges
            if optimize_indicators:
                for indicator_name, ind_config in combo['indicators'].items():
                    if ind_config.get('enabled'):
                        # RSI Filter
                        if indicator_name == 'RSI Filter':
                            if ind_config.get('Min RSI', 0) >= ind_config.get('Max RSI', 100):
                                ind_config['Min RSI'], ind_config['Max RSI'] = ind_config['Max RSI'], ind_config['Min RSI']
                        # SMA Crossover
                        elif indicator_name == 'SMA Crossover':
                            if ind_config.get('Short Period', 0) >= ind_config.get('Long Period', 200):
                                ind_config['Short Period'], ind_config['Long Period'] = ind_config['Long Period'], ind_config['Short Period']
                        # ATR Filter
                        elif indicator_name == 'ATR Filter':
                            if ind_config.get('Min ATR', 0) >= ind_config.get('Max ATR', 10):
                                ind_config['Min ATR'], ind_config['Max ATR'] = ind_config['Max ATR'], ind_config['Min ATR']
                        # IV Rank Filter
                        elif indicator_name == 'IV Rank Filter':
                            if ind_config.get('Min IV Rank', 0) >= ind_config.get('Max IV Rank', 100):
                                ind_config['Min IV Rank'], ind_config['Max IV Rank'] = ind_config['Max IV Rank'], ind_config['Min IV Rank']

            combinations.append(combo)

        return combinations

    def apply_parameters(self, params):
        """Apply parameter combination to the strategy tab"""
        # === RISK MANAGEMENT ===
        if 'stop_loss_pct' in params:
            self.strategy_tab.use_stop_loss.set(True)
            self.strategy_tab.stop_loss_pct.delete(0, tk.END)
            self.strategy_tab.stop_loss_pct.insert(0, str(params['stop_loss_pct']))

        if 'profit_target_pct' in params:
            self.strategy_tab.use_profit_target.set(True)
            self.strategy_tab.profit_target_pct.delete(0, tk.END)
            self.strategy_tab.profit_target_pct.insert(0, str(params['profit_target_pct']))

        if 'trailing_stop_pct' in params:
            self.strategy_tab.trailing_stop_pct.delete(0, tk.END)
            self.strategy_tab.trailing_stop_pct.insert(0, str(params['trailing_stop_pct']))

        if 'min_dte' in params:
            self.strategy_tab.min_dte.delete(0, tk.END)
            self.strategy_tab.min_dte.insert(0, str(params['min_dte']))

        if 'max_dte' in params:
            self.strategy_tab.max_dte.delete(0, tk.END)
            self.strategy_tab.max_dte.insert(0, str(params['max_dte']))

        if 'max_positions' in params:
            self.strategy_tab.max_positions.delete(0, tk.END)
            self.strategy_tab.max_positions.insert(0, str(params['max_positions']))

        if 'capital_per_trade' in params:
            self.strategy_tab.capital_per_trade.delete(0, tk.END)
            self.strategy_tab.capital_per_trade.insert(0, str(params['capital_per_trade']))

        # === TRADING FREQUENCY ===
        if 'trade_frequency' in params:
            self.strategy_tab.trade_freq.set(params['trade_frequency'])

        # === STRATEGY-SPECIFIC PARAMETERS ===
        param_mapping = {
            'Delta Range (Short Leg)': lambda p: f"{p.get('delta_short_min', 0.20)},{p.get('delta_short_max', 0.35)}",
            'Delta Range (Long Leg)': lambda p: f"{p.get('delta_long_min', 0.05)},{p.get('delta_long_max', 0.15)}",
            'Min IV Rank': lambda p: str(p.get('iv_rank_min', 30)),
            'Max IV Rank': lambda p: str(p.get('iv_rank_max', 80)),
            'Min Open Interest': lambda p: str(p.get('min_open_interest', 100)),
            'Min Volume': lambda p: str(p.get('min_volume', 50)),
        }

        for param_name, value_func in param_mapping.items():
            if param_name in self.strategy_tab.param_widgets:
                widget = self.strategy_tab.param_widgets[param_name]
                widget.delete(0, tk.END)
                widget.insert(0, value_func(params))

        # === INDICATORS ===
        if 'indicators' in params:
            for indicator_name, ind_config in params['indicators'].items():
                # Set checkbox
                if indicator_name in self.strategy_tab.indicator_vars:
                    is_enabled = ind_config.get('enabled', False)
                    self.strategy_tab.indicator_vars[indicator_name].set(is_enabled)

                    # Apply indicator parameters if enabled
                    if is_enabled and indicator_name in self.strategy_tab.indicator_param_widgets:
                        for param_name, param_value in ind_config.items():
                            if param_name != 'enabled' and param_name in self.strategy_tab.indicator_param_widgets[indicator_name]:
                                widget = self.strategy_tab.indicator_param_widgets[indicator_name][param_name]
                                widget.delete(0, tk.END)
                                widget.insert(0, str(param_value))

                    # Show/hide parameter frames
                    self.strategy_tab.toggle_indicator_params(indicator_name)

    def run_backtest_with_params(self, params):
        """Run backtest with specific parameters and return total return %"""
        # Apply parameters
        self.apply_parameters(params)

        # Run backtest (simulated version)
        try:
            start = datetime.strptime(self.strategy_tab.start_date.get(), "%Y-%m-%d")
            end = datetime.strptime(self.strategy_tab.end_date.get(), "%Y-%m-%d")

            # Use the existing backtest generation method
            results = self.strategy_tab.generate_indicator_filtered_backtest(start, end)

            if not results or not results.get('trades'):
                return None

            # Calculate total return %
            starting_capital = 20000
            total_pnl = results['stats']['total_pnl']
            total_return_pct = (total_pnl / starting_capital) * 100

            # Count enabled indicators
            enabled_indicators = []
            if 'indicators' in params:
                enabled_indicators = [name for name, config in params['indicators'].items() if config.get('enabled')]

            return {
                'params': params.copy(),
                'total_return_pct': total_return_pct,
                'results': results,
                'stats': results['stats'],
                'enabled_indicators': enabled_indicators,
                'trade_frequency': params.get('trade_frequency', 'On Signal'),
                'trades_per_day': params.get('trades_per_day_limit', 1)
            }

        except Exception as e:
            print(f"Error running backtest: {e}")
            import traceback
            traceback.print_exc()
            return None

    def optimize(self, progress_callback=None, max_combinations=50, optimize_indicators=True):
        """
        Run optimization to find best parameters

        Args:
            progress_callback: Function to call with progress updates
            max_combinations: Maximum number of parameter combinations to test
            optimize_indicators: If True, optimizes indicator settings too
        """
        self.is_running = True
        self.all_results = []
        self.best_result = None

        # Generate parameter combinations
        combinations = self.create_parameter_combinations(max_combinations, optimize_indicators)
        total = len(combinations)

        if progress_callback:
            progress_callback(f"Testing {total} parameter combinations (including indicators)...", 0, total)

        # Test each combination
        for idx, params in enumerate(combinations):
            if not self.is_running:
                break

            result = self.run_backtest_with_params(params)

            if result:
                self.all_results.append(result)

                # Update best result
                if self.best_result is None or result['total_return_pct'] > self.best_result['total_return_pct']:
                    self.best_result = result

            if progress_callback:
                best_msg = f"Best: {self.best_result['total_return_pct']:.2f}% return" if self.best_result else "Searching..."
                indicators_msg = f" | {len(result.get('enabled_indicators', []))} indicators" if result else ""
                progress_callback(
                    f"Tested {idx+1}/{total} | {best_msg}{indicators_msg}",
                    idx + 1,
                    total
                )

        self.is_running = False
        return self.best_result

    def stop(self):
        """Stop the optimization process"""
        self.is_running = False


# Import original OptimizerWindow and modify it
from optimizer import OptimizerWindow as OriginalOptimizerWindow


class EnhancedOptimizerWindow(OriginalOptimizerWindow):
    """Enhanced GUI window for parameter optimization with indicator support"""

    def __init__(self, parent, strategy_tab):
        self.strategy_tab = strategy_tab
        self.optimizer = EnhancedParameterOptimizer(strategy_tab)  # Use enhanced optimizer
        self.window = tk.Toplevel(parent)
        self.window.title("Enhanced Parameter Optimizer - Goal Seeking")
        self.window.geometry("900x700")
        self.window.configure(bg="#f0f0f0")

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#1a1a1a", height=90)
        header.pack(fill=tk.X)

        tk.Label(header, text="🎯 ENHANCED PARAMETER OPTIMIZER", fg="#32CD32",
                bg="#1a1a1a", font=("Arial", 22, "bold")).pack(pady=5)
        tk.Label(header, text="Optimize ALL parameters including indicators & trading frequency to maximize Total Return %",
                fg="white", bg="#1a1a1a", font=("Arial", 10)).pack()

        # Settings panel
        settings_frame = tk.LabelFrame(self.window, text=" ⚙️ OPTIMIZATION SETTINGS ",
                                       bg="white", fg="black", font=("Arial", 12, "bold"), bd=3)
        settings_frame.pack(fill=tk.X, padx=20, pady=15)

        inner = tk.Frame(settings_frame, bg="white")
        inner.pack(fill=tk.X, padx=20, pady=15)

        # Number of combinations to test
        tk.Label(inner, text="Number of Parameter Combinations to Test:",
                bg="white", fg="black", font=("Arial", 11)).pack(anchor='w', pady=(0, 5))

        combo_frame = tk.Frame(inner, bg="white")
        combo_frame.pack(anchor='w', pady=(0, 10))

        self.num_combinations = tk.Scale(combo_frame, from_=10, to=200, orient=tk.HORIZONTAL,
                                         length=300, bg="white", fg="black",
                                         font=("Arial", 10), label="")
        self.num_combinations.set(75)
        self.num_combinations.pack(side=tk.LEFT)

        tk.Label(combo_frame, text="(More = better results but slower)",
                bg="white", fg="#666", font=("Arial", 9)).pack(side=tk.LEFT, padx=10)

        # Include indicators checkbox
        self.optimize_indicators = tk.BooleanVar(value=True)
        tk.Checkbutton(inner, text="Include Indicator Optimization (all 8 indicators + parameters)",
                      variable=self.optimize_indicators, bg="white", fg="black",
                      font=("Arial", 10, "bold"), selectcolor="white").pack(anchor='w', pady=(10, 5))

        # Optimization goal
        tk.Label(inner, text="\nOptimization Goal:",
                bg="white", fg="black", font=("Arial", 11, "bold")).pack(anchor='w', pady=(5, 5))

        goal_text = "Maximize: Total Return % (Equity Return Total Value %)"
        tk.Label(inner, text=goal_text, bg="white", fg="#4CAF50",
                font=("Arial", 10, "bold")).pack(anchor='w', padx=20)

        # What gets optimized
        tk.Label(inner, text="\nParameters to be optimized:",
                bg="white", fg="black", font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))

        # Create two columns for parameters
        params_frame = tk.Frame(inner, bg="white")
        params_frame.pack(fill=tk.X, padx=20, pady=5)

        col1 = tk.Frame(params_frame, bg="white")
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        col2 = tk.Frame(params_frame, bg="white")
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        params_col1 = """STRATEGY PARAMETERS:
• Stop Loss %
• Profit Target %
• Trailing Stop %
• Min/Max DTE
• Delta Ranges
• IV Rank Range
• Open Interest & Volume
• Max Positions
• Capital per Trade"""

        params_col2 = """INDICATORS (All 8):
• SMA Crossover + params
• RSI Filter + params
• MACD Signal + params
• Bollinger Bands + params
• Volume Filter + params
• ATR Filter + params
• IV Rank Filter + params
• Momentum + params

TRADING FREQUENCY:
• Intraday/Daily/Weekly
• Trades per day limit
• Min time between trades"""

        tk.Label(col1, text=params_col1, bg="white", fg="black",
                font=("Arial", 9), justify=tk.LEFT).pack(anchor='w')

        tk.Label(col2, text=params_col2, bg="white", fg="black",
                font=("Arial", 9), justify=tk.LEFT).pack(anchor='w')

        # Progress panel
        progress_frame = tk.LabelFrame(self.window, text=" 📊 OPTIMIZATION PROGRESS ",
                                       bg="white", fg="black", font=("Arial", 12, "bold"), bd=3)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        inner_progress = tk.Frame(progress_frame, bg="white")
        inner_progress.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Progress bar
        self.progress_label = tk.Label(inner_progress, text="Ready to start optimization",
                                       bg="white", fg="black", font=("Arial", 11))
        self.progress_label.pack(pady=(0, 10))

        self.progress_bar = ttk.Progressbar(inner_progress, mode='determinate', length=700)
        self.progress_bar.pack(pady=(0, 15))

        # Results display
        results_scroll = tk.Frame(inner_progress, bg="white")
        results_scroll.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(results_scroll)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text = tk.Text(results_scroll, height=8, bg="#f9f9f9", fg="black",
                                    font=("Courier", 9), yscrollcommand=scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)

        # Control buttons
        btn_frame = tk.Frame(self.window, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.start_btn = tk.Button(btn_frame, text="🚀 START OPTIMIZATION", bg="#4CAF50", fg="white",
                                   font=("Arial", 14, "bold"), command=self.start_optimization,
                                   padx=30, pady=15, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(btn_frame, text="⏹ STOP", bg="#F44336", fg="white",
                                  font=("Arial", 14, "bold"), command=self.stop_optimization,
                                  padx=30, pady=15, cursor="hand2", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        self.apply_btn = tk.Button(btn_frame, text="✓ APPLY BEST PARAMETERS", bg="#2196F3", fg="white",
                                   font=("Arial", 14, "bold"), command=self.apply_best_parameters,
                                   padx=30, pady=15, cursor="hand2", state=tk.DISABLED)
        self.apply_btn.pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="CLOSE", bg="#757575", fg="white",
                 font=("Arial", 14, "bold"), command=self.window.destroy,
                 padx=30, pady=15, cursor="hand2").pack(side=tk.RIGHT, padx=10)

    def start_optimization(self):
        """Start the optimization process"""
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.apply_btn.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)

        max_combinations = self.num_combinations.get()
        include_indicators = self.optimize_indicators.get()

        def run_optimization():
            self.log_result(f"Starting ENHANCED optimization with {max_combinations} combinations...\n")
            self.log_result(f"Strategy: {self.strategy_tab.strategy_var.get()}")
            self.log_result(f"Date Range: {self.strategy_tab.start_date.get()} to {self.strategy_tab.end_date.get()}")
            self.log_result(f"Indicator Optimization: {'ENABLED' if include_indicators else 'DISABLED'}")
            self.log_result(f"Trading Frequency: Will be optimized\n")

            result = self.optimizer.optimize(
                progress_callback=self.update_progress,
                max_combinations=max_combinations,
                optimize_indicators=include_indicators
            )

            if result:
                self.log_result("\n" + "="*70)
                self.log_result("OPTIMIZATION COMPLETE!")
                self.log_result("="*70 + "\n")
                self.log_result(f"Best Total Return: {result['total_return_pct']:.2f}%\n")

                # Display enabled indicators
                if result.get('enabled_indicators'):
                    self.log_result(f"Optimal Indicators ({len(result['enabled_indicators'])}):")
                    for ind in result['enabled_indicators']:
                        ind_params = result['params']['indicators'][ind]
                        self.log_result(f"  ✓ {ind}")
                        for param_name, param_value in ind_params.items():
                            if param_name != 'enabled':
                                self.log_result(f"      {param_name}: {param_value}")
                    self.log_result("")
                else:
                    self.log_result("Optimal Strategy: No indicators\n")

                self.log_result("Trading Frequency:")
                self.log_result(f"  • Frequency: {result.get('trade_frequency', 'On Signal')}")
                self.log_result(f"  • Max trades per day: {result.get('trades_per_day', 1)}\n")

                self.log_result("Best Strategy Parameters:")
                self.log_result("-" * 70)
                for key, value in result['params'].items():
                    if key != 'indicators':
                        self.log_result(f"  {key}: {value}")

                self.log_result("\n" + "-" * 70)
                self.log_result("Performance Metrics:")
                self.log_result("-" * 70)
                stats = result['stats']
                self.log_result(f"  Total Trades: {stats['total_trades']}")
                self.log_result(f"  Win Rate: {stats['win_rate']:.2f}%")
                self.log_result(f"  Total P&L: ${stats['total_pnl']:.2f}")
                self.log_result(f"  Avg P&L per Trade: ${stats['avg_pnl']:.2f}")
                self.log_result(f"  Profit Factor: {stats['profit_factor']:.2f}")
                self.log_result(f"  Sharpe Ratio: {stats['sharpe_ratio']:.2f}")

                self.log_result("\n✓ Click 'APPLY BEST PARAMETERS' to use these settings")

                self.apply_btn.config(state=tk.NORMAL)
            else:
                self.log_result("\nOptimization failed or was stopped.")

            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

        # Run in thread to keep UI responsive
        thread = threading.Thread(target=run_optimization, daemon=True)
        thread.start()

    def apply_best_parameters(self):
        """Apply the best parameters found to the strategy tab"""
        if not self.optimizer.best_result:
            messagebox.showwarning("No Results", "No optimization results available")
            return

        # Apply the best parameters
        self.optimizer.apply_parameters(self.optimizer.best_result['params'])

        # Get indicator summary
        enabled_inds = self.optimizer.best_result.get('enabled_indicators', [])
        indicator_msg = ""
        if enabled_inds:
            indicator_msg = f"\n\nOptimal Indicators ({len(enabled_inds)}):\n" + "\n".join(f"✓ {ind}" for ind in enabled_inds)
        else:
            indicator_msg = "\n\nNo indicators (strategy parameters only)"

        messagebox.showinfo(
            "Parameters Applied",
            f"Best parameters have been applied to the Strategy Configuration.\n\n"
            f"Expected Total Return: {self.optimizer.best_result['total_return_pct']:.2f}%\n"
            f"Trading Frequency: {self.optimizer.best_result.get('trade_frequency', 'On Signal')}"
            f"{indicator_msg}\n\n"
            f"You can now run a backtest with these optimized settings."
        )

        self.window.destroy()
