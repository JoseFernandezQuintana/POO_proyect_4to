import customtkinter as ctk
from PIL import Image
import os 
from datetime import datetime, timedelta
from tkinter import messagebox
import calendar
import webbrowser
import urllib.parse 
from agendar_controller import AgendarCitaController
from notifications_helper import NotificationsHelper

# --- CONFIGURACIÓN ESTÉTICA ---
BG_MAIN = "#F4F6F9"
WHITE_CARD = "#FFFFFF"
TEXT_DARK = "#333333"
ACCENT_BLUE = "#007BFF"
BORDER_COLOR = "#E0E0E0"
HEADER_CAL = "#E8F0FE"
SUCCESS_COLOR = "#28A745"
WARNING_COLOR = "#FFC107"
DANGER_COLOR = "#DC3545"
INFO_COLOR = "#17A2B8"

current_dir = os.path.dirname(os.path.abspath(__file__))

class AgendarCitaFrame(ctk.CTkFrame):
    
    def __init__(self, master):
        super().__init__(master, fg_color=BG_MAIN)
        self.controller = AgendarCitaController()
        
        try: self.user_id = self.master.master.user_id 
        except: self.user_id = None
        
        self.servicios_agregados = []
        self.selected_date = None           
        self.display_date = datetime.now()  
        self.cliente_existente_id = None 
        self.mapa_pacientes_temp = {}
        self.tratamientos_externos = [] 

        # Layout Principal
        self.grid_columnconfigure(0, weight=3) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        self.bind("<Button-1>", lambda e: self.focus_set())

        # Panel Izquierdo
        self.left_card = ctk.CTkFrame(self, fg_color=WHITE_CARD, corner_radius=15, border_color=BORDER_COLOR, border_width=1)
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.left_card.grid_rowconfigure(0, weight=1) 
        self.left_card.grid_columnconfigure(0, weight=1)
        self.left_card.bind("<Button-1>", lambda e: self.focus_set())

        # Panel Derecho (Sidebar)
        self.sidebar = ctk.CTkFrame(self, fg_color="transparent", width=250)
        self.sidebar.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)

        # Scroll del formulario
        self.scroll = ctk.CTkScrollableFrame(self.left_card, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scroll.grid_columnconfigure(0, weight=1)
        
        # Botones inferiores
        self.bottom_frame = ctk.CTkFrame(self.left_card, fg_color="transparent", height=90)
        self.bottom_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 10))
        self.bottom_frame.grid_columnconfigure((0, 1), weight=1)

        self.create_form()    
        self.create_buttons()   
        self.create_sidebar() 

    def create_form(self):
        p = self.scroll
        for w in p.winfo_children(): w.destroy()
        
        c = ctk.CTkFrame(p, fg_color="transparent")
        c.pack(fill="x", expand=True, padx=5, pady=2)
        c.grid_columnconfigure((0, 1), weight=1)
        c.bind("<Button-1>", lambda e: self.focus_set())

        r = 0 
        ctk.CTkLabel(c, text="📅 Nueva Cita", font=("Segoe UI", 22, "bold"), text_color=ACCENT_BLUE).grid(row=r, column=0, columnspan=2, sticky="w", pady=(0, 10)); r+=1

        self.modo_var = ctk.StringVar(value="Nuevo Paciente")
        self.seg = ctk.CTkSegmentedButton(c, values=["Nuevo Paciente", "Paciente Existente"], variable=self.modo_var, command=self.cambiar_modo, selected_color=ACCENT_BLUE)
        self.seg.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10)); r+=1

        # --- BUSCADOR ESTILO CALENDARIO ---
        self.frame_bus = ctk.CTkFrame(c, fg_color="transparent")
        self.frame_bus.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
        self.frame_bus.grid_remove()
        
        search_bar = ctk.CTkFrame(self.frame_bus, fg_color="#F1F3F4", corner_radius=20)
        search_bar.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(search_bar, text="🔍", font=("Arial", 14), text_color="#555").pack(side="left", padx=(15, 5), pady=8)
        self.ent_bus = ctk.CTkEntry(search_bar, placeholder_text="Buscar paciente...", border_width=0, fg_color="transparent", text_color=TEXT_DARK, height=35, font=("Segoe UI", 12))
        self.ent_bus.pack(side="left", fill="x", expand=True)
        self.ent_bus.bind("<Return>", self.buscar_pacientes_click)
        
        ctk.CTkButton(search_bar, text="Buscar", width=60, fg_color=ACCENT_BLUE, corner_radius=15, command=self.buscar_pacientes_click).pack(side="left", padx=5)
        ctk.CTkButton(search_bar, text="✕", width=30, fg_color="transparent", text_color="#999", hover_color="#EEE", command=self.limpiar_busqueda).pack(side="left", padx=(0,10))

        self.results_frame = ctk.CTkScrollableFrame(self.frame_bus, height=0, fg_color="white", border_color="#DDD", border_width=1, corner_radius=8)
        
        r+=1 

        self._title(c, "INFORMACIÓN PERSONAL", r); r+=1
        self.ent_nom = ctk.CTkEntry(c, placeholder_text="Nombre Completo *", height=40, border_color=BORDER_COLOR, fg_color="white", text_color="black")
        self.ent_nom.grid(row=r, column=0, sticky="ew", padx=10, pady=(0, 8))
        
        frm_mix = ctk.CTkFrame(c, fg_color="transparent", height=40)
        frm_mix.grid(row=r, column=1, sticky="ew", padx=10, pady=(0, 8))
        frm_mix.grid_columnconfigure((0,1), weight=1)
        
        self.cmb_edad = ctk.CTkOptionMenu(frm_mix, values=["Edad"] + ['0-3', '3-6', '6-12', '12-18', '18-35', '35-60', '60+'], fg_color="#FAFAFA", text_color=TEXT_DARK, button_color="#CCC")
        self.cmb_edad.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.cmb_gen = ctk.CTkOptionMenu(frm_mix, values=["Género","Femenino","Masculino"], fg_color="#FAFAFA", text_color=TEXT_DARK, button_color="#CCC")
        self.cmb_gen.pack(side="left", fill="x", expand=True, padx=(5,0))
        r+=1 

        self._title(c, "ESPECIALISTA Y ANTECEDENTES", r); r+=1
        self.cmb_doc = ctk.CTkOptionMenu(c, values=["Selecciona Doctora"]+self.controller.obtener_lista_nombres_doctoras(), command=self.al_cambiar_doc, fg_color="#FAFAFA", text_color=TEXT_DARK, button_color="#CCC")
        self.cmb_doc.grid(row=r, column=0, sticky="ew", padx=(10, 5), pady=2)
        
        frm_prev_cont = ctk.CTkFrame(c, fg_color="transparent")
        frm_prev_cont.grid(row=r, column=1, sticky="ew", padx=(5,10))
        
        self.cmb_prev_opt = ctk.CTkOptionMenu(
            frm_prev_cont, 
            values=["Tratamiento previo: No", "Tratamiento previo: Sí, Clínica", "Tratamiento previo: Sí, Externa", "Tratamiento previo: Sí, Ambas"], 
            command=self.toggle_prev, 
            fg_color="#FAFAFA", 
            text_color=TEXT_DARK,
            button_color="#CCC"
        )
        self.cmb_prev_opt.pack(side="left", fill="x", expand=True)
        r+=1

        self.frm_ext_treats = ctk.CTkFrame(c, fg_color="#FAFAFA", border_color="#EEE", border_width=1)
        self.frm_ext_treats.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(5,0))
        self.frm_ext_treats.grid_remove()
        row_add = ctk.CTkFrame(self.frm_ext_treats, fg_color="transparent")
        row_add.pack(fill="x", padx=5, pady=5)
        self.ent_ext_treat = ctk.CTkEntry(row_add, placeholder_text="Describir tratamiento externo...", height=30, fg_color="white", text_color="black")
        self.ent_ext_treat.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row_add, text="+", width=30, command=self.agregar_tratamiento_externo).pack(side="left", padx=5)
        self.scroll_ext_list = ctk.CTkScrollableFrame(self.frm_ext_treats, height=80, fg_color="transparent")
        self.scroll_ext_list.pack(fill="x", padx=5, pady=2)
        r+=1; self._sep(c, r); r+=1

        self._title(c, "FECHA Y DURACIÓN", r); r+=1
        frm_dt = ctk.CTkFrame(c, fg_color="transparent")
        frm_dt.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10)
        frm_dt.grid_columnconfigure(0, weight=0); frm_dt.grid_columnconfigure(1, weight=1)
        self.cal_frame = ctk.CTkFrame(frm_dt, fg_color="white", border_color="#DDD", border_width=1)
        self.cal_frame.grid(row=0, column=0, sticky="n", padx=(0, 15), ipady=5)
        self.render_calendar()

        frm_tm = ctk.CTkFrame(frm_dt, fg_color="transparent")
        frm_tm.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(frm_tm, text="1. Hora Inicio", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0,2))
        frm_reloj = ctk.CTkFrame(frm_tm, fg_color="transparent"); frm_reloj.pack(fill="x", pady=(0, 10))
        self.cmb_h = ctk.CTkOptionMenu(frm_reloj, values=["--"], width=95, command=self.al_cambiar_hora, fg_color="#E8F0FE", text_color="black")
        self.cmb_h.pack(side="left", padx=(0, 5))
        self.cmb_m = ctk.CTkOptionMenu(frm_reloj, values=["--"], width=95, command=self.calc_fin, fg_color="#E8F0FE", text_color="black")
        self.cmb_m.pack(side="left")
        ctk.CTkLabel(frm_tm, text="2. Duración", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0,2))
        self.lbl_dur_val = ctk.CTkLabel(frm_tm, text="30 min", font=("Arial", 13, "bold"), text_color=ACCENT_BLUE)
        self.lbl_dur_val.pack(anchor="w")
        self.slider_dur = ctk.CTkSlider(frm_tm, from_=5, to=300, number_of_steps=59, command=self.upd_slider)
        self.slider_dur.set(30); self.slider_dur.pack(fill="x", pady=(0, 5))
        self.lbl_fin_hora = ctk.CTkLabel(frm_tm, text="Fin: --:--", font=("Arial", 11), text_color="#555"); self.lbl_fin_hora.pack(anchor="w", pady=(5,0))
        r+=1; self._sep(c, r); r+=1

        self._title(c, "DETALLES", r); r+=1
        self.tipo_var = ctk.StringVar(value="Presupuesto")
        self.seg_tipo = ctk.CTkSegmentedButton(c, values=["Presupuesto", "Tratamiento"], variable=self.tipo_var, command=self.toggle_serv, selected_color=ACCENT_BLUE)
        self.seg_tipo.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5)); r+=1
        
        self.frm_serv = ctk.CTkFrame(c, fg_color="#FAFAFA", border_color="#EEE", border_width=2, height=300)
        self.frm_serv.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.frm_serv.grid_remove()
        ctk.CTkButton(self.frm_serv, text="+ Agregar Servicio del Catálogo", fg_color="transparent", border_color=ACCENT_BLUE, border_width=1, text_color=ACCENT_BLUE, command=self.open_serv_popup).pack(fill="x", padx=10, pady=10)
        self.lst_serv_visual = ctk.CTkScrollableFrame(self.frm_serv, fg_color="transparent")
        self.lst_serv_visual.pack(fill="both", expand=True, padx=5, pady=5)
        self.lbl_tot = ctk.CTkLabel(self.frm_serv, text="Total: $0.00", font=("Arial", 14, "bold"), text_color=SUCCESS_COLOR)
        self.lbl_tot.pack(anchor="e", padx=15, pady=10)
        r+=1; self._sep(c, r); r+=1
        r = self.create_contact(c, r); self._sep(c, r); r+=1

        self._title(c, "OBSERVACIONES", r); r+=1
        self.frm_nota = ctk.CTkFrame(c, fg_color="#FAFAFA", border_color="#CCC", border_width=1, corner_radius=6)
        self.frm_nota.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
        self.frm_nota.grid_columnconfigure(0, weight=1); self.frm_nota.grid_rowconfigure(0, weight=1)
        self.txt_nota = ctk.CTkTextbox(self.frm_nota, height=60, fg_color="white", text_color="black", wrap="word", font=("Segoe UI", 12))
        self.txt_nota.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.lbl_ph = ctk.CTkLabel(self.txt_nota, text="Notas adicionales...", text_color="#999", font=("Segoe UI", 12, "italic"))
        self.lbl_ph.place(x=5, y=5)
        self.lbl_ph.bind("<Button-1>", lambda e: self.txt_nota.focus_set())
        self.txt_nota.bind("<FocusIn>", lambda e: self.lbl_ph.place_forget())
        self.txt_nota.bind("<FocusOut>", self.chk_ph)

    def create_contact(self, p, r):
        self._title(p, "MEDIOS DE CONTACTO", r); r+=1
        f = ctk.CTkFrame(p, fg_color="#F9F9F9", corner_radius=8)
        f.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5)); r+=1
        f.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(f, text="📱", font=("Arial", 16)).grid(row=0, column=0, padx=(10,5), pady=5)
        self.ent_tel = ctk.CTkEntry(f, placeholder_text="Teléfono / WhatsApp", fg_color="white", border_color="#DDD", text_color="black")
        self.ent_tel.grid(row=0, column=1, sticky="ew", padx=(0,10), pady=5)
        
        ctk.CTkLabel(f, text="📧", font=("Arial", 16)).grid(row=1, column=0, padx=(10,5), pady=5)
        self.ent_email = ctk.CTkEntry(f, placeholder_text="Correo Electronico", fg_color="white", border_color="#DDD", text_color="black")
        self.ent_email.grid(row=1, column=1, sticky="ew", padx=(0,10), pady=5)
        
        self.var_notif = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(p, text="Notificar (WhatsApp y Correo)", variable=self.var_notif, progress_color=SUCCESS_COLOR).grid(row=r, column=0, columnspan=2, sticky="w", padx=20, pady=5); r+=1
        return r

    def create_sidebar(self):
        for w in self.sidebar.winfo_children(): w.destroy()
        
        c1 = ctk.CTkFrame(self.sidebar, fg_color=WHITE_CARD, corner_radius=10, border_color=BORDER_COLOR, border_width=1)
        c1.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(c1, text="🏥 Equipo Médico", font=("Segoe UI", 13, "bold"), text_color=ACCENT_BLUE).pack(pady=10, padx=15, anchor="w")
        
        scroll_medicos = ctk.CTkScrollableFrame(c1, fg_color="transparent", height=150)
        scroll_medicos.pack(fill="x", padx=5, pady=5)
        
        info = self.controller.obtener_info_doctoras_visual()
        for nombre, dat in info.items():
            r = ctk.CTkFrame(scroll_medicos, fg_color="transparent")
            r.pack(fill="x", padx=5, pady=5)
            
            if dat['tipo'] == "archivo":
                try:
                    img_pil = Image.open(dat['foto'])
                    img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(40, 40))
                    ctk.CTkLabel(r, text="", image=img_ctk).pack(side="left")
                except:
                    ctk.CTkLabel(r, text="📷", font=("Arial", 20)).pack(side="left")
            else:
                ctk.CTkLabel(r, text=dat['foto'], font=("Arial", 20)).pack(side="left")

            t = ctk.CTkFrame(r, fg_color="transparent"); t.pack(side="left", padx=8)
            ctk.CTkLabel(t, text=nombre, font=("Segoe UI", 11, "bold")).pack(anchor="w")
            ctk.CTkLabel(t, text=dat['especialidad'], font=("Segoe UI", 10), text_color="gray").pack(anchor="w")

        c2 = ctk.CTkFrame(self.sidebar, fg_color=WHITE_CARD, corner_radius=10, border_color=BORDER_COLOR, border_width=1)
        c2.pack(fill="x")
        ctk.CTkLabel(c2, text=f"📊 Resumen Hoy", font=("Segoe UI", 13, "bold"), text_color=ACCENT_BLUE).pack(pady=10, padx=15, anchor="w")
        st = self.controller.obtener_resumen_citas()
        items = [
            ("Pendiente", st.get('Pendiente',0), WARNING_COLOR), 
            ("En curso", st.get('En curso',0), INFO_COLOR), 
            ("Completada", st.get('Completada',0), SUCCESS_COLOR), 
            ("Cancelada", st.get('Cancelada',0), DANGER_COLOR)
        ]
        for l, v, col in items:
            r = ctk.CTkFrame(c2, fg_color="transparent"); r.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(r, text="●", text_color=col).pack(side="left")
            ctk.CTkLabel(r, text=l, font=("Segoe UI", 11)).pack(side="left", padx=5)
            ctk.CTkLabel(r, text=str(v), font=("bold", 12)).pack(side="right")

    # --- LÓGICA DE TRATAMIENTOS PREVIOS ---
    def toggle_prev(self, val):
        if "Externa" in val or "Ambas" in val:
            self.frm_ext_treats.grid()
        else:
            self.frm_ext_treats.grid_remove()
            self.tratamientos_externos = [] 
            self.render_lista_externos()

    def agregar_tratamiento_externo(self):
        texto = self.ent_ext_treat.get().strip()
        if texto:
            self.tratamientos_externos.append(texto)
            self.ent_ext_treat.delete(0, 'end')
            self.render_lista_externos()

    def eliminar_tratamiento_externo(self, index):
        self.tratamientos_externos.pop(index)
        self.render_lista_externos()

    def render_lista_externos(self):
        for w in self.scroll_ext_list.winfo_children(): w.destroy()
        for i, t in enumerate(self.tratamientos_externos):
            row = ctk.CTkFrame(self.scroll_ext_list, fg_color="white", corner_radius=6)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"• {t}", font=("Arial", 11), text_color="#555").pack(side="left", padx=5)
            ctk.CTkButton(row, text="×", width=20, height=20, fg_color="transparent", text_color=DANGER_COLOR, command=lambda x=i: self.eliminar_tratamiento_externo(x)).pack(side="right", padx=5)

    # --- MENÚ SERVICIOS ---
    def toggle_serv(self, v):
        if v=="Tratamiento": self.frm_serv.grid()
        else: self.frm_serv.grid_remove()

    def open_serv_popup(self):
        self.top_serv = ctk.CTkToplevel(self)
        self.top_serv.title("Catálogo de Servicios")
        self.top_serv.geometry("750x600")
        self.top_serv.configure(fg_color=BG_MAIN)
        self.top_serv.transient(self)
        self.top_serv.grab_set()
        self._construir_interfaz_popup()

    def _construir_interfaz_popup(self):
        f = ctk.CTkFrame(self.top_serv, fg_color="white"); f.pack(fill="x", padx=10, pady=10)
        
        row1 = ctk.CTkFrame(f, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=10)
        
        cats = ["Todas"] + self.controller.obtener_categorias_unicas()
        ctk.CTkLabel(row1, text="Categoría:", font=("bold", 12)).pack(side="left")
        self.pop_cat = ctk.CTkOptionMenu(row1, values=cats, command=self._act_subs_popup, width=150, fg_color="#FAFAFA", text_color=TEXT_DARK)
        self.pop_cat.pack(side="left", padx=5)
        
        ctk.CTkLabel(row1, text="Subcategoría:", font=("bold", 12)).pack(side="left", padx=(15,0))
        self.pop_sub = ctk.CTkOptionMenu(row1, values=["Todas"], command=lambda x: self._cargar_lista_popup(), width=150, fg_color="#FAFAFA", text_color=TEXT_DARK)
        self.pop_sub.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(f, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0,10))
        self.pop_search = ctk.CTkEntry(row2, placeholder_text="🔍 Buscar...", fg_color="#FAFAFA")
        self.pop_search.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.pop_search.bind("<KeyRelease>", lambda e: self._cargar_lista_popup())
        
        ctk.CTkButton(row2, text="Limpiar", width=80, fg_color="#DDD", text_color="black", command=self._reset_filtros_popup).pack(side="right")

        self.pop_scroll = ctk.CTkScrollableFrame(self.top_serv, fg_color="transparent")
        self.pop_scroll.pack(fill="both", expand=True, padx=15, pady=(0,15))
        
        self._cargar_lista_popup()
    
    def _act_subs_popup(self, cat):
        if cat == "Todas": subs = ["Todas"]
        else: subs = ["Todas"] + self.controller.obtener_subcategorias_por_cat(cat)
        self.pop_sub.configure(values=subs)
        self.pop_sub.set("Todas")
        self._cargar_lista_popup()

    def _reset_filtros_popup(self):
        self.pop_cat.set("Todas")
        self._act_subs_popup("Todas")
        self.pop_search.delete(0, 'end')
        self._cargar_lista_popup()

    def _cargar_lista_popup(self):
        # Limpiamos el scroll frame
        target_scroll = getattr(self, 'pop_scroll', getattr(self, 'pop_list', None))
        for w in target_scroll.winfo_children(): w.destroy()

        # Obtenemos controlador según el archivo donde estemos
        ctrl = getattr(self, 'aux_ctrl', getattr(self, 'controller', None))
        servicios = ctrl.buscar_servicios_filtros(self.pop_search.get(), self.pop_cat.get(), self.pop_sub.get())
        
        if not servicios: 
            ctk.CTkLabel(target_scroll, text="No hay servicios.", text_color="gray").pack(pady=20)
            return

        for s in servicios:
            # Tarjeta idéntica a tu versión original
            c = ctk.CTkFrame(target_scroll, fg_color="#FFFFFF", corner_radius=8, border_color="#D1D5DB", border_width=1)
            c.pack(fill="x", pady=4, padx=5)
            
            # Info Izquierda
            left_info = ctk.CTkFrame(c, fg_color="transparent")
            left_info.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            ctk.CTkLabel(left_info, text=s['nombre'], font=("Segoe UI", 12, "bold"), text_color="#333").pack(anchor="w")
            ctk.CTkLabel(left_info, text=f"{s['categoria']}", font=("Arial", 9), text_color="gray").pack(anchor="w")
            
            # Info Derecha (Precio y Botón)
            right_box = ctk.CTkFrame(c, fg_color="transparent")
            right_box.pack(side="right", padx=10)
            
            unidad_str = s.get('tipo_unidad', 'Unidad')
            ctk.CTkLabel(right_box, text=unidad_str, font=("Segoe UI", 10, "bold"), text_color="#555").pack(side="left", padx=(0, 15))
            
            # Precio Base visual (Si es 0 sale Cotizar, si no sale el precio base)
            p_base = float(s['precio_base'])
            if p_base > 0:
                txt_p = f"${p_base:,.2f}"
                col_p = "#007BFF" # Azul
            else:
                txt_p = "Cotizar"
                col_p = "#FFC107" # Amarillo
            
            ctk.CTkLabel(right_box, text=txt_p, font=("bold", 12), text_color=col_p).pack(side="left", padx=(0, 15))
            
            # Botón Agregar (Llama a análisis de variantes)
            ctk.CTkButton(right_box, text="+ Agregar", width=80, fg_color="#28A745", hover_color="#218838", 
                          command=lambda item=s: self._analizar_variantes(item)).pack(side="left")

    def _analizar_variantes(self, item):
        unidad = item.get('tipo_unidad', '')
        # Si detectamos " o " (ej: Por boca o diente) o "/" abrimos el menú
        if " o " in unidad or "/" in unidad: 
            self._abrir_selector_variante(item)
        else: 
            # Si es simple, pasa directo con el precio base
            self._agregar_servicio_final(item, 1, unidad, item['precio_base'])

    def _abrir_selector_variante(self, item):
        import json
        
        # Crear ventana emergente (Popup)
        var_win = ctk.CTkToplevel(self.top_serv)
        var_win.title("Selecciona Opción")
        var_win.geometry("350x250") # Un poco más alto para que quepan botones
        var_win.transient(self.top_serv)
        var_win.grab_set()
        
        # Centrar visualmente (opcional)
        try: var_win.geometry(f"+{self.top_serv.winfo_rootx()+50}+{self.top_serv.winfo_rooty()+50}")
        except: pass

        ctk.CTkLabel(var_win, text=f"{item['nombre']}", font=("bold", 14), text_color="#333").pack(pady=(15, 5))
        ctk.CTkLabel(var_win, text="Selecciona la modalidad:", text_color="gray").pack(pady=(0, 10))
        
        # 1. Obtener lista de nombres separando por ' o ' o '/'
        nombres_opciones = item['tipo_unidad'].replace("/", " o ").split(" o ")
        
        # 2. Intentar leer precios específicos del JSON (si existen)
        precios_dict = {}
        if item.get('opciones_json'):
            try: precios_dict = json.loads(item['opciones_json'])
            except: pass
            
        # 3. Crear un botón por cada opción EN ORDEN
        for op in nombres_opciones:
            op = op.strip()
            if not op: continue
            
            # Determinar precio: Buscamos en el JSON, si no está, usamos el base
            precio_real = float(precios_dict.get(op, item['precio_base']))
            
            # Texto del botón: "Por boca - $500.00" o "Por boca - Cotizar"
            txt_precio = f"${precio_real:,.2f}" if precio_real > 0 else "Cotizar"
            texto_boton = f"{op}  ➔  {txt_precio}"
            
            # Color del botón (Azul normal, Amarillo si es cotizar/0)
            fg_col = "#007BFF" if precio_real > 0 else "#FFC107"
            text_col = "white" if precio_real > 0 else "black"

            btn = ctk.CTkButton(
                var_win, 
                text=texto_boton, 
                width=280, 
                height=40,
                fg_color=fg_col,
                text_color=text_col,
                font=("Segoe UI", 12, "bold"),
                # Al dar clic, enviamos ESTE precio específico
                command=lambda u=op, p=precio_real: self._agregar_servicio_final(item, 1, u, p, ventana_cierre=var_win)
            )
            btn.pack(pady=5)
            
        # Botón cancelar
        ctk.CTkButton(var_win, text="Cancelar", fg_color="transparent", text_color="gray", hover_color="#EEE", command=var_win.destroy).pack(pady=10)

    def _agregar_servicio_final(self, item, cantidad, unidad_nombre, precio_u, ventana_cierre=None):
        precio_final = float(precio_u)
        
        # --- Lógica de Cotización Manual ($0) ---
        if precio_final == 0:
            dialog = ctk.CTkInputDialog(text=f"Cotización para: {item['nombre']}\nIngrese el costo unitario ($):", title="Cotizar Servicio")
            try: dialog.geometry(f"+{self.top_serv.winfo_rootx()+50}+{self.top_serv.winfo_rooty()+50}")
            except: pass
            
            input_str = dialog.get_input()
            if not input_str: return # Cancelar sin mensaje
            try:
                precio_final = float(input_str)
            except ValueError:
                messagebox.showerror("Error", "Monto inválido", parent=self.top_serv)
                return

        nuevo = {
            'id': item['id'],
            'nombre': item['nombre'],
            'cantidad': cantidad,
            'unidad': unidad_nombre,
            'precio_unitario': precio_final,
            'precio_total': precio_final * cantidad
        }
        self.servicios_agregados.append(nuevo)
        self.actualizar_lista_servicios_visual()
        messagebox.showinfo("Agregado", f"Se agregó: {item['nombre']}", parent=self.top_serv)
        if ventana_cierre: ventana_cierre.destroy()

    def actualizar_lista_servicios_visual(self):
        for w in self.lst_serv_visual.winfo_children(): w.destroy()
        
        total_global = 0
        
        for idx, s in enumerate(self.servicios_agregados):
            row = ctk.CTkFrame(self.lst_serv_visual, fg_color="white", corner_radius=8, border_color="#DDD", border_width=2)
            row.pack(fill="x", pady=2, padx=2)
            
            desc = s['nombre']
            if s['unidad'] and s['unidad'] not in ["Unidad", ""]:
                desc += f" ({s['unidad']})"
            
            ctk.CTkLabel(row, text=desc, font=("bold", 11), text_color=TEXT_DARK, fg_color="transparent").pack(side="left", padx=10, pady=5)
            
            right_box = ctk.CTkFrame(row, fg_color="transparent")
            right_box.pack(side="right", padx=5)
            
            ctk.CTkLabel(right_box, text=f"${s['precio_total']:,.2f}", font=("bold", 12), text_color=ACCENT_BLUE, fg_color="transparent").pack(side="left", padx=10)
            
            btn_minus = ctk.CTkButton(right_box, text="-", width=25, height=25, fg_color="#EEE", text_color="black", hover_color="#DDD",
                                      command=lambda i=idx: self._cambiar_cantidad(i, -1))
            btn_minus.pack(side="left", padx=2)
            
            ctk.CTkLabel(right_box, text=str(s['cantidad']), width=20, font=("bold", 12), text_color=TEXT_DARK).pack(side="left", padx=2)
            
            btn_plus = ctk.CTkButton(right_box, text="+", width=25, height=25, fg_color="#EEE", text_color="black", hover_color="#DDD",
                                     command=lambda i=idx: self._cambiar_cantidad(i, 1))
            btn_plus.pack(side="left", padx=2)
            
            btn_del = ctk.CTkButton(right_box, text="🗑️", width=30, height=25, fg_color="transparent", text_color=DANGER_COLOR, hover_color="#FFEEEE",
                                    command=lambda i=idx: self.eliminar_servicio(i))
            btn_del.pack(side="left", padx=(10, 0))
            
            total_global += s['precio_total']
            
        self.lbl_tot.configure(text=f"Total: ${total_global:,.2f}")

    def _cambiar_cantidad(self, index, delta):
        item = self.servicios_agregados[index]
        nueva_cant = item['cantidad'] + delta
        if nueva_cant <= 0:
            self.eliminar_servicio(index)
        else:
            item['cantidad'] = nueva_cant
            item['precio_total'] = item['precio_unitario'] * nueva_cant
            self.actualizar_lista_servicios_visual()

    def eliminar_servicio(self, idx):
        self.servicios_agregados.pop(idx)
        self.actualizar_lista_servicios_visual()

    # --- CALENDARIO ---
    def render_calendar(self):
        for w in self.cal_frame.winfo_children(): w.destroy()
        h = ctk.CTkFrame(self.cal_frame, fg_color=HEADER_CAL); h.pack(fill="x")
        ctk.CTkButton(h, text="<", width=25, command=lambda: self.mv_cal(-1), fg_color="transparent", text_color=ACCENT_BLUE).pack(side="left")
        ctk.CTkLabel(h, text=self.display_date.strftime("%B %Y").upper(), font=("Arial", 12, "bold"), text_color="#333").pack(side="left", expand=True)
        ctk.CTkButton(h, text=">", width=25, command=lambda: self.mv_cal(1), fg_color="transparent", text_color=ACCENT_BLUE).pack(side="right")
        g = ctk.CTkFrame(self.cal_frame, fg_color="white"); g.pack()
        
        cal = calendar.Calendar(firstweekday=6).monthdayscalendar(self.display_date.year, self.display_date.month)
        hoy = datetime.now().date()
        for r, wk in enumerate(cal):
            for c, d in enumerate(wk):
                if d==0: continue
                dt = datetime(self.display_date.year, self.display_date.month, d).date()
                st = "disabled" if (dt.weekday()==6 or dt<hoy) else "normal"
                bg = ACCENT_BLUE if self.selected_date and d==self.selected_date.day else "white"
                fg = "#CCC" if st=="disabled" else ("white" if bg==ACCENT_BLUE else "black")
                ctk.CTkButton(g, text=str(d), width=30, height=28, fg_color=bg, text_color=fg, state=st, command=lambda x=d: self.set_day(x)).grid(row=r, column=c, padx=1, pady=1)

    def mv_cal(self, m):
        nm = self.display_date.month + m; ny = self.display_date.year
        if nm>12: nm=1; ny+=1
        elif nm<1: nm=12; ny-=1
        self.display_date = self.display_date.replace(year=ny, month=nm); self.render_calendar()
    def set_day(self, d): self.selected_date = datetime(self.display_date.year, self.display_date.month, d); self.render_calendar(); self.act_horarios()
    def al_cambiar_doc(self, _): 
        if self.selected_date: self.act_horarios()
    def act_horarios(self):
        d = self.cmb_doc.get()
        if "Selecciona" in d or not self.selected_date: 
            return # Si no hay doctora o fecha, no hace nada
        
        # Obtenemos horarios
        s = self.controller.obtener_horas_inicio_disponibles(self.selected_date, d)
        
        self.mapa_horarios = {}
        if not s: 
            self.cmb_h.configure(values=["Lleno"]); self.cmb_h.set("Lleno")
            self.cmb_m.configure(values=["--"]); self.cmb_m.set("--")
            return
            
        for x in s:
            # Formato esperado: "11:00 AM"
            p = x.split(":")
            h_k = f"{p[0]} {p[1].split()[1]}" # Ejemplo: "11 AM"
            m_v = p[1].split()[0]             # Ejemplo: "00"
            
            if h_k not in self.mapa_horarios: self.mapa_horarios[h_k]=[]
            self.mapa_horarios[h_k].append(m_v)
            
        ks = list(self.mapa_horarios.keys())
        self.cmb_h.configure(values=ks)
        
        # Autoseleccionar el primero disponible si el actual no es válido
        if self.cmb_h.get() not in ks:
            self.cmb_h.set(ks[0])
            
        # FORZAR actualización de minutos basada en la hora seleccionada
        self.calc_fin(None)
    def calc_fin(self, _):
        """Esta función corre al mover minutos o slider. Solo calcula, NO REINICIA nada."""
        try:
            # Simplemente leemos lo que esté seleccionado actualmente
            hf = f"{self.cmb_h.get().split()[0]}:{self.cmb_m.get()} {self.cmb_h.get().split()[1]}"
            i = datetime.strptime(hf, "%I:%M %p")
            fn = i + timedelta(minutes=int(self.slider_dur.get()))
            self.lbl_fin_hora.configure(text=f"Fin: {fn.strftime('%I:%M %p')}")
        except: pass
    def upd_slider(self, v):
        minutes = int(v)
        if minutes < 60:
            txt = f"{minutes} min"
        else:
            h = minutes // 60
            m = minutes % 60
            txt = f"{h}:{m:02d} min"
        self.lbl_dur_val.configure(text=txt)
        self.calc_fin(None)
    
    def cambiar_modo(self, m):
        if m=="Paciente Existente": 
            self.frame_bus.grid()
            self.ent_nom.configure(state="disabled")
        else: 
            self.frame_bus.grid_remove() 
            self.reset_form_only()
            self.ent_nom.configure(state="normal")
            
    def buscar_pacientes_click(self, event=None):
        query = self.ent_bus.get().strip()
        if len(query) < 2: return
        
        for w in self.results_frame.winfo_children(): w.destroy()
        
        res = self.controller.buscar_pacientes_existentes(query)
        
        if res:
            self.results_frame.pack(fill="x", pady=(0, 5))
            self.results_frame.configure(height=min(len(res)*40, 150))
            
            for p in res:
                btn = ctk.CTkButton(
                    self.results_frame, 
                    text=f"👤 {p['nombre_completo']} | {p['telefono']}", 
                    anchor="w", 
                    fg_color="transparent", 
                    text_color=TEXT_DARK, 
                    hover_color="#EEE", 
                    command=lambda d=p: self.selec_paciente_lista(d)
                )
                btn.pack(fill="x", pady=1)
        else:
            self.results_frame.pack_forget()

    def selec_paciente_lista(self, d):
        self.cliente_existente_id = d['id']
        
        self.ent_nom.configure(state="normal")
        self.ent_nom.delete(0,'end'); self.ent_nom.insert(0, d['nombre_completo'])
        self.ent_nom.configure(state="disabled")
        self.ent_tel.delete(0,'end'); self.ent_tel.insert(0,d['telefono'])
        self.ent_email.delete(0,'end'); self.ent_email.insert(0,d['email'])
        
        if d.get('rango_edad'): self.cmb_edad.set(d['rango_edad'])
        if d.get('genero'): self.cmb_gen.set("Masculino" if d['genero']=='m' else "Femenino")
        
        # Corregir lectura de Notificación (asegurar booleano)
        val_notif = d.get('notificacion', 1)
        self.var_notif.set(True if val_notif == 1 else False)

        # --- CORRECCIÓN DE TRATAMIENTO PREVIO ---
        # Leemos directo el texto que viene de la BD
        desc_bd = d.get('descripcion_tratamiento', '') or ""
        tiene_tp_mark = d.get('tratamiento_previo', 0) == 1
        
        val_prev = "Tratamiento previo: No"
        
        # Prioridad: Lo que diga el texto
        if "Interno" in desc_bd and ("Externa" in desc_bd or "," in desc_bd):
             val_prev = "Tratamiento previo: Sí, Ambas"
        elif "Interno" in desc_bd:
             val_prev = "Tratamiento previo: Sí, Clínica"
        elif "Externa" in desc_bd or tiene_tp_mark:
             val_prev = "Tratamiento previo: Sí, Externa"
            
        self.cmb_prev_opt.set(val_prev)
        self.toggle_prev(val_prev)
        
        # Cargar tratamientos externos a la lista visual
        self.tratamientos_externos = []
        if desc_bd:
            clean_txt = desc_bd.replace("Historial Interno.", "").strip()
            if clean_txt:
                parts = clean_txt.split(",")
                for p in parts:
                    if p.strip(): self.tratamientos_externos.append(p.strip())
        self.render_lista_externos()
        
        sugerida = self.controller.obtener_doctor_sugerido(d['id'])
        if sugerida:
            self.cmb_doc.set(sugerida)
            self.al_cambiar_doc(sugerida)

        self.ent_bus.delete(0, 'end'); self.ent_bus.insert(0, d['nombre_completo'])
        self.results_frame.pack_forget()

    def limpiar_busqueda(self):
        # 1. Limpiar el input de búsqueda y ocultar la lista de resultados
        self.ent_bus.delete(0, 'end')
        self.results_frame.pack_forget()

        # 2. Limpiar los campos de datos (Nombre, Tel, Email, etc.)
        # Habilitamos temporalmente el nombre para poder borrarlo
        self.ent_nom.configure(state="normal") 
        self.ent_nom.delete(0, 'end')
        self.ent_tel.delete(0, 'end')
        self.ent_email.delete(0, 'end')
        
        # Limpiar notas y placeholder
        self.txt_nota.delete("1.0", "end")
        self.lbl_ph.place(x=5, y=5)

        # Resetear selectores y variables internas
        self.cliente_existente_id = None
        self.cmb_edad.set("Edad")
        self.cmb_gen.set("Género")
        
        # Resetear Tratamiento Previo
        self.cmb_prev_opt.set("Tratamiento previo: No")
        self.toggle_prev("Tratamiento previo: No")
        
        # 3. CLAVE: Volver a bloquear el nombre
        self.ent_nom.configure(state="disabled")

    def reset_form_only(self):
        # 1. Limpiar campos de texto simples
        self.ent_nom.configure(state="normal")
        self.ent_nom.delete(0,'end')
        self.ent_tel.delete(0,'end')
        self.ent_email.delete(0,'end')
        
        # 2. Limpiar Textbox de Notas (SOLUCIÓN TEXTO FANTASMA)
        self.txt_nota.delete("1.0", "end") 
        self.lbl_ph.place(x=5, y=5) # Forzamos que aparezca el placeholder
        
        self.cliente_existente_id = None
        self.cmb_edad.set("Edad")
        self.cmb_gen.set("Género")
        self.cmb_prev_opt.set("Tratamiento previo: No")
        self.toggle_prev("Tratamiento previo: No")
        self.tipo_var.set("Presupuesto")
        if hasattr(self, 'seg'): self.seg.set("Nuevo Paciente") 
        if hasattr(self, 'seg_tipo'): self.seg_tipo.set("Presupuesto")
        self.toggle_serv("Presupuesto")

    def reset(self): 
        # 1. Limpia datos del paciente (Nombre, Tel, Email, Notas)
        self.reset_form_only()
        
        # 2. Resetear UI de búsqueda y habilitar campos
        self.frame_bus.grid_remove() 
        self.ent_nom.configure(state="normal")
        self.ent_bus.delete(0, 'end')
        self.results_frame.pack_forget()

        # 3. LIMPIAR DOCTORA
        if hasattr(self, 'cmb_doc'):
            self.cmb_doc.set("Selecciona Doctora")

        # 4. LIMPIAR FECHA (Quita la selección azul del calendario)
        self.selected_date = None
        self.render_calendar()

        # 5. LIMPIAR HORARIOS
        if hasattr(self, 'cmb_h'):
            self.cmb_h.configure(values=["--"])
            self.cmb_h.set("--")
        if hasattr(self, 'cmb_m'):
            self.cmb_m.configure(values=["--"])
            self.cmb_m.set("--")
        
        if hasattr(self, 'slider_dur'):
            self.slider_dur.set(30)
            self.lbl_dur_val.configure(text="30 min") # Reset texto visual
            
        if hasattr(self, 'lbl_fin_hora'):
            self.lbl_fin_hora.configure(text="Fin: --:--")

        # 6. Limpiar Servicios y Tratamientos Externos
        self.servicios_agregados = []
        self.actualizar_lista_servicios_visual()
        self.tratamientos_externos = []
        self.frm_ext_treats.grid_remove()

    def chk_ph(self, e): 
        if not self.txt_nota.get("1.0", "end-1c").strip(): self.lbl_ph.place(x=5, y=5)
    def _sep(self, p, r): ctk.CTkFrame(p, height=1, fg_color="#E0E0E0").grid(row=r, column=0, columnspan=2, sticky="ew", pady=(8, 0), padx=10)
    def _title(self, p, t, r): ctk.CTkLabel(p, text=t, font=("Segoe UI", 11, "bold"), text_color="#999").grid(row=r, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 2))
    
    def create_buttons(self):
        for w in self.bottom_frame.winfo_children(): w.destroy()
        
        linea = ctk.CTkFrame(self.bottom_frame, height=2, fg_color="#E0E0E0")
        linea.pack(fill="x", side="top", pady=(0, 10))
        
        ctk.CTkButton(self.bottom_frame, text="Limpiar", fg_color="#89CFF0", hover_color="#76BEE0", width=100, height=50, command=self.reset).pack(side="left", padx=(25,5), pady=5)
        
        ctk.CTkButton(
            self.bottom_frame, 
            text="CONFIRMAR CITA", 
            font=("Segoe UI", 18, "bold"), 
            fg_color=ACCENT_BLUE, 
            hover_color="#0056b3", 
            height=55, 
            corner_radius=12, 
            command=self.guardar
        ).pack(side="left", fill="x", expand=True, padx=(5, 25), pady=5)

    def al_cambiar_hora(self, hora_seleccionada):
        """Esta función SOLO corre cuando cambias la HORA. Actualiza la lista de minutos y pone el primero."""
        if hasattr(self, 'mapa_horarios') and hora_seleccionada in self.mapa_horarios:
            nuevos_minutos = self.mapa_horarios[hora_seleccionada]
            self.cmb_m.configure(values=nuevos_minutos)
            self.cmb_m.set(nuevos_minutos[0]) # Aquí sí reiniciamos al primer minuto (00)
        self.calc_fin(None)

    def guardar(self):
        try:
            if not self.ent_nom.get(): messagebox.showwarning("Error", "Falta Nombre"); return
            if not self.selected_date: messagebox.showwarning("Error", "Selecciona Fecha"); return
            if "Lleno" in self.cmb_h.get(): messagebox.showwarning("Error", "Horario ocupado"); return
            
            hf = f"{self.cmb_h.get().split()[0]}:{self.cmb_m.get()} {self.cmb_h.get().split()[1]}"
            gen = "m" if "Masculino" in self.cmb_gen.get() else "f"
            
            prev_opt = self.cmb_prev_opt.get()
            prev_desc = ""
            if "Externa" in prev_opt or "Ambas" in prev_opt:
                prev_desc = ", ".join(self.tratamientos_externos)
            if "Clínica" in prev_opt: 
                prev_desc = f"Historial Interno. {prev_desc}"

            raw_min = int(self.slider_dur.get())
            dur_str = f"{raw_min} min"

            # Lógica correcta para TP
            es_previo = ("Externa" in prev_opt) or ("Clínica" in prev_opt) or ("Ambas" in prev_opt)
            if self.tratamientos_externos: es_previo = True

            d = {
                'cliente_id_existente': self.cliente_existente_id, 
                'nombre': self.ent_nom.get().strip(), 
                'telefono': self.ent_tel.get().strip(), 
                'email': self.ent_email.get().strip(), 
                'edad': self.cmb_edad.get(), 
                'genero': gen, 
                'doctora': self.cmb_doc.get(), 
                'fecha': self.selected_date.strftime("%Y-%m-%d"), 
                'hora_inicio': hf, 
                'duracion': dur_str, 
                'tipo_cita': self.tipo_var.get(), 
                'notificar': self.var_notif.get(), 
                'descripcion': self.txt_nota.get("1.0","end-1c").strip(), 
                'previo_desc': prev_desc
            }
            
            ok, m = self.controller.guardar_cita_completa(d, self.servicios_agregados, self.user_id)
            
            if ok:
                messagebox.showinfo("Éxito", m)
                
                # Intentar notificar usando el Helper nuevo
                try:
                    if self.var_notif.get():
                        from notifications_helper import NotificationsHelper
                        NotificationsHelper.enviar_notificacion_agendar(
                            d['nombre'], d['fecha'], hf, d['telefono'], d['email']
                        )
                except Exception as e:
                    print(f"Error al notificar: {e}")

                # Limpiar siempre
                self.reset()
                self.create_sidebar()
            else: 
                messagebox.showerror("Error", m)
                
        except Exception as e: 
            messagebox.showerror("Error Crítico", str(e))
    def enviar_wa(self, tel, nom, fec, hor):
        num = "".join(filter(str.isdigit, tel))
        if len(num)<10: return
        txt = f"Hola {nom}, cita confirmada: {fec} a las {hor}. Ortho Guzmán."
        webbrowser.open(f"https://web.whatsapp.com/send?phone={num}&text={urllib.parse.quote(txt)}")
