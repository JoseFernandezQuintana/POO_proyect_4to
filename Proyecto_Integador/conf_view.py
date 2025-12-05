import customtkinter as ctk

# Estilos
BLUE_HEADER = "#1A5276"
LIGHT_GRAY_BG = "#F2F2F2"
HOVER_GRAY = "#E0E0E0"
DARK_GRAY_TEXT = "#333333"
ACCENT_RED_SOFT = "#FFF5F5"
ACCENT_RED_HOVER = "#FFD5D5"
TEXT_RED_DARK = "#C0392B"

class ConfFrame(ctk.CTkFrame):
    # AÑADIMOS 'rol' AL CONSTRUCTOR
    def __init__(self, master, handle_action_callback, rol, **kwargs):
        super().__init__(master, **kwargs)
        self.handle_action_callback = handle_action_callback
        
        # Usamos el rol que nos pasan, es más seguro y directo
        self.rol_actual = rol 
        
        self.grid_columnconfigure(0, weight=1)
        self.configure(fg_color="white", corner_radius=15)

        ctk.CTkLabel(self, text="⚙️ Configuración", font=ctk.CTkFont(size=16, weight="bold"), text_color=BLUE_HEADER).pack(pady=(20, 10), padx=15, anchor="w")

        # --- GENERACIÓN DINÁMICA DE BOTONES ---
        opciones = [
            {"texto": "👤 Mi Perfil", "cmd": "Mi Perfil", "roles": ["Administrador", "Doctora", "Recepcionista"]},
            {"texto": "👥 Gestión de Usuarios", "cmd": "Administración de Cuentas", "roles": ["Administrador", "Doctora"]},
            {"texto": "🦷 Catálogo y Precios", "cmd": "Cotización de Servicios", "roles": ["Administrador", "Doctora", "Recepcionista"]},
            {"texto": "📊 Gráficas y KPIs", "cmd": "Gráficas y Estadísticas", "roles": ["Administrador"]}, 
        ]

        for op in opciones:
            if self.rol_actual in op["roles"]:
                self.crear_boton(op["texto"], op["cmd"])

        # Separador
        ctk.CTkFrame(self, height=1, fg_color="#E0E0E0").pack(fill="x", padx=15, pady=10)

        # Cerrar Sesión
        self.crear_boton("🚪 Cerrar Sesión", "🚪 Cerrar Sesión", es_rojo=True)
        self.crear_boton("🛑 Cerrar App", "🛑 Cerrar App", es_rojo=True)

    def crear_boton(self, texto, comando_str, es_rojo=False):
        color_fg = ACCENT_RED_SOFT if es_rojo else LIGHT_GRAY_BG
        color_hover = ACCENT_RED_HOVER if es_rojo else HOVER_GRAY
        color_text = TEXT_RED_DARK if es_rojo else DARK_GRAY_TEXT
        
        ctk.CTkButton(
            self, text=texto, 
            command=lambda: self.handle_action_callback(comando_str),
            fg_color=color_fg, hover_color=color_hover, text_color=color_text,
            corner_radius=8, height=40, font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(fill="x", padx=15, pady=5)