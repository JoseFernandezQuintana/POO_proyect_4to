import customtkinter as ctk 
from tkinter import messagebox, ttk
import tkinter as tk

from products_controller import ver_productos, crear_producto, actualizar_producto, eliminar_producto


class ProductsApp:
    def __init__(self, root, dashboard_root):
        self.root = root
        self.dashboard_root = dashboard_root  
        self.root.title("Gestión de Productos")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)

        self.configurar_estilo_treeview(root)
        
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.crear_elementos()
        self.ver_productos()

    def configurar_estilo_treeview(self, root_widget): 
        style = ttk.Style()
        
        style.theme_use("default") 
        
        bg_color = root_widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = root_widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        
        style.configure("Treeview", 
                        background=bg_color,
                        foreground=text_color,
                        fieldbackground=bg_color,
                        bordercolor=bg_color,
                        borderwidth=0)
        style.map('Treeview', 
                  background=[('selected', '#3B82F6')])
        style.configure("Treeview.Heading", 
                        background=root_widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"]),
                        foreground=text_color,
                        font=('Arial', 12, 'bold'),
                        borderwidth=0)

    def crear_elementos(self):
        ctk.CTkLabel(
            self.main_frame, 
            text="📦 Gestión de Productos",
             fg_color="#424242",  
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=15)

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame, text="Ver Productos 🔄", command=self.ver_productos
        ).grid(row=0, column=0, padx=10, pady=5)

        ctk.CTkButton(
            btn_frame, text="Agregar Producto ➕", command=self.crear_producto
        ).grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkButton(
            btn_frame, text="Actualizar Producto ✏️", command=self.actualizar_producto
        ).grid(row=0, column=2, padx=10, pady=5)

        ctk.CTkButton(
            btn_frame, text="Eliminar Producto 🗑️", command=self.eliminar_producto, fg_color="#F44336", hover_color="#D32F2F"
        ).grid(row=0, column=3, padx=10, pady=5)

        nav_btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        nav_btn_frame.pack(pady=15)
        
        ctk.CTkButton(
            nav_btn_frame, text="Volver al Dashboard 🏠", command=self.volver_dashboard, 
            width=200, height=40, fg_color="#424242", hover_color="#616161", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=20)

        ctk.CTkButton(
            nav_btn_frame, text="Salir del Sistema 🚪", command=self.salir_sistema, 
            width=200, height=40, fg_color="#D32F2F", hover_color="#C62828", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=1, padx=20)

       
        columns = ("ID", "Nombre", "Stock", "Precio", "Status", "Marca", "Proveedor", "Descripción")
        self.tree = ttk.Treeview(self.main_frame, columns=columns, height=15, show='headings')
        
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.heading("Nombre", text="Nombre del Producto")
        self.tree.column("Nombre", width=180, anchor=tk.W)
        self.tree.heading("Stock", text="Stock")
        self.tree.column("Stock", width=80, anchor=tk.CENTER)
        self.tree.heading("Precio", text="Precio")
        self.tree.column("Precio", width=100, anchor=tk.E)
        self.tree.heading("Status", text="Status")
        self.tree.column("Status", width=80, anchor=tk.CENTER)
        self.tree.heading("Marca", text="Marca")
        self.tree.column("Marca", width=100, anchor=tk.W)
        self.tree.heading("Proveedor", text="Proveedor")
        self.tree.column("Proveedor", width=150, anchor=tk.W)
        self.tree.heading("Descripción", text="Descripción")
        self.tree.column("Descripción", width=250, anchor=tk.W)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

    def ver_productos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        productos = ver_productos()
        for p in productos:
            p_list = list(p)
            if len(p_list) > 4:
                 p_list[4] = "Activo" if p_list[4] == 1 else "Inactivo"
            self.tree.insert("", tk.END, values=p_list)


    def crear_producto(self): 
        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                stock = int(entry_stock.get().strip())
                precio = float(entry_precio.get().strip())
                status = 1 if status_var.get() == "Activo" else 0
                marca = entry_marca.get().strip()
                proveedor = entry_proveedor.get().strip()
                descripcion = entry_descripcion.get().strip()
            except ValueError:
                messagebox.showerror("Error de datos", "Asegúrese de que Stock y Precio sean números válidos.")
                return

            if not nombre or stock is None or precio is None:
                messagebox.showwarning("Campos obligatorios", "Nombre, Stock y Precio son obligatorios.")
                return

            if crear_producto(nombre, stock, precio, status, marca, proveedor, descripcion):
                messagebox.showinfo("Éxito", f"Producto '{nombre}' creado correctamente.")
                self.ver_productos()
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el producto. Verifique la conexión o datos.")

        ventana = ctk.CTkToplevel(self.root) 
        ventana.title("Agregar Producto")
        ventana.geometry("500x750")
        ventana.transient(self.root) 
        ventana.grab_set() 
        ventana.focus_force()

        frame = ctk.CTkFrame(ventana)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Nombre:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_nombre = ctk.CTkEntry(frame, width=350)
        entry_nombre.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Stock:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_stock = ctk.CTkEntry(frame, width=350)
        entry_stock.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Precio:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_precio = ctk.CTkEntry(frame, width=350)
        entry_precio.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Status:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        status_var = ctk.StringVar(value="Activo")
        ctk.CTkOptionMenu(frame, values=["Activo", "Inactivo"], variable=status_var, width=350).pack(pady=5)
        
        ctk.CTkLabel(frame, text="Marca:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_marca = ctk.CTkEntry(frame, width=350)
        entry_marca.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Proveedor:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_proveedor = ctk.CTkEntry(frame, width=350)
        entry_proveedor.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Descripción:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_descripcion = ctk.CTkEntry(frame, width=350)
        entry_descripcion.pack(pady=5)
        
        ctk.CTkButton(frame, text="Crear Producto", command=guardar, width=200, font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkButton(frame, text="Cancelar", command=ventana.destroy, width=200, fg_color="gray").pack(pady=5)


    def actualizar_producto(self):
        def guardar():
            try:
                id_producto = int(entry_id.get().strip())
                nombre = entry_nombre.get().strip()
                stock = int(entry_stock.get().strip())
                precio = float(entry_precio.get().strip())
                status = 1 if status_var.get() == "Activo" else 0
                marca = entry_marca.get().strip()
                proveedor = entry_proveedor.get().strip()
                descripcion = entry_descripcion.get().strip()
            except ValueError:
                messagebox.showerror("Error de datos", "Asegúrese de que ID, Stock y Precio sean números válidos.")
                return

            if not nombre or stock is None or precio is None or id_producto is None:
                messagebox.showwarning("Campos obligatorios", "ID, Nombre, Stock y Precio son obligatorios.")
                return

            if actualizar_producto(id_producto, nombre, stock, precio, status, marca, proveedor, descripcion):
                messagebox.showinfo("Éxito", f"Producto con ID {id_producto} actualizado correctamente.")
                self.ver_productos()
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el producto. Verifique el ID.")

        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Actualizar Producto")
        ventana.geometry("500x750")
        ventana.transient(self.root)
        ventana.grab_set()
        ventana.focus_force()

        frame = ctk.CTkFrame(ventana)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="ID del Producto a actualizar:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 0))
        entry_id = ctk.CTkEntry(frame, width=350)
        entry_id.pack(pady=5)

        ctk.CTkLabel(frame, text="Nombre:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_nombre = ctk.CTkEntry(frame, width=350)
        entry_nombre.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Stock:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_stock = ctk.CTkEntry(frame, width=350)
        entry_stock.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Precio:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_precio = ctk.CTkEntry(frame, width=350)
        entry_precio.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Status:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        status_var = ctk.StringVar(value="Activo")
        ctk.CTkOptionMenu(frame, values=["Activo", "Inactivo"], variable=status_var, width=350).pack(pady=5)
        
        ctk.CTkLabel(frame, text="Marca:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_marca = ctk.CTkEntry(frame, width=350)
        entry_marca.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Proveedor:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_proveedor = ctk.CTkEntry(frame, width=350)
        entry_proveedor.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Descripción:", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        entry_descripcion = ctk.CTkEntry(frame, width=350)
        entry_descripcion.pack(pady=5)

        ctk.CTkButton(frame, text="Guardar Cambios", command=guardar, width=200, font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkButton(frame, text="Cancelar", command=ventana.destroy, width=200, fg_color="gray").pack(pady=5)

    def eliminar_producto(self):
        def eliminar():
            product_id = entry_id.get().strip()
            if not product_id:
                messagebox.showwarning("Campo vacío", "Ingrese el ID del producto a eliminar.")
                return
            
            try:
                product_id_int = int(product_id)
            except ValueError:
                messagebox.showerror("Error", "El ID debe ser un número entero.")
                return

            confirm = messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Está seguro de eliminar el producto con ID '{product_id_int}'?"
            )
            if confirm:
                if eliminar_producto(product_id_int):
                    messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
                    self.ver_productos()
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el producto. Verifique el ID.")

        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Eliminar Producto")
        ventana.geometry("300x200")
        ventana.transient(self.root)
        ventana.grab_set()
        ventana.focus_force()

        frame = ctk.CTkFrame(ventana)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="ID del producto a eliminar:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        entry_id = ctk.CTkEntry(frame, width=200)
        entry_id.pack(pady=5)

        ctk.CTkButton(frame, text="Eliminar", command=eliminar, width=150, fg_color="#F44336", hover_color="#D32F2F", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkButton(frame, text="Cancelar", command=ventana.destroy, width=150, fg_color="gray").pack(pady=5)


    def volver_dashboard(self):
        self.root.destroy()
        if self.dashboard_root and self.dashboard_root.winfo_exists():
            self.dashboard_root.deiconify() 

    def salir_sistema(self):
        if messagebox.askyesno("Salir", "¿Estás seguro de que deseas salir del sistema?"):
            self.root.destroy()
            if self.dashboard_root and self.dashboard_root.winfo_exists():
                 self.dashboard_root.destroy()
            self.root.quit()