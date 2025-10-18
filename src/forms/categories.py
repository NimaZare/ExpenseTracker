import tkinter as tk
from tkinter import ttk, messagebox
from services.category import CategoryService


class CategoriesPage:
    def __init__(self, master):
        self.master = master
        self.category_service = CategoryService()
        self.selected_category_id = None
        
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

        self.cat_tree = ttk.Treeview(list_frame, columns=('id', 'name', 'type', 'budget'), show='tree headings', height=10)
        
        self.cat_tree.column('#0', width=0, stretch=False)
        self.cat_tree.column('id', width=0, stretch=False)
        self.cat_tree.column('name', width=150)
        self.cat_tree.column('type', width=100)
        self.cat_tree.column('budget', width=100)
        
        self.cat_tree.heading('id', text='')
        self.cat_tree.heading('name', text='Name')
        self.cat_tree.heading('type', text='Type')
        self.cat_tree.heading('budget', text='Budget')
        
        self.cat_tree.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.cat_tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns', pady=(0, 10))
        self.cat_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cat_tree.bind('<Button-3>', self.show_context_menu)
        self.cat_tree.bind('<<TreeviewSelect>>', self.on_category_select)
        self.cat_tree.bind('<Double-1>', self.edit_category)
        
        self.context_menu = tk.Menu(self.cat_tree, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_category)
        self.context_menu.add_command(label="Delete", command=self.delete_category)
        
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        ttk.Button(button_frame, text="🗑 Delete Selected", command=self.delete_category).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="✏ Edit Selected", command=self.edit_category).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🔄 Refresh", command=self.load_categories).pack(side='left', padx=5)

        self.add_frame = ttk.Frame(content_container, style='Card.TFrame', padding="15")
        self.add_frame.grid(row=0, column=1, sticky='nsew', padx=(15, 0))
        
        self.form_title = ttk.Label(self.add_frame, text="Add New Category", style='H4.TLabel')
        self.form_title.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(self.add_frame, text="Name*", style='H5.TLabel').pack(anchor='w', pady=(5, 2))
        self.name_entry = ttk.Entry(self.add_frame)
        self.name_entry.pack(fill='x', pady=(0, 10))
        
        ttk.Label(self.add_frame, text="Type*", style='H5.TLabel').pack(anchor='w', pady=(5, 2))
        self.type_combo = ttk.Combobox(self.add_frame, values=["Expense", "Income", "Transfer"], state="readonly")
        self.type_combo.pack(fill='x', pady=(0, 10))
        self.type_combo.set("Expense")
        
        ttk.Label(self.add_frame, text="Budget (Optional)", style='H5.TLabel').pack(anchor='w', pady=(5, 2))
        self.budget_entry = ttk.Entry(self.add_frame)
        self.budget_entry.pack(fill='x', pady=(0, 10))
        
        ttk.Label(self.add_frame, text="Description (Optional)", style='H5.TLabel').pack(anchor='w', pady=(5, 2))
        self.description_entry = ttk.Entry(self.add_frame)
        self.description_entry.pack(fill='x', pady=(0, 15))
        
        btn_frame = ttk.Frame(self.add_frame)
        btn_frame.pack(fill='x')
        
        self.save_button = ttk.Button(btn_frame, text="Add Category", style='Accent.TButton', command=self.save_category)
        self.save_button.pack(fill='x', ipady=8, pady=(0, 5))
        
        self.cancel_button = ttk.Button(btn_frame, text="Clear Form", command=self.clear_form)
        self.cancel_button.pack(fill='x', ipady=8)
        
        self.load_categories()

    def load_categories(self):
        """Load all categories from database"""
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)
        
        try:
            categories = self.category_service.get_all()
            categories.extend(self.category_service.get_default_categories())
            for cat in categories:
                budget = f"${cat.get('budget', 0)}" if cat.get('budget') else "N/A"
                self.cat_tree.insert('', 'end', values=(
                    cat['id'],
                    cat['name'],
                    cat['type'],
                    budget
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {str(e)}")

    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.cat_tree.selection()
        if selection:
            item = self.cat_tree.item(selection[0])
            values = item['values']
            if values:
                self.selected_category_id = values[0]

    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.cat_tree.identify_row(event.y)
        if item:
            self.cat_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def save_category(self):
        """Save or update category"""
        name = self.name_entry.get().strip()
        cat_type = self.type_combo.get()
        budget_str = self.budget_entry.get().strip()
        description = self.description_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Category name is required")
            return
        
        if not cat_type:
            messagebox.showerror("Error", "Category type is required")
            return
        
        budget = None
        if budget_str:
            try:
                budget = float(budget_str.replace('$', '').replace(',', ''))
                if budget < 0:
                    messagebox.showerror("Error", "Budget must be a positive number")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid budget amount")
                return
        
        try:
            if self.selected_category_id:
                result = self.category_service.update(
                    self.selected_category_id,
                    name=name,
                    type=cat_type,
                    budget=budget,
                    description=description
                )
                if result:
                    messagebox.showinfo("Success", "Category updated successfully!")
                else:
                    messagebox.showerror("Error", "Failed to update category")
            else:
                existing = self.category_service.get_by_name(name)
                if existing:
                    messagebox.showerror("Error", f"Category '{name}' already exists")
                    return
                
                result = self.category_service.create(
                    name=name,
                    type=cat_type,
                    budget=budget,
                    description=description
                )
                if result:
                    messagebox.showinfo("Success", "Category added successfully!")
                else:
                    messagebox.showerror("Error", "Failed to add category")
            
            self.load_categories()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def edit_category(self):
        """Load selected category into form for editing"""
        selection = self.cat_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to edit")
            return
        
        item = self.cat_tree.item(selection[0])
        values = item['values']
        
        try:
            category = self.category_service.get_by_id(values[0])
            if category:
                self.selected_category_id = category['id']
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, category['name'])
                self.type_combo.set(category['type'])
                
                self.budget_entry.delete(0, tk.END)
                if category.get('budget'):
                    self.budget_entry.insert(0, str(category['budget']))
                
                self.description_entry.delete(0, tk.END)
                if category.get('description'):
                    self.description_entry.insert(0, category['description'])
                
                self.form_title.config(text="Edit Category")
                self.save_button.config(text="Update Category")
            else:
                messagebox.showerror("Error", "Category not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load category: {str(e)}")

    def delete_category(self):
        """Delete selected category"""
        selection = self.cat_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to delete")
            return
        
        item = self.cat_tree.item(selection[0])
        values = item['values']
        category_name = values[1]

        if category_name in self.category_service.get_default_categories():
            messagebox.showwarning("Warning", "Default categories cannot be deleted")
            return
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{category_name}'?"):
            return
        
        try:
            if self.category_service.delete(values[0]):
                messagebox.showinfo("Success", "Category deleted successfully!")
                self.load_categories()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to delete category")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def clear_form(self):
        """Clear form and reset to add mode"""
        self.selected_category_id = None
        self.name_entry.delete(0, tk.END)
        self.type_combo.set("Expense")
        self.budget_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        
        self.form_title.config(text="Add New Category")
        self.save_button.config(text="Add Category")
        
        for item in self.cat_tree.selection():
            self.cat_tree.selection_remove(item)
