import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
from polygon import RESTClient

class TradeVisualizationTab:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg="#0a0e27")
        self.current_symbol = None
        self.current_trades = []
        self.price_data = None
        self.selected_trade_index = None
        self.trade_markers = []
        self.setup_ui()

    def setup_ui(self):
        # Futuristic Header with gradient effect
        header = tk.Frame(self.frame, bg="#0a0e27", height=80)
        header.pack(fill=tk.X)

        tk.Label(header, text="⚡ TRADE VISUALIZATION", fg="#00ff88",
                bg="#0a0e27", font=("Arial", 26, "bold")).pack(pady=5)
        tk.Label(header, text="Interactive Analysis • Real-time Insights • Advanced Trading View",
                fg="#6c7a89", bg="#0a0e27", font=("Arial", 10)).pack()

        # Main container with dark theme
        main = tk.Frame(self.frame, bg="#0a0e27")
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Control Panel - Futuristic Design
        control_panel = tk.Frame(main, bg="#1a1f3a", relief=tk.FLAT, bd=0)
        control_panel.pack(fill=tk.X, pady=(0, 10))

        control_inner = tk.Frame(control_panel, bg="#1a1f3a")
        control_inner.pack(padx=20, pady=15)

        tk.Label(control_inner, text="◉ SELECT SYMBOL", bg="#1a1f3a", fg="#00ff88",
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 15))

        # Symbol dropdown with custom style
        self.symbol_var = tk.StringVar()
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#2d3250", background="#2d3250",
                       foreground="white", arrowcolor="#00ff88")

        self.symbol_dropdown = ttk.Combobox(control_inner, textvariable=self.symbol_var,
                                           font=("Arial", 11), width=12, state="readonly",
                                           style="TCombobox")
        self.symbol_dropdown.pack(side=tk.LEFT, padx=5)
        self.symbol_dropdown.bind("<<ComboboxSelected>>", self.on_symbol_change)

        # Load button - futuristic style
        load_btn = tk.Button(control_inner, text="⚡ LOAD CHART", bg="#00ff88", fg="#0a0e27",
                 font=("Arial", 10, "bold"), padx=25, pady=8, relief=tk.FLAT,
                 cursor="hand2", activebackground="#00cc70",
                 command=self.load_chart)
        load_btn.pack(side=tk.LEFT, padx=15)

        # Status indicator
        self.info_label = tk.Label(control_inner, text="● READY", bg="#1a1f3a",
                                   fg="#6c7a89", font=("Arial", 10, "bold"))
        self.info_label.pack(side=tk.LEFT, padx=20)

        # Chart Container - Dark theme with neon accents
        chart_container = tk.Frame(main, bg="#1a1f3a", relief=tk.FLAT, bd=2)
        chart_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Chart title bar
        chart_header = tk.Frame(chart_container, bg="#0f1523", height=35)
        chart_header.pack(fill=tk.X)
        tk.Label(chart_header, text="📈 PRICE ACTION", bg="#0f1523", fg="#00ff88",
                font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=15, pady=5)

        # Create matplotlib figure with dark theme
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(14, 6), facecolor='#1a1f3a', edgecolor='#00ff88')
        self.ax = self.fig.add_subplot(111, facecolor='#0f1523')

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Bind click events for interactivity
        self.canvas.mpl_connect('button_press_event', self.on_chart_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_chart_hover)

        # Trade Table - Futuristic dark theme
        table_container = tk.Frame(main, bg="#1a1f3a", relief=tk.FLAT, bd=2)
        table_container.pack(fill=tk.BOTH, pady=(0, 10))

        # Table header
        table_header = tk.Frame(table_container, bg="#0f1523", height=35)
        table_header.pack(fill=tk.X)

        tk.Label(table_header, text="⚙ TRADE LOG", bg="#0f1523", fg="#00ff88",
                font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=15, pady=5)
        tk.Label(table_header, text="Click rows or chart markers for details  |  Interactive sync enabled",
                bg="#0f1523", fg="#6c7a89", font=("Arial", 9)).pack(side=tk.LEFT, padx=10)

        # Treeview with dark theme styling
        tree_frame = tk.Frame(table_container, bg="#1a1f3a")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure dark treeview style
        style.configure("Dark.Treeview",
                       background="#1a1f3a",
                       foreground="white",
                       fieldbackground="#1a1f3a",
                       rowheight=32,
                       font=("Arial", 10))
        style.configure("Dark.Treeview.Heading",
                       background="#0f1523",
                       foreground="#00ff88",
                       font=("Arial", 10, "bold"),
                       relief=tk.FLAT)
        style.map("Dark.Treeview",
                 background=[('selected', '#00ff88')],
                 foreground=[('selected', '#0a0e27')])

        columns = ("Entry Date", "Exit Date", "Days", "Entry $", "Exit $", "P&L", "P&L %", "Exit Reason")
        self.trade_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                       height=8, style="Dark.Treeview")

        # Configure columns with better spacing
        col_widths = {
            "Entry Date": 110,
            "Exit Date": 110,
            "Days": 60,
            "Entry $": 90,
            "Exit $": 90,
            "P&L": 90,
            "P&L %": 90,
            "Exit Reason": 140
        }

        for col in columns:
            self.trade_tree.heading(col, text=col)
            self.trade_tree.column(col, width=col_widths.get(col, 100), anchor='center')

        # Dark scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.trade_tree.yview)
        self.trade_tree.configure(yscrollcommand=scrollbar.set)

        self.trade_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection events for interactivity
        self.trade_tree.bind("<<TreeviewSelect>>", self.on_table_select)
        self.trade_tree.bind("<Double-1>", self.on_table_double_click)

        # Navigation footer
        nav_frame = tk.Frame(self.frame, bg="#0a0e27")
        nav_frame.pack(fill=tk.X, pady=15)

        back_btn = tk.Button(nav_frame, text="← BACK TO RESULTS", bg="#2d3250", fg="#00ff88",
                 font=("Arial", 12, "bold"), padx=30, pady=12, relief=tk.FLAT,
                 cursor="hand2", activebackground="#1a1f3a",
                 command=lambda: self.app.notebook.select(3))
        back_btn.pack()

    def generate_simulated_price_data(self, symbol, start_date, end_date):
        """Generate simulated price data for demo mode"""
        import random
        import numpy as np

        # Generate date range (business days only)
        dates = pd.date_range(start=start_date, end=end_date, freq='B')

        # Starting price based on symbol (rough approximations)
        if symbol in ['SPY', 'QQQ']:
            base_price = 400
        elif symbol in ['IWM', 'DIA']:
            base_price = 180
        else:
            base_price = random.uniform(50, 300)

        # Generate random walk price data
        num_days = len(dates)
        returns = np.random.normal(0.0005, 0.015, num_days)  # Small daily returns with volatility
        price_multipliers = np.exp(np.cumsum(returns))
        prices = base_price * price_multipliers

        # Generate OHLC data
        data = []
        for i, date in enumerate(dates):
            close = prices[i]
            open_price = close * (1 + random.uniform(-0.01, 0.01))
            high = max(open_price, close) * (1 + random.uniform(0, 0.02))
            low = min(open_price, close) * (1 - random.uniform(0, 0.02))
            volume = random.randint(50000000, 150000000)

            data.append({
                'Date': date,
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': close,
                'Volume': volume
            })

        df = pd.DataFrame(data)
        df.set_index('Date', inplace=True)
        return df

    def fetch_price_data_from_polygon(self, symbol, start_date, end_date):
        """Fetch daily price data from Polygon API"""
        try:
            client = RESTClient(self.app.api_key)

            # Format dates for Polygon API
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            # Fetch aggregates (daily bars)
            aggs = client.get_aggs(
                ticker=symbol,
                multiplier=1,
                timespan='day',
                from_=start_str,
                to=end_str,
                limit=50000
            )

            if not aggs or len(aggs) == 0:
                return None

            # Convert to pandas DataFrame
            data = []
            for agg in aggs:
                data.append({
                    'Date': datetime.fromtimestamp(agg.timestamp / 1000),
                    'Open': agg.open,
                    'High': agg.high,
                    'Low': agg.low,
                    'Close': agg.close,
                    'Volume': agg.volume
                })

            df = pd.DataFrame(data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)

            return df

        except Exception as e:
            print(f"Error fetching price data from Polygon: {e}")
            import traceback
            traceback.print_exc()
            return None

    def display_results(self, results):
        """Called when backtest results are ready"""
        if not results or 'by_symbol' not in results:
            return

        # Get list of symbols that have trades
        # Handle both old and new data structure formats
        symbols = []
        for sym, data in results['by_symbol'].items():
            if isinstance(data, dict) and 'trades' in data:
                if data['trades']:
                    symbols.append(sym)
            elif data:
                symbols.append(sym)

        symbols = sorted(symbols)

        if not symbols:
            self.info_label.config(text="● NO DATA", fg="#ff4444")
            return

        # Populate dropdown
        self.symbol_dropdown['values'] = symbols
        if symbols:
            self.symbol_dropdown.current(0)
            self.symbol_var.set(symbols[0])

        self.results = results
        self.info_label.config(text=f"● {len(symbols)} SYMBOLS LOADED", fg="#00ff88")

    def on_symbol_change(self, event=None):
        """Handle symbol selection change"""
        pass  # Chart loads when user clicks LOAD CHART button

    def load_chart(self):
        """Load and display chart for selected symbol"""
        symbol = self.symbol_var.get()
        if not symbol:
            return

        self.info_label.config(text="● LOADING...", fg="#ffaa00")
        self.frame.update()

        try:
            # Get trades for this symbol
            self.current_symbol = symbol

            # Handle both old and new data structure formats
            symbol_data = self.results['by_symbol'][symbol]
            if isinstance(symbol_data, dict) and 'trades' in symbol_data:
                self.current_trades = symbol_data['trades']
            else:
                self.current_trades = symbol_data

            if not self.current_trades:
                self.info_label.config(text="● NO TRADES", fg="#ff4444")
                return

            # Determine date range
            all_dates = []
            for trade in self.current_trades:
                all_dates.append(datetime.strptime(trade['Entry Date'], '%Y-%m-%d'))
                all_dates.append(datetime.strptime(trade['Exit Date'], '%Y-%m-%d'))

            start_date = min(all_dates) - timedelta(days=30)
            end_date = max(all_dates) + timedelta(days=30)

            # Fetch price data
            self.info_label.config(text="● DOWNLOADING...", fg="#ffaa00")
            self.frame.update()

            if not self.app.api_key:
                self.info_label.config(text="● API KEY MISSING", fg="#ff4444")
                return

            self.price_data = self.fetch_price_data_from_polygon(symbol, start_date, end_date)

            if self.price_data is None or self.price_data.empty:
                # Generate simulated price data for demo mode
                self.info_label.config(text="● GENERATING DEMO CHART...", fg="#ffaa00")
                self.frame.update()
                self.price_data = self.generate_simulated_price_data(symbol, start_date, end_date)

            # Plot the chart
            self.plot_chart()

            # Populate trade table
            self.populate_trade_table()

            self.info_label.config(text=f"● {len(self.current_trades)} TRADES", fg="#00ff88")

        except Exception as e:
            self.info_label.config(text=f"● ERROR: {str(e)[:20]}", fg="#ff4444")
            import traceback
            traceback.print_exc()

    def plot_chart(self):
        """Plot futuristic stock chart with interactive trade markers"""
        self.ax.clear()

        if self.price_data is None or self.price_data.empty:
            return

        # Plot price line with glow effect
        dates = self.price_data.index
        prices = self.price_data['Close']

        # Background glow
        self.ax.plot(dates, prices, color='#00ff88', linewidth=3, alpha=0.2, zorder=1)
        # Main line
        self.ax.plot(dates, prices, color='#00ff88', linewidth=2, label='Price', zorder=2)

        # Plot trade markers
        self.trade_markers = []

        for idx, trade in enumerate(self.current_trades):
            entry_date = datetime.strptime(trade['Entry Date'], '%Y-%m-%d')
            exit_date = datetime.strptime(trade['Exit Date'], '%Y-%m-%d')

            entry_price = self.get_price_on_date(entry_date)
            exit_price = self.get_price_on_date(exit_date)

            if entry_price is not None:
                # Entry marker - cyan diamond with glow
                self.ax.scatter(entry_date, entry_price,
                              color='#00ddff', marker='D', s=200, alpha=0.3,
                              zorder=3, edgecolors='none')
                self.ax.scatter(entry_date, entry_price,
                              color='#00ddff', marker='D', s=120,
                              zorder=4, edgecolors='#00ffff', linewidths=2,
                              label='Entry' if idx == 0 else "")
                self.trade_markers.append({
                    'type': 'entry',
                    'date': entry_date,
                    'price': entry_price,
                    'trade_idx': idx
                })

            if exit_price is not None:
                # Exit marker - color based on P&L
                is_win = trade.get('Win', trade.get('PnL', 0) > 0)
                exit_color = '#00ff88' if is_win else '#ff4466'
                edge_color = '#00ffaa' if is_win else '#ff6688'

                # Glow effect
                self.ax.scatter(exit_date, exit_price,
                              color=exit_color, marker='s', s=200, alpha=0.3,
                              zorder=3, edgecolors='none')
                # Main marker
                self.ax.scatter(exit_date, exit_price,
                              color=exit_color, marker='s', s=120,
                              zorder=4, edgecolors=edge_color, linewidths=2,
                              label='Win Exit' if is_win and idx == 0 else
                                    'Loss Exit' if not is_win and idx == 0 else "")
                self.trade_markers.append({
                    'type': 'exit',
                    'date': exit_date,
                    'price': exit_price,
                    'trade_idx': idx
                })

        # Futuristic styling
        self.ax.set_title(f"{self.current_symbol} • TRADE ANALYSIS",
                         fontsize=14, fontweight='bold', color='#00ff88', pad=15)
        self.ax.set_xlabel("Timeline", fontsize=10, color='#6c7a89')
        self.ax.set_ylabel("Price (USD)", fontsize=10, color='#6c7a89')

        # Grid with neon effect
        self.ax.grid(True, alpha=0.15, color='#00ff88', linestyle='--', linewidth=0.5)

        # Customize spines
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#00ff88')
            spine.set_linewidth(1)
            spine.set_alpha(0.3)

        # Legend
        legend = self.ax.legend(loc='upper left', fontsize=9, framealpha=0.8,
                               facecolor='#0f1523', edgecolor='#00ff88')
        for text in legend.get_texts():
            text.set_color('#00ff88')

        # Format x-axis
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        self.ax.tick_params(axis='x', colors='#6c7a89', labelsize=9)
        self.ax.tick_params(axis='y', colors='#6c7a89', labelsize=9)
        self.fig.autofmt_xdate()

        # Tight layout
        self.fig.tight_layout()
        self.canvas.draw()

    def get_price_on_date(self, target_date):
        """Get closing price on or nearest to target date"""
        if self.price_data is None or self.price_data.empty:
            return None

        try:
            if target_date in self.price_data.index:
                return self.price_data.loc[target_date]['Close']

            idx = self.price_data.index.searchsorted(target_date)
            if idx == 0:
                return self.price_data.iloc[0]['Close']
            elif idx == len(self.price_data):
                return self.price_data.iloc[-1]['Close']
            else:
                before = self.price_data.index[idx - 1]
                after = self.price_data.index[idx]
                if abs((target_date - before).days) < abs((after - target_date).days):
                    return self.price_data.iloc[idx - 1]['Close']
                else:
                    return self.price_data.iloc[idx]['Close']
        except:
            return None

    def on_chart_click(self, event):
        """Handle click on chart markers - highlight corresponding trade"""
        if event.inaxes != self.ax or not self.trade_markers:
            return

        # Find clicked marker
        click_date = mdates.num2date(event.xdata)
        # Make timezone-naive for comparison
        if hasattr(click_date, 'tzinfo') and click_date.tzinfo is not None:
            click_date = click_date.replace(tzinfo=None)
        click_price = event.ydata

        # Search for nearby marker
        min_dist = float('inf')
        clicked_trade_idx = None

        for marker in self.trade_markers:
            # Calculate distance
            date_diff = abs((marker['date'] - click_date).days)
            price_diff = abs(marker['price'] - click_price) / click_price

            dist = date_diff + price_diff * 100  # Weighted distance

            if dist < min_dist and dist < 10:  # Threshold
                min_dist = dist
                clicked_trade_idx = marker['trade_idx']

        if clicked_trade_idx is not None:
            # Select the corresponding row in the table
            self.select_trade_in_table(clicked_trade_idx)

    def on_chart_hover(self, event):
        """Show tooltip on hover (optional enhancement)"""
        # Could add tooltip functionality here
        pass

    def on_table_select(self, event):
        """Handle table row selection - highlight on chart"""
        selection = self.trade_tree.selection()
        if not selection:
            return

        # Get selected row index
        item = selection[0]
        idx = self.trade_tree.index(item)

        if idx < len(self.current_trades):
            self.selected_trade_index = idx
            self.highlight_trade_on_chart(idx)

    def on_table_double_click(self, event):
        """Handle double click - could show detailed trade info"""
        selection = self.trade_tree.selection()
        if not selection:
            return

        item = selection[0]
        idx = self.trade_tree.index(item)

        if idx < len(self.current_trades):
            trade = self.current_trades[idx]
            # Could open a detailed view popup here
            print(f"Trade details: {trade}")

    def select_trade_in_table(self, idx):
        """Select a specific trade row in the table"""
        if idx < 0 or idx >= len(self.trade_tree.get_children()):
            return

        # Clear current selection
        for item in self.trade_tree.selection():
            self.trade_tree.selection_remove(item)

        # Select the item
        item_id = self.trade_tree.get_children()[idx]
        self.trade_tree.selection_set(item_id)
        self.trade_tree.see(item_id)  # Scroll to visible

        self.selected_trade_index = idx

    def highlight_trade_on_chart(self, idx):
        """Highlight selected trade on the chart"""
        if idx is None or idx >= len(self.current_trades):
            return

        # Redraw chart with highlighted trade
        self.plot_chart()

        # Add highlight overlay for selected trade
        trade = self.current_trades[idx]
        entry_date = datetime.strptime(trade['Entry Date'], '%Y-%m-%d')
        exit_date = datetime.strptime(trade['Exit Date'], '%Y-%m-%d')

        entry_price = self.get_price_on_date(entry_date)
        exit_price = self.get_price_on_date(exit_date)

        if entry_price and exit_price:
            # Highlight with larger markers
            self.ax.scatter(entry_date, entry_price,
                          color='#ffff00', marker='D', s=300, alpha=0.5,
                          zorder=10, edgecolors='#ffff00', linewidths=3)
            self.ax.scatter(exit_date, exit_price,
                          color='#ffff00', marker='s', s=300, alpha=0.5,
                          zorder=10, edgecolors='#ffff00', linewidths=3)

            # Draw connecting line
            self.ax.plot([entry_date, exit_date], [entry_price, exit_price],
                        color='#ffff00', linewidth=2, alpha=0.6, linestyle='--', zorder=9)

        self.canvas.draw()

    def populate_trade_table(self):
        """Populate the trade table with current trades"""
        # Clear existing rows
        for item in self.trade_tree.get_children():
            self.trade_tree.delete(item)

        # Add trades
        for trade in self.current_trades:
            pnl = trade.get('PnL', 0)
            pnl_pct = trade.get('PnL %', 0)

            # Format values
            entry_cost = f"${trade.get('Entry Cost', 0):.2f}"
            exit_cost = f"${trade.get('Exit Value', 0):.2f}"
            pnl_str = f"${pnl:.2f}"
            pnl_pct_str = f"{pnl_pct:.1f}%"

            values = (
                trade['Entry Date'],
                trade['Exit Date'],
                trade.get('Days Held', ''),
                entry_cost,
                exit_cost,
                pnl_str,
                pnl_pct_str,
                trade.get('Exit Reason', 'Closed')
            )

            # Add row with tag for coloring
            tag = 'win' if pnl > 0 else 'loss'
            self.trade_tree.insert('', 'end', values=values, tags=(tag,))

        # Apply row colors
        self.trade_tree.tag_configure('win', foreground='#00ff88')
        self.trade_tree.tag_configure('loss', foreground='#ff4466')
