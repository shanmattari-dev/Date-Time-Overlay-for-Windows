#Created by WASIN WANNATHONG A.K.A. Shan★Mattari
#P.S. AI Vibe Coding

import tkinter as tk
from tkinter import ttk, colorchooser, font
from datetime import datetime
import ctypes
import sys

class DateTimeOverlay:
    POSITIONS = {
        "Top Left": "top_left",
        "Top Center": "top_center",
        "Top Right": "top_right",
        "Bottom Left": "bottom_left",
        "Bottom Center": "bottom_center",
        "Bottom Right": "bottom_right",
    }
    
    # Language translations
    TRANSLATIONS = {
        "English": {
            "title": "Control Panel",
            "header": "Date & Time Overlay",
            "font": "Font",
            "font_size": "Font Size",
            "text_color": "Text Color",
            "bg_color": "Background Color",
            "position": "Position",
            "date_format": "Date / Time Format",
            "transparency": "Transparency",
            "toggle_overlay": "Toggle Overlay",
            "language": "Language",
            "theme": "Theme",
            "status": "Status: ",
            "status_active": "Activated",
            "status_inactive": "Deactivated",
            "click_through": "Click-Through",
            "click_through_on": "ON (locked)",
            "click_through_off": "OFF (draggable)",
            "reset": "Reset Settings"
        },
        "Thai": {
            "title": "แผงควบคุม",
            "header": "Date & Time Overlay",
            "font": "แบบอักษร",
            "font_size": "ขนาดข้อความ",
            "text_color": "สีข้อความ",
            "bg_color": "สีพื้นหลัง",
            "position": "ตำแหน่ง",
            "date_format": "รูปแบบ Date / Time",
            "transparency": "ความโปร่งใส",
            "toggle_overlay": "เปิด/ปิด Overlay",
            "language": "ภาษา",
            "theme": "ธีม",
            "status": "สถานะ: ",
            "status_active": "กำลังทำงาน",
            "status_inactive": "หยุดทำงาน",
            "click_through": "คลิกทะลุ (Click-Through)",
            "click_through_on": "เปิด (ล็อกตำแหน่ง)",
            "click_through_off": "ปิด (ลากย้ายได้)",
            "reset": "รีเซ็ตการตั้งค่า"
        },
        "Chinese": {
            "title": "控制面板",
            "header": "日期和时间覆盖层",
            "font": "字体",
            "font_size": "字体大小",
            "text_color": "文字颜色",
            "bg_color": "背景颜色",
            "position": "位置",
            "date_format": "日期/时间格式",
            "transparency": "透明度",
            "toggle_overlay": "切换覆盖层",
            "language": "语言",
            "theme": "主题",
            "status": "状态: ",
            "status_active": "已激活",
            "status_inactive": "已停用",
            "click_through": "鼠标穿透",
            "click_through_on": "开启（锁定位置）",
            "click_through_off": "关闭（可拖动）",
            "reset": "重置设置"
        },
        "Japanese": {
            "title": "コントロールパネル",
            "header": "日時オーバーレイ",
            "font": "フォント",
            "font_size": "フォントサイズ",
            "text_color": "テキストカラー",
            "bg_color": "背景色",
            "position": "位置",
            "date_format": "日付/時刻形式",
            "transparency": "透明度",
            "toggle_overlay": "オーバーレイ切替",
            "language": "言語",
            "theme": "テーマ",
            "status": "ステータス: ",
            "status_active": "アクティブ",
            "status_inactive": "非アクティブ",
            "click_through": "クリックスルー",
            "click_through_on": "オン（位置固定）",
            "click_through_off": "オフ（ドラッグ移動可）",
            "reset": "設定をリセット"
        }
    }

    def __init__(self, root):
        self.root = root
        self.current_language = tk.StringVar(value="English")
        self.theme = tk.StringVar(value="Default")
        self.root.title(self.TRANSLATIONS["English"]["title"])
        self.root.geometry("362x570")
        self.root.resizable(False, False)
        
        # Center the window on screen
        self.center_window()

        self.overlay = None
        self.timer_id = None
        self.is_active = False
        self.is_refreshing = False

        # Click-through state and manual drag position
        self.click_through_var = tk.BooleanVar(value=True)  # Changed to ON by default
        self.manual_position = False
        self._manual_x = None
        self._manual_y = None
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._win_start_x = 0
        self._win_start_y = 0

        # เปลี่ยน Default Font เป็น Tahoma
        self.font_name = tk.StringVar(value="Tahoma")
        self.font_size = tk.IntVar(value=28)
        self.text_color = tk.StringVar(value="#FFFFFF")
        self.bg_color = tk.StringVar(value="#000000")
        self.position = tk.StringVar(value="Top Center")
        self.date_format = tk.StringVar(value="%H:%M:%S")  # Changed to time-only format
        self.alpha = tk.DoubleVar(value=0.90)

        # Fixed overlay spacing (no user-facing margin setting).
        self.position_margin = 20
        self.overlay_padding = 20

        self.build_gui()
        self.load_fonts()

        # Update the visible overlay immediately whenever a setting changes.
        for variable in (
            self.font_name,
            self.font_size,
            self.text_color,
            self.bg_color,
            self.position,
            self.date_format,
        ):
            variable.trace_add("write", self._setting_changed)
        self.theme.trace_add("write", self._theme_changed)
        self.apply_theme()
        
        # Set close protocol to exit program completely
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = 362
        height = 570
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius=15, fill="black", outline="black"):
        """Draw a rounded rectangle on canvas."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        
        return canvas.create_polygon(
            points,
            fill=fill,
            outline=outline,
            smooth=True,
            splinesteps=4,
            tags="bg"
        )

    def build_gui(self):
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        self.header_label = ttk.Label(
            main,
            text=self.TRANSLATIONS["English"]["header"],
            font=("Segoe UI", 18, "bold")
        )
        self.header_label.pack(anchor="w", pady=(0, 15))

        # Language selection at top
        lang_frame = ttk.Frame(main)
        lang_frame.pack(fill="x", pady=(0, 15))
        
        self.lang_label = ttk.Label(lang_frame, text=self.TRANSLATIONS["English"]["language"])
        self.lang_label.pack(side="left", padx=(0, 10))
        
        self.lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.current_language,
            values=["English", "Thai", "Chinese", "Japanese"],
            state="readonly",
            width=15
        )
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self.change_language)

        # Theme selection
        theme_frame = ttk.Frame(main)
        theme_frame.pack(fill="x", pady=(0, 15))

        self.theme_label = ttk.Label(theme_frame, text=self.TRANSLATIONS["English"]["theme"])
        self.theme_label.pack(side="left", padx=(0, 10))

        self.theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme,
            values=["Default", "Classic"],
            state="readonly",
            width=15
        )
        self.theme_combo.pack(side="left")
        self.theme_combo.bind("<<ComboboxSelected>>", self.change_theme)

        settings = ttk.Frame(main)
        settings.pack(fill="x")

        # Font
        self.font_label = ttk.Label(settings, text=self.TRANSLATIONS["English"]["font"])
        self.font_label.grid(row=0, column=0, sticky="w", pady=6)
        self.font_combo = ttk.Combobox(
            settings,
            textvariable=self.font_name,
            state="readonly",
            width=30
        )
        self.font_combo.grid(row=0, column=1, sticky="w", padx=10)
        self.font_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_overlay())

        # Font Size
        self.font_size_label = ttk.Label(settings, text=self.TRANSLATIONS["English"]["font_size"])
        self.font_size_label.grid(row=1, column=0, sticky="w", pady=6)
        
        font_size_frame = ttk.Frame(settings)
        font_size_frame.grid(row=1, column=1, sticky="w", padx=10)
        
        # Styled font size slider
        self.font_size_scale = tk.Scale(
            font_size_frame,
            from_=8,
            to=200,
            variable=self.font_size,
            orient="horizontal",
            length=160
        )
        self.font_size_scale.pack(side="left")
        
        # self.font_size_value_label = tk.Label(
            # font_size_frame,
            # text="28",
            # width=4,
            # font=("Segoe UI", 10, "bold")
        # )
        # self.font_size_value_label.pack(side="left", padx=(10, 0))
        
        self.font_size.trace_add("write", self._update_font_size_label)

        # Text Color
        self.text_color_label = ttk.Label(settings, text=self.TRANSLATIONS["English"]["text_color"])
        self.text_color_label.grid(row=2, column=0, sticky="w", pady=6)
        self.text_color_button = tk.Button(
            settings,
            textvariable=self.text_color,
            command=self.choose_text_color,
            width=15,
            bg=self.text_color.get(),
            fg=self.get_contrast_color(self.text_color.get()),
            activebackground=self.text_color.get(),
            activeforeground=self.get_contrast_color(self.text_color.get()),
            relief="raised",
            bd=2
        )
        self.text_color_button.grid(row=2, column=1, sticky="w", padx=10)

        # Background Color
        self.bg_color_label = ttk.Label(settings, text=self.TRANSLATIONS["English"]["bg_color"])
        self.bg_color_label.grid(row=3, column=0, sticky="w", pady=6)
        self.bg_color_button = tk.Button(
            settings,
            textvariable=self.bg_color,
            command=self.choose_bg_color,
            width=15,
            bg=self.bg_color.get(),
            fg=self.get_contrast_color(self.bg_color.get()),
            activebackground=self.bg_color.get(),
            activeforeground=self.get_contrast_color(self.bg_color.get()),
            relief="raised",
            bd=2
        )
        self.bg_color_button.grid(row=3, column=1, sticky="w", padx=10)

        # Position
        self.position_label = ttk.Label(settings, text=self.TRANSLATIONS["English"]["position"])
        self.position_label.grid(row=4, column=0, sticky="w", pady=6)
        self.position_combo = ttk.Combobox(
            settings,
            textvariable=self.position,
            values=list(self.POSITIONS.keys()),
            state="readonly",
            width=28
        )
        self.position_combo.grid(row=4, column=1, sticky="w", padx=10)
        self.position_combo.bind("<<ComboboxSelected>>", self._on_position_changed)

        # Date Format
        self.date_format_label = ttk.Label(settings, text=self.TRANSLATIONS["English"]["date_format"])
        self.date_format_label.grid(row=5, column=0, sticky="w", pady=6)
        self.format_combo = ttk.Combobox(
            settings,
            textvariable=self.date_format,
            values=[
                "%Y-%m-%d  %H:%M:%S",
                "%d/%m/%Y  %H:%M:%S",
                "%d/%m/%Y  %H:%M",
                "%Y-%m-%d  %H:%M",
                "%H:%M:%S",
            ],
            width=28
        )
        self.format_combo.grid(row=5, column=1, sticky="w", padx=10)
        self.format_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_overlay())

        # Transparency
        self.transparency_label = ttk.Label(settings, text=self.TRANSLATIONS["English"]["transparency"])
        self.transparency_label.grid(row=6, column=0, sticky="w", pady=6)
        
        # Transparency slider frame with value display
        alpha_frame = ttk.Frame(settings)
        alpha_frame.grid(row=6, column=1, sticky="w", padx=10)
        
        # Styled transparency slider
        self.alpha_scale = tk.Scale(
            alpha_frame,
            from_=0.1,
            to=1.0,
            variable=self.alpha,
            orient="horizontal",
            length=130,
            resolution=0.01,
            command=self.on_alpha_change
        )
        self.alpha_scale.pack(side="left")
        
        # Transparency value display
        # self.alpha_value_label = tk.Label(
            # alpha_frame,
            # text="90%",
            # width=5,
            # font=("Segoe UI", 10, "bold")
        # )
        # self.alpha_value_label.pack(side="left", padx=(10, 0))
        
        self.alpha.trace_add("write", self._update_alpha_label)

        # Click-Through toggle
        self.click_through_label = ttk.Label(settings, text=self.TRANSLATIONS["English"]["click_through"])
        self.click_through_label.grid(row=7, column=0, sticky="w", pady=6)

        click_through_frame = ttk.Frame(settings)
        click_through_frame.grid(row=7, column=1, sticky="w", padx=10)

        self.click_through_check = ttk.Checkbutton(
            click_through_frame,
            variable=self.click_through_var,
            command=self.on_click_through_toggle
        )
        self.click_through_check.pack(side="left")

        self.click_through_status_label = ttk.Label(
            click_through_frame,
            text=self.TRANSLATIONS["English"]["click_through_on"],  # Changed to show ON by default
            width=20
        )
        self.click_through_status_label.pack(side="left", padx=(6, 0))

        # Reset Settings button (moved to below Click-Through)
        reset_frame = ttk.Frame(settings)
        reset_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.reset_button = ttk.Button(
            reset_frame,
            text=self.TRANSLATIONS["English"]["reset"],
            command=self.reset_settings,
            width=30
        )
        self.reset_button.pack()

        ttk.Separator(main).pack(fill="x", pady=18)

        # Status and Toggle Button Frame
        status_frame = ttk.Frame(main)
        status_frame.pack(fill="x", pady=(0, 10))

        # Status Label with "Status: " prefix
        self.status_prefix_label = ttk.Label(
            status_frame,
            text=self.TRANSLATIONS["English"]["status"],
            font=("Segoe UI", 12, "bold")
        )
        self.status_prefix_label.pack(side="left")
        
        self.status_label = tk.Label(
            status_frame,
            text=self.TRANSLATIONS["English"]["status_inactive"],
            font=("Segoe UI", 12, "bold"),
            fg="red"
        )
        self.status_label.pack(side="left", padx=(0, 20))

        # Toggle Overlay button
        self.toggle_button = ttk.Button(
            status_frame,
            text=self.TRANSLATIONS["English"]["toggle_overlay"],
            command=self.toggle_overlay,
            width=20
        )
        self.toggle_button.pack(side="left")

    def _update_alpha_label(self, *args):
        """Update the alpha value display label."""
        try:
            value = int(float(self.alpha.get()) * 100)
            self.alpha_value_label.config(text=f"{value}%")
        except:
            pass

    THEME_PALETTES = {
        "Default": {"bg": "#F0F0F0", "fg": "#000000", "accent": "#0078D7", "overlay_bg": "#000000", "overlay_fg": "#FFFFFF"},
        "Classic": {"bg": "#E8DCC4", "fg": "#3B2A1A", "accent": "#8B5A2B", "overlay_bg": "#3B2A1A", "overlay_fg": "#F5E6C8"},
    }

    def _theme_changed(self, *args):
        self.apply_theme()
        self.refresh_overlay()

    def change_theme(self, event=None):
        palette = self.THEME_PALETTES.get(self.theme.get(), self.THEME_PALETTES["Default"])
        # Theme controls the visual palette of the overlay.
        self.bg_color.set(palette["overlay_bg"])
        self.text_color.set(palette["overlay_fg"])
        self.apply_theme()
        self.update_color_buttons()
        if self.is_active:
            self.refresh_overlay()

    def apply_theme(self):
        palette = self.THEME_PALETTES.get(self.theme.get(), self.THEME_PALETTES["Default"])
        try:
            style = ttk.Style(self.root)
            style.configure("TFrame", background=palette["bg"])
            style.configure("TLabel", background=palette["bg"], foreground=palette["fg"])
            style.configure("TCheckbutton", background=palette["bg"], foreground=palette["fg"])
            style.configure("TButton", background=palette["bg"], foreground=palette["fg"])
            style.configure("TCombobox", fieldbackground=palette["bg"], background=palette["bg"], foreground=palette["fg"])
            
            # Enhanced slider styling
            style.configure("TScale", 
                background=palette["bg"],
                troughcolor=palette["fg"] if palette["fg"] != "#000000" else "#D0D0D0",
                sliderrelief="flat",
                sliderthickness=18
            )
            style.configure("Vertical.TScale", sliderrelief="flat", sliderthickness=18)
            
            self.root.configure(bg=palette["bg"])
            self.header_label.configure(foreground=palette["fg"], background=palette["bg"])
            self.status_prefix_label.configure(foreground=palette["fg"], background=palette["bg"])
            self.status_label.configure(background=palette["bg"])
            self.update_color_buttons()
        except Exception:
            pass

    def change_language(self, *args):
        """Change the UI language."""
        lang = self.current_language.get()
        trans = self.TRANSLATIONS[lang]
        
        self.root.title(trans["title"])
        self.header_label.config(text=trans["header"])
        
        self.font_label.config(text=trans["font"])
        self.font_size_label.config(text=trans["font_size"])
        self.text_color_label.config(text=trans["text_color"])
        self.bg_color_label.config(text=trans["bg_color"])
        self.position_label.config(text=trans["position"])
        self.date_format_label.config(text=trans["date_format"])
        self.transparency_label.config(text=trans["transparency"])
        self.lang_label.config(text=trans["language"])
        self.theme_label.config(text=trans["theme"])
        self.status_prefix_label.config(text=trans["status"])
        self.click_through_label.config(text=trans["click_through"])
        self.click_through_status_label.config(
            text=trans["click_through_on"] if self.click_through_var.get() else trans["click_through_off"]
        )
        
        self.toggle_button.config(text=trans["toggle_overlay"])
        self.reset_button.config(text=trans["reset"])
        if self.is_active:
            self.status_label.config(text=trans["status_active"])
            self.status_label.config(fg="green")
        else:
            self.status_label.config(text=trans["status_inactive"])
            self.status_label.config(fg="red")

    def reset_settings(self):
        """Restore all user-adjustable settings to the program defaults."""
        defaults = {
            "font_name": "Tahoma",
            "font_size": 28,
            "text_color": "#FFFFFF",
            "bg_color": "#000000",
            "position": "Top Center",
            "date_format": "%H:%M:%S",  # Changed to time-only format
            "alpha": 0.90,
            "click_through": True,  # Changed to ON by default
        }

        self.manual_position = False
        self._manual_x = None
        self._manual_y = None

        self.current_language.set("English")
        self.theme.set("Default")
        self.font_name.set(defaults["font_name"])
        self.font_size.set(defaults["font_size"])
        self.text_color.set(defaults["text_color"])
        self.bg_color.set(defaults["bg_color"])
        self.position.set(defaults["position"])
        self.date_format.set(defaults["date_format"])
        self.alpha.set(defaults["alpha"])
        self.click_through_var.set(defaults["click_through"])

        self.change_language()
        self.update_color_buttons()
        self._update_font_size_label()
        self._update_alpha_label()
        
        # แก้ไข: อัปเดตข้อความ Click-Through ให้ถูกต้องตามค่า Default
        lang = self.current_language.get()
        trans = self.TRANSLATIONS[lang]
        is_on = self.click_through_var.get()
        self.click_through_status_label.config(
            text=trans["click_through_on"] if is_on else trans["click_through_off"]
        )

        if self.overlay is not None and self.is_active:
            self.refresh_overlay()
            self.enable_click_through()

    def toggle_overlay(self):
        if self.is_active:
            self.hide_overlay()
        else:
            self.show_overlay()

    def _update_font_size_label(self, *args):
        try:
            value = int(self.font_size.get())
            self.font_size_value_label.config(text=str(value))
        except:
            pass

    def load_fonts(self):
        try:
            families = sorted(set(font.families()))
            self.font_combo["values"] = families
            # ตั้งค่า Default เป็น Tahoma
            if "Tahoma" in families:
                self.font_name.set("Tahoma")
            elif families:
                self.font_name.set(families[0])
        except Exception:
            pass

    def _setting_changed(self, *args):
        self.refresh_overlay()

    def on_alpha_change(self, value):
        if self.overlay is not None:
            try:
                self.overlay.attributes("-alpha", float(value))
                self.enable_click_through()
            except Exception:
                pass

    def _on_position_changed(self, event=None):
        """User picked a preset position from the combobox: drop any manual drag offset."""
        self.manual_position = False
        self.refresh_overlay()

    def on_click_through_toggle(self):
        """Flip click-through mode and update the status label / window style."""
        lang = self.current_language.get()
        trans = self.TRANSLATIONS[lang]
        is_on = self.click_through_var.get()
        self.click_through_status_label.config(
            text=trans["click_through_on"] if is_on else trans["click_through_off"]
        )
        self.enable_click_through()
        self._update_drag_cursor()

    def _update_drag_cursor(self):
        """Show a move cursor over the overlay while it can be dragged."""
        if self.overlay is None:
            return
        cursor = "fleur" if not self.click_through_var.get() else ""
        for widget in (self.overlay, getattr(self, "overlay_canvas", None), getattr(self, "overlay_label", None)):
            if widget is None:
                continue
            try:
                widget.config(cursor=cursor)
            except tk.TclError:
                pass

    def _bind_drag_events(self):
        """Allow dragging the overlay to reposition it while click-through is OFF."""
        widgets = (
            self.overlay,
            getattr(self, "overlay_canvas", None),
            getattr(self, "overlay_label", None),
        )
        for widget in widgets:
            if widget is None:
                continue
            try:
                widget.bind("<ButtonPress-1>", self._on_drag_start)
                widget.bind("<B1-Motion>", self._on_drag_motion)
                widget.bind("<ButtonRelease-1>", self._on_drag_end)
            except tk.TclError:
                pass

    def _on_drag_start(self, event):
        if self.click_through_var.get() or self.overlay is None:
            return
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._win_start_x = self.overlay.winfo_x()
        self._win_start_y = self.overlay.winfo_y()

    def _on_drag_motion(self, event):
        if self.click_through_var.get() or self.overlay is None:
            return
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        new_x = self._win_start_x + dx
        new_y = self._win_start_y + dy
        try:
            self.overlay.geometry(f"+{new_x}+{new_y}")
        except tk.TclError:
            return
        self.manual_position = True
        self._manual_x = new_x
        self._manual_y = new_y

    def _on_drag_end(self, event):
        pass

    @staticmethod
    def get_contrast_color(hex_color):
        """Return black/white text that remains readable on a color button."""
        try:
            value = hex_color.lstrip("#")
            if len(value) != 6:
                return "black"
            r, g, b = (int(value[i:i+2], 16) for i in (0, 2, 4))
            # Perceived luminance approximation.
            luminance = (0.299 * r + 0.587 * g + 0.114 * b)
            return "black" if luminance >= 150 else "white"
        except Exception:
            return "black"

    def update_color_buttons(self):
        """Make each color selector button visibly match its selected color."""
        try:
            text_bg = self.text_color.get()
            text_fg = self.get_contrast_color(text_bg)
            self.text_color_button.config(
                bg=text_bg,
                fg=text_fg,
                activebackground=text_bg,
                activeforeground=text_fg
            )
        except (AttributeError, tk.TclError):
            pass

        try:
            bg = self.bg_color.get()
            bg_fg = self.get_contrast_color(bg)
            self.bg_color_button.config(
                bg=bg,
                fg=bg_fg,
                activebackground=bg,
                activeforeground=bg_fg
            )
        except (AttributeError, tk.TclError):
            pass

    def choose_text_color(self):
        result = colorchooser.askcolor(initialcolor=self.text_color.get())
        if result[1]:
            self.text_color.set(result[1])
            self.update_color_buttons()
            self.refresh_overlay()

    def choose_bg_color(self):
        result = colorchooser.askcolor(initialcolor=self.bg_color.get())
        if result[1]:
            self.bg_color.set(result[1])
            self.update_color_buttons()
            self.refresh_overlay()

    def get_datetime_text(self):
        """Return the clock text using the computer's local date/time."""
        try:
            return datetime.now().astimezone().strftime(self.date_format.get())
        except Exception:
            return datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    def update_rounded_background(self, canvas, label, bg_color):
        try:
            if not canvas.winfo_exists() or not label.winfo_exists():
                return
            
            label.update_idletasks()
            width = label.winfo_reqwidth() + 40
            height = label.winfo_reqheight() + 40
            
            canvas.config(width=width, height=height)
            canvas.delete("bg")
            radius = 15
            self.draw_rounded_rect(
                canvas,
                0, 0, width, height,
                radius=radius,
                fill=bg_color,
                outline=bg_color
            )
            label.place(relx=0.5, rely=0.5, anchor="center")
        except (tk.TclError, AttributeError):
            pass

    def create_rounded_corner_label(self, parent, text, font, fg, bg, padx, pady):
        canvas = tk.Canvas(
            parent,
            highlightthickness=0,
            bg=parent.cget("bg") if hasattr(parent, "cget") else "black"
        )
        
        label = tk.Label(
            canvas,
            text=text,
            font=font,
            fg=fg,
            bg=bg,
            padx=padx,
            pady=pady
        )
        
        label.pack()
        
        def update_canvas_size(event=None):
            try:
                if not label.winfo_exists():
                    return
                self.update_rounded_background(canvas, label, bg)
            except (tk.TclError, AttributeError):
                pass
        
        label.bind("<Configure>", update_canvas_size)
        parent.after(10, update_canvas_size)
        
        return canvas, label

    def show_overlay(self):
        if self.is_active:
            return

        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.config(bg=self.bg_color.get())
        
        container = tk.Frame(self.overlay, bg=self.bg_color.get())
        container.pack()
        
        self.overlay_canvas, self.overlay_label = self.create_rounded_corner_label(
            container,
            self.get_datetime_text(),
            (self.font_name.get(), int(self.font_size.get())),
            self.text_color.get(),
            self.bg_color.get(),
            self.overlay_padding,
            self.overlay_padding
        )
        self.overlay_canvas.pack()

        self._bind_drag_events()
        self._update_drag_cursor()

        try:
            self.overlay.after(
                50,
                lambda: (
                    self.overlay.attributes("-alpha", float(self.alpha.get())),
                    self.enable_click_through()
                )
            )
        except Exception:
            pass

        self.overlay.update_idletasks()
        self.position_overlay()
        self.overlay.after(100, self.enable_click_through)

        self.is_active = True
        lang = self.current_language.get()
        self.status_label.config(text=self.TRANSLATIONS[lang]["status_active"])
        self.status_label.config(fg="green")
        self.update_clock()

    def enable_click_through(self):
        if self.overlay is None or sys.platform != "win32":
            return

        try:
            import ctypes.wintypes as wintypes

            user32 = ctypes.windll.user32

            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_NOACTIVATE = 0x08000000

            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_FRAMECHANGED = 0x0020
            HWND_TOPMOST = -1

            # tkinter's winfo_id() returns the handle of the inner "content"
            # window, not the real top-level window that Windows manages.
            # Extended styles (click-through) only take effect when applied
            # to that real top-level window, so we resolve it via GetParent.
            user32.GetParent.restype = wintypes.HWND
            user32.GetParent.argtypes = [wintypes.HWND]

            child_hwnd = wintypes.HWND(self.overlay.winfo_id())
            hwnd = user32.GetParent(child_hwnd)
            if not hwnd:
                hwnd = child_hwnd

            # Use the pointer-sized variants so window handles are not
            # truncated on 64-bit Windows/Python.
            if ctypes.sizeof(ctypes.c_void_p) == 8:
                get_window_long = user32.GetWindowLongPtrW
                set_window_long = user32.SetWindowLongPtrW
            else:
                get_window_long = user32.GetWindowLongW
                set_window_long = user32.SetWindowLongW

            get_window_long.restype = ctypes.c_ssize_t
            get_window_long.argtypes = [wintypes.HWND, ctypes.c_int]
            set_window_long.restype = ctypes.c_ssize_t
            set_window_long.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]

            style = get_window_long(hwnd, GWL_EXSTYLE)
            style |= WS_EX_LAYERED | WS_EX_TOOLWINDOW

            if self.click_through_var.get():
                # Click-through ON: mouse clicks pass through to whatever is
                # underneath, and the window can't be dragged or focused.
                style |= WS_EX_TRANSPARENT | WS_EX_NOACTIVATE
            else:
                # Click-through OFF: the overlay accepts mouse input so it
                # can be dragged to a new position.
                style &= ~WS_EX_TRANSPARENT
                style &= ~WS_EX_NOACTIVATE

            set_window_long(hwnd, GWL_EXSTYLE, style)

            # NOTE: this call also controls the window's opacity (LWA_ALPHA).
            # It must be re-applied with the CURRENT slider value every time
            # this function runs (which happens after every settings change),
            # otherwise it silently resets the overlay back to fully opaque
            # and the Transparency slider stops having any visible effect.
            try:
                alpha_byte = int(round(float(self.alpha.get()) * 255))
            except Exception:
                alpha_byte = 255
            alpha_byte = max(0, min(255, alpha_byte))

            user32.SetLayeredWindowAttributes(
                hwnd,
                0,
                alpha_byte,
                0x02
            )

            user32.SetWindowPos(
                hwnd,
                HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED
            )
        except Exception:
            pass

    def position_overlay(self):
        if self.overlay is None:
            return

        try:
            self.overlay.update_idletasks()

            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()

            width = self.overlay.winfo_reqwidth()
            height = self.overlay.winfo_reqheight()
            margin = self.overlay_padding

            if self.manual_position and self._manual_x is not None and self._manual_y is not None:
                x = self._manual_x
                y = self._manual_y
                self.overlay.geometry(f"{width}x{height}+{x}+{y}")
                self.enable_click_through()
                return

            pos = self.POSITIONS.get(self.position.get(), "bottom_right")

            if pos == "top_left":
                x = margin
                y = margin
            elif pos == "top_center":
                x = (sw - width) // 2
                y = margin
            elif pos == "top_right":
                x = sw - width - margin
                y = margin
            elif pos == "bottom_left":
                x = margin
                y = sh - height - margin
            elif pos == "bottom_center":
                x = (sw - width) // 2
                y = sh - height - margin
            else:
                x = sw - width - margin
                y = sh - height - margin

            self.overlay.geometry(f"{width}x{height}+{x}+{y}")
            self.enable_click_through()
        except (tk.TclError, AttributeError):
            pass

    def refresh_overlay(self):
        if self.overlay is None or not self.is_active or self.is_refreshing:
            return

        self.is_refreshing = True
        try:
            if not self.overlay.winfo_exists():
                return

            bg_color = self.bg_color.get()
            text_color = self.text_color.get()
            font_name = self.font_name.get()
            font_size = int(self.font_size.get())
            margin = self.overlay_padding
            current_text = self.get_datetime_text()

            if hasattr(self, 'overlay_label') and self.overlay_label:
                try:
                    self.overlay_label.config(
                        text=current_text,
                        font=(font_name, font_size),
                        fg=text_color,
                        bg=bg_color,
                        padx=margin,
                        pady=margin
                    )
                    
                    if hasattr(self, 'overlay_canvas') and self.overlay_canvas:
                        self.update_rounded_background(
                            self.overlay_canvas, 
                            self.overlay_label, 
                            bg_color
                        )
                    
                    self.overlay.configure(bg=bg_color)
                    self.position_overlay()
                    
                    try:
                        self.overlay.attributes("-alpha", float(self.alpha.get()))
                    except Exception:
                        pass
                        
                except Exception:
                    self._recreate_overlay()
                
        except (tk.TclError, AttributeError):
            pass
        finally:
            self.is_refreshing = False

    def _recreate_overlay(self):
        try:
            bg_color = self.bg_color.get()
            text_color = self.text_color.get()
            font_name = self.font_name.get()
            font_size = int(self.font_size.get())
            margin = self.overlay_padding
            current_text = self.get_datetime_text()
            
            if hasattr(self, 'overlay_canvas') and self.overlay_canvas:
                try:
                    self.overlay_canvas.destroy()
                except:
                    pass
            
            container = tk.Frame(self.overlay, bg=bg_color)
            container.pack()
            
            self.overlay_canvas, self.overlay_label = self.create_rounded_corner_label(
                container,
                current_text,
                (font_name, font_size),
                text_color,
                bg_color,
                margin,
                margin
            )
            self.overlay_canvas.pack()

            self._bind_drag_events()

            self.overlay.configure(bg=bg_color)
            self.position_overlay()
            
            try:
                self.overlay.attributes("-alpha", float(self.alpha.get()))
            except Exception:
                pass
        except Exception:
            pass

    def update_clock(self):
        if self.overlay is None or not self.is_active:
            return

        try:
            if not self.overlay.winfo_exists():
                return

            if hasattr(self, 'overlay_label') and self.overlay_label:
                try:
                    self.overlay_label.config(text=self.get_datetime_text())
                    if hasattr(self, 'overlay_canvas') and self.overlay_canvas:
                        self.update_rounded_background(
                            self.overlay_canvas, 
                            self.overlay_label, 
                            self.bg_color.get()
                        )
                except:
                    pass

            self.timer_id = self.root.after(250, self.update_clock)
        except Exception:
            self.timer_id = None

    def hide_overlay(self):
        if not self.is_active:
            return

        if self.timer_id is not None:
            try:
                self.root.after_cancel(self.timer_id)
            except Exception:
                pass
            self.timer_id = None

        if self.overlay is not None:
            try:
                self.overlay.destroy()
            except Exception:
                pass

        self.overlay = None
        self.is_active = False
        
        lang = self.current_language.get()
        self.status_label.config(text=self.TRANSLATIONS[lang]["status_inactive"])
        self.status_label.config(fg="red")

    def close(self):
        """Completely terminate the application."""
        self.hide_overlay()
        try:
            self.root.destroy()
        except tk.TclError:
            pass


def main():
    root = tk.Tk()
    app = DateTimeOverlay(root)
    app.show_overlay()
    root.mainloop()


if __name__ == "__main__":
    main()