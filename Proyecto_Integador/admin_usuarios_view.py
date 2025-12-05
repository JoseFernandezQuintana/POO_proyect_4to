import customtkinter as ctk
from tkinter import messagebox
from admin_controller import AdminController

# ... (Imports y colores igual que antes) ...
BG_MAIN = "#F4F6F9"
WHITE = "#FFFFFF"
ACCENT = "#007BFF"

class AdminUsuariosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_MAIN)
        self.controller = AdminController()
        
        # Recuperar datos de sesión
        try:
            self.rol_sesion = self.master.master.rol
            # Necesitamos el ID del usuario actual para el anti-suicidio
            # Como no lo guardamos en self.master, lo buscaremos por nombre de usuario (un pequeño hack seguro)
            self.user_sesion = self.master.master.username 
            # Idealmente DashboardApp debería tener self.user_id, pero lo inferimos:
            all_users = self.controller.obtener_usuarios()
            self.uid_sesion = next((u['id'] for u in all_users if u['nombre_completo'] == self.user_sesion or u['usuario'] == self.user_sesion), 0)
        except:
            self.rol_sesion = "Recepcionista"
            self.uid_sesion = 0

        # ... (Layout de 2 columnas igual que antes) ...
        # (Copia el __init__ visual que te pasé en la respuesta anterior, es idéntico)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL IZQUIERDO: LISTA ---
        left_panel = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=10)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(left_panel, text="👥 Gestión de Personal", font=("Segoe UI", 18, "bold"), text_color=ACCENT).pack(pady=15)
        self.scroll_list = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.scroll_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        # --- PANEL DERECHO: FORMULARIO ---
        right_panel = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=10)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.lbl_form = ctk.CTkLabel(right_panel, text="➕ Nuevo Usuario", font=("Segoe UI", 16, "bold"))
        self.lbl_form.pack(pady=15)
        self.crear_formulario(right_panel)
        
        self.cargar_usuarios()

    def crear_formulario(self, parent):
        # (Igual que antes)
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=15)
        self.ent_nombre = ctk.CTkEntry(f, placeholder_text="Nombre"); self.ent_nombre.pack(fill="x", pady=5)
        self.ent_user = ctk.CTkEntry(f, placeholder_text="Usuario"); self.ent_user.pack(fill="x", pady=5)
        self.ent_pass = ctk.CTkEntry(f, placeholder_text="Contraseña"); self.ent_pass.pack(fill="x", pady=5)
        ctk.CTkLabel(f, text="Rol:").pack(anchor="w")
        self.cmb_rol = ctk.CTkOptionMenu(f, values=["Doctora", "Recepcionista", "Administrador"])
        self.cmb_rol.pack(fill="x", pady=(0,10))
        self.btn_guardar = ctk.CTkButton(parent, text="Guardar", command=self.guardar)
        self.btn_guardar.pack(fill="x", padx=15, pady=10)
        self.btn_cancelar = ctk.CTkButton(parent, text="Cancelar", fg_color="gray", command=self.reset_form)

    def cargar_usuarios(self):
        for w in self.scroll_list.winfo_children(): w.destroy()
        usuarios = self.controller.obtener_usuarios()
        
        for u in usuarios:
            # Regla visual: Si soy Doctora, NO puedo editar a un Administrador
            es_intocable = (self.rol_sesion == "Doctora" and u['rol'] == "Administrador")
            
            card = ctk.CTkFrame(self.scroll_list, fg_color="#F9F9F9")
            card.pack(fill="x", pady=3)
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", padx=10)
            ctk.CTkLabel(info, text=u['nombre_completo'], font=("bold",12)).pack(anchor="w")
            ctk.CTkLabel(info, text=u['rol'], font=("Arial",11), text_color="gray").pack(anchor="w")

            if not es_intocable:
                btns = ctk.CTkFrame(card, fg_color="transparent")
                btns.pack(side="right", padx=5)
                ctk.CTkButton(btns, text="✏️", width=30, fg_color="#FFC107", text_color="black", 
                              command=lambda x=u: self.editar(x)).pack(side="left", padx=2)
                ctk.CTkButton(btns, text="🗑️", width=30, fg_color="#DC3545", 
                              command=lambda x=u['id']: self.eliminar(x)).pack(side="left", padx=2)
            else:
                ctk.CTkLabel(card, text="🔒 Admin", text_color="gray", font=("bold",10)).pack(side="right", padx=10)

    def eliminar(self, uid):
        # Pasamos ID de sesión y Rol de sesión para que el Controller valide
        if messagebox.askyesno("Confirmar", "¿Desactivar usuario?"):
            ok, msg = self.controller.eliminar_usuario(uid, self.uid_sesion, self.rol_sesion)
            if ok: messagebox.showinfo("Listo", msg); self.cargar_usuarios()
            else: messagebox.showerror("Error", msg)
    
    # ... (Resto de métodos editar, guardar, reset_form iguales al código anterior) ...
    # Solo asegúrate de copiar la lógica del método guardar que te pasé antes.
    def guardar(self):
        nom = self.ent_nombre.get(); usr = self.ent_user.get(); pwd = self.ent_pass.get(); rol = self.cmb_rol.get()
        # Si estoy editando (self.usuario_seleccionado existe)...
        if hasattr(self, 'usuario_seleccionado') and self.usuario_seleccionado:
             ok, msg = self.controller.actualizar_usuario(self.usuario_seleccionado['id'], nom, usr, rol, pwd)
        else:
             ok, msg = self.controller.crear_usuario(nom, usr, pwd, rol)
        
        if ok: messagebox.showinfo("Éxito", msg); self.reset_form(); self.cargar_usuarios()
        else: messagebox.showerror("Error", msg)

    def editar(self, u):
        self.usuario_seleccionado = u
        self.lbl_form.configure(text="✏️ Editar", text_color="#FFC107")
        self.btn_guardar.configure(text="Actualizar", fg_color="#FFC107", text_color="black")
        self.btn_cancelar.pack(fill="x", padx=15, pady=5)
        self.ent_nombre.delete(0,'end'); self.ent_nombre.insert(0, u['nombre_completo'])
        self.ent_user.delete(0,'end'); self.ent_user.insert(0, u['usuario'])
        self.cmb_rol.set(u['rol'])

    def reset_form(self):
        self.usuario_seleccionado = None
        self.lbl_form.configure(text="➕ Nuevo Usuario", text_color="#333")
        self.btn_guardar.configure(text="Guardar", fg_color="#007BFF", text_color="white")
        self.btn_cancelar.pack_forget()
        self.ent_nombre.delete(0,'end'); self.ent_user.delete(0,'end'); self.ent_pass.delete(0,'end')