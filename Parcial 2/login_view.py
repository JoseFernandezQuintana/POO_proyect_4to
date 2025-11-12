
import tkinter as tk
from tkinter import messagebox
from auth_controller import validar_credenciales
from user_view import UserApp


class LoginApp: 
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de inicio de sesión")
        self.root.geometry("400x300")
        self.root.resizable(False, False) #Son dos false, uno para el ancho y otro para el largo

        # Encabezado de la ventana
        tk.Label(root, text="Bienvenido al Login", font=("Arial",16,"bold")).pack(pady=15)

        #Campos
        tk.Label(root, text="Nombre de usuario:").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Contraseña").pack()
        self.password_entry = tk.Entry(root, show="*") #El show oculta la contraseña
        self.password_entry.pack(pady=5)

        tk.Button(root, text="Iniciar sesión", command=self.Login).pack(pady=20)

    def Login(self):
        # Obtener los datos de entrada (entry) y llamar al validador
        usuario = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
     
        if not usuario or not password: 
            messagebox.showwarning("Faltan datos por ingresar", "Por favor ingresa usuario y contraseña")
            return

        if validar_credenciales(usuario, password):
            messagebox.showinfo("Acceso concedido", f"Bienvenido {usuario}")
            self.root.destroy()# Es para que se cierre la ventana del Login
            App = UserApp(usuario)

        else:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos")