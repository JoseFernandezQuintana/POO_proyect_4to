import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from PIL import Image, ImageTk 
import mysql.connector
from ui_utils import mostrar_loading

# Importación de Vistas
from agendar_view import AgendarCitaFrame
from calendario_view import CalendarFrame
from pagos_view import PagosFrame
from mod_agendar_view import ModificarCitaView

# Admin / Configuración
from conf_view import ConfFrame
from profile_view import ProfileFrame
from admin_usuarios_view import AdminUsuariosFrame
from admin_servicios_view import AdminServiciosFrame
from admin_reportes_view import AdminReportesFrame

class DashboardApp:
    def __init__(self, uid, u_nom, u_rol, root):
        self.root = root
        self.root.user_id = uid 
        self.root.rol = u_rol
        self.username = u_nom
        
        self.root.title("Futuras Sonrisas - Sistema de Agendado")
        self.main_bg_color = "#F4F6F7" 
        self.root.configure(fg_color=self.main_bg_color)
        
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Vistas Estáticas
        self.views = {
            "agendar": AgendarCitaFrame,
            "pagos": PagosFrame
        }
        
        # Variables de botones
        self.b_ag = None
        self.b_ci = None
        self.b_pa = None
        
        self.create_header()
        self.create_nav()
        
        self.container = ctk.CTkFrame(self.root, fg_color=self.main_bg_color, corner_radius=0)
        self.container.grid(row=2, column=0, sticky="nsew", padx=25, pady=(0, 20))
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        self.curr_view = None
        self.conf_panel = None
        self.ignore_next_click = False 
        
        self.root.bind_all("<Button-1>", self.chk_click, add="+")
        
        self.nav_to("agendar")

    def nav_to(self, name):
        if not self.b_ag or not self.b_ci or not self.b_pa:
            self.root.after(100, lambda: self.nav_to(name)) 
            return

        for b in [self.b_ag, self.b_ci, self.b_pa]: 
            b.configure(fg_color="transparent", text_color="black")
        
        color_activo = "#D6EAF8" 
        
        if name == "agendar": self.b_ag.configure(fg_color=color_activo, text_color="#154360")
        elif name == "citas": self.b_ci.configure(fg_color=color_activo, text_color="#154360")
        elif name == "pagos": self.b_pa.configure(fg_color=color_activo, text_color="#154360")
        
        self._limpiar_contenedor()
        
        # --- CAMBIO: USAMOS TIPO='CIRCULO' ---
        mostrar_loading(self.container, 500, lambda: self._load_view(name), tipo="circulo", mensaje="Cargando vista...")

    def obtener_ruta_foto(self):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="futuras_sonrisas", port=3306
            )
            cursor = conn.cursor()
            cursor.execute("SELECT foto_perfil FROM usuarios WHERE id = %s", (self.root.user_id,))
            res = cursor.fetchone()
            conn.close()
            if res and res[0]:
                return res[0]
            return None
        except:
            return None

    def create_header(self):
        h = ctk.CTkFrame(self.root, height=60, fg_color="#154360", corner_radius=0)
        h.grid(row=0, column=0, sticky="ew")
        
        # LOGO CLICKEABLE
        logo_frame = ctk.CTkFrame(h, fg_color="transparent", cursor="hand2") 
        logo_frame.pack(side="left", padx=10, pady=5)
        
        lbl_tit = ctk.CTkLabel(logo_frame, text="FUTURAS SONRISAS", font=("Segoe UI", 18, "bold"), text_color="white")
        lbl_tit.pack(anchor="w")
        lbl_sub = ctk.CTkLabel(logo_frame, text="Sistema de Gestión de Agendado", font=("Segoe UI", 11), text_color="#A9CCE3")
        lbl_sub.pack(anchor="w")
        
        logo_frame.bind("<Button-1>", lambda e: self.nav_to("agendar"))
        lbl_tit.bind("<Button-1>", lambda e: self.nav_to("agendar"))
        lbl_sub.bind("<Button-1>", lambda e: self.nav_to("agendar"))

        # USUARIO
        r = ctk.CTkFrame(h, fg_color="transparent")
        r.pack(side="right", padx=20)
        
        foto_path = self.obtener_ruta_foto()
        imagen_perfil = None
        texto_emoji = ""

        if foto_path and os.path.exists(foto_path):
            try:
                img_pil = Image.open(foto_path)
                width, height = img_pil.size
                new_side = min(width, height)
                left = (width - new_side) / 2
                top = (height - new_side) / 2
                right = (width + new_side) / 2
                bottom = (height + new_side) / 2
                img_cropped = img_pil.crop((left, top, right, bottom))
                img_resized = img_cropped.resize((35, 35), Image.Resampling.LANCZOS)
                imagen_perfil = ctk.CTkImage(img_resized, size=(35, 35))
            except: pass 
        
        if not imagen_perfil:
            rol_lower = self.root.rol.lower()
            if "doctor" in rol_lower: texto_emoji = "👩‍⚕️"
            elif "recepcionista" in rol_lower: texto_emoji = "💁‍♀️"
            else: texto_emoji = "🧑‍💻"

        btn_perfil = ctk.CTkButton(
            r, 
            text=f"  {texto_emoji}   {self.username} | {self.root.rol}  ", 
            image=imagen_perfil,
            compound="left", 
            font=("Segoe UI", 12, "bold"),
            text_color="white",
            fg_color="transparent",
            hover_color="#1F618D",
            command=self.abrir_mi_perfil_directo, 
            corner_radius=20
        )
        btn_perfil.pack(side="left", padx=(0, 10))

        self.btn_conf = ctk.CTkButton(
            r, text="⚙️", width=35, height=30,
            command=self.toggle_conf, 
            fg_color="#1A5276", hover_color="#21618C", 
            text_color="white", corner_radius=6
        )
        self.btn_conf.pack(side="left")

    def create_nav(self):
        n = ctk.CTkFrame(self.root, fg_color="white", corner_radius=0, height=70)
        n.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        
        center_box = ctk.CTkFrame(n, fg_color="transparent")
        center_box.pack(anchor="center", pady=15)

        cf = {
            "font": ("Segoe UI", 13, "bold"), 
            "fg_color": "transparent", 
            "hover_color": "#E5E8E8",  
            "text_color": "black",     
            "height": 40, 
            "width": 120,
            "corner_radius": 20,       
            "border_width": 0          
        }
        
        self.b_ag = ctk.CTkButton(center_box, text="📅 Agendar", command=lambda: self.nav_to("agendar"), **cf)
        self.b_ag.pack(side="left", padx=5)

        sep1 = ctk.CTkFrame(center_box, width=2, height=25, fg_color="#D5DBDB")
        sep1.pack(side="left", padx=5)

        self.b_ci = ctk.CTkButton(center_box, text="📂 Citas", command=lambda: self.nav_to("citas"), **cf)
        self.b_ci.pack(side="left", padx=5)

        sep2 = ctk.CTkFrame(center_box, width=2, height=25, fg_color="#D5DBDB")
        sep2.pack(side="left", padx=5)

        self.b_pa = ctk.CTkButton(center_box, text="💰 Pagos", command=lambda: self.nav_to("pagos"), **cf)
        self.b_pa.pack(side="left", padx=5)

    def nav_to(self, name):
        if not self.b_ag or not self.b_ci or not self.b_pa:
            self.root.after(100, lambda: self.nav_to(name)) 
            return

        for b in [self.b_ag, self.b_ci, self.b_pa]: 
            b.configure(fg_color="transparent", text_color="black")
        
        color_activo = "#D6EAF8" 
        
        if name == "agendar": 
            self.b_ag.configure(fg_color=color_activo, text_color="#154360")
        elif name == "citas": 
            self.b_ci.configure(fg_color=color_activo, text_color="#154360")
        elif name == "pagos": 
            self.b_pa.configure(fg_color=color_activo, text_color="#154360")
        
        self.root.after(50, lambda: self._load_view(name))

    # --- FUNCIÓN NUEVA: LIMPIEZA NUCLEAR ---
    def _limpiar_contenedor(self):
        # 1. Destruir referencia lógica
        if self.curr_view: 
            try:
                self.curr_view.destroy()
            except: pass
            self.curr_view = None
        
        # 2. BARRIDO FÍSICO: Destruir cualquier hijo que quede en el contenedor
        # Esto elimina barras de scroll fantasmas o frames pegados
        for widget in self.container.winfo_children():
            try:
                widget.destroy()
            except: pass
            
        # 3. Forzar actualización de la interfaz para redibujar el vacío
        self.container.update_idletasks()

    def _load_view(self, name):
        # Usamos la limpieza nuclear
        self._limpiar_contenedor()
        
        if name == "citas":
            self.curr_view = CalendarFrame(self.container, callback_modificar=self.ir_a_modificar_cita)
            self.curr_view.pack(fill="both", expand=True)
        else:
            cls = self.views.get(name)
            if cls: 
                self.curr_view = cls(self.container)
                self.curr_view.pack(fill="both", expand=True)

    def _load_admin(self, cls_or_lambda):
        self._limpiar_contenedor()
        
        if self.b_ag and self.b_ci and self.b_pa:
            for b in [self.b_ag, self.b_ci, self.b_pa]: 
                b.configure(fg_color="transparent", text_color="black")
        
        def _accion_real():
            if isinstance(cls_or_lambda, type):
                self.curr_view = cls_or_lambda(self.container)
            else:
                self.curr_view = cls_or_lambda(self.container)
            self.curr_view.pack(fill="both", expand=True)

        # --- CAMBIO: USAMOS TIPO='CIRCULO' ---
        mostrar_loading(self.container, 500, _accion_real, tipo="circulo", mensaje="Cargando...")

    def ir_a_modificar_cita(self, cita_id):
        # También aquí por si acaso
        self._limpiar_contenedor()
        
        self.curr_view = ModificarCitaView(
            self.container, 
            cita_id, 
            callback_volver=self.volver_a_citas,
            current_user_id=self.root.user_id
        )
        self.curr_view.pack(fill="both", expand=True)

    def volver_a_citas(self):
        self.nav_to("citas")

    def toggle_conf(self):
        if self.conf_panel: 
            self.conf_panel.destroy()
            self.conf_panel = None
        else:
            self.conf_panel = ConfFrame(self.root, self.on_conf_action, self.root.rol)
            self.conf_panel.place(relx=1.0, y=67, anchor="ne", relheight=0.9) 
            self.conf_panel.lift()
            self.ignore_next_click = True 

    def chk_click(self, e):
        if self.ignore_next_click:
            self.ignore_next_click = False
            return
        if self.conf_panel:
            try:
                widget = e.widget
                if str(self.conf_panel) not in str(widget) and widget != self.btn_conf:
                    self.conf_panel.destroy()
                    self.conf_panel = None
            except: pass

    def abrir_mi_perfil_directo(self):
        if isinstance(self.curr_view, ProfileFrame):
            return 
        self._load_admin(lambda parent: ProfileFrame(parent, self.root.user_id, self.root.rol))

    def on_conf_action(self, act):
        if self.conf_panel: self.conf_panel.destroy(); self.conf_panel=None
        
        # --- LÓGICA DE PERMISOS JERÁRQUICOS ---
        rol_efectivo = self.root.rol # Por defecto es tu propio rol

        # Si soy Recepcionista y quiero entrar a zonas restringidas, pido permiso
        if self.root.rol == "Recepcionista" and act in ["Administración de Cuentas", "Cotización de Servicios"]:
            rol_autorizado = self._solicitar_permiso_supervisor()
            if not rol_autorizado:
                return # Si cancela o falla, no entramos
            rol_efectivo = rol_autorizado # HEREDA EL PODER (Admin o Doctora)

        # --- NAVEGACIÓN CON ROL EFECTIVO ---
        if act == "Mi Perfil": 
            self.abrir_mi_perfil_directo()
        
        elif act == "Administración de Cuentas": 
            # Pasamos el rol_efectivo a la vista
            self._load_admin(lambda p: AdminUsuariosFrame(p, rol_contexto=rol_efectivo))
        
        elif act == "Cotización de Servicios": 
            # Pasamos el rol_efectivo a la vista
            self._load_admin(lambda p: AdminServiciosFrame(p, rol_contexto=rol_efectivo))
            
        elif act == "Reportes y Estadisticas": 
            self._load_admin(AdminReportesFrame)
            
        elif "Cerrar Sesión" in act:
            if messagebox.askyesno("Cerrar Sesión", "¿Deseas cerrar tu sesión actual?"):
                self.logout()
        elif "Cerrar App" in act:
             if messagebox.askyesno("Salir", "¿Estás seguro de que quieres salir?"):
                self.root.destroy(); sys.exit()

    def _solicitar_permiso_supervisor(self):
        """Muestra popup y retorna el ROL del supervisor que autorizó (o None)"""
        dialog = ctk.CTkInputDialog(text="Requiere autorización (Admin/Doctora)\nIngrese Usuario:", title="Acceso Restringido")
        # Truco para centrar el popup (opcional)
        try: dialog.geometry(f"+{self.root.winfo_x()+100}+{self.root.winfo_y()+100}")
        except: pass
        
        user = dialog.get_input()
        if not user: return None
        
        dialog_pass = ctk.CTkInputDialog(text=f"Usuario: {user}\nIngrese Contraseña:", title="Credenciales")
        try: dialog_pass.geometry(f"+{self.root.winfo_x()+100}+{self.root.winfo_y()+100}")
        except: pass
        
        pwd = dialog_pass.get_input()
        if not pwd: return None

        # Validamos usando la BD directamente o controller
        # Nota: Usamos database.validar_login para obtener el rol real del supervisor
        import database
        datos = database.validar_login(user, pwd)
        
        if datos:
            rol_sup = datos['rol']
            if rol_sup in ["Administrador", "Doctora"]:
                messagebox.showinfo("Autorizado", f"Acceso concedido por: {datos['nombre_completo']} ({rol_sup})")
                return rol_sup # RETORNAMOS EL ROL DEL JEFE
            else:
                messagebox.showerror("Error", "Este usuario no tiene permisos para autorizar.")
        else:
            messagebox.showerror("Error", "Credenciales incorrectas.")
        
        return None

    def logout(self):
        for widget in self.root.winfo_children(): widget.destroy()
        try:
            from login_view import LoginApp
        except ImportError: return
        def relogin_cb(datos):
            uid, nom, rol, _ = datos
            for w in self.root.winfo_children(): w.destroy()
            try: self.root.state('zoomed')
            except: self.root.geometry("1300x800")
            DashboardApp(uid, nom, rol, self.root)
        LoginApp(self.root, on_login_success=relogin_cb)
