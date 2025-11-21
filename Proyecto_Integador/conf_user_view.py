# conf_user_view.py
# Interfaz de Administración de Usuarios con CustomTkinter
import customtkinter as ctk
from tkinter import messagebox
from conf_user_controller import (
    get_all_users, get_user_by_id, find_users_by_term,
    add_user, update_user, delete_user
)

# Definición estricta de roles válidos para la UI y la validación local
VALID_ROLES = ["Administrador", "Doctora", "Recepcionista"]

# Paleta de colores
PRIMARY_COLOR = "#3498DB"
ACCENT_COLOR = "#2ECC71"
DANGER_COLOR = "#E74C3C"
BG_LIGHT = "#ECF0F1"
HEADER_DARK = "#2C3E50"
DISABLED_COLOR = "#95A5A6"

class UserAdminWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Usuarios")
        # Tamaño inicial y ventana redimensionable
        self.geometry("1000x500")
        self.resizable(True, True) 
        self.configure(fg_color=BG_LIGHT)

        # Configuración Modal
        try:
            self.transient(master)
            self.grab_set()
        except Exception:
            pass

        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ## 1. Header
        header = ctk.CTkFrame(self, fg_color=HEADER_DARK, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(header, text=" Administrador de Usuarios", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="white", anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=12)

        ## 2. Barra de Herramientas
        toolbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 5))
        toolbar_frame.grid_columnconfigure(1, weight=1)

        # Búsqueda
        search_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(search_frame, text="Buscar:", width=60, anchor="w").grid(row=0, column=0, padx=(0, 5))
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Nombre, apellido o usuario", width=250)
        self.search_entry.grid(row=0, column=1, padx=5)
        ctk.CTkButton(search_frame, text="🔎 Buscar", width=90, command=self.on_search).grid(row=0, column=2, padx=(5, 10))
        
        # Botones de acción derecha
        action_buttons_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        action_buttons_frame.grid(row=0, column=2, sticky="e")

        ctk.CTkButton(action_buttons_frame, text="🔄 Refrescar", width=110, command=self.load_users, 
                      fg_color=PRIMARY_COLOR, hover_color="#2A7BBC").grid(row=0, column=0, padx=5)
        ctk.CTkButton(action_buttons_frame, text="➕ Agregar Nuevo Usuario", fg_color=ACCENT_COLOR, hover_color="#24A15A",
                      command=self.open_add_form).grid(row=0, column=1, padx=5)


        ## 3. Contenido Principal: Lista (Izquierda, 80%) + Formulario (Derecha, 20%)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(5, 20))
        main_frame.grid_columnconfigure(0, weight=4) 
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Marco de la Lista/Tabla
        list_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=12)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(list_frame, text="👥 Listado de Usuarios", font=ctk.CTkFont(size=16, weight="bold"),
                     anchor="w").grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")

        # Tabla (ScrollableFrame)
        self.scrollable_table_frame = ctk.CTkScrollableFrame(list_frame, label_text="", label_fg_color="transparent", fg_color="transparent")
        self.scrollable_table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 15))
        
        # Peso de columnas de la tabla (para alineación)
        self.scrollable_table_frame.grid_columnconfigure((0, 1, 2, 3), weight=1) 
        self.scrollable_table_frame.grid_columnconfigure(4, weight=0) # Acción (fijo)

        # Formulario (derecha)
        form_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=12)
        form_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        form_frame.grid_columnconfigure(0, weight=1)

        self.form_title = ctk.CTkLabel(form_frame, text="📝 Crear Nuevo Usuario", font=ctk.CTkFont(size=16, weight="bold"))
        self.form_title.grid(row=0, column=0, pady=(15, 10), padx=15)

        # Campos del Formulario
        self.frm_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre", height=35)
        self.frm_apellido = ctk.CTkEntry(form_frame, placeholder_text="Apellido", height=35)
        self.frm_usuario = ctk.CTkEntry(form_frame, placeholder_text="Usuario", height=35)
        self.frm_password = ctk.CTkEntry(form_frame, placeholder_text="Password (obligatorio al crear)", show="*", height=35)

        self.frm_nombre.grid(row=1, column=0, padx=15, pady=(5, 8), sticky="ew")
        self.frm_apellido.grid(row=2, column=0, padx=15, pady=8, sticky="ew")
        self.frm_usuario.grid(row=3, column=0, padx=15, pady=8, sticky="ew")
        self.frm_password.grid(row=4, column=0, padx=15, pady=8, sticky="ew")

        # Rol (solo roles definidos)
        ctk.CTkLabel(form_frame, text="Rol:", anchor="w").grid(row=5, column=0, sticky="ew", padx=15, pady=(8,0))
        self.role_menu = ctk.CTkComboBox(form_frame, values=list(VALID_ROLES), height=35)
        self.role_menu.set(VALID_ROLES[0] if VALID_ROLES else "")
        self.role_menu.grid(row=6, column=0, padx=15, pady=(0, 15), sticky="ew")

        # Acciones del Formulario
        actions = ctk.CTkFrame(form_frame, fg_color="transparent")
        actions.grid(row=7, column=0, pady=10, padx=15, sticky="ew")
        actions.grid_columnconfigure((0, 1), weight=1)

        self.btn_save = ctk.CTkButton(actions, text="Guardar", fg_color=ACCENT_COLOR, hover_color="#24A15A", command=self.on_save)
        self.btn_save.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Botón Eliminar reubicado
        self.btn_delete = ctk.CTkButton(actions, text="🗑️ Eliminar Usuario", fg_color=DANGER_COLOR, hover_color="#C0392B", 
                                        command=self.on_delete_selected, state="disabled")
        self.btn_delete.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        ctk.CTkButton(form_frame, text="Limpiar Formulario", command=self.clear_form, fg_color=DISABLED_COLOR, hover_color="#7F8C8D").grid(row=8, column=0, pady=(0, 10), padx=15, sticky="ew")
        ctk.CTkButton(form_frame, text="✖️ Cerrar Ventana", command=self.on_close, fg_color=HEADER_DARK).grid(row=9, column=0, pady=(0, 15), padx=15, sticky="ew")

        # Estado
        self.editing_user_id = None

        # Cargar usuarios al inicio
        self.load_users()

    # ------------------------------------------------------------------
    # ---------- LÓGICA DE LA VISTA (MÉTODOS) --------------------------
    # ------------------------------------------------------------------

    def on_close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def clear_form(self):
        self.editing_user_id = None
        self.frm_nombre.delete(0, "end")
        self.frm_apellido.delete(0, "end")
        self.frm_usuario.delete(0, "end")
        self.frm_password.delete(0, "end")
        self.role_menu.set(VALID_ROLES[0] if VALID_ROLES else "")
        
        self.btn_save.configure(text="Guardar", fg_color=ACCENT_COLOR, hover_color="#24A15A")
        self.btn_delete.configure(state="disabled")
        self.frm_password.configure(placeholder_text="Password (obligatorio al crear)", show="*")
        self.form_title.configure(text="📝 Crear Nuevo Usuario")
        self.frm_nombre.focus_set()

    def on_search(self):
        term = self.search_entry.get().strip()
        if not term:
            self.load_users()
            return
        rows = find_users_by_term(term)
        self.render_table(rows)

    def load_users(self):
        rows = get_all_users()
        self.render_table(rows)

    def render_table(self, rows):
        # Limpia filas previas
        for widget in self.scrollable_table_frame.winfo_children():
            widget.destroy()

        # Encabezados de la Tabla (sin ID)
        headers = ["NOMBRE", "APELLIDO", "USUARIO", "ROL", "ACCIÓN"]
        
        # Contenedor del encabezado
        header_row_frame = ctk.CTkFrame(self.scrollable_table_frame, fg_color=PRIMARY_COLOR, corner_radius=0)
        header_row_frame.grid(row=0, column=0, columnspan=5, sticky="ew", padx=0, pady=0)
        
        # Peso de columnas para el encabezado (alineación)
        header_row_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        header_row_frame.grid_columnconfigure(4, weight=0)

        for col, h in enumerate(headers):
            padx_val = 10 
            ctk.CTkLabel(header_row_frame, text=h, font=ctk.CTkFont(weight="bold"), 
                         text_color="white", anchor="w").grid(row=0, column=col, padx=padx_val, pady=8, sticky="ew")
        
        if not rows:
            ctk.CTkLabel(self.scrollable_table_frame, text="No hay usuarios registrados.", fg_color="transparent").grid(row=1, column=0, columnspan=5, pady=20)
            return

        # Rellenar filas
        for r_index, r in enumerate(rows, start=1):
            row_color = "#F0F0F0" if r_index % 2 == 0 else "white" 
            row_frame = ctk.CTkFrame(self.scrollable_table_frame, fg_color=row_color, corner_radius=0)
            row_frame.grid(row=r_index, column=0, columnspan=5, sticky="ew", padx=0, pady=(0,1))
            
            # Peso de columnas para las filas de datos (alineación)
            row_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            row_frame.grid_columnconfigure(4, weight=0) 

            # Columnas de datos
            data_cols = [
                r.get("nombre", "")[:30],
                r.get("apellido", "")[:30],
                r.get("usuario", "")[:20],
                str(r.get("rol", ""))
            ]
            
            for col, data in enumerate(data_cols):
                ctk.CTkLabel(row_frame, text=data, anchor="w").grid(row=0, column=col, padx=10, pady=8, sticky="ew")

            # Botón seleccionar
            select_btn = ctk.CTkButton(row_frame, text="Seleccionar", width=100, font=ctk.CTkFont(size=11),
                                     command=lambda uid=r.get("usuario_id"): self._select_row(uid),
                                     fg_color=PRIMARY_COLOR, hover_color="#2A7BBC")
            select_btn.grid(row=0, column=4, padx=10, pady=5, sticky="e") 

    def _select_row(self, user_id):
        data = get_user_by_id(user_id)
        if not data:
            messagebox.showerror("Seleccionar", "No se encontró el usuario.")
            return
        
        self.clear_form() 
        self.editing_user_id = user_id
        
        # Rellenar todos los campos (excepto contraseña por seguridad)
        self.frm_nombre.insert(0, data["nombre"])
        self.frm_apellido.insert(0, data["apellido"])
        self.frm_usuario.insert(0, data["usuario"])
        self.role_menu.set(data.get("rol", VALID_ROLES[0] if VALID_ROLES else ""))
        
        # Actualizar UI a modo edición (sin ID)
        full_name = f"{data.get('nombre', '')} {data.get('apellido', '')}"
        self.form_title.configure(text=f"✏️ Editar Usuario: {full_name.strip()}")
        
        self.btn_save.configure(text="Actualizar", fg_color=PRIMARY_COLOR, hover_color="#2A7BBC")
        self.btn_delete.configure(state="normal")
        self.frm_password.configure(placeholder_text="Password (no dejar vacio)")
        self.frm_nombre.focus_set()

    def open_add_form(self):
        self.clear_form()
        self.frm_nombre.focus_set()

    def on_delete_selected(self):
        if not self.editing_user_id:
            messagebox.showwarning("Eliminar", "Selecciona primero una fila.")
            return
        
        nombre_usuario = self.frm_usuario.get()
        confirm = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de eliminar el usuario '{nombre_usuario}'?")
        
        if not confirm:
            return
        
        success, msg = delete_user(self.editing_user_id)
        if success:
            messagebox.showinfo("Eliminar", msg)
            self.clear_form()
            self.load_users()
        else:
            messagebox.showerror("Eliminar", msg)

    def on_save(self):
        nombre = self.frm_nombre.get().strip()
        apellido = self.frm_apellido.get().strip()
        usuario = self.frm_usuario.get().strip()
        password = self.frm_password.get().strip()
        rol = self.role_menu.get().strip()

        # Validaciones de campos
        if not nombre or not apellido or not usuario:
            messagebox.showwarning("Validación", "Nombre, apellido y usuario son obligatorios.")
            return
        if rol not in VALID_ROLES:
            messagebox.showwarning("Validación", f"Rol inválido. Opciones: {', '.join(VALID_ROLES)}")
            return
        if len(usuario) < 3:
            messagebox.showwarning("Validación", "El usuario debe tener al menos 3 caracteres.")
            return

        if self.editing_user_id:  # Actualizar
            plain_password = password if password else None
            success, msg = update_user(self.editing_user_id, nombre, apellido, usuario, plain_password, rol)
            if success:
                messagebox.showinfo("Actualizar", msg)
                self.clear_form()
                self.load_users()
            else:
                messagebox.showerror("Actualizar", msg)
        else:  # Crear nuevo
            if not password:
                messagebox.showwarning("Validación", "La contraseña es obligatoria al crear un usuario.")
                return
            success, msg = add_user(nombre, apellido, usuario, password, rol)
            if success:
                messagebox.showinfo("Crear", msg)
                self.clear_form()
                self.load_users()
            else:
                messagebox.showerror("Crear", msg)
