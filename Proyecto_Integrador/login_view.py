import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import auth_controller

# Configuración
current_dir = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(current_dir, "logo.png")

BG_COLOR = "#F0F8FF"
WHITE = "#FFFFFF"
ACCENT_BLUE = "#1E90FF"
TEXT_BLUE_LOGO = "#007ACC"
BORDER_COLOR = "#D0E4F5"
TEXT_COLOR = "#333333"

class LoginApp:
    def __init__(self, root, on_login_success=None):
        self.root = root
        self.on_login_success = on_login_success
        
        self.root.title("Acceso - Ortho Guzmán")
        self.root.configure(fg_color=BG_COLOR)
        
        # Control de foco global
        self.root.bind_all("<Button-1>", self.gestionar_foco)

        # --- TARJETA PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(
            self.root, 
            fg_color=WHITE, 
            corner_radius=20, 
            border_color=BORDER_COLOR, 
            border_width=2
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.8)

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0) 
        self.main_frame.grid_columnconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # === IZQUIERDA ===
        self.left_side = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.left_side.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Contenedor logo
        self.logo_box = ctk.CTkFrame(self.left_side, fg_color="transparent")
        self.logo_box.place(relx=0.5, rely=0.5, anchor="center")

        try:
            pil_img = Image.open(LOGO_PATH)
            ratio = pil_img.width / pil_img.height
            new_w = 350
            new_h = int(new_w / ratio)
            logo_img = ctk.CTkImage(light_image=pil_img, size=(new_w, new_h))
            
            ctk.CTkLabel(self.logo_box, text="", image=logo_img).pack(pady=(0, 15))
        except:
            ctk.CTkLabel(self.logo_box, text="🦷", font=("Arial", 80)).pack(pady=(0,15))

        ctk.CTkLabel(
            self.logo_box, 
            text="Sistema de Gestión de Citas", 
            font=("Arial", 18, "bold"), 
            text_color=TEXT_BLUE_LOGO
        ).pack()

        # === CENTRO: LÍNEA ===
        self.sep = ctk.CTkFrame(self.main_frame, width=2, fg_color="#F0F0F0")
        self.sep.grid(row=0, column=1, sticky="ns", pady=40)

        # === DERECHA: FORMULARIO ===
        self.right_side = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.right_side.grid(row=0, column=2, sticky="nsew", padx=30, pady=30)
        
        self.form_box = ctk.CTkFrame(self.right_side, fg_color="transparent")
        self.form_box.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)

        ctk.CTkLabel(self.form_box, text="Bienvenido", font=("Segoe UI", 28, "bold"), text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.form_box, text="Inicia sesión para continuar", font=("Arial", 12), text_color="gray").pack(anchor="w", pady=(0, 30))

        # Usuario
        ctk.CTkLabel(self.form_box, text="Usuario", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", pady=(0,5))
        self.user_entry = ctk.CTkEntry(
            self.form_box, 
            placeholder_text="Nombre de usuario", 
            height=45, 
            fg_color="#FAFAFA",
            border_color="#E0E0E0",
            text_color="black"
        )
        self.user_entry.pack(fill="x", pady=(0, 15))

        # Contraseña
        ctk.CTkLabel(self.form_box, text="Contraseña", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", pady=(0,5))
        self.pass_frame = ctk.CTkFrame(self.form_box, fg_color="transparent")
        self.pass_frame.pack(fill="x", pady=(0, 25))

        self.pass_entry = ctk.CTkEntry(
            self.pass_frame, 
            placeholder_text="••••••••", 
            show="*", 
            height=45, 
            fg_color="#FAFAFA",
            border_color="#E0E0E0",
            text_color="black"
        )
        self.pass_entry.pack(side="left", fill="x", expand=True)

        self.btn_eye = ctk.CTkButton(
            self.pass_frame,
            text="👁",
            width=40,
            height=45,
            fg_color="transparent",
            text_color="#555",
            hover_color="#E0E0E0",
            font=("Arial", 16),
            command=self.toggle_password
        )
        self.btn_eye.pack(side="right", padx=(5, 0))

        # Botón Login
        self.btn_login = ctk.CTkButton(
            self.form_box, 
            text="INICIAR SESIÓN", 
            height=50, 
            fg_color=ACCENT_BLUE, 
            hover_color="#0056b3",
            font=("Segoe UI", 13, "bold"), 
            command=self.login_action
        )
        self.btn_login.pack(fill="x", pady=10)
        
        self.pass_entry.bind("<Return>", lambda e: self.login_action())

    def gestionar_foco(self, event):
        try:
            widget = event.widget
            if "entry" in widget.winfo_class().lower():
                return
            self.root.focus_set()
        except:
            pass

    def toggle_password(self):
        if self.pass_entry.cget("show") == "*":
            self.pass_entry.configure(show="")
            self.btn_eye.configure(text="✕") 
        else:
            self.pass_entry.configure(show="*")
            self.btn_eye.configure(text="👁") 

    def login_action(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()
        if not u or not p:
            messagebox.showwarning("Faltan datos", "Ingresa usuario y contraseña.")
            return
        
        datos = auth_controller.login_user(u, p)
        if datos:
            if self.on_login_success: self.on_login_success(datos)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas.")
            self.pass_entry.delete(0, 'end')
