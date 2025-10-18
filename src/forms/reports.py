import csv
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, messagebox
from collections import defaultdict
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tools.utils import Utils
from services.category import CategoryService
from services.transaction import TransactionService


class ReportsPage:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.category_service = CategoryService()
        self.transaction_service = TransactionService()
        self.settings = Utils.load_app_settings()
        
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.main_frame = ttk.Frame(parent_frame)
        self.main_frame.pack(fill='both', expand=True)
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=250)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.filter_frame = ttk.Frame(self.main_frame, padding="20", style='Card.TFrame')
        self.filter_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ttk.Label(self.filter_frame, text="REPORT FILTERS", style='H3.TLabel').pack(anchor='w', pady=(0, 20))
        
        ttk.Label(self.filter_frame, text="Date Range", style='H5.TLabel').pack(anchor='w', pady=(10, 5))
        self.date_range = tk.StringVar(value="This Month")
        ranges = ["Last 7 Days", "Last 30 Days", "This Month", "Last 3 Months", "This Year", "All Time"]
        for r in ranges:
            ttk.Radiobutton(self.filter_frame, text=r, value=r, variable=self.date_range).pack(anchor='w', padx=5)

        ttk.Label(self.filter_frame, text="Transaction Type", style='H5.TLabel').pack(anchor='w', pady=(20, 5))
        self.trans_type = tk.StringVar(value="All")
        types = ["All", "Expense", "Income", "Transfer"]
        for t in types:
            ttk.Radiobutton(self.filter_frame, text=t, value=t, variable=self.trans_type).pack(anchor='w', padx=5)

        ttk.Label(self.filter_frame, text="Category", style='H5.TLabel').pack(anchor='w', pady=(20, 5))
        self.category_var = tk.StringVar(value="All Categories")
        self.category_combo = ttk.Combobox(self.filter_frame, textvariable=self.category_var, state='readonly')
        self.category_combo.pack(fill='x', ipady=5)
        self.load_categories()

        ttk.Label(self.filter_frame, text="Account", style='H5.TLabel').pack(anchor='w', pady=(20, 5))
        self.account_var = tk.StringVar(value="All Accounts")
        self.account_combo = ttk.Combobox(self.filter_frame, textvariable=self.account_var, 
                                          values=["All Accounts", "Checking", "Savings", "Cash", "Credit Card"], 
                                          state='readonly')
        self.account_combo.pack(fill='x', ipady=5)
        
        ttk.Button(self.filter_frame, text="Apply Filters", style='Accent.TButton', 
                   command=self.generate_report).pack(fill='x', ipady=10, pady=(30, 5))
        ttk.Button(self.filter_frame, text="Export Report", 
                   command=self.export_report).pack(fill='x', ipady=10, pady=(5, 5))
        ttk.Button(self.filter_frame, text="Reset Filters", 
                   command=self.reset_filters).pack(fill='x', ipady=10, pady=(5, 0))

        self.report_content_frame = ttk.Frame(self.main_frame, padding="20")
        self.report_content_frame.grid(row=0, column=1, sticky="nsew")
        self.report_content_frame.grid_columnconfigure(0, weight=1)
        self.report_content_frame.grid_rowconfigure(3, weight=1)

        ttk.Label(self.report_content_frame, text="Financial Reports", style='H2.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 20))

        summary_frame = ttk.Frame(self.report_content_frame)
        summary_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        summary_frame.grid_columnconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(1, weight=1)
        summary_frame.grid_columnconfigure(2, weight=1)

        self.income_card = self._create_summary_card(summary_frame, "Total Income", f"{self.settings.get('currency', '$')}0.00", 0, 0)

        self.expense_card = self._create_summary_card(summary_frame, "Total Expenses", f"{self.settings.get('currency', '$')}0.00", 0, 1)

        self.balance_card = self._create_summary_card(summary_frame, "Net Balance", f"{self.settings.get('currency', '$')}0.00", 0, 2)

        chart_frame = ttk.Frame(self.report_content_frame, style='Card.TFrame', padding="15")
        chart_frame.grid(row=2, column=0, sticky='ew', pady=(0, 20))
        chart_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(chart_frame, text="Expense Breakdown by Category", style='H4.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 10))
        
        self.chart_container = ttk.Frame(chart_frame)
        self.chart_container.grid(row=1, column=0, sticky='ew')
        
        ttk.Label(self.report_content_frame, text="DETAILED TRANSACTIONS", style='H4.TLabel').grid(
            row=3, column=0, sticky='w', pady=(15, 10))
        
        table_frame = ttk.Frame(self.report_content_frame)
        table_frame.grid(row=4, column=0, sticky='nsew')
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(table_frame, columns=('id', 'date', 'type', 'category', 'account', 'amount', 'description'), 
                                 show='headings', height=10)
        
        self.tree.column('id', width=0, stretch=False)
        self.tree.column('date', width=100)
        self.tree.column('type', width=80)
        self.tree.column('category', width=120)
        self.tree.column('account', width=100)
        self.tree.column('amount', width=100, anchor='e')
        self.tree.column('description', width=200)
        
        self.tree.heading('id', text='')
        self.tree.heading('date', text='Date')
        self.tree.heading('type', text='Type')
        self.tree.heading('category', text='Category')
        self.tree.heading('account', text='Account')
        self.tree.heading('amount', text='Amount')
        self.tree.heading('description', text='Description')
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.report_content_frame.grid_rowconfigure(4, weight=1)

        self.status_label = ttk.Label(self.report_content_frame, text="", style='H5.TLabel')
        self.status_label.grid(row=5, column=0, sticky='w', pady=(10, 0))

        self.generate_report()

    def _create_summary_card(self, parent, title, value, row, col):
        """Create a summary card widget"""
        card = ttk.Frame(parent, style='Card.TFrame', padding="15")
        card.grid(row=row, column=col, sticky='ew', padx=5)
        
        ttk.Label(card, text=title, style='H5.TLabel').pack(anchor='w')
        value_label = ttk.Label(card, text=value, style='H2.TLabel')
        value_label.pack(anchor='w', pady=(5, 0))
        
        return value_label

    def load_categories(self):
        """Load categories into the filter dropdown"""
        try:
            categories = self.category_service.get_all()
            category_names = ["All Categories"] + [cat['name'] for cat in categories]
            self.category_combo['values'] = category_names
            self.category_combo.set("All Categories")
        except Exception as e:
            print(f"Error loading categories: {e}")

    def get_date_range(self):
        """Calculate start and end dates based on selected range"""
        today = datetime.now().date()
        range_value = self.date_range.get()
        
        if range_value == "Last 7 Days":
            start_date = today - timedelta(days=7)
            end_date = today
        elif range_value == "Last 30 Days":
            start_date = today - timedelta(days=30)
            end_date = today
        elif range_value == "This Month":
            start_date = today.replace(day=1)
            end_date = today
        elif range_value == "Last 3 Months":
            start_date = today - timedelta(days=90)
            end_date = today
        elif range_value == "This Year":
            start_date = today.replace(month=1, day=1)
            end_date = today
        else:  # All Time
            start_date = datetime(2000, 1, 1).date()
            end_date = today
        
        return start_date.isoformat(), end_date.isoformat()

    def generate_report(self):
        """Generate report based on selected filters"""
        try:
            start_date, end_date = self.get_date_range()
            transactions = self.transaction_service.get_transactions_by_date_range(start_date, end_date)

            filtered_transactions = []
            for trans in transactions:
                if self.trans_type.get() != "All" and trans['type'] != self.trans_type.get():
                    continue
                
                if self.category_var.get() != "All Categories" and trans['category'] != self.category_var.get():
                    continue
                
                if self.account_var.get() != "All Accounts" and trans['account'] != self.account_var.get():
                    continue
                
                filtered_transactions.append(trans)

            self.filtered_transactions = filtered_transactions
            self.update_summary(filtered_transactions)
            self.update_chart(filtered_transactions)
            self.update_table(filtered_transactions)

            self.status_label.config(text=f"Showing {len(filtered_transactions)} transactions from {start_date} to {end_date}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def update_summary(self, transactions):
        """Update summary cards with calculated values"""
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'Expense')
        net_balance = total_income - total_expense

        self.income_card.config(text=f"{self.settings.get('currency', '$')}{total_income:,.2f}")
        self.expense_card.config(text=f"{self.settings.get('currency', '$')}{total_expense:,.2f}")
        self.balance_card.config(text=f"{self.settings.get('currency', '$')}{net_balance:,.2f}")

    def update_chart(self, transactions):
        """Update the pie chart with expense breakdown"""
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        expenses = [t for t in transactions if t['type'] == 'Expense']
        
        if not expenses:
            ttk.Label(self.chart_container, text="No expense data to display").pack()
            return
        
        category_totals = defaultdict(float)
        for expense in expenses:
            category_totals[expense['category']] += expense['amount']
        
        fig = Figure(figsize=(8, 4), dpi=80)
        ax = fig.add_subplot(111)
        
        categories = list(category_totals.keys())
        values = list(category_totals.values())
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
        
        ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=90, colors=colors[:len(categories)])
        ax.axis('equal')
        
        canvas = FigureCanvasTkAgg(fig, self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def update_table(self, transactions):
        """Update transactions table"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        sorted_transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
        
        for trans in sorted_transactions:
            amount_str = f"{self.settings.get('currency', '$')}{trans['amount']:,.2f}"
            if trans['type'] == 'Expense':
                amount_str = f"-{amount_str}"
            
            self.tree.insert('', 'end', values=(
                trans['id'],
                trans['date'],
                trans['type'],
                trans['category'],
                trans['account'],
                amount_str,
                trans.get('description', '')
            ))

    def reset_filters(self):
        """Reset all filters to default"""
        self.date_range.set("This Month")
        self.trans_type.set("All")
        self.category_var.set("All Categories")
        self.account_var.set("All Accounts")
        self.generate_report()

    def export_report(self):
        """Export report to CSV"""
        self.save_to_csv(self.filtered_transactions)

    def save_to_csv(self, transactions):
        """Save the filtered transactions to a CSV file"""
        if not transactions:
            messagebox.showinfo("Export", "No transactions to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                   filetypes=[("CSV files", "*.csv"),
                                                              ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Date", "Type", "Category", "Account", "Amount", "Description"])
                for trans in transactions:
                    writer.writerow([trans['id'],
                                     trans['date'],
                                     trans['type'],
                                     trans['category'],
                                     trans['account'],
                                     trans['amount'],
                                     trans.get('description', '')])
            messagebox.showinfo("Export", "Report exported successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
