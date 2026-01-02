import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import requests
import io

class StockSelectionTab:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg="#ffffff")
        self.bg_main = "#ffffff"
        self.bg_dark = "#1a1a1a"
        self.accent = "#32CD32"
        self.icon_checked = "✓"
        self.icon_unchecked = "○"
        self.sector_vars = {}
        self.setup_ui()
        self.load_sp500_universe()
    
    def setup_ui(self):
        # REMOVE SCROLLABLE CANVAS - Use direct frame instead for better Mac compatibility
        main_frame = tk.Frame(self.frame, bg=self.bg_main)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(main_frame, bg=self.bg_dark, height=80)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="OPTIONS BACKTEST PRO", fg="#32CD32", 
                bg=self.bg_dark, font=("Arial", 28, "bold")).pack(pady=5)
        tk.Label(header, text="Advanced Multi-Strategy Options Backtesting Platform", 
                fg="white", bg=self.bg_dark, font=("Arial", 12)).pack()
        
        # Content frame with native scrolling
        content_frame = tk.Frame(main_frame, bg=self.bg_main)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Info panel
        info_panel = tk.LabelFrame(content_frame, text=" 📌 STEP 1: SELECT UNDERLYING ASSETS ", 
                                   bg="#e8f5e9", fg="#000000", font=("Arial", 13, "bold"), bd=3)
        info_panel.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(info_panel, text="Select stocks to backtest options strategies on. "
                "You can select individual stocks or entire sectors.",
                bg="#e8f5e9", fg="#000000", font=("Arial", 11), wraplength=1200,
                justify=tk.LEFT).pack(padx=15, pady=10)
        
        # Bulk selection panel
        bulk_panel = tk.LabelFrame(content_frame, text=" BULK SELECTION ", 
                                   bg="#f5f5f5", fg="#000000", font=("Arial", 12, "bold"), bd=2)
        bulk_panel.pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = tk.Frame(bulk_panel, bg="#f5f5f5")
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Button(btn_frame, text="✓ SELECT ALL S&P 500", bg=self.accent, fg="#000000",
                 command=self.select_all_sp500, font=("Arial", 11, "bold"),
                 padx=20, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✗ CLEAR ALL", bg="#f44336", fg="white",
                 command=self.clear_all_selections, font=("Arial", 11, "bold"),
                 padx=20, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="★ TECH SECTOR", bg="#2196F3", fg="white",
                 command=lambda: self.select_sector("Information Technology"),
                 font=("Arial", 11, "bold"), padx=20, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="💰 FINANCIAL", bg="#FF9800", fg="#000000",
                 command=lambda: self.select_sector("Financials"),
                 font=("Arial", 11, "bold"), padx=20, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🏥 HEALTHCARE", bg="#9C27B0", fg="white",
                 command=lambda: self.select_sector("Health Care"),
                 font=("Arial", 11, "bold"), padx=20, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Sector checkboxes
        self.sector_checkbox_frame = tk.Frame(bulk_panel, bg="#f5f5f5")
        self.sector_checkbox_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Search
        search_frame = tk.Frame(content_frame, bg=self.bg_main)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="🔍 SEARCH:", fg="#000000", bg=self.bg_main, 
                font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_tree)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=("Arial", 14), bg="white", fg="#000000", 
                               relief=tk.SOLID, bd=2, width=40)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Selected portfolio display
        selected_panel = tk.LabelFrame(content_frame, text=" SELECTED PORTFOLIO ", 
                                       bg="#fff3e0", fg="#000000", font=("Arial", 12, "bold"), bd=2)
        selected_panel.pack(fill=tk.X, pady=(0, 10))
        
        self.selected_text = tk.Text(selected_panel, height=4, wrap=tk.WORD, 
                                     font=("Arial", 11, "bold"), bg="white", fg="#000000",
                                     relief=tk.FLAT, padx=10, pady=10)
        self.selected_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Stock list tree
        tree_frame = tk.Frame(content_frame, bg=self.bg_main)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Setup tree style
        style = ttk.Style()
        style.configure("Treeview", background="white", foreground="black", 
                       rowheight=35, font=("Arial", 11), fieldbackground="white")
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), 
                       foreground="black", background="#e0e0e0")
        style.map('Treeview', background=[('selected', '#32CD32')],
                 foreground=[('selected', 'black')])
        
        self.tree = ttk.Treeview(tree_frame, columns=("Name", "Sector", "Price"), 
                                show="tree headings", selectmode="browse", height=18)
        self.tree.heading("#0", text="✓ Ticker")
        self.tree.heading("Name", text="Company Name")
        self.tree.heading("Sector", text="Sector")
        self.tree.heading("Price", text="Last Price")
        
        self.tree.column("#0", width=120)
        self.tree.column("Name", width=350)
        self.tree.column("Sector", width=250)
        self.tree.column("Price", width=100)
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        # Footer - at bottom of main_frame
        footer = tk.Frame(main_frame, bg="#f5f5f5", height=100)
        footer.pack(fill=tk.X, padx=30, pady=20, side=tk.BOTTOM)
        
        # Stock count
        count_frame = tk.Frame(footer, bg="#1a1a1a", relief=tk.RAISED, bd=3)
        count_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(count_frame, text="SELECTED:", bg="#1a1a1a",
                fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(20, 5), pady=15)
        
        self.count_label = tk.Label(count_frame, text="0", bg="#1a1a1a",
                                    fg=self.accent, font=("Arial", 32, "bold"))
        self.count_label.pack(side=tk.LEFT, padx=(0, 20), pady=15)
        
        # Next button
        next_btn = tk.Button(footer, text="NEXT: CONFIGURE OPTIONS STRATEGY →", 
                            bg=self.accent, fg="#000000", font=("Arial", 16, "bold"), 
                            command=self.open_strategy_tab, cursor="hand2", 
                            padx=40, pady=18, relief=tk.RAISED, bd=4)
        next_btn.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def load_sp500_universe(self):
        """Load S&P 500 stocks from Wikipedia"""
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            table = pd.read_html(io.StringIO(response.text), flavor='html5lib')[0]
            
            self.app.full_universe = []
            for _, row in table.iterrows():
                self.app.full_universe.append({
                    'ticker': row['Symbol'].replace('.', '-'), 
                    'name': row['Security'], 
                    'sector': row['GICS Sector'],
                    'price': None  # Will be populated on demand
                })
            
            self.create_sector_checkboxes()
            self.refresh_tree(self.app.full_universe)
            print(f"✓ Loaded {len(self.app.full_universe)} S&P 500 stocks")
            
        except Exception as e:
            messagebox.showerror("Data Error", f"Could not load S&P 500 data: {e}")
    
    def create_sector_checkboxes(self):
        """Create checkboxes for each sector"""
        sectors = sorted(set(d['sector'] for d in self.app.full_universe))
        for idx, sector in enumerate(sectors):
            var = tk.BooleanVar()
            self.sector_vars[sector] = var
            
            cb = tk.Checkbutton(self.sector_checkbox_frame, text=sector, variable=var,
                          command=self.on_sector_toggle, bg="#f5f5f5", fg="#000000",
                          font=("Arial", 10), activebackground="#e0e0e0",
                          selectcolor="white")
            cb.grid(row=idx//3, column=idx%3, sticky='w', padx=10, pady=3)
    
    def on_sector_toggle(self):
        """Handle sector checkbox toggle"""
        for sector, var in self.sector_vars.items():
            tickers = {d['ticker'] for d in self.app.full_universe if d['sector'] == sector}
            if var.get(): 
                self.app.selected_tickers.update(tickers)
            else: 
                self.app.selected_tickers.difference_update(tickers)
        
        self.refresh_tree(self.app.full_universe)
        self.update_selected_display()
    
    def select_sector(self, sector_name):
        """Quick select a specific sector"""
        if sector_name in self.sector_vars:
            self.sector_vars[sector_name].set(True)
            self.on_sector_toggle()
    
    def select_all_sp500(self):
        """Select all S&P 500 stocks"""
        self.app.selected_tickers = {d['ticker'] for d in self.app.full_universe}
        for v in self.sector_vars.values(): 
            v.set(True)
        self.refresh_tree(self.app.full_universe)
        self.update_selected_display()
    
    def clear_all_selections(self):
        """Clear all selections"""
        self.app.selected_tickers.clear()
        for v in self.sector_vars.values(): 
            v.set(False)
        self.refresh_tree(self.app.full_universe)
        self.update_selected_display()
    
    def refresh_tree(self, data):
        """Refresh the treeview with current data"""
        self.tree.delete(*self.tree.get_children())
        for d in data:
            icon = self.icon_checked if d['ticker'] in self.app.selected_tickers else self.icon_unchecked
            price_str = f"${d['price']:.2f}" if d['price'] else "---"
            self.tree.insert("", "end", iid=d['ticker'], 
                           text=f"{icon} {d['ticker']}", 
                           values=(d['name'], d['sector'], price_str))
    
    def on_tree_click(self, event):
        """Handle tree item click"""
        iid = self.tree.identify_row(event.y)
        if iid:
            if iid in self.app.selected_tickers: 
                self.app.selected_tickers.discard(iid)
            else: 
                self.app.selected_tickers.add(iid)
            self.update_selected_display()
            self.refresh_tree(self.app.full_universe)
    
    def filter_tree(self, *args):
        """Filter tree based on search"""
        q = self.search_var.get().upper()
        filtered = [d for d in self.app.full_universe 
                   if q in d['ticker'] or q in d['sector'].upper() or q in d['name'].upper()]
        self.refresh_tree(filtered)
    
    def update_selected_display(self):
        """Update the selected portfolio display"""
        self.selected_text.delete(1.0, tk.END)
        count = len(self.app.selected_tickers)
        sorted_tickers = sorted(self.app.selected_tickers)
        
        if count == 0:
            self.selected_text.insert(1.0, "No stocks selected. Click stocks below or use bulk selection buttons.")
        else:
            self.selected_text.insert(1.0, 
                f"TOTAL SELECTED: {count} stocks\n\n" + 
                ", ".join(sorted_tickers))
        
        self.count_label.config(text=str(count))
    
    def open_strategy_tab(self):
        """Open the strategy configuration tab"""
        if not self.app.selected_tickers:
            return messagebox.showwarning("No Selection", 
                "Please select at least one stock before proceeding.")
        
        self.app.enable_strategy_tab()
        self.app.notebook.select(1)
