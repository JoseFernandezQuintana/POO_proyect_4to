import customtkinter as ctk
from tkinter import messagebox
from admin_controller import AdminController
import database 

BG_MAIN = "#F4F6F9"
WHITE = "#FFFFFF"
ACCENT = "#007BFF"

class AdminServiciosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_MAIN)
        self.controller = AdminController()
        
        try: self.rol_actual = self.master.master.rol 
        except: self.rol_actual = "Recepcionista"

        # Barra Superior
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(top_bar, text="🦷 Catálogo de Servicios", font=("Segoe UI", 20, "bold"), text_color=ACCENT).pack(side="left")
        
        txt_btn = "🔒 + Nuevo (Req. Auth)" if self.rol_actual == "Recepcionista" else "+ Nuevo Servicio"
        col_btn = "#6C757D" if self.rol_actual == "Recepcionista" else "#28A745"
        ctk.CTkButton(top_bar, text=txt_btn, fg_color=col_btn, command=self.verificar_permiso_nuevo).pack(side="right")

        # --- BUSCADOR ESTILO IMAGEN (Categoría | Subcategoría | Texto) ---
        search_frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=10)
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # 1. Categoría
        cats = ["Todas"] + database.obtener_columnas_unicas("categoria")
        ctk.CTkLabel(search_frame, text="Categoría:", font=("Arial", 11, "bold")).pack(side="left", padx=(15, 5))
        self.cmb_cat = ctk.CTkOptionMenu(search_frame, values=cats, width=150, command=self.actualizar_subs_filtro)
        self.cmb_cat.pack(side="left", padx=5, pady=10)

        # 2. Subcategoría
        ctk.CTkLabel(search_frame, text="Subcategoría:", font=("Arial", 11, "bold")).pack(side="left", padx=(15, 5))
        self.cmb_sub = ctk.CTkOptionMenu(search_frame, values=["Todas"], width=150, command=lambda x: self.cargar_lista())
        self.cmb_sub.pack(side="left", padx=5, pady=10)

        # 3. Buscador Texto
        self.ent_search = ctk.CTkEntry(search_frame, placeholder_text="Buscar servicio...", height=35)
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=10)
        self.ent_search.bind("<KeyRelease>", lambda e: self.cargar_lista())
        
        # Botón Refrescar
        ctk.CTkButton(search_frame, text="🔄", width=40, command=self.reset_filtros).pack(side="left", padx=(0, 15))

        # Tabla
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.cargar_lista()

    # --- MÉTODOS DEL BUSCADOR ---
    def actualizar_subs_filtro(self, cat):
        """Actualiza el combo de subcategorías del BUSCADOR"""
        if cat == "Todas":
            subs = ["Todas"]
        else:
            subs = ["Todas"] + database.obtener_subcategorias_filtro(cat)
        self.cmb_sub.configure(values=subs)
        self.cmb_sub.set("Todas")
        self.cargar_lista()

    def reset_filtros(self):
        self.cmb_cat.set("Todas")
        self.actualizar_subs_filtro("Todas")
        self.ent_search.delete(0, 'end')
        self.cargar_lista()

    def cargar_lista(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        servicios = database.buscar_servicios_avanzado(
            self.ent_search.get(), 
            self.cmb_cat.get(), 
            self.cmb_sub.get()
        )
        
        if not servicios:
            ctk.CTkLabel(self.scroll, text="Sin resultados.", text_color="gray").pack(pady=20)
            return

        h = ctk.CTkFrame(self.scroll, fg_color="#F0F0F0", height=30)
        h.pack(fill="x", pady=2)
        ctk.CTkLabel(h, text="Servicio", width=300, anchor="w", font=("bold", 12)).pack(side="left", padx=10)
        ctk.CTkLabel(h, text="Precio", width=100, anchor="e", font=("bold", 12)).pack(side="right", padx=30)

        for s in servicios:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkFrame(self.scroll, height=1, fg_color="#EEE").pack(fill="x")

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", padx=10)
            ctk.CTkLabel(info, text=s['nombre'], font=("Segoe UI", 12, "bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=f"{s['categoria']} > {s['subcategoria']}", font=("Segoe UI", 10), text_color="gray").pack(anchor="w")

            p_val = float(s['precio_base'])
            txt_p = f"${p_val:,.2f}" if p_val > 0 else "Cotizar"
            
            if self.rol_actual == "Recepcionista":
                ctk.CTkButton(row, text=f"🔒 {txt_p}", width=100, fg_color="#E9ECEF", text_color="gray", 
                              command=lambda x=s: self.verificar_permiso_editar(x)).pack(side="right", padx=10)
            else:
                ctk.CTkButton(row, text=txt_p, width=100, fg_color="#E3F2FD", text_color=ACCENT, 
                              command=lambda x=s: self.editar_precio(x)).pack(side="right", padx=10)
                ctk.CTkButton(row, text="×", width=30, fg_color="transparent", text_color="red", 
                              command=lambda x=s['id']: self.eliminar(x)).pack(side="right")

    # --- PERMISOS Y ACCIONES ---
    def popup_supervisor(self, callback):
        top = ctk.CTkToplevel(self)
        top.title("🛡️ Autorización"); top.geometry("350x250")
        top.transient(self.winfo_toplevel()); top.grab_set(); top.lift()
        ctk.CTkLabel(top, text="⚠️ Acción Restringida", font=("bold", 16), text_color="#DC3545").pack(pady=10)
        u = ctk.CTkEntry(top, placeholder_text="Usuario Supervisor"); u.pack(fill="x", padx=30, pady=5)
        p = ctk.CTkEntry(top, placeholder_text="Contraseña", show="*"); p.pack(fill="x", padx=30, pady=5)
        def v():
            if self.controller.validar_supervisor(u.get(), p.get()): top.destroy(); callback()
            else: messagebox.showerror("Error", "No autorizado", parent=top)
        ctk.CTkButton(top, text="Autorizar", command=v, fg_color="#DC3545").pack(pady=15)

    def verificar_permiso_nuevo(self):
        if self.rol_actual == "Recepcionista": self.popup_supervisor(self.popup_nuevo_servicio)
        else: self.popup_nuevo_servicio()

    def verificar_permiso_editar(self, s):
        if self.rol_actual == "Recepcionista": self.popup_supervisor(lambda: self.editar_precio(s))
        else: self.editar_precio(s)

    def editar_precio(self, s):
        d = ctk.CTkInputDialog(text=f"Nuevo precio para:\n{s['nombre']}", title="Actualizar Precio")
        val = d.get_input()
        if val:
            ok, msg = self.controller.actualizar_precio(s['id'], val)
            if ok: self.cargar_lista()
            else: messagebox.showerror("Error", msg)

    def eliminar(self, sid):
        if messagebox.askyesno("Confirmar", "¿Eliminar servicio?"):
            self.controller.eliminar_servicio(sid); self.cargar_lista()

    # --- POPUP NUEVO SERVICIO (Constructor Avanzado) ---
    def popup_nuevo_servicio(self):
        top = ctk.CTkToplevel(self)
        top.title("Nuevo Servicio (Avanzado)"); top.geometry("500x650")
        top.transient(self.winfo_toplevel()); top.grab_set(); top.lift(); top.focus_force()
        
        scroll_frm = ctk.CTkScrollableFrame(top, fg_color="transparent")
        scroll_frm.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(scroll_frm, text="Registrar Tratamiento", font=("bold", 18), text_color=ACCENT).pack(pady=(10, 20))
        
        cats = database.obtener_columnas_unicas("categoria")
        if not cats: cats = ["General", "Ortodoncia"]
        
        # 1. Categoría
        ctk.CTkLabel(scroll_frm, text="Categoría:", font=("bold", 12)).pack(anchor="w", padx=20)
        var_cat = ctk.StringVar(value=cats[0])
        c = ctk.CTkOptionMenu(scroll_frm, values=cats, variable=var_cat)
        c.pack(fill="x", padx=20, pady=(5, 15))
        
        # 2. Subcategoría (COMBOBOX: Permite seleccionar existente o escribir nueva)
        ctk.CTkLabel(scroll_frm, text="Subcategoría:", font=("bold", 12)).pack(anchor="w", padx=20)
        
        # Llenar con subcategorías de la primera categoría por defecto
        subs_init = database.obtener_subcategorias_filtro(cats[0])
        if not subs_init: subs_init = ["General"]
        
        # CORRECCIÓN: Usamos ComboBox para permitir escritura
        s = ctk.CTkComboBox(scroll_frm, values=subs_init)
        s.set("") # Dejar vacío o sugerir
        s.pack(fill="x", padx=20, pady=(5, 15))
        
        # Callback para actualizar subcategorías si cambian la categoría
        def update_subs_combo(choice):
            nuevas = database.obtener_subcategorias_filtro(choice)
            if not nuevas: nuevas = ["General"]
            s.configure(values=nuevas)
            s.set("")
        c.configure(command=update_subs_combo)

        # 3. Nombre
        ctk.CTkLabel(scroll_frm, text="Nombre del Servicio:", font=("bold", 12)).pack(anchor="w", padx=20)
        n = ctk.CTkEntry(scroll_frm)
        n.pack(fill="x", padx=20, pady=(5, 20))
        
        # 4. Constructor de Precios
        ctk.CTkLabel(scroll_frm, text="Configuración de Costos:", font=("bold", 14), text_color="#333").pack(anchor="w", padx=20)
        ctk.CTkLabel(scroll_frm, text="Define las variantes (Ej: Por diente - $500)", font=("Arial", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0,10))
        
        unidades_comunes = ["Por diente", "Por zona", "Por arcada", "Boca completa", "Por cuadrante", "Por caso (Cotizar)"]
        self.filas_precios = []
        
        # Generar 5 filas
        for i in range(5):
            row = ctk.CTkFrame(scroll_frm, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            
            # Combo Unidad
            cmb = ctk.CTkComboBox(row, values=unidades_comunes, width=200)
            cmb.set("") 
            if i == 0: cmb.set("Por diente") 
            cmb.pack(side="left", padx=5)
            
            # Entry Precio
            ent = ctk.CTkEntry(row, placeholder_text="$ Precio", width=100)
            if i == 0: ent.insert(0, "0.00")
            ent.pack(side="left", padx=5)
            
            self.filas_precios.append((cmb, ent))

        def guardar():
            datos_opciones = []
            for cmb_u, ent_p in self.filas_precios:
                u_val = cmb_u.get().strip()
                p_val = ent_p.get().strip()
                
                if u_val: 
                    if "caso" in u_val.lower() or "cotizar" in u_val.lower():
                        p_val = "0.00" 
                    elif not p_val:
                        p_val = "0.00"
                    datos_opciones.append((u_val, p_val))
            
            # Enviamos al controlador (que maneja el JSON)
            ok, msg = self.controller.crear_servicio_avanzado(c.get(), s.get(), n.get(), datos_opciones)
            if ok: messagebox.showinfo("Éxito", msg); top.destroy(); self.cargar_lista()
            else: messagebox.showerror("Error", msg, parent=top)
            
        ctk.CTkButton(scroll_frm, text="GUARDAR SERVICIO", command=guardar, fg_color="#28A745", height=40).pack(pady=30, padx=20, fill="x")