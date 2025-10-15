import tkinter as tk
from tkinter import ttk


class CategoriesPage:
    def __init__(self, master):
        self.master = master
        
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        main_frame = ttk.Frame(master, padding="30")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        ttk.Label(main_frame, text="Manage Categories", style='H2.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 20))
        
        content_container = ttk.Frame(main_frame)
        content_container.grid(row=1, column=0, sticky='nsew')
        content_container.columnconfigure(0, weight=1)
        content_container.columnconfigure(1, weight=1)
        content_container.grid_rowconfigure(0, weight=1)
        
        list_frame = ttk.Frame(content_container)
        list_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 15))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        self.cat_tree = ttk.Treeview(list_frame, columns=('type', 'budget'), show='headings', height=10)
        self.cat_tree.heading('type', text='Type')
        self.cat_tree.heading('budget', text='Budget')
        self.cat_tree.column('type', width=100)
        self.cat_tree.column('budget', width=100)
        self.cat_tree.grid(row=0, column=0, sticky='nsew', pady=(0, 10))

        categories = [
            ("Groceries", "Expense", "$400"),
            ("Salary", "Income", "N/A"),
            ("Utilities", "Expense", "$150"),
        ]
        for name, c_type, budget in categories:
            self.cat_tree.insert('', 'end', text=name, values=(c_type, budget))

        add_frame = ttk.Frame(content_container, style='Card.TFrame', padding="15")
        add_frame.grid(row=0, column=1, sticky='nsew', padx=(15, 0))
        
        ttk.Label(add_frame, text="Category Details", style='H4.TLabel').pack(anchor='w', pady=(0, 10))
        
        ttk.Label(add_frame, text="Name").pack(anchor='w')
        ttk.Entry(add_frame).pack(fill='x', pady=(0, 10))
        
        ttk.Label(add_frame, text="Type").pack(anchor='w')
        ttk.Combobox(add_frame, values=["Expense", "Income"], state="readonly").pack(fill='x', pady=(0, 10))
        
        ttk.Button(add_frame, text="Add New Category", style='Accent.TButton', command=self.add_category).pack(fill='x', ipady=8, pady=(15, 0))

    def add_category(self):
        print("Action: Adding new category.")
