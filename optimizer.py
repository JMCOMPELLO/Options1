"""
Parameter Optimization Module
Goal-seeking optimization to maximize equity return total value %
"""

import tkinter as tk
from tkinter import ttk, messagebox
import itertools
from datetime import datetime
import threading
import json


class ParameterOptimizer:
    """Optimizes strategy parameters to maximize total return %"""

    def __init__(self, strategy_tab):
        self.strategy_tab = strategy_tab
        self.app = strategy_tab.app
        self.is_running = False
        self.best_result = None
        self.all_results = []

    def get_parameter_ranges(self):
        """Define parameter ranges for optimization"""
        ranges = {
            # Risk Management Parameters
            'stop_loss_pct': [25, 50, 75, 100],
            'profit_target_pct': [25, 50, 75, 100],
            'trailing_stop_pct': [15, 25, 35, 50],
            'min_dte': [20, 30, 45, 60],
            'max_dte': [45, 60, 75, 90],

            # Strategy Parameters (will vary by strategy)
            'delta_short_min': [0.15, 0.20, 0.25, 0.30],
            'delta_short_max': [0.30, 0.35, 0.40, 0.45],
            'delta_long_min': [0.05, 0.10, 0.15],
            'delta_long_max': [0.10, 0.15, 0.20],
            'iv_rank_min': [20, 30, 40, 50],
            'iv_rank_max': [60, 70, 80, 90],
            'min_open_interest': [50, 100, 200, 500],
            'min_volume': [25, 50, 100, 200],

            # Position Management
            'max_positions': [5, 10, 15, 20],
            'capital_per_trade': [500, 1000, 2000, 5000],
        }

        return ranges

    def create_parameter_combinations(self, max_combinations=100):
        """
        Create parameter combinations to test
        Uses smart sampling to avoid testing every possible combination
        """
        ranges = self.get_parameter_ranges()

        # For initial optimization, sample key parameters
        # Later can be refined with grid search around best results

        # Create combinations for critical parameters first
        critical_params = {
            'stop_loss_pct': ranges['stop_loss_pct'],
            'profit_target_pct': ranges['profit_target_pct'],
            'min_dte': ranges['min_dte'],
            'max_dte': ranges['max_dte'],
        }

        # Generate all combinations of critical params
        critical_combos = list(itertools.product(*critical_params.values()))
        critical_keys = list(critical_params.keys())

        # For each critical combo, randomly sample other parameters
        import random
        combinations = []

        # Limit to max_combinations
        sample_size = min(len(critical_combos), max_combinations)
        sampled_critical = random.sample(critical_combos, sample_size) if len(critical_combos) > sample_size else critical_combos

        for critical_combo in sampled_critical:
            combo = dict(zip(critical_keys, critical_combo))

            # Add sampled values for other parameters
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

            # Ensure min < max for ranges
            if combo['min_dte'] >= combo['max_dte']:
                combo['max_dte'] = combo['min_dte'] + 15
            if combo['delta_short_min'] >= combo['delta_short_max']:
                combo['delta_short_min'], combo['delta_short_max'] = combo['delta_short_max'], combo['delta_short_min']
            if combo['delta_long_min'] >= combo['delta_long_max']:
                combo['delta_long_min'], combo['delta_long_max'] = combo['delta_long_max'], combo['delta_long_min']
            if combo['iv_rank_min'] >= combo['iv_rank_max']:
                combo['iv_rank_min'], combo['iv_rank_max'] = combo['iv_rank_max'], combo['iv_rank_min']

            combinations.append(combo)

        return combinations

    def apply_parameters(self, params):
        """Apply parameter combination to the strategy tab"""
        # Risk management
        if 'stop_loss_pct' in params:
            self.strategy_tab.stop_loss_pct.delete(0, tk.END)
            self.strategy_tab.stop_loss_pct.insert(0, str(params['stop_loss_pct']))

        if 'profit_target_pct' in params:
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

        # Strategy-specific parameters (update param_widgets)
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

            return {
                'params': params.copy(),
                'total_return_pct': total_return_pct,
                'results': results,
                'stats': results['stats']
            }

        except Exception as e:
            print(f"Error running backtest: {e}")
            return None

    def optimize(self, progress_callback=None, max_combinations=50):
        """
        Run optimization to find best parameters

        Args:
            progress_callback: Function to call with progress updates
            max_combinations: Maximum number of parameter combinations to test
        """
        self.is_running = True
        self.all_results = []
        self.best_result = None

        # Generate parameter combinations
        combinations = self.create_parameter_combinations(max_combinations)
        total = len(combinations)

        if progress_callback:
            progress_callback(f"Testing {total} parameter combinations...", 0, total)

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
                progress_callback(
                    f"Tested {idx+1}/{total} combinations. Best so far: {self.best_result['total_return_pct']:.2f}% return" if self.best_result else f"Tested {idx+1}/{total}",
                    idx + 1,
                    total
                )

        self.is_running = False
        return self.best_result

    def stop(self):
        """Stop the optimization process"""
        self.is_running = False


class OptimizerWindow:
    """GUI window for parameter optimization"""

    def __init__(self, parent, strategy_tab):
        self.strategy_tab = strategy_tab
        self.optimizer = ParameterOptimizer(strategy_tab)
        self.window = tk.Toplevel(parent)
        self.window.title("Parameter Optimizer - Goal Seeking")
        self.window.geometry("800x600")
        self.window.configure(bg="#f0f0f0")

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#1a1a1a", height=80)
        header.pack(fill=tk.X)

        tk.Label(header, text="🎯 PARAMETER OPTIMIZER", fg="#32CD32",
                bg="#1a1a1a", font=("Arial", 22, "bold")).pack(pady=10)
        tk.Label(header, text="Automatically find optimal parameters to maximize Total Return %",
                fg="white", bg="#1a1a1a", font=("Arial", 11)).pack()

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
        combo_frame.pack(anchor='w', pady=(0, 15))

        self.num_combinations = tk.Scale(combo_frame, from_=10, to=200, orient=tk.HORIZONTAL,
                                         length=300, bg="white", fg="black",
                                         font=("Arial", 10), label="")
        self.num_combinations.set(50)
        self.num_combinations.pack(side=tk.LEFT)

        tk.Label(combo_frame, text="(More = better results but slower)",
                bg="white", fg="#666", font=("Arial", 9)).pack(side=tk.LEFT, padx=10)

        # Optimization goal
        tk.Label(inner, text="Optimization Goal:",
                bg="white", fg="black", font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))

        goal_text = "Maximize: Total Return % (Equity Return Total Value %)"
        tk.Label(inner, text=goal_text, bg="white", fg="#4CAF50",
                font=("Arial", 10, "bold")).pack(anchor='w', padx=20)

        # What gets optimized
        tk.Label(inner, text="\nParameters that will be optimized:",
                bg="white", fg="black", font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))

        params_text = """• Stop Loss %
• Profit Target %
• Trailing Stop %
• Min/Max DTE (Days to Expiration)
• Delta Ranges (Short & Long Legs)
• IV Rank Range
• Min Open Interest & Volume
• Max Concurrent Positions
• Capital per Trade"""

        tk.Label(inner, text=params_text, bg="white", fg="black",
                font=("Arial", 9), justify=tk.LEFT).pack(anchor='w', padx=20)

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

        self.progress_bar = ttk.Progressbar(inner_progress, mode='determinate', length=600)
        self.progress_bar.pack(pady=(0, 15))

        # Results display
        results_scroll = tk.Frame(inner_progress, bg="white")
        results_scroll.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(results_scroll)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text = tk.Text(results_scroll, height=10, bg="#f9f9f9", fg="black",
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

    def update_progress(self, message, current, total):
        """Update progress display"""
        self.progress_label.config(text=message)
        self.progress_bar['maximum'] = total
        self.progress_bar['value'] = current
        self.window.update()

    def log_result(self, message):
        """Log a result to the text display"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.window.update()

    def start_optimization(self):
        """Start the optimization process"""
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.apply_btn.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)

        max_combinations = self.num_combinations.get()

        def run_optimization():
            self.log_result(f"Starting optimization with {max_combinations} parameter combinations...\n")
            self.log_result(f"Strategy: {self.strategy_tab.strategy_var.get()}")
            self.log_result(f"Date Range: {self.strategy_tab.start_date.get()} to {self.strategy_tab.end_date.get()}\n")

            result = self.optimizer.optimize(
                progress_callback=self.update_progress,
                max_combinations=max_combinations
            )

            if result:
                self.log_result("\n" + "="*60)
                self.log_result("OPTIMIZATION COMPLETE!")
                self.log_result("="*60 + "\n")
                self.log_result(f"Best Total Return: {result['total_return_pct']:.2f}%\n")
                self.log_result("Best Parameters:")
                self.log_result("-" * 60)

                for key, value in result['params'].items():
                    self.log_result(f"  {key}: {value}")

                self.log_result("\n" + "-" * 60)
                self.log_result("Performance Metrics:")
                self.log_result("-" * 60)
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

    def stop_optimization(self):
        """Stop the optimization"""
        self.optimizer.stop()
        self.log_result("\n⏹ Optimization stopped by user")
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL)

    def apply_best_parameters(self):
        """Apply the best parameters found to the strategy tab"""
        if not self.optimizer.best_result:
            messagebox.showwarning("No Results", "No optimization results available")
            return

        # Apply the best parameters
        self.optimizer.apply_parameters(self.optimizer.best_result['params'])

        # Enable risk management checkboxes
        self.strategy_tab.use_stop_loss.set(True)
        self.strategy_tab.use_profit_target.set(True)

        messagebox.showinfo(
            "Parameters Applied",
            f"Best parameters have been applied to the Strategy Configuration.\n\n"
            f"Expected Total Return: {self.optimizer.best_result['total_return_pct']:.2f}%\n\n"
            f"You can now run a backtest with these optimized settings."
        )

        self.window.destroy()
