import tkinter as tk
from tkinter import ttk, scrolledtext
import pandas as pd

class BacktestResultsTab:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg="#f5f5f5")
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.frame, bg="#1a1a1a", height=70)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="DETAILED TRADE RESULTS", fg="#32CD32",
                bg="#1a1a1a", font=("Arial", 24, "bold")).pack(pady=15)
        
        # Main content
        content = tk.Frame(self.frame, bg="#f5f5f5")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Filter panel
        filter_panel = tk.LabelFrame(content, text=" 🔍 FILTERS ",
                                    bg="white", fg="black",
                                    font=("Arial", 12, "bold"), bd=2)
        filter_panel.pack(fill=tk.X, pady=(0, 10))
        
        filter_inner = tk.Frame(filter_panel, bg="white")
        filter_inner.pack(fill=tk.X, padx=15, pady=10)
        
        # Filter controls
        tk.Label(filter_inner, text="Show:", bg="white",
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.filter_var = tk.StringVar(value="All")
        for option in ["All", "Winners", "Losers"]:
            tk.Radiobutton(filter_inner, text=option, variable=self.filter_var,
                          value=option, command=self.apply_filter,
                          bg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(filter_inner, text="Symbol:", bg="white",
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 5))
        
        self.symbol_filter = ttk.Combobox(filter_inner, width=12, state='readonly')
        self.symbol_filter.pack(side=tk.LEFT, padx=5)
        self.symbol_filter.bind('<<ComboboxSelected>>', lambda e: self.apply_filter())
        
        tk.Button(filter_inner, text="Clear Filters", bg="#757575", fg="white",
                 command=self.clear_filters, font=("Arial", 9, "bold"),
                 padx=15, pady=5).pack(side=tk.LEFT, padx=20)
        
        # Results tree
        tree_frame = tk.Frame(content, bg="white", relief=tk.SUNKEN, bd=2)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Setup tree style
        style = ttk.Style()
        style.configure("Results.Treeview", 
                       background="white", 
                       foreground="black",
                       rowheight=30, 
                       font=("Arial", 10))
        style.configure("Results.Treeview.Heading", 
                       font=("Arial", 10, "bold"),
                       background="#e0e0e0",
                       foreground="black")
        style.map('Results.Treeview', 
                 background=[('selected', '#2196F3')])
        
        # Create treeview
        columns = ("Symbol", "Strategy", "Entry", "Exit", "Days", "Entry Cost", 
                  "P&L", "P&L %", "Exit Reason", "Result")
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                style="Results.Treeview", selectmode="browse")
        
        # Configure columns
        self.tree.heading("Symbol", text="Symbol")
        self.tree.heading("Strategy", text="Strategy")
        self.tree.heading("Entry", text="Entry Date")
        self.tree.heading("Exit", text="Exit Date")
        self.tree.heading("Days", text="Days")
        self.tree.heading("Entry Cost", text="Entry Cost")
        self.tree.heading("P&L", text="P&L")
        self.tree.heading("P&L %", text="P&L %")
        self.tree.heading("Exit Reason", text="Exit Reason")
        self.tree.heading("Result", text="Result")
        
        self.tree.column("Symbol", width=80, anchor='center')
        self.tree.column("Strategy", width=150)
        self.tree.column("Entry", width=100, anchor='center')
        self.tree.column("Exit", width=100, anchor='center')
        self.tree.column("Days", width=60, anchor='center')
        self.tree.column("Entry Cost", width=100, anchor='e')
        self.tree.column("P&L", width=100, anchor='e')
        self.tree.column("P&L %", width=80, anchor='e')
        self.tree.column("Exit Reason", width=120)
        self.tree.column("Result", width=80, anchor='center')
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click for details
        self.tree.bind('<Double-1>', self.show_trade_details)
        
        # Summary panel
        summary_panel = tk.LabelFrame(content, text=" 📋 TRADE BREAKDOWN ",
                                     bg="white", fg="black",
                                     font=("Arial", 12, "bold"), bd=2)
        summary_panel.pack(fill=tk.X, pady=(10, 0))
        
        self.summary_text = tk.Text(summary_panel, height=6, wrap=tk.WORD,
                                   bg="white", fg="black", font=("Arial", 10))
        self.summary_text.pack(fill=tk.X, padx=15, pady=10)
        
        # Navigation
        nav_frame = tk.Frame(self.frame, bg="#f5f5f5")
        nav_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Button(nav_frame, text="⬅ BACK TO EQUITY CURVE", bg="#757575", fg="white",
                 font=("Arial", 13, "bold"), command=lambda: self.app.notebook.select(2),
                 padx=25, pady=12, cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(nav_frame, text="📊 EXPORT TO CSV", bg="#4CAF50", fg="white",
                 font=("Arial", 13, "bold"), command=self.export_csv,
                 padx=25, pady=12, cursor="hand2").pack(side=tk.RIGHT, padx=10)
    
    def display_results(self, results: dict):
        """Display backtest results in tree"""
        self.results = results
        self.all_trades = results['trades']
        
        # Populate symbol filter
        symbols = sorted(set(t['Symbol'] for t in self.all_trades))
        self.symbol_filter['values'] = ['All'] + symbols
        self.symbol_filter.current(0)
        
        # Display all trades initially
        self.refresh_tree(self.all_trades)
        self.update_summary(self.all_trades)
    
    def refresh_tree(self, trades: list):
        """Refresh tree with trades"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add trades
        for trade in trades:
            is_win = trade.get('Win', False)
            result = "✓ WIN" if is_win else "✗ LOSS"
            
            # Format values
            pnl = trade.get('PnL', 0)
            pnl_pct = trade.get('PnL %', 0)
            
            values = (
                trade.get('Symbol', ''),
                trade.get('Strategy', ''),
                trade.get('Entry Date', ''),
                trade.get('Exit Date', ''),
                trade.get('Days Held', ''),
                f"${trade.get('Entry Cost', 0):.2f}",
                f"${pnl:.2f}",
                f"{pnl_pct:.1f}%",
                trade.get('Exit Reason', ''),
                result
            )
            
            # Insert with tag for coloring
            tag = 'win' if is_win else 'loss'
            self.tree.insert('', 'end', values=values, tags=(tag,))
        
        # Configure tags for coloring
        self.tree.tag_configure('win', background='#E8F5E9')
        self.tree.tag_configure('loss', background='#FFEBEE')
    
    def apply_filter(self):
        """Apply filters to trades"""
        filtered = self.all_trades
        
        # Filter by win/loss
        filter_type = self.filter_var.get()
        if filter_type == "Winners":
            filtered = [t for t in filtered if t.get('Win', False)]
        elif filter_type == "Losers":
            filtered = [t for t in filtered if not t.get('Win', False)]
        
        # Filter by symbol
        symbol = self.symbol_filter.get()
        if symbol and symbol != "All":
            filtered = [t for t in filtered if t.get('Symbol') == symbol]
        
        self.refresh_tree(filtered)
        self.update_summary(filtered)
    
    def clear_filters(self):
        """Clear all filters"""
        self.filter_var.set("All")
        self.symbol_filter.current(0)
        self.apply_filter()
    
    def update_summary(self, trades: list):
        """Update summary text"""
        self.summary_text.delete(1.0, tk.END)
        
        if not trades:
            self.summary_text.insert(1.0, "No trades match the current filters.")
            return
        
        df = pd.DataFrame(trades)
        
        total = len(df)
        winners = len(df[df['Win']]) if 'Win' in df.columns else 0
        losers = total - winners
        win_rate = (winners / total * 100) if total > 0 else 0
        
        total_pnl = df['PnL'].sum() if 'PnL' in df.columns else 0
        avg_pnl = df['PnL'].mean() if 'PnL' in df.columns else 0
        
        avg_days = df['Days Held'].mean() if 'Days Held' in df.columns else 0
        
        # By strategy breakdown
        if 'Strategy' in df.columns:
            strategy_counts = df['Strategy'].value_counts().to_dict()
            strategy_text = ", ".join([f"{k}: {v}" for k, v in strategy_counts.items()])
        else:
            strategy_text = "N/A"
        
        summary = f"""FILTERED RESULTS SUMMARY:
Total Trades: {total} | Winners: {winners} ({win_rate:.1f}%) | Losers: {losers}
Total P&L: ${total_pnl:,.2f} | Average P&L: ${avg_pnl:,.2f}
Average Days Held: {avg_days:.1f} days
Strategies: {strategy_text}

Double-click any trade for detailed information."""
        
        self.summary_text.insert(1.0, summary)
    
    def show_trade_details(self, event):
        """Show detailed information for selected trade"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Find the full trade data
        symbol = values[0]
        entry_date = values[2]
        
        trade = None
        for t in self.all_trades:
            if t.get('Symbol') == symbol and t.get('Entry Date') == entry_date:
                trade = t
                break
        
        if not trade:
            return
        
        # Create detail window
        detail_window = tk.Toplevel(self.frame)
        detail_window.title(f"Trade Details - {symbol}")
        detail_window.geometry("600x500")
        detail_window.configure(bg="white")
        
        # Header
        header = tk.Frame(detail_window, bg="#1a1a1a", height=60)
        header.pack(fill=tk.X)
        
        is_win = trade.get('Win', False)
        result_text = "✓ WINNING TRADE" if is_win else "✗ LOSING TRADE"
        result_color = "#4CAF50" if is_win else "#F44336"
        
        tk.Label(header, text=f"{symbol} - {result_text}", 
                fg=result_color, bg="#1a1a1a",
                font=("Arial", 18, "bold")).pack(pady=15)
        
        # Details
        details_frame = tk.Frame(detail_window, bg="white")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD,
                                                font=("Courier", 10),
                                                bg="#f5f5f5", fg="black")
        details_text.pack(fill=tk.BOTH, expand=True)
        
        # Format trade details
        details = f"""
═══════════════════════════════════════════════════════
TRADE DETAILS
═══════════════════════════════════════════════════════

Strategy:           {trade.get('Strategy', 'N/A')}
Symbol:             {trade.get('Symbol', 'N/A')}

TIMING
Entry Date:         {trade.get('Entry Date', 'N/A')}
Exit Date:          {trade.get('Exit Date', 'N/A')}
Days Held:          {trade.get('Days Held', 'N/A')} days

FINANCIALS
Entry Cost:         ${trade.get('Entry Cost', 0):,.2f}
Max Profit:         ${trade.get('Max Profit', 0):,.2f}
Max Loss:           ${trade.get('Max Loss', 0):,.2f}
Realized P&L:       ${trade.get('PnL', 0):,.2f}
P&L Percentage:     {trade.get('PnL %', 0):.2f}%

UNDERLYING
Entry Price:        ${trade.get('Underlying Entry', 0):.2f}
Exit Price:         ${trade.get('Underlying Exit', 0):.2f}

EXIT
Exit Reason:        {trade.get('Exit Reason', 'N/A')}
Result:             {'WIN' if is_win else 'LOSS'}

═══════════════════════════════════════════════════════
"""
        
        details_text.insert(1.0, details)
        details_text.config(state=tk.DISABLED)
        
        # Close button
        tk.Button(detail_window, text="Close", bg="#757575", fg="white",
                 font=("Arial", 12, "bold"), command=detail_window.destroy,
                 padx=30, pady=10).pack(pady=15)
    
    def export_csv(self):
        """Export results to CSV"""
        from tkinter import filedialog
        import csv
        from datetime import datetime
        
        if not self.all_trades:
            from tkinter import messagebox
            messagebox.showwarning("No Data", "No trades to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"detailed_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.all_trades[0].keys())
                writer.writeheader()
                writer.writerows(self.all_trades)
            
            from tkinter import messagebox
            messagebox.showinfo("Success", f"Exported {len(self.all_trades)} trades to {filename}")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Export failed: {e}")
