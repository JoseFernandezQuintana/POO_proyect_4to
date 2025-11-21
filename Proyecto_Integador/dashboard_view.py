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
# Importar la nueva vista de configuración
from conf_view import ConfFrame 

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

# --- PLACEHOLDER DE ConfFrame ELIMINADO ---
# Se elimina la clase ConfFrame de placeholder.


class DashboardApp:
    def __init__(self, username, root):
        self.root = root
        self.username = username
        self.root.title(f"Dashboard | Bienvenido, {username}")
        self.root.geometry("1400x900") 
        self.root.configure(fg_color=BG_COLOR)

        self.root.grid_rowconfigure(2, weight=1) 
        
        # Configurar las dos columnas para la fila 2 (Contenido Principal y Sidebar de Configuración)
        self.root.grid_columnconfigure(0, weight=1) # Columna 0: Contenido principal, expande
        self.root.grid_columnconfigure(1, weight=0) # Columna 1: Configuración, no expande
        
        # Bandera que debe ser verificada por main.py 
        self.app_closed_completely = False 

        self.views_map: Dict[str, Any] = {
            "agendar": AgendarCitaFrame,
            "modificar": ModificarCitaFrame,
            "calendario": CalendarFrame
        }
        
        self.config_sidebar_visible = False

        # 1. HEADER / BARRA SUPERIOR
        self.create_header()

        # 2. BARRA DE NAVEGACIÓN
        self.create_navigation_bar()

        # 3. Panel Lateral de Configuración (Creación inicial)
        self.create_config_sidebar() 

        # 4. CONTENIDO PRINCIPAL (Se ubica en la columna 0, fila 2)
        self.content_container = ctk.CTkFrame(self.root, fg_color=BG_COLOR)
        self.content_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=0)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        self.current_view = None
        self.show_view("agendar")

    
    def create_header(self):
        self.header_frame = ctk.CTkFrame(self.root, height=60, fg_color=BLUE_HEADER, corner_radius=0)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew") # Ocupa ambas columnas
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
        
        # --- BOTÓN DE CONFIGURACIÓN (Activa el sidebar) ---
        self.config_button = ctk.CTkButton(
            right_header_frame,
            text="⚙️ Configuración",
            width=180, 
            height=35,
            corner_radius=10,
            fg_color="#FFFFFF",
            text_color=BLUE_HEADER,
            hover_color="#D9EFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.toggle_config_sidebar # Llama al nuevo método
        )
        self.config_button.pack(side="left", padx=10)
        
    def create_config_sidebar(self):
        """Crea el frame del panel lateral de configuración."""
        # Se inicializa, pero no se coloca en la cuadrícula hasta que se togglee.
        # Usa la clase importada ConfFrame
        self.config_frame = ConfFrame(
            self.root, 
            handle_action_callback=self.handle_config_action, 
            width=250 # Ancho fijo para el sidebar
        )
        
    def toggle_config_sidebar(self):
        """Muestra u oculta el panel lateral de configuración, ajustando la cuadrícula."""
        if self.config_sidebar_visible:
            # OCULTAR: Eliminar el sidebar de la cuadrícula y permitir que el contenido principal expanda.
            self.config_frame.grid_forget()
            self.config_sidebar_visible = False
            
            # Restaurar el grid: Columna 0 (contenido) ocupa todo el ancho.
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_columnconfigure(1, weight=0) # Asegura que la columna 1 no exista

        else:
            # MOSTRAR: Colocar el sidebar en la columna 1.
            self.config_frame.grid(row=2, column=1, sticky="nsew", padx=(0, 20), pady=0)
            self.config_sidebar_visible = True
            
            # Ajustar el grid: Columna 0 (contenido) sigue expandiendo, Columna 1 es fija.
            # El padding del content_container (padx=20) se ajusta automáticamente.
            self.root.grid_columnconfigure(1, weight=0) # Columna de la configuración no expande.

        # Asegura que el content_container ocupe la columna 0.
        # Esto es importante para el caso de ocultar (donde debe rellenar el espacio).
        self.content_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=0)


    def create_navigation_bar(self):
        self.nav_frame = ctk.CTkFrame(self.root, fg_color=BG_COLOR)
        # La barra de navegación debe ocupar ambas columnas si la configuración está visible
        self.nav_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 5)) 
        
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
        # Oculta el sidebar de configuración si estaba visible al cambiar de vista principal
        if self.config_sidebar_visible:
            self.toggle_config_sidebar() 
            
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
            # Asegura que la vista se muestre dentro del content_container
            self.current_view = ViewClass(self.content_container)
            self.current_view.pack(fill="both", expand=True)
            
    # Función de acción principal (ahora llamada desde ConfFrame)
    def handle_config_action(self, choice):
        """Maneja la acción seleccionada en el menú de Configuración y oculta el panel (si procede)."""
        
        # Ocultar el panel después de la selección, a menos que la acción sea cerrar la app/sesión
        if self.config_sidebar_visible and choice not in ["🚪 Cerrar Sesión", "🛑 Cerrar App"]:
            self.toggle_config_sidebar() 
            
        should_close = False
        
        if choice == "Administración de Cuentas":
            from conf_user_view import UserAdminWindow
            UserAdminWindow(self.root)
        elif choice == "Cotización de Servicios":
            messagebox.showinfo("Configuración", "Abriendo herramienta de Cotización de Servicios...")
        elif choice == "🚪 Cerrar Sesión":
            self.logout()
            should_close = True 
        elif choice == "🛑 Cerrar App":
            self.close_app()
            should_close = True 

    def logout(self):
        """Cierra la ventana del Dashboard para regresar a la vista de Login (manejado en main.py)."""
        confirm = messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que quieres cerrar la sesión y regresar a la pantalla de inicio de sesión?")
        if confirm:
            self.root.destroy() 
            
    def close_app(self):
        """Cierra la aplicación por completo usando sys.exit() para asegurar el fin del proceso."""
        confirm = messagebox.askyesno("Cerrar Aplicación", "¿Estás seguro de que quieres cerrar la aplicación por completo?")
        if confirm:
            self.app_closed_completely = True # Bandera para que main.py sepa que debe terminar.
            self.root.destroy()
            sys.exit()

