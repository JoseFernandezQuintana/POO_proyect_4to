import customtkinter as ctk
from tkinter import messagebox
from admin_controller import AdminController

class ProfileFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F4F6F9")
        self.controller = AdminController()
        
        # Obtener datos de sesión
        try:
            self.username = self.master.master.username
            all_users = self.controller.obtener_usuarios()
            self.user_data = next((u for u in all_users if u['nombre_completo'] == self.username or u['usuario'] == self.username), None)
        except:
            self.user_data = None

        # --- CAMBIO DE TAMAÑO AQUÍ (500x550) ---
        self.card = ctk.CTkFrame(self, fg_color="white", corner_radius=15, width=500, height=550)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.grid_propagate(False) 
        
        # Título
        ctk.CTkLabel(self.card, text="👤 Mi Perfil", font=("Segoe UI", 22, "bold"), text_color="#007BFF").pack(pady=(25, 10))
        
        # --- SELECTOR DE ACCIÓN ---
        ctk.CTkLabel(self.card, text="¿Qué deseas modificar?", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(0, 5))
        
        # Botones un poco más compactos en altura pero anchos
        self.selector = ctk.CTkSegmentedButton(self.card, values=["Datos Personales", "Seguridad (Contraseña)"], command=self.cambiar_vista, height=35)
        self.selector.set("Datos Personales")
        self.selector.pack(pady=10, padx=40, fill="x")

        # --- CONTENEDOR VISTAS ---
        self.frame_contenido = ctk.CTkFrame(self.card, fg_color="transparent")
        self.frame_contenido.pack(fill="both", expand=True, padx=40, pady=5)
        
        # VISTA 1: DATOS
        self.frm_datos = ctk.CTkFrame(self.frame_contenido, fg_color="transparent")
        ctk.CTkLabel(self.frm_datos, text="Nombre Completo:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10,0))
        self.ent_nom = ctk.CTkEntry(self.frm_datos, placeholder_text="Escribe tu nombre...", height=40)
        self.ent_nom.pack(fill="x", pady=(5, 15))
        
        ctk.CTkLabel(self.frm_datos, text="Usuario (Login):", font=("Arial", 11, "bold")).pack(anchor="w")
        self.ent_usr = ctk.CTkEntry(self.frm_datos, placeholder_text="Escribe tu usuario...", height=40)
        self.ent_usr.pack(fill="x", pady=5)
        
        # VISTA 2: PASSWORD
        self.frm_pass = ctk.CTkFrame(self.frame_contenido, fg_color="transparent")
        ctk.CTkLabel(self.frm_pass, text="Nueva Contraseña:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10,0))
        self.ent_pwd_new = ctk.CTkEntry(self.frm_pass, placeholder_text="Mínimo 4 caracteres", show="*", height=40)
        self.ent_pwd_new.pack(fill="x", pady=(5, 15))
        
        ctk.CTkLabel(self.frm_pass, text="Confirmar Contraseña:", font=("Arial", 11, "bold")).pack(anchor="w")
        self.ent_pwd_conf = ctk.CTkEntry(self.frm_pass, placeholder_text="Repite la contraseña", show="*", height=40)
        self.ent_pwd_conf.pack(fill="x", pady=5)
        
        # Pre-llenar datos
        if self.user_data:
            self.ent_nom.insert(0, self.user_data['nombre_completo'])
            self.ent_usr.insert(0, self.user_data['usuario'])

        # Botón Guardar
        self.btn_guardar = ctk.CTkButton(self.card, text="GUARDAR CAMBIOS", command=self.guardar, height=45, font=("Segoe UI", 13, "bold"))
        self.btn_guardar.pack(pady=30, padx=40, fill="x")
        
        # Iniciar vista
        self.cambiar_vista("Datos Personales")

    def cambiar_vista(self, valor):
        # Limpiar frame
        self.frm_datos.pack_forget()
        self.frm_pass.pack_forget()
        
        if valor == "Datos Personales":
            self.frm_datos.pack(fill="both", expand=True)
        else:
            self.frm_pass.pack(fill="both", expand=True)

    def guardar(self):
        if not self.user_data: return
        
        modo = self.selector.get()
        nom = self.user_data['nombre_completo']
        usr = self.user_data['usuario']
        pwd = ""
        
        if modo == "Datos Personales":
            nom = self.ent_nom.get().strip()
            usr = self.ent_usr.get().strip()
            if not nom or not usr:
                messagebox.showwarning("Atención", "Nombre y Usuario no pueden estar vacíos.")
                return
                
        else: # Seguridad
            p1 = self.ent_pwd_new.get()
            p2 = self.ent_pwd_conf.get()
            
            if not p1:
                messagebox.showwarning("Atención", "Escribe una contraseña.")
                return
            if p1 != p2:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return
            if len(p1) < 4:
                messagebox.showwarning("Seguridad", "La contraseña es muy corta (mín 4).")
                return
            pwd = p1

        # Enviar al controlador
        ok, msg = self.controller.actualizar_mi_perfil(self.user_data['id'], nom, usr, pwd)
        
        if ok: 
            messagebox.showinfo("Éxito", "Perfil actualizado correctamente.\nSi cambiaste datos críticos, reinicia sesión.")
            # Limpiar campos de password por seguridad
            self.ent_pwd_new.delete(0, 'end')
            self.ent_pwd_conf.delete(0, 'end')
            if modo == "Seguridad (Contraseña)":
                self.selector.set("Datos Personales")
                self.cambiar_vista("Datos Personales")
        else: 
            messagebox.showerror("Error", msg)