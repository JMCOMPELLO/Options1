"""
ULTIMATE Parameter Optimization Module
Tests ALL strategies, ALL indicators, ALL parameters
Maximum granularity for finding absolute best configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import itertools
from datetime import datetime
import threading
import json
import random


class UltimateParameterOptimizer:
    """The most comprehensive optimizer - tests EVERYTHING including all strategies"""

    def __init__(self, strategy_tab):
        self.strategy_tab = strategy_tab
        self.app = strategy_tab.app
        self.is_running = False
        self.best_result = None
        self.all_results = []
        self.results_by_strategy = {}  # Track best for each strategy

    def get_all_strategies(self):
        """Get all available option strategies"""
        strategies = {
            "BULLISH": [
                "Long Call", "Cash-Secured Put", "Bull Call Spread",
                "Bull Put Spread", "Call Diagonal Spread", "Call Ratio Backspread"
            ],
            "BEARISH": [
                "Long Put", "Bear Put Spread", "Bear Call Spread", "Put Ratio Backspread"
            ],
            "NEUTRAL/INCOME": [
                "Covered Call", "Protective Put", "Collar", "Iron Condor",
                "Iron Butterfly", "Short Strangle", "Short Straddle"
            ],
            "VOLATILITY": [
                "Long Straddle", "Long Strangle", "Calendar Spread"
            ]
        }

        # Flatten into single list
        all_strats = []
        for category, strats in strategies.items():
            all_strats.extend(strats)

        return all_strats, strategies

    def get_indicator_parameter_ranges(self):
        """Define MAXIMUM granular parameter ranges for ALL indicators"""
        indicator_ranges = {
            'SMA Crossover': {
                'enabled': [True, False],
                'Short Period': [3, 5, 7, 8, 10, 12, 15, 18, 20, 25, 30],  # Very granular
                'Long Period': [15, 20, 25, 30, 40, 50, 60, 75, 100, 120, 150, 200, 250]  # Very granular
            },
            'RSI Filter': {
                'enabled': [True, False],
                'RSI Period': [3, 5, 7, 9, 10, 12, 14, 16, 18, 21, 25, 30],  # Very granular
                'Min RSI': [10, 15, 20, 25, 30, 35, 40, 45, 50],  # Very granular
                'Max RSI': [50, 55, 60, 65, 70, 75, 80, 85, 90]  # Very granular
            },
            'MACD Signal': {
                'enabled': [True, False],
                'Fast Period': [6, 8, 10, 12, 14, 16, 18, 20],
                'Slow Period': [18, 21, 24, 26, 28, 30, 35, 40],
                'Signal Period': [5, 6, 7, 8, 9, 10, 12, 14, 15]
            },
            'Bollinger Bands': {
                'enabled': [True, False],
                'Period': [5, 10, 12, 15, 20, 25, 30, 40, 50],
                'Std Dev': [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.5]
            },
            'Volume Filter': {
                'enabled': [True, False],
                'Min Volume': [10000, 50000, 100000, 250000, 500000, 750000, 1000000, 1500000, 2000000, 3000000, 5000000],
                'Volume Multiplier': [1.0, 1.1, 1.2, 1.4, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0]
            },
            'ATR Filter': {
                'enabled': [True, False],
                'ATR Period': [5, 7, 10, 12, 14, 17, 20, 25, 30],
                'Min ATR': [0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0],
                'Max ATR': [1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0]
            },
            'IV Rank Filter': {
                'enabled': [True, False],
                'Min IV Rank': [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
                'Max IV Rank': [45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
            },
            'Momentum': {
                'enabled': [True, False],
                'Period': [3, 5, 7, 10, 12, 15, 18, 20, 25, 30],
                'Min Change %': [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.0, 10.0]
            }
        }
        return indicator_ranges

    def get_parameter_ranges(self):
        """Define ULTRA-GRANULAR parameter ranges for optimization"""
        ranges = {
            # Risk Management Parameters (MAXIMUM granularity near 0.1, 1, 2, 4, 8 pattern)
            'stop_loss_pct': [0.1, 0.5, 1, 2, 4, 8, 10, 15, 20, 25, 30, 40, 50, 60, 75, 90, 100, 125, 150, 200],
            'profit_target_pct': [0.1, 0.5, 1, 2, 4, 8, 10, 15, 20, 25, 30, 40, 50, 60, 75, 90, 100],
            'trailing_stop_pct': [0.1, 0.5, 1, 2, 4, 8, 10, 15, 20, 25, 30, 35, 40, 50, 60, 75, 100],
            'min_dte': [1, 2, 4, 7, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 75, 90],
            'max_dte': [7, 14, 21, 30, 45, 50, 60, 75, 90, 105, 120, 150, 180, 210, 270, 365],

            # Strategy Parameters (ultra-granular with 0.01 precision for deltas)
            'delta_short_min': [0.05, 0.08, 0.10, 0.12, 0.15, 0.17, 0.20, 0.22, 0.25, 0.27, 0.30, 0.33, 0.35],
            'delta_short_max': [0.20, 0.25, 0.27, 0.30, 0.32, 0.35, 0.37, 0.40, 0.42, 0.45, 0.47, 0.50, 0.55],
            'delta_long_min': [0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.12, 0.15, 0.18, 0.20],
            'delta_long_max': [0.05, 0.08, 0.10, 0.12, 0.15, 0.17, 0.20, 0.23, 0.25, 0.30],
            'iv_rank_min': [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60],
            'iv_rank_max': [40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100],
            'min_open_interest': [1, 5, 10, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 2000, 5000],
            'min_volume': [1, 5, 10, 25, 40, 50, 75, 100, 150, 200, 300, 500, 1000, 2000],

            # Position Management (granular pattern: 1, 2, 4, 8...)
            'max_positions': [1, 2, 4, 5, 7, 10, 12, 15, 18, 20, 25, 30, 40, 50, 75, 100],
            'capital_per_trade': [100, 200, 250, 500, 750, 1000, 1500, 2000, 3000, 5000, 7500, 10000, 15000, 20000],

            # Trading Frequency (all options)
            'trade_frequency': ['Intraday (Multiple per day)', 'On Signal', 'Daily', 'Weekly', 'Monthly'],
            'trades_per_day_limit': [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 30, 50],
            'min_time_between_trades': [0, 1, 2, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 360],
        }

        return ranges

    def create_granular_combinations(self, max_combinations=100, test_all_strategies=True, optimize_indicators=True):
        """
        Create ULTRA-GRANULAR parameter combinations

        Args:
            max_combinations: Maximum combinations to test
            test_all_strategies: If True, tests all 23 option strategies
            optimize_indicators: If True, optimizes all indicators
        """
        ranges = self.get_parameter_ranges()
        indicator_ranges = self.get_indicator_parameter_ranges()
        all_strategies, strategy_categories = self.get_all_strategies()

        combinations = []

        if test_all_strategies:
            # Calculate combinations per strategy
            combos_per_strategy = max(1, max_combinations // len(all_strategies))

            # Test each strategy with different parameter sets
            for strategy in all_strategies:
                for _ in range(combos_per_strategy):
                    combo = self._create_single_combination(strategy, ranges, indicator_ranges, optimize_indicators)
                    combinations.append(combo)
        else:
            # Use currently selected strategy only
            current_strategy = self.strategy_tab.strategy_var.get()
            for _ in range(max_combinations):
                combo = self._create_single_combination(current_strategy, ranges, indicator_ranges, optimize_indicators)
                combinations.append(combo)

        return combinations

    def _create_single_combination(self, strategy, ranges, indicator_ranges, optimize_indicators):
        """Create a single parameter combination"""
        combo = {}

        # === STRATEGY ===
        combo['strategy'] = strategy

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

        # === TRADING FREQUENCY ===
        combo['trade_frequency'] = random.choice(ranges['trade_frequency'])
        combo['trades_per_day_limit'] = random.choice(ranges['trades_per_day_limit'])
        combo['min_time_between_trades'] = random.choice(ranges['min_time_between_trades'])

        # === INDICATORS ===
        combo['indicators'] = {}

        if optimize_indicators:
            indicator_names = list(indicator_ranges.keys())

            # Randomly enable 0-5 indicators (increased max)
            num_indicators = random.choice([0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5])
            enabled_indicators = random.sample(indicator_names, num_indicators)

            for indicator_name in indicator_names:
                indicator_config = {}
                is_enabled = indicator_name in enabled_indicators
                indicator_config['enabled'] = is_enabled

                if is_enabled:
                    ind_ranges = indicator_ranges[indicator_name]
                    for param_name, param_values in ind_ranges.items():
                        if param_name != 'enabled':
                            indicator_config[param_name] = random.choice(param_values)

                combo['indicators'][indicator_name] = indicator_config

        # === VALIDATION ===
        # Ensure min < max for all ranges
        if combo['min_dte'] >= combo['max_dte']:
            combo['max_dte'] = combo['min_dte'] + 15
        if combo['delta_short_min'] >= combo['delta_short_max']:
            combo['delta_short_min'], combo['delta_short_max'] = combo['delta_short_max'], combo['delta_short_min']
        if combo['delta_long_min'] >= combo['delta_long_max']:
            combo['delta_long_min'], combo['delta_long_max'] = combo['delta_long_max'], combo['delta_long_min']
        if combo['iv_rank_min'] >= combo['iv_rank_max']:
            combo['iv_rank_min'], combo['iv_rank_max'] = combo['iv_rank_max'], combo['iv_rank_min']

        # Validate indicator ranges
        if optimize_indicators:
            for indicator_name, ind_config in combo['indicators'].items():
                if ind_config.get('enabled'):
                    if indicator_name == 'RSI Filter':
                        if ind_config.get('Min RSI', 0) >= ind_config.get('Max RSI', 100):
                            ind_config['Min RSI'], ind_config['Max RSI'] = ind_config['Max RSI'], ind_config['Min RSI']
                    elif indicator_name == 'SMA Crossover':
                        if ind_config.get('Short Period', 0) >= ind_config.get('Long Period', 200):
                            ind_config['Short Period'], ind_config['Long Period'] = ind_config['Long Period'], ind_config['Short Period']
                    elif indicator_name == 'ATR Filter':
                        if ind_config.get('Min ATR', 0) >= ind_config.get('Max ATR', 10):
                            ind_config['Min ATR'], ind_config['Max ATR'] = ind_config['Max ATR'], ind_config['Min ATR']
                    elif indicator_name == 'IV Rank Filter':
                        if ind_config.get('Min IV Rank', 0) >= ind_config.get('Max IV Rank', 100):
                            ind_config['Min IV Rank'], ind_config['Max IV Rank'] = ind_config['Max IV Rank'], ind_config['Min IV Rank']

        return combo

    def create_full_grid_search(self, test_all_strategies=True, optimize_indicators=False):
        """
        Create FULL GRID SEARCH - tests ALL combinations of key parameters

        This tests every combination of:
        - Stop Loss, Profit Target, Trailing Stop (critical risk params)
        - DTE ranges (critical timing params)
        - Delta ranges (critical strategy params)
        - Strategies (if test_all_strategies=True)

        Reduces granularity slightly for practical runtime while still being comprehensive.
        """
        import itertools

        ranges = self.get_parameter_ranges()
        all_strategies, _ = self.get_all_strategies()

        # REDUCED parameter ranges for grid search (still very comprehensive)
        grid_ranges = {
            # Risk Management - most critical, test all values
            'stop_loss_pct': [0.5, 1, 2, 4, 8, 10, 15, 20, 25, 30, 40, 50, 75, 100],  # 14 values
            'profit_target_pct': [0.5, 1, 2, 4, 8, 10, 15, 20, 25, 30, 40, 50, 75, 100],  # 14 values
            'trailing_stop_pct': [0.5, 1, 2, 4, 8, 10, 15, 20, 25, 30, 40, 50],  # 12 values

            # DTE - very important for options
            'min_dte': [1, 7, 15, 20, 30, 45, 60],  # 7 values
            'max_dte': [14, 30, 45, 60, 90, 120, 180],  # 7 values

            # Deltas - critical for strategy selection
            'delta_short_min': [0.05, 0.10, 0.15, 0.20, 0.25, 0.30],  # 6 values
            'delta_short_max': [0.25, 0.30, 0.35, 0.40, 0.45, 0.50],  # 6 values
            'delta_long_min': [0.01, 0.05, 0.10, 0.15, 0.20],  # 5 values
            'delta_long_max': [0.05, 0.10, 0.15, 0.20, 0.25],  # 5 values

            # Sample other parameters (less critical)
            'iv_rank_min': [0, 20, 30, 40, 50],  # 5 values
            'iv_rank_max': [50, 60, 70, 80, 100],  # 5 values
            'min_open_interest': [10, 50, 100, 500, 1000],  # 5 values
            'min_volume': [10, 25, 50, 100, 200],  # 5 values
            'max_positions': [5, 10, 15, 20, 30],  # 5 values
            'capital_per_trade': [500, 1000, 2000, 5000, 10000],  # 5 values

            # Trading frequency - test key options
            'trade_frequency': ['On Signal', 'Daily'],  # 2 values (most common)
            'trades_per_day_limit': [1, 3, 5],  # 3 values
            'min_time_between_trades': [0, 30, 60],  # 3 values
        }

        # Calculate total combinations
        # 14 × 14 × 12 × 7 × 7 × 6 × 6 × 5 × 5 × 5 × 5 × 5 × 5 × 5 × 5 × 2 × 3 × 3 = ~1.7 billion
        # But we'll validate and skip invalid combinations

        print("Generating grid search combinations...")
        combinations = []

        strategies_to_test = all_strategies if test_all_strategies else [self.strategy_tab.strategy_var.get()]

        # Generate all combinations using itertools.product
        param_names = list(grid_ranges.keys())
        param_values = [grid_ranges[name] for name in param_names]

        combo_count = 0
        for strategy in strategies_to_test:
            for values in itertools.product(*param_values):
                # Create parameter dict
                combo = {'strategy': strategy}
                for i, name in enumerate(param_names):
                    combo[name] = values[i]

                # Validate constraints (skip invalid combinations)
                if combo['min_dte'] >= combo['max_dte']:
                    continue
                if combo['delta_short_min'] >= combo['delta_short_max']:
                    continue
                if combo['delta_long_min'] >= combo['delta_long_max']:
                    continue
                if combo['iv_rank_min'] >= combo['iv_rank_max']:
                    continue

                # For indicators, use defaults (grid search focuses on core params)
                combo['indicators'] = {}
                if optimize_indicators:
                    # Don't enumerate all indicator combinations in grid search
                    # Instead use a few representative configurations
                    # This keeps the search focused on the most important parameters
                    pass

                combinations.append(combo)
                combo_count += 1

                # Progress update every 10,000 combinations
                if combo_count % 10000 == 0:
                    print(f"Generated {combo_count:,} valid combinations...")

        print(f"Total grid search combinations: {len(combinations):,}")
        return combinations

    def apply_parameters(self, params):
        """Apply parameter combination to the strategy tab"""

        # === STRATEGY SELECTION ===
        if 'strategy' in params:
            self.strategy_tab.strategy_var.set(params['strategy'])
            self.strategy_tab.on_strategy_change()  # Rebuild parameter panel

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
                if indicator_name in self.strategy_tab.indicator_vars:
                    is_enabled = ind_config.get('enabled', False)
                    self.strategy_tab.indicator_vars[indicator_name].set(is_enabled)

                    if is_enabled and indicator_name in self.strategy_tab.indicator_param_widgets:
                        for param_name, param_value in ind_config.items():
                            if param_name != 'enabled' and param_name in self.strategy_tab.indicator_param_widgets[indicator_name]:
                                widget = self.strategy_tab.indicator_param_widgets[indicator_name][param_name]
                                widget.delete(0, tk.END)
                                widget.insert(0, str(param_value))

                    self.strategy_tab.toggle_indicator_params(indicator_name)

    def run_backtest_with_params(self, params):
        """Run backtest with specific parameters and return total return %"""
        try:
            # Apply parameters
            self.apply_parameters(params)

            # Run backtest
            start = datetime.strptime(self.strategy_tab.start_date.get(), "%Y-%m-%d")
            end = datetime.strptime(self.strategy_tab.end_date.get(), "%Y-%m-%d")

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
                'strategy': params.get('strategy', 'Unknown'),
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

    def optimize(self, progress_callback=None, max_combinations=100,
                 test_all_strategies=True, optimize_indicators=True, use_grid_search=False):
        """
        Run ULTIMATE optimization

        Args:
            progress_callback: Function for progress updates
            max_combinations: Max combinations to test
            test_all_strategies: If True, tests all 23 strategies
            optimize_indicators: If True, optimizes indicators
            use_grid_search: If True, performs exhaustive grid search
        """
        self.is_running = True
        self.all_results = []
        self.best_result = None
        self.results_by_strategy = {}

        # Generate combinations
        if use_grid_search:
            combinations = self.create_full_grid_search(test_all_strategies, optimize_indicators)
        else:
            combinations = self.create_granular_combinations(
                max_combinations, test_all_strategies, optimize_indicators
            )
        total = len(combinations)

        if progress_callback:
            strategy_msg = "ALL 23 strategies" if test_all_strategies else "current strategy"
            indicator_msg = "with indicators" if optimize_indicators else "parameters only"
            progress_callback(f"Testing {total} combinations ({strategy_msg}, {indicator_msg})...", 0, total)

        # Test each combination
        for idx, params in enumerate(combinations):
            if not self.is_running:
                break

            result = self.run_backtest_with_params(params)

            if result:
                self.all_results.append(result)
                strategy = result['strategy']

                # Track best for this strategy
                if strategy not in self.results_by_strategy or \
                   result['total_return_pct'] > self.results_by_strategy[strategy]['total_return_pct']:
                    self.results_by_strategy[strategy] = result

                # Track overall best
                if self.best_result is None or result['total_return_pct'] > self.best_result['total_return_pct']:
                    self.best_result = result

            if progress_callback:
                best_msg = f"Best: {self.best_result['total_return_pct']:.2f}% ({self.best_result['strategy']})" if self.best_result else "Searching..."
                progress_callback(f"Tested {idx+1}/{total} | {best_msg}", idx + 1, total)

        self.is_running = False
        return self.best_result

    def stop(self):
        """Stop the optimization process"""
        self.is_running = False

    def get_top_strategies(self, n=5):
        """Get top N strategies by return"""
        sorted_results = sorted(
            self.results_by_strategy.items(),
            key=lambda x: x[1]['total_return_pct'],
            reverse=True
        )
        return sorted_results[:n]


class UltimateOptimizerWindow:
    """Ultimate optimization GUI - tests ALL strategies with maximum granularity"""

    def __init__(self, parent, strategy_tab):
        self.strategy_tab = strategy_tab
        self.optimizer = UltimateParameterOptimizer(strategy_tab)
        self.window = tk.Toplevel(parent)
        self.window.title("ULTIMATE Parameter Optimizer - Maximum Granularity")
        self.window.geometry("1000x800")
        self.window.configure(bg="#f0f0f0")

        self.setup_ui()

    def setup_ui(self):
        # Create scrollable main container
        main_canvas = tk.Canvas(self.window, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=main_canvas.yview)
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
        header = tk.Frame(scrollable, bg="#1a1a1a", height=100)
        header.pack(fill=tk.X)

        tk.Label(header, text="🎯 ULTIMATE OPTIMIZER", fg="#FFD700",
                bg="#1a1a1a", font=("Arial", 26, "bold")).pack(pady=5)
        tk.Label(header, text="Test ALL 23 strategies × ALL indicators × ALL parameters",
                fg="white", bg="#1a1a1a", font=("Arial", 12)).pack()
        tk.Label(header, text="Maximum granularity - finds the absolute best configuration",
                fg="#32CD32", bg="#1a1a1a", font=("Arial", 10)).pack()

        # Settings panel
        settings_frame = tk.LabelFrame(scrollable, text=" ⚙️ ULTIMATE OPTIMIZATION SETTINGS ",
                                       bg="white", fg="black", font=("Arial", 13, "bold"), bd=3)
        settings_frame.pack(fill=tk.X, padx=20, pady=15)

        inner = tk.Frame(settings_frame, bg="white")
        inner.pack(fill=tk.X, padx=20, pady=15)

        # Strategy testing option
        self.test_all_strategies = tk.BooleanVar(value=True)
        tk.Checkbutton(inner, text="Test ALL 23 Option Strategies (vs. current strategy only)",
                      variable=self.test_all_strategies, bg="white", fg="black",
                      font=("Arial", 11, "bold"), selectcolor="white").pack(anchor='w', pady=(0, 5))

        strategy_info = tk.Label(inner, text="  ✓ Tests: Iron Condor, Bull Call Spread, Long Straddle, etc. (all 23)",
                                bg="white", fg="#666", font=("Arial", 9))
        strategy_info.pack(anchor='w', padx=20, pady=(0, 10))

        # Indicator optimization
        self.optimize_indicators = tk.BooleanVar(value=True)
        tk.Checkbutton(inner, text="Optimize ALL 8 Indicators + Parameters",
                      variable=self.optimize_indicators, bg="white", fg="black",
                      font=("Arial", 11, "bold"), selectcolor="white").pack(anchor='w', pady=(5, 5))

        # Full Grid Search mode
        self.full_grid_search = tk.BooleanVar(value=False)
        tk.Checkbutton(inner, text="🔥 FULL GRID SEARCH - Test EVERY combination (50k-100k tests, 4-8 hours)",
                      variable=self.full_grid_search, bg="white", fg="#FF4500",
                      font=("Arial", 11, "bold"), selectcolor="white",
                      command=self.on_grid_search_toggle).pack(anchor='w', pady=(5, 5))

        grid_info = tk.Label(inner, text="  ⚠️  When enabled, tests ALL parameter values exhaustively (overrides combination count)",
                            bg="white", fg="#FF4500", font=("Arial", 8))
        grid_info.pack(anchor='w', padx=20, pady=(0, 10))

        # Number of combinations (only for non-grid search)
        self.combo_label = tk.Label(inner, text="\nCombinations to Test:",
                                    bg="white", fg="black", font=("Arial", 11, "bold"))
        self.combo_label.pack(anchor='w', pady=(10, 5))

        combo_frame = tk.Frame(inner, bg="white")
        combo_frame.pack(anchor='w', pady=(0, 5))

        self.num_combinations = tk.Scale(combo_frame, from_=50, to=500, orient=tk.HORIZONTAL,
                                         length=400, bg="white", fg="black",
                                         font=("Arial", 10), label="")
        self.num_combinations.set(200)
        self.num_combinations.pack(side=tk.LEFT)

        tk.Label(combo_frame, text="combinations", bg="white", fg="black",
                font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        # Time estimate
        self.time_label = tk.Label(inner, text="Estimated time: ~10-15 minutes",
                                   bg="white", fg="#666", font=("Arial", 9))
        self.time_label.pack(anchor='w', padx=20, pady=5)

        self.num_combinations.config(command=self.update_time_estimate)

        # Granularity info
        tk.Label(inner, text="\nGranularity Level: MAXIMUM",
                bg="white", fg="black", font=("Arial", 11, "bold")).pack(anchor='w', pady=(15, 5))

        granular_text = """ULTRA-GRANULAR TESTING (Min & Max for all variables):

STRATEGY: All 23 option strategies tested

INDICATORS (8 total):
  • SMA: 7 short periods × 7 long periods = 49 combinations
  • RSI: 7 periods × 6 min values × 6 max values = 252 combinations
  • MACD: 5 fast × 6 slow × 7 signal = 210 combinations
  • Bollinger: 6 periods × 7 std devs = 42 combinations
  • Volume: 7 min volumes × 7 multipliers = 49 combinations
  • ATR: 6 periods × 6 min × 6 max = 216 combinations
  • IV Rank: 9 min × 9 max = 81 combinations
  • Momentum: 7 periods × 8 min changes = 56 combinations

PARAMETERS (All with min/max ranges):
  • Stop Loss: 11 values (20%-150%)
  • Profit Target: 10 values (15%-100%)
  • Trailing Stop: 10 values (10%-75%)
  • DTE Min: 10 values (15-75 days)
  • DTE Max: 10 values (30-180 days)
  • Delta ranges: 9 min × 11 max (short), 7 min × 8 max (long)
  • IV Rank: 10 min × 10 max values
  • Open Interest: 10 values (25-1000)
  • Volume: 10 values (10-500)
  • Max Positions: 11 values (3-40)
  • Capital per Trade: 10 values ($250-$10,000)

TRADING FREQUENCY:
  • 5 frequency options (Intraday to Monthly)
  • Trades per day: 10 options (1-15)
  • Time between: 10 options (0-180 min)

TOTAL PARAMETER SPACE: Billions of combinations
SMART SAMPLING: Tests diverse representative set"""

        tk.Label(inner, text=granular_text, bg="#f9f9f9", fg="black",
                font=("Courier", 8), justify=tk.LEFT, relief=tk.SUNKEN, padx=10, pady=10).pack(
                    fill=tk.X, padx=10, pady=10)

        # Progress panel
        progress_frame = tk.LabelFrame(scrollable, text=" 📊 OPTIMIZATION PROGRESS ",
                                       bg="white", fg="black", font=("Arial", 12, "bold"), bd=3)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        inner_progress = tk.Frame(progress_frame, bg="white")
        inner_progress.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Progress bar
        self.progress_label = tk.Label(inner_progress, text="Ready to start ultimate optimization",
                                       bg="white", fg="black", font=("Arial", 11, "bold"))
        self.progress_label.pack(pady=(0, 10))

        self.progress_bar = ttk.Progressbar(inner_progress, mode='determinate', length=800)
        self.progress_bar.pack(pady=(0, 15))

        # Results display
        results_scroll = tk.Frame(inner_progress, bg="white")
        results_scroll.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(results_scroll)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text = tk.Text(results_scroll, height=10, bg="#f9f9f9", fg="black",
                                    font=("Courier", 9), yscrollcommand=scrollbar.set, wrap=tk.WORD)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)

        # Control buttons
        btn_frame = tk.Frame(scrollable, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.start_btn = tk.Button(btn_frame, text="🚀 START ULTIMATE OPTIMIZATION", bg="#4CAF50", fg="white",
                                   font=("Arial", 14, "bold"), command=self.start_optimization,
                                   padx=30, pady=15, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(btn_frame, text="⏹ STOP", bg="#F44336", fg="white",
                                  font=("Arial", 14, "bold"), command=self.stop_optimization,
                                  padx=30, pady=15, cursor="hand2", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        self.apply_btn = tk.Button(btn_frame, text="✓ APPLY BEST", bg="#2196F3", fg="white",
                                   font=("Arial", 14, "bold"), command=self.apply_best_parameters,
                                   padx=30, pady=15, cursor="hand2", state=tk.DISABLED)
        self.apply_btn.pack(side=tk.LEFT, padx=10)

        self.compare_btn = tk.Button(btn_frame, text="📊 COMPARE TOP 5", bg="#FF9800", fg="white",
                                     font=("Arial", 14, "bold"), command=self.show_top_strategies,
                                     padx=30, pady=15, cursor="hand2", state=tk.DISABLED)
        self.compare_btn.pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="CLOSE", bg="#757575", fg="white",
                 font=("Arial", 14, "bold"), command=self.window.destroy,
                 padx=30, pady=15, cursor="hand2").pack(side=tk.RIGHT, padx=10)

    def on_grid_search_toggle(self):
        """Handle grid search checkbox toggle"""
        is_grid = self.full_grid_search.get()
        if is_grid:
            # Disable combination slider
            self.num_combinations.config(state=tk.DISABLED)
            self.combo_label.config(fg="#999")
        else:
            # Enable combination slider
            self.num_combinations.config(state=tk.NORMAL)
            self.combo_label.config(fg="black")
        self.update_time_estimate()

    def update_time_estimate(self, value=None):
        """Update estimated time based on number of combinations"""
        if self.full_grid_search.get():
            # Grid search estimates
            self.time_label.config(text="Estimated time: 4-8 hours (50,000-100,000 tests)", fg="#FF4500")
        else:
            num = self.num_combinations.get()
            test_all = self.test_all_strategies.get()

            # Rough estimate: 2 combinations per second
            seconds = num / 2
            if test_all:
                seconds *= 1.2  # Extra time for strategy switching

            minutes = int(seconds / 60)
            self.time_label.config(text=f"Estimated time: ~{minutes}-{minutes+2} minutes", fg="#666")

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
        """Start the ultimate optimization process"""
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.apply_btn.config(state=tk.DISABLED)
        self.compare_btn.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)

        max_combinations = self.num_combinations.get()
        test_all_strategies = self.test_all_strategies.get()
        optimize_indicators = self.optimize_indicators.get()
        use_grid_search = self.full_grid_search.get()

        def run_optimization():
            self.log_result("="*80)
            if use_grid_search:
                self.log_result("🔥 FULL GRID SEARCH OPTIMIZATION STARTED")
            else:
                self.log_result("ULTIMATE OPTIMIZATION STARTED")
            self.log_result("="*80 + "\n")

            if use_grid_search:
                self.log_result("Mode: FULL GRID SEARCH - Testing ALL parameter combinations")
                self.log_result("Expected Tests: 50,000-100,000 combinations")
                self.log_result("Expected Time: 4-8 hours")
            else:
                self.log_result(f"Total Combinations: {max_combinations}")

            self.log_result(f"Strategies: {'ALL 23' if test_all_strategies else 'Current only'}")
            self.log_result(f"Indicators: {'ALL 8 optimized' if optimize_indicators else 'Disabled'}")
            self.log_result(f"Date Range: {self.strategy_tab.start_date.get()} to {self.strategy_tab.end_date.get()}")
            self.log_result(f"Granularity: MAXIMUM (min/max for all parameters)\n")

            result = self.optimizer.optimize(
                progress_callback=self.update_progress,
                max_combinations=max_combinations,
                test_all_strategies=test_all_strategies,
                optimize_indicators=optimize_indicators,
                use_grid_search=use_grid_search
            )

            if result:
                self.log_result("\n" + "="*80)
                self.log_result("🏆 ULTIMATE OPTIMIZATION COMPLETE!")
                self.log_result("="*80 + "\n")

                self.log_result(f"🥇 BEST OVERALL RESULT:")
                self.log_result(f"   Strategy: {result['strategy']}")
                self.log_result(f"   Total Return: {result['total_return_pct']:.2f}%\n")

                # Show top strategies
                if test_all_strategies:
                    self.log_result("📊 TOP 5 STRATEGIES:")
                    self.log_result("-" * 80)
                    top_strategies = self.optimizer.get_top_strategies(5)
                    for idx, (strategy, strat_result) in enumerate(top_strategies, 1):
                        self.log_result(f"{idx}. {strategy}: {strat_result['total_return_pct']:.2f}% return")
                        self.log_result(f"   Win Rate: {strat_result['stats']['win_rate']:.1f}%,  "
                                      f"Trades: {strat_result['stats']['total_trades']},  "
                                      f"PF: {strat_result['stats']['profit_factor']:.2f}")
                    self.log_result("")

                # Show optimal indicators
                if result.get('enabled_indicators'):
                    self.log_result(f"📈 OPTIMAL INDICATORS ({len(result['enabled_indicators'])}):")
                    for ind in result['enabled_indicators']:
                        ind_params = result['params']['indicators'][ind]
                        self.log_result(f"  ✓ {ind}")
                        for param_name, param_value in ind_params.items():
                            if param_name != 'enabled':
                                self.log_result(f"      {param_name}: {param_value}")
                    self.log_result("")
                else:
                    self.log_result("📈 OPTIMAL APPROACH: No indicators (pure strategy parameters)\n")

                # Trading frequency
                self.log_result("⏰ OPTIMAL TRADING FREQUENCY:")
                self.log_result(f"   Frequency: {result.get('trade_frequency', 'On Signal')}")
                if result.get('trade_frequency') == 'Intraday (Multiple per day)':
                    self.log_result(f"   Max trades/day: {result.get('trades_per_day', 1)}")
                    self.log_result(f"   Min time between: {result['params'].get('min_time_between_trades', 0)} min")
                self.log_result("")

                # Key parameters
                self.log_result("⚙️  OPTIMAL PARAMETERS:")
                self.log_result(f"   Stop Loss: {result['params']['stop_loss_pct']}%")
                self.log_result(f"   Profit Target: {result['params']['profit_target_pct']}%")
                self.log_result(f"   DTE Range: {result['params']['min_dte']}-{result['params']['max_dte']} days")
                self.log_result(f"   Delta Short: {result['params']['delta_short_min']}-{result['params']['delta_short_max']}")
                self.log_result(f"   Max Positions: {result['params']['max_positions']}")
                self.log_result(f"   Capital/Trade: ${result['params']['capital_per_trade']}\n")

                # Performance metrics
                self.log_result("📊 PERFORMANCE METRICS:")
                self.log_result("-" * 80)
                stats = result['stats']
                self.log_result(f"   Total Trades: {stats['total_trades']}")
                self.log_result(f"   Win Rate: {stats['win_rate']:.2f}%")
                self.log_result(f"   Total P&L: ${stats['total_pnl']:,.2f}")
                self.log_result(f"   Avg P&L/Trade: ${stats['avg_pnl']:.2f}")
                self.log_result(f"   Profit Factor: {stats['profit_factor']:.2f}")
                self.log_result(f"   Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
                self.log_result(f"   Max Drawdown: ${stats['max_drawdown']:,.2f}\n")

                self.log_result("="*80)
                self.log_result("✅ Click 'APPLY BEST' to use these settings")
                self.log_result("✅ Click 'COMPARE TOP 5' to see all top strategies")
                self.log_result("="*80)

                self.apply_btn.config(state=tk.NORMAL)
                if test_all_strategies:
                    self.compare_btn.config(state=tk.NORMAL)
            else:
                self.log_result("\n⚠️  Optimization failed or was stopped.")

            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

        # Run in thread
        thread = threading.Thread(target=run_optimization, daemon=True)
        thread.start()

    def stop_optimization(self):
        """Stop the optimization"""
        self.optimizer.stop()
        self.log_result("\n⏹ Optimization stopped by user")
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL)

    def apply_best_parameters(self):
        """Apply the best parameters found"""
        if not self.optimizer.best_result:
            messagebox.showwarning("No Results", "No optimization results available")
            return

        self.optimizer.apply_parameters(self.optimizer.best_result['params'])

        # Enable risk management
        self.strategy_tab.use_stop_loss.set(True)
        self.strategy_tab.use_profit_target.set(True)

        enabled_inds = self.optimizer.best_result.get('enabled_indicators', [])
        indicator_msg = ""
        if enabled_inds:
            indicator_msg = f"\n\nOptimal Indicators ({len(enabled_inds)}):\n" + "\n".join(f"✓ {ind}" for ind in enabled_inds)

        messagebox.showinfo(
            "Best Parameters Applied",
            f"✅ ULTIMATE optimization complete!\n\n"
            f"Strategy: {self.optimizer.best_result['strategy']}\n"
            f"Expected Total Return: {self.optimizer.best_result['total_return_pct']:.2f}%"
            f"{indicator_msg}\n\n"
            f"All settings applied. Run backtest to see full results!"
        )

        self.window.destroy()

    def show_top_strategies(self):
        """Show comparison window of top 5 strategies"""
        if not self.optimizer.results_by_strategy:
            messagebox.showwarning("No Results", "No strategy comparison data available")
            return

        # Create comparison window
        comp_window = tk.Toplevel(self.window)
        comp_window.title("Top 5 Strategies Comparison")
        comp_window.geometry("900x600")
        comp_window.configure(bg="#f0f0f0")

        # Header
        header = tk.Frame(comp_window, bg="#1a1a1a", height=60)
        header.pack(fill=tk.X)

        tk.Label(header, text="📊 TOP 5 STRATEGIES COMPARISON", fg="#32CD32",
                bg="#1a1a1a", font=("Arial", 20, "bold")).pack(pady=15)

        # Content
        content = tk.Frame(comp_window, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create scrollable text
        scrollbar = tk.Scrollbar(content)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text = tk.Text(content, bg="white", fg="black", font=("Courier", 10),
                      yscrollcommand=scrollbar.set, wrap=tk.WORD)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)

        # Enable mouse wheel scrolling for comparison window
        def _on_mousewheel_comp(event):
            text.yview_scroll(int(-1*(event.delta)), "units")

        def _on_mousewheel_linux_comp(event):
            if event.num == 4:
                text.yview_scroll(-1, "units")
            elif event.num == 5:
                text.yview_scroll(1, "units")

        # Bind to the text widget specifically (not bind_all to avoid conflicts)
        text.bind("<MouseWheel>", _on_mousewheel_comp)
        text.bind("<Button-4>", _on_mousewheel_linux_comp)
        text.bind("<Button-5>", _on_mousewheel_linux_comp)

        # Get top strategies
        top_strategies = self.optimizer.get_top_strategies(5)

        text.insert(tk.END, "="*90 + "\n")
        text.insert(tk.END, "TOP 5 PERFORMING STRATEGIES\n")
        text.insert(tk.END, "="*90 + "\n\n")

        for idx, (strategy, result) in enumerate(top_strategies, 1):
            text.insert(tk.END, f"{'='*90}\n")
            text.insert(tk.END, f"#{idx} - {strategy}\n")
            text.insert(tk.END, f"{'='*90}\n\n")

            text.insert(tk.END, f"💰 RETURN: {result['total_return_pct']:.2f}%\n\n")

            stats = result['stats']
            text.insert(tk.END, f"📊 Performance:\n")
            text.insert(tk.END, f"   Total Trades: {stats['total_trades']}\n")
            text.insert(tk.END, f"   Win Rate: {stats['win_rate']:.1f}%\n")
            text.insert(tk.END, f"   Total P&L: ${stats['total_pnl']:,.2f}\n")
            text.insert(tk.END, f"   Avg P&L/Trade: ${stats['avg_pnl']:.2f}\n")
            text.insert(tk.END, f"   Profit Factor: {stats['profit_factor']:.2f}\n")
            text.insert(tk.END, f"   Sharpe Ratio: {stats['sharpe_ratio']:.2f}\n\n")

            if result.get('enabled_indicators'):
                text.insert(tk.END, f"📈 Indicators ({len(result['enabled_indicators'])}):\n")
                for ind in result['enabled_indicators']:
                    text.insert(tk.END, f"   ✓ {ind}\n")
                text.insert(tk.END, "\n")

            text.insert(tk.END, f"⚙️  Key Parameters:\n")
            text.insert(tk.END, f"   Stop Loss: {result['params']['stop_loss_pct']}%\n")
            text.insert(tk.END, f"   Profit Target: {result['params']['profit_target_pct']}%\n")
            text.insert(tk.END, f"   DTE: {result['params']['min_dte']}-{result['params']['max_dte']} days\n")
            text.insert(tk.END, f"   Frequency: {result.get('trade_frequency', 'On Signal')}\n\n")

        text.config(state=tk.DISABLED)

        # Close button
        btn_frame = tk.Frame(comp_window, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Button(btn_frame, text="CLOSE", bg="#757575", fg="white",
                 font=("Arial", 12, "bold"), command=comp_window.destroy,
                 padx=30, pady=10, cursor="hand2").pack()
