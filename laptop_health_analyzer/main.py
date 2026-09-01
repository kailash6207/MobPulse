# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import threading
import time
import os
import math
import subprocess
from datetime import datetime

from config import load_settings, save_settings
from analyzer import LaptopHealthAnalyzer

# Set default CustomTkinter appearance
cfg = load_settings()
ctk.set_appearance_mode(cfg.get("appearance_mode", "Dark"))
ctk.set_default_color_theme(cfg.get("color_theme", "blue"))

class LaptopHealthApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Laptop Health Suite Pro — Ultimate Edition")
        self.geometry("1120x760")
        self.minsize(980, 680)
        
        self.analyzer = LaptopHealthAnalyzer()
        self.settings = load_settings()
        
        # Telemetry State Cache
        self.telemetry = {
            "battery": {},
            "storage": [],
            "temp": {},
            "ram": {},
            "cpu": {},
            "ping": {},
            "health_score": {"score": 100, "grade": "A+", "rating": "Checking...", "color": "#00E676"},
            "alerts": []
        }
        
        self.running = True
        self.is_paused = False
        self.active_tab = "dashboard"
        
        # Graph metric toggles
        self.graph_show_cpu = tk.BooleanVar(value=True)
        self.graph_show_ram = tk.BooleanVar(value=True)
        self.graph_show_bat = tk.BooleanVar(value=True)
        self.graph_show_temp = tk.BooleanVar(value=False)
        self.graph_show_ping = tk.BooleanVar(value=False)
        
        self._build_ui()
        
        # Start background polling thread
        self.monitor_thread = threading.Thread(target=self._background_poll_loop, daemon=True)
        self.monitor_thread.start()
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ==========================================
        # 1. SIDEBAR NAVIGATION
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=230, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="⚡ LAP_HEALTH", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 2))
        
        self.sublogo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="PRO SUITE • v2.0 ULTIMATE", 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#00E5FF"
        )
        self.sublogo_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("hardware", "💻  Hardware & RAM"),
            ("battery", "🔋  Battery Lab"),
            ("storage", "🗄️  Storage & Cleaner"),
            ("network", "🌐  Network Radar"),
            ("analytics", "📈  Analytics & Stress"),
            ("settings", "⚙️  Settings & Reports")
        ]
        
        for idx, (tab_key, text) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                anchor="w",
                height=38,
                corner_radius=8,
                font=ctk.CTkFont(size=13, weight="normal"),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray25"),
                command=lambda k=tab_key: self._select_tab(k)
            )
            btn.grid(row=idx + 2, column=0, padx=12, pady=4, sticky="ew")
            self.nav_buttons[tab_key] = btn
            
        self.btn_sidebar_turbo = ctk.CTkButton(
            self.sidebar_frame,
            text="⚡ Turbo RAM Purge",
            height=34,
            corner_radius=8,
            fg_color="#7C4DFF",
            hover_color="#651FFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._trigger_turbo_ram
        )
        self.btn_sidebar_turbo.grid(row=9, column=0, padx=12, pady=(10, 8), sticky="ew")

        self.footer_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.footer_frame.grid(row=10, column=0, padx=12, pady=(0, 15), sticky="ew")
        
        self.lbl_live_status = ctk.CTkLabel(
            self.footer_frame,
            text="● LIVE MONITOR (3s)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#00E676"
        )
        self.lbl_live_status.pack(side="left")
        
        self.btn_pause = ctk.CTkButton(
            self.footer_frame,
            text="Pause",
            width=50,
            height=22,
            font=ctk.CTkFont(size=10),
            fg_color=("gray75", "gray30"),
            command=self._toggle_pause
        )
        self.btn_pause.pack(side="right")

        # ==========================================
        # 2. MAIN CONTENT CONTAINER & TABS
        # ==========================================
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)
        
        self.tabs = {}
        self._init_dashboard_tab()
        self._init_hardware_tab()
        self._init_battery_tab()
        self._init_storage_tab()
        self._init_network_tab()
        self._init_analytics_tab()
        self._init_settings_tab()
        
        self._select_tab("dashboard")

    def _select_tab(self, tab_key):
        self.active_tab = tab_key
        for k, btn in self.nav_buttons.items():
            if k == tab_key:
                btn.configure(fg_color=("gray75", "gray25"), font=ctk.CTkFont(size=13, weight="bold"))
            else:
                btn.configure(fg_color="transparent", font=ctk.CTkFont(size=13, weight="normal"))
                
        for k, frame in self.tabs.items():
            if k == tab_key:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()

    # =========================================================================
    # TAB 1: DASHBOARD (OVERVIEW & HEALTH GAUGE)
    # =========================================================================
    def _init_dashboard_tab(self):
        tab = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.tabs["dashboard"] = tab
        
        score_card = ctk.CTkFrame(tab, corner_radius=12, border_width=1, border_color=("gray80", "gray25"))
        score_card.pack(fill="x", pady=(0, 15))
        score_card.grid_columnconfigure(1, weight=1)
        
        self.canvas_score = tk.Canvas(score_card, width=170, height=170, bg="#1E222B" if ctk.get_appearance_mode()=="Dark" else "#F0F2F5", highlightthickness=0)
        self.canvas_score.grid(row=0, column=0, padx=15, pady=15)
        
        details_frame = ctk.CTkFrame(score_card, fg_color="transparent")
        details_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
        
        self.lbl_dash_rating = ctk.CTkLabel(
            details_frame, 
            text="Calculating System Vitals...", 
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        self.lbl_dash_rating.pack(fill="x")
        
        self.lbl_dash_summary = ctk.CTkLabel(
            details_frame,
            text="Host: Analyzing... | OS: Windows | Uptime: Fetching...",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70"),
            anchor="w"
        )
        self.lbl_dash_summary.pack(fill="x", pady=(2, 10))
        
        badges_row = ctk.CTkFrame(details_frame, fg_color="transparent")
        badges_row.pack(fill="x", pady=(0, 5))
        
        self.badge_bat = ctk.CTkLabel(badges_row, text="🔋 Battery: --%", font=ctk.CTkFont(size=11, weight="bold"), fg_color=("gray85", "gray20"), corner_radius=6, padx=8, pady=4)
        self.badge_bat.pack(side="left", padx=(0, 8))
        
        self.badge_temp = ctk.CTkLabel(badges_row, text="🌡️ CPU: --°C", font=ctk.CTkFont(size=11, weight="bold"), fg_color=("gray85", "gray20"), corner_radius=6, padx=8, pady=4)
        self.badge_temp.pack(side="left", padx=(0, 8))
        
        self.badge_net = ctk.CTkLabel(badges_row, text="🌐 Ping: -- ms", font=ctk.CTkFont(size=11, weight="bold"), fg_color=("gray85", "gray20"), corner_radius=6, padx=8, pady=4)
        self.badge_net.pack(side="left")

        vitals_grid = ctk.CTkFrame(tab, fg_color="transparent")
        vitals_grid.pack(fill="x", pady=(0, 15))
        vitals_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Card A: CPU Load
        c_cpu = ctk.CTkFrame(vitals_grid, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        c_cpu.grid(row=0, column=0, padx=(0, 8), sticky="nsew", ipady=6)
        ctk.CTkLabel(c_cpu, text="💻 PROCESSOR (CPU)", font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray40", "gray60")).pack(anchor="w", padx=12, pady=(10, 2))
        self.lbl_dash_cpu_val = ctk.CTkLabel(c_cpu, text="--%", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_dash_cpu_val.pack(anchor="w", padx=12)
        self.bar_dash_cpu = ctk.CTkProgressBar(c_cpu, height=8, progress_color="#00E5FF")
        self.bar_dash_cpu.pack(fill="x", padx=12, pady=(8, 4))
        self.bar_dash_cpu.set(0)
        self.lbl_dash_cpu_sub = ctk.CTkLabel(c_cpu, text="-- GHz | -- Cores", font=ctk.CTkFont(size=10), text_color=("gray40", "gray60"))
        self.lbl_dash_cpu_sub.pack(anchor="w", padx=12, pady=(0, 8))

        # Card B: Memory (RAM)
        c_ram = ctk.CTkFrame(vitals_grid, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        c_ram.grid(row=0, column=1, padx=(0, 8), sticky="nsew", ipady=6)
        ctk.CTkLabel(c_ram, text="🧠 MEMORY (RAM)", font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray40", "gray60")).pack(anchor="w", padx=12, pady=(10, 2))
        self.lbl_dash_ram_val = ctk.CTkLabel(c_ram, text="--%", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_dash_ram_val.pack(anchor="w", padx=12)
        self.bar_dash_ram = ctk.CTkProgressBar(c_ram, height=8, progress_color="#7C4DFF")
        self.bar_dash_ram.pack(fill="x", padx=12, pady=(8, 4))
        self.bar_dash_ram.set(0)
        self.lbl_dash_ram_sub = ctk.CTkLabel(c_ram, text="-- / -- GB Used", font=ctk.CTkFont(size=10), text_color=("gray40", "gray60"))
        self.lbl_dash_ram_sub.pack(anchor="w", padx=12, pady=(0, 8))

        # Card C: Battery & Power
        c_bat = ctk.CTkFrame(vitals_grid, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        c_bat.grid(row=0, column=2, padx=(0, 8), sticky="nsew", ipady=6)
        ctk.CTkLabel(c_bat, text="🔋 BATTERY CHARGE", font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray40", "gray60")).pack(anchor="w", padx=12, pady=(10, 2))
        self.lbl_dash_bat_val = ctk.CTkLabel(c_bat, text="--%", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_dash_bat_val.pack(anchor="w", padx=12)
        self.bar_dash_bat = ctk.CTkProgressBar(c_bat, height=8, progress_color="#00E676")
        self.bar_dash_bat.pack(fill="x", padx=12, pady=(8, 4))
        self.bar_dash_bat.set(0)
        self.lbl_dash_bat_sub = ctk.CTkLabel(c_bat, text="Health: --%", font=ctk.CTkFont(size=10), text_color=("gray40", "gray60"))
        self.lbl_dash_bat_sub.pack(anchor="w", padx=12, pady=(0, 8))

        # Card D: Primary Storage
        c_disk = ctk.CTkFrame(vitals_grid, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        c_disk.grid(row=0, column=3, sticky="nsew", ipady=6)
        ctk.CTkLabel(c_disk, text="🗄️ STORAGE (C:)", font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray40", "gray60")).pack(anchor="w", padx=12, pady=(10, 2))
        self.lbl_dash_disk_val = ctk.CTkLabel(c_disk, text="--%", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_dash_disk_val.pack(anchor="w", padx=12)
        self.bar_dash_disk = ctk.CTkProgressBar(c_disk, height=8, progress_color="#FF9100")
        self.bar_dash_disk.pack(fill="x", padx=12, pady=(8, 4))
        self.bar_dash_disk.set(0)
        self.lbl_dash_disk_sub = ctk.CTkLabel(c_disk, text="-- GB Free", font=ctk.CTkFont(size=10), text_color=("gray40", "gray60"))
        self.lbl_dash_disk_sub.pack(anchor="w", padx=12, pady=(0, 8))

        alerts_header = ctk.CTkLabel(tab, text="📋 LIVE SYSTEM ADVISORY & PREDICTIVE DIAGNOSTICS", font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
        alerts_header.pack(fill="x", pady=(5, 8))
        
        self.alerts_frame = ctk.CTkFrame(tab, corner_radius=10, fg_color="transparent")
        self.alerts_frame.pack(fill="x")

    def _draw_score_gauge(self, score, grade, color):
        self.canvas_score.delete("all")
        bg_c = "#1C222D" if ctk.get_appearance_mode() == "Dark" else "#F0F2F5"
        self.canvas_score.configure(bg=bg_c)
        
        cx, cy, r = 85, 85, 62
        start_angle = 135
        total_extent = 270
        progress_extent = -(total_extent * (score / 100.0))
        
        self.canvas_score.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=start_angle, extent=-total_extent,
            style="arc", outline="#2A3241" if ctk.get_appearance_mode()=="Dark" else "#D0D7DE",
            width=12
        )
        
        self.canvas_score.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=start_angle, extent=progress_extent,
            style="arc", outline=color,
            width=12
        )
        
        self.canvas_score.create_text(
            cx, cy - 8,
            text=f"{score}",
            font=("Segoe UI", 26, "bold"),
            fill="#FFFFFF" if ctk.get_appearance_mode()=="Dark" else "#1F2328"
        )
        
        self.canvas_score.create_text(
            cx, cy + 18,
            text=f"GRADE {grade}",
            font=("Segoe UI", 9, "bold"),
            fill=color
        )
        
        self.canvas_score.create_text(
            cx, cy + 32,
            text="HEALTH INDEX",
            font=("Segoe UI", 7),
            fill="#8B949E"
        )

    # =========================================================================
    # TAB 2: HARDWARE HUB & PROCESS MANAGER
    # =========================================================================
    def _init_hardware_tab(self):
        tab = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.tabs["hardware"] = tab
        
        specs_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        specs_card.pack(fill="x", pady=(0, 15), padx=2)
        
        ctk.CTkLabel(specs_card, text="💻 SYSTEM SPECIFICATIONS & CORE HARDWARE", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))
        
        self.specs_grid = ctk.CTkFrame(specs_card, fg_color="transparent")
        self.specs_grid.pack(fill="x", padx=15, pady=(0, 15))
        self.specs_grid.grid_columnconfigure((0, 1), weight=1)
        
        self.lbl_spec_cpu = ctk.CTkLabel(self.specs_grid, text="Processor: Fetching...", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_spec_cpu.grid(row=0, column=0, sticky="w", pady=3)
        
        self.lbl_spec_gpu = ctk.CTkLabel(self.specs_grid, text="Graphics: Fetching...", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_spec_gpu.grid(row=0, column=1, sticky="w", pady=3)
        
        self.lbl_spec_ram = ctk.CTkLabel(self.specs_grid, text="Installed RAM: Fetching...", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_spec_ram.grid(row=1, column=0, sticky="w", pady=3)
        
        self.lbl_spec_disk = ctk.CTkLabel(self.specs_grid, text="Primary Drive: Fetching...", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_spec_disk.grid(row=1, column=1, sticky="w", pady=3)
        
        self.lbl_spec_os = ctk.CTkLabel(self.specs_grid, text="OS Build: Fetching...", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_spec_os.grid(row=2, column=0, sticky="w", pady=3)
        
        self.lbl_spec_uptime = ctk.CTkLabel(self.specs_grid, text="System Uptime: Fetching...", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_spec_uptime.grid(row=2, column=1, sticky="w", pady=3)

        cores_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        cores_card.pack(fill="x", pady=(0, 15), padx=2)
        
        ctk.CTkLabel(cores_card, text="⚡ MULTI-CORE PROCESSOR UTILIZATION MATRIX", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))
        
        self.cores_bars_frame = ctk.CTkFrame(cores_card, fg_color="transparent")
        self.cores_bars_frame.pack(fill="x", padx=15, pady=(0, 15))
        self.core_widgets = []

        proc_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        proc_card.pack(fill="x", pady=(0, 15), padx=2)
        
        proc_top = ctk.CTkFrame(proc_card, fg_color="transparent")
        proc_top.pack(fill="x", padx=15, pady=(12, 8))
        
        ctk.CTkLabel(proc_top, text="🧠 ACTIVE PROCESSES & MEMORY CONSUMERS", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        
        btn_turbo = ctk.CTkButton(
            proc_top, 
            text="⚡ Turbo RAM Purge", 
            width=140, 
            height=30,
            fg_color="#7C4DFF", 
            hover_color="#651FFF", 
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._trigger_turbo_ram
        )
        btn_turbo.pack(side="right")

        filter_row = ctk.CTkFrame(proc_card, fg_color="transparent")
        filter_row.pack(fill="x", padx=15, pady=(0, 8))
        
        self.entry_proc_search = ctk.CTkEntry(filter_row, placeholder_text="Filter process by name or PID...", height=30)
        self.entry_proc_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_proc_search.bind("<KeyRelease>", lambda e: self._refresh_process_table())
        
        btn_kill = ctk.CTkButton(
            filter_row, 
            text="Terminate Selected", 
            width=130, 
            height=30, 
            fg_color="#FF5252", 
            hover_color="#D50000",
            command=self._kill_selected_process
        )
        btn_kill.pack(side="right")

        tree_frame = ctk.CTkFrame(proc_card, fg_color="transparent")
        tree_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Proc.Treeview",
            background="#1E222B" if ctk.get_appearance_mode()=="Dark" else "#FFFFFF",
            foreground="#FFFFFF" if ctk.get_appearance_mode()=="Dark" else "#1F2328",
            fieldbackground="#1E222B" if ctk.get_appearance_mode()=="Dark" else "#FFFFFF",
            rowheight=26,
            font=("Segoe UI", 10)
        )
        style.configure("Proc.Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#2A3241", foreground="#FFFFFF")
        
        self.tree_proc = ttk.Treeview(tree_frame, columns=("pid", "name", "mem", "cpu", "user"), show="headings", height=8, style="Proc.Treeview")
        self.tree_proc.heading("pid", text="PID")
        self.tree_proc.heading("name", text="Application / Process Name")
        self.tree_proc.heading("mem", text="Memory (RAM MB)")
        self.tree_proc.heading("cpu", text="CPU Load")
        self.tree_proc.heading("user", text="User Account")
        
        self.tree_proc.column("pid", width=70, anchor="center")
        self.tree_proc.column("name", width=250, anchor="w")
        self.tree_proc.column("mem", width=130, anchor="center")
        self.tree_proc.column("cpu", width=90, anchor="center")
        self.tree_proc.column("user", width=120, anchor="center")
        
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_proc.yview)
        self.tree_proc.configure(yscrollcommand=scroll.set)
        
        self.tree_proc.pack(side="left", fill="x", expand=True)
        scroll.pack(side="right", fill="y")

    # =========================================================================
    # TAB 3: BATTERY LAB & WEAR ANALYSIS
    # =========================================================================
    def _init_battery_tab(self):
        tab = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.tabs["battery"] = tab
        
        top_grid = ctk.CTkFrame(tab, fg_color="transparent")
        top_grid.pack(fill="x", pady=(0, 15))
        top_grid.grid_columnconfigure((0, 1), weight=1)
        
        c_deg = ctk.CTkFrame(top_grid, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        c_deg.grid(row=0, column=0, padx=(0, 8), sticky="nsew", ipady=8)
        
        ctk.CTkLabel(c_deg, text="🔋 BATTERY CAPACITY & WEAR INDEX", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 6))
        
        self.lbl_bat_wear_status = ctk.CTkLabel(c_deg, text="Health Index: Fetching...", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00E676")
        self.lbl_bat_wear_status.pack(anchor="w", padx=15, pady=(0, 6))
        
        self.lbl_bat_design_cap = ctk.CTkLabel(c_deg, text="• Factory Design Capacity: Fetching...", font=ctk.CTkFont(size=12))
        self.lbl_bat_design_cap.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_bat_full_cap = ctk.CTkLabel(c_deg, text="• Full Charge Max Capacity: Fetching...", font=ctk.CTkFont(size=12))
        self.lbl_bat_full_cap.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_bat_wear_pct = ctk.CTkLabel(c_deg, text="• Total Wear Degradation: Fetching...", font=ctk.CTkFont(size=12))
        self.lbl_bat_wear_pct.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_bat_cycle_count = ctk.CTkLabel(c_deg, text="• Lifetime Charge Cycles: Fetching...", font=ctk.CTkFont(size=12))
        self.lbl_bat_cycle_count.pack(anchor="w", padx=15, pady=2)

        c_live = ctk.CTkFrame(top_grid, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        c_live.grid(row=0, column=1, sticky="nsew", ipady=8)
        
        ctk.CTkLabel(c_live, text="⚡ LIVE DISCHARGE & RUNTIME ESTIMATE", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 6))
        
        self.lbl_bat_current_pct = ctk.CTkLabel(c_live, text="Current Level: --%", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_bat_current_pct.pack(anchor="w", padx=15, pady=(0, 6))
        
        self.lbl_bat_plugged = ctk.CTkLabel(c_live, text="• Power Connection: Fetching...", font=ctk.CTkFont(size=12))
        self.lbl_bat_plugged.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_bat_runtime = ctk.CTkLabel(c_live, text="• Estimated Battery Life: Calculating...", font=ctk.CTkFont(size=12))
        self.lbl_bat_runtime.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_bat_chemistry = ctk.CTkLabel(c_live, text="• Cell Chemistry: Li-Ion", font=ctk.CTkFont(size=12))
        self.lbl_bat_chemistry.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_bat_mfg = ctk.CTkLabel(c_live, text="• Battery Manufacturer: OEM Factory", font=ctk.CTkFont(size=12))
        self.lbl_bat_mfg.pack(anchor="w", padx=15, pady=2)

        plan_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        plan_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(plan_card, text="⚙️ WINDOWS POWER PROFILE SWITCHER", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))
        
        plan_btn_frame = ctk.CTkFrame(plan_card, fg_color="transparent")
        plan_btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        plan_btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        plans = [
            ("balanced", "⚖️ Balanced", "#4A90E2"),
            ("high_performance", "🚀 High Performance", "#FF9100"),
            ("power_saver", "🍃 Power Saver", "#00E676"),
            ("ultimate", "⚡ Ultimate Power", "#7C4DFF")
        ]
        
        for idx, (p_key, p_lbl, p_col) in enumerate(plans):
            btn = ctk.CTkButton(
                plan_btn_frame,
                text=p_lbl,
                height=36,
                fg_color=("gray80", "gray20"),
                hover_color=p_col,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda k=p_key: self._switch_power_plan(k)
            )
            btn.grid(row=0, column=idx, padx=4, sticky="ew")

        tips_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        tips_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(tips_card, text="💡 SMART BATTERY HEALTH ADVISORY", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 6))
        tips_text = (
            "• 80% Charge Limit: To double your battery's lifespan, avoid keeping your laptop at 100% plugged in 24/7.\n"
            "• Thermal Protection: Lithium-ion cells degrade rapidly when operated above 35°C ambient or during high CPU thermal spikes.\n"
            "• Shallow Discharge: Recharge when your laptop hits 20% to prevent deep cycle voltage degradation."
        )
        ctk.CTkLabel(tips_card, text=tips_text, font=ctk.CTkFont(size=12), justify="left", anchor="w", text_color=("gray40", "gray70")).pack(anchor="w", padx=15, pady=(0, 12))

    # =========================================================================
    # TAB 4: STORAGE & JUNK CLEANER
    # =========================================================================
    def _init_storage_tab(self):
        tab = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.tabs["storage"] = tab
        
        self.storage_drives_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.storage_drives_frame.pack(fill="x", pady=(0, 15))
        
        bench_row = ctk.CTkFrame(tab, fg_color="transparent")
        bench_row.pack(fill="x", pady=(0, 15))
        bench_row.grid_columnconfigure((0, 1), weight=1)
        
        io_card = ctk.CTkFrame(bench_row, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        io_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew", ipady=8)
        
        ctk.CTkLabel(io_card, text="📈 REAL-TIME DISK THROUGHPUT", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 6))
        self.lbl_disk_read_speed = ctk.CTkLabel(io_card, text="Read Speed: 0.0 MB/s", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00E5FF")
        self.lbl_disk_read_speed.pack(anchor="w", padx=15, pady=2)
        self.lbl_disk_write_speed = ctk.CTkLabel(io_card, text="Write Speed: 0.0 MB/s", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FF9100")
        self.lbl_disk_write_speed.pack(anchor="w", padx=15, pady=2)

        speed_card = ctk.CTkFrame(bench_row, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        speed_card.grid(row=0, column=1, sticky="nsew", ipady=8)
        
        ctk.CTkLabel(speed_card, text="⚡ QUICK SSD SPEED BENCHMARK", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 6))
        
        self.lbl_bench_res = ctk.CTkLabel(speed_card, text="Status: Ready to test sequential speed", font=ctk.CTkFont(size=12), text_color=("gray40", "gray70"))
        self.lbl_bench_res.pack(anchor="w", padx=15, pady=2)
        
        self.btn_run_bench = ctk.CTkButton(
            speed_card,
            text="🚀 Run SSD Speed Test (32MB)",
            height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._run_disk_benchmark
        )
        self.btn_run_bench.pack(anchor="w", padx=15, pady=(6, 8))

        clean_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        clean_card.pack(fill="x", pady=(0, 10))
        
        clean_top = ctk.CTkFrame(clean_card, fg_color="transparent")
        clean_top.pack(fill="x", padx=15, pady=(12, 6))
        ctk.CTkLabel(clean_top, text="🧹 SMART JUNK & TEMP CLEANER", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        
        self.lbl_junk_status = ctk.CTkLabel(clean_card, text="Click 'Scan Temporary Junk' to calculate cleanable storage.", font=ctk.CTkFont(size=12), text_color=("gray40", "gray70"))
        self.lbl_junk_status.pack(anchor="w", padx=15, pady=(0, 8))
        
        btn_clean_row = ctk.CTkFrame(clean_card, fg_color="transparent")
        btn_clean_row.pack(fill="x", padx=15, pady=(0, 15))
        
        self.btn_scan_junk = ctk.CTkButton(btn_clean_row, text="🔍 Scan Junk Files", width=140, height=32, command=self._scan_junk)
        self.btn_scan_junk.pack(side="left", padx=(0, 10))
        
        self.btn_clean_junk = ctk.CTkButton(btn_clean_row, text="🧹 Clean Junk Files Now", width=160, height=32, fg_color="#00E676", hover_color="#00C853", text_color="#000000", font=ctk.CTkFont(weight="bold"), command=self._clean_junk)
        self.btn_clean_junk.pack(side="left")

    # =========================================================================
    # TAB 5: NETWORK & WI-FI RADAR
    # =========================================================================
    def _init_network_tab(self):
        tab = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.tabs["network"] = tab
        
        net_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        net_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(net_card, text="🌐 NETWORK LATENCY & JITTER STABILITY RADAR", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))
        
        net_grid = ctk.CTkFrame(net_card, fg_color="transparent")
        net_grid.pack(fill="x", padx=15, pady=(0, 15))
        net_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        m1 = ctk.CTkFrame(net_grid, fg_color=("gray85", "gray20"), corner_radius=8)
        m1.grid(row=0, column=0, padx=(0, 6), sticky="nsew", ipady=8)
        ctk.CTkLabel(m1, text="PING LATENCY", font=ctk.CTkFont(size=10, weight="bold"), text_color=("gray40", "gray60")).pack()
        self.lbl_net_ping = ctk.CTkLabel(m1, text="-- ms", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00E5FF")
        self.lbl_net_ping.pack()

        m2 = ctk.CTkFrame(net_grid, fg_color=("gray85", "gray20"), corner_radius=8)
        m2.grid(row=0, column=1, padx=(0, 6), sticky="nsew", ipady=8)
        ctk.CTkLabel(m2, text="JITTER VARIATION", font=ctk.CTkFont(size=10, weight="bold"), text_color=("gray40", "gray60")).pack()
        self.lbl_net_jitter = ctk.CTkLabel(m2, text="-- ms", font=ctk.CTkFont(size=20, weight="bold"), text_color="#7C4DFF")
        self.lbl_net_jitter.pack()

        m3 = ctk.CTkFrame(net_grid, fg_color=("gray85", "gray20"), corner_radius=8)
        m3.grid(row=0, column=2, sticky="nsew", ipady=8)
        ctk.CTkLabel(m3, text="CONNECTION LINK", font=ctk.CTkFont(size=10, weight="bold"), text_color=("gray40", "gray60")).pack()
        self.lbl_net_link_state = ctk.CTkLabel(m3, text="Online", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00E676")
        self.lbl_net_link_state.pack()

        wifi_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        wifi_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(wifi_card, text="📡 WI-FI ADAPTER & LIVE BANDWIDTH SPEEDS", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))
        
        self.lbl_wifi_ssid = ctk.CTkLabel(wifi_card, text="• Connected Network: Fetching...", font=ctk.CTkFont(size=12))
        self.lbl_wifi_ssid.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_wifi_sig = ctk.CTkLabel(wifi_card, text="• Signal Quality: Fetching...", font=ctk.CTkFont(size=12))
        self.lbl_wifi_sig.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_wifi_rates = ctk.CTkLabel(wifi_card, text="• Link Transmission Speed: Fetching...", font=ctk.CTkFont(size=12))
        self.lbl_wifi_rates.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_net_bandwidth = ctk.CTkLabel(wifi_card, text="• Live Speed: ↓ 0.0 KB/s  |  ↑ 0.0 KB/s", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00E5FF")
        self.lbl_net_bandwidth.pack(anchor="w", padx=15, pady=(2, 12))

        tools_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        tools_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(tools_card, text="🛠️ NETWORK DIAGNOSTIC & RECOVERY TOOLKIT", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))
        
        net_btn_row = ctk.CTkFrame(tools_card, fg_color="transparent")
        net_btn_row.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(net_btn_row, text="🌐 Flush DNS Cache", width=140, height=32, command=self._run_dns_flush).pack(side="left", padx=(0, 8))
        ctk.CTkButton(net_btn_row, text="🔄 Renew IP / DHCP", width=140, height=32, command=self._run_ip_renew).pack(side="left", padx=(0, 8))
        ctk.CTkButton(net_btn_row, text="📋 Open Task Manager", width=150, height=32, fg_color=("gray75", "gray30"), command=lambda: os.system("start taskmgr")).pack(side="left")

    # =========================================================================
    # TAB 6: LIVE ANALYTICS & STRESS TEST
    # =========================================================================
    def _init_analytics_tab(self):
        tab = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.tabs["analytics"] = tab
        
        graph_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        graph_card.pack(fill="x", pady=(0, 15))
        
        g_top = ctk.CTkFrame(graph_card, fg_color="transparent")
        g_top.pack(fill="x", padx=15, pady=(12, 6))
        
        ctk.CTkLabel(g_top, text="📈 REAL-TIME HARDWARE METRICS WAVEFORM", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        
        toggles_frame = ctk.CTkFrame(graph_card, fg_color="transparent")
        toggles_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        ctk.CTkCheckBox(toggles_frame, text="CPU Load (%)", variable=self.graph_show_cpu, text_color="#00E5FF", fg_color="#00E5FF", command=self._redraw_analytics_graph).pack(side="left", padx=(0, 12))
        ctk.CTkCheckBox(toggles_frame, text="RAM Alloc (%)", variable=self.graph_show_ram, text_color="#7C4DFF", fg_color="#7C4DFF", command=self._redraw_analytics_graph).pack(side="left", padx=(0, 12))
        ctk.CTkCheckBox(toggles_frame, text="Battery (%)", variable=self.graph_show_bat, text_color="#00E676", fg_color="#00E676", command=self._redraw_analytics_graph).pack(side="left", padx=(0, 12))
        ctk.CTkCheckBox(toggles_frame, text="Temp (°C)", variable=self.graph_show_temp, text_color="#FF5252", fg_color="#FF5252", command=self._redraw_analytics_graph).pack(side="left", padx=(0, 12))
        ctk.CTkCheckBox(toggles_frame, text="Ping (ms)", variable=self.graph_show_ping, text_color="#FFD600", fg_color="#FFD600", command=self._redraw_analytics_graph).pack(side="left")

        self.canvas_graph = tk.Canvas(graph_card, height=240, bg="#1E222B" if ctk.get_appearance_mode()=="Dark" else "#FFFFFF", highlightthickness=0)
        self.canvas_graph.pack(fill="x", padx=15, pady=(0, 15))

        stress_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        stress_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(stress_card, text="🔥 MULTI-CORE CPU STRESS TEST & THERMAL BENCHMARK", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 6))
        
        stress_desc = "Stresses 100% of all logical processor cores to measure peak computational throughput and thermal cooling efficiency."
        ctk.CTkLabel(stress_card, text=stress_desc, font=ctk.CTkFont(size=12), text_color=("gray40", "gray70")).pack(anchor="w", padx=15, pady=(0, 10))
        
        stress_ctl_row = ctk.CTkFrame(stress_card, fg_color="transparent")
        stress_ctl_row.pack(fill="x", padx=15, pady=(0, 8))
        
        ctk.CTkLabel(stress_ctl_row, text="Duration:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))
        self.stress_duration_var = ctk.StringVar(value="5")
        ctk.CTkSegmentedButton(stress_ctl_row, values=["3", "5", "10"], variable=self.stress_duration_var, width=120).pack(side="left", padx=(0, 15))
        
        self.btn_run_stress = ctk.CTkButton(
            stress_ctl_row, 
            text="🔥 Start CPU Stress Benchmark", 
            fg_color="#FF5252", 
            hover_color="#D50000", 
            font=ctk.CTkFont(weight="bold"),
            command=self._run_cpu_stress
        )
        self.btn_run_stress.pack(side="left")
        
        self.lbl_stress_results = ctk.CTkLabel(stress_card, text="Benchmark Status: Ready", font=ctk.CTkFont(size=12), text_color=("gray40", "gray70"))
        self.lbl_stress_results.pack(anchor="w", padx=15, pady=(0, 15))

    # =========================================================================
    # TAB 7: SETTINGS & REPORT EXPORT
    # =========================================================================
    def _init_settings_tab(self):
        tab = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.tabs["settings"] = tab
        
        theme_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        theme_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(theme_card, text="🎨 UI APPEARANCE & THEME CONTROLS", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))
        
        theme_row = ctk.CTkFrame(theme_card, fg_color="transparent")
        theme_row.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(theme_row, text="Theme Mode:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 10))
        self.opt_mode = ctk.CTkOptionMenu(theme_row, values=["Dark", "Light", "System"], command=self._change_appearance_mode)
        self.opt_mode.set(self.settings.get("appearance_mode", "Dark"))
        self.opt_mode.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(theme_row, text="Polling Interval:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 10))
        self.opt_interval = ctk.CTkOptionMenu(theme_row, values=["2 Seconds", "3 Seconds", "5 Seconds", "10 Seconds"], command=self._change_polling_interval)
        self.opt_interval.set(f"{self.settings.get('refresh_interval_sec', 3)} Seconds")
        self.opt_interval.pack(side="left")

        report_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        report_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(report_card, text="📑 SYSTEM HEALTH AUDIT & DIAGNOSTIC REPORTS", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 6))
        
        ctk.CTkLabel(report_card, text="Export professional dark-mode HTML reports or full text logs directly to your Desktop.", font=ctk.CTkFont(size=12), text_color=("gray40", "gray70")).pack(anchor="w", padx=15, pady=(0, 10))
        
        rep_btn_row = ctk.CTkFrame(report_card, fg_color="transparent")
        rep_btn_row.pack(fill="x", padx=15, pady=(0, 15))
        
        btn_html = ctk.CTkButton(
            rep_btn_row, 
            text="🌐 Generate HTML Dashboard Report", 
            height=34,
            fg_color="#00E5FF", 
            hover_color="#00B0FF",
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            command=self._export_html_report
        )
        btn_html.pack(side="left", padx=(0, 10))
        
        btn_txt = ctk.CTkButton(
            rep_btn_row, 
            text="📝 Export Full Text Audit Log (.txt)", 
            height=34,
            command=self._export_txt_report
        )
        btn_txt.pack(side="left", padx=(0, 10))
        
        btn_desk = ctk.CTkButton(
            rep_btn_row,
            text="📂 Open Desktop",
            height=34,
            fg_color=("gray75", "gray30"),
            command=lambda: os.system(f'explorer "{os.path.join(os.path.expanduser("~"), "Desktop")}"')
        )
        btn_desk.pack(side="left")

        thresh_card = ctk.CTkFrame(tab, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
        thresh_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(thresh_card, text="⚠️ CONFIGURABLE ALERT & THRESHOLD LIMITS", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 6))
        
        thresh_grid = ctk.CTkFrame(thresh_card, fg_color="transparent")
        thresh_grid.pack(fill="x", padx=15, pady=(0, 15))
        thresh_grid.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(thresh_grid, text="RAM Warning Alert: 80%", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", pady=4)
        self.slider_ram = ctk.CTkSlider(thresh_grid, from_=50, to=95, number_of_steps=45)
        self.slider_ram.set(self.settings.get("ram_warning_threshold", 80))
        self.slider_ram.grid(row=0, column=1, sticky="ew", pady=4)
        
        ctk.CTkLabel(thresh_grid, text="CPU Thermal Alert: 75°C", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", pady=4)
        self.slider_temp = ctk.CTkSlider(thresh_grid, from_=60, to=95, number_of_steps=35)
        self.slider_temp.set(self.settings.get("temp_warning_threshold", 75))
        self.slider_temp.grid(row=1, column=1, sticky="ew", pady=4)
        
        ctk.CTkLabel(thresh_grid, text="Storage Warning: 85%", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", pady=4)
        self.slider_disk = ctk.CTkSlider(thresh_grid, from_=60, to=95, number_of_steps=35)
        self.slider_disk.set(self.settings.get("storage_warning_threshold", 85))
        self.slider_disk.grid(row=2, column=1, sticky="ew", pady=4)

    # =========================================================================
    # BACKGROUND TELEMETRY LOOP & THREAD-SAFE GUI REFRESH
    # =========================================================================
    def _background_poll_loop(self):
        while self.running:
            if not self.is_paused:
                battery = self.analyzer.get_battery_health()
                storage = self.analyzer.get_storage_usage()
                temp = self.analyzer.get_temperature()
                ram = self.analyzer.get_ram_usage()
                cpu = self.analyzer.get_cpu_metrics()
                ping = self.analyzer.get_network_metrics()
                
                self.analyzer.log_current_metrics(
                    battery.get("percent", 0),
                    ram.get("percent_used", 0),
                    cpu.get("overall_percent", 0),
                    temp.get("current", 0),
                    ping.get("ping_ms", 0)
                )
                
                health_score = self.analyzer.get_overall_health_score(battery, storage, temp, ram, ping, cpu)
                alerts = self.analyzer.generate_predictive_alerts(battery, storage, temp, ram, ping, cpu)
                
                self.telemetry = {
                    "battery": battery,
                    "storage": storage,
                    "temp": temp,
                    "ram": ram,
                    "cpu": cpu,
                    "ping": ping,
                    "health_score": health_score,
                    "alerts": alerts
                }
                
                if self.running:
                    self.after(0, self._update_gui)
                    
            interval = self.settings.get("refresh_interval_sec", 3)
            time.sleep(max(1, interval))

    def _update_gui(self):
        if not self.running:
            return
            
        t = self.telemetry
        b = t["battery"]
        s = t["storage"]
        tmp = t["temp"]
        r = t["ram"]
        c = t["cpu"]
        p = t["ping"]
        score = t["health_score"]
        alerts = t["alerts"]
        
        # 1. Update Dashboard
        self._draw_score_gauge(score["score"], score["grade"], score["color"])
        self.lbl_dash_rating.configure(text=f"{score['score']}/100 — {score['rating']}", text_color=score["color"])
        
        specs = self.analyzer.get_system_specs()
        self.lbl_dash_summary.configure(text=f"Host: {specs['hostname']} | OS: {specs['os_name']} | Uptime: {specs['uptime']}")
        
        self.badge_bat.configure(text=f"🔋 Battery: {b.get('percent', '--')}%")
        t_str = f"{tmp.get('current')}°C" if tmp.get("status") == "Success" else "N/A"
        self.badge_temp.configure(text=f"🌡️ CPU: {t_str}")
        p_str = f"{p.get('ping_ms')} ms" if p.get("status") == "Online" else "Offline"
        self.badge_net.configure(text=f"🌐 Ping: {p_str}")
        
        self.lbl_dash_cpu_val.configure(text=f"{c.get('overall_percent', 0)}%")
        self.bar_dash_cpu.set(c.get("overall_percent", 0) / 100.0)
        self.lbl_dash_cpu_sub.configure(text=f"{c.get('current_freq_ghz', 0)} GHz | {specs['cpu_cores_logical']} Cores")
        
        self.lbl_dash_ram_val.configure(text=f"{r.get('percent_used', 0)}%")
        self.bar_dash_ram.set(r.get("percent_used", 0) / 100.0)
        self.lbl_dash_ram_sub.configure(text=f"{r.get('used_gb', 0)} / {r.get('total_gb', 0)} GB Used")
        
        self.lbl_dash_bat_val.configure(text=f"{b.get('percent', 0)}%")
        self.bar_dash_bat.set(b.get("percent", 0) / 100.0)
        self.lbl_dash_bat_sub.configure(text=f"Health: {b.get('score', 100)}% ({b.get('wear_percent', 0)}% Wear)")
        
        if s:
            primary_d = s[0]
            self.lbl_dash_disk_val.configure(text=f"{primary_d['percent_used']}%")
            self.bar_dash_disk.set(primary_d["percent_used"] / 100.0)
            self.lbl_dash_disk_sub.configure(text=f"{primary_d['free_gb']} GB Free ({primary_d['drive']})")

        for widget in self.alerts_frame.winfo_children():
            widget.destroy()
            
        for a in alerts:
            border_c = "#00E676" if a["type"] == "success" else ("#FF5252" if a["type"] == "critical" else "#FFD600")
            card = ctk.CTkFrame(self.alerts_frame, corner_radius=8, border_width=1, border_color=border_c)
            card.pack(fill="x", pady=3)
            
            ctk.CTkLabel(card, text=a["title"], font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", padx=12, pady=(6, 2))
            ctk.CTkLabel(card, text=a["msg"], font=ctk.CTkFont(size=11), text_color=("gray40", "gray70"), justify="left", anchor="w", wraplength=700).pack(fill="x", padx=12, pady=(0, 6))

        # 2. Update Hardware Tab
        self.lbl_spec_cpu.configure(text=f"• CPU: {specs['cpu_name']} ({specs['cpu_cores_physical']}C / {specs['cpu_cores_logical']}T)")
        self.lbl_spec_gpu.configure(text=f"• GPU: {specs['gpu_name']} ({specs['gpu_vram_gb']})")
        self.lbl_spec_ram.configure(text=f"• Memory: {specs['ram_total_gb']} GB RAM Total")
        self.lbl_spec_disk.configure(text=f"• Storage: {specs['disk_model']} ({specs['disk_type']})")
        self.lbl_spec_os.configure(text=f"• OS: {specs['os_name']} (Build {specs['os_build']})")
        self.lbl_spec_uptime.configure(text=f"• Uptime: {specs['uptime']}")

        per_core = c.get("per_core_percent", [])
        if len(self.core_widgets) != len(per_core):
            for w in self.cores_bars_frame.winfo_children():
                w.destroy()
            self.core_widgets = []
            for i in range(len(per_core)):
                c_row = ctk.CTkFrame(self.cores_bars_frame, fg_color="transparent")
                c_row.pack(fill="x", pady=2)
                lbl = ctk.CTkLabel(c_row, text=f"Core {i+1}: 0%", width=80, anchor="w", font=ctk.CTkFont(size=11))
                lbl.pack(side="left")
                bar = ctk.CTkProgressBar(c_row, height=8, progress_color="#00E5FF")
                bar.pack(side="left", fill="x", expand=True, padx=8)
                self.core_widgets.append((lbl, bar))
                
        for i, val in enumerate(per_core):
            if i < len(self.core_widgets):
                lbl, bar = self.core_widgets[i]
                lbl.configure(text=f"Core {i+1}: {val}%")
                bar.set(val / 100.0)

        if self.active_tab == "hardware":
            self._refresh_process_table()

        # 3. Update Battery Tab
        self.lbl_bat_wear_status.configure(text=b.get("wear_health", "Normal"))
        self.lbl_bat_design_cap.configure(text=f"• Factory Design Capacity: {b.get('design_cap', 'N/A')}")
        self.lbl_bat_full_cap.configure(text=f"• Full Charge Max Capacity: {b.get('full_cap', 'N/A')}")
        self.lbl_bat_wear_pct.configure(text=f"• Total Wear Degradation: {b.get('wear_percent', 0)}%")
        self.lbl_bat_cycle_count.configure(text=f"• Lifetime Charge Cycles: {b.get('cycle_count', 'N/A')}")
        
        self.lbl_bat_current_pct.configure(text=f"Current Level: {b.get('percent', 0)}%")
        plugged_str = "Plugged In (Charging on AC Power)" if b.get("power_plugged") else "On Battery Power (Discharging)"
        self.lbl_bat_plugged.configure(text=f"• Power Connection: {plugged_str}")
        self.lbl_bat_runtime.configure(text=f"• Estimated Battery Life: {b.get('time_left_str', 'Calculating...')}")
        self.lbl_bat_chemistry.configure(text=f"• Cell Chemistry: {b.get('chemistry', 'Li-Ion')}")
        self.lbl_bat_mfg.configure(text=f"• Battery Manufacturer: {b.get('manufacturer', 'OEM')}")

        # 4. Update Storage Tab
        for w in self.storage_drives_frame.winfo_children():
            w.destroy()
            
        for drive in s:
            d_card = ctk.CTkFrame(self.storage_drives_frame, corner_radius=10, border_width=1, border_color=("gray80", "gray25"))
            d_card.pack(fill="x", pady=3)
            
            d_top = ctk.CTkFrame(d_card, fg_color="transparent")
            d_top.pack(fill="x", padx=15, pady=(10, 4))
            
            ctk.CTkLabel(d_top, text=f"Drive ({drive['drive']}) — {drive['type']}", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(d_top, text=f"{drive['used_gb']} GB Used / {drive['total_gb']} GB Total ({drive['percent_used']}%)", font=ctk.CTkFont(size=11), text_color=("gray40", "gray70")).pack(side="right")
            
            bar_c = "#FF5252" if drive["percent_used"] >= 85 else "#00E5FF"
            p_bar = ctk.CTkProgressBar(d_card, height=10, progress_color=bar_c)
            p_bar.pack(fill="x", padx=15, pady=(0, 10))
            p_bar.set(drive["percent_used"] / 100.0)

        io = self.analyzer.get_disk_io_throughput()
        self.lbl_disk_read_speed.configure(text=f"Read Speed: {io['read_mb_s']} MB/s")
        self.lbl_disk_write_speed.configure(text=f"Write Speed: {io['write_mb_s']} MB/s")

        # 5. Update Network Tab
        self.lbl_net_ping.configure(text=f"{p.get('ping_ms', '--')} ms")
        self.lbl_net_jitter.configure(text=f"{p.get('jitter_ms', 0)} ms")
        self.lbl_net_link_state.configure(text=p.get("status", "Offline"), text_color="#00E676" if p.get("status")=="Online" else "#FF5252")
        
        wf = p.get("wifi", {})
        self.lbl_wifi_ssid.configure(text=f"• Connected Network: {wf.get('ssid', 'Ethernet')}")
        self.lbl_wifi_sig.configure(text=f"• Signal Quality: {wf.get('signal_pct', 100)}% ({wf.get('radio_type', '')})")
        self.lbl_wifi_rates.configure(text=f"• Link Rate: Rx {wf.get('rx_rate', 'N/A')} | Tx {wf.get('tx_rate', 'N/A')}")
        self.lbl_net_bandwidth.configure(text=f"• Live Speed: ↓ {p.get('down_kb_s', 0)} KB/s  |  ↑ {p.get('up_kb_s', 0)} KB/s")

        # 6. Redraw Analytics Waveform if active
        if self.active_tab == "analytics":
            self._redraw_analytics_graph()

    def _refresh_process_table(self):
        query = self.entry_proc_search.get() if hasattr(self, 'entry_proc_search') else ""
        procs = self.analyzer.get_processes_list(limit=40, search_query=query)
        
        selected_pid = None
        sel = self.tree_proc.selection()
        if sel:
            selected_pid = self.tree_proc.item(sel[0])["values"][0]
            
        for row in self.tree_proc.get_children():
            self.tree_proc.delete(row)
            
        for p in procs:
            item_id = self.tree_proc.insert("", "end", values=(p["pid"], p["name"], f"{p['memory_mb']} MB", f"{p['cpu_percent']}%", p["user"]))
            if selected_pid and p["pid"] == selected_pid:
                self.tree_proc.selection_set(item_id)

    def _kill_selected_process(self):
        sel = self.tree_proc.selection()
        if not sel:
            messagebox.showwarning("Select Process", "Please click a process in the table to select it for termination.")
            return
            
        vals = self.tree_proc.item(sel[0])["values"]
        pid = int(vals[0])
        name = vals[1]
        
        confirm = messagebox.askyesno("Confirm Terminate", f"Are you sure you want to terminate '{name}' (PID: {pid})?")
        if confirm:
            success, msg = self.analyzer.kill_process(pid)
            if success:
                messagebox.showinfo("Process Terminated", msg)
                self._refresh_process_table()
            else:
                messagebox.showerror("Error", msg)

    def _trigger_turbo_ram(self):
        def task():
            res = self.analyzer.turbo_ram_clean()
            self.after(0, lambda: messagebox.showinfo(
                "⚡ Turbo RAM Clean Completed",
                f"Memory Optimization Successful!\n\n"
                f"• Cleaned Working Sets: {res['processes_trimmed']} active applications\n"
                f"• RAM Freed: {res['freed_mb']} MB\n"
                f"• New RAM Usage: {res['new_ram_percent']}%"
            ))
            
        t = threading.Thread(target=task, daemon=True)
        t.start()

    def _switch_power_plan(self, plan_key):
        success, msg = self.analyzer.set_power_plan(plan_key)
        if success:
            messagebox.showinfo("Power Scheme Updated", msg)
        else:
            messagebox.showwarning("Power Scheme", msg)

    def _run_disk_benchmark(self):
        self.btn_run_bench.configure(state="disabled", text="Running 32MB Benchmark...")
        self.lbl_bench_res.configure(text="Testing sequential read/write throughput...")
        
        def task():
            res = self.analyzer.benchmark_disk_speed(32)
            def done():
                self.btn_run_bench.configure(state="normal", text="🚀 Run SSD Speed Test (32MB)")
                if res.get("success"):
                    self.lbl_bench_res.configure(
                        text=f"Write: {res['write_mb_s']} MB/s | Read: {res['read_mb_s']} MB/s ({res['rating']})",
                        text_color="#00E676"
                    )
                else:
                    self.lbl_bench_res.configure(text=f"Benchmark Failed: {res.get('error')}", text_color="#FF5252")
            self.after(0, done)
            
        t = threading.Thread(target=task, daemon=True)
        t.start()

    def _scan_junk(self):
        self.lbl_junk_status.configure(text="Scanning temporary folders...")
        def task():
            res = self.analyzer.scan_junk_files()
            self.after(0, lambda: self.lbl_junk_status.configure(
                text=f"Found {res['total_mb']} MB cleanable junk across {res['file_count']} temporary files.",
                text_color="#00E5FF"
            ))
        t = threading.Thread(target=task, daemon=True)
        t.start()

    def _clean_junk(self):
        self.lbl_junk_status.configure(text="Cleaning junk files safely...")
        def task():
            res = self.analyzer.clean_junk_files()
            self.after(0, lambda: messagebox.showinfo(
                "Disk Cleanup Complete",
                f"Temporary Cleanup Finished!\n\n"
                f"• Cleaned: {res['cleaned_mb']} MB\n"
                f"• Files Deleted: {res['deleted_count']}"
            ))
            self.after(0, lambda: self.lbl_junk_status.configure(text="Temporary junk cleaned clean!"))
        t = threading.Thread(target=task, daemon=True)
        t.start()

    def _run_dns_flush(self):
        ok = self.analyzer.flush_dns()
        if ok:
            messagebox.showinfo("DNS Cache", "Windows DNS Resolver Cache successfully flushed!")
        else:
            messagebox.showerror("Error", "Could not flush DNS cache.")

    def _run_ip_renew(self):
        def task():
            ok = self.analyzer.renew_ip()
            self.after(0, lambda: messagebox.showinfo("IP Renew", "DHCP IP configuration successfully renewed!"))
        threading.Thread(target=task, daemon=True).start()

    def _run_cpu_stress(self):
        dur = int(self.stress_duration_var.get())
        self.btn_run_stress.configure(state="disabled", text=f"Stressing CPU ({dur}s)...")
        self.lbl_stress_results.configure(text=f"Running multithreaded math operations across all cores for {dur}s...")
        
        def task():
            res = self.analyzer.run_cpu_stress_test(dur)
            def done():
                self.btn_run_stress.configure(state="normal", text="🔥 Start CPU Stress Benchmark")
                self.lbl_stress_results.configure(
                    text=f"Score: {res['score']:,} pts | Ops: {res['total_ops']:,} | Peak Temp: {res['peak_temp']}°C (+{res['temp_delta']}°C)",
                    text_color="#00E676"
                )
            self.after(0, done)
            
        threading.Thread(target=task, daemon=True).start()

    def _redraw_analytics_graph(self):
        self.canvas_graph.delete("all")
        history = self.analyzer.get_historical_data()
        
        w = self.canvas_graph.winfo_width()
        h = self.canvas_graph.winfo_height()
        if w < 50: w = 750
        if h < 50: h = 240
        
        pad_l, pad_r, pad_t, pad_b = 40, 20, 20, 30
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b
        
        bg_c = "#1E222B" if ctk.get_appearance_mode()=="Dark" else "#FFFFFF"
        grid_c = "#2A3241" if ctk.get_appearance_mode()=="Dark" else "#E5E7EB"
        text_c = "#8B949E"
        
        self.canvas_graph.configure(bg=bg_c)
        
        for i in range(0, 101, 25):
            y = pad_t + plot_h - (i / 100.0 * plot_h)
            self.canvas_graph.create_line(pad_l, y, w - pad_r, y, fill=grid_c, dash=(2, 4))
            self.canvas_graph.create_text(pad_l - 8, y, text=f"{i}%", font=("Segoe UI", 8), fill=text_c, anchor="e")
            
        if len(history) < 2:
            self.canvas_graph.create_text(w / 2, h / 2, text="Collecting metrics telemetry... (Graph updates in 3s)", font=("Segoe UI", 11), fill=text_c)
            return

        x_step = plot_w / max(1, len(history) - 1)
        
        def plot_series(key, color, max_scale=100.0):
            pts = []
            for idx, pt in enumerate(history):
                val = pt.get(key, 0)
                norm = min(1.0, max(0.0, val / max_scale))
                x = pad_l + (idx * x_step)
                y = pad_t + plot_h - (norm * plot_h)
                pts.append((x, y))
                
            for i in range(len(pts) - 1):
                self.canvas_graph.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], fill=color, width=2, smooth=True)
                self.canvas_graph.create_oval(pts[i][0]-2, pts[i][1]-2, pts[i][0]+2, pts[i][1]+2, fill=color, outline="")

        if self.graph_show_bat.get(): plot_series("battery", "#00E676")
        if self.graph_show_ram.get(): plot_series("ram", "#7C4DFF")
        if self.graph_show_cpu.get(): plot_series("cpu", "#00E5FF")
        if self.graph_show_temp.get(): plot_series("temp", "#FF5252", max_scale=100.0)
        if self.graph_show_ping.get(): plot_series("ping", "#FFD600", max_scale=200.0)

        for idx in range(0, len(history), max(1, len(history) // 5)):
            x = pad_l + (idx * x_step)
            t_str = history[idx].get("time", "")
            self.canvas_graph.create_text(x, h - pad_b + 12, text=t_str, font=("Segoe UI", 8), fill=text_c)

    def _export_html_report(self):
        t = self.telemetry
        path = self.analyzer.export_html_report(
            t["battery"], t["storage"], t["temp"], t["ram"], t["ping"], t["cpu"], t["health_score"], t["alerts"]
        )
        msg = f"HTML Diagnostic Report generated successfully!\n\nSaved to Desktop:\n{path}\n\nWould you like to open it in your browser now?"
        if messagebox.askyesno("Report Ready", msg):
            os.system(f'start "" "{path}"')

    def _export_txt_report(self):
        t = self.telemetry
        path = self.analyzer.export_text_log(
            t["battery"], t["storage"], t["temp"], t["ram"], t["ping"], t["cpu"], t["health_score"], t["alerts"]
        )
        messagebox.showinfo("Export Successful", f"Diagnostic Audit Log saved to Desktop:\n\n{path}")

    def _change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode)
        self.settings["appearance_mode"] = mode
        save_settings(self.settings)
        self._redraw_analytics_graph()
        self._update_gui()

    def _change_polling_interval(self, val):
        sec = int(val.split()[0])
        self.settings["refresh_interval_sec"] = sec
        save_settings(self.settings)
        self.lbl_live_status.configure(text=f"● LIVE MONITOR ({sec}s)")

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.configure(text="Resume", fg_color="#00E676", text_color="#000000")
            self.lbl_live_status.configure(text="⏸ PAUSED", text_color="#FFD600")
        else:
            self.btn_pause.configure(text="Pause", fg_color=("gray75", "gray30"), text_color=("gray10", "gray90"))
            sec = self.settings.get("refresh_interval_sec", 3)
            self.lbl_live_status.configure(text=f"● LIVE MONITOR ({sec}s)", text_color="#00E676")

    def _on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = LaptopHealthApp()
    app.mainloop()
