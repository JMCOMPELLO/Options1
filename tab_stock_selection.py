import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import requests
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class StockSelectionTab:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg="#ffffff")
        self.setup_ui()
        self.load_sp500_universe()
    
    def setup_ui(self):
        # ULTRA SIMPLE - NO SCROLLING CANVAS AT ALL
        
        # Header
        header = tk.Frame(self.frame, bg="#2C3E50", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="OPTIONS BACKTEST PRO", fg="white",
                bg="#2C3E50", font=("Arial", 24, "bold")).pack(pady=10)
        
        # Main area
        main = tk.Frame(self.frame, bg="#ffffff")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Bulk selection - Modern card-style design
        bulk = tk.Frame(main, bg="white", relief=tk.FLAT, bd=0)
        bulk.pack(fill=tk.X, pady=(0, 15))

        # Header with control buttons
        header_frame = tk.Frame(bulk, bg="white")
        header_frame.pack(fill=tk.X, padx=0, pady=(0, 10))

        tk.Label(header_frame, text="Select Sectors", bg="white", fg="#2C3E50",
                font=("Arial", 14, "bold")).pack(side=tk.LEFT)

        button_container = tk.Frame(header_frame, bg="white")
        button_container.pack(side=tk.RIGHT)

        # Modern flat buttons
        select_all_btn = tk.Button(button_container, text="Select All", bg="white", fg="#27AE60",
                                   command=self.select_all, font=("Arial", 10),
                                   relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
                                   borderwidth=1, highlightthickness=1)
        select_all_btn.pack(side=tk.LEFT, padx=5)

        clear_all_btn = tk.Button(button_container, text="Clear All", bg="white", fg="#E74C3C",
                                  command=self.clear_all, font=("Arial", 10),
                                  relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
                                  borderwidth=1, highlightthickness=1)
        clear_all_btn.pack(side=tk.LEFT)

        # Sector chips/tags in a clean grid
        sector_frame = tk.Frame(bulk, bg="white")
        sector_frame.pack(padx=0, pady=(0, 10), fill=tk.X)

        self.sector_buttons = {}
        sectors = [
            ("Communication Services", "#E91E63"),
            ("Information Technology", "#3498DB"),
            ("Financials", "#F39C12"),
            ("Industrials", "#7F8C8D"),
            ("Health Care", "#9B59B6"),
            ("Consumer Discretionary", "#E67E22"),
            ("Consumer Staples", "#27AE60"),
            ("Energy", "#16A085"),
            ("Real Estate", "#1ABC9C"),
            ("Materials", "#D35400"),
            ("Utilities", "#F1C40F")
        ]

        # Create modern chip-style buttons in flowing layout
        row = 0
        col = 0
        for sector_name, color in sectors:
            # Create a frame for each sector chip
            chip_frame = tk.Frame(sector_frame, bg="white")
            chip_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')

            # Sector button with modern design - darker gray background
            btn = tk.Button(chip_frame, text=sector_name, bg="#D5DBDB", fg="black",
                          font=("Arial", 10, "bold"), relief=tk.FLAT, padx=15, pady=8,
                          cursor="hand2", anchor='w',
                          command=lambda s=sector_name: self.select_sector_toggle(s))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Store button and color reference
            self.sector_buttons[sector_name] = {'button': btn, 'color': color, 'selected': False}

            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1

        # Make columns expand equally
        for i in range(3):
            sector_frame.columnconfigure(i, weight=1)
        
        # Search
        sf = tk.Frame(main, bg="#ffffff")
        sf.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(sf, text="SEARCH:", fg="black", bg="#ffffff",
                font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_tree)
        tk.Entry(sf, textvariable=self.search_var, font=("Arial", 12),
                bg="white", fg="black", width=30).pack(side=tk.LEFT)

        # Selected count
        self.count_label = tk.Label(sf, text="Selected: 0", bg="#ffffff",
                                    fg="black", font=("Arial", 12, "bold"))
        self.count_label.pack(side=tk.RIGHT, padx=10)

        # Selected portfolio display box (ADDED BACK)
        selected_panel = tk.LabelFrame(main, text=" SELECTED PORTFOLIO ",
                                       bg="#EBF5FB", fg="black", font=("Arial", 11, "bold"), bd=2)
        selected_panel.pack(fill=tk.X, pady=(0, 10))

        self.selected_text = tk.Text(selected_panel, height=3, wrap=tk.WORD,
                                     font=("Arial", 10), bg="white", fg="black",
                                     relief=tk.FLAT)
        self.selected_text.pack(fill=tk.X, padx=10, pady=8)

        # Toggle header with buttons to switch between Stock List and Sector Breakdown
        toggle_header = tk.Frame(main, bg="#D5DBDB", bd=2, relief=tk.RAISED)
        toggle_header.pack(fill=tk.X, pady=(0, 2))

        # Create toggle buttons
        self.view_mode = tk.StringVar(value="list")  # "list" or "chart"

        # Left side - view toggle buttons
        left_btns = tk.Frame(toggle_header, bg="#D5DBDB")
        left_btns.pack(side=tk.LEFT, padx=5, pady=5)

        list_btn = tk.Button(left_btns, text="STOCK LIST", bg="#3498DB", fg="black",
                            font=("Arial", 11, "bold"), relief=tk.FLAT, padx=20, pady=10,
                            cursor="hand2", command=lambda: self.switch_view("list"))
        list_btn.pack(side=tk.LEFT, padx=2)
        self.list_btn = list_btn

        chart_btn = tk.Button(left_btns, text="SECTOR BREAKDOWN", bg="#D5DBDB", fg="black",
                             font=("Arial", 11, "bold"), relief=tk.FLAT, padx=20, pady=10,
                             cursor="hand2", command=lambda: self.switch_view("chart"))
        chart_btn.pack(side=tk.LEFT, padx=2)
        self.chart_btn = chart_btn

        # Right side - Next button
        next_btn = tk.Button(toggle_header, text="NEXT: CONFIGURE STRATEGY →",
                            bg="#27AE60", fg="black", font=("Arial", 12, "bold"),
                            relief=tk.FLAT, padx=30, pady=10, cursor="hand2",
                            command=self.next_tab)
        next_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        self.next_btn = next_btn

        # Container for both views (only one visible at a time)
        view_container = tk.Frame(main, bg="#FDFEFE", bd=2, relief=tk.SUNKEN)
        view_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Stock tree view
        tree_frame = tk.Frame(view_container, bg="#FDFEFE")
        self.tree_frame = tree_frame

        style = ttk.Style()
        style.configure("Treeview", background="white", foreground="black",
                       rowheight=28, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"),
                       foreground="black")
        style.map('Treeview', background=[('selected', '#3498DB')],
                 foreground=[('selected', 'white')])

        self.tree = ttk.Treeview(tree_frame, columns=("Name", "Sector"),
                                show="tree headings", height=12)
        self.tree.heading("#0", text="Ticker")
        self.tree.heading("Name", text="Company")
        self.tree.heading("Sector", text="Sector")
        self.tree.column("#0", width=80)
        self.tree.column("Name", width=300)
        self.tree.column("Sector", width=200)

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Button-1>", self.on_click)

        # Chart view
        self.chart_panel = tk.Frame(view_container, bg="#FDFEFE")

        # Create matplotlib figure for pie chart - larger size to fill the space
        self.fig = Figure(figsize=(10, 7), facecolor='#FDFEFE')
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Initialize with empty chart
        self.update_pie_chart()

        # Show stock list by default
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
    
    def load_sp500_universe(self):
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            table = pd.read_html(io.StringIO(response.text), flavor='html5lib')[0]
            
            self.app.full_universe = []
            for _, row in table.iterrows():
                self.app.full_universe.append({
                    'ticker': row['Symbol'].replace('.', '-'), 
                    'name': row['Security'], 
                    'sector': row['GICS Sector']
                })
            
            self.refresh_tree(self.app.full_universe)
            print(f"✓ Loaded {len(self.app.full_universe)} stocks")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data: {e}")
    
    def select_sector_toggle(self, sector):
        """Toggle sector selection with visual feedback"""
        btn_info = self.sector_buttons[sector]
        btn = btn_info['button']
        color = btn_info['color']

        if btn_info['selected']:
            # Deselect - remove tickers
            tickers = {d['ticker'] for d in self.app.full_universe if d['sector'] == sector}
            self.app.selected_tickers -= tickers
            btn.config(bg="#D5DBDB", fg="black")
            btn_info['selected'] = False
        else:
            # Select - add tickers
            tickers = {d['ticker'] for d in self.app.full_universe if d['sector'] == sector}
            self.app.selected_tickers.update(tickers)
            btn.config(bg=color, fg="black")
            btn_info['selected'] = True

        self.refresh_tree(self.app.full_universe)
        self.update_count()

    def select_sector(self, sector):
        """Legacy method for compatibility"""
        self.select_sector_toggle(sector)

    def select_all(self):
        self.app.selected_tickers = {d['ticker'] for d in self.app.full_universe}
        # Update all sector buttons to selected state
        for sector_name, btn_info in self.sector_buttons.items():
            btn_info['button'].config(bg=btn_info['color'], fg="black")
            btn_info['selected'] = True
        self.refresh_tree(self.app.full_universe)
        self.update_count()

    def clear_all(self):
        self.app.selected_tickers.clear()
        # Update all sector buttons to unselected state
        for sector_name, btn_info in self.sector_buttons.items():
            btn_info['button'].config(bg="#D5DBDB", fg="black")
            btn_info['selected'] = False
        self.refresh_tree(self.app.full_universe)
        self.update_count()
    
    def refresh_tree(self, data):
        self.tree.delete(*self.tree.get_children())
        for d in data:
            icon = "[X]" if d['ticker'] in self.app.selected_tickers else "[ ]"
            self.tree.insert("", "end", iid=d['ticker'],
                           text=f"{icon} {d['ticker']}",
                           values=(d['name'], d['sector']))
    
    def on_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            if iid in self.app.selected_tickers: 
                self.app.selected_tickers.discard(iid)
            else: 
                self.app.selected_tickers.add(iid)
            self.refresh_tree(self.app.full_universe)
            self.update_count()
    
    def filter_tree(self, *args):
        q = self.search_var.get().upper()
        if not q:
            filtered = self.app.full_universe
        else:
            filtered = [d for d in self.app.full_universe 
                       if q in d['ticker'] or q in d['sector'].upper() or q in d['name'].upper()]
        self.refresh_tree(filtered)
    
    def update_count(self):
        count = len(self.app.selected_tickers)
        self.count_label.config(text=f"Selected: {count}")

        # Update the selected portfolio text box
        self.selected_text.delete(1.0, tk.END)
        sorted_tickers = sorted(self.app.selected_tickers)

        if count == 0:
            self.selected_text.insert(1.0, "No stocks selected. Click stocks or use buttons above.")
        else:
            # Show up to 100 tickers, then indicate more
            display_tickers = sorted_tickers[:100]
            ticker_text = ", ".join(display_tickers)

            if count > 100:
                self.selected_text.insert(1.0, f"TOTAL: {count} stocks\n{ticker_text}... and {count-100} more")
            else:
                self.selected_text.insert(1.0, f"TOTAL: {count} stocks\n{ticker_text}")

        # Update pie chart
        self.update_pie_chart()

    def switch_view(self, mode):
        """Switch between stock list and sector breakdown views"""
        self.view_mode.set(mode)

        if mode == "list":
            # Show stock list, hide chart
            self.chart_panel.pack_forget()
            self.tree_frame.pack(fill=tk.BOTH, expand=True)
            # Update button styles
            self.list_btn.config(bg="#3498DB", fg="black")
            self.chart_btn.config(bg="#D5DBDB", fg="black")
        else:  # mode == "chart"
            # Show chart, hide stock list
            self.tree_frame.pack_forget()
            self.chart_panel.pack(fill=tk.BOTH, expand=True)
            # Update button styles
            self.list_btn.config(bg="#D5DBDB", fg="black")
            self.chart_btn.config(bg="#3498DB", fg="black")

    def update_pie_chart(self):
        """Update the pie chart showing sector breakdown of selected stocks"""
        self.ax.clear()

        if not self.app.selected_tickers:
            # Show empty message
            self.ax.text(0.5, 0.5, 'No stocks selected',
                        ha='center', va='center', fontsize=14, color='#95A5A6')
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.axis('off')
            self.canvas.draw()
            return

        # Count stocks by sector
        sector_counts = {}
        for ticker in self.app.selected_tickers:
            # Find the sector for this ticker
            stock_info = next((d for d in self.app.full_universe if d['ticker'] == ticker), None)
            if stock_info:
                sector = stock_info['sector']
                sector_counts[sector] = sector_counts.get(sector, 0) + 1

        if not sector_counts:
            self.ax.text(0.5, 0.5, 'No sector data available',
                        ha='center', va='center', fontsize=14, color='#95A5A6')
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.axis('off')
            self.canvas.draw()
            return

        # Prepare data for pie chart
        sectors = list(sector_counts.keys())
        counts = list(sector_counts.values())

        # Define sector colors (matching button colors - updated palette)
        sector_colors = {
            "Communication Services": "#E91E63",
            "Information Technology": "#3498DB",
            "Financials": "#F39C12",
            "Industrials": "#95A5A6",
            "Health Care": "#9B59B6",
            "Consumer Discretionary": "#E67E22",
            "Consumer Staples": "#27AE60",
            "Energy": "#16A085",
            "Real Estate": "#1ABC9C",
            "Materials": "#D35400",
            "Utilities": "#F1C40F"
        }

        colors = [sector_colors.get(sector, "#888888") for sector in sectors]

        # Create pie chart with improved label handling
        # If many sectors, show percentage only inside slices and create a legend
        if len(sectors) > 6:
            # For many sectors, use legend instead of labels on slices
            wedges, texts, autotexts = self.ax.pie(counts, colors=colors,
                                                   autopct=lambda pct: f'{pct:.1f}%' if pct > 3 else '',
                                                   startangle=90,
                                                   textprops={'fontsize': 9, 'color': 'white', 'weight': 'bold'})

            # Create legend with sector names and counts
            legend_labels = [f'{sector}: {count} stocks ({count/sum(counts)*100:.1f}%)'
                           for sector, count in zip(sectors, counts)]
            self.ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                          fontsize=9, frameon=True, fancybox=True)

            # Make percentage text white and bold for visibility
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
        else:
            # For few sectors, show labels on the pie
            wedges, texts, autotexts = self.ax.pie(counts, labels=sectors, colors=colors,
                                                   autopct='%1.1f%%', startangle=90,
                                                   textprops={'fontsize': 10, 'color': 'black', 'weight': 'bold'})

            # Make percentage text white and bold
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)

            # Make sector labels readable
            for text in texts:
                text.set_color('black')
                text.set_fontsize(10)
                text.set_fontweight('bold')

        # Remove title to save space and make chart bigger

        self.canvas.draw()
    
    def next_tab(self):
        if not self.app.selected_tickers:
            messagebox.showwarning("No Selection", "Please select at least one stock.")
            return
        self.app.enable_strategy_tab()
        self.app.notebook.select(1)
