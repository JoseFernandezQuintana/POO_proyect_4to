import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import auth_controller  # Importamos el controlador corregido
# Asegúrate de tener dashboard_view.py en la misma carpeta
# from dashboard_view import DashboardApp 

# --- CONFIGURACIÓN DE RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(current_dir, "logo.png")
ICON_USER_PATH = os.path.join(current_dir, "icon_user.png")
ICON_LOCK_PATH = os.path.join(current_dir, "icon_lock.png")

# --- COLORES ---
BG_COLOR = "#F0F8FF"
FRAME_COLOR = "white"
ACCENT_BLUE = "#1E90FF"
ACCENT_LIGHT_BLUE = "#D9EFFF" 

class LoginApp:
    def __init__(self, root, on_login_success=None):
        self.root = root
        self.on_login_success = on_login_success # Callback para cambiar ventana
        self.root.configure(fg_color=BG_COLOR) 
        self.root.title("Sistema de Gestión de Citas - Ortho Guzmán")

        # Marco principal
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
        
        logo_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        logo_container.place(relx=0.5, rely=0.5, anchor=ctk.CENTER, relwidth=0.9) 

        # Intento de cargar logo
        try:
            logo = ctk.CTkImage(light_image=Image.open(LOGO_PATH), size=(400, 270)) 
            ctk.CTkLabel(logo_container, text="", image=logo).pack(pady=(0, 20))
        except Exception:
            ctk.CTkLabel(logo_container, text="Ortho Guzmán", font=ctk.CTkFont(size=30, weight="bold"), text_color=ACCENT_BLUE).pack(pady=(0, 20))

        ctk.CTkLabel(
            logo_container,
            text="Sistema de Gestión de Citas",
            font=ctk.CTkFont(family="Arial", size=17, weight="bold"),
            text_color="#007ACC"
        ).pack(pady=(10, 0))

        # ===== Panel derecho (Formulario Login) =====
        self.right_frame = ctk.CTkFrame(
            self.main_frame, 
            corner_radius=25, 
            fg_color=FRAME_COLOR, 
            border_width=2, 
            border_color=ACCENT_LIGHT_BLUE
        )
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 10), pady=10)

        form_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        form_container.place(relx=0.5, rely=0.5, anchor=ctk.CENTER, relwidth=0.85) 

        ctk.CTkLabel(
            form_container,
            text=" 🔒  Inicio de Sesión", 
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"), 
            text_color="#333333", 
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkFrame(form_container, height=1, fg_color=ACCENT_LIGHT_BLUE).pack(fill="x", pady=(5, 30))

        # --- Campo Usuario ---
        ctk.CTkLabel(form_container, text="Usuario", anchor="w", font=ctk.CTkFont(weight="bold"), text_color="#333333").pack(fill="x", pady=(0, 5))
        
        usuario_frame = ctk.CTkFrame(form_container, fg_color="white", corner_radius=10, border_width=1, border_color="#DDDDDD") 
        usuario_frame.pack(pady=5, fill="x")
        
        try:
            icon_user = ctk.CTkImage(light_image=Image.open(ICON_USER_PATH), size=(18, 18))
            ctk.CTkLabel(usuario_frame, image=icon_user, text="").pack(side="left", padx=(10, 5))
        except:
            ctk.CTkLabel(usuario_frame, text="👤", font=ctk.CTkFont(size=18)).pack(side="left", padx=(10, 5))

        self.username_entry = ctk.CTkEntry(usuario_frame, placeholder_text="Ej: dra.raquel", height=40, border_width=0, fg_color="white")
        self.username_entry.pack(side="left", padx=(5, 10), pady=3, fill="x", expand=True) 

        # --- Campo Contraseña ---
        ctk.CTkLabel(form_container, text="Contraseña", anchor="w", font=ctk.CTkFont(weight="bold"), text_color="#333333").pack(fill="x", pady=(15, 5))
        
        pass_frame = ctk.CTkFrame(form_container, fg_color="white", corner_radius=10, border_width=1, border_color="#DDDDDD") 
        pass_frame.pack(pady=5, fill="x")

        try:
            icon_lock = ctk.CTkImage(light_image=Image.open(ICON_LOCK_PATH), size=(18, 18))
            ctk.CTkLabel(pass_frame, image=icon_lock, text="").pack(side="left", padx=(10, 5))
        except:
            ctk.CTkLabel(pass_frame, text="🔑", font=ctk.CTkFont(size=18)).pack(side="left", padx=(10, 5))

        self.password_entry = ctk.CTkEntry(pass_frame, placeholder_text="••••••••", show="*", height=40, border_width=0, fg_color="white")
        self.password_entry.pack(side="left", padx=(5, 5), pady=3, fill="x", expand=True)

        # Botón Ojo (Ver contraseña)
        self.mostrar = False
        self.eye_icon = ctk.CTkButton(pass_frame, text="👁", width=40, height=35, fg_color="transparent", hover_color="#F0F0F0", command=self.toggle_password, text_color="#AAAAAA")
        self.eye_icon.pack(side="left", padx=(0, 10))

        # Botón Login
        self.boton_login = ctk.CTkButton(
            form_container,
            text="Iniciar Sesión",
            command=self.login,
            width=360, height=45, corner_radius=10,
            fg_color=("#00C6FF", "#005EEA"), 
            hover_color=("#00B0E5", "#004FB8"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.boton_login.pack(pady=(45, 10), fill="x")
        
        self.root.bind('<Return>', lambda event: self.login())

    def toggle_password(self):
        self.mostrar = not self.mostrar
        if self.mostrar:
            self.password_entry.configure(show="")
            self.eye_icon.configure(text="🔓")
        else:
            self.password_entry.configure(show="*")
            self.eye_icon.configure(text="👁")

    def login(self):
        usuario = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not usuario or not password:
            messagebox.showwarning("Atención", "Por favor ingresa usuario y contraseña.")
            return

        # Llamada al Controller corregido
        datos_usuario = auth_controller.login_user(usuario, password)

        if datos_usuario:
            # datos_usuario es: (id, nombre_completo, nombre_rol)
            user_id, nombre_completo, rol = datos_usuario
            
            # Si main.py pasó una función de transición, la usamos
            if self.on_login_success:
                self.on_login_success(nombre_completo, rol)
            else:
                # MODO PRUEBA (si ejecutas login_view.py directo)
                messagebox.showinfo("Éxito", f"Bienvenida, {nombre_completo}\nRol: {rol}")
                self.root.destroy()
                # Aquí podrías abrir el dashboard manualmente si es una prueba:
                # root_dash = ctk.CTk()
                # from dashboard_view import DashboardApp
                # DashboardApp(nombre_completo, rol, root_dash)
                # root_dash.mainloop()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

# Bloque para probar el Login independientemente
if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    root = ctk.CTk()
    root.geometry("900x600")
    app = LoginApp(root)
    root.mainloop()