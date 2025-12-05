import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
from typing import Dict
from calendario_controller import CalendarioController

# --- CONFIGURACIÓN ESTÉTICA ---
BG_COLOR = "#F0F8FF"
WHITE_FRAME = "white"
ACCENT_BLUE = "#007BFF"
SOFT_BLUE_FRAME = "#D9EFFF"
VISIBLE_BORDER = "#C8CDD6"
HEADER_CALENDAR = "#E8F0FE" # Color nuevo del header

# Colores Estados
SUCCESS_COLOR = "#28A745"
WARNING_COLOR = "#FFC107"
DANGER_COLOR = "#DC3545"
INFO_COLOR = "#17A2B8"

DOCTORAS_DATA = [
    "Dra. Raquel Guzmán Reyes (Especialista en Ortodoncia)",
    "Dra. Paola Jazmin Vera Guzmán (Especialista en Endodoncia)",
    "Dra. María Fernanda Cabrera Guzmán (Cirujana Dentista)"
]

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_COLOR)
        self.master = master
        self.current_date = datetime.now()
        self.controller = CalendarioController()

        # Layout Principal (Estructura Original)
        scroll_container = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR)
        scroll_container.pack(fill="both", expand=True)

        main_card = ctk.CTkFrame(scroll_container, fg_color=WHITE_FRAME, corner_radius=15, border_color=VISIBLE_BORDER, border_width=1)
        main_card.pack(fill="x", expand=False, padx=20, pady=10) 
        main_card.grid_columnconfigure(0, weight=1)

        main_content = ctk.CTkFrame(main_card, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=10) 

        main_content.grid_rowconfigure(0, weight=0)
        main_content.grid_rowconfigure(1, weight=1) 
        main_content.grid_rowconfigure(2, weight=0) 
        main_content.grid_columnconfigure(0, weight=1)

        # 1. Filtros
        self.create_filter_panel(main_content, row=0)
        # 2. Paneles Centrales (Calendario + Resumen)
        self.create_main_panels(main_content, row=1)
        # 3. Lista Abajo
        self.create_daily_appointments_panel(main_content, row=2)
        
        self.load_daily_schedule() 

    def create_filter_panel(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=10, border_color=VISIBLE_BORDER, border_width=1)
        f.grid(row=row, column=0, sticky="ew", pady=(0, 15)) 
        f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(f, text="Filtrar por Doctora", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333").grid(row=0, column=0, padx=15, pady=10)
        
        check_frame = ctk.CTkFrame(f, fg_color="transparent")
        check_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.doctora_vars = {}
        for i, doc in enumerate(DOCTORAS_DATA):
            self.doctora_vars[doc] = ctk.StringVar(value="on")
            # Diseño checkbox original
            # El contenedor 'w' tiene bordes redondeados (corner_radius=15)
            w = ctk.CTkFrame(check_frame, fg_color=SOFT_BLUE_FRAME, corner_radius=15, border_color=ACCENT_BLUE, border_width=1)
            w.pack(side="left", padx=5, fill="x", expand=True)
            
            # Agregamos 'pady=5' al Label y al CheckBox para que no toquen el borde superior/inferior
            ctk.CTkLabel(w, text=doc.split("(")[0], font=ctk.CTkFont(size=11), text_color=ACCENT_BLUE).pack(side="left", padx=10, pady=5)
            
            ctk.CTkCheckBox(w, text="", variable=self.doctora_vars[doc], command=self.load_daily_schedule, onvalue="on", offvalue="off", width=15, height=15).pack(side="right", padx=10, pady=5)
            
    def create_main_panels(self, parent, row):
        p = ctk.CTkFrame(parent, fg_color="transparent")
        p.grid(row=row, column=0, sticky="nsew", pady=(0, 15))
        p.grid_columnconfigure(0, weight=1) 
        p.grid_columnconfigure(1, weight=1) 
        
        self.create_date_picker_panel(p, column=0)
        self.create_summary_panel(p, column=1)

    def create_date_picker_panel(self, parent, column):
        p = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=10, border_color=VISIBLE_BORDER, border_width=1)
        p.grid(row=0, column=column, sticky="nsew", padx=(0, 15))
        
        ctk.CTkLabel(p, text=" 📅 Calendario", font=ctk.CTkFont(size=15, weight="bold"), text_color="#333", anchor="w").pack(fill="x", padx=15, pady=(15, 5))
        
        self.calendar_container = ctk.CTkFrame(p, fg_color="transparent")
        self.calendar_container.pack(padx=10, pady=5, fill="both", expand=True)
        
        self._create_mini_calendar() 

        l = ctk.CTkFrame(p, fg_color=SOFT_BLUE_FRAME, corner_radius=10)
        l.pack(fill="x", padx=15, pady=(10, 15))
        ctk.CTkLabel(l, text="Días en negrita tienen citas.", font=ctk.CTkFont(size=12), text_color="#333").pack(padx=10, pady=5)

    def _create_mini_calendar(self):
        for w in self.calendar_container.winfo_children(): w.destroy()

        cal = calendar.Calendar(firstweekday=6) # 6 = Domingo
        md = cal.monthdayscalendar(self.current_date.year, self.current_date.month)
        hoy = datetime.now()
        
        # --- HEADER ---
        h = ctk.CTkFrame(self.calendar_container, fg_color=HEADER_CALENDAR, corner_radius=5)
        h.pack(fill="x", pady=(0, 5))
        ctk.CTkButton(h, text="<", width=25, fg_color="transparent", text_color=ACCENT_BLUE, hover_color="white", command=lambda: self.update_schedule(months=-1)).pack(side="left")
        ctk.CTkLabel(h, text=self.current_date.strftime("%B %Y").capitalize(), font=("Arial", 12, "bold"), text_color="#333").pack(side="left", expand=True)
        ctk.CTkButton(h, text=">", width=25, fg_color="transparent", text_color=ACCENT_BLUE, hover_color="white", command=lambda: self.update_schedule(months=1)).pack(side="right")
        
        # --- GRID DÍAS ---
        g = ctk.CTkFrame(self.calendar_container, fg_color="transparent")
        g.pack(padx=5)
        
        # Cabeceras (Do, Lu, Ma...)
        dias_sem = ["Do","Lu","Ma","Mi","Ju","Vi","Sa"]
        for i, d in enumerate(dias_sem): 
            # Domingo en Rojo o Gris oscuro para destacar
            col = "#888" if i == 0 else "#666"
            ctk.CTkLabel(g, text=d, font=("Arial", 9, "bold"), width=35, text_color=col).grid(row=0, column=i)
        
        dias_con_citas = self.controller.obtener_dias_ocupados(self.current_date.year, self.current_date.month)

        for r, week in enumerate(md):
            for c, d in enumerate(week):
                if d == 0: continue
                
                dt = datetime(self.current_date.year, self.current_date.month, d)
                es_domingo = dt.weekday() == 6 # 6 es Domingo en Python datetime (Lunes=0)
                
                es_hoy = dt.date() == hoy.date()
                es_sel = dt.date() == self.current_date.date()
                tiene_cita = d in dias_con_citas
                
                # --- ESTILOS VISUALES ---
                
                # 1. Color de Fondo y Texto
                if es_sel:
                    bg = ACCENT_BLUE
                    fg = "white"
                elif es_domingo:
                    bg = "#F0F0F0" # Gris claro para fondo domingo
                    fg = "#AAA"    # Texto gris apagado
                else:
                    bg = "white"
                    fg = "#333"

                # 2. Bordes
                if es_hoy:
                    bc = "black"
                    bw = 2
                elif es_sel:
                    bc = ACCENT_BLUE
                    bw = 1
                else:
                    bc = "#EEE"
                    bw = 1
                
                # 3. Fuente (Negrita SOLO si tiene cita, NO por ser hoy)
                font_weight = "bold" if tiene_cita else "normal"

                # Estado del botón (Domingo deshabilitado o visualmente gris)
                state = "disabled" if es_domingo else "normal"
                if es_domingo: hover = "#F0F0F0" # No cambia al pasar mouse
                else: hover = "#D9EFFF"

                btn = ctk.CTkButton(
                    g, text=str(d), width=35, height=30, 
                    fg_color=bg, text_color=fg, 
                    border_color=bc, border_width=bw,
                    font=("Arial", 11, font_weight), 
                    corner_radius=6, 
                    state=state,
                    hover_color=hover, 
                    command=lambda x=d: self.select_day(x)
                )
                btn.grid(row=r+1, column=c, padx=2, pady=2)

    def create_summary_panel(self, parent, column):
        p = ctk.CTkFrame(parent, fg_color=SOFT_BLUE_FRAME, corner_radius=10, border_color=VISIBLE_BORDER, border_width=1)
        p.grid(row=0, column=column, sticky="nsew", padx=(15, 0))
        
        ctk.CTkLabel(p, text=" 👤 Resumen del Día", font=ctk.CTkFont(size=15, weight="bold"), text_color=ACCENT_BLUE, anchor="w").pack(fill="x", padx=15, pady=(15, 10))
        self.summary_list_frame = ctk.CTkFrame(p, fg_color="transparent")
        self.summary_list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def update_summary(self, data=None):
        if data is None: data = self.controller.obtener_citas_del_dia(self.current_date, self.doctora_vars)
        for w in self.summary_list_frame.winfo_children(): w.destroy()
        
        tot = sum(len(v) for v in data.values())
        items = [("Total", tot, None), ("Pendientes", len(data['Pendientes']), WARNING_COLOR),
                 ("En curso", len(data['En curso']), INFO_COLOR), ("Completadas", len(data['Completadas']), SUCCESS_COLOR),
                 ("Canceladas", len(data['Canceladas']), DANGER_COLOR)]
        
        for l, v, c in items:
            f = ctk.CTkFrame(self.summary_list_frame, fg_color="transparent")
            f.pack(fill="x", pady=5)
            if c: ctk.CTkLabel(f, text="●", text_color=c, font=("Arial", 14, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(f, text=l, font=("Segoe UI", 12), text_color="#333").pack(side="left")
            ctk.CTkLabel(f, text=str(v), font=("Segoe UI", 12, "bold"), text_color="#333").pack(side="right")

    def create_daily_appointments_panel(self, parent, row):
        p = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=10, border_color=VISIBLE_BORDER, border_width=1)
        p.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        
        self.daily_header = ctk.CTkLabel(p, text="", font=ctk.CTkFont(size=15, weight="bold"), text_color="#333", anchor="w")
        self.daily_header.pack(fill="x", padx=15, pady=(15, 10))
        
        self.apps_scroll = ctk.CTkFrame(p, fg_color="transparent")
        self.apps_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def load_daily_schedule(self):
        data = self.controller.obtener_citas_del_dia(self.current_date, self.doctora_vars)
        self.update_summary(data)
        
        txt_fecha = self.current_date.strftime('%A, %d de %B').capitalize()
        self.daily_header.configure(text=f"🗓️ {txt_fecha}")
        
        for w in self.apps_scroll.winfo_children(): w.destroy()
        
        for st, apps in data.items():
            if not apps: continue
            ctk.CTkLabel(self.apps_scroll, text=st, font=("Segoe UI", 12, "bold"), text_color="#666").pack(anchor="w", pady=(10, 5))
            for a in apps: self._add_appointment_item(a, st)

    def _add_appointment_item(self, app, status):
        col = INFO_COLOR if status=="En curso" else (SUCCESS_COLOR if status=="Completadas" else (DANGER_COLOR if status=="Canceladas" else WARNING_COLOR))
        
        card = ctk.CTkFrame(self.apps_scroll, fg_color=WHITE_FRAME, corner_radius=10, border_color=col, border_width=1)
        card.pack(fill="x", pady=5)
        
        # Grid interno
        card.grid_columnconfigure(1, weight=1)
        
        # Hora
        tf = ctk.CTkFrame(card, fg_color="transparent")
        tf.grid(row=0, column=0, sticky="nw", padx=15, pady=15)
        ctk.CTkLabel(tf, text="🕒", font=("Arial", 18)).pack(side="left")
        ctk.CTkLabel(tf, text=app['hora'], font=("Segoe UI", 14, "bold"), text_color=ACCENT_BLUE).pack(side="left", padx=5)
        
        # Info
        inf = ctk.CTkFrame(card, fg_color="transparent")
        inf.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        
        # Etiqueta Estado
        ctk.CTkLabel(inf, text=status[:-1] if status.endswith('s') else status, fg_color=col, text_color="white", corner_radius=6, font=("Arial", 10, "bold")).pack(anchor="e")
        
        ctk.CTkLabel(inf, text=f"👤 {app['paciente']}", font=("Segoe UI", 14, "bold"), text_color="#333").pack(anchor="w")
        ctk.CTkLabel(inf, text=app['tratamiento'], font=("Segoe UI", 13), text_color="#666").pack(anchor="w")
        ctk.CTkLabel(inf, text=f"Dra. {app['doctora']}", font=("Segoe UI", 12, "bold"), text_color=ACCENT_BLUE).pack(anchor="w", pady=(5,0))

    def select_day(self, d):
        self.current_date = self.current_date.replace(day=d)
        self._create_mini_calendar(); self.load_daily_schedule()

    def update_schedule(self, months=0):
        nm = self.current_date.month + months; ny = self.current_date.year
        if nm > 12: nm=1; ny+=1
        elif nm < 1: nm=12; ny-=1
        try: self.current_date = self.current_date.replace(year=ny, month=nm)
        except: self.current_date = self.current_date.replace(year=ny, month=nm, day=1)
        self._create_mini_calendar(); self.load_daily_schedule()
