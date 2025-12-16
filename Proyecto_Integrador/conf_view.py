import customtkinter as ctk

# Estilos
BLUE_HEADER = "#1A5276"
HOVER_GRAY = "#E0E0E0"
DARK_GRAY_TEXT = "#333333"
ACCENT_RED_SOFT = "#FFF5F5"
ACCENT_RED_HOVER = "#FFD5D5"
TEXT_RED_DARK = "#C0392B"

class ConfFrame(ctk.CTkFrame):
    def __init__(self, master, handle_action_callback, rol, **kwargs):
        super().__init__(master, **kwargs)
        self.handle_action_callback = handle_action_callback
        self.rol_actual = rol 
        
        # Panel lateral de configuración
        self.configure(fg_color="white", corner_radius=0, width=280, border_width=1, border_color="#D5DBDB")
        
        # Contenedor principal
        main_col = ctk.CTkFrame(self, fg_color="transparent")
        main_col.pack(side="left", fill="both", expand=True, padx=15, pady=20)

        ctk.CTkLabel(main_col, text="⚙️ Configuración", font=("Segoe UI", 16, "bold"), text_color=BLUE_HEADER).pack(pady=(5, 20), anchor="w")

        opciones = [
            {"texto": "👤 Mi Perfil", "cmd": "Mi Perfil", "roles": ["Administrador", "Doctora", "Recepcionista"]},
            {"texto": "👥 Gestión de Usuarios", "cmd": "Administración de Cuentas", "roles": ["Administrador", "Doctora", "Recepcionista"]}, 
            {"texto": "🦷 Catálogo y Precios", "cmd": "Cotización de Servicios", "roles": ["Administrador", "Doctora", "Recepcionista"]}, 
            {"texto": "📊 Reportes y Estadisticas", "cmd": "Reportes y Estadisticas", "roles": ["Administrador", "Doctora", "Recepcionista"]},
        ]

        for op in opciones:
            if self.rol_actual in op["roles"]:
                self.crear_boton(main_col, op["texto"], op["cmd"])

        ctk.CTkFrame(main_col, height=1, fg_color="#E0E0E0").pack(fill="x", pady=15)

        self.crear_boton(main_col, "🚪 Cerrar Sesión", "Cerrar Sesión", es_rojo=True)
        self.crear_boton(main_col, "🛑 Cerrar App", "Cerrar App", es_rojo=True)

    def crear_boton(self, parent, texto, comando_str, es_rojo=False):
        color_fg = ACCENT_RED_SOFT if es_rojo else "transparent"
        color_hover = ACCENT_RED_HOVER if es_rojo else HOVER_GRAY
        color_text = TEXT_RED_DARK if es_rojo else DARK_GRAY_TEXT
        
        btn = ctk.CTkButton(
            parent, text=texto, 
            command=lambda: self.handle_action_callback(comando_str),
            fg_color=color_fg, 
            hover_color=color_hover, 
            text_color=color_text,
            corner_radius=6, 
            height=40, 
            font=("Segoe UI", 13), 
            anchor="w"
        )
        btn.pack(fill="x", pady=3)
