import customtkinter as ctk
from tkinter import messagebox
from user_view import DashboardApp
from auth_controller import validar_credenciales

class LoginApp:
    def __init__(self, root):
        self.root = root
        
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            self.main_frame, 
            text="Bienvenido al sistema", 
            font=ctk.CTkFont(family="Arial", size=20, weight="bold")
        ).pack(pady=(15, 25))

        self.username_entry = ctk.CTkEntry(
            self.main_frame, 
            placeholder_text="Nombre de usuario",
            width=250,
            height=35
        )
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            self.main_frame, 
            placeholder_text="Contraseña",
            show="*", 
            width=250,
            height=35
        )  
        self.password_entry.pack(pady=10)

        ctk.CTkButton(
            self.main_frame, 
            text="Iniciar Sesión", 
            command=self.login,
            width=250,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=20)

   
    def login(self):
        usuario = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        
        if not usuario or not password:
            messagebox.showwarning("Faltan datos", "Favor de ingresar el usuario y la contraseña")
            return  
        if validar_credenciales(usuario, password):
            messagebox.showinfo("Acceso permitido", f"Bienvenido {usuario}")
            self.root.destroy()
            
            root_dashboard = ctk.CTk() 
            DashboardApp(usuario, root_dashboard) 
            root_dashboard.mainloop()
        else:
            messagebox.showerror("Acceso denegado", "Tus datos no son correctos")