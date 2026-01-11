"""
Facebook Automation - ULTRA PROFESSIONAL GUI
Responsive design, live statistics, modern dark theme
"""
# import tkinter as tk
# from tkinter import ttk, scrolledtext, messagebox
import threading
import logging
import json
from datetime import datetime
from auto_messenger import FacebookAutoMessenger


class UltraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Facebook Automation PRO - Enterprise Edition")
        
        # Make window responsive
        self.root.state('zoomed')  # Start maximized
        self.root.minsize(1200, 700)  # Minimum size
        
        # Configure grid weights for responsive resize
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.automation = FacebookAutoMessenger()
        self.automation_thread = None
        
        # Ultra Modern Dark Theme
        self.colors = {
            'bg_dark': '#0D1117',
            'bg_darker': '#010409',
            'bg_card': '#161B22',
            'bg_sidebar': '#0D1117',
            'accent_blue': '#58A6FF',
            'accent_green': '#3FB950',
            'accent_purple': '#A371F7',
            'accent_orange': '#F85149',
            'accent_yellow': '#D29922',
            'text_white': '#C9D1D9',
            'text_gray': '#8B949E',
            'text_light': '#F0F6FC',
            'border': '#30363D',
            'success': '#3FB950',
            'warning': '#F85149',
            'error': '#F85149',
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        
        self._create_ui()
        self._setup_logging()
        self._start_stats_updater()  # Live updates!
    
    def _create_ui(self):
        # Main container with grid layout
#         main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=0, minsize=300)  # Sidebar fixed width
        main_container.grid_columnconfigure(1, weight=1)  # Content expands
        
        # LEFT SIDEBAR
        self._create_sidebar(main_container)
        
        # RIGHT CONTENT
        self._create_content(main_container)
    
    def _create_sidebar(self, parent):
#         sidebar = tk.Frame(parent, bg=self.colors['bg_sidebar'], width=300)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        
        # Logo/Header
#         header_frame = tk.Frame(sidebar, bg=self.colors['bg_darker'], height=140)
#         header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
#         tk.Label(
            header_frame,
            text="🚀",
            font=("Segoe UI", 48),
            bg=self.colors['bg_darker'],
            fg=self.colors['accent_blue']
        ).pack(pady=(25, 5))
        
#         tk.Label(
            header_frame,
            text="Facebook Automation",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['bg_darker'],
            fg=self.colors['text_white']
        ).pack()
        
#         tk.Label(
            header_frame,
            text="Professional Edition",
            font=("Segoe UI", 9),
            bg=self.colors['bg_darker'],
            fg=self.colors['accent_blue']
        ).pack(pady=(2, 15))
        
        # Menu Buttons with gradient colors
        menu_items = [
            ("🚀 AUTO MODUS", self._start_auto_mode, self.colors['accent_purple']),
            ("📝 Gruppenposting", self._start_group_posting, self.colors['accent_blue']),
            ("💬 Kommentieren", self._start_group_commenting, self.colors['accent_green']),
            ("📧 Nachrichten", self._start_messaging, self.colors['accent_blue']),
            ("👥 Freunde", self._start_add_friends, self.colors['accent_orange']),
            ("➕ GRUPPEN BEITRETEN", self._start_join_groups, self.colors['success']),
        ]
        
#         tk.Frame(sidebar, bg=self.colors['bg_sidebar'], height=20).pack()
        
        self.menu_buttons = []
        for text, command, color in menu_items:
#             btn_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
#             btn_frame.pack(fill=tk.X, padx=20, pady=6)
            
#             btn = tk.Button(
                btn_frame,
                text=text,
                command=command,
                font=("Segoe UI", 10, "bold"),
                bg=color,
                fg="white",
                activebackground=self._lighten_color(color),
                activeforeground="white",
#                 relief=tk.FLAT,
                cursor="hand2",
                anchor="w",
                padx=18,
                pady=14,
                bd=0
            )
#             btn.pack(fill=tk.X)
            self.menu_buttons.append(btn)
            
            # Hover
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=self._lighten_color(c)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
        
        # Stop Button
#         tk.Frame(sidebar, bg=self.colors['bg_sidebar'], height=15).pack()
        
#         stop_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
#         stop_frame.pack(fill=tk.X, padx=20, pady=10)
        
#         self.stop_btn = tk.Button(
            stop_frame,
            text="⬛ STOPPEN",
            command=self._stop_automation,
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['error'],
            fg="white",
            activebackground="#D32F2F",
#             relief=tk.FLAT,
            cursor="hand2",
            padx=18,
            pady=16,
            bd=0,
#             state=tk.DISABLED
        )
#         self.stop_btn.pack(fill=tk.X)
        
        # Status at bottom
#         status_frame = tk.Frame(sidebar, bg=self.colors['bg_darker'], height=70)
#         status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
#         tk.Label(
            status_frame,
            text="STATUS",
            font=("Segoe UI", 8),
            bg=self.colors['bg_darker'],
            fg=self.colors['text_gray']
        ).pack(pady=(12, 4))
        
#         self.status_indicator = tk.Label(
            status_frame,
            text="● BEREIT",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['bg_darker'],
            fg=self.colors['success']
        )
        self.status_indicator.pack(pady=(0, 12))
    
    def _create_content(self, parent):
#         content = tk.Frame(parent, bg=self.colors['bg_dark'])
        content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Configure grid for responsive layout
        content.grid_rowconfigure(0, weight=0)  # Stats - fixed height
        content.grid_rowconfigure(1, weight=0)  # Config - fixed height  
        content.grid_rowconfigure(2, weight=1)  # Log - expands
        content.grid_columnconfigure(0, weight=1)
        
        # Statistics Cards (LIVE UPDATES!)
        self._create_stats_section(content)
        
        # Configuration Panel
        self._create_config_panel(content)
        
        # Activity Log
        self._create_log_panel(content)
    
    def _create_stats_section(self, parent):
#         stats_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        stats_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 10))
        
#         tk.Label(
            stats_frame,
            text="📊 LIVE STATISTIKEN",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_white']
        ).pack(anchor="w", pady=(0, 12))
        
        # Stats cards container
#         cards_frame = tk.Frame(stats_frame, bg=self.colors['bg_dark'])
#         cards_frame.pack(fill=tk.X)
        
        # Create stat cards
        stat_items = [
            ("📝", "Beiträge", 'total_posts', self.colors['accent_blue']),
            ("💬", "Kommentare", 'total_comments', self.colors['accent_green']),
            ("📧", "Nachrichten", 'total_messages', self.colors['accent_purple']),
            ("👥", "Freunde", 'total_friend_requests', self.colors['accent_orange']),
            ("➕", "Gruppen Joined", 'total_groups_joined', self.colors['accent_yellow']),
        ]
        
        self.stat_labels = {}
        for icon, label, key, color in stat_items:
#             card = tk.Frame(cards_frame, bg=self.colors['bg_card'])
#             card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
            
#             tk.Label(
                card,
                text=icon,
                font=("Segoe UI", 28),
                bg=self.colors['bg_card'],
                fg=color
            ).pack(pady=(15, 5))
            
#             value_label = tk.Label(
                card,
                text="0",
                font=("Segoe UI", 24, "bold"),
                bg=self.colors['bg_card'],
                fg=color
            )
            value_label.pack()
            self.stat_labels[key] = value_label  # Store for live updates!
            
#             tk.Label(
                card,
                text=label,
                font=("Segoe UI", 9),
                bg=self.colors['bg_card'],
                fg=self.colors['text_gray']
            ).pack(pady=(0, 15))
    
    def _create_config_panel(self, parent):
#         config = tk.Frame(parent, bg=self.colors['bg_card'])
        config.grid(row=1, column=0, sticky="ew", padx=25, pady=10)
        
#         tk.Label(
            config,
            text="⚙️ KONFIGURATION",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['text_white']
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
#         settings = tk.Frame(config, bg=self.colors['bg_card'])
#         settings.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Cities
        self._create_setting(settings, "🌍 Städte", 
                            "Berlin,Stuttgart,München,Hamburg,Köln,Frankfurt", 0)
        self.cities_var = self._last_var
        
        # Group URL
        self._create_setting(settings, "🔗 Gruppen-URL",
                            "https://www.facebook.com/groups/werbungprofessional/", 1)
        self.group_var = self._last_var
        
        # Max values
#         max_frame = tk.Frame(settings, bg=self.colors['bg_card'])
        max_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)
        
        self._create_mini(max_frame, "📊 Max. Beiträge", "20", 0)
        self.max_posts_var = self._last_var
        
        self._create_mini(max_frame, "📧 Max. Nachrichten", "20", 1)
        self.max_messages_var = self._last_var
        
        self._create_mini(max_frame, "👥 Max. Freunde", "20", 2)
        self.max_friends_var = self._last_var
    
    def _create_log_panel(self, parent):
#         log_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        log_frame.grid(row=2, column=0, sticky="nsew", padx=25, pady=(10, 25))
        
        # Configure log_frame grid for expansion
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
#         tk.Label(
            log_frame,
            text="📋 AKTIVITÄTSPROTOKOLL (LIVE)",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['text_white']
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 8))
        
        # Log text with scrollbar
#         log_container = tk.Frame(log_frame, bg=self.colors['bg_darker'])
        log_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Configure log_container for text expansion
        log_container.grid_rowconfigure(0, weight=1)
        log_container.grid_columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_container,
#             wrap=tk.WORD,
            font=("Consolas", 9),
            bg=self.colors['bg_darker'],
            fg=self.colors['text_light'],
            insertbackground=self.colors['accent_blue'],
#             relief=tk.FLAT,
            padx=12,
            pady=12,
#             state=tk.DISABLED,
            selectbackground=self.colors['accent_blue'],
            selectforeground="white"
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    
    def _create_setting(self, parent, label_text, default, row):
#         tk.Label(
            parent,
            text=label_text,
            font=("Segoe UI", 9, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['text_gray']
        ).grid(row=row, column=0, sticky="w", pady=6)
        
#         var = tk.StringVar(value=default)
#         entry = tk.Entry(
            parent,
            textvariable=var,
            font=("Segoe UI", 9),
            bg=self.colors['bg_darker'],
            fg=self.colors['text_white'],
            insertbackground=self.colors['accent_blue'],
#             relief=tk.FLAT,
            width=70,
            bd=0
        )
        entry.grid(row=row, column=1, sticky="ew", padx=(12, 0), pady=6, ipady=6)
        
        parent.grid_columnconfigure(1, weight=1)  # Make entry expand
        self._last_var = var
    
    def _create_mini(self, parent, label_text, default, col):
#         frame = tk.Frame(parent, bg=self.colors['bg_card'])
#         frame.pack(side=tk.LEFT, padx=(0, 25))
        
#         tk.Label(
            frame,
            text=label_text,
            font=("Segoe UI", 8, "bold"),
            bg=self.colors['bg_card'],
            fg=self.colors['text_gray']
        ).pack(anchor="w", pady=(0, 4))
        
#         var = tk.StringVar(value=default)
#         entry = tk.Entry(
            frame,
            textvariable=var,
            font=("Segoe UI", 9),
            bg=self.colors['bg_darker'],
            fg=self.colors['text_white'],
            insertbackground=self.colors['accent_blue'],
#             relief=tk.FLAT,
            width=10,
            bd=0
        )
        entry.pack(ipady=5)
        
        self._last_var = var
    
    def _lighten_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 25)
        g = min(255, g + 25)
        b = min(255, b + 25)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _start_stats_updater(self):
        """Update statistics every 2 seconds - LIVE!"""
        def update_loop():
            try:
                # Read stats from file
                if hasattr(self.automation, 'stats_file'):
                    try:
                        with open(self.automation.stats_file, 'r') as f:
                            stats = json.load(f)
                            
                            # Update GUI labels
                            for key, label in self.stat_labels.items():
                                value = stats.get(key, 0)
                                label.config(text=str(value))
                    except:
                        pass
            except:
                pass
            
            # Schedule next update
            self.root.after(2000, update_loop)  # Every 2 seconds
        
        # Start the update loop
        update_loop()
    
    def _setup_logging(self):
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                def append():
#                     self.text_widget.configure(state=tk.NORMAL)
                    
                    # Color coding
                    if "✅" in msg:
                        color = "#3FB950"
                    elif "⚠️" in msg or "❌" in msg:
                        color = "#F85149"
                    elif "🔍" in msg or "📝" in msg:
                        color = "#58A6FF"
                    else:
                        color = "#C9D1D9"
                    
                    self.text_widget.tag_config("colored", foreground=color)
#                     self.text_widget.insert(tk.END, msg + '\n', "colored")
#                     self.text_widget.configure(state=tk.DISABLED)
#                     self.text_widget.see(tk.END)
                
                self.text_widget.after(0, append)
        
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
        logging.getLogger().addHandler(handler)
    
    def _disable_buttons(self):
        for btn in self.menu_buttons:
#             btn.config(state=tk.DISABLED)
#         self.stop_btn.config(state=tk.NORMAL)
        self.status_indicator.config(text="● LÄUFT", fg=self.colors['accent_blue'])
    
    def _enable_buttons(self):
        for btn in self.menu_buttons:
#             btn.config(state=tk.NORMAL)
#         self.stop_btn.config(state=tk.DISABLED)
        self.status_indicator.config(text="● BEREIT", fg=self.colors['success'])
    
    def _start_auto_mode(self):
        cities = [c.strip() for c in self.cities_var.get().split(',') if c.strip()]
        if not cities:
            messagebox.showerror("Fehler", "Bitte Städte eingeben!")
            return
        
        group_url = self.group_var.get().strip()
        if not group_url:
            messagebox.showerror("Fehler", "Bitte Gruppen-URL eingeben!")
            return
        
        result = messagebox.askyesno(
            "🚀 AUTO MODUS",
            "AUTO MODUS startet ALLES:\n\n✓ Gruppen posten\n✓ Kommentare\n✓ Likes/Reaktionen\n✓ Freunde\n✓ Nachrichten\n✓ Profile besuchen\n\nENDLOS bis gestoppt!\n\nFortfahren?"
        )
        
        if result:
            self._disable_buttons()
            self.automation_thread = threading.Thread(
                target=lambda: self._run_and_finish(self.automation.run_auto_mode, cities, group_url),
                daemon=True
            )
            self.automation_thread.start()
    
    def _start_group_posting(self):
        cities = [c.strip() for c in self.cities_var.get().split(',') if c.strip()]
        if cities:
            self._disable_buttons()
            self.automation_thread = threading.Thread(
                target=lambda: self._run_and_finish(
                    self.automation.run_group_posting, cities, int(self.max_posts_var.get() or 20)
                ),
                daemon=True
            )
            self.automation_thread.start()
    
    def _start_group_commenting(self):
        cities = [c.strip() for c in self.cities_var.get().split(',') if c.strip()]
        if cities:
            self._disable_buttons()
            self.automation_thread = threading.Thread(
                target=lambda: self._run_and_finish(
                    self.automation.run_group_commenting, cities, int(self.max_posts_var.get() or 20)
                ),
                daemon=True
            )
            self.automation_thread.start()
    
    def _start_messaging(self):
        group_url = self.group_var.get().strip()
        if group_url:
            self._disable_buttons()
            self.automation_thread = threading.Thread(
                target=lambda: self._run_and_finish(
                    self.automation.run_automation, int(self.max_messages_var.get() or 20), group_url
                ),
                daemon=True
            )
            self.automation_thread.start()
    
    def _start_add_friends(self):
        group_url = self.group_var.get().strip()
        if group_url:
            self._disable_buttons()
            self.automation_thread = threading.Thread(
                target=lambda: self._run_and_finish(
                    self.automation.run_add_friends, int(self.max_friends_var.get() or 20), group_url
                ),
                daemon=True
            )
            self.automation_thread.start()
    
    def _start_join_groups(self):
        cities = [c.strip() for c in self.cities_var.get().split(',') if c.strip()]
        if cities:
            result = messagebox.askyesno(
                "➕ GRUPPEN BEITRETEN",
                "Automatisch Gruppen beitreten!\n\nENDLOS bis gestoppt.\n\nFortfahren?"
            )
            
            if result:
                self._disable_buttons()
                self.automation_thread = threading.Thread(
                    target=lambda: self._run_and_finish(self.automation.run_join_groups, cities),
                    daemon=True
                )
                self.automation_thread.start()
    
    def _run_and_finish(self, func, *args):
        try:
            func(*args)
        except Exception as e:
            logging.error(f"Fehler: {e}")
        finally:
            self.root.after(0, self._automation_finished)
    
    def _stop_automation(self):
        self.automation.stop()
        self.status_indicator.config(text="● WIRD GESTOPPT...", fg=self.colors['warning'])
    
    def _automation_finished(self):
        self._enable_buttons()
        messagebox.showinfo("✅ Abgeschlossen", "Automatisierung abgeschlossen!")
    
    def on_closing(self):
        if self.automation.is_running:
            if messagebox.askokcancel("Beenden", "Automatisierung läuft. Stoppen?"):
                self.automation.stop()
                self.automation.cleanup()
                self.root.destroy()
        else:
            self.automation.cleanup()
            self.root.destroy()


def main():
#     root = tk.Tk()
    app = UltraGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
