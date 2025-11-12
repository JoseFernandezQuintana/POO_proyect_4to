# dashboard_view.py
import tkinter as tk
from tkinter import messagebox

class DashboardApp:
    def __init__(self, username, root):
        self.username = username
        self.root = root 
        self.root.title(f"Bienvenido {username}")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        self.crear_elementos()
       

    def crear_elementos(self):
        tk.Label(
            self.root, text=f"Hola {self.username}", font=("Arial", 22, "bold")
        ).pack(pady=10)

        tk.Button(
            self.root, text="Ver usuarios", width=20, command=self.ver_usuarios
        ).pack(pady=10)

        tk.Button(
            self.root, text="Agregar usuarios", width=20, command=self.agregar_usuarios
        ).pack(pady=10)

        tk.Button(
            self.root, text="Actualizar usuarios", width=20, command=self.actualizar_usuarios
        ).pack(pady=10)

        tk.Button(
            self.root, text="Eliminar usuarios", width=20, command=self.eliminar_usuarios
        ).pack(pady=10)

        tk.Button(
            self.root, text="Cerrar Sesión", width=20, command=self.cerrar_sesion
        ).pack(pady=20)

    def ver_usuarios(self):
        messagebox.showinfo("Acción", "Ver usuarios")

    def agregar_usuarios(self):
        messagebox.showinfo("Acción", "Agregar usuarios")

    def actualizar_usuarios(self):
        messagebox.showinfo("Acción", "Actualizar usuarios")

    def eliminar_usuarios(self):
        messagebox.showinfo("Acción", "Eliminar usuarios")

    def cerrar_sesion(self):
        respuesta = messagebox.askyesno(
            "Confirmar cierre de sesión",
            "¿Estás seguro de que deseas cerrar sesión?"
        )
        if respuesta:
            self.root.destroy()