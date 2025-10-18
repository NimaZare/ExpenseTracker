import tkinter as tk
from tools.utils import Utils
from tkinter import ttk, messagebox
from services.category import CategoryService
from services.transaction import TransactionService


class AddTransactionPage:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.trs = TransactionService()
        self.category_service = CategoryService()
        self.settings = Utils.load_app_settings()
        
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.main_frame = ttk.Frame(parent_frame, padding="30")
        self.main_frame.pack(fill='both', expand=True)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.main_frame, text="Add New Transaction", style='H2.TLabel').grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 25))

        type_frame = ttk.Frame(self.main_frame)
        type_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        
        self.transaction_type = tk.StringVar(value="Expense")
        
        ttk.Label(type_frame, text="Type:", style='H5.TLabel').pack(side='left', padx=(0, 10))
        
        ttk.Radiobutton(type_frame, text="Expense", value="Expense", variable=self.transaction_type, style='Accent.TRadiobutton').pack(side='left', padx=5)
        ttk.Radiobutton(type_frame, text="Income", value="Income", variable=self.transaction_type, style='Accent.TRadiobutton').pack(side='left', padx=5)
        ttk.Radiobutton(type_frame, text="Transfer", value="Transfer", variable=self.transaction_type, style='Accent.TRadiobutton').pack(side='left', padx=5)

        self.amount_entry = self._create_input_field(self.main_frame, f"Amount ({self.settings.get('currency', '$')})", ttk.Entry, row=2, column=0, large=True)
        self.date_entry = self._create_input_field(self.main_frame, "Date", ttk.Entry, row=2, column=1, default_text=f"{self.settings.get('date_format', 'YYYY-MM-DD')}", large=True)

        categories_db = self.category_service.get_all()
        categories = [cat['name'] for cat in categories_db]
        categories.extend(Utils.get_default_categories())
        self.category_combo = self._create_dropdown_field(self.main_frame, "Category", categories, row=4, column=0)
        
        accounts = ["Checking", "Savings", "Cash", "Credit Card"]
        self.account_combo = self._create_dropdown_field(self.main_frame, "Account", accounts, row=4, column=1)
        
        ttk.Label(self.main_frame, text="Description / Note", style='H5.TLabel').grid(row=6, column=0, sticky='w', pady=(15, 5))
        self.description_entry = ttk.Entry(self.main_frame)
        self.description_entry.grid(row=7, column=0, columnspan=2, sticky='ew', ipady=5)
        
        ttk.Button(self.main_frame, text="Save Transaction", style='Accent.TButton', command=self.save_transaction).grid(row=8, column=0, columnspan=2, sticky='ew', pady=(30, 10), ipady=10)


    def _create_input_field(self, parent, label_text, widget_class, row, column, large=False, default_text=""):
        padx = (0, 15) if column == 0 else (15, 0)
        ttk.Label(parent, text=label_text, style='H5.TLabel').grid(row=row, column=column, sticky='w', pady=(15, 5), padx=padx)
        entry = widget_class(parent)
        entry.grid(row=row + 1, column=column, sticky='ew', ipady=(10 if large else 5), padx=padx)
        if default_text:
            entry.insert(0, default_text)
        return entry

    def _create_dropdown_field(self, parent, label_text, options, row, column):
        padx = (0, 15) if column == 0 else (15, 0)
        ttk.Label(parent, text=label_text, style='H5.TLabel').grid(row=row, column=column, sticky='w', pady=(15, 5), padx=padx)
        combo = ttk.Combobox(parent, values=options, state="readonly")
        combo.grid(row=row + 1, column=column, sticky='ew', ipady=5, padx=padx)
        if options:
            combo.set(options[0])
        return combo

    def save_transaction(self):
        amount = self.amount_entry.get().strip()
        date = self.date_entry.get().strip()
        
        if not amount:
            messagebox.showerror("Error", "Please enter an amount")
            return
        
        try:
            amount_value = float(amount)
            if amount_value <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for amount")
            return
        
        if date == f"{self.settings.get('date_format', 'YYYY-MM-DD')}" or not date:
            messagebox.showerror("Error", "Please enter a valid date")
            return
        
        data = {
            "type": self.transaction_type.get(),
            "amount": amount_value,
            "date": date,
            "category": self.category_combo.get(),
            "account": self.account_combo.get(),
            "description": self.description_entry.get().strip()
        }
        
        try:
            result = self.trs.add_transaction(data)
            if result:
                messagebox.showinfo("Success", "Transaction saved successfully!")
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to save transaction")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields after successful save"""
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, f"{self.settings.get('date_format', 'YYYY-MM-DD')}")
        self.description_entry.delete(0, tk.END)
        self.transaction_type.set("Expense")
        self.category_combo.current(0)
        self.account_combo.current(0)
