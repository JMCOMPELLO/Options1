import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import requests
import io

class StockSelectionTab:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg="#ffffff")
        self.setup_ui()
        self.load_sp500_universe()
    
    def setup_ui(self):
        # ULTRA SIMPLE - NO SCROLLING CANVAS AT ALL
        
        # Header
        header = tk.Frame(self.frame, bg="#1a1a1a", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="OPTIONS BACKTEST PRO", fg="#32CD32", 
                bg="#1a1a1a", font=("Arial", 24, "bold")).pack(pady=10)
        
        # Main area
        main = tk.Frame(self.frame, bg="#ffffff")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Bulk selection
        bulk = tk.LabelFrame(main, text=" BULK SELECTION ", bg="#f5f5f5", 
                            fg="#000000", font=("Arial", 12, "bold"), bd=2)
        bulk.pack(fill=tk.X, pady=(0, 10))
        
        bf = tk.Frame(bulk, bg="#f5f5f5")
        bf.pack(padx=15, pady=10)
        
        tk.Button(bf, text="✓ SELECT ALL", bg="#32CD32", fg="#000000",
                 command=self.select_all, font=("Arial", 11, "bold"),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(bf, text="✗ CLEAR", bg="#f44336", fg="white",
                 command=self.clear_all, font=("Arial", 11, "bold"),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(bf, text="TECH", bg="#2196F3", fg="white",
                 command=lambda: self.select_sector("Information Technology"),
                 font=("Arial", 11, "bold"), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Search
        sf = tk.Frame(main, bg="#ffffff")
        sf.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(sf, text="SEARCH:", fg="#000000", bg="#ffffff", 
                font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_tree)
        tk.Entry(sf, textvariable=self.search_var, font=("Arial", 12), 
                bg="white", fg="#000000", width=30).pack(side=tk.LEFT)
        
        # Selected count
        self.count_label = tk.Label(sf, text="Selected: 0", bg="#ffffff",
                                    fg="#000000", font=("Arial", 12, "bold"))
        self.count_label.pack(side=tk.RIGHT, padx=10)
        
        # Stock tree with NATIVE scrollbar (works on Mac!)
        tree_frame = tk.Frame(main, bg="#ffffff")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        style = ttk.Style()
        style.configure("Treeview", background="white", foreground="#000000", 
                       rowheight=28, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), 
                       foreground="#000000")
        style.map('Treeview', background=[('selected', '#32CD32')],
                 foreground=[('selected', '#000000')])
        
        self.tree = ttk.Treeview(tree_frame, columns=("Name", "Sector"), 
                                show="tree headings", height=20)
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
        
        # Footer with NEXT button - ALWAYS VISIBLE
        footer = tk.Frame(self.frame, bg="#f5f5f5", height=80)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Button(footer, text="NEXT: CONFIGURE STRATEGY →", 
                 bg="#32CD32", fg="#000000", font=("Arial", 18, "bold"), 
                 command=self.next_tab, padx=50, pady=20).pack(pady=15)
    
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
    
    def select_sector(self, sector):
        tickers = {d['ticker'] for d in self.app.full_universe if d['sector'] == sector}
        self.app.selected_tickers.update(tickers)
        self.refresh_tree(self.app.full_universe)
        self.update_count()
    
    def select_all(self):
        self.app.selected_tickers = {d['ticker'] for d in self.app.full_universe}
        self.refresh_tree(self.app.full_universe)
        self.update_count()
    
    def clear_all(self):
        self.app.selected_tickers.clear()
        self.refresh_tree(self.app.full_universe)
        self.update_count()
    
    def refresh_tree(self, data):
        self.tree.delete(*self.tree.get_children())
        for d in data:
            icon = "✓" if d['ticker'] in self.app.selected_tickers else "○"
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
        self.count_label.config(text=f"Selected: {len(self.app.selected_tickers)}")
    
    def next_tab(self):
        if not self.app.selected_tickers:
            messagebox.showwarning("No Selection", "Please select at least one stock.")
            return
        self.app.enable_strategy_tab()
        self.app.notebook.select(1)
