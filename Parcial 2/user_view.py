
import tkinter as tk
from tkinter import messagebox, ttk
from user_controller import agregar_usuarios, ver_usuarios, crear_conexion, actualizar_usuarios, eliminar_usuarios

class UserApp:
    def __init__(self, username):
        self.username = username 
        self.root = tk.Tk()
        self.root.title(f"Bienvenido {username}")
        self.root.geometry("1920x1200")
        self.root.resizable(True, True)

        self.crear_elementos()
        self.ver_usuario()
        self.root.mainloop()

    def crear_elementos(self):
        tk.Label(self.root, text=f"Hola, {self.username}", font=("Arial", 22, "bold")).pack(pady=10)

        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Cerrar sesión", command=self.cerrar_sesion).pack(pady=25)

        tk.Button(frame_botones, text="Agregar usuarios", command=self.agregar_usuario).pack(pady=25)

        tk.Button(frame_botones, text="Actualizar usuarios", command=self.actualizar_usuario).pack(pady=25)

        tk.Button(frame_botones, text="Eliminar usuarios", command=self.eliminar_usuario).pack(pady=25)

        tk.Label(self.root, text=f"Lista de Usuarios", font=("Arial", 22, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Usuario"), show="headings", height=20)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Usuario", text="Usuario")
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

    def agregar_usuario(self):
        def guardar():
            u = entry_user.get().strip()
            p = entry_pass.get().strip()
            if not u or not p:
                messagebox.showwarning("Campos vacíos", "Ingrese usuario y contraseña.")
                return
            if agregar_usuarios(u, p):
                messagebox.showinfo("Éxito", f"Usuario {u} creado correctamente.")
                self.ver_usuarios()
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el usuario.")
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar Usuario")
        ventana.geometry("300x200")
        tk.Label(ventana, text="Usuario").pack(pady=5)
        entry_user = tk.Entry(ventana)
        entry_user.pack(pady=5)
        tk.Label(ventana, text="Contraseña").pack(pady=5)
        entry_pass = tk.Entry(ventana, show="*")
        entry_pass.pack(pady=5)
        tk.Button(ventana, text="crear usuario", command=guardar).pack(pady=10)

    def ver_usuario(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        usuarios = ver_usuarios()
        for u in usuarios:
            self.tree.insert("", tk.END, values=u)

    def actualizar_usuario(self):
        ""

    def eliminar_usuario(self):
        selecc_usuario = self.tree.focus()
        if not selecc_usuario:
            messagebox.showwarning("Por favor, selecciona un usuario")
            return
        
        values = self.tree.item(selecc_usuario, "values")
        user_id = values [0]
        confirmacion = messagebox.askyesno("¿Seguro que deseas eliminar este usuario?")

        if confirmacion:
            if eliminar_usuarios(user_id):
                messagebox.showinfo("Usuario eliminado correctamente")
                self.ver_usuarios()

    def cerrar_sesion(self):
        self.root.destroy()

if __name__ == "__main__":
 App = UserApp("admin")