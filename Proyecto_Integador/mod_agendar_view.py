import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta, date
import calendar
from mod_agendar_controller import ModificarCitaController
from agendar_controller import AgendarCitaController 
from notifications_helper import NotificationsHelper

# --- CONFIGURACIÓN VISUAL ---
BG_MAIN = "#F4F6F9"
WHITE_CARD = "#FFFFFF"
ACCENT_BLUE = "#007BFF"
TEXT_DARK = "#333333"
BORDER_COLOR = "#D1D5DB"
HEADER_CAL = "#E8F0FE"
DANGER_COLOR = "#DC3545"
SUCCESS_COLOR = "#28A745"
WARNING_COLOR = "#FFC107"

class ModificarCitaView(ctk.CTkFrame):
    def __init__(self, master, cita_id, callback_volver, current_user_id):
        super().__init__(master, fg_color=BG_MAIN) 
        self.ctrl = ModificarCitaController()
        self.aux_ctrl = AgendarCitaController() 
        
        self.cita_id = cita_id
        self.callback_volver = callback_volver
        self.current_user_id = current_user_id 
        
        self.tratamientos_externos = [] 

        self.bind("<Button-1>", lambda e: self.focus_set())

        # Cargar datos
        self.data_completa = self.ctrl.obtener_cita_data(cita_id)
        if not self.data_completa:
            messagebox.showerror("Error", "No se pudo cargar la información de la cita.")
            self.callback_volver()
            return

        self.datos_cita = self.data_completa['cita'] 
        self.es_cancelada = (self.datos_cita['estado'] == 'Cancelada')
        
        # Recuperar servicios de la cita
        self.servicios_agregados = []
        for s in self.data_completa.get('servicios', []):
            self.servicios_agregados.append({
                'id': s['id'], 'nombre': s['nombre'], 
                'cantidad': s['cantidad'], 'unidad': s['unidad'],
                'precio_unitario': float(s['precio_unitario']), 'precio_total': float(s['precio_total'])
            })
            
        self.selected_date = self.datos_cita['fecha_cita']
        self.display_date = self.selected_date 
        
        # Grid Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._crear_header()
        
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.main_container.grid_columnconfigure(0, weight=1) 
        self.main_container.grid_columnconfigure(1, weight=3) 
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.bind("<Button-1>", lambda e: self.focus_set())

        self._crear_menu_lateral()
        self._crear_area_contenido()

        self.mostrar_panel("paciente")

    def _crear_header(self):
        h = ctk.CTkFrame(self, fg_color="transparent", height=50)
        h.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))
        h.bind("<Button-1>", lambda e: self.focus_set())
        
        btn_back = ctk.CTkButton(h, text="◄ Regresar", fg_color="transparent", border_color=ACCENT_BLUE, border_width=1, text_color=ACCENT_BLUE, hover_color="#E8F0FE", width=100, command=self.callback_volver)
        btn_back.pack(side="left")
        
        ctk.CTkLabel(h, text=f"EDITAR CITA #{self.cita_id}", font=("Segoe UI", 16, "bold"), text_color=TEXT_DARK).pack(side="left", padx=20)

    def _crear_menu_lateral(self):
        self.sidebar = ctk.CTkFrame(self.main_container, fg_color=WHITE_CARD, corner_radius=15, border_color=BORDER_COLOR, border_width=1)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        self.sidebar.bind("<Button-1>", lambda e: self.focus_set())
        
        ctk.CTkLabel(self.sidebar, text="SECCIONES", font=("Segoe UI", 12, "bold"), text_color="#999").pack(anchor="w", padx=20, pady=(20, 10))
        
        self.btn_pac = self._sidebar_btn("👤 Datos Paciente", lambda: self.mostrar_panel("paciente"))
        self.btn_fec = self._sidebar_btn("📅 Fecha y Hora", lambda: self.mostrar_panel("fecha"))
        self.btn_ser = self._sidebar_btn("🦷 Servicios", lambda: self.mostrar_panel("servicios"))
        self.btn_not = self._sidebar_btn("📝 Notas / Obs.", lambda: self.mostrar_panel("notas"))
        
        if not self.es_cancelada:
            ctk.CTkFrame(self.sidebar, height=2, fg_color="#F0F0F0").pack(fill="x", padx=15, pady=20)
            ctk.CTkLabel(self.sidebar, text="ACCIONES", font=("Segoe UI", 12, "bold"), text_color="#999").pack(anchor="w", padx=20, pady=(0, 5))
            ctk.CTkButton(self.sidebar, text="🗑️ Cancelar Cita", fg_color="#FFF0F0", text_color=DANGER_COLOR, hover_color="#FFE5E5", border_color=DANGER_COLOR, border_width=1, anchor="w", height=40, command=self.cancelar).pack(fill="x", padx=15, pady=5)

    def _sidebar_btn(self, txt, cmd):
        btn = ctk.CTkButton(self.sidebar, text=txt, fg_color="transparent", text_color=TEXT_DARK, anchor="w", hover_color="#F0F2F5", height=40, command=cmd)
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def _crear_area_contenido(self):
        self.content_area = ctk.CTkFrame(self.main_container, fg_color=WHITE_CARD, corner_radius=15, border_color=BORDER_COLOR, border_width=1)
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=0, pady=10)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=0)
        self.content_area.bind("<Button-1>", lambda e: self.focus_set())

        self.frm_paciente = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self._build_paciente_form(self.frm_paciente)
        
        self.frm_fecha = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self._build_fecha_form(self.frm_fecha)
        
        self.frm_servicios = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self._build_servicios_form(self.frm_servicios)
        
        self.frm_notas = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self._build_notas_form(self.frm_notas)

        # Botón Guardar Global
        if not self.es_cancelada:
            btn_save = ctk.CTkButton(self.content_area, text="💾 GUARDAR CAMBIOS", fg_color=ACCENT_BLUE, hover_color="#0056b3", height=50, font=("Segoe UI", 13, "bold"), command=self.guardar_todo)
            btn_save.grid(row=1, column=0, sticky="ew", padx=30, pady=20)
        else:
            ctk.CTkLabel(self.content_area, text="⛔ Cita Cancelada - Solo Lectura", text_color=DANGER_COLOR, font=("bold", 14)).grid(row=1, column=0, pady=20)

    def mostrar_panel(self, nombre):
        for f in [self.frm_paciente, self.frm_fecha, self.frm_servicios, self.frm_notas]:
            f.grid_forget()
        for b in [self.btn_pac, self.btn_fec, self.btn_ser, self.btn_not]:
            b.configure(fg_color="transparent", font=("Segoe UI", 12))

        if nombre == "paciente":
            self.frm_paciente.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
            self.btn_pac.configure(fg_color="#E3F2FD", font=("Segoe UI", 12, "bold"))
        elif nombre == "fecha":
            self.frm_fecha.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
            self.btn_fec.configure(fg_color="#E3F2FD", font=("Segoe UI", 12, "bold"))
        elif nombre == "servicios":
            self.frm_servicios.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
            self.btn_ser.configure(fg_color="#E3F2FD", font=("Segoe UI", 12, "bold"))
        elif nombre == "notas":
            self.frm_notas.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
            self.btn_not.configure(fg_color="#E3F2FD", font=("Segoe UI", 12, "bold"))

    # =========================================================================
    # --- PANELES ---
    # =========================================================================
    
    def _build_paciente_form(self, parent):
        for widget in parent.winfo_children(): widget.destroy()
        parent.bind("<Button-1>", lambda e: self.focus_set())
        
        # --- SECCIÓN 1: INFORMACIÓN PERSONAL ---
        ctk.CTkLabel(parent, text="INFORMACIÓN PERSONAL", font=("Segoe UI", 11, "bold"), text_color="#999").pack(anchor="w", pady=(0, 10))
        self.ent_nombre = self._campo_input(parent, "Nombre Completo", self.datos_cita['nombre_completo'], placeholder="Ej: Juan Pérez")
        ctk.CTkFrame(parent, height=1, fg_color="#E0E0E0").pack(fill="x", pady=15)

        # --- SECCIÓN 2: MEDIOS DE CONTACTO ---
        ctk.CTkLabel(parent, text="MEDIOS DE CONTACTO", font=("Segoe UI", 11, "bold"), text_color="#999").pack(anchor="w", pady=(0, 5))
        frm_contact = ctk.CTkFrame(parent, fg_color="#F9F9F9", corner_radius=8)
        frm_contact.pack(fill="x", pady=5)
        
        row_tel = ctk.CTkFrame(frm_contact, fg_color="transparent")
        row_tel.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(row_tel, text="📱", font=("Arial", 16), text_color="black").pack(side="left", padx=(5,10))
        self.ent_tel = ctk.CTkEntry(row_tel, placeholder_text="Teléfono / WhatsApp", height=35, fg_color="white", border_color="#DDD", text_color="#333", placeholder_text_color="#999")
        val_tel = self.datos_cita.get('telefono', '')
        if val_tel: self.ent_tel.insert(0, str(val_tel))
        self.ent_tel.pack(side="left", fill="x", expand=True)

        row_mail = ctk.CTkFrame(frm_contact, fg_color="transparent")
        row_mail.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(row_mail, text="📧", font=("Arial", 16), text_color="black").pack(side="left", padx=(5,10))
        self.ent_email = ctk.CTkEntry(row_mail, placeholder_text="Correo Electrónico", height=35, fg_color="white", border_color="#DDD", text_color="#333", placeholder_text_color="#999")
        val_email = self.datos_cita.get('email', '')
        if val_email: self.ent_email.insert(0, str(val_email))
        self.ent_email.pack(side="left", fill="x", expand=True)

        val_notif = self.datos_cita.get('notificacion', 1)
        self.var_notif = ctk.BooleanVar(value=bool(val_notif))
        ctk.CTkSwitch(frm_contact, text="🔔 Notificar cambios por WhatsApp/Correo", variable=self.var_notif, progress_color=SUCCESS_COLOR, font=("Segoe UI", 12), text_color="#333").pack(anchor="w", padx=15, pady=(10, 15))
        ctk.CTkFrame(parent, height=1, fg_color="#E0E0E0").pack(fill="x", pady=15)

        # --- SECCIÓN 3: ANTECEDENTES CLÍNICOS ---
        ctk.CTkLabel(parent, text="ANTECEDENTES CLÍNICOS", font=("Segoe UI", 11, "bold"), text_color="#999").pack(anchor="w", pady=(0, 5))
        frm_prev_cont = ctk.CTkFrame(parent, fg_color="transparent"); frm_prev_cont.pack(fill="x", pady=5)
        
        # --- CORRECCIÓN LÓGICA DE CARGA ---
        # 1. Usamos 'desc_previo' que es como viene de la consulta SQL (JOIN)
        desc_prev = self.datos_cita.get('desc_previo', '') or ""
        if desc_prev is None: desc_prev = ""
        
        # 2. Lógica estricta basada en el texto guardado
        def_val = "Tratamiento previo: No"
        
        if "Interno" in desc_prev and ("Externa" in desc_prev or "," in desc_prev): 
             def_val = "Tratamiento previo: Sí, Ambas"
        elif "Interno" in desc_prev or "Clínica" in desc_prev: 
             def_val = "Tratamiento previo: Sí, Clínica"
        elif "Externa" in desc_prev or self.datos_cita.get('tratamiento_previo') == 1: 
             def_val = "Tratamiento previo: Sí, Externa"

        self.cmb_prev_opt = ctk.CTkOptionMenu(frm_prev_cont, values=["Tratamiento previo: No", "Tratamiento previo: Sí, Clínica", "Tratamiento previo: Sí, Externa", "Tratamiento previo: Sí, Ambas"], command=self.toggle_prev, fg_color="white", text_color=TEXT_DARK, button_color="#CCC")
        self.cmb_prev_opt.set(def_val)
        self.cmb_prev_opt.pack(side="left", fill="x", expand=True)

        self.frm_ext_treats = ctk.CTkFrame(parent, fg_color="#FAFAFA", border_color="#EEE", border_width=1)
        self.tratamientos_externos = [] 
        
        # 3. Limpiamos el texto para mostrar solo lo externo en la lista
        if desc_prev:
            raw_txt = desc_prev.replace("Historial Interno.", "").strip()
            if raw_txt:
                parts = raw_txt.split(",")
                for p in parts:
                    clean_p = p.strip().rstrip('.') # Quitar puntos finales extra
                    if clean_p: self.tratamientos_externos.append(clean_p)

        row_add = ctk.CTkFrame(self.frm_ext_treats, fg_color="transparent")
        row_add.pack(fill="x", padx=5, pady=5)
        self.ent_ext_treat = ctk.CTkEntry(row_add, placeholder_text="Escribe tratamiento y pulsa +", height=30, fg_color="white", text_color="black")
        self.ent_ext_treat.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row_add, text="+", width=40, fg_color=SUCCESS_COLOR, command=self.agregar_tratamiento_externo).pack(side="left", padx=5)
        
        self.scroll_ext_list = ctk.CTkScrollableFrame(self.frm_ext_treats, height=100, fg_color="transparent")
        self.scroll_ext_list.pack(fill="x", padx=5, pady=2)
        self.render_lista_externos()

        if "Externa" in def_val or "Ambas" in def_val: self.frm_ext_treats.pack(fill="x", pady=(5,0))
        else: self.frm_ext_treats.pack_forget()

    def toggle_prev(self, val):
        if "Externa" in val or "Ambas" in val: self.frm_ext_treats.pack(fill="x", pady=(5,0))
        else: self.frm_ext_treats.pack_forget()

    def agregar_tratamiento_externo(self):
        t = self.ent_ext_treat.get().strip()
        if t: 
            self.tratamientos_externos.append(t)
            self.ent_ext_treat.delete(0, 'end')
            self.render_lista_externos()

    def eliminar_tratamiento_externo(self, index):
        self.tratamientos_externos.pop(index)
        self.render_lista_externos()

    def render_lista_externos(self):
        for w in self.scroll_ext_list.winfo_children(): w.destroy()
        if not self.tratamientos_externos:
            ctk.CTkLabel(self.scroll_ext_list, text="Ningún tratamiento registrado.", text_color="gray", font=("Arial", 10)).pack(anchor="w", padx=5)
            return
        for i, t in enumerate(self.tratamientos_externos):
            row = ctk.CTkFrame(self.scroll_ext_list, fg_color="white", corner_radius=6)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"• {t}", font=("Arial", 11), text_color="#333").pack(side="left", padx=5)
            ctk.CTkButton(row, text="×", width=25, height=20, fg_color="transparent", text_color=DANGER_COLOR, hover_color="#FFE5E5", command=lambda x=i: self.eliminar_tratamiento_externo(x)).pack(side="right", padx=5)

    def _build_fecha_form(self, parent):
        parent.bind("<Button-1>", lambda e: self.focus_set())
        ctk.CTkLabel(parent, text="REPROGRAMACIÓN DE CITA", font=("Segoe UI", 16, "bold"), text_color=ACCENT_BLUE).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkLabel(parent, text="Especialista:", font=("bold", 12)).pack(anchor="w")
        nombres_docs = [d['nombre'] for d in self.ctrl.lista_doctoras]
        self.opt_doc = ctk.CTkOptionMenu(parent, values=nombres_docs, fg_color="white", text_color=TEXT_DARK, button_color="#CCC")
        self.opt_doc.set(self.datos_cita.get('doctora_nombre', ''))
        self.opt_doc.pack(fill="x", pady=(5, 20))
        self.opt_doc.configure(command=self.al_cambiar_doc)

        row_dt = ctk.CTkFrame(parent, fg_color="transparent")
        row_dt.pack(fill="x", expand=True)
        
        self.cal_frame = ctk.CTkFrame(row_dt, fg_color="white", border_color="#DDD", border_width=1)
        self.cal_frame.pack(side="left", padx=(0, 20), anchor="n")
        self.render_calendar() 

        right_tm = ctk.CTkFrame(row_dt, fg_color="transparent")
        right_tm.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(right_tm, text="Hora Inicio:", font=("bold", 12)).pack(anchor="w")
        row_clk = ctk.CTkFrame(right_tm, fg_color="transparent"); row_clk.pack(fill="x", pady=(5, 15))
        
        try:
            h_obj = (datetime.min + self.datos_cita['hora_inicio']).time()
            h_actual = h_obj.strftime("%I %p") 
            m_actual = h_obj.strftime("%M")    
        except: h_actual="--"; m_actual="--"

        self.cmb_h = ctk.CTkOptionMenu(row_clk, values=[h_actual], width=100, fg_color="#E8F0FE", text_color="black", command=self.calc_fin)
        self.cmb_h.pack(side="left", padx=(0, 5))
        self.cmb_m = ctk.CTkOptionMenu(row_clk, values=[m_actual], width=100, fg_color="#E8F0FE", text_color="black", command=self.calc_fin)
        self.cmb_m.pack(side="left")
        
        ctk.CTkLabel(right_tm, text="Duración:", font=("bold", 12)).pack(anchor="w")
        try:
            t1 = datetime.strptime(str(self.datos_cita['hora_inicio']), "%H:%M:%S")
            t2 = datetime.strptime(str(self.datos_cita['hora_final']), "%H:%M:%S")
            diff = (t2 - t1).seconds // 60
        except: diff = 30
        
        self.lbl_dur_val = ctk.CTkLabel(right_tm, text=self._fmt_min(diff), font=("Arial", 13, "bold"), text_color=ACCENT_BLUE)
        self.lbl_dur_val.pack(anchor="w")
        self.slider_dur = ctk.CTkSlider(right_tm, from_=5, to=300, number_of_steps=59, command=self.upd_slider)
        self.slider_dur.set(diff)
        self.slider_dur.pack(fill="x", pady=5)
        
        self.lbl_fin = ctk.CTkLabel(right_tm, text="Hora Fin: --:--", text_color="gray")
        self.lbl_fin.pack(anchor="w")
        self.after(100, self.act_horarios)

    def _build_servicios_form(self, parent):
        for w in parent.winfo_children(): w.destroy()
        parent.bind("<Button-1>", lambda e: self.focus_set())
        ctk.CTkLabel(parent, text="SERVICIOS Y PRESUPUESTO", font=("Segoe UI", 16, "bold"), text_color=ACCENT_BLUE).pack(anchor="w", pady=(0, 10))
        
        val_inicial = self.datos_cita.get('tipo', 'Presupuesto')
        self.tipo_var = ctk.StringVar(value=val_inicial)
        
        seg = ctk.CTkSegmentedButton(parent, values=["Presupuesto", "Tratamiento"], variable=self.tipo_var, selected_color=ACCENT_BLUE, command=self.toggle_serv)
        seg.pack(fill="x", pady=10)
        
        self.frm_serv_container = ctk.CTkFrame(parent, fg_color="#FAFAFA", border_color="#EEE", border_width=2)
        
        ctk.CTkButton(self.frm_serv_container, text="+ Agregar Servicio del Catálogo", fg_color="transparent", border_color=ACCENT_BLUE, border_width=1, text_color=ACCENT_BLUE, command=self.open_serv_popup).pack(fill="x", padx=10, pady=10)
        
        self.lst_serv_visual = ctk.CTkScrollableFrame(self.frm_serv_container, fg_color="transparent", height=200)
        self.lst_serv_visual.pack(fill="both", expand=True, padx=5, pady=5)
        self.lst_serv_visual.bind("<Button-1>", lambda e: self.focus_set())
        
        self.lbl_tot = ctk.CTkLabel(self.frm_serv_container, text="Total: $0.00", font=("Arial", 16, "bold"), text_color=SUCCESS_COLOR)
        self.lbl_tot.pack(anchor="e", padx=15, pady=10)

        self.actualizar_lista_servicios_visual()
        self.toggle_serv(val_inicial)

    def toggle_serv(self, val):
        if val == "Tratamiento":
            self.frm_serv_container.pack(fill="both", expand=True, padx=5, pady=10)
        else:
            self.frm_serv_container.pack_forget()

    def _build_notas_form(self, parent):
        parent.bind("<Button-1>", lambda e: self.focus_set())
        ctk.CTkLabel(parent, text="NOTAS Y OBSERVACIONES", font=("Segoe UI", 16, "bold"), text_color=ACCENT_BLUE).pack(anchor="w", pady=(0, 20))
        self.txt_desc = ctk.CTkTextbox(parent, height=150, fg_color="white", border_color=BORDER_COLOR, border_width=1, text_color="black")
        self.txt_desc.insert("1.0", self.datos_cita.get('descripcion') or "")
        self.txt_desc.pack(fill="both", expand=True)

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
                es_sel = (self.selected_date and d == self.selected_date.day and self.selected_date.month == self.display_date.month)
                bg = ACCENT_BLUE if es_sel else "white"
                fg = "white" if es_sel else ("#CCC" if dt < hoy else "black")
                st = "disabled" if dt < hoy else "normal"
                if es_sel: st="normal" 
                ctk.CTkButton(g, text=str(d), width=30, height=28, fg_color=bg, text_color=fg, state=st, hover_color="#D9EFFF" if not es_sel else "#0056b3", command=lambda x=d: self.set_day(x)).grid(row=r, column=c, padx=1, pady=1)

    def mv_cal(self, m):
        nm = self.display_date.month + m; ny = self.display_date.year
        if nm>12: nm=1; ny+=1
        elif nm<1: nm=12; ny-=1
        self.display_date = self.display_date.replace(year=ny, month=nm); self.render_calendar()
    
    def set_day(self, d): 
        self.selected_date = datetime(self.display_date.year, self.display_date.month, d).date()
        self.render_calendar()
        self.act_horarios()

    def al_cambiar_doc(self, _): 
        if self.selected_date: self.act_horarios()

    def act_horarios(self):
        d = self.opt_doc.get()
        if not d or not self.selected_date: return
        
        dt_full = datetime.combine(self.selected_date, datetime.min.time())
        s = self.ctrl.obtener_horas_disponibles_edicion(dt_full, d, self.cita_id)
        
        # --- LÓGICA PARA RECUPERAR HORA Y MINUTO ORIGINAL ---
        es_mismo_dia_db = (self.selected_date == self.datos_cita['fecha_cita'])
        target_h_db = None 
        target_m_db = None # Variable nueva para el minuto

        if es_mismo_dia_db:
            raw = self.datos_cita['hora_inicio']
            # Convertir timedelta a time si es necesario
            if isinstance(raw, timedelta): raw = (datetime.min + raw).time()
            
            # Formatear a estilo AM/PM para buscar en el mapa
            hora_visual_actual = raw.strftime("%I:%M %p") # "11:15 AM"
            parts_t = hora_visual_actual.split(":") 
            
            if len(parts_t) > 1:
                # Clave Hora: "11 AM"
                target_h_db = f"{parts_t[0]} {parts_t[1].split()[1]}" 
                # Valor Minuto: "15"
                target_m_db = parts_t[1].split()[0]

            # Inyectar la hora actual en la lista de disponibles si no está
            if hora_visual_actual not in s:
                s.append(hora_visual_actual)
                s.sort(key=lambda x: datetime.strptime(x, "%I:%M %p"))

        self.mapa_horarios = {}
        if not s: 
            self.cmb_h.configure(values=["Lleno"]); self.cmb_h.set("Lleno")
            self.cmb_m.configure(values=["--"]); self.cmb_m.set("--")
            self.lbl_fin.configure(text="Fin: --:--")
            return
            
        for x in s:
            try:
                parts = x.split(":") 
                h_part = parts[0]; rest = parts[1].split() 
                m_part = rest[0]; ampm = rest[1]
                h_k = f"{h_part} {ampm}"
                m_v = m_part
                if h_k not in self.mapa_horarios: self.mapa_horarios[h_k]=[]
                if m_v not in self.mapa_horarios[h_k]: self.mapa_horarios[h_k].append(m_v)
            except: continue
            
        ks = list(self.mapa_horarios.keys())
        self.cmb_h.configure(values=ks)
        
        seleccion_h = ks[0] if ks else ""
        
        if target_h_db and target_h_db in ks:
            seleccion_h = target_h_db
        elif self.cmb_h.get() in ks:
            seleccion_h = self.cmb_h.get()
            
        self.cmb_h.set(seleccion_h)
        
        # --- ACTUALIZAR MINUTOS Y FORZAR EL CORRECTO ---
        # 1. Cargamos los minutos disponibles para esa hora
        vals_m = self.mapa_horarios.get(seleccion_h, ["00"])
        self.cmb_m.configure(values=vals_m)
        
        # 2. Intentamos poner el minuto original de la BD
        if target_m_db and target_m_db in vals_m:
            self.cmb_m.set(target_m_db)
        # 3. Si no, mantenemos el que estaba o ponemos el primero
        elif self.cmb_m.get() not in vals_m:
            self.cmb_m.set(vals_m[0])
            
        # Calcular hora fin visualmente
        self.calc_fin(None)

    def calc_fin(self, _):
        if hasattr(self, 'mapa_horarios') and self.cmb_h.get() in self.mapa_horarios:
            vals = self.mapa_horarios[self.cmb_h.get()]
            self.cmb_m.configure(values=vals)
            if self.cmb_m.get() not in vals: self.cmb_m.set(vals[0])
        
        try:
            hf = f"{self.cmb_h.get().split()[0]}:{self.cmb_m.get()} {self.cmb_h.get().split()[1]}"
            i = datetime.strptime(hf, "%I:%M %p")
            fn = i + timedelta(minutes=int(self.slider_dur.get()))
            self.lbl_fin.configure(text=f"Fin: {fn.strftime('%I:%M %p')}")
        except: pass

    def upd_slider(self, v): 
        self.lbl_dur_val.configure(text=self._fmt_min(int(v)))
        self.calc_fin(None)
    
    def _fmt_min(self, m): return f"{m} min" if m < 60 else f"{m//60} h {m%60} min"

    def _campo_input(self, parent, label, val, side="top", placeholder=""):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side=side, fill="x", expand=True, padx=5)
        ctk.CTkLabel(f, text=label, font=("bold", 12)).pack(anchor="w")
        e = ctk.CTkEntry(f, height=38, fg_color="white", border_color=BORDER_COLOR, text_color="black", placeholder_text=placeholder)
        if val: e.insert(0, str(val))
        e.pack(fill="x", pady=(2, 0))
        return e

    # --- LÓGICA DE POPUP Y FILTROS COMPLETA (Igual a Agendar) ---
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
        
        # Filtro Categoría (Usamos self.aux_ctrl para consultar catálogo)
        cats = ["Todas"] + self.aux_ctrl.obtener_categorias_unicas()
        ctk.CTkLabel(row1, text="Categoría:", font=("bold", 12)).pack(side="left")
        self.pop_cat = ctk.CTkOptionMenu(row1, values=cats, command=self._act_subs_popup, width=150, fg_color="#FAFAFA", text_color=TEXT_DARK)
        self.pop_cat.pack(side="left", padx=5)
        
        # Filtro Subcategoría
        ctk.CTkLabel(row1, text="Subcategoría:", font=("bold", 12)).pack(side="left", padx=(15,0))
        self.pop_sub = ctk.CTkOptionMenu(row1, values=["Todas"], command=lambda x: self._cargar_lista_popup(), width=150, fg_color="#FAFAFA", text_color=TEXT_DARK)
        self.pop_sub.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(f, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0,10))
        
        # Buscador Texto
        self.pop_search = ctk.CTkEntry(row2, placeholder_text="🔍 Buscar...", fg_color="#FAFAFA")
        self.pop_search.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.pop_search.bind("<KeyRelease>", lambda e: self._cargar_lista_popup())
        
        # Botón Limpiar
        ctk.CTkButton(row2, text="Limpiar", width=80, fg_color="#DDD", text_color="black", command=self._reset_filtros_popup).pack(side="right")

        self.pop_list = ctk.CTkScrollableFrame(self.top_serv, fg_color="transparent")
        self.pop_list.pack(fill="both", expand=True, padx=15, pady=(0,15))
        
        self._cargar_lista_popup()
    
    def _act_subs_popup(self, cat):
        if cat == "Todas": subs = ["Todas"]
        else: subs = ["Todas"] + self.aux_ctrl.obtener_subcategorias_por_cat(cat)
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
        
        # Cotización Manual si es $0
        if precio_final == 0:
            dialog = ctk.CTkInputDialog(text=f"Cotización para: {item['nombre']}\nIngrese el costo unitario ($):", title="Cotizar Servicio")
            try: dialog.geometry(f"+{self.top_serv.winfo_rootx()+50}+{self.top_serv.winfo_rooty()+50}")
            except: pass
            
            input_str = dialog.get_input()
            if not input_str: return 
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
            if s['unidad'] and s['unidad'] not in ["Unidad", ""]: desc += f" ({s['unidad']})"
            ctk.CTkLabel(row, text=desc, font=("bold", 11), text_color=TEXT_DARK, fg_color="transparent").pack(side="left", padx=10, pady=5)
            right_box = ctk.CTkFrame(row, fg_color="transparent"); right_box.pack(side="right", padx=5)
            ctk.CTkLabel(right_box, text=f"${s['precio_total']:,.2f}", font=("bold", 12), text_color=ACCENT_BLUE, fg_color="transparent").pack(side="left", padx=10)
            ctk.CTkButton(right_box, text="-", width=25, height=25, fg_color="#EEE", text_color="black", hover_color="#DDD", command=lambda i=idx: self._cambiar_cantidad(i, -1)).pack(side="left", padx=2)
            ctk.CTkLabel(right_box, text=str(s['cantidad']), width=20, font=("bold", 12), text_color=TEXT_DARK).pack(side="left", padx=2)
            ctk.CTkButton(right_box, text="+", width=25, height=25, fg_color="#EEE", text_color="black", hover_color="#DDD", command=lambda i=idx: self._cambiar_cantidad(i, 1)).pack(side="left", padx=2)
            ctk.CTkButton(right_box, text="🗑️", width=30, height=25, fg_color="transparent", text_color=DANGER_COLOR, hover_color="#FFEEEE", command=lambda i=idx: self.eliminar_servicio(i)).pack(side="left", padx=(10, 0))
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
    
    def guardar_todo(self):
        # 1. Validaciones previas
        if not self.ent_nombre.get().strip():
            messagebox.showwarning("Faltan datos", "El nombre del paciente es obligatorio.")
            self.mostrar_panel("paciente"); return
        if "Lleno" in self.cmb_h.get():
            messagebox.showwarning("Horario Ocupado", "El horario seleccionado no está disponible.")
            self.mostrar_panel("fecha"); return

        # 2. Preparar datos
        h_str = str(self.datos_cita['hora_inicio'])
        if hasattr(self, 'cmb_h'):
            h_str = f"{self.cmb_h.get().split()[0]}:{self.cmb_m.get()} {self.cmb_h.get().split()[1]}"
        
        prev_opt = self.cmb_prev_opt.get()
        prev_desc = ""
        if "Externa" in prev_opt or "Ambas" in prev_opt: prev_desc = ", ".join(self.tratamientos_externos)
        if "Clínica" in prev_opt: prev_desc = f"Historial Interno. {prev_desc}"

        datos = {
            'cliente_id': self.datos_cita['cliente_id_real'],
            'nombre': self.ent_nombre.get().strip(),
            'telefono': self.ent_tel.get().strip(),
            'email': self.ent_email.get().strip(),
            'notificar': self.var_notif.get(),
            'doctora': self.opt_doc.get(),
            'fecha': self.selected_date, 
            'hora_inicio': h_str, 
            'duracion_minutos': int(self.slider_dur.get()), 
            'tipo_cita': self.tipo_var.get(),
            'estado': self.datos_cita['estado'], 
            'descripcion': self.txt_desc.get("1.0", "end-1c").strip(),
            'servicios_actualizados': self.servicios_agregados,
            'previo_desc': prev_desc
        }
        
        # 3. Llamada al Controlador
        status, msg, lista_afectados = self.ctrl.guardar_cambios(self.cita_id, datos, self.current_user_id)
        
        if status == "pregunta_dia":
            if messagebox.askyesno("Horario Excedido", f"{msg}\n\nSÍ: Cancelar para ajustar manual.\nNO: Guardar excediendo horario."):
                return 
            else: pass 

        if status == "ok" or status == "pregunta_dia":
            import time
            from notifications_helper import NotificationsHelper
            
            # A. Notificar al dueño de la cita actual
            if self.var_notif.get():
                NotificationsHelper.enviar_notificacion_modificacion(
                    datos['nombre'], datos['fecha'], datos['hora_inicio'], datos['telefono'], datos['email'], es_recorrida=False
                )
                time.sleep(1.5)

            # B. MANEJO INTELIGENTE DE AFECTADOS (PROTECCIÓN)
            cantidad = len(lista_afectados)
            LIMITE_SEGURO = 10 

            if cantidad > 0:
                if cantidad <= LIMITE_SEGURO:
                    # --- MODO AUTOMÁTICO (Hasta 10 afectados) ---
                    count = 0
                    for p in lista_afectados:
                        if p['notif']: 
                            if count > 0: time.sleep(2.5) 
                            NotificationsHelper.enviar_notificacion_modificacion(
                                p['nombre'], p['fecha'], p['hora'], p['telefono'], p['email'], es_recorrida=True
                            )
                            count += 1
                    messagebox.showinfo("Éxito", f"Se guardó y se abrieron {count} notificaciones.")
                else:
                    # --- MODO LISTA DE TAREAS (Más de 10) ---
                    self._mostrar_resumen_masivo(lista_afectados)
                    messagebox.showinfo("Éxito", "Cambios guardados.\nDebido a la gran cantidad de cambios, usa la lista generada para notificar manualmente.")
            else:
                messagebox.showinfo("Éxito", "Cambios guardados correctamente.")

            if self.callback_volver: self.callback_volver()
            
        elif status == "error":
            messagebox.showerror("Error", msg)

    def cancelar(self):
        if messagebox.askyesno("Confirmar Cancelación", "¿Estás seguro que deseas CANCELAR esta cita de forma permanente?"):
            self.ctrl.cancelar_cita(self.cita_id, self.current_user_id)
            messagebox.showinfo("Cancelada", "La cita ha sido marcada como cancelada.")
            self.callback_volver()
