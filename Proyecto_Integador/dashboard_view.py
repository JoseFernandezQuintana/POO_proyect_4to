import customtkinter as ctk
from tkinter import messagebox
import os
import sys 
from typing import Dict, Any

# --- IMPORTACIÓN DE VISTAS PRINCIPALES ---
from agendar_view import AgendarCitaFrame
from mod_agendar_view import ModificarCitaFrame 
from calendario_view import CalendarFrame
from pagos_view import PagosFrame

# --- IMPORTACIÓN DE VISTAS DE CONFIGURACIÓN/ADMIN ---
from conf_view import ConfFrame 
from admin_usuarios_view import AdminUsuariosFrame
from admin_servicios_view import AdminServiciosFrame
from admin_reportes_view import AdminReportesFrame
from profile_view import ProfileFrame

# --- CONFIGURACIÓN DE COLORES Y RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
BG_COLOR = "#F0F8FF"
WHITE_FRAME = "white"
BLUE_HEADER = "#1A5276"
ACCENT_BLUE = "#007BFF"

class DashboardApp:
    def __init__(self, username, rol, root):
        self.root = root
        self.username = username
        self.rol = rol  

        # --- CORRECCIÓN VITAL: INYECTAR DATOS EN LA VENTANA RAÍZ ---
        # Esto permite que las vistas (como AdminUsuarios) accedan a self.master.master.rol
        self.root.rol = rol
        self.root.username = username
        
        self.root.title(f"Dashboard | {rol} : {username}")
        
        # Intentar maximizar
        try:
            self.root.state('zoomed')
        except:
            self.root.geometry("1400x900")
            
        self.root.configure(fg_color=BG_COLOR)

        # --- CONFIGURACIÓN DE LA GRILLA PRINCIPAL (LAYOUT) ---
        self.root.grid_rowconfigure(2, weight=1) 
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0) 
        
        self.app_closed_completely = False 

        # Mapa de Vistas Principales
        self.views_map: Dict[str, Any] = {
            "agendar": AgendarCitaFrame,
            "modificar": ModificarCitaFrame,
            "calendario": CalendarFrame,
            "pagos": PagosFrame
        }

        # 1. HEADER
        self.create_header()

        # 2. BARRA DE NAVEGACIÓN
        self.create_navigation_bar()

        # 3. CONTENIDO PRINCIPAL
        self.content_container = ctk.CTkFrame(self.root, fg_color=BG_COLOR)
        self.content_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=0)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        # 4. CAPA DE CONFIGURACIÓN
        self.config_panel = None
        self.click_listener_id = None

        # 5. CAPA DE CARGA
        self.loading_overlay = None

        self.current_view = None
        # Iniciamos
        self.show_view_with_loading("agendar")

    # --------------------------------------------------------------------------
    # SISTEMA DE "CARGANDO..."
    # --------------------------------------------------------------------------
    def show_loading(self, mensaje="Cargando..."):
        if self.loading_overlay: return 

        self.loading_overlay = ctk.CTkFrame(self.root, fg_color=("gray90", "gray10"), corner_radius=0)
        self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        center_frame = ctk.CTkFrame(self.loading_overlay, fg_color=WHITE_FRAME, corner_radius=15, border_width=2, border_color=ACCENT_BLUE)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(center_frame, text="⏳", font=("Arial", 40)).pack(padx=20, pady=(20, 10))
        ctk.CTkLabel(center_frame, text=mensaje, font=("Arial", 16, "bold"), text_color=BLUE_HEADER).pack(padx=40, pady=(0, 20))
        self.root.update_idletasks()

    def hide_loading(self):
        if self.loading_overlay:
            self.loading_overlay.destroy()
            self.loading_overlay = None

    def show_view_with_loading(self, view_name):
        self.show_loading(f"Cargando módulo {view_name}...")
        self.root.after(50, lambda: self._execute_show_view(view_name))

    def _execute_show_view(self, view_name):
        try:
            self.show_view(view_name)
        except Exception as e:
            messagebox.showerror("Error Crítico", f"No se pudo cargar la vista: {e}")
        finally:
            self.hide_loading()

    # --------------------------------------------------------------------------
    # COMPONENTES VISUALES
    # --------------------------------------------------------------------------
    def create_header(self):
        self.header_frame = ctk.CTkFrame(self.root, height=60, fg_color=BLUE_HEADER, corner_radius=0)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1) 
        self.header_frame.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            self.header_frame, 
            text=" Sistema de Gestión de Citas", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="white"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        right_header_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header_frame.grid(row=0, column=1, sticky="e", padx=20)
        
        ctk.CTkLabel(
            right_header_frame,
            text=f"👤 {self.username} ({self.rol})",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20)
        
        self.btn_config = ctk.CTkButton(
            right_header_frame,
            text="⚙️ Configuración",
            command=self.toggle_config_panel,
            width=140, 
            fg_color="#D9EFFF",
            text_color=BLUE_HEADER,
            hover_color="white",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_config.pack(side="left", padx=10)

    def create_navigation_bar(self):
        self.nav_frame = ctk.CTkFrame(self.root, fg_color=BG_COLOR)
        self.nav_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(15, 5))
        
        self.nav_buttons_frame = ctk.CTkFrame(
            self.nav_frame, 
            fg_color=WHITE_FRAME, 
            corner_radius=25, 
            height=60, 
            border_color="#D0D0D0", 
            border_width=1
        )
        self.nav_buttons_frame.pack(anchor="n", padx=20, pady=5)

        self.nav_buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="group1")
        self.nav_buttons_frame.grid_rowconfigure(0, weight=1)

        btn_config = {
            "height": 40, "corner_radius": 15, "font": ctk.CTkFont(size=14, weight="bold"),
            "fg_color": "transparent", "text_color": "#555555", "hover_color": "#E8F0FE"
        }

        self.btn_agendar = ctk.CTkButton(self.nav_buttons_frame, text="📅 Agendar Cita", command=lambda: self.show_view_with_loading("agendar"), **btn_config)
        self.btn_agendar.grid(row=0, column=0, padx=5, pady=8, sticky="ew")
        
        self.btn_modificar = ctk.CTkButton(self.nav_buttons_frame, text="✏️ Modificar", command=lambda: self.show_view_with_loading("modificar"), **btn_config)
        self.btn_modificar.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        self.btn_calendario = ctk.CTkButton(self.nav_buttons_frame, text="🗓️ Calendario", command=lambda: self.show_view_with_loading("calendario"), **btn_config)
        self.btn_calendario.grid(row=0, column=2, padx=5, pady=8, sticky="ew")

        self.btn_pagos = ctk.CTkButton(self.nav_buttons_frame, text="💰 Caja / Pagos", command=lambda: self.show_view_with_loading("pagos"), **btn_config)
        self.btn_pagos.grid(row=0, column=3, padx=5, pady=8, sticky="ew")

    def show_view(self, view_name):
        self.close_config_panel() 

        if self.current_view:
            self.current_view.destroy()
            
        for btn in [self.btn_agendar, self.btn_modificar, self.btn_calendario, self.btn_pagos]:
            btn.configure(fg_color="transparent", text_color="#555555", border_width=0)

        active_button = None
        if view_name == "agendar": active_button = self.btn_agendar
        elif view_name == "modificar": active_button = self.btn_modificar
        elif view_name == "calendario": active_button = self.btn_calendario
        elif view_name == "pagos": active_button = self.btn_pagos
            
        if active_button:
            active_button.configure(fg_color=ACCENT_BLUE, text_color="white")
            
        ViewClass = self.views_map.get(view_name)
        if ViewClass:
            self.current_view = ViewClass(self.content_container)
            self.current_view.pack(fill="both", expand=True)

    # --------------------------------------------------------------------------
    # LÓGICA DE CONFIGURACIÓN
    # --------------------------------------------------------------------------
    def toggle_config_panel(self):
        if self.config_panel:
            self.close_config_panel()
            return

        # Creamos el panel pasando el rol explícitamente
        self.config_panel = ConfFrame(
            self.root, 
            handle_action_callback=self.handle_config_action,
            rol=self.rol, # <--- SE PASA EL ROL AQUÍ
            width=300
        )
        
        self.config_panel.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=0, pady=0)
        self.click_listener_id = self.root.bind_all("<Button-1>", self.check_click_outside, add="+")

    def check_click_outside(self, event):
        if self.config_panel:
            widget = event.widget
            try:
                if widget == self.btn_config: return
                if str(self.config_panel) in str(widget): return
                self.close_config_panel()
            except: pass

    def close_config_panel(self):
        if self.config_panel:
            self.config_panel.destroy()
            self.config_panel = None
        
        if self.click_listener_id:
            try: self.root.unbind_all("<Button-1>")
            except: pass
            self.click_listener_id = None

    def handle_config_action(self, choice):
        self.close_config_panel()
        
        # Resetear navegación visual
        for btn in [self.btn_agendar, self.btn_modificar, self.btn_calendario, self.btn_pagos]:
            btn.configure(fg_color="transparent", text_color="#555555")
        
        if self.current_view: self.current_view.destroy()

        # Enrutamiento
        if choice == "Mi Perfil":
            self.current_view = ProfileFrame(self.content_container)
            self.current_view.pack(fill="both", expand=True)

        elif choice == "Administración de Cuentas":
            if self.rol not in ["Administrador", "Doctora"]:
                messagebox.showerror("Acceso Denegado", "No tienes permisos suficientes.")
                self.show_view_with_loading("agendar")
            else:
                self.current_view = AdminUsuariosFrame(self.content_container)
                self.current_view.pack(fill="both", expand=True)
                
        elif choice == "Cotización de Servicios":
            self.current_view = AdminServiciosFrame(self.content_container)
            self.current_view.pack(fill="both", expand=True)
            
        elif choice in ["Gráficas y Estadísticas", "Reportes Financieros"]:
            if self.rol != "Administrador":
                 messagebox.showerror("Acceso Denegado", "Solo Administradores.")
            else:
                self.current_view = AdminReportesFrame(self.content_container)
                self.current_view.pack(fill="both", expand=True)

        elif choice == "🚪 Cerrar Sesión":
            self.logout()
            
        elif choice == "🛑 Cerrar App":
            self.close_app()

    def logout(self):
        confirm = messagebox.askyesno("Cerrar Sesión", "¿Seguro que quieres salir?")
        if confirm:
            self.show_loading("Cerrando sesión...")
            self.root.after(1000, lambda: self.root.destroy())
            
    def close_app(self):
        confirm = messagebox.askyesno("Cerrar Aplicación", "¿Salir completamente del sistema?")
        if confirm:
            self.app_closed_completely = True
            self.root.destroy()
            sys.exit()
