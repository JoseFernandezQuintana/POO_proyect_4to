import customtkinter as ctk
from tkinter import messagebox
import json
from admin_controller import AdminController

BG_MAIN = "#F4F6F9"
WHITE = "#FFFFFF"
ACCENT = "#007BFF"

class AdminServiciosFrame(ctk.CTkFrame):
    def __init__(self, master, rol_contexto=None):
        super().__init__(master, fg_color=BG_MAIN)
        self.controller = AdminController()
        
        # Detectar Rol
        try: 
            self.rol_actual = rol_contexto if rol_contexto else self.master.master.rol 
        except: 
            self.rol_actual = "Recepcionista"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.bind("<Button-1>", lambda e: self._quitar_foco_inteligente(e, self))

        # 1. Header
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        ctk.CTkLabel(top, text="🦷 Catálogo de Servicios", font=("Segoe UI", 20, "bold"), text_color=ACCENT).pack(side="left")
        
        txt_btn = "🔒 + Nuevo (Req. Supervisor)" if self.rol_actual == "Recepcionista" else "+ Nuevo Servicio"
        col_btn = "#6C757D" if self.rol_actual == "Recepcionista" else "#28A745"
        ctk.CTkButton(top, text=txt_btn, fg_color=col_btn, command=self.verificar_permiso_nuevo).pack(side="right")

        # 2. Buscador
        self.crear_filtros()

        # 3. Lista
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=WHITE, corner_radius=10)
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.scroll.bind("<Button-1>", lambda e: self._quitar_foco_inteligente(e, self))
        
        self.cargar_lista()

    def _quitar_foco_inteligente(self, event, widget_destino):
        try:
            clase = event.widget.winfo_class()
            if "Entry" not in clase and "Text" not in clase:
                widget_destino.focus()
        except: pass

    def crear_filtros(self):
        f = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=10)
        f.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        f.bind("<Button-1>", lambda e: self._quitar_foco_inteligente(e, self))
        
        # Obtenemos categorías a través del controller
        cats = ["Todas"] + (self.controller.obtener_categorias() or [])
        
        ctk.CTkLabel(f, text="Categoría:", font=("bold", 11)).pack(side="left", padx=(15,5))
        self.cmb_cat = ctk.CTkOptionMenu(f, values=cats, width=150, command=self.actualizar_subs, fg_color="#FAFAFA", text_color="#333", button_color="#CCC")
        self.cmb_cat.pack(side="left", padx=5, pady=10)

        ctk.CTkLabel(f, text="Subcategoría:", font=("bold", 11)).pack(side="left", padx=(15,5))
        self.cmb_sub = ctk.CTkOptionMenu(f, values=["Todas"], width=150, command=lambda x: self.cargar_lista(), fg_color="#FAFAFA", text_color="#333", button_color="#CCC")
        self.cmb_sub.pack(side="left", padx=5, pady=10)

        self.ent_search = ctk.CTkEntry(f, placeholder_text="Buscar servicio...", height=35, fg_color="#FAFAFA", border_color="#E0E0E0")
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(15,10))
        self.ent_search.bind("<KeyRelease>", lambda e: self.cargar_lista())
        
        ctk.CTkButton(f, text="Limpiar", width=60, fg_color="#DDD", text_color="black", command=self.reset_filtros).pack(side="left", padx=(0,15))

    def cargar_lista(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        servicios = self.controller.buscar_servicios(
            self.ent_search.get(), 
            self.cmb_cat.get(), 
            self.cmb_sub.get()
        )
        
        if not servicios:
            ctk.CTkLabel(self.scroll, text="No se encontraron servicios.", text_color="gray").pack(pady=20)
            return

        h = ctk.CTkFrame(self.scroll, fg_color="#F1F1F1", height=40)
        h.pack(fill="x", pady=(0, 5))
        h.grid_columnconfigure(0, weight=1) 
        h.grid_columnconfigure(1, weight=0, minsize=350) 
        h.grid_columnconfigure(2, weight=0, minsize=100)

        ctk.CTkLabel(h, text="SERVICIO / CATEGORÍA", font=("bold", 11), anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(h, text="LISTA DE PRECIOS", font=("bold", 11), anchor="center").grid(row=0, column=1, sticky="ew", pady=10)
        ctk.CTkLabel(h, text="ACCIONES", font=("bold", 11), anchor="center").grid(row=0, column=2, sticky="ew", padx=10, pady=10)

        for s in servicios:
            row = ctk.CTkFrame(self.scroll, fg_color=WHITE, corner_radius=8, border_color="#E0E0E0", border_width=1)
            row.pack(fill="x", pady=4, padx=5)
            row.bind("<Button-1>", lambda e: self._quitar_foco_inteligente(e, self))
            row.grid_columnconfigure(0, weight=1) 
            row.grid_columnconfigure(1, weight=0, minsize=350) 
            row.grid_columnconfigure(2, weight=0, minsize=100)

            left_box = ctk.CTkFrame(row, fg_color="transparent")
            left_box.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)
            ctk.CTkLabel(left_box, text=s['nombre'], font=("Segoe UI", 12, "bold"), text_color="#333", wraplength=200, justify="left").pack(anchor="w")
            ctk.CTkLabel(left_box, text=f"{s['categoria']} > {s['subcategoria']}", font=("Arial", 10), text_color="gray").pack(anchor="w")

            center_box = ctk.CTkFrame(row, fg_color="transparent")
            center_box.grid(row=0, column=1, sticky="ns", pady=10) 
            center_box.grid_columnconfigure(0, weight=1) 
            center_box.grid_columnconfigure(1, weight=1) 

            raw_units = s.get('tipo_unidad', 'Unidad').replace("/", " o ")
            lista_unidades = raw_units.split(" o ")
            
            precios_json = {}
            if s.get('opciones_json'):
                try: precios_json = json.loads(s['opciones_json'])
                except: pass

            for i, unidad in enumerate(lista_unidades):
                unidad = unidad.strip()
                if not unidad: continue
                ctk.CTkLabel(center_box, text=f"• {unidad}", font=("Segoe UI", 11), text_color="#555").grid(row=i, column=0, sticky="e", padx=(0, 10), pady=2)

                precio_val = float(precios_json.get(unidad, s['precio_base']))
                txt_p = f"${precio_val:,.2f}" if precio_val > 0 else "Cotizar"
                col_btn = "#E3F2FD" if precio_val > 0 else "#FFF3CD"
                txt_col = ACCENT if precio_val > 0 else "#856404"

                if self.rol_actual == "Recepcionista":
                     ctk.CTkLabel(center_box, text=f"🔒 {txt_p}", font=("bold", 11), text_color="gray").grid(row=i, column=1, sticky="w", pady=2)
                else:
                    cmd_edit = lambda sid=s['id'], nom=unidad, actual=precio_val: self._editar_precio_variante(sid, nom, actual)
                    ctk.CTkButton(center_box, text=txt_p, width=90, height=24, fg_color=col_btn, text_color=txt_col, hover_color="#D0E4F5",
                                  font=("bold", 11), command=cmd_edit).grid(row=i, column=1, sticky="w", pady=2)

            if self.rol_actual != "Recepcionista":
                ctk.CTkButton(row, text="× Eliminar", width=80, fg_color="#FFF0F0", text_color="#DC3545", hover_color="#FFE5E5", 
                              border_color="#DC3545", border_width=1, 
                              command=lambda x=s['id']: self.eliminar(x)).grid(row=0, column=2, padx=10, pady=15)
                    
    def _editar_precio_variante(self, sid, nombre_variante, precio_actual):
        dialog = ctk.CTkInputDialog(text=f"Nuevo precio para:\n'{nombre_variante}'\n(Escribe 0 para Cotizar)", title="Editar Precio")
        try: dialog.geometry(f"+{self.winfo_rootx()+100}+{self.winfo_rooty()+100}")
        except: pass
        val = dialog.get_input()
        if val is not None:
            clean_val = val.replace('$','').replace(',','')
            if clean_val.replace('.', '', 1).isdigit():
                ok, msg = self.controller.actualizar_precio_variante(sid, nombre_variante, clean_val)
                if ok: self.cargar_lista()
                else: messagebox.showerror("Error", msg)
            elif clean_val == "": pass
            else: messagebox.showerror("Error", "Ingresa un número válido")

    def reset_filtros(self):
        self.cmb_cat.set("Todas")
        self.actualizar_subs("Todas")
        self.ent_search.delete(0, 'end')
        self.focus() 
        self.cargar_lista()

    def actualizar_subs(self, cat):
        subs = ["Todas"] + (self.controller.obtener_subcategorias(cat) if cat != "Todas" else [])
        self.cmb_sub.configure(values=subs)
        self.cmb_sub.set("Todas")
        self.cargar_lista()

    def verificar_permiso_nuevo(self):
        if self.rol_actual == "Recepcionista":
            self.popup_supervisor(self.popup_nuevo_servicio)
        else:
            self.popup_nuevo_servicio()

    def popup_supervisor(self, callback):
        top = ctk.CTkToplevel(self)
        top.title("Autorización"); top.geometry("300x200")
        top.transient(self.winfo_toplevel()); top.grab_set()
        top.bind("<Button-1>", lambda e: self._quitar_foco_inteligente(e, top))

        ctk.CTkLabel(top, text="Requiere Supervisor", font=("bold",14)).pack(pady=10)
        u = ctk.CTkEntry(top, placeholder_text="Usuario", fg_color="#FAFAFA"); u.pack(fill="x", padx=20, pady=5)
        p = ctk.CTkEntry(top, placeholder_text="Contraseña", show="*", fg_color="#FAFAFA"); p.pack(fill="x", padx=20, pady=5)
        def validar():
            if self.controller.validar_supervisor(u.get(), p.get()):
                top.destroy(); callback()
            else: messagebox.showerror("Error", "Credenciales inválidas", parent=top)
        ctk.CTkButton(top, text="Autorizar", command=validar, fg_color=ACCENT).pack(pady=15)

    def eliminar(self, sid):
        if messagebox.askyesno("Confirmar", "¿Eliminar este servicio?"):
            self.controller.eliminar_servicio(sid)
            self.cargar_lista()

    def popup_nuevo_servicio(self):
        top = ctk.CTkToplevel(self)
        top.title("Nuevo Servicio")
        top.geometry("550x650")
        top.transient(self.winfo_toplevel())
        top.grab_set()
        top.bind("<Button-1>", lambda e: self._quitar_foco_inteligente(e, top))

        scroll = ctk.CTkScrollableFrame(top, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        scroll.bind("<Button-1>", lambda e: self._quitar_foco_inteligente(e, top))
        
        ctk.CTkLabel(scroll, text="Registrar Nuevo Servicio", font=("bold", 18), text_color=ACCENT).pack(pady=10)
        
        cats = self.controller.obtener_categorias() or ["General"]
        if "Otros" not in cats: cats.append("Otros") 

        ctk.CTkLabel(scroll, text="Categoría:", font=("bold",12)).pack(anchor="w", padx=20)
        
        def _actualizar_subs_popup(cat_seleccionada):
            subs = self.controller.obtener_subcategorias(cat_seleccionada)
            if not subs: subs = ["General"]
            c_sub.configure(values=subs)
            c_sub.set(subs[0])

        c_cat = ctk.CTkOptionMenu(scroll, values=cats, command=_actualizar_subs_popup, fg_color="#FAFAFA", text_color="#333", button_color="#CCC")
        c_cat.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(scroll, text="Subcategoría (o escribe nueva):", font=("bold",12)).pack(anchor="w", padx=20)
        c_sub = ctk.CTkComboBox(scroll, values=["General"], fg_color="#FAFAFA", text_color="#333", border_color="#CCC")
        c_sub.pack(fill="x", padx=20, pady=5)
        _actualizar_subs_popup(cats[0])

        ctk.CTkLabel(scroll, text="Nombre del Servicio:", font=("bold",12)).pack(anchor="w", padx=20)
        e_nom = ctk.CTkEntry(scroll, fg_color="#FAFAFA", border_color="#CCC")
        e_nom.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(scroll, text="Variantes y Precios:", font=("bold",14)).pack(anchor="w", padx=20, pady=(15,5))
        ctk.CTkLabel(scroll, text="Define las unidades (ej: boca, diente). El sistema agregará 'Por ' automáticamente.", font=("Arial", 10), text_color="gray").pack(anchor="w", padx=20)

        filas_variantes = []
        for i in range(5):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=2)
            row.bind("<Button-1>", lambda e: self._quitar_foco_inteligente(e, top))
            
            ctk.CTkLabel(row, text="Por", font=("bold", 12), text_color="#555").pack(side="left", padx=(5,2))
            u = ctk.CTkEntry(row, placeholder_text=f"unidad {i+1} (ej: diente)", width=150, fg_color="#FAFAFA", border_color="#CCC")
            u.pack(side="left", fill="x", expand=True)
            p = ctk.CTkEntry(row, placeholder_text="$", width=80, fg_color="#FAFAFA", border_color="#CCC")
            p.pack(side="right", padx=(5,0))
            filas_variantes.append((u,p))

        def guardar():
            opciones_dict = {}
            for u_obj, p_obj in filas_variantes:
                uni = u_obj.get().strip()
                pre_str = p_obj.get().strip()
                if uni:
                    uni_capital = uni.capitalize() 
                    nombre_final = f"Por {uni_capital}" 
                    try: val_pre = float(pre_str) if pre_str else 0.0
                    except: val_pre = 0.0
                    opciones_dict[nombre_final] = val_pre
            
            if not e_nom.get():
                messagebox.showwarning("Faltan datos", "Nombre obligatorio", parent=top); return
            if not opciones_dict:
                messagebox.showwarning("Faltan datos", "Agrega al menos una variante", parent=top); return

            ok, msg = self.controller.crear_servicio_avanzado(c_cat.get(), c_sub.get().strip(), e_nom.get().strip(), opciones_dict)
            if ok:
                messagebox.showinfo("Éxito", msg, parent=top)
                top.destroy()
                self.cargar_lista()
            else:
                messagebox.showerror("Error", msg, parent=top)

        ctk.CTkButton(scroll, text="GUARDAR SERVICIO", command=guardar, fg_color="#28A745", height=45, font=("bold", 12)).pack(pady=20, padx=20, fill="x")
        