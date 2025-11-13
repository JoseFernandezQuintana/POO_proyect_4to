import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from dashboard_view import DashboardApp 
from auth_controller import validar_credenciales
import os

# Rutas de Archivos (Asegúrate de que tus archivos de imagen estén en la misma carpeta)
current_dir = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(current_dir, "logo.png") # Asegúrate de que tu logo se llame 'logo.png'
ICON_USER_PATH = os.path.join(current_dir, "icon_user.png")
ICON_LOCK_PATH = os.path.join(current_dir, "icon_lock.png")

# Colores y estilos ajustados para igualar la imagen
BG_COLOR = "#F0F8FF" # Fondo muy claro (similar al de la imagen)
FRAME_COLOR = "white"
ACCENT_BLUE = "#1E90FF"
ACCENT_LIGHT_BLUE = "#D9EFFF" 


class LoginApp:
    def __init__(self, root):
        self.root = root
        # Color de fondo del root (el exterior)
        self.root.configure(fg_color=BG_COLOR) 
        self.root.title("Sistema de Gestión de Citas - Ortho Guzmán")

        # Marco principal (contiene ambos paneles)
        self.main_frame = ctk.CTkFrame(self.root, fg_color=BG_COLOR)
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=40) 
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # ===== Panel izquierdo (Logo) =====
        self.left_frame = ctk.CTkFrame(
            self.main_frame, 
            corner_radius=25, 
            fg_color=FRAME_COLOR, 
            border_width=2, 
            border_color=ACCENT_LIGHT_BLUE
        )
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 20), pady=10)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Contenedor para el logo y texto (centrado vertical)
        logo_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        # Ajustamos las coordenadas para hacer más espacio horizontal para el logo (relwidth)
        logo_container.place(relx=0.5, rely=0.5, anchor=ctk.CENTER, relwidth=0.9) 

        # Carga del logo
        try:
            # Tamaño del logo
            logo = ctk.CTkImage(light_image=Image.open(LOGO_PATH), size=(400, 300)) 
            ctk.CTkLabel(logo_container, text="", image=logo).pack(pady=(0, 20))
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
            ctk.CTkLabel(logo_container, text="Ortho Guzmán Logo", font=ctk.CTkFont(size=20)).pack(pady=(0, 20))


        # Texto inferior (Sistema de Gestión de Citas)
        ctk.CTkLabel(
            logo_container,
            text="Sistema de Gestión de Citas",
            font=ctk.CTkFont(family="Arial", size=17, weight="bold"),
            text_color="#007ACC"
        ).pack(pady=(10, 0))


        # ===== Panel derecho (Login) - Simula el difuminado con un borde suave =====
        self.right_frame = ctk.CTkFrame(
            self.main_frame, 
            corner_radius=25, 
            fg_color=FRAME_COLOR, 
            border_width=2, 
            border_color=ACCENT_LIGHT_BLUE
        )
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 10), pady=10)
        self.right_frame.grid_propagate(False)

        # Contenedor principal para el formulario (centrado vertical)
        form_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        form_container.place(relx=0.5, rely=0.5, anchor=ctk.CENTER, relwidth=0.85) 

        # Icono de candado y texto (Inicio de Sesión)
        ctk.CTkLabel(
            form_container,
            text=" 🔒  Inicio de Sesión", 
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"), 
            text_color="#333333", 
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        # Franja divisoria azul
        ctk.CTkFrame(form_container, height=1, fg_color=ACCENT_LIGHT_BLUE).pack(fill="x", pady=(5, 30))

        # Texto de acceso
        ctk.CTkLabel(
            form_container,
            text="Acceso exclusivo para personal de Ortho Guzmán",
            font=ctk.CTkFont(size=14),
            text_color="#6B6B6B",
            anchor="w"
        ).pack(fill="x", pady=(0, 30))

        # --- Nombre de Usuario ---
        ctk.CTkLabel(form_container, text="Nombre de Usuario", anchor="w", font=ctk.CTkFont(size=15, weight="bold"), text_color="#333333").pack(fill="x", pady=(0, 8))

        # Campo de entrada: Fondo blanco con borde azul sutil
        usuario_frame = ctk.CTkFrame(form_container, fg_color="white", corner_radius=10, border_width=1, border_color="#DDDDDD") 
        usuario_frame.pack(pady=5, fill="x")

        # Carga del ícono de usuario
        try:
            icon_user = ctk.CTkImage(light_image=Image.open(ICON_USER_PATH), size=(18, 18))
            ctk.CTkLabel(usuario_frame, image=icon_user, text="").pack(side="left", padx=(10, 5))
        except:
            ctk.CTkLabel(usuario_frame, text="👤", font=ctk.CTkFont(size=18)).pack(side="left", padx=(10, 5))
        
        self.username_entry = ctk.CTkEntry(
            usuario_frame,
            placeholder_text="Ingresa tu nombre de usuario",
            height=40,
            border_width=0,
            fg_color="white", 
            font=ctk.CTkFont(size=14)
        )
        # CORRECCIÓN: Agregar pady a Entry para exponer el borde del Frame contenedor
        self.username_entry.pack(side="left", padx=(5, 10), pady=3, fill="x", expand=True) 

        # --- Contraseña ---
        ctk.CTkLabel(form_container, text="Contraseña", anchor="w", font=ctk.CTkFont(size=15, weight="bold"), text_color="#333333").pack(fill="x", pady=(20, 8))

        # Campo de entrada: Fondo blanco con borde azul sutil
        pass_frame = ctk.CTkFrame(form_container, fg_color="white", corner_radius=10, border_width=1, border_color="#DDDDDD") 
        pass_frame.pack(pady=5, fill="x")

        # Carga del ícono de candado
        try:
            icon_lock = ctk.CTkImage(light_image=Image.open(ICON_LOCK_PATH), size=(18, 18))
            ctk.CTkLabel(pass_frame, image=icon_lock, text="").pack(side="left", padx=(10, 5))
        except:
            ctk.CTkLabel(pass_frame, text="🔑", font=ctk.CTkFont(size=18)).pack(side="left", padx=(10, 5))


        self.password_entry = ctk.CTkEntry(
            pass_frame,
            placeholder_text="••••••••",
            show="*",
            height=40,
            border_width=0,
            fg_color="white",
            font=ctk.CTkFont(size=14)
        )
        # CORRECCIÓN: Agregar pady a Entry para exponer el borde del Frame contenedor
        self.password_entry.pack(side="left", padx=(5, 5), pady=3, fill="x", expand=True)

        # Botón para mostrar/ocultar contraseña (usando el ícono de "ojo")
        self.mostrar = False
        self.eye_icon = ctk.CTkButton(
            pass_frame,
            text=" 👁", 
            width=40, 
            height=35,
            fg_color="transparent",
            hover_color="#F0F0F0",
            command=self.toggle_password,
            corner_radius=10,
            text_color="#AAAAAA"
        )
        self.eye_icon.pack(side="left", padx=(0, 10))

        # ===== Botón Iniciar Sesión (Gradiente) =====
        self.boton_login = ctk.CTkButton(
            form_container,
            text="Iniciar Sesión",
            command=self.login,
            width=360,
            height=45,
            corner_radius=10,
            fg_color=("#00C6FF", "#005EEA"), 
            hover_color=("#00B0E5", "#004FB8"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.boton_login.pack(pady=(45, 10), fill="x")

        # Texto inferior
        ctk.CTkLabel(
            form_container,
            text="Acceso restringido • Solo personal autorizado",
            font=ctk.CTkFont(size=12),
            text_color="#7A7A7A"
        ).pack(pady=(20, 10))

    # Mostrar/ocultar contraseña
    def toggle_password(self):
        self.mostrar = not self.mostrar
        if self.mostrar:
            self.password_entry.configure(show="")
            self.eye_icon.configure(text=" 🔓")
        else:
            self.password_entry.configure(show="*")
            self.eye_icon.configure(text=" 👁")

    # Validación del login
    def login(self):
        usuario = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not usuario or not password:
            messagebox.showwarning("Faltan datos", "Favor de ingresar el usuario y la contraseña")
            return

        if validar_credenciales(usuario, password):
            messagebox.showinfo("Acceso permitido", f"Bienvenido {usuario}")

            # Llamar al método definido en main.py para cerrar el login
            # y abrir el dashboard sin errores Tcl
            if hasattr(self, "cerrar_y_abrir_dashboard"):
                self.cerrar_y_abrir_dashboard(usuario)
            else:
                # Método de respaldo (por si se ejecuta de forma aislada)
                for after_id in self.root.tk.call('after', 'info').split():
                    try:
                        self.root.after_cancel(after_id)
                    except Exception:
                        pass
                self.root.destroy()
                root_dashboard = ctk.CTk()
                DashboardApp(usuario, root_dashboard)
                root_dashboard.mainloop()
        else:
            messagebox.showerror("Acceso denegado", "Tus datos no son correctos")
