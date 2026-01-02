#!/usr/bin/env python3
"""
Advanced Options Strategy Backtesting Platform
Uses Massive API for historical options data
"""

import tkinter as tk
from tkinter import ttk
import os

# Try to import from config.py first, fallback to .env
try:
    import config
    api_key_source = config.MASSIVE_API_KEY
except ImportError:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key_source = os.getenv('MASSIVE_API_KEY')
    except:
        api_key_source = None

class OptionsBacktestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Options Strategy Backtester")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a1a")
        
        # Application state
        self.selected_tickers = set()
        self.full_universe = []
        self.backtest_results = None
        self.api_key = api_key_source
        
        if not self.api_key:
            from tkinter import messagebox
            messagebox.showerror("API Key Missing", 
                "MASSIVE_API_KEY not found in environment variables.\n"
                "Please create a .env file with your API key.")
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Style configuration
        self.setup_styles()
        
        # Import and create tabs
        from tab_stock_selection import StockSelectionTab
        from tab_strategy_config import StrategyConfigTab
        from tab_backtest_results import BacktestResultsTab
        from tab_equity_curve import EquityCurveTab
        from tab_trade_visualization import TradeVisualizationTab

        # Initialize tabs
        self.stock_tab = StockSelectionTab(self.notebook, self)
        self.strategy_tab = StrategyConfigTab(self.notebook, self)
        self.results_tab = BacktestResultsTab(self.notebook, self)
        self.equity_tab = EquityCurveTab(self.notebook, self)
        self.viz_tab = TradeVisualizationTab(self.notebook, self)

        # Add tabs to notebook
        self.notebook.add(self.stock_tab.frame, text="📊 Stock Selection")
        self.notebook.add(self.strategy_tab.frame, text="⚙️ Strategy Configuration", state="disabled")
        self.notebook.add(self.equity_tab.frame, text="📈 Equity Curve", state="disabled")
        self.notebook.add(self.results_tab.frame, text="📋 Detailed Results", state="disabled")
        self.notebook.add(self.viz_tab.frame, text="📉 Trade Visualization", state="disabled")
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Notebook style
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2d2d2d', foreground='white', 
                       padding=[20, 10], font=('Arial', 11, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#32CD32')],
                 foreground=[('selected', 'black')])
    
    def enable_strategy_tab(self):
        """Enable strategy configuration tab"""
        self.notebook.tab(1, state="normal")
    
    def enable_analysis_tabs(self):
        """Enable analysis tabs after backtest"""
        self.notebook.tab(2, state="normal")
        self.notebook.tab(3, state="normal")
        self.notebook.tab(4, state="normal")

def main():
    root = tk.Tk()
    app = OptionsBacktestApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()