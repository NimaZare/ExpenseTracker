import tkinter as tk
from tkinter import ttk
import sv_ttk


class ReportsPage:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.main_frame = ttk.Frame(parent_frame)
        self.main_frame.pack(fill='both', expand=True)
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=250)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.filter_frame = ttk.Frame(self.main_frame, padding="20", style='Card.TFrame')
        self.filter_frame.grid(row=0, column=0, sticky="nsew")
        
        ttk.Label(self.filter_frame, text="REPORT FILTERS", style='H3.TLabel').pack(anchor='w', pady=(0, 20))
        
        ttk.Label(self.filter_frame, text="Date Range", style='H5.TLabel').pack(anchor='w', pady=(10, 5))
        self.date_range = tk.StringVar(value="This Month")
        ranges = ["Last 7 Days", "This Month", "Last 3 Months", "Custom"]
        for r in ranges:
            ttk.Radiobutton(self.filter_frame, text=r, value=r, variable=self.date_range).pack(anchor='w', padx=5)

        ttk.Label(self.filter_frame, text="Categories", style='H5.TLabel').pack(anchor='w', pady=(20, 5))
        ttk.Entry(self.filter_frame, state='readonly').pack(fill='x', ipady=5)
        
        ttk.Button(self.filter_frame, text="Apply Filters", style='Accent.TButton', command=self.generate_report).pack(fill='x', ipady=10, pady=(30, 10))


        self.report_content_frame = ttk.Frame(self.main_frame, padding="20")
        self.report_content_frame.grid(row=0, column=1, sticky="nsew")
        self.report_content_frame.grid_columnconfigure(0, weight=1)
        self.report_content_frame.grid_rowconfigure(2, weight=1)

        ttk.Label(self.report_content_frame, text="Financial Reports", style='H2.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 20))

        chart1_frame = ttk.Frame(self.report_content_frame, style='Card.TFrame', padding="15")
        chart1_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        ttk.Label(chart1_frame, text="Monthly Expense Trend (Bar Chart Placeholder)", style='H4.TLabel').pack(anchor='w', pady=5)
        
        ttk.Label(chart1_frame, text="[Area for Matplotlib/Plotly Bar Chart]").pack(fill='x', expand=True)

        ttk.Label(self.report_content_frame, text="DETAILED TRANSACTIONS", style='H4.TLabel').grid(row=2, column=0, sticky='w', pady=(15, 10))
        
        self.tree = ttk.Treeview(self.report_content_frame, columns=('date', 'category', 'amount'), show='headings', height=10)
        self.tree.heading('date', text='Date')
        self.tree.heading('category', text='Category')
        self.tree.heading('amount', text='Amount', anchor='e')
        self.tree.column('date', width=100)
        self.tree.column('category', width=150)
        self.tree.column('amount', width=100, anchor='e')
        self.tree.grid(row=3, column=0, sticky='nsew')
        self.report_content_frame.grid_rowconfigure(3, weight=1)

        self.tree.insert('', 'end', values=('2024-10-10', 'Groceries', '$85.20'))
        self.tree.insert('', 'end', values=('2024-10-05', 'Salary', '$1,500.00'))


    def generate_report(self):
        print(f"Generating Report for: {self.date_range.get()}")
