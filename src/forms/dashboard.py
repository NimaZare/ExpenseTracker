import sv_ttk
import tkinter as tk
import matplotlib.pyplot as plt

from tkinter import ttk
from datetime import datetime
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from forms.reports import ReportsPage
from forms.settings import SettingsPage
from tools.theme_tools import ThemeManager
from forms.categories import CategoriesPage
from services.transaction import TransactionService
from forms.add_transaction import AddTransactionPage


class ExpenseTrackerApp:
    def __init__(self, master):
        self.master = master
        self.is_initialized = False
        self.theme_manager = ThemeManager(master)
        self.transaction_service = TransactionService()

        window_width = 1100
        window_height = 700
        master.update_idletasks()
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        master.geometry(f"{window_width}x{window_height}+{x}+{y}")

        master.grid_columnconfigure(0, weight=0, minsize=200)
        master.grid_columnconfigure(1, weight=1)
        
        master.grid_columnconfigure(2, weight=0, minsize=300)
        master.grid_rowconfigure(0, weight=1)

        self.theme_manager.apply_theme()
        
        self.chart_data = {}

        self.pages = {
            "dashboard": self._load_dashboard,
            "add": AddTransactionPage,
            "reports": ReportsPage,
            "categories": CategoriesPage,
            "settings": SettingsPage,
        }

        self.sidebar_frame = ttk.Frame(master, padding="15 10")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1) 
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(self.sidebar_frame, text="TRACKER", style='H3.TLabel', anchor='w').grid(row=0, column=0, sticky='ew', pady=(0, 20))

        nav_container = ttk.Frame(self.sidebar_frame)
        nav_container.grid(row=1, column=0, sticky="nsew")

        nav_buttons = [
            ("Dashboard", "dashboard"),
            ("Add Transaction", "add"),
            ("Reports", "reports"),
            ("Categories", "categories"),
            ("Settings", "settings"),
        ]

        self.nav_widgets = {}
        for text, page in nav_buttons:
            btn = ttk.Button(nav_container, text=text, command=lambda p=page: self.load_page(p))
            btn.pack(fill='x', ipady=10, pady=4)
            self.nav_widgets[page] = btn

        self.theme_check = ttk.Checkbutton(
            self.sidebar_frame,
            text="🌙 Dark Mode" if sv_ttk.get_theme() == "dark" else "☀ Light Mode",
            style="Switch.TCheckbutton",
            command=self.toggle_theme
        )

        if sv_ttk.get_theme() == "dark":
            self.theme_check.state(['selected'])
            self.theme_check.grid(row=2, column=0, sticky='ew', ipady=5, pady=(40, 0))
        else:
            self.theme_check.grid(row=2, column=0, sticky='ew', ipady=5, pady=(40, 0))

        self.center_frame = ttk.Frame(master, padding="20")
        self.center_frame.grid(row=0, column=1, sticky="nsew")

        self.right_frame = ttk.Frame(master, padding="20 15")
        self.right_frame.grid(row=0, column=2, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)

        self._create_right_panel()

        self.load_page("dashboard")
        self.is_initialized = True

    def _set_active_button(self, active_page):
        for page, btn in self.nav_widgets.items():
            if page == active_page:
                btn.config(style='Accent.TButton')
            else:
                btn.config(style='TButton')

    def load_page(self, page_name):
        for widget in self.center_frame.winfo_children():
            widget.destroy()

        self._set_active_button(page_name)

        if page_name == "dashboard":
            self._load_dashboard()
            self.right_frame.grid()
            self.master.grid_columnconfigure(2, weight=0, minsize=300)
        else:
            self.right_frame.grid_remove()
            self.master.grid_columnconfigure(2, weight=0, minsize=0)
            page_class = self.pages.get(page_name)
            if page_class:
                page_class(self.center_frame)

    def _load_dashboard(self):
        now = datetime.now()
        
        summary = self.transaction_service.get_dashboard_summary(now.month, now.year)
        total_balance = summary['total_balance']
        monthly_expenses = summary['monthly_expenses']
        monthly_income = summary['monthly_income']
        
        self.chart_data = self.transaction_service.get_spending_breakdown(now.month, now.year)

        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(2, weight=1)

        self.balance_card = ttk.Frame(self.center_frame, style='Card.TFrame', padding="20")
        self.balance_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ttk.Label(self.balance_card, text="CURRENT BALANCE", style='H4.TLabel').pack(anchor='w')
        
        ttk.Label(
            self.balance_card, 
            text=f"${total_balance:,.2f}", 
            font=("Helvetica", 36, "bold"), 
            foreground=self._get_color('success' if total_balance >= 0 else 'error')
        ).pack(anchor='w', pady=(5, 0))
        
        metrics_frame = ttk.Frame(self.center_frame)
        metrics_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)

        self._create_metric_card(metrics_frame, 0, "MONTHLY EXPENSES", f"${monthly_expenses:,.2f}", "error")
        self._create_metric_card(metrics_frame, 1, "MONTHLY INCOME", f"${monthly_income:,.2f}", "success")
        
        chart_frame = ttk.Frame(self.center_frame, style='Card.TFrame', padding="20")
        chart_frame.grid(row=2, column=0, sticky="nsew")
        
        ttk.Label(chart_frame, text="Monthly Spending Breakdown", style='H4.TLabel').pack(anchor='w', pady=(0, 10))
        
        self._create_spending_chart(chart_frame)

    def _create_spending_chart(self, parent_frame):
        """
        Creates a Matplotlib pie chart with the legend/categories placed on the 
        left side of the chart using GridSpec for precise positioning.
        """
        categories = list(self.chart_data.keys())
        amounts = list(self.chart_data.values())

        if not amounts:
             ttk.Label(parent_frame, text="No expense data for this month.", style='H6.TLabel').pack(pady=50)
             return

        fig = plt.Figure(figsize=(7, 4.5), dpi=100)
        gs = GridSpec(1, 2, figure=fig, width_ratios=[1, 2], wspace=0.1) 
        
        ax_pie = fig.add_subplot(gs[0, 1])
        ax_legend = fig.add_subplot(gs[0, 0])
        
        fig.patch.set_alpha(0.0)
        ax_pie.patch.set_alpha(0.0)
        ax_legend.patch.set_alpha(0.0)
        
        autopct_format = lambda pct: f"{pct:.1f}%" if pct > 5 else ''

        wedges, texts, autotexts = ax_pie.pie(
            amounts, 
            autopct=autopct_format, 
            startangle=90,
            wedgeprops={'edgecolor': 'none', 'linewidth': 0.5},
            textprops={'color': 'white', 'fontsize': 10}
        )
        
        ax_pie.axis('equal')
        
        ax_legend.legend(
            wedges,
            categories,
            title="Categories",
            loc='center',
            frameon=False,
            title_fontsize='large',
            fontsize='medium',
            labelcolor='black',
        )

        ax_legend.axis('off')
        fig.tight_layout(pad=0) 
        
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas_widget = canvas.get_tk_widget()
        
        canvas_widget.pack(fill='both', expand=True, padx=10, pady=10)
        canvas.draw()

    def _create_right_panel(self):
        ttk.Button(self.right_frame, text="+ New Expense", style='Accent.TButton', 
                    command=lambda: self.load_page("add")).pack(fill='x', ipady=15, pady=(0, 25))

        ttk.Label(self.right_frame, text="RECENT TRANSACTIONS", style='H4.TLabel').pack(anchor='w', pady=(0, 10))

        self.tree = ttk.Treeview(self.right_frame, columns=('description', 'amount'), show='headings', height=10)
        self.tree.heading('description', text='Description')
        self.tree.heading('amount', text='Amount', anchor='e')
        self.tree.column('description', width=180, stretch=tk.YES)
        self.tree.column('amount', width=80, stretch=tk.NO, anchor='e')
        
        recent_transactions = self.transaction_service.get_recent_transactions(limit=5)
        
        for t in recent_transactions:
            desc = t.get('description', 'N/A')
            amount = t['amount']
            ttype = t['type']
            
            color_tag = 'success' if ttype == 'Income' else 'error'
            
            self.tree.insert('', 'end', values=(desc, f"${amount:.2f}"), tags=(color_tag,))

        self.tree.tag_configure('error', foreground='#F44336')
        self.tree.tag_configure('success', foreground='#4CAF50')
        self.tree.tag_configure('info', foreground='#2196F3')

        self.tree.pack(fill='both', expand=True)

    def toggle_theme(self):
        current_theme = sv_ttk.get_theme()
        if current_theme == "dark":
            sv_ttk.set_theme("light")
            self.theme_manager.save_theme_preference("light")
            self.theme_manager.apply_theme()
            self.theme_check.config(text="☀ Light Mode")
        else:
            sv_ttk.set_theme("dark")
            self.theme_manager.save_theme_preference("dark")
            self.theme_manager.apply_theme()
            self.theme_check.config(text="🌙 Dark Mode")
        
        if self.is_initialized and self.master.title().startswith("Expense Tracker"):
            self.load_page("dashboard")

    def _create_metric_card(self, parent, column, title, value, color_tag):
        card = ttk.Frame(parent, style='Card.TFrame', padding="15")
        card.grid(row=0, column=column, sticky="nsew", padx=(5 if column == 1 else 0, 5 if column == 0 else 0))
        
        ttk.Label(card, text=title, style='H5.TLabel').pack(anchor='w')
        
        ttk.Label(card, text=value, font=("Helvetica", 20, "bold"), 
                  foreground=self._get_color(color_tag)).pack(anchor='w')
        
        return card

    def _get_color(self, tag):
        if sv_ttk.get_theme() == 'dark':
            colors = {'error': '#F44336', 'success': '#4CAF50', 'info': '#2196F3'}
        else:
            colors = {'error': '#D32F2F', 'success': '#388E3C', 'info': '#1976D2'}
        return colors.get(tag, 'white')
