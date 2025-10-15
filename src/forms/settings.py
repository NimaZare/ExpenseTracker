from tkinter import ttk


class SettingsPage:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_rowconfigure(0, weight=1)

        self.main_frame = ttk.Frame(parent_frame, padding="30")
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        ttk.Label(self.main_frame, text="Application Settings", style='H2.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 20))

        self._setup_settings_content()

    def _setup_settings_content(self):
        settings_container = ttk.Frame(self.main_frame, style='Card.TFrame', padding="20")
        settings_container.grid(row=1, column=0, sticky='new')
        settings_container.columnconfigure(0, weight=1)
        
        ttk.Label(settings_container, text="Appearance", style='H4.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        ttk.Label(settings_container, text="Currency Symbol:").grid(row=1, column=0, sticky='w', padx=(0, 10))
        
        currency_options = ttk.Combobox(settings_container, values=["$", "€", "£"], state="readonly")
        currency_options.set("$")
        currency_options.grid(row=2, column=0, sticky='w', pady=(0, 20))
        
        ttk.Label(settings_container, text="Data & Backup", style='H4.TLabel').grid(row=3, column=0, sticky='w', pady=(10, 10))
        
        ttk.Button(settings_container, text="Backup Data Now", command=self.backup_data).grid(row=4, column=0, sticky='w', pady=(0, 10), ipady=5)

        ttk.Button(settings_container, text="Export All Data (.csv)", command=self.export_data).grid(row=5, column=0, sticky='w', pady=(0, 10), ipady=5)

    def backup_data(self):
        print("Action: Backing up application data.")

    def export_data(self):
        print("Action: Exporting all data to CSV.")

