import customtkinter as ctk
from tkinter import messagebox, filedialog
import mysql.connector
from PIL import Image, ImageTk 
import os

# --- Ajusta tus credenciales ---
def conectar_bd():
    try:
        return mysql.connector.connect(
            host="localhost", user="root", password="", database="futuras_sonrisas", port=3306
        )
    except Exception as e:
        messagebox.showerror("Error", f"Error conexión BD: {e}")
        return None

class ProfileFrame(ctk.CTkScrollableFrame): 
    def __init__(self, master, user_id, user_rol, **kwargs):
        super().__init__(master, **kwargs)
        self.user_id = user_id
        self.user_rol = user_rol
        self.photo_path = None 
        
        self.configure(fg_color="#F4F6F7", corner_radius=0)
        self.bind("<Button-1>", lambda e: self.focus_set())

        # Variables Auxiliares (Solo para etiquetas que no son inputs)
        self.label_usuario_titulo = ctk.StringVar(value="Cargando...")

        # Título
        lbl_title = ctk.CTkLabel(self, textvariable=self.label_usuario_titulo, font=("Segoe UI", 24, "bold"), text_color="#1A5276")
        lbl_title.pack(pady=(25, 20), anchor="w", padx=30)
        lbl_title.bind("<Button-1>", lambda e: self.focus_set())

        # --- CONTENEDOR PRINCIPAL ---
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="x", padx=20, pady=10)
        main_container.bind("<Button-1>", lambda e: self.focus_set())

        # =================================================
        # COLUMNA IZQUIERDA: INFORMACIÓN PERSONAL
        # =================================================
        left_panel = ctk.CTkFrame(main_container, fg_color="white", corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        left_panel.bind("<Button-1>", lambda e: self.focus_set())

        ctk.CTkLabel(left_panel, text="Información General", font=("Segoe UI", 15, "bold"), text_color="#2C3E50").pack(pady=(20, 15))

        # Foto
        self.photo_frame = ctk.CTkFrame(left_panel, width=110, height=110, corner_radius=55, fg_color="#EAEAEA")
        self.photo_frame.pack(pady=10)
        self.photo_frame.pack_propagate(False)
        self.photo_label = ctk.CTkLabel(self.photo_frame, text="📷", font=("Segoe UI", 20))
        self.photo_label.pack(expand=True)

        ctk.CTkButton(left_panel, text="Cambiar Foto", command=self.seleccionar_foto, width=110, height=30, fg_color="#5D6D7E", font=("Segoe UI", 11, "bold")).pack(pady=5)

        # CAMPOS IZQUIERDA (Guardamos referencias self.entry_X para usarlas luego)
        self.entry_nombre = self.crear_campo(left_panel, "Nombre Completo", placeholder="Ej. Dra. María Pérez")
        
        self.entry_especialidad = None
        if "Doctor" in self.user_rol:
             self.entry_especialidad = self.crear_campo(left_panel, "Especialidad Médica", placeholder="Ej. Ortodoncia, Endodoncia...")
        
        self.entry_contacto = self.crear_campo(left_panel, "Contacto / Teléfono", placeholder="Ej. 555-000-1234")

        ctk.CTkButton(left_panel, text="Guardar Información Personal", command=self.guardar_datos_personales, 
                      fg_color="#28B463", hover_color="#1D8348", height=35, font=("Segoe UI", 12, "bold")).pack(pady=30, padx=30, fill="x")

        # =================================================
        # COLUMNA DERECHA: SEGURIDAD
        # =================================================
        right_panel = ctk.CTkFrame(main_container, fg_color="white", corner_radius=10)
        right_panel.pack(side="right", fill="both", expand=True)
        right_panel.bind("<Button-1>", lambda e: self.focus_set())

        ctk.CTkLabel(right_panel, text="Configuración de Cuenta", font=("Segoe UI", 15, "bold"), text_color="#2C3E50").pack(pady=(20, 15))

        # Rol (Solo lectura, usamos un Entry deshabilitado o Label)
        self.crear_campo(right_panel, "Rol Asignado", variable_texto=self.user_rol, readonly=True)

        # Usuario
        ctk.CTkLabel(right_panel, text="Usuario de Acceso (Login)", font=("Segoe UI", 11, "bold"), anchor="w", text_color="#7F8C8D").pack(fill="x", padx=30, pady=(15, 0))
        self.entry_usuario = ctk.CTkEntry(right_panel, font=("Segoe UI", 13), height=35, placeholder_text="Usuario para entrar", placeholder_text_color="#909497")
        self.entry_usuario.pack(fill="x", padx=30, pady=(5, 0))
        ctk.CTkLabel(right_panel, text="* Requerido para iniciar sesión", font=("Segoe UI", 9), text_color="#999", anchor="w").pack(fill="x", padx=30)

        ctk.CTkFrame(right_panel, height=1, fg_color="#EAEDED").pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(right_panel, text="Actualizar Contraseña", font=("Segoe UI", 14, "bold"), text_color="#2C3E50").pack(pady=(0, 15))

        # Contraseñas
        self.entry_pass_new = self.crear_campo(right_panel, "Nueva Contraseña", is_password=True, placeholder="Mínimo 4 caracteres")
        self.entry_pass_confirm = self.crear_campo(right_panel, "Confirmar Contraseña", is_password=True, placeholder="Repetir contraseña")

        ctk.CTkButton(right_panel, text="Confirmar Cambios de Cuenta", command=self.guardar_seguridad, 
                      fg_color="#E67E22", hover_color="#D35400", height=35, font=("Segoe UI", 12, "bold")).pack(pady=30, padx=30, fill="x")

        # Cargar datos AL FINAL para rellenar los campos
        self.cargar_datos_iniciales()
        self.cargar_foto_visual()

    def crear_campo(self, parent, label_text, variable_texto=None, readonly=False, is_password=False, placeholder=""):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=30, pady=(10, 0))
        
        lbl = ctk.CTkLabel(f, text=label_text, font=("Segoe UI", 11, "bold"), anchor="w", text_color="#7F8C8D")
        lbl.pack(fill="x")
        
        entry = ctk.CTkEntry(
            parent, 
            font=("Segoe UI", 13), 
            height=35, 
            placeholder_text=placeholder,
            placeholder_text_color="#909497"
        )
        
        # Si pasamos texto fijo (como el Rol), lo insertamos y deshabilitamos
        if variable_texto:
            entry.insert(0, variable_texto)
            
        entry.pack(fill="x", padx=30, pady=(5, 5))
        
        if readonly:
            entry.configure(state="disabled", fg_color="#F8F9F9", text_color="#555", border_color="#E5E8E8")
        if is_password:
             entry.configure(show="*")
        
        return entry

    # --- LÓGICA DE IMAGEN MEJORADA (Recorte Cuadrado + Alta Calidad) ---
    def procesar_imagen_cuadrada(self, path, size=(110, 110)):
        try:
            img = Image.open(path)
            
            # 1. Calcular recorte cuadrado centrado
            width, height = img.size
            new_side = min(width, height)
            
            left = (width - new_side) / 2
            top = (height - new_side) / 2
            right = (width + new_side) / 2
            bottom = (height + new_side) / 2
            
            img_cropped = img.crop((left, top, right, bottom))
            
            # 2. Redimensionar con ALTA CALIDAD (LANCZOS) para evitar borrosidad
            img_resized = img_cropped.resize(size, Image.Resampling.LANCZOS)
            
            return ctk.CTkImage(img_resized, size=size)
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return None

    def seleccionar_foto(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
        if path:
            self.photo_path = path
            self.mostrar_preview(path)

    def mostrar_preview(self, path):
        photo = self.procesar_imagen_cuadrada(path, size=(110, 110))
        if photo:
            self.photo_label.configure(image=photo, text="")

    def cargar_datos_iniciales(self):
        conn = conectar_bd()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT nombre_completo, usuario, especialidad, contacto, foto_perfil FROM usuarios WHERE id = %s"
            cursor.execute(sql, (self.user_id,))
            user = cursor.fetchone()
            if user:
                # Actualizar título
                self.label_usuario_titulo.set(f"Mi Perfil | {user['usuario']}")
                self.original_username = user['usuario']
                
                # INSERTAR DATOS EN LOS CAMPOS (Sin usar variables conflictivas)
                # Primero limpiamos (por si acaso), luego insertamos si hay dato
                
                # Nombre
                if user['nombre_completo']:
                    self.entry_nombre.delete(0, 'end')
                    self.entry_nombre.insert(0, user['nombre_completo'])

                # Usuario
                if user['usuario']:
                    self.entry_usuario.delete(0, 'end')
                    self.entry_usuario.insert(0, user['usuario'])

                # Contacto
                if user['contacto']:
                    self.entry_contacto.delete(0, 'end')
                    self.entry_contacto.insert(0, user['contacto'])

                # Especialidad (Solo si existe el campo)
                if self.entry_especialidad and user['especialidad']:
                     self.entry_especialidad.delete(0, 'end')
                     self.entry_especialidad.insert(0, user['especialidad'])
                
                if user['foto_perfil'] and os.path.exists(user['foto_perfil']):
                    self.photo_path = user['foto_perfil']
        except Exception as e:
            print(e)
        finally:
            conn.close()

    def cargar_foto_visual(self):
        if self.photo_path and os.path.exists(self.photo_path):
            self.mostrar_preview(self.photo_path)

    def guardar_datos_personales(self):
        # Leer directo de los widgets
        val_nombre = self.entry_nombre.get()
        val_contacto = self.entry_contacto.get()
        val_especialidad = self.entry_especialidad.get() if self.entry_especialidad else None

        if not val_nombre:
            messagebox.showwarning("Falta Información", "El nombre completo es obligatorio.")
            return

        conn = conectar_bd()
        if not conn: return
        try:
            cursor = conn.cursor()
            sql = "UPDATE usuarios SET nombre_completo=%s, contacto=%s, foto_perfil=%s"
            params = [val_nombre, val_contacto, self.photo_path]
            
            if "Doctor" in self.user_rol:
                sql += ", especialidad=%s"
                params.append(val_especialidad)
            
            sql += " WHERE id=%s"
            params.append(self.user_id)
            
            cursor.execute(sql, tuple(params))
            conn.commit()
            messagebox.showinfo("Éxito", "Tu información personal ha sido actualizada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def guardar_seguridad(self):
        new_user = self.entry_usuario.get().strip()
        p1 = self.entry_pass_new.get()
        p2 = self.entry_pass_confirm.get()
        
        usuario_cambiado = (new_user != self.original_username)
        pass_cambiado = (len(p1) > 0)

        if not new_user:
            messagebox.showwarning("Error", "El usuario no puede estar vacío.")
            return

        if not usuario_cambiado and not pass_cambiado:
            messagebox.showinfo("Sin cambios", "No hay cambios de seguridad para guardar.")
            return

        if pass_cambiado:
            if len(p1) < 4:
                messagebox.showwarning("Seguridad", "La contraseña debe tener al menos 4 caracteres.")
                return
            if p1 != p2:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return

        msg = "¿Estás seguro de actualizar tu cuenta?"
        if usuario_cambiado:
            msg += f"\n\n⚠️ IMPORTANTE: Estás cambiando tu LOGIN.\nAnterior: {self.original_username}\nNuevo: {new_user}"

        if not messagebox.askyesno("Confirmar Seguridad", msg):
            return

        conn = conectar_bd()
        if not conn: return
        try:
            cursor = conn.cursor()
            sql = "UPDATE usuarios SET usuario=%s"
            params = [new_user]

            if pass_cambiado:
                sql += ", contrasena=%s"
                params.append(p1)
            
            sql += " WHERE id=%s"
            params.append(self.user_id)

            cursor.execute(sql, tuple(params))
            conn.commit()
            
            self.original_username = new_user 
            self.label_usuario_titulo.set(f"Mi Perfil | {new_user}") # Actualizar título visual

            if pass_cambiado:
                self.entry_pass_new.delete(0, 'end')
                self.entry_pass_confirm.delete(0, 'end')
            
            messagebox.showinfo("Cuenta Actualizada", "Los cambios de seguridad se aplicaron correctamente.")

        except mysql.connector.Error as err:
            if err.errno == 1062: 
                messagebox.showerror("Error", "El nombre de usuario ya está en uso.")
            else:
                messagebox.showerror("Error", str(err))
        finally:
            conn.close()
