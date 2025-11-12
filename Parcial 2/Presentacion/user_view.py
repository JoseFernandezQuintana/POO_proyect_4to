import customtkinter as ctk 
from tkinter import messagebox, ttk
from user_controller import ver_usuario, crear_usuarios, actualizar_usuarios, eliminar_usuario
from products_view import ProductsApp
import tkinter as tk

class DashboardApp:
    def __init__(self, username, root):
        self.username = username
        self.root = root 
        self.root.title(f"Bienvenido {username}")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        self.configurar_estilo_treeview()
        
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.crear_elementos()
        self.ver_usuarios()
    
    def configurar_estilo_treeview(self):
        style = ttk.Style()
        
        style.theme_use("default") 
        
        bg_color = self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        
        style.configure("Treeview", 
                        background=bg_color,
                        foreground=text_color,
                        fieldbackground=bg_color,
                        bordercolor=bg_color,
                        borderwidth=0)
        style.map('Treeview', 
                  background=[('selected', '#3B82F6')])
        
        style.configure("Treeview.Heading", 
                        background=self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"]),
                        foreground=text_color,
                        font=('Arial', 12, 'bold'),
                        borderwidth=0)
        
    def crear_elementos(self):
        ctk.CTkLabel(
            self.main_frame, 
            text=f"Panel de Administración", 
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=15)
        
        ctk.CTkLabel(
            self.main_frame, 
            text=f"Hola, {self.username}", 
            font=ctk.CTkFont(size=16)
        ).pack(pady=(0, 10))

        user_btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        user_btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            user_btn_frame, text="Ver Usuarios 🔄", command=self.ver_usuarios
        ).grid(row=0, column=0, padx=10, pady=5)

        ctk.CTkButton(
            user_btn_frame, text="Agregar Usuario ➕", command=self.crear_usuarios
        ).grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkButton(
            user_btn_frame, text="Actualizar Usuario ✏️", command=self.actualizar_usuarios
        ).grid(row=0, column=2, padx=10, pady=5)

        ctk.CTkButton(
            user_btn_frame, text="Eliminar Usuario 🗑️", command=self.eliminar_usuarios, fg_color="#F44336", hover_color="#D32F2F"
        ).grid(row=0, column=3, padx=10, pady=5)
        
        ctk.CTkFrame(self.main_frame, height=2, fg_color="#3B82F6").pack(fill="x", pady=15) # Separador visual

        action_btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        action_btn_frame.pack(pady=10)

        ctk.CTkButton(
            action_btn_frame, 
            text="Gestionar Productos 📦", 
            command=self.gestionar_productos,
            width=200, 
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=20)

        ctk.CTkButton(
            action_btn_frame, 
            text="Cerrar Sesión 🚪", 
            command=self.cerrar_sesion, 
            fg_color="#424242", 
            hover_color="#616161",
            width=200, 
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=1, padx=20)
        
        self.tree = ttk.Treeview(self.main_frame, columns = ("ID usuario", "Username"), height = 10)
        self.tree.heading("#0", text="", anchor=tk.CENTER)
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.heading("ID usuario", text = "ID usuario")
        self.tree.column("ID usuario", width=100, anchor=tk.CENTER)
        self.tree.heading("Username", text = "Nombre del usuario")
        self.tree.column("Username", anchor=tk.W)
        self.tree.pack(padx=10, pady=10, fill = "both", expand = True)

    def ver_usuarios(self):
        """Recarga y muestra la lista de usuarios en el Treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        usuarios = ver_usuario()
        for u in usuarios:
            self.tree.insert("", tk.END, values=u)


    def crear_usuarios(self):
        def guardar():
            u = entry_user.get().strip()
            p = entry_pass.get().strip()
            if not u or not p:
                messagebox.showwarning("Campos vacíos", "Ingrese usuario y contraseña.")
                return
            
            if crear_usuarios(u, p):
                messagebox.showinfo("Éxito", f"Usuario {u} creado correctamente.")
                self.ver_usuarios()
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el usuario. Puede que ya exista.")
        
        ventana = ctk.CTkToplevel(self.root) 
        ventana.title("Agregar Usuario")
        ventana.geometry("300x280")
        ventana.transient(self.root) 
        ventana.grab_set() 
        ventana.focus_force()
        frame = ctk.CTkFrame(ventana)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Usuario", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        entry_user = ctk.CTkEntry(frame, width=200)
        entry_user.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Contraseña", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        entry_pass = ctk.CTkEntry(frame, show="*", width=200)
        entry_pass.pack(pady=5)
        
        ctk.CTkButton(frame, text="Crear Usuario", command=guardar, width=150, font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkButton(frame, text="Cancelar", command=ventana.destroy, width=150, fg_color="gray").pack(pady=5)

    def actualizar_usuarios(self):
        def guardar():
            user_id = entry_id.get().strip()
            nuevo_user = entry_user.get().strip()
            nueva_pass = entry_pass.get().strip()

            if not user_id or not nuevo_user or not nueva_pass:
                messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos.")
                return
            
            try:
                user_id_int = int(user_id)
            except ValueError:
                messagebox.showerror("Error", "El ID debe ser un número entero.")
                return

            if actualizar_usuarios(user_id_int, nuevo_user, nueva_pass):
                messagebox.showinfo("Éxito", "Usuario actualizado correctamente.")
                self.ver_usuarios() 
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el usuario. Verifique el ID.")

        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Actualizar Usuario")
        ventana.geometry("300x380")
        ventana.transient(self.root)
        ventana.grab_set()
        ventana.focus_force()

        frame = ctk.CTkFrame(ventana)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="ID de usuario a actualizar:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        entry_id = ctk.CTkEntry(frame, width=200)
        entry_id.pack(pady=5)

        ctk.CTkLabel(frame, text="Nuevo nombre de usuario:", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        entry_user = ctk.CTkEntry(frame, width=200)
        entry_user.pack(pady=5)

        ctk.CTkLabel(frame, text="Nueva contraseña:", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        entry_pass = ctk.CTkEntry(frame, show="*", width=200)
        entry_pass.pack(pady=5)

        ctk.CTkButton(frame, text="Guardar Cambios", command=guardar, width=150, font=ctk.CTkFont(weight="bold")).pack(pady=(25, 5))
        ctk.CTkButton(frame, text="Cancelar", command=ventana.destroy, width=150, fg_color="gray").pack(pady=5)

    def eliminar_usuarios(self):
        def eliminar():
            user_id = entry_id.get().strip()
            if not user_id:
                messagebox.showwarning("Campo vacío", "Ingrese el ID del usuario a eliminar.")
                return
            
            try:
                user_id_int = int(user_id)
            except ValueError:
                messagebox.showerror("Error", "El ID debe ser un número entero.")
                return

            confirm = messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Está seguro de eliminar al usuario con ID '{user_id_int}'?"
            )
            
            if confirm:
                if eliminar_usuario(user_id_int):
                    messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
                    self.ver_usuarios()
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el usuario. Verifique el ID.")

        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Eliminar Usuario")
        ventana.geometry("300x200")
        ventana.transient(self.root)
        ventana.grab_set()
        ventana.focus_force()

        frame = ctk.CTkFrame(ventana)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="ID del usuario a eliminar:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        entry_id = ctk.CTkEntry(frame, width=200)
        entry_id.pack(pady=5)

        ctk.CTkButton(frame, text="Eliminar", command=eliminar, width=150, fg_color="#F44336", hover_color="#D32F2F", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkButton(frame, text="Cancelar", command=ventana.destroy, width=150, fg_color="gray").pack(pady=5)

    def cerrar_sesion(self):
        respuesta = messagebox.askyesno(
            "Confirmar cierre de sesión",
            "¿Estás seguro de que deseas cerrar sesión?"
        )
        if respuesta:
            self.root.destroy()

    def gestionar_productos(self):
        self.root.withdraw() 
        
        root_products = ctk.CTk() 
        
        app = ProductsApp(root_products, self.root)
        
        root_products.mainloop() 
        
        if self.root.winfo_exists():
            self.root.deiconify()