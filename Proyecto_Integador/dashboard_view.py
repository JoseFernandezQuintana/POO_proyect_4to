import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
import os
import sys 
from typing import Dict, Any, Union 

# Importar las vistas y controladores de las subsecciones
from agendar_view import AgendarCitaFrame
from mod_agendar_view import ModificarCitaFrame 
from calendario_view import CalendarFrame

# Intentar importar el controlador de autenticación
try:
    from auth_controller import validar_credenciales 
except ImportError:
    def validar_credenciales(*args): return True 

# --- CONFIGURACIÓN DE COLORES Y RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
BG_COLOR = "#F0F8FF"
WHITE_FRAME = "white"
BLUE_HEADER = "#1A5276"
ACCENT_BLUE = "#007BFF"

# Rutas de imágenes
LOGO_DASHBOARD_PATH = os.path.join(current_dir, "logo.jpg") 


class DashboardApp:
    def __init__(self, username, root):
        self.root = root
        self.username = username
        self.root.title(f"Dashboard | Bienvenido, {username}")
        self.root.geometry("1400x900") 
        self.root.configure(fg_color=BG_COLOR)

        self.root.grid_rowconfigure(2, weight=1) 
        self.root.grid_columnconfigure(0, weight=1)
        
        # Bandera que debe ser verificada por main.py 
        self.app_closed_completely = False 

        self.views_map: Dict[str, Any] = {
            "agendar": AgendarCitaFrame,
            "modificar": ModificarCitaFrame,
            "calendario": CalendarFrame
        }

        # 1. HEADER / BARRA SUPERIOR
        self.create_header()

        # 2. BARRA DE NAVEGACIÓN
        self.create_navigation_bar()

        # 3. Panel Desplegable de Configuración (Inicialización Oculta)
        self.create_settings_panel() # Se crea antes del contenido para que esté en un nivel superior (z-order)

        # 4. CONTENIDO PRINCIPAL 
        self.content_container = ctk.CTkFrame(self.root, fg_color=BG_COLOR)
        self.content_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=0)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        self.current_view = None
        self.show_view("agendar")

    
    def create_header(self):
        self.header_frame = ctk.CTkFrame(self.root, height=60, fg_color=BLUE_HEADER, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1) 
        self.header_frame.grid_columnconfigure(1, weight=0)

        # Logo y Título
        try:
            generic_logo_path = os.path.join(current_dir, "logo.jpg") 
            logo_img = ctk.CTkImage(Image.open(generic_logo_path).resize((40, 40)), size=(40, 40))
            logo_label = ctk.CTkLabel(self.header_frame, text=" Sistema de Gestión de Citas", 
                                             image=logo_img, compound="left", font=ctk.CTkFont(size=18, weight="bold"), 
                                             text_color="white")
            logo_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        except Exception:
            ctk.CTkLabel(self.header_frame, text="Sistema de Gestión de Citas", 
                          font=ctk.CTkFont(size=18, weight="bold"), text_color="white").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Contenedor de Hora, Configuración y Botón de Sesión
        right_header_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header_frame.grid(row=0, column=1, sticky="e", padx=20)
        
        # Horario de Atención
        ctk.CTkLabel(
            right_header_frame,
            text=" 🕒 Lunes - Sábado: 11:00 AM - 8:00 PM",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20)
        
        # --- BOTÓN DE CONFIGURACIÓN (Reemplazo del OptionMenu) ---
        self.config_button = ctk.CTkButton(
            right_header_frame,
            text="⚙️ Configuración",
            width=180, # Aumento el ancho para que coincida con el panel
            height=35,
            corner_radius=10,
            fg_color="#FFFFFF",
            text_color=BLUE_HEADER,
            hover_color="#D9EFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.toggle_settings_panel
        )
        self.config_button.pack(side="left", padx=10)
        
    def create_settings_panel(self):
        """Crea el panel desplegable de configuración que se muestra/oculta."""
        
        # Panel desplegable de configuración (oculto al inicio)
        self.settings_panel = ctk.CTkFrame(
            self.root, 
            fg_color="white", 
            corner_radius=10,
            # Agregamos un borde sutil para destacarlo
            border_color="#DDDDDD",
            border_width=1
        )
        self.settings_panel_visible = False
        
        # Botones dentro del panel
        
        # Administración de Cuentas
        ctk.CTkButton(
            self.settings_panel,
            text="Administración de Cuentas",
            command=lambda: self.handle_config_action("Administración de Cuentas"),
            fg_color="#F2F2F2",
            hover_color="#E0E0E0",
            text_color="#333333",
            corner_radius=8
        ).pack(fill="x", padx=10, pady=(10, 5))

        # Cotización de Servicios
        ctk.CTkButton(
            self.settings_panel,
            text="Cotización de Servicios",
            command=lambda: self.handle_config_action("Cotización de Servicios"),
            fg_color="#F2F2F2",
            hover_color="#E0E0E0",
            text_color="#333333",
            corner_radius=8
        ).pack(fill="x", padx=10, pady=5)
        
        # Separador visual
        ctk.CTkFrame(self.settings_panel, height=1, fg_color="#E0E0E0").pack(fill="x", padx=10, pady=5)

        # Cerrar Sesión
        ctk.CTkButton(
            self.settings_panel,
            text="🚪 Cerrar Sesión",
            command=lambda: self.handle_config_action("🚪 Cerrar Sesión"),
            fg_color="#FFF5F5", # Color suave de alerta
            hover_color="#FFD5D5",
            text_color="#C0392B", # Rojo oscuro para contraste
            corner_radius=8
        ).pack(fill="x", padx=10, pady=5)

        # Cerrar App
        ctk.CTkButton(
            self.settings_panel,
            text="🛑 Cerrar App",
            command=lambda: self.handle_config_action("🛑 Cerrar App"),
            fg_color="#FFCCCC", # Rojo más intenso
            hover_color="#FFBBBB",
            text_color="#880000",
            corner_radius=8
        ).pack(fill="x", padx=10, pady=(5, 10))


    def toggle_settings_panel(self):
        """Muestra u oculta el panel de configuración personalizado."""
        if self.settings_panel_visible:
            # Ocultar
            self.settings_panel.place_forget()
            self.settings_panel_visible = False
        else:
            # Mostrar: Ubicar debajo y alineado a la derecha del botón
            
            # 1. Obtener coordenadas absolutas del botón
            btn_x_root = self.config_button.winfo_rootx()
            btn_y_root = self.config_button.winfo_rooty()
            btn_width = self.config_button.winfo_width()
            
            # 2. Obtener coordenadas absolutas de la ventana principal
            root_x = self.root.winfo_rootx()
            root_y = self.root.winfo_rooty()
            
            # 3. Calcular la posición relativa (x, y) para 'place'
            # x: Alineado a la derecha del botón
            panel_width = 180 # Coincidir con el ancho del botón
            x_pos = (btn_x_root - root_x) + btn_width - panel_width
            
            # y: Debajo del botón (+ 40 es la altura aproximada de la barra)
            y_pos = (btn_y_root - root_y) + self.config_button.winfo_height() + 5
            
            self.settings_panel.place(x=x_pos, y=y_pos, width=panel_width)
            self.settings_panel_visible = True

    def create_navigation_bar(self):
        self.nav_frame = ctk.CTkFrame(self.root, fg_color=BG_COLOR)
        self.nav_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 5))
        
        self.nav_buttons_frame = ctk.CTkFrame(self.nav_frame, fg_color=WHITE_FRAME, corner_radius=18, height=40, border_color="#DDDDDD", border_width=1)
        self.nav_buttons_frame.pack(padx=20, pady=10, anchor="n")
        
        # Botones de navegación (Agendar, Modificar, Calendario)
        self.btn_agendar = ctk.CTkButton(
            self.nav_buttons_frame,
            text=" 📅 Agendar Cita",
            command=lambda: self.show_view("agendar"),
            width=150, height=35, corner_radius=18, fg_color=ACCENT_BLUE, hover_color="#3A82D0", text_color="white", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_agendar.pack(side="left", padx=5, pady=2)
        
        self.btn_modificar = ctk.CTkButton(
            self.nav_buttons_frame,
            text=" ✏️ Modificar Citas",
            command=lambda: self.show_view("modificar"),
            width=150, height=35, corner_radius=18, fg_color="transparent", hover_color="#F0F0F0", text_color="#333333", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_modificar.pack(side="left", padx=5, pady=2)
        
        self.btn_calendario = ctk.CTkButton(
            self.nav_buttons_frame,
            text=" 🗓️ Calendario",
            command=lambda: self.show_view("calendario"),
            width=150, height=35, corner_radius=18, fg_color="transparent", hover_color="#F0F0F0", text_color="#333333", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_calendario.pack(side="left", padx=5, pady=2)


    def show_view(self, view_name):
        if self.current_view:
            self.current_view.destroy()
            
        self.btn_agendar.configure(fg_color="transparent", text_color="#333333")
        self.btn_modificar.configure(fg_color="transparent", text_color="#333333") 
        self.btn_calendario.configure(fg_color="transparent", text_color="#333333")

        active_button = None
        if view_name == "agendar":
            active_button = self.btn_agendar
        elif view_name == "modificar":
            active_button = self.btn_modificar
        elif view_name == "calendario":
            active_button = self.btn_calendario
            
        if active_button:
            active_button.configure(fg_color=ACCENT_BLUE, text_color="white")
            
        ViewClass = self.views_map.get(view_name)
        if ViewClass:
            self.current_view = ViewClass(self.content_container)
            self.current_view.pack(fill="both", expand=True)
            
    # Función de acción principal (con modificación para ocultar el panel)
    def handle_config_action(self, choice):
        """Maneja la acción seleccionada en el menú de Configuración y oculta el panel."""
        
        # Ocultar el panel después de la selección
        if self.settings_panel_visible:
            self.settings_panel.place_forget()
            self.settings_panel_visible = False
            
        should_close = False
        
        if choice == "Administración de Cuentas":
            messagebox.showinfo("Configuración", "Abriendo panel de Administración de Cuentas...")
        elif choice == "Cotización de Servicios":
            messagebox.showinfo("Configuración", "Abriendo herramienta de Cotización de Servicios...")
        elif choice == "🚪 Cerrar Sesión":
            self.logout()
            should_close = True 
        elif choice == "🛑 Cerrar App":
            self.close_app()
            should_close = True 
        
        # Nota: La línea 'if not should_close: self.config_menu.set("⚙️ Configuración")'
        # ya no es necesaria porque el botón ahora es un CTkButton simple y su texto no cambia.

    def logout(self):
        """Cierra la ventana del Dashboard para regresar a la vista de Login (manejado en main.py)."""
        confirm = messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que quieres cerrar la sesión y regresar a la pantalla de inicio de sesión?")
        if confirm:
            # Solo destruimos la ventana. El flujo en main.py detectará esto y relanzará el Login.
            self.root.destroy() 
            
    def close_app(self):
        """Cierra la aplicación por completo usando sys.exit() para asegurar el fin del proceso."""
        confirm = messagebox.askyesno("Cerrar Aplicación", "¿Estás seguro de que quieres cerrar la aplicación por completo?")
        if confirm:
            self.app_closed_completely = True # Bandera para que main.py sepa que debe terminar.
            self.root.destroy()
            sys.exit() # Forzamos la salida para no necesitar doble clic
            