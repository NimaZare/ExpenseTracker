import os
import csv
import json
import shutil
import tkinter as tk
from pathlib import Path
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

from tools.utils import Utils
from dotenv import load_dotenv
from database.engine import get_db_connection
from services.category import CategoryService
from services.transaction import TransactionService


load_dotenv()
DATABASE_NAME = os.getenv("DATABASE_NAME", "finance.db")
DB_URL = Utils.resource_path(f"data/{DATABASE_NAME}")

class SettingsPage:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.transaction_service = TransactionService()
        self.category_service = CategoryService()
        
        self.settings_file = Path(Utils.resource_path(f"data/app_settings.json"))
        if not self.settings_file.parent.exists():
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        self.settings = self.load_settings()
        
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_rowconfigure(0, weight=1)

        canvas = tk.Canvas(parent_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        self.main_frame = ttk.Frame(canvas, padding="30")
        
        self.main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.main_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(self.main_frame, text="Application Settings", style='H2.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 30))

        self._setup_appearance_settings()
        self._setup_preferences_settings()
        self._setup_data_management_settings()
        self._setup_account_settings()
        self._setup_about_section()

    def load_settings(self):
        """Load settings from JSON file"""
        default_settings = {
            "currency": "$",
            "date_format": "YYYY-MM-DD",
            "theme": "Dark",
            "default_account": "Checking",
            "show_decimals": True,
            "auto_backup": False
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return {**default_settings, **json.load(f)}
            except Exception:
                return default_settings
        return default_settings

    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def _create_section_frame(self, row, title):
        """Create a section frame with title"""
        section = ttk.Frame(self.main_frame, style='Card.TFrame', padding="20")
        section.grid(row=row, column=0, sticky='ew', pady=(0, 20))
        section.columnconfigure(1, weight=1)
        
        ttk.Label(section, text=title, style='H4.TLabel').grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        return section

    def _setup_appearance_settings(self):
        """Setup appearance section"""
        section = self._create_section_frame(1, "💎 Appearance")
        
        ttk.Label(section, text="Currency Symbol:", style='H5.TLabel').grid(
            row=1, column=0, sticky='w', pady=(5, 5))
        
        self.currency_var = tk.StringVar(value=self.settings.get("currency", "$"))
        currency_combo = ttk.Combobox(section, textvariable=self.currency_var,
                                      values=["$", "€", "£", "¥", "₹", "₦"], 
                                      state="readonly", width=10)
        currency_combo.grid(row=1, column=1, sticky='w', pady=(5, 5))
        currency_combo.bind('<<ComboboxSelected>>', lambda e: self.update_setting("currency", self.currency_var.get()))
        
        ttk.Label(section, text="Date Format:", style='H5.TLabel').grid(
            row=2, column=0, sticky='w', pady=(5, 5))
        
        self.date_format_var = tk.StringVar(value=self.settings.get("date_format", "YYYY-MM-DD"))
        date_combo = ttk.Combobox(section, textvariable=self.date_format_var,
                                  values=["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"], 
                                  state="readonly", width=15)
        date_combo.grid(row=2, column=1, sticky='w', pady=(5, 5))
        date_combo.bind('<<ComboboxSelected>>', lambda e: self.update_setting("date_format", self.date_format_var.get()))
        
        ttk.Label(section, text="Theme:", style='H5.TLabel').grid(
            row=3, column=0, sticky='w', pady=(5, 5))
        
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "Dark"))
        theme_combo = ttk.Combobox(section, textvariable=self.theme_var,
                                   values=["Light", "Dark"], 
                                   state="readonly", width=15)
        theme_combo.grid(row=3, column=1, sticky='w', pady=(5, 5))
        theme_combo.bind('<<ComboboxSelected>>', lambda e: self.update_setting("theme", self.theme_var.get()))

    def _setup_preferences_settings(self):
        """Setup preferences section"""
        section = self._create_section_frame(2, "⚙️ Preferences")
        
        ttk.Label(section, text="Default Account:", style='H5.TLabel').grid(
            row=1, column=0, sticky='w', pady=(5, 5))
        
        self.account_var = tk.StringVar(value=self.settings.get("default_account", "Checking"))
        account_combo = ttk.Combobox(section, textvariable=self.account_var,
                                     values=["Checking", "Savings", "Cash", "Credit Card"], 
                                     state="readonly", width=15)
        account_combo.grid(row=1, column=1, sticky='w', pady=(5, 5))
        account_combo.bind('<<ComboboxSelected>>', lambda e: self.update_setting("default_account", self.account_var.get()))
        
        self.decimals_var = tk.BooleanVar(value=self.settings.get("show_decimals", True))
        decimals_check = ttk.Checkbutton(section, text="Show decimal places in amounts", 
                                         variable=self.decimals_var,
                                         command=lambda: self.update_setting("show_decimals", self.decimals_var.get()))
        decimals_check.grid(row=2, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        self.auto_backup_var = tk.BooleanVar(value=self.settings.get("auto_backup", False))
        backup_check = ttk.Checkbutton(section, text="Enable automatic daily backups", 
                                       variable=self.auto_backup_var,
                                       command=lambda: self.update_setting("auto_backup", self.auto_backup_var.get()))
        backup_check.grid(row=3, column=0, columnspan=2, sticky='w', pady=(5, 5))

    def _setup_data_management_settings(self):
        """Setup data management section"""
        section = self._create_section_frame(3, "💾 Data Management")
        
        db_info_frame = ttk.Frame(section)
        db_info_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(5, 15))
        
        stats = self.get_database_stats()
        ttk.Label(db_info_frame, text=f"📊 Total Transactions: {stats['transactions']}", 
                  style='H5.TLabel').pack(anchor='w', pady=2)
        ttk.Label(db_info_frame, text=f"📁 Total Categories: {stats['categories']}", 
                  style='H5.TLabel').pack(anchor='w', pady=2)
        ttk.Label(db_info_frame, text=f"💽 Database Size: {stats['db_size']}", 
                  style='H5.TLabel').pack(anchor='w', pady=2)
        
        button_frame = ttk.Frame(section)
        button_frame.grid(row=2, column=0, columnspan=2, sticky='ew')
        
        ttk.Button(button_frame, text="🔄 Backup Database", 
                   command=self.backup_database, 
                   style='Accent.TButton').pack(fill='x', pady=(0, 5), ipady=8)
        
        ttk.Button(button_frame, text="📤 Export Transactions (CSV)", 
                   command=self.export_transactions).pack(fill='x', pady=(0, 5), ipady=8)
        
        ttk.Button(button_frame, text="📤 Export Categories (CSV)", 
                   command=self.export_categories).pack(fill='x', pady=(0, 5), ipady=8)
        
        ttk.Button(button_frame, text="📥 Import Data", 
                   command=self.import_data).pack(fill='x', pady=(0, 5), ipady=8)

    def _setup_account_settings(self):
        """Setup account management section"""
        section = self._create_section_frame(4, "👤 Account Management")
        
        button_frame = ttk.Frame(section)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        ttk.Button(button_frame, text="🔧 Reset Application", 
                   command=self.reset_application).pack(fill='x', pady=(0, 5), ipady=8)
        
        ttk.Button(button_frame, text="🗑️ Clear All Data", 
                   command=self.clear_all_data).pack(fill='x', pady=(0, 5), ipady=8)

    def _setup_about_section(self):
        """Setup about section"""
        section = self._create_section_frame(5, "ℹ️ About")
        
        about_text = (
            "Personal Finance Manager v1.0\n\n"
            "A simple and efficient application to manage your personal finances.\n"
            "Track expenses, income, and generate insightful reports.\n\n"
            f"© {datetime.now().year} All rights reserved."
        )
        
        ttk.Label(section, text=about_text.strip(), justify='left').grid(
            row=1, column=0, columnspan=2, sticky='w', pady=(5, 5))

    def update_setting(self, key, value):
        """Update a setting and save"""
        self.settings[key] = value
        self.save_settings()

    def get_database_stats(self):
        """Get database statistics"""
        try:
            transactions = self.transaction_service.get_total_count()
            categories = self.category_service.get_total_count()
            
            db_size = "Unknown"
            if os.path.exists(DB_URL):
                size_bytes = os.path.getsize(DB_URL)
                if size_bytes < 1024:
                    db_size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    db_size = f"{size_bytes / 1024:.2f} KB"
                else:
                    db_size = f"{size_bytes / (1024 * 1024):.2f} MB"
            
            return {
                "transactions": transactions,
                "categories": categories,
                "db_size": db_size
            }
        except Exception:
            return {
                "transactions": 0,
                "categories": 0,
                "db_size": "Unknown"
            }

    def backup_database(self):
        """Backup the database file"""
        try:
            if not os.path.exists(DB_URL):
                messagebox.showerror("Error", "Database file not found")
                return
            
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"finance_backup_{timestamp}.db"
            
            shutil.copy2(DB_URL, backup_path)
            messagebox.showinfo("Success", f"Database backed up successfully!\n\nLocation: {backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to backup database: {str(e)}")

    def export_transactions(self):
        """Export all transactions to CSV"""
        try:
            transactions = self.transaction_service.get_all()
            
            if not transactions:
                messagebox.showinfo("Info", "No transactions to export")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Type", "Amount", "Date", "Category", "Account", "Description", "Created At", "Updated At"])
                
                for trans in transactions:
                    writer.writerow([
                        trans['id'],
                        trans['type'],
                        trans['amount'],
                        trans['date'],
                        trans['category'],
                        trans['account'],
                        trans.get('description', ''),
                        trans['created_at'],
                        trans['updated_at']
                    ])
            
            messagebox.showinfo("Success", f"Exported {len(transactions)} transactions successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export transactions: {str(e)}")

    def export_categories(self):
        """Export all categories to CSV"""
        try:
            categories = self.category_service.get_all()
            
            if not categories:
                messagebox.showinfo("Info", "No categories to export")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"categories_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Type", "Budget", "Description", "Created At", "Updated At"])
                
                for cat in categories:
                    writer.writerow([
                        cat['id'],
                        cat['name'],
                        cat['type'],
                        cat.get('budget', ''),
                        cat.get('description', ''),
                        cat['created_at'],
                        cat['updated_at']
                    ])
            
            messagebox.showinfo("Success", f"Exported {len(categories)} categories successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export categories: {str(e)}")

    def import_data(self):
        """Import data from CSV (placeholder)"""
        messagebox.showinfo("Import", "Import functionality coming soon!\n\nThis will allow you to import transactions and categories from CSV files.")

    def reset_application(self):
        """Reset application settings"""
        if messagebox.askyesno("Confirm Reset", "This will reset all application settings to default.\n\nYour data will not be affected.\n\nContinue?"):
            try:
                if self.settings_file.exists():
                    self.settings_file.unlink()
                self.settings = self.load_settings()
                messagebox.showinfo("Success", "Settings reset successfully!\n\nPlease restart the application.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")

    def clear_all_data(self):
        """Clear all data from database"""
        if messagebox.askyesno("⚠️ WARNING", "This will permanently delete ALL transactions and categories!\n\nThis action CANNOT be undone!\n\nAre you absolutely sure?"):
            if messagebox.askyesno("⚠️ FINAL WARNING", "Last chance!\n\nDelete ALL data permanently?"):
                try:
                    with get_db_connection() as conn:
                        conn.execute("DELETE FROM transactions")
                        conn.execute("DELETE FROM categories")
                        conn.commit()
                    messagebox.showinfo("Success", "All data has been cleared")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to clear data: {str(e)}")
