# dashboard_view.py
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
import os
import sys 

# Importar las vistas y controladores de las subsecciones
from agendar_view import AgendarCitaFrame
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

        # Se configura solo hasta la fila 2 (donde va el contenido)
        self.root.grid_rowconfigure(2, weight=1) 
        self.root.grid_columnconfigure(0, weight=1)

        # 1. HEADER / BARRA SUPERIOR
        self.create_header()

        # 2. BARRA DE NAVEGACIÓN
        self.create_navigation_bar()

        # 3. CONTENIDO PRINCIPAL 
        self.content_container = ctk.CTkFrame(self.root, fg_color=BG_COLOR)
        # El contenido ocupa la fila 2
        self.content_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=0)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # 4. FOOTER / PIE DE PÁGINA: ELIMINADO PARA SIMPLIFICAR LA ESTÉTICA
        
        self.current_view = None
        self.show_view("agendar")

    # ... (El resto de los métodos create_header, create_navigation_bar, show_view, logout se mantienen) ...
    # NOTA: El método create_footer ha sido eliminado de esta clase.
    
    def create_header(self):
        # ... (Método sin cambios) ...
        self.header_frame = ctk.CTkFrame(self.root, height=60, fg_color=BLUE_HEADER, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1) 
        self.header_frame.grid_columnconfigure(1, weight=0)

        # Logo y Título
        try:
            # Intentar cargar una imagen genérica para evitar el error si 'logo.jpg' no existe
            generic_logo_path = os.path.join(current_dir, "logo.jpg") 
            logo_img = ctk.CTkImage(Image.open(generic_logo_path).resize((40, 40)), size=(40, 40))
            logo_label = ctk.CTkLabel(self.header_frame, text=" Sistema de Gestión de Citas", 
                                      image=logo_img, compound="left", font=ctk.CTkFont(size=18, weight="bold"), 
                                      text_color="white")
            logo_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        except Exception:
            ctk.CTkLabel(self.header_frame, text="Sistema de Gestión de Citas", 
                         font=ctk.CTkFont(size=18, weight="bold"), text_color="white").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Contenedor de Hora y Botón
        right_header_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header_frame.grid(row=0, column=1, sticky="e", padx=20)
        
        # Horario de Atención
        ctk.CTkLabel(
            right_header_frame,
            text=" 🕒 Lunes - Sábado: 11:00 AM - 8:00 PM",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20)
        
        # Botón Cerrar Sesión
        ctk.CTkButton(
            right_header_frame, 
            text=" 🚪 Cerrar Sesión", 
            command=self.logout, 
            fg_color="#D9EFFF", hover_color="#FFFFFF", text_color=BLUE_HEADER, 
            font=ctk.CTkFont(size=14, weight="bold"), corner_radius=10
        ).pack(side="left")


    def create_navigation_bar(self):
        # ... (Método sin cambios) ...
        self.nav_frame = ctk.CTkFrame(self.root, fg_color=BG_COLOR)
        self.nav_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 5))
        
        self.nav_buttons_frame = ctk.CTkFrame(self.nav_frame, fg_color=WHITE_FRAME, corner_radius=18, height=40, border_color="#DDDDDD", border_width=1)
        self.nav_buttons_frame.pack(padx=20, pady=10, anchor="n")
        
        # Botón Agendar Cita
        self.btn_agendar = ctk.CTkButton(
            self.nav_buttons_frame,
            text=" 📅 Agendar Cita",
            command=lambda: self.show_view("agendar"),
            width=150, height=35, corner_radius=18, fg_color=ACCENT_BLUE, hover_color="#3A82D0", text_color="white", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_agendar.pack(side="left", padx=5, pady=2)
        
        # Botón Calendario
        self.btn_calendario = ctk.CTkButton(
            self.nav_buttons_frame,
            text=" 🗓️ Calendario",
            command=lambda: self.show_view("calendario"),
            width=150, height=35, corner_radius=18, fg_color="transparent", hover_color="#F0F0F0", text_color="#333333", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_calendario.pack(side="left", padx=5, pady=2)


    def show_view(self, view_name):
        # ... (Método sin cambios) ...
        if self.current_view:
            self.current_view.destroy()
            
        # Actualizar colores de los botones
        if view_name == "agendar":
            self.btn_agendar.configure(fg_color=ACCENT_BLUE, text_color="white")
            self.btn_calendario.configure(fg_color="transparent", text_color="#333333")
            self.current_view = AgendarCitaFrame(self.content_container)
        elif view_name == "calendario":
            self.btn_agendar.configure(fg_color="transparent", text_color="#333333")
            self.btn_calendario.configure(fg_color=ACCENT_BLUE, text_color="white")
            self.current_view = CalendarFrame(self.content_container)
            
        self.current_view.pack(fill="both", expand=True)

    def logout(self):
        # ... (Método sin cambios) ...
        confirm = messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que quieres cerrar la sesión?")
        if confirm:
            self.root.destroy()
    
    # --- Nuevo Método para el Footer Compacto ---
    def create_compact_footer(self):
        """Crea un pie de página minimalista que no interfiere con el contenido."""
        
        # El footer ocupa la Fila 3, asegurando que el Contenido (Fila 2) tenga prioridad.
        self.footer_frame = ctk.CTkFrame(self.root, height=30, fg_color=WHITE_FRAME, corner_radius=0, border_width=1, border_color="#DDDDDD")
        self.footer_frame.grid(row=3, column=0, sticky="ew")
        self.footer_frame.grid_columnconfigure(0, weight=1) # Columna del centro

        # Frame interno para contener la información y usar padding
        inner_footer = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        inner_footer.pack(fill="both", padx=20, pady=5)
        
        # 1. Copyright (Izquierda)
        ctk.CTkLabel(
            inner_footer,
            text="© 2025 Ortho Guzmán. Todos los derechos reservados.",
            font=ctk.CTkFont(size=11),
            text_color="#AAAAAA"
        ).pack(side="left", padx=(0, 20))
        
        # 2. Información de Contacto (Derecha)
        ctk.CTkLabel(
            inner_footer,
            text="📞 (871) 555-1234 | 📧 info@orthoguzman.com",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6B6B6B"
        ).pack(side="right")
        
        # 3. Horario (Centro - Se mantiene en un solo renglón para ser compacto)
        ctk.CTkLabel(
            inner_footer,
            text="🕒 Lunes - Sábado: 11:00 AM - 8:00 PM",
            font=ctk.CTkFont(size=11),
            text_color="#6B6B6B"
        ).pack(side="right", padx=20)