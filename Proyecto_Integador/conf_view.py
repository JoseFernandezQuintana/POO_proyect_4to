import customtkinter as ctk

# Definición de colores para consistencia (copiados de dashboard_view.py)
BLUE_HEADER = "#1A5276"

# Colores usados específicamente en ConfFrame para estilos de botón
LIGHT_GRAY_BG = "#F2F2F2"
HOVER_GRAY = "#E0E0E0"
DARK_GRAY_TEXT = "#333333"

ACCENT_RED_SOFT = "#FFF5F5"      # Fondo de Cerrar Sesión
ACCENT_RED_HOVER = "#FFD5D5"
TEXT_RED_DARK = "#C0392B"        # Texto de Cerrar Sesión

ACCENT_RED_INTENSE = "#FFCCCC"   # Fondo de Cerrar App
ACCENT_RED_HOVER_INTENSE = "#FFBBBB"
TEXT_RED_VERY_DARK = "#880000"   # Texto de Cerrar App


class ConfFrame(ctk.CTkFrame):
    """
    Panel lateral de configuración para el Dashboard.
    Contiene botones para Administración, Cotización, Cerrar Sesión y Cerrar App.
    """
    def __init__(self, master, handle_action_callback, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configuración del contenedor
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.configure(fg_color="white", corner_radius=15, border_color="#DDDDDD", border_width=1)
        
        self.handle_action_callback = handle_action_callback
        
        # Estilos compartidos para botones normales
        button_style = {
            "fg_color": LIGHT_GRAY_BG, 
            "hover_color": HOVER_GRAY, 
            "text_color": DARK_GRAY_TEXT, 
            "corner_radius": 8,
            "height": 35,
            "font": ctk.CTkFont(size=14, weight="bold")
        }

        # Título del Panel
        ctk.CTkLabel(
            self,
            text="Opciones de Configuración",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=BLUE_HEADER
        ).grid(row=0, column=0, pady=(15, 10), padx=15, sticky="ew")
        
        # 1. Administración de Cuentas
        ctk.CTkButton(
            self,
            text="Administración de Cuentas",
            command=lambda: self.handle_action_callback("Administración de Cuentas"),
            **button_style
        ).grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        # 2. Cotización de Servicios
        ctk.CTkButton(
            self,
            text="Cotización de Servicios",
            command=lambda: self.handle_action_callback("Cotización de Servicios"),
            **button_style
        ).grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        
        # Separador visual
        ctk.CTkFrame(self, height=1, fg_color="#E0E0E0").grid(
            row=3, column=0, sticky="ew", padx=15, pady=10
        )

        # 3. Cerrar Sesión
        ctk.CTkButton(
            self,
            text="🚪 Cerrar Sesión",
            command=lambda: self.handle_action_callback("🚪 Cerrar Sesión"),
            fg_color=ACCENT_RED_SOFT,
            hover_color=ACCENT_RED_HOVER,
            text_color=TEXT_RED_DARK,
            corner_radius=8,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        # 4. Cerrar App
        ctk.CTkButton(
            self,
            text="🛑 Cerrar App",
            command=lambda: self.handle_action_callback("🛑 Cerrar App"),
            fg_color=ACCENT_RED_INTENSE,
            hover_color=ACCENT_RED_HOVER_INTENSE,
            text_color=TEXT_RED_VERY_DARK,
            corner_radius=8,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=5, column=0, padx=15, pady=(5, 15), sticky="ew")