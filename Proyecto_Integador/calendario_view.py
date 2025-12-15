import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
from tkinter import messagebox 
from calendario_controller import CalendarioController

# --- COLORES Y ESTILOS ---
BG_COLOR = "#F4F6F8"
WHITE_FRAME = "white"
ACCENT_BLUE = "#007BFF"
HEADER_CAL = "#E8F0FE"  
SOFT_ACTIVE_FILTER = "#E3F2FD" 
TEXT_DARK = "#2D3436"
TEXT_LIGHT = "#636E72"
BORDER_COLOR = "#E0E0E0"

# Colores de Estado
STATUS_COLORS = {
    'Pendiente': "#FFC107",
    'En curso': "#17A2B8",
    'Completada': "#28A745",
    'Cancelada': "#DC3545"
}

# Orden fijo para las métricas
METRICS_ORDER = ['Pendiente', 'En curso', 'Completada', 'Cancelada']

# Prioridad de ordenamiento en la lista
STATUS_PRIORITY = {
    'En curso': 1,
    'Pendiente': 2,
    'Completada': 3,
    'Cancelada': 4
}

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, master, callback_modificar=None):
        super().__init__(master, fg_color=BG_COLOR)
        self.master = master
        self.callback_modificar = callback_modificar
        self.ctrl = CalendarioController()
        
        self.current_date = datetime.now()
        self.paciente_filtro_id = None
        self.doctora_vars = {}
        self.filter_widgets = {}
        self.bind("<Button-1>", self.release_focus)

        # Scroll General
        scroll_container = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR)
        scroll_container.pack(fill="both", expand=True)
        scroll_container.bind("<Button-1>", self.release_focus)
        
        # Contenedor Central
        main_card = ctk.CTkFrame(scroll_container, fg_color=BG_COLOR)
        main_card.pack(fill="x", expand=False, padx=20, pady=10) 
        main_card.grid_columnconfigure(0, weight=1)
        main_card.bind("<Button-1>", self.release_focus)

        # 1. Filtros
        self.create_filter_panel(main_card, row=0)
        
        # 2. Paneles (Calendario y Resumen)
        self.create_main_panels(main_card, row=1)
        
        # Separador visual
        sep = ctk.CTkFrame(main_card, height=2, fg_color="#E0E0E0")
        sep.grid(row=2, column=0, sticky="ew", pady=15)
        
        # 3. Lista de Citas
        self.create_daily_appointments_panel(main_card, row=3)
        
        self.load_daily_schedule() 

    def release_focus(self, event):
        """Función para quitar el foco del buscador al dar clic afuera"""
        self.focus()

    # --- PANEL DE FILTROS ---
    def create_filter_panel(self, parent, row):
        filter_frame = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=15, border_color="#E5E5E5", border_width=1)
        filter_frame.grid(row=row, column=0, sticky="ew", pady=(0, 15)) 
        filter_frame.bind("<Button-1>", self.release_focus)
        
        inner = ctk.CTkFrame(filter_frame, fg_color="transparent")
        inner.pack(padx=15, pady=15, fill="x")

        # Buscador
        search_bar = ctk.CTkFrame(inner, fg_color="#F1F3F4", corner_radius=20)
        search_bar.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(search_bar, text="🔍", font=ctk.CTkFont(size=14)).pack(side="left", padx=(15, 5), pady=8)
        self.ent_search = ctk.CTkEntry(search_bar, width=250, placeholder_text="Buscar paciente...", border_width=0, fg_color="transparent", text_color=TEXT_DARK)
        self.ent_search.pack(side="left", fill="x", expand=True)
        self.ent_search.bind("<Return>", self.buscar_pacientes)
        
        ctk.CTkButton(search_bar, text="Buscar", width=60, fg_color=ACCENT_BLUE, corner_radius=15, command=self.buscar_pacientes).pack(side="left", padx=5)
        ctk.CTkButton(search_bar, text="✕", width=30, fg_color="transparent", text_color="#999", hover_color="#EEE", command=self.limpiar_paciente).pack(side="left", padx=(0,10))

        self.results_frame = ctk.CTkScrollableFrame(inner, height=0, fg_color="white")
        
        # Checkbox Doctoras
        ctk.CTkLabel(inner, text="Filtrar por Doctora:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_LIGHT).pack(anchor="w", pady=(10,5))
        grid_container = ctk.CTkFrame(inner, fg_color="transparent")
        grid_container.pack(fill="x")
        grid_container.grid_columnconfigure((0, 1), weight=1)

        docs_db = self.ctrl.obtener_doctoras_activas()
        for i, doc in enumerate(docs_db):
            self.doctora_vars[doc['id']] = ctk.StringVar(value="on") 
            self._create_doctora_checkbox(grid_container, doc, (i // 2), (i % 2))

    def _create_doctora_checkbox(self, parent, doc_data, row, col):
        doc_id = doc_data['id']
        nombre = doc_data['nombre']
        var = self.doctora_vars[doc_id]

        wrapper = ctk.CTkFrame(parent, fg_color=SOFT_ACTIVE_FILTER, corner_radius=8, border_color="#ADD8E6", border_width=1, cursor="hand2")
        wrapper.grid(row=row, column=col, sticky="ew", padx=5, pady=4) 
        wrapper.grid_columnconfigure(0, weight=1) 
        
        cmd = lambda e, d=doc_id: self.toggle_filter_click(d)
        wrapper.bind("<Button-1>", cmd)
        
        lbl = ctk.CTkLabel(wrapper, text=nombre, font=ctk.CTkFont(size=12), text_color=TEXT_DARK, anchor="w", cursor="hand2")
        lbl.grid(row=0, column=0, sticky="ew", padx=(10, 0), pady=8)
        lbl.bind("<Button-1>", cmd)
        
        chk = ctk.CTkCheckBox(wrapper, text="", variable=var, onvalue="on", offvalue="off", command=lambda d=doc_id: self.toggle_filter_click(d, from_check=True), fg_color=ACCENT_BLUE, width=18, height=18)
        chk.grid(row=0, column=1, sticky="e", padx=10)
        self.filter_widgets[doc_id] = {'frame': wrapper, 'check': chk}

    def toggle_filter_click(self, doc_id, from_check=False):
        var = self.doctora_vars[doc_id]
        if not from_check: var.set("off" if var.get() == "on" else "on")
        w = self.filter_widgets[doc_id]['frame']
        if var.get() == "on": w.configure(fg_color=SOFT_ACTIVE_FILTER, border_color="#ADD8E6")
        else: w.configure(fg_color="white", border_color="#E0E0E0")
        self.load_daily_schedule()

    # --- PANELES CENTRALES ---
    def create_main_panels(self, parent, row):
        panels = ctk.CTkFrame(parent, fg_color="transparent")
        panels.grid(row=row, column=0, sticky="nsew")
        panels.grid_columnconfigure(0, weight=3)
        panels.grid_columnconfigure(1, weight=2)
        
        # Calendario
        cal_frame = ctk.CTkFrame(panels, fg_color=WHITE_FRAME, corner_radius=15, border_color="#E5E5E5", border_width=1)
        cal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        cal_frame.bind("<Button-1>", self.release_focus)
        
        ctk.CTkLabel(cal_frame, text="📅 Calendario", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_DARK).pack(anchor="w", padx=20, pady=(15,5))
        
        self.calendar_container = ctk.CTkFrame(cal_frame, fg_color="white") 
        self.calendar_container.pack(padx=10, pady=5, fill="both", expand=True)
        self._create_mini_calendar() 

        # Resumen
        self.summary_card = ctk.CTkFrame(panels, fg_color=WHITE_FRAME, corner_radius=15, border_color="#E5E5E5", border_width=1)
        self.summary_card.grid(row=0, column=1, sticky="nsew")
        self.summary_card.bind("<Button-1>", self.release_focus)
        
        ctk.CTkLabel(self.summary_card, text="📊 Resumen del Día", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_DARK).pack(anchor="w", padx=20, pady=15)
        self.summary_list_frame = ctk.CTkFrame(self.summary_card, fg_color="transparent")
        self.summary_list_frame.pack(fill="both", expand=True, padx=15)

    # --- CALENDARIO AJUSTADO Y CON LEYENDA ---
    def _create_mini_calendar(self):
        for widget in self.calendar_container.winfo_children(): widget.destroy()
        
        center_box = ctk.CTkFrame(self.calendar_container, fg_color="white")
        center_box.pack(pady=5)

        # 1. Cabecera COMPACTA (Dentro del center_box)
        header = ctk.CTkFrame(center_box, fg_color=HEADER_CAL, height=30)
        header.pack(fill="x", pady=(0, 5))
        
        ctk.CTkButton(header, text="<", width=25, height=25, fg_color="transparent", text_color=ACCENT_BLUE, 
                      hover_color="#D9EFFF", font=("Arial", 12, "bold"),
                      command=lambda: self.update_schedule(months=-1)).pack(side="left", padx=2)
        
        ctk.CTkLabel(header, text=self.current_date.strftime("%B %Y").upper(), 
                     font=ctk.CTkFont(size=12, weight="bold"), text_color="#333").pack(side="left", expand=True, padx=5)
        
        ctk.CTkButton(header, text=">", width=25, height=25, fg_color="transparent", text_color=ACCENT_BLUE, 
                      hover_color="#D9EFFF", font=("Arial", 12, "bold"),
                      command=lambda: self.update_schedule(months=1)).pack(side="right", padx=2)

        # 2. Grid de días
        grid = ctk.CTkFrame(center_box, fg_color="white")
        grid.pack()
        
        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(self.current_date.year, self.current_date.month)
        
        ids_sel = [id for id, var in self.doctora_vars.items() if var.get() == "on"]
        bold_days, blue_days = self.ctrl.obtener_estilos_dias(self.current_date.year, self.current_date.month, self.paciente_filtro_id, ids_sel)
        
        # Headers dias
        dias_h = ["D", "L", "M", "M", "J", "V", "S"]
        for i, d in enumerate(dias_h):
            col_h = "#DC3545" if i == 0 else "#999"
            ctk.CTkLabel(grid, text=d, text_color=col_h, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=i, padx=2, pady=(0,2))

        # Días
        today = datetime.now()
        for r, week in enumerate(month_days):
            for c, day in enumerate(week):
                if day == 0: continue
                
                sel = (day == self.current_date.day)
                is_bold = (day in bold_days)
                is_blue = (day in blue_days) 
                
                # Colores
                bg = ACCENT_BLUE if sel else ("#E1F5FE" if is_blue else "white")
                
                # Texto
                dia_dt = datetime(self.current_date.year, self.current_date.month, day)
                es_domingo = (dia_dt.weekday() == 6)
                
                if sel: fg = "white"
                elif is_blue: fg = ACCENT_BLUE
                elif es_domingo: fg = "#DC3545" # Domingo Rojo
                else: fg = TEXT_DARK
                
                font_w = "bold" if (is_bold or sel) else "normal"
                
                border_c = ACCENT_BLUE if (day == today.day and self.current_date.month == today.month) else "white"
                border_w = 1 if (day == today.day and self.current_date.month == today.month) else 0

                btn = ctk.CTkButton(grid, text=str(day), width=28, height=26, 
                                    fg_color=bg, text_color=fg, 
                                    border_color=border_c, border_width=border_w,
                                    font=ctk.CTkFont(size=11, weight=font_w),
                                    hover_color="#D9EFFF" if not sel else "#0056b3",
                                    command=lambda d=day: self.select_day(d))
                btn.grid(row=r+1, column=c, padx=2, pady=2)
        
        # 3. LEYENDA (FEEDBACK VISUAL)
        legend_frame = ctk.CTkFrame(center_box, fg_color="transparent")
        legend_frame.pack(pady=(10, 0))
        
        l1 = ctk.CTkLabel(legend_frame, text="Negrita: ", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_DARK)
        l1.pack(side="left")
        ctk.CTkLabel(legend_frame, text="Cita Dras  ", font=ctk.CTkFont(size=10), text_color="#666").pack(side="left")
        
        l2 = ctk.CTkLabel(legend_frame, text="■ ", font=ctk.CTkFont(size=10), text_color="#E1F5FE") # Cuadrito simulado
        l2.pack(side="left")
        ctk.CTkLabel(legend_frame, text="Azul: ", font=ctk.CTkFont(size=10, weight="bold"), text_color=ACCENT_BLUE).pack(side="left")
        ctk.CTkLabel(legend_frame, text="Cita Paciente", font=ctk.CTkFont(size=10), text_color="#666").pack(side="left")


    # --- LISTA DE CITAS (CON ORDENAMIENTO Y ESTÉTICA) ---
    def create_daily_appointments_panel(self, parent, row):
        self.daily_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.daily_container.grid(row=row, column=0, sticky="nsew")
        self.daily_container.grid_columnconfigure(0, weight=1)
        self.daily_container.bind("<Button-1>", self.release_focus)

        self.lbl_daily_header = ctk.CTkLabel(self.daily_container, text="", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_DARK, anchor="w")
        self.lbl_daily_header.pack(fill="x", padx=0, pady=(0, 10))

        self.appointments_scroll = ctk.CTkScrollableFrame(self.daily_container, fg_color="transparent", height=400)
        self.appointments_scroll.pack(fill="both", expand=True)
        self.appointments_scroll.grid_columnconfigure(0, weight=1)
        self.appointments_scroll.bind("<Button-1>", self.release_focus)

    def load_daily_schedule(self, *args):
        ids_sel = [id for id, var in self.doctora_vars.items() if var.get() == "on"]
        citas = self.ctrl.obtener_citas_dia(self.current_date, ids_sel)
        
        # ORDENAR CITAS
        citas.sort(key=lambda x: STATUS_PRIORITY.get(x.get('estado', 'Pendiente'), 99))
        
        self._update_metrics(citas)
        self._create_mini_calendar() 
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        fecha_txt = f"{self.current_date.day} de {meses[self.current_date.month-1]}"
        self.lbl_daily_header.configure(text=f"Citas del {fecha_txt} ({len(citas)})")
        
        for w in self.appointments_scroll.winfo_children(): w.destroy()

        if not citas:
            ctk.CTkLabel(self.appointments_scroll, text="No hay citas programadas.", text_color="gray", font=ctk.CTkFont(size=14)).pack(pady=40)
            return

        for cita in citas:
            self._crear_tarjeta_cita(cita)

    def _crear_tarjeta_cita(self, data):
        est = data.get('estado', 'Pendiente')
        col = STATUS_COLORS.get(est, "#999")
        cita_id = data['id']
        
        card = ctk.CTkFrame(self.appointments_scroll, fg_color=WHITE_FRAME, 
                            corner_radius=12, border_color=col, border_width=2, cursor="hand2")
        card.pack(fill="x", pady=6, padx=5)
        
        cmd = lambda e: self.abrir_modificar_cita(cita_id)
        card.bind("<Button-1>", cmd)

        # 1. HORA (AM/PM)
        try:
            raw_h = data['hora_inicio']
            if isinstance(raw_h, timedelta): 
                t_obj = (datetime.min + raw_h).time()
            else:
                t_obj = datetime.strptime(str(raw_h), "%H:%M:%S").time()
            
            h_str = t_obj.strftime("%I:%M %p").lstrip("0") 
        except: 
            h_str = str(data['hora_inicio'])[:5]

        f_h = ctk.CTkFrame(card, fg_color="transparent")
        f_h.pack(side="left", padx=15, pady=10)
        
        lbl_h = ctk.CTkLabel(f_h, text=h_str, font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_DARK)
        lbl_h.pack(anchor="w")

        # DURACIÓN FORMATEADA
        dur = data.get('duracion_minutos', 30)
        if dur < 60:
            dur_txt = f"{dur} min"
        else:
            horas = dur // 60
            mins = dur % 60
            if mins == 0: dur_txt = f"{horas} hr"
            else: dur_txt = f"{horas} hr {mins} min"

        ctk.CTkLabel(f_h, text=dur_txt, font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")
        
        for w in f_h.winfo_children(): w.bind("<Button-1>", cmd); f_h.bind("<Button-1>", cmd)

        # Divisor
        ctk.CTkFrame(card, width=2, height=40, fg_color="#F0F0F0").pack(side="left", padx=(0,10))

        # 2. Info Paciente
        f_i = ctk.CTkFrame(card, fg_color="transparent")
        f_i.pack(side="left", fill="both", expand=True, pady=8)
        
        nom = data['paciente_nombre_completo']
        if self.paciente_filtro_id and data.get('cliente_id') == self.paciente_filtro_id: nom = "★ " + nom
        
        lbl_n = ctk.CTkLabel(f_i, text=nom, font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_DARK, anchor="w")
        lbl_n.pack(fill="x")
        
        doc_nom = f"Dra. {data['doctora_nombre_completo']}"
        lbl_s = ctk.CTkLabel(f_i, text=doc_nom, font=ctk.CTkFont(size=12), text_color=ACCENT_BLUE, anchor="w")
        lbl_s.pack(fill="x")
        
        for w in f_i.winfo_children(): w.bind("<Button-1>", cmd); f_i.bind("<Button-1>", cmd)

        # 3. Badge Estado
        f_act = ctk.CTkFrame(card, fg_color="transparent")
        f_act.pack(side="right", padx=15)
        
        badge = ctk.CTkLabel(f_act, text=est.upper(), font=ctk.CTkFont(size=10, weight="bold"), 
                             text_color="white", fg_color=col, corner_radius=10, width=90)
        badge.pack(pady=(0,5))
        badge.bind("<Button-1>", cmd)
        
        btn = ctk.CTkLabel(f_act, text="Editar >", font=ctk.CTkFont(size=11), text_color="#999")
        btn.pack()
        btn.bind("<Button-1>", cmd)
        f_act.bind("<Button-1>", cmd)

    def _update_metrics(self, citas):
        total = len(citas)
        stats = {'Pendiente':0,'En curso':0, 'Confirmada':0, 'Cancelada':0}
        for c in citas: stats[c.get('estado', 'Pendiente')] = stats.get(c.get('estado', 'Pendiente'), 0) + 1
        
        for w in self.summary_list_frame.winfo_children(): w.destroy()
        
        # Fila Total
        row = ctk.CTkFrame(self.summary_list_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)
        ctk.CTkLabel(row, text="Total Citas", text_color=TEXT_DARK, font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkLabel(row, text=str(total), text_color=ACCENT_BLUE, font=ctk.CTkFont(weight="bold")).pack(side="right")
        
        # Filas Estados
        for k in METRICS_ORDER:
            v = stats.get(k, 0)
            col = STATUS_COLORS.get(k, "#333")
            
            txt_col_val = "#333" if v > 0 else "#CCC"
            txt_col_lbl = "#666" if v > 0 else "#CCC"
            dot_col = col if v > 0 else "#E0E0E0"

            r = ctk.CTkFrame(self.summary_list_frame, fg_color="transparent")
            r.pack(fill="x", pady=1)
            
            ctk.CTkLabel(r, text="●", text_color=dot_col, font=ctk.CTkFont(size=14)).pack(side="left", padx=(0,5))
            ctk.CTkLabel(r, text=k, text_color=txt_col_lbl, font=ctk.CTkFont(size=12)).pack(side="left")
            ctk.CTkLabel(r, text=str(v), text_color=txt_col_val, font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")

    # --- UTILIDADES ---
    def buscar_pacientes(self, event=None):
        txt = self.ent_search.get().strip()
        if not txt: return
        for w in self.results_frame.winfo_children(): w.destroy()
        res = self.ctrl.buscar_pacientes_lista(txt)
        if res:
            self.results_frame.pack(fill="x", pady=(0, 10))
            self.results_frame.configure(height=min(len(res)*40, 150))
            for p in res:
                btn = ctk.CTkButton(self.results_frame, text=f"👤 {p['nombre_completo']} | {p['telefono']}", anchor="w", fg_color="transparent", text_color=TEXT_DARK, hover_color="#EEE", command=lambda i=p['id'], n=p['nombre_completo']: self.sel_paciente(i, n))
                btn.pack(fill="x")
        else:
            self.results_frame.pack_forget()

    def sel_paciente(self, pid, nombre):
        self.paciente_filtro_id = pid
        self.ent_search.delete(0, 'end'); self.ent_search.insert(0, nombre)
        self.results_frame.pack_forget()
        self.load_daily_schedule()
        self.focus()

    def limpiar_paciente(self):
        self.paciente_filtro_id = None
        self.ent_search.delete(0, 'end')
        self.results_frame.pack_forget()
        self.load_daily_schedule()
        self.focus()

    def select_day(self, d):
        self.current_date = self.current_date.replace(day=d)
        self.load_daily_schedule()

    def update_schedule(self, months=0):
        m = self.current_date.month + months
        y = self.current_date.year
        if m>12: m=1; y+=1
        elif m<1: m=12; y-=1
        try: self.current_date = self.current_date.replace(year=y, month=m)
        except: self.current_date = self.current_date.replace(year=y, month=m, day=1)
        self.load_daily_schedule()

    def abrir_modificar_cita(self, cita_id):
        if self.callback_modificar: self.callback_modificar(cita_id)
        else: messagebox.showinfo("Info", f"Cita ID: {cita_id}")
