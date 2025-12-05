import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
import calendar
from mod_agendar_controller import ModificarCitaController

# Configuración Visual
BG_MAIN = "#F4F6F9"
WHITE_CARD = "#FFFFFF"
TEXT_DARK = "#333333"
ACCENT_BLUE = "#007BFF"
SOFT_BLUE_BTN = "#89CFF0" 
BORDER_COLOR = "#E0E0E0"
HEADER_CALENDAR = "#E8F0FE"
DANGER_COLOR = "#DC3545"
SUCCESS_COLOR = "#28A745"
WARNING_COLOR = "#FFC107"
INFO_COLOR = "#17A2B8"

class ModificarCitaFrame(ctk.CTkFrame):
    
    def __init__(self, master):
        super().__init__(master, fg_color=BG_MAIN)
        self.controller = ModificarCitaController()
        self.tarjeta_seleccionada = None
        self.servicios_agregados = []
        
        self.cita_id_actual = None
        self.cliente_id_actual = None
        self.selected_date = None
        self.display_date = datetime.now()
        
        self.mapa_horarios = {} # Para hora dividida

        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        # --- IZQUIERDA ---
        self.left_card = ctk.CTkFrame(self, fg_color=WHITE_CARD, corner_radius=15, border_color=BORDER_COLOR, border_width=1)
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.left_card.grid_rowconfigure(0, weight=1) 
        self.left_card.grid_columnconfigure(0, weight=1)

        self.scroll = ctk.CTkScrollableFrame(self.left_card, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scroll.grid_columnconfigure(0, weight=1)
        
        self.bottom_frame = ctk.CTkFrame(self.left_card, fg_color="transparent", height=70)
        self.bottom_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 10))
        self.bottom_frame.grid_columnconfigure((0, 1), weight=1)

        self.create_form()
        self.create_buttons()

        # --- DERECHA ---
        self.right_sidebar = ctk.CTkFrame(self, fg_color="transparent")
        self.right_sidebar.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.right_sidebar.grid_rowconfigure(1, weight=1)
        self.right_sidebar.grid_columnconfigure(0, weight=1)
        
        self.create_search_panel()
        self.create_results_list()
        
        self.crear_overlay_bloqueo()
        self.buscar_citas() 

    def crear_overlay_bloqueo(self):
        self.overlay = ctk.CTkFrame(self.left_card, fg_color=WHITE_CARD, corner_radius=15)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        msg_frame = ctk.CTkFrame(self.overlay, fg_color="transparent")
        msg_frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(msg_frame, text="🔒", font=("Arial", 60)).pack(pady=10)
        ctk.CTkLabel(msg_frame, text="Formulario Bloqueado", font=("Segoe UI", 20, "bold"), text_color=TEXT_DARK).pack()
        ctk.CTkLabel(msg_frame, text="Selecciona una cita del panel derecho\npara comenzar a editar.", font=("Segoe UI", 14), text_color="gray").pack(pady=10)

    def desbloquear_formulario(self):
        self.overlay.place_forget()

    def bloquear_formulario(self):
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    # --- FORMULARIO (Estructura idéntica a Agendar) ---
    def create_form(self):
        parent = self.scroll
        for w in parent.winfo_children(): w.destroy()
        c = ctk.CTkFrame(parent, fg_color="transparent")
        c.pack(fill="x", expand=True, padx=5, pady=2)
        c.grid_columnconfigure((0, 1), weight=1)
        r = 0 

        ctk.CTkLabel(c, text="✏️ Modificar Cita", font=("Segoe UI", 22, "bold"), text_color=ACCENT_BLUE).grid(row=r, column=0, columnspan=2, sticky="w", pady=(0, 10)); r+=1

        self._title(c, "INFORMACIÓN PERSONAL", r); r+=1
        self.ent_nom = ctk.CTkEntry(c, placeholder_text="Nombre Completo", height=35, border_color=BORDER_COLOR, fg_color="#FAFAFA")
        self.ent_nom.grid(row=r, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        frm_mix = ctk.CTkFrame(c, fg_color="transparent", height=35)
        frm_mix.grid(row=r, column=1, sticky="ew", padx=10, pady=(0, 5))
        frm_mix.grid_columnconfigure((0,1), weight=1)
        self.cmb_edad = ctk.CTkOptionMenu(frm_mix, values=["Edad", "0-3", "3-6", "6-12", "12-18", "18-35", "35-60", "60+"], height=35, fg_color="#FAFAFA", text_color=TEXT_DARK, button_color="#CCC")
        self.cmb_edad.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.cmb_gen = ctk.CTkOptionMenu(frm_mix, values=["Género", "Femenino", "Masculino"], height=35, fg_color="#FAFAFA", text_color=TEXT_DARK, button_color="#CCC")
        self.cmb_gen.pack(side="left", fill="x", expand=True, padx=(5,0))
        r+=1 

        self._sep(c, r); r+=1

        self._title(c, "ESPECIALISTA Y ANTECEDENTES", r); r+=1
        docs = ["Selecciona Doctora"] + self.controller.obtener_lista_nombres_doctoras()
        self.cmb_doc = ctk.CTkOptionMenu(c, values=docs, command=self.al_cambiar_doc, fg_color="#FAFAFA", text_color=TEXT_DARK, button_color="#CCC")
        self.cmb_doc.grid(row=r, column=0, sticky="ew", padx=(10, 5), pady=2)
        
        frm_prev = ctk.CTkFrame(c, fg_color="transparent")
        frm_prev.grid(row=r, column=1, sticky="ew", padx=(5, 10))
        self.cmb_prev = ctk.CTkOptionMenu(frm_prev, values=["Tratamiento previo: No", "Tratamiento previo: Sí"], command=self.toggle_prev, fg_color="#FAFAFA", text_color=TEXT_DARK, button_color="#CCC")
        self.cmb_prev.pack(side="left", fill="x", expand=True)
        self.ent_prev = ctk.CTkEntry(frm_prev, placeholder_text="¿Cuál?", width=80, fg_color="#FAFAFA", border_color="#CCC")
        r+=1

        self._sep(c, r); r+=1

        # --- FECHA Y DURACIÓN (DIVIDIDO) ---
        self._title(c, "FECHA Y DURACIÓN", r); r+=1
        frm_dt = ctk.CTkFrame(c, fg_color="transparent")
        frm_dt.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10)
        frm_dt.grid_columnconfigure(0, weight=0); frm_dt.grid_columnconfigure(1, weight=1)
        
        self.cal_frame = ctk.CTkFrame(frm_dt, fg_color="white", border_color="#DDD", border_width=1)
        self.cal_frame.grid(row=0, column=0, sticky="n", padx=(0, 15), ipady=5)
        self.render_calendar()

        frm_tm = ctk.CTkFrame(frm_dt, fg_color="transparent")
        frm_tm.grid(row=0, column=1, sticky="nsew")
        
        # 1. Selector Hora
        ctk.CTkLabel(frm_tm, text="1. Hora de Inicio", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0,2))
        
        frm_reloj = ctk.CTkFrame(frm_tm, fg_color="transparent")
        frm_reloj.pack(fill="x", pady=(0, 10))
        self.cmb_h = ctk.CTkOptionMenu(frm_reloj, values=["--"], width=95, command=self.al_seleccionar_hora_h, fg_color="#E8F0FE", text_color="black")
        self.cmb_h.pack(side="left", padx=(0, 5))
        self.cmb_m = ctk.CTkOptionMenu(frm_reloj, values=["--"], width=95, command=self.al_seleccionar_min_m, fg_color="#E8F0FE", text_color="black")
        self.cmb_m.pack(side="left")
        
        # 2. Duración (SLIDER)
        ctk.CTkLabel(frm_tm, text="2. Duración Estimada", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0,2))
        self.lbl_dur_val = ctk.CTkLabel(frm_tm, text="30 min", font=("Arial", 13, "bold"), text_color=ACCENT_BLUE)
        self.lbl_dur_val.pack(anchor="w")
        
        self.slider_dur = ctk.CTkSlider(frm_tm, from_=5, to=300, number_of_steps=59, command=self.actualizar_slider)
        self.slider_dur.set(30)
        self.slider_dur.pack(fill="x", pady=(0, 5))
        
        self.lbl_fin_hora = ctk.CTkLabel(frm_tm, text="Finaliza a las: --:--", font=("Arial", 11), text_color="#555")
        self.lbl_fin_hora.pack(anchor="w", pady=(5,0))
        r+=1

        self._sep(c, r); r+=1

        self._title(c, "DETALLES", r); r+=1
        self.tipo_var = ctk.StringVar(value="Presupuesto")
        self.seg_tipo = ctk.CTkSegmentedButton(c, values=["Presupuesto (Gratuito)", "Tratamiento"], variable=self.tipo_var, command=self.toggle_serv, selected_color=ACCENT_BLUE)
        self.seg_tipo.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5)); r+=1
        
        self.frm_serv = ctk.CTkFrame(c, fg_color="#FAFAFA", border_color="#EEE", border_width=1)
        self.frm_serv.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10)
        self.frm_serv.grid_remove() 
        
        ctk.CTkButton(self.frm_serv, text="+ Agregar Servicio", fg_color="transparent", border_color=ACCENT_BLUE, border_width=1, text_color=ACCENT_BLUE, command=self.abrir_servicios_mod).pack(fill="x", padx=10, pady=5)
        self.lst_serv = ctk.CTkFrame(self.frm_serv, fg_color="transparent")
        self.lst_serv.pack(fill="x", padx=10, pady=5)
        self.lbl_tot = ctk.CTkLabel(self.frm_serv, text="Total: $0.00", font=("Arial", 12, "bold"), text_color=SUCCESS_COLOR)
        self.lbl_tot.pack(anchor="e", padx=10, pady=5)
        r+=1

        # 5. Contacto
        r = self.create_contact(c, r)
        self._sep(c, r); r+=1

        # 6. Notas
        self._title(c, "ADICIONALES", r); r+=1
        self.frm_nota = ctk.CTkFrame(c, fg_color="#FAFAFA", border_color="#CCC", border_width=1, corner_radius=6)
        self.frm_nota.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
        self.frm_nota.grid_columnconfigure(0, weight=1); self.frm_nota.grid_rowconfigure(0, weight=1)
        
        self.txt_nota = ctk.CTkTextbox(self.frm_nota, height=60, fg_color="#FAFAFA", wrap="word", font=("Segoe UI", 12))
        self.txt_nota.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    # --- LÓGICA DE TIEMPO (IDÉNTICA A AGENDAR) ---
    def act_horarios(self):
        doc = self.cmb_doc.get()
        if not self.selected_date or "Selecciona" in doc: return
        raw_slots = self.controller.obtener_horas_inicio_disponibles(self.selected_date, doc)
        self.mapa_horarios = {}
        if not raw_slots:
            self.cmb_h.configure(values=["Lleno"]); self.cmb_h.set("Lleno")
            self.cmb_m.configure(values=["--"]); self.cmb_m.set("--")
            return
        for slot in raw_slots:
            parts = slot.split(":") 
            hora_num = parts[0]
            resto = parts[1].split(" ")
            minu = resto[0]
            ampm = resto[1]
            k = f"{hora_num} {ampm}"
            if k not in self.mapa_horarios: self.mapa_horarios[k] = []
            self.mapa_horarios[k].append(minu)
        horas = list(self.mapa_horarios.keys())
        self.cmb_h.configure(values=horas)
        self.cmb_h.set(horas[0])
        self.al_seleccionar_hora_h(horas[0])

    def al_seleccionar_hora_h(self, hora_sel):
        minutos = self.mapa_horarios.get(hora_sel, ["--"])
        self.cmb_m.configure(values=minutos)
        self.cmb_m.set(minutos[0])
        self.calcular_hora_final()

    def al_seleccionar_min_m(self, m):
        self.calcular_hora_final()

    def actualizar_slider(self, val):
        m = int(val)
        if m < 60: txt = f"{m} min"
        else:
            h = m // 60; mn = m % 60
            txt = f"{h} h {mn:02d} min" if mn > 0 else f"{h} horas"
        self.lbl_dur_val.configure(text=txt)
        self.calcular_hora_final()

    def calcular_hora_final(self):
        h_txt = self.cmb_h.get()
        m_txt = self.cmb_m.get()
        if "Lleno" in h_txt or "--" in m_txt:
            self.lbl_fin_hora.configure(text="Finaliza: --:--")
            return
        try:
            parts = h_txt.split(" ")
            full_str = f"{parts[0]}:{m_txt} {parts[1]}"
            inicio = datetime.strptime(full_str, "%I:%M %p")
            dur = int(self.slider_dur.get())
            fin = inicio + timedelta(minutes=dur)
            self.lbl_fin_hora.configure(text=f"Finaliza: {fin.strftime('%I:%M %p').lstrip('0').replace(' 0',' ')}")
        except: self.lbl_fin_hora.configure(text="Finaliza: --:--")

    # --- DERECHA Y LÓGICA ---
    def create_search_panel(self):
        p = ctk.CTkFrame(self.right_sidebar, fg_color=WHITE_CARD, corner_radius=10, border_color=BORDER_COLOR, border_width=1)
        p.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        ctk.CTkLabel(p, text="🔍 Buscar Paciente", font=("Segoe UI", 13, "bold"), text_color=ACCENT_BLUE).pack(anchor="w", padx=15, pady=(10, 5))
        self.ent_search = ctk.CTkEntry(p, placeholder_text="Nombre o Teléfono...", height=35)
        self.ent_search.pack(fill="x", padx=15, pady=(0, 10))
        self.ent_search.bind("<KeyRelease>", lambda e: self.buscar_citas())

    def create_results_list(self):
        self.list_scroll = ctk.CTkScrollableFrame(self.right_sidebar, fg_color="transparent")
        self.list_scroll.grid(row=1, column=0, sticky="nsew")
        self.list_scroll.grid_columnconfigure(0, weight=1)

    def buscar_citas(self, query=""):
        if not query: query = self.ent_search.get()
        citas = self.controller.buscar_citas(query)
        for w in self.list_scroll.winfo_children(): w.destroy()
        if not citas: ctk.CTkLabel(self.list_scroll, text="No se encontraron citas.", text_color="gray").pack(pady=20); return
        for c in citas: self._crear_tarjeta_cita(c)

    def _crear_tarjeta_cita(self, data):
        est = data['estado_calc']
        col = INFO_COLOR if est == "En curso" else (WARNING_COLOR if est == "Pendiente" else (DANGER_COLOR if est=="Cancelada" else SUCCESS_COLOR))
        card = ctk.CTkFrame(self.list_scroll, fg_color=WHITE_CARD, corner_radius=8, border_color=BORDER_COLOR, border_width=1)
        card.pack(fill="x", pady=5)
        
        def al_hacer_click(event):
            self.resaltar_tarjeta(card)
            self.cargar_cita_en_formulario(data['id'])

        card.bind("<Button-1>", al_hacer_click)
        h = ctk.CTkFrame(card, fg_color="transparent", height=25)
        h.pack(fill="x", padx=10, pady=(10, 0))
        ctk.CTkLabel(h, text=f"● {est}", text_color=col, font=("Segoe UI", 11, "bold")).pack(side="left")
        ctk.CTkLabel(h, text=str(data['hora_inicio'])[:5], font=("Segoe UI", 12, "bold")).pack(side="right")
        b = ctk.CTkFrame(card, fg_color="transparent")
        b.pack(fill="x", padx=10, pady=(5, 10))
        ctk.CTkLabel(b, text=data['nombre_completo'], font=("Segoe UI", 12, "bold"), text_color="#333").pack(anchor="w")
        
        for w in [h, b] + h.winfo_children() + b.winfo_children():
            w.bind("<Button-1>", al_hacer_click)

    def cargar_cita_en_formulario(self, cita_id):
        self.desbloquear_formulario()
        data_full = self.controller.obtener_cita_completa(cita_id)
        if not data_full: return
        cita = data_full['cita']
        self.cita_id_actual = cita['id']
        self.cliente_id_actual = cita['cliente_id_real']
        
        self.ent_nom.delete(0, 'end'); self.ent_nom.insert(0, cita['nombre_completo'])
        self.ent_tel.delete(0, 'end'); self.ent_tel.insert(0, cita['telefono'] or "")
        self.ent_email.delete(0, 'end'); self.ent_email.insert(0, cita['email'] or "")
        
        if cita['rango_edad']: self.cmb_edad.set(cita['rango_edad'])
        if cita['genero']: self.cmb_gen.set("Masculino" if cita['genero']=='m' else "Femenino")
        
        mapa = self.controller.obtener_info_doctoras()
        nom_doc = "Selecciona Doctora"
        for n, d in mapa.items():
            if d['id'] == cita['doctora_id']: nom_doc = n; break
        self.cmb_doc.set(nom_doc)
        
        self.selected_date = datetime.strptime(str(cita['fecha_cita']), "%Y-%m-%d")
        self.display_date = self.selected_date
        self.render_calendar(); self.act_horarios()
        
        # --- CARGAR HORA DIVIDIDA ---
        try:
            t_obj = (datetime.min + cita['hora_inicio']).time() if isinstance(cita['hora_inicio'], timedelta) else cita['hora_inicio']
            h_str_full = t_obj.strftime("%I:%M %p") # "11:05 AM"
            parts = h_str_full.split(":") 
            parts2 = parts[1].split(" ")
            
            h_val = f"{parts[0]} {parts2[1]}" # "11 AM"
            m_val = parts2[0] # "05"
            
            if h_val in self.cmb_h.cget("values"):
                self.cmb_h.set(h_val)
                self.al_seleccionar_hora_h(h_val)
                if m_val in self.cmb_m.cget("values"):
                    self.cmb_m.set(m_val)
            self.calcular_hora_final()
        except: pass
        
        # CARGAR TIPO Y SERVICIOS
        self.servicios_agregados = [] 
        tipo_bd = cita['tipo']
        raw_servicios = data_full.get('servicios', [])
        for s in raw_servicios:
            self.servicios_agregados.append({
                'id': s['id'], 'nombre': s['nombre'], 'unidad': s['unidad'],
                'precio_unitario': float(s['precio_unitario']),
                'cantidad': int(s['cantidad']), 'precio_total': float(s['precio_total'])
            })
            
        if tipo_bd == "Presupuesto":
            self.tipo_var.set("Presupuesto (Gratuito)")
            self.toggle_serv("Presupuesto (Gratuito)")
        else:
            self.tipo_var.set("Tratamiento")
            self.toggle_serv("Tratamiento")
            
        self.actualizar_servicios_mod()
        
        if cita['tratamiento_previo']:
            self.cmb_prev.set("Tratamiento previo: Sí"); self.toggle_prev("Sí")
            self.ent_prev.delete(0, 'end'); self.ent_prev.insert(0, cita['desc_previo'] or "")
        else: self.cmb_prev.set("Tratamiento previo: No"); self.toggle_prev("No")
        
    def guardar_cambios(self):
        if not self.cita_id_actual: return
        gen = {"Masculino": "m", "Femenino": "f"}.get(self.cmb_gen.get(), "f")
        
        # Reconstruir Hora
        h_sel = self.cmb_h.get().split(" ")
        m_sel = self.cmb_m.get()
        hora_str = f"{h_sel[0]}:{m_sel} {h_sel[1]}"
        dur_str = self.lbl_dur_val.cget("text")

        datos = {
            'cliente_id': self.cliente_id_actual, 'nombre': self.ent_nom.get(),
            'telefono': self.ent_tel.get(), 'email': self.ent_email.get(),
            'edad': self.cmb_edad.get(), 'genero': gen, 'doctora': self.cmb_doc.get(),
            'fecha': self.selected_date.strftime("%Y-%m-%d"), 
            'hora_inicio': hora_str, 'duracion': dur_str, 
            'tipo_cita': self.tipo_var.get(),
            'descripcion': self.txt_nota.get("1.0", "end-1c")
        }
        ok, msg = self.controller.actualizar_cita(self.cita_id_actual, datos)
        if ok: messagebox.showinfo("Éxito", msg); self.buscar_citas()
        else: messagebox.showerror("Error", msg)

    def cancelar_cita(self):
        if not self.cita_id_actual: return
        if messagebox.askyesno("Confirmar", "⚠️ ¿CANCELAR CITA?\nEl horario quedará libre."):
            if self.controller.cambiar_estado_cancelada(self.cita_id_actual):
                messagebox.showinfo("Listo", "Cita cancelada."); self.reset_form(); self.buscar_citas()

    def reset_form(self):
        self.bloquear_formulario()
        self.ent_nom.delete(0, 'end'); self.ent_tel.delete(0, 'end'); self.ent_email.delete(0, 'end')
        self.txt_nota.delete("1.0", "end"); self.cita_id_actual = None
        self.tarjeta_seleccionada = None
        self.buscar_citas()

    def create_buttons(self):
        for w in self.bottom_frame.winfo_children(): w.destroy()
        ctk.CTkButton(self.bottom_frame, text="🗑️ Cancelar Cita", font=("Segoe UI", 12, "bold"), fg_color=DANGER_COLOR, hover_color="#B71C1C", width=120, height=50, command=self.cancelar_cita).pack(side="left", padx=(25, 5), pady=10)
        ctk.CTkButton(self.bottom_frame, text="GUARDAR CAMBIOS", font=("Segoe UI", 15, "bold"), fg_color=ACCENT_BLUE, hover_color="#0056b3", height=50, command=self.guardar_cambios).pack(side="left", fill="x", expand=True, padx=(5, 25), pady=10)

    def resaltar_tarjeta(self, widget_frame):
        if self.tarjeta_seleccionada:
            try: self.tarjeta_seleccionada.configure(fg_color=WHITE_CARD, border_color=BORDER_COLOR, border_width=1)
            except: pass
        widget_frame.configure(fg_color="#D9EFFF", border_color=ACCENT_BLUE, border_width=2)
        self.tarjeta_seleccionada = widget_frame

    # --- SERVICIOS ---
    def toggle_serv(self, valor):
        if valor == "Tratamiento": self.frm_serv.grid()
        else: self.frm_serv.grid_remove()

    def actualizar_servicios_mod(self):
        for w in self.lst_serv.winfo_children(): w.destroy()
        tot = 0
        for i, s in enumerate(self.servicios_agregados):
            r = ctk.CTkFrame(self.lst_serv, fg_color="white", corner_radius=6); r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=s['nombre'], font=("Segoe UI", 11, "bold"), width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(r, text=f"${s['precio_total']:,.2f}", font=("Segoe UI", 11, "bold"), text_color=ACCENT_BLUE).pack(side="right", padx=10)
            ctk.CTkButton(r, text="×", width=25, height=20, fg_color="transparent", text_color=DANGER_COLOR, command=lambda x=i: self.del_serv_mod(x)).pack(side="right")
            tot += s['precio_total']
        self.lbl_tot.configure(text=f"Total: ${tot:,.2f}")

    def del_serv_mod(self, i): 
        self.servicios_agregados.pop(i); self.actualizar_servicios_mod()

    def abrir_servicios_mod(self):
        # Mismo código de agendar_view pero adaptado
        try:
            top = ctk.CTkToplevel(self)
            top.title("Catálogo de Tratamientos"); top.geometry("1000x600"); top.lift(); top.focus_force()
            top.transient(self.winfo_toplevel()); top.grab_set() # Fix oculto
            
            filter_frame = ctk.CTkFrame(top, fg_color="transparent"); filter_frame.pack(fill="x", padx=15, pady=10)
            ctk.CTkLabel(filter_frame, text="Categoría:", font=("bold", 11)).pack(side="left")
            cats = ["Todas"] + self.controller.obtener_categorias_unicas()
            combo_cat = ctk.CTkOptionMenu(filter_frame, values=cats, width=180); combo_cat.pack(side="left", padx=5)
            ctk.CTkLabel(filter_frame, text="Subcategoría:", font=("bold", 11)).pack(side="left", padx=10)
            combo_sub = ctk.CTkOptionMenu(filter_frame, values=["Todas"], width=180); combo_sub.pack(side="left", padx=5)
            entry_search = ctk.CTkEntry(filter_frame, placeholder_text="Buscar...", width=200); entry_search.pack(side="left", padx=10)
            ctk.CTkButton(filter_frame, text="🔄", width=40, command=lambda: reset_filtros()).pack(side="left", padx=5)

            header = ctk.CTkFrame(top, fg_color="#E0E0E0", height=30); header.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(header, text="Servicio", width=300, anchor="w", font=("bold", 11)).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Precio", width=100, anchor="e", font=("bold", 11)).pack(side="right", padx=20)

            scroll = ctk.CTkScrollableFrame(top, fg_color="white"); scroll.pack(fill="both", expand=True, padx=15, pady=10)

            def buscar(e=None):
                for w in scroll.winfo_children(): w.destroy()
                res = self.controller.buscar_servicios_filtros(entry_search.get(), combo_cat.get(), combo_sub.get())
                if not res: ctk.CTkLabel(scroll, text="Sin resultados", text_color="gray").pack(pady=20); return
                for s in res:
                    r = ctk.CTkFrame(scroll, fg_color="transparent", height=40); r.pack(fill="x", pady=2)
                    ctk.CTkLabel(r, text=s['nombre'], width=300, anchor="w", font=("bold", 11)).pack(side="left", padx=5)
                    ctk.CTkButton(r, text="+", width=40, fg_color=ACCENT_BLUE, command=lambda x=s: logica_precio(x)).pack(side="right", padx=5)
                    p = float(s['precio_base'])
                    txt = f"${p:,.2f}" if "caso" not in s['tipo_unidad'] else "Cotizar"
                    ctk.CTkLabel(r, text=txt, width=80, anchor="e", text_color="green").pack(side="right", padx=5)

            def logica_precio(s):
                pb = float(s['precio_base']); u = s['tipo_unidad']
                ops = u.split(" o ")
                if len(ops) == 1:
                    if "caso" in u or pb==0: pedir_manual(s, u)
                    else: agregar(s, pb, u)
                    return
                
                t = ctk.CTkToplevel(top); t.geometry("300x300"); t.transient(top)
                ctk.CTkLabel(t, text=f"{s['nombre']}\nOpciones:", font=("bold", 12)).pack(pady=10)
                for op in ops:
                    op = op.strip()
                    if "caso" in op or pb==0: 
                        cmd = lambda x=op: [t.destroy(), self.after(100, lambda: pedir_manual(s, x))]
                        col = "gray"
                    else:
                        cmd = lambda x=op: [agregar(s, pb, x), t.destroy()]
                        col = ACCENT_BLUE
                    ctk.CTkButton(t, text=op.capitalize(), command=cmd, fg_color=col).pack(pady=5)

            def pedir_manual(s, u):
                d = ctk.CTkInputDialog(text=f"Precio {s['nombre']}:", title="Manual")
                v = d.get_input()
                if v and v.isdigit(): agregar(s, float(v), u)

            def agregar(s, p, u):
                self.servicios_agregados.append({'id': s['id'], 'nombre': s['nombre'], 'unidad': u, 'precio_unitario': p, 'cantidad': 1, 'precio_total': p})
                self.actualizar_servicios_mod(); 
                # NO CERRAMOS LA VENTANA PARA SEGUIR AGREGANDO

            def up_sub(c): 
                combo_sub.configure(values=["Todas"]+self.controller.obtener_subcategorias_por_cat(c) if c!="Todas" else ["Todas"]); combo_sub.set("Todas"); buscar()
            def reset_filtros():
                combo_cat.set("Todas"); combo_sub.configure(values=["Todas"]); entry_search.delete(0, 'end'); buscar()

            combo_cat.configure(command=up_sub); combo_sub.configure(command=buscar); entry_search.bind("<Return>", buscar); buscar()
        except Exception as e: messagebox.showerror("Error", str(e))

    # --- HELPERS ---
    def _sep(self, p, r): ctk.CTkFrame(p, height=1, fg_color="#E0E0E0").grid(row=r, column=0, columnspan=2, sticky="ew", pady=(5, 5), padx=10)
    def _title(self, p, t, r): ctk.CTkLabel(p, text=t, font=("Segoe UI", 11, "bold"), text_color="#999").grid(row=r, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 2))
    def create_contact(self, p, r):
        self._title(p, "CONTACTO Y NOTIFICACIONES", r); r+=1
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5)); r+=1
        f.grid_columnconfigure((0,1), weight=1)
        self.ent_tel = ctk.CTkEntry(f, placeholder_text="Teléfono (WhatsApp) *", fg_color="#FAFAFA", border_color="#CCC")
        self.ent_tel.grid(row=0, column=0, sticky="ew", padx=(0,5))
        self.ent_email = ctk.CTkEntry(f, placeholder_text="Email (Opcional)", fg_color="#FAFAFA", border_color="#CCC")
        self.ent_email.grid(row=0, column=1, sticky="ew", padx=(5,0))
        return r
    def render_calendar(self):
        for w in self.cal_frame.winfo_children(): w.destroy()
        cal = calendar.Calendar(firstweekday=6); md = cal.monthdayscalendar(self.display_date.year, self.display_date.month); hoy = datetime.now()
        h = ctk.CTkFrame(self.cal_frame, fg_color=HEADER_CALENDAR, corner_radius=5); h.pack(fill="x", pady=(0,5))
        ctk.CTkButton(h, text="<", width=25, fg_color="transparent", text_color=ACCENT_BLUE, hover_color="white", command=lambda: self.chg_month(-1)).pack(side="left")
        ctk.CTkLabel(h, text=self.display_date.strftime("%B %Y").capitalize(), font=("Arial", 12, "bold"), text_color="#333").pack(side="left", expand=True)
        ctk.CTkButton(h, text=">", width=25, fg_color="transparent", text_color=ACCENT_BLUE, hover_color="white", command=lambda: self.chg_month(1)).pack(side="right")
        g = ctk.CTkFrame(self.cal_frame, fg_color="transparent"); g.pack(padx=5)
        for i, d in enumerate(["Do","Lu","Ma","Mi","Ju","Vi","Sa"]): ctk.CTkLabel(g, text=d, font=("Arial",9,"bold"), width=30, text_color="#666" if i!=0 else "#888").grid(row=0, column=i)
        for r, w in enumerate(md):
            for c, d in enumerate(w):
                if d == 0: continue
                dt = datetime(self.display_date.year, self.display_date.month, d)
                dom = dt.weekday() == 6; pas = dt.date() < hoy.date(); hoy_dia = dt.date() == hoy.date(); sel = self.selected_date and dt.date() == self.selected_date.date()
                bg = ACCENT_BLUE if sel else ("#F0F0F0" if dom else "white")
                fg = "white" if sel else ("#AAA" if dom else ("#DDD" if pas else "#333"))
                st = "disabled" if (dom or pas) else "normal"
                bc = "black" if hoy_dia else ("#EEE" if not sel else ACCENT_BLUE); bw = 2 if hoy_dia else 1
                ctk.CTkButton(g, text=str(d), width=30, height=28, fg_color=bg, text_color=fg, border_color=bc, border_width=bw, state=st, font=("Arial", 11, "bold" if hoy_dia else "normal"), corner_radius=6, hover_color="#D9EFFF" if st=="normal" else bg, command=lambda x=d: self.sel_day(x)).grid(row=r+1, column=c, padx=2, pady=2)
    def chg_month(self, s):
        m = self.display_date.month + s; y = self.display_date.year
        if m > 12: m=1; y+=1
        elif m < 1: m=12; y-=1
        self.display_date = self.display_date.replace(year=y, month=m, day=1); self.render_calendar()
    def sel_day(self, d): self.selected_date = datetime(self.display_date.year, self.display_date.month, d); self.render_calendar(); self.act_horarios()
    def al_cambiar_doc(self, _): self.act_horarios()
    def toggle_prev(self, v):
        if "Sí" in v: self.ent_prev.pack(side="left", fill="x", padx=(5,0), expand=True)
        else: self.ent_prev.pack_forget()