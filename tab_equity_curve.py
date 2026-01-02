import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

class EquityCurveTab:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg="#f5f5f5")
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.frame, bg="#1a1a1a", height=70)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="EQUITY CURVE & PERFORMANCE", fg="#32CD32",
                bg="#1a1a1a", font=("Arial", 24, "bold")).pack(pady=15)
        
        # Main content area
        content = tk.Frame(self.frame, bg="#f5f5f5")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Stats panel (top) - very compact
        self.stats_frame = tk.LabelFrame(content, text=" 📊 PERFORMANCE SUMMARY ",
                                        bg="white", fg="black",
                                        font=("Arial", 10, "bold"), bd=1)
        self.stats_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Chart panel (bottom)
        chart_frame = tk.LabelFrame(content, text=" 📈 EQUITY CURVE ",
                                   bg="white", fg="black",
                                   font=("Arial", 13, "bold"), bd=3)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 6), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Navigation buttons
        nav_frame = tk.Frame(self.frame, bg="#f5f5f5")
        nav_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Button(nav_frame, text="⬅ BACK TO CONFIG", bg="#757575", fg="white",
                 font=("Arial", 13, "bold"), command=lambda: self.app.notebook.select(1),
                 padx=25, pady=12, cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(nav_frame, text="VIEW DETAILED RESULTS →", bg="#2196F3", fg="white",
                 font=("Arial", 13, "bold"), command=lambda: self.app.notebook.select(3),
                 padx=25, pady=12, cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(nav_frame, text="💾 EXPORT RESULTS", bg="#4CAF50", fg="white",
                 font=("Arial", 13, "bold"), command=self.export_results,
                 padx=25, pady=12, cursor="hand2").pack(side=tk.RIGHT, padx=10)
    
    def display_results(self, results: dict):
        """Display backtest results"""
        stats = results['stats']
        equity_curve = results['equity_curve']

        # Clear previous stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # Create stats grid - very compact
        stats_grid = tk.Frame(self.stats_frame, bg="white")
        stats_grid.pack(fill=tk.X, padx=10, pady=5)

        # Calculate total return percentage
        starting_capital = 20000
        total_return_pct = (stats['total_pnl'] / starting_capital) * 100

        # Define stats to display (5 per row for even more compactness)
        stat_items = [
            ("Trades", stats['total_trades'], "#2196F3"),
            ("Win Rate", f"{stats['win_rate']}%", "#4CAF50" if stats['win_rate'] >= 50 else "#F44336"),
            ("Total Return", f"{total_return_pct:+.2f}%", "#4CAF50" if total_return_pct > 0 else "#F44336"),
            ("Total P&L", f"${stats['total_pnl']:,.2f}", "#4CAF50" if stats['total_pnl'] > 0 else "#F44336"),
            ("Avg P&L", f"${stats['avg_pnl']:,.2f}", "#2196F3"),
            ("Avg Win", f"${stats['avg_win']:,.2f}", "#4CAF50"),
            ("Avg Loss", f"${stats['avg_loss']:,.2f}", "#F44336"),
            ("Profit Factor", f"{stats['profit_factor']:.2f}", "#2196F3"),
            ("Max DD", f"${stats['max_drawdown']:,.2f}", "#F44336"),
            ("Sharpe", f"{stats['sharpe_ratio']:.2f}", "#2196F3"),
        ]

        # 5 columns per row instead of 3
        for idx, (label, value, color) in enumerate(stat_items):
            row = idx // 5
            col = idx % 5

            stat_box = tk.Frame(stats_grid, bg="#f0f0f0", relief=tk.FLAT, bd=1, highlightbackground="#d0d0d0", highlightthickness=1)
            stat_box.grid(row=row, column=col, padx=3, pady=2, sticky='nsew')

            tk.Label(stat_box, text=label, bg="#f0f0f0", fg="#666666",
                    font=("Arial", 8)).pack(pady=(3, 0))

            tk.Label(stat_box, text=str(value), bg="#f0f0f0", fg=color,
                    font=("Arial", 12, "bold")).pack(pady=(0, 3), padx=5)
        
        # Configure grid weights for 5 columns
        for i in range(5):
            stats_grid.columnconfigure(i, weight=1)
        
        # Plot equity curve
        self.plot_equity_curve(equity_curve, stats)
    
    def plot_equity_curve(self, equity_curve: list, stats: dict):
        """Plot the equity curve"""
        if not equity_curve:
            return

        # Clear previous plot
        self.ax.clear()

        # Starting capital
        starting_capital = 20000

        # Prepare data
        df = pd.DataFrame(equity_curve)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Calculate account balance (starting capital + cumulative P&L)
        df['account_balance'] = starting_capital + df['cumulative_pnl']

        # Calculate final balance and return
        final_balance = df['account_balance'].iloc[-1]
        total_return_pct = ((final_balance - starting_capital) / starting_capital) * 100

        # Determine profit/loss color
        line_color = '#4CAF50' if final_balance >= starting_capital else '#F44336'

        # Plot account balance with thicker line
        self.ax.plot(df['date'], df['account_balance'],
                    linewidth=3, color=line_color, label='Portfolio Value', zorder=3)

        # Add starting capital reference line
        self.ax.axhline(y=starting_capital, color='#666666', linestyle=':',
                       linewidth=1.5, alpha=0.6, zorder=1)

        # Fill area above/below starting capital
        self.ax.fill_between(df['date'], df['account_balance'], starting_capital,
                            where=(df['account_balance'] >= starting_capital),
                            color='#4CAF50', alpha=0.15, zorder=2)
        self.ax.fill_between(df['date'], df['account_balance'], starting_capital,
                            where=(df['account_balance'] < starting_capital),
                            color='#F44336', alpha=0.15, zorder=2)

        # Add text annotations for start and end
        self.ax.text(df['date'].iloc[0], starting_capital,
                    f'  Start: ${starting_capital:,.0f}',
                    fontsize=10, va='center', ha='left',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#666666', alpha=0.9))

        self.ax.text(df['date'].iloc[-1], final_balance,
                    f'  End: ${final_balance:,.0f}\n  ({total_return_pct:+.1f}%)',
                    fontsize=10, va='center', ha='left',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor=line_color, edgecolor=line_color, alpha=0.2))

        # Clean styling
        self.ax.set_xlabel('Date', fontsize=11, color='#333333')
        self.ax.set_ylabel('Portfolio Value ($)', fontsize=11, color='#333333')
        self.ax.set_title(f'Account Growth - {stats["total_trades"]} Trades',
                         fontsize=14, fontweight='bold', color='#333333', pad=15)

        # Lighter grid
        self.ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#cccccc')
        self.ax.set_facecolor('#fafafa')

        # Remove top and right spines for cleaner look
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#cccccc')
        self.ax.spines['bottom'].set_color('#cccccc')
        
        # Format y-axis as currency
        self.ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: f'${x:,.0f}')
        )
        
        # Rotate x-axis labels
        self.fig.autofmt_xdate()
        
        # Tight layout
        self.fig.tight_layout()
        
        # Redraw
        self.canvas.draw()
    
    def export_results(self):
        """Export results to CSV"""
        from tkinter import filedialog
        import csv
        from datetime import datetime
        
        if not self.app.backtest_results:
            from tkinter import messagebox
            messagebox.showwarning("No Data", "No backtest results to export")
            return
        
        # Ask for filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            trades = self.app.backtest_results['trades']
            
            with open(filename, 'w', newline='') as f:
                if trades:
                    writer = csv.DictWriter(f, fieldnames=trades[0].keys())
                    writer.writeheader()
                    writer.writerows(trades)
            
            from tkinter import messagebox
            messagebox.showinfo("Success", f"Results exported to {filename}")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to export: {e}")
