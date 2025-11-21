import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
from tkinter import messagebox 
from typing import Dict # CORRECCIÓN 1: Se importa Dict para anotaciones de tipo

# Importamos el controlador
from calendario_controller import CalendarioController

# --- CONFIGURACIÓN DE COLORES ---
BG_COLOR = "#F0F8FF"
WHITE_FRAME = "white"
ACCENT_BLUE = "#007BFF"
SOFT_BLUE_FRAME = "#D9EFFF"
SUCCESS_COLOR = "#28A745"
WARNING_COLOR = "#FFC107"
DANGER_COLOR = "#DC3545"
INFO_COLOR = "#17A2B8"
VISIBLE_BORDER = "#C8CDD6"

# Nombres tal cual aparecerán en la Interfaz (Deben coincidir con el MAPA en el controller)
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
        
        # Instancia del controlador
        self.controller = CalendarioController()

        # Layout Principal
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

        self.create_filter_panel(main_content, row=0)
        self.create_main_panels(main_content, row=1)
        self.create_daily_appointments_panel(main_content, row=2)
        
        self.load_daily_schedule() 

    def create_filter_panel(self, parent, row):
        filter_frame = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=10, border_color=VISIBLE_BORDER, border_width=1)
        filter_frame.grid(row=row, column=0, sticky="ew", pady=(0, 15)) 
        filter_frame.grid_columnconfigure(0, weight=0)
        filter_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(filter_frame, text="Filtrar por Doctora", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").grid(row=0, column=0, padx=(20, 10), pady=10, sticky="nw")
        
        self.doctora_vars: Dict[str, ctk.StringVar] = {} 
        checkbox_grid_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        checkbox_grid_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        checkbox_grid_frame.grid_columnconfigure((0, 1), weight=1) 
        
        # CORRECCIÓN 2: Se inicializa en "on" para que todos los filtros estén activados al inicio
        # Fila 1
        self.doctora_vars[DOCTORAS_DATA[0]] = ctk.StringVar(value="on")
        self._create_doctora_checkbox(checkbox_grid_frame, DOCTORAS_DATA[0], self.doctora_vars[DOCTORAS_DATA[0]], row=0, column=0)

        self.doctora_vars[DOCTORAS_DATA[1]] = ctk.StringVar(value="on")
        self._create_doctora_checkbox(checkbox_grid_frame, DOCTORAS_DATA[1], self.doctora_vars[DOCTORAS_DATA[1]], row=0, column=1)
        
        # Fila 2
        self.doctora_vars[DOCTORAS_DATA[2]] = ctk.StringVar(value="on")
        checkbox_grid_frame.grid_rowconfigure(1, weight=1) 
        self._create_doctora_checkbox(checkbox_grid_frame, DOCTORAS_DATA[2], self.doctora_vars[DOCTORAS_DATA[2]], row=1, column=0, columnspan=2)

    def _create_doctora_checkbox(self, parent_frame, doc_name, var_control, row, column, columnspan=1):
        check_wrapper = ctk.CTkFrame(parent_frame, fg_color=SOFT_BLUE_FRAME, corner_radius=15, border_color=ACCENT_BLUE, border_width=1)
        check_wrapper.grid(row=row, column=column, columnspan=columnspan, sticky="w", padx=5, pady=5) 
        check_wrapper.grid_columnconfigure(0, weight=1)
        check_wrapper.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(check_wrapper, text=doc_name, font=ctk.CTkFont(size=11), text_color=ACCENT_BLUE, anchor="w").grid(row=0, column=0, sticky="ew", padx=(10, 0), pady=5)
        
        ctk.CTkCheckBox(
            check_wrapper, text="", variable=var_control, 
            command=self.load_daily_schedule, 
            fg_color=ACCENT_BLUE, hover_color="#3A82D0", 
            border_color=ACCENT_BLUE, width=15, height=15,
            # *** ESTO FUERZA EL ESTADO VISUAL Y LA LÓGICA DE LA VARIABLE ***
            onvalue="on", 
            offvalue="off"
        ).grid(row=0, column=1, sticky="e", padx=(5, 10), pady=5)
                
    def create_main_panels(self, parent, row):
        panels_frame = ctk.CTkFrame(parent, fg_color="transparent")
        panels_frame.grid(row=row, column=0, sticky="nsew", pady=(0, 15))
        panels_frame.grid_columnconfigure(0, weight=1) 
        panels_frame.grid_columnconfigure(1, weight=1) 
        panels_frame.grid_rowconfigure(0, weight=1)
        
        self.create_date_picker_panel(panels_frame, column=0)
        self.create_summary_panel(panels_frame, column=1)

    def create_date_picker_panel(self, parent, column):
        calendar_panel = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=10, border_color=VISIBLE_BORDER, border_width=1)
        calendar_panel.grid(row=0, column=column, sticky="nsew", padx=(0, 15), pady=0)
        
        ctk.CTkLabel(calendar_panel, text=" 📅 Calendario", font=ctk.CTkFont(size=15, weight="bold"), text_color="#333333", anchor="w").pack(fill="x", padx=15, pady=(15, 5))
        
        self.calendar_container = ctk.CTkFrame(calendar_panel, fg_color="transparent")
        self.calendar_container.pack(padx=10, pady=5)
        
        # CORRECCIÓN 3: Llamada sin argumentos para evitar el TypeError
        self._create_mini_calendar() 

        legend_frame = ctk.CTkFrame(calendar_panel, fg_color=SOFT_BLUE_FRAME, corner_radius=10, border_color=VISIBLE_BORDER, border_width=1)
        legend_frame.pack(fill="x", padx=15, pady=(10, 15))
        ctk.CTkLabel(legend_frame, text="Los días en negrita tienen citas programadas", font=ctk.CTkFont(size=12), text_color="#333333").pack(padx=10, pady=5)
        
    def _create_mini_calendar(self):
        for widget in self.calendar_container.winfo_children():
            widget.destroy()

        cal = calendar.Calendar(firstweekday=0) 
        month_days = cal.monthdayscalendar(self.current_date.year, self.current_date.month)
        
        # Header Mes/Año
        header_frame = ctk.CTkFrame(self.calendar_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(header_frame, text="<", width=20, height=20, fg_color="transparent", hover_color="#DDDDDD", text_color="#333333", command=lambda: self.update_schedule(months=-1)).grid(row=0, column=0, padx=(0, 5))
        self.month_year_label = ctk.CTkLabel(header_frame, text=self.current_date.strftime("%B %Y").capitalize(), font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333")
        self.month_year_label.grid(row=0, column=1, sticky="ew")
        ctk.CTkButton(header_frame, text=">", width=20, height=20, fg_color="transparent", hover_color="#DDDDDD", text_color="#333333", command=lambda: self.update_schedule(months=1)).grid(row=0, column=2, padx=(5, 0))
        
        # Días semana
        days_of_week = ["lu", "ma", "mi", "ju", "vi", "sa", "do"] 
        days_frame = ctk.CTkFrame(self.calendar_container, fg_color="transparent")
        days_frame.pack(fill="x", padx=5, pady=(5, 0))
        for i, day in enumerate(days_of_week):
            days_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(days_frame, text=day.capitalize(), font=ctk.CTkFont(size=10, weight="normal"), text_color="#6B6B6B").grid(row=0, column=i, sticky="nsew")
        
        day_number_frame = ctk.CTkFrame(self.calendar_container, fg_color="transparent")
        day_number_frame.pack(fill="x", padx=5, pady=(0, 10))
        
        # Consultar días con citas en BD
        days_with_appointments = self.controller.obtener_dias_ocupados(self.current_date.year, self.current_date.month)
        today = datetime.now()
        
        for r, week in enumerate(month_days):
            for c, day in enumerate(week):
                day_number_frame.grid_columnconfigure(c, weight=1)
                
                if day != 0:
                    is_selected = (day == self.current_date.day)
                    has_appointments = day in days_with_appointments
                    is_today = (day == today.day and self.current_date.month == today.month and self.current_date.year == today.year)
                    
                    bg_color = ACCENT_BLUE if is_selected else WHITE_FRAME
                    text_color = "white" if is_selected else "#333333"
                    font_weight = "bold" if has_appointments else "normal"
                    hover_color = "#3A82D0" if is_selected else "#DDDDDD"

                    btn = ctk.CTkButton(
                        day_number_frame, text=str(day), width=25, height=25, 
                        fg_color=bg_color, text_color=text_color, 
                        font=ctk.CTkFont(size=12, weight=font_weight),
                        hover_color=hover_color, corner_radius=5,
                        command=lambda d=day: self.select_day(d)
                    )
                    if is_today and not is_selected:
                         btn.configure(border_color="#333333", border_width=1)
                    btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

    def create_summary_panel(self, parent, column):
        self.summary_card = ctk.CTkFrame(parent, fg_color=SOFT_BLUE_FRAME, corner_radius=10, border_color=VISIBLE_BORDER, border_width=1)
        self.summary_card.grid(row=0, column=column, sticky="nsew", padx=(15, 0), pady=0)
        self.summary_card.grid_columnconfigure(0, weight=1)
        self.summary_card.grid_rowconfigure(1, weight=1) 
        
        ctk.CTkLabel(self.summary_card, text=" 👤 Resumen del Día", font=ctk.CTkFont(size=15, weight="bold"), text_color=ACCENT_BLUE, anchor="w").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        self.summary_list_frame = ctk.CTkFrame(self.summary_card, fg_color="transparent")
        self.summary_list_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.summary_list_frame.grid_columnconfigure(0, weight=1)

    def update_summary(self, citas_data=None):
        if citas_data is None:
            citas_data = self.controller.obtener_citas_del_dia(self.current_date, self.doctora_vars)

        total = sum(len(citas_data[k]) for k in citas_data)
        
        summary_data = {
            "Total de citas": (total, None),
            "Pendientes": (len(citas_data.get('Pendientes', [])), WARNING_COLOR),
            "En curso": (len(citas_data.get('En curso', [])), INFO_COLOR),
            "Completadas": (len(citas_data.get('Completadas', [])), SUCCESS_COLOR),
            "Canceladas": (len(citas_data.get('Canceladas', [])), DANGER_COLOR),
        }
        
        for widget in self.summary_list_frame.winfo_children():
            widget.destroy()
            
        for i, (key, (value, color)) in enumerate(summary_data.items()):
            item_frame = ctk.CTkFrame(self.summary_list_frame, fg_color="transparent")
            item_frame.grid(row=i, column=0, sticky="ew", pady=(5, 5))
            item_frame.grid_columnconfigure(1, weight=1)
            
            if color:
                ctk.CTkLabel(item_frame, text="●", text_color=color, font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=(5, 10), sticky="w")
            
            ctk.CTkLabel(item_frame, text=key, font=ctk.CTkFont(size=14), text_color="#333333", anchor="w").grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(item_frame, text=str(value), font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").grid(row=0, column=2, padx=(10, 5), sticky="e")

    def create_daily_appointments_panel(self, parent, row):
        self.daily_appointments_card = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=10, border_color=VISIBLE_BORDER, border_width=1)
        self.daily_appointments_card.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        self.daily_appointments_card.grid_columnconfigure(0, weight=1)
        
        self.daily_header_label = ctk.CTkLabel(self.daily_appointments_card, text="", font=ctk.CTkFont(size=15, weight="bold"), text_color="#333333", anchor="w")
        self.daily_header_label.pack(fill="x", padx=15, pady=(15, 10))
        
        self.appointments_scroll_frame = ctk.CTkFrame(self.daily_appointments_card, fg_color="transparent")
        self.appointments_scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.appointments_scroll_frame.grid_columnconfigure(0, weight=1)

    def load_daily_schedule(self):
        # Obtener datos de la BD via Controller
        citas_data = self.controller.obtener_citas_del_dia(self.current_date, self.doctora_vars)
        
        # Actualizar resumen y header
        self.update_summary(citas_data)
        total_citas = sum(len(citas_data[k]) for k in citas_data)
        self.daily_header_label.configure(
            text=f"🗓️ {self.current_date.strftime('%A, %d de %B de %Y').capitalize()} | {total_citas} citas programadas"
        )
        
        for widget in self.appointments_scroll_frame.winfo_children():
            widget.destroy()

        current_row = 0
        for status, apps in citas_data.items():
            if not apps: continue

            title_frame = ctk.CTkFrame(self.appointments_scroll_frame, fg_color="transparent")
            title_frame.grid(row=current_row, column=0, sticky="w", pady=(15, 5))
            
            count = len(apps)
            ctk.CTkLabel(title_frame, text=f"{status}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").pack(side="left")
            ctk.CTkLabel(title_frame, text=f" {count}", font=ctk.CTkFont(size=12, weight="bold"), text_color="white", fg_color=ACCENT_BLUE, corner_radius=10, width=25, height=20).pack(side="left", padx=5)
            
            current_row += 1

            for app in apps:
                self._add_appointment_item(self.appointments_scroll_frame, app, status, current_row)
                current_row += 1

    def _add_appointment_item(self, parent, app_data, status, row):
        # Mapeo colores
        if status == 'Pendientes':
            tag_color = WARNING_COLOR
            border_color = WARNING_COLOR
            status_text = 'Pendiente'
        elif status == 'En curso':
            tag_color = INFO_COLOR
            border_color = INFO_COLOR
            status_text = 'En curso'
        elif status == 'Completadas':
            tag_color = SUCCESS_COLOR
            border_color = SUCCESS_COLOR
            status_text = 'Completada'
        else:
            tag_color = DANGER_COLOR
            border_color = DANGER_COLOR
            status_text = 'Cancelada'

        card = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=10, border_color=border_color, border_width=1)
        card.grid(row=row, column=0, sticky="ew", pady=5)
        card.grid_columnconfigure(1, weight=1)
        
        time_frame = ctk.CTkFrame(card, fg_color="transparent")
        time_frame.grid(row=0, column=0, sticky="nw", padx=15, pady=15)
        ctk.CTkLabel(time_frame, text="🕒", font=ctk.CTkFont(size=18)).pack(side="left")
        ctk.CTkLabel(time_frame, text=app_data['hora'], font=ctk.CTkFont(size=14, weight="bold"), text_color=ACCENT_BLUE).pack(side="left", padx=(5, 0))
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        info_frame.grid_columnconfigure(0, weight=1)
        
        tag = ctk.CTkLabel(info_frame, text=status_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="white", fg_color=tag_color, corner_radius=8, padx=10, pady=3)
        tag.grid(row=0, column=1, sticky="e")
        
        ctk.CTkLabel(info_frame, text=f"👤 {app_data['paciente']}", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 2))
        ctk.CTkLabel(info_frame, text=app_data['tratamiento'], font=ctk.CTkFont(size=13), anchor="w", text_color="#6B6B6B").grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 2))
        ctk.CTkLabel(info_frame, text=f"📞 {app_data.get('telefono', 'N/A')}", font=ctk.CTkFont(size=13), anchor="w", text_color="#6B6B6B").grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 2))
        ctk.CTkLabel(info_frame, text=f"Dra. {app_data['doctora']}", font=ctk.CTkFont(size=12, weight="bold"), anchor="w", text_color=ACCENT_BLUE).grid(row=4, column=0, columnspan=2, sticky="w", pady=(5, 0))

        if app_data.get('nota'):
             ctk.CTkLabel(info_frame, text=f"Nota: {app_data['nota']}", font=ctk.CTkFont(size=12, slant='italic'), anchor="w", text_color="#888888").grid(row=5, column=0, columnspan=2, sticky="w", pady=(2, 0))

    # Métodos de navegación 
    def select_day(self, day):
        new_date = self.current_date.replace(day=day)
        self.current_date = new_date
        self._create_mini_calendar() 
        self.load_daily_schedule() 

    def update_schedule(self, days=0, months=0):
        if days != 0:
            self.current_date += timedelta(days=days)
        elif months != 0:
            new_month = self.current_date.month + months
            new_year = self.current_date.year
            if new_month > 12:
                new_month = 1
                new_year += 1
            elif new_month < 1:
                new_month = 12
                new_year -= 1
            try:
                self.current_date = self.current_date.replace(year=new_year, month=new_month)
            except ValueError:
                last_day = calendar.monthrange(new_year, new_month)[1]
                self.current_date = self.current_date.replace(year=new_year, month=new_month, day=last_day)
        self._create_mini_calendar()
        self.load_daily_schedule()
        
    def handle_empty_slot_click(self, hour, minute):
        pass
    