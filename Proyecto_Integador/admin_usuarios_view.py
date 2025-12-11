import customtkinter as ctk
from tkinter import messagebox
from admin_controller import AdminController

# Configuración Visual
BG_MAIN = "#F4F6F9"
WHITE = "#FFFFFF"
ACCENT = "#007BFF"
DANGER = "#DC3545"

class AdminUsuariosFrame(ctk.CTkFrame):
    def __init__(self, master, rol_contexto=None):
        super().__init__(master, fg_color=BG_MAIN)
        self.controller = AdminController()
        self.usuario_seleccionado = None
        
        # Obtener datos de sesión
        try:
            self.rol_actual = rol_contexto if rol_contexto else self.master.master.rol
            self.user_id_sesion = self.master.master.user_id
        except:
            self.rol_actual = "Recepcionista"
            self.user_id_sesion = 0

        # --- EVENTO GLOBAL PARA QUITAR FOCO ---
        # Vinculamos el clic en el fondo principal para soltar el cursor
        self.bind("<Button-1>", self.quitar_foco)

        # Layout Principal
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL IZQUIERDO (LISTA) ---
        self.left_panel = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=10, border_color="#E0E0E0", border_width=1)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.left_panel.bind("<Button-1>", self.quitar_foco) 
        
        ctk.CTkLabel(self.left_panel, text="👥 Gestión de Personal", font=("Segoe UI", 18, "bold"), text_color=ACCENT).pack(pady=15)
        
        # --- ENCABEZADOS DE TABLA (ALINEACIÓN CORREGIDA) ---
        h = ctk.CTkFrame(self.left_panel, fg_color="#F1F1F1", height=35)
        h.pack(fill="x", padx=10)
        
        # TRUCO DE ALINEACIÓN: Usamos 'uniform="cols"' para obligar a que
        # las columnas midan lo mismo aquí que en las filas de abajo.
        h.grid_columnconfigure(0, weight=3, uniform="cols") 
        h.grid_columnconfigure(1, weight=2, uniform="cols") 
        h.grid_columnconfigure(2, weight=1, uniform="cols") 

        ctk.CTkLabel(h, text="   Nombre", font=("Arial", 11, "bold"), anchor="w").grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(h, text="Rol", font=("Arial", 11, "bold"), anchor="center").grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(h, text="Acciones   ", font=("Arial", 11, "bold"), anchor="e").grid(row=0, column=2, sticky="ew", padx=10)

        self.scroll_list = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.scroll_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.scroll_list.bind("<Button-1>", self.quitar_foco) 
        
        # --- PANEL DERECHO (FORMULARIO) ---
        self.right_panel = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=10, border_color="#E0E0E0", border_width=1)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
        self.right_panel.bind("<Button-1>", self.quitar_foco) # Importante para que funcione al clicar la derecha

        self.lbl_form = ctk.CTkLabel(self.right_panel, text="➕ Nuevo Usuario", font=("Segoe UI", 16, "bold"))
        self.lbl_form.pack(pady=15)
        
        self.crear_formulario(self.right_panel)
        
        self.cargar_usuarios()

    def quitar_foco(self, event):
        """Fuerza a la interfaz a dejar de enfocar cualquier Entry"""
        self.focus_set()

    def crear_formulario(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=15)
        
        ctk.CTkLabel(f, text="Nombre Completo *", font=("Arial", 11, "bold")).pack(anchor="w")
        self.ent_nombre = ctk.CTkEntry(f, placeholder_text="Ej: Juan Pérez", height=35, fg_color="#FAFAFA")
        self.ent_nombre.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(f, text="Usuario (Login) *", font=("Arial", 11, "bold")).pack(anchor="w")
        self.ent_user = ctk.CTkEntry(f, placeholder_text="Ej: jperez", height=35, fg_color="#FAFAFA")
        self.ent_user.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(f, text="Contraseña *", font=("Arial", 11, "bold")).pack(anchor="w")
        self.ent_pass = ctk.CTkEntry(f, placeholder_text="Mínimo 4 caracteres", show="*", height=35, fg_color="#FAFAFA")
        self.ent_pass.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(f, text="Rol en Sistema *", font=("Arial", 11, "bold")).pack(anchor="w")
        
        self.cmb_rol = ctk.CTkOptionMenu(
            f, 
            values=["Doctora", "Recepcionista", "Administrador"], 
            fg_color="#FAFAFA", text_color="#333", button_color="#CCC",
            command=self.al_cambiar_rol 
        )
        self.cmb_rol.pack(fill="x", pady=(0, 10))

        # --- CAMPO ESPECIALIDAD ---
        self.lbl_esp = ctk.CTkLabel(f, text="Especialidad (Solo Doctoras) *", font=("Arial", 11, "bold"), text_color="#E67E22")
        self.lbl_esp.pack(anchor="w")
        
        self.ent_especialidad = ctk.CTkEntry(f, placeholder_text="Ej: Ortodoncia, General...", height=35, fg_color="#FAFAFA")
        self.ent_especialidad.pack(fill="x", pady=(0, 20))
        
        self.btn_guardar = ctk.CTkButton(parent, text="GUARDAR USUARIO", height=40, font=("bold", 12), command=self.guardar)
        self.btn_guardar.pack(fill="x", padx=15, pady=5)
        
        self.btn_cancelar = ctk.CTkButton(parent, text="Cancelar Edición", fg_color="gray", hover_color="#666", command=self.reset_form)
        
        # Inicializar estado correcto
        self.al_cambiar_rol("Doctora")

    def al_cambiar_rol(self, rol_seleccionado):
        self.ent_especialidad.configure(state="normal")
        
        if rol_seleccionado == "Doctora":
            curr = self.ent_especialidad.get()
            if curr in ["Administrador", "Recepcionista"]:
                self.ent_especialidad.delete(0, 'end')
            
            self.ent_especialidad.configure(fg_color="#FAFAFA", text_color="#333")
            self.lbl_esp.configure(text="Especialidad *", text_color="#E67E22")
        else:
            self.ent_especialidad.delete(0, 'end')
            self.ent_especialidad.insert(0, rol_seleccionado)
            self.ent_especialidad.configure(state="disabled", fg_color="#E0E0E0", text_color="gray") 
            self.lbl_esp.configure(text="Especialidad (Automática)", text_color="gray")

    def cargar_usuarios(self):
        for w in self.scroll_list.winfo_children(): w.destroy()
        usuarios = self.controller.obtener_usuarios()
        
        if not usuarios:
            ctk.CTkLabel(self.scroll_list, text="No hay usuarios.").pack(pady=20)
            return

        for u in usuarios:
            es_target_admin = (u['rol'] == "Administrador")
            soy_admin_supremo = (self.rol_actual == "Administrador")
            
            # REGLA DE ORO: Si es Admin, solo otro Admin lo toca.
            # Si soy Doctora (o Recepcionista con permiso de Doctora), se bloquea.
            bloqueado = False
            if es_target_admin and not soy_admin_supremo:
                bloqueado = True

            # ... (Creación de la tarjeta visual igual que antes) ...
            card = ctk.CTkFrame(self.scroll_list, fg_color="#FAFAFA", corner_radius=6)
            card.pack(fill="x", pady=3, padx=5)
            card.grid_columnconfigure(0, weight=3, uniform="cols") 
            card.grid_columnconfigure(1, weight=2, uniform="cols") 
            card.grid_columnconfigure(2, weight=1, uniform="cols") 

            # Nombre y Rol (Igual)
            lbl_nom = ctk.CTkLabel(card, text=u['nombre_completo'], font=("Segoe UI", 12, "bold"), anchor="w")
            lbl_nom.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
            col_rol = ACCENT if u['rol'] == "Administrador" else ("#28A745" if u['rol']=="Doctora" else "gray")
            ctk.CTkLabel(card, text=u['rol'], text_color=col_rol, font=("Arial", 10, "bold")).grid(row=0, column=1)

            # Botones
            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.grid(row=0, column=2, sticky="e", padx=10)

            if not bloqueado:
                ctk.CTkButton(btns, text="✏️", width=30, fg_color="#FFC107", text_color="black", hover_color="#FFD54F", 
                              command=lambda x=u: self.editar(x)).pack(side="left", padx=2)
                
                # No puedes borrarte a ti mismo
                if u['id'] != self.user_id_sesion:
                    ctk.CTkButton(btns, text="🗑️", width=30, fg_color=DANGER, hover_color="#C82333", 
                                  command=lambda x=u['id']: self.eliminar(x)).pack(side="left", padx=2)
            else:
                # Icono de candado si está bloqueado por jerarquía
                ctk.CTkLabel(btns, text="🔒", text_color="gray", font=("Arial", 14)).pack(padx=5)

    def guardar(self):
        nom = self.ent_nombre.get().strip()
        usr = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()
        rol = self.cmb_rol.get()
        esp_input = self.ent_especialidad.get().strip()

        if not nom or not usr:
            messagebox.showwarning("Incompleto", "Nombre y Usuario requeridos.")
            return
        
        if rol == "Doctora":
            if not esp_input or esp_input in ["Administrador", "Recepcionista"]:
                messagebox.showerror("Requerido", "Para registrar una DOCTORA es obligatorio llenar el campo 'Especialidad'.")
                return
            esp_final = esp_input
        else:
            esp_final = rol

        if not self.usuario_seleccionado and len(pwd) < 4:
            messagebox.showwarning("Seguridad", "Contraseña muy corta.")
            return

        if self.usuario_seleccionado:
            ok, msg = self.controller.actualizar_usuario(self.usuario_seleccionado['id'], nom, usr, rol, pwd, esp_final)
        else:
            ok, msg = self.controller.crear_usuario(nom, usr, pwd, rol, esp_final)
        
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.reset_form()
            self.cargar_usuarios()
        else:
            messagebox.showerror("Error", msg)

    def editar(self, u):
        self.usuario_seleccionado = u
        self.lbl_form.configure(text="✏️ Editando Usuario", text_color="#E67E22")
        self.btn_guardar.configure(text="ACTUALIZAR", fg_color="#E67E22", hover_color="#D35400")
        
        self.ent_nombre.delete(0, 'end'); self.ent_nombre.insert(0, u['nombre_completo'])
        self.ent_user.delete(0, 'end'); self.ent_user.insert(0, u['usuario'])
        self.ent_pass.delete(0, 'end'); self.ent_pass.configure(placeholder_text="(Vacío para no cambiar)")
        
        self.cmb_rol.set(u['rol'])
        self.al_cambiar_rol(u['rol'])
        
        if u['rol'] == "Doctora" and u.get('especialidad'):
            self.ent_especialidad.delete(0, 'end')
            self.ent_especialidad.insert(0, u['especialidad'])
        
        self.btn_cancelar.pack(fill="x", padx=15, pady=5)

    def eliminar(self, uid):
        if messagebox.askyesno("Confirmar", "¿Desactivar usuario?"):
            ok, msg = self.controller.eliminar_usuario(uid, self.user_id_sesion, self.rol_sesion)
            if ok:
                messagebox.showinfo("Listo", msg)
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", msg)

    def reset_form(self):
        self.usuario_seleccionado = None
        self.lbl_form.configure(text="➕ Nuevo Usuario", text_color="#333")
        self.btn_guardar.configure(text="GUARDAR USUARIO", fg_color=ACCENT, hover_color="#0056b3")
        
        self.ent_nombre.delete(0, 'end')
        self.ent_user.delete(0, 'end')
        self.ent_pass.delete(0, 'end')
        
        self.ent_pass.configure(placeholder_text="Mínimo 4 caracteres")
        self.cmb_rol.set("Doctora")
        
        self.al_cambiar_rol("Doctora")
        self.ent_especialidad.delete(0, 'end') 
        
        self.btn_cancelar.pack_forget()
        self.focus_set()
