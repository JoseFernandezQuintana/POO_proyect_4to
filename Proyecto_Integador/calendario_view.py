# calendario_view.py
import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox 
import calendar # <<-- NECESARIO PARA EL MINI CALENDARIO

# --- CONFIGURACIÓN DE COLORES ---
BG_COLOR = "#F0F8FF"
WHITE_FRAME = "white"
ACCENT_BLUE = "#007BFF"        
SOFT_BLUE_FRAME = "#D9EFFF"    
SUCCESS_COLOR = "#28A745"      
WARNING_COLOR = "#FFC107"      
DANGER_COLOR = "#DC3545"       


class CalendarFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.master = master
        
        main_card = ctk.CTkFrame(self, fg_color=WHITE_FRAME, corner_radius=15, border_color="#DDDDDD", border_width=1)
        main_card.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Header de la tarjeta
        ctk.CTkLabel(main_card, text=" 🗓️ Visualización de Citas y Calendario", font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT_BLUE, anchor="w").pack(fill="x", padx=30, pady=(20, 5))
        ctk.CTkLabel(main_card, text="Consulta la ocupación por día. Haz clic en un espacio vacío para agendar.", font=ctk.CTkFont(size=13), text_color="#6B6B6B", anchor="w").pack(fill="x", padx=30, pady=(0, 20))
        
        content_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        content_frame.grid_columnconfigure(0, weight=1) 
        content_frame.grid_columnconfigure(1, weight=4) 
        content_frame.grid_rowconfigure(0, weight=1)
        
        self.current_date = datetime.now()
        
        self.create_date_picker_panel(content_frame)
        self.create_schedule_panel(content_frame)

    # --- Panel Izquierdo: Mini Calendario y Leyenda ---
    def create_date_picker_panel(self, parent):
        # Usamos un ScrollableFrame para que el contenido se ajuste si es necesario
        calendar_panel = ctk.CTkScrollableFrame(parent, fg_color=SOFT_BLUE_FRAME, corner_radius=10)
        calendar_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=0)
        
        ctk.CTkLabel(calendar_panel, text="🗓️ Agenda por Mes", font=ctk.CTkFont(size=15, weight="bold"), text_color="#333333").pack(pady=(15, 10))
        
        # Etiqueta de la fecha seleccionada
        self.date_label = ctk.CTkLabel(
            calendar_panel, 
            text=self.current_date.strftime("%A, %d de %B %Y").capitalize(), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color="#6B6B6B"
        )
        self.date_label.pack(pady=(0, 10))

        # Contenedor del calendario
        self.calendar_container = ctk.CTkFrame(calendar_panel, fg_color="transparent")
        self.calendar_container.pack(fill="x", padx=10, pady=(5, 15))
        
        self._create_mini_calendar() # Dibuja la vista de mes

        # Leyenda de Ocupación (Esta sección está fija en la parte baja del ScrollableFrame)
        ctk.CTkLabel(calendar_panel, text="Referencia de Ocupación", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").pack(pady=(20, 5))
        
        self._add_legend_item(calendar_panel, "Cita Programada", SUCCESS_COLOR)
        self._add_legend_item(calendar_panel, "Receso/Comida", WARNING_COLOR)
        self._add_legend_item(calendar_panel, "Espacio Libre", SOFT_BLUE_FRAME, "#333333")
        self._add_legend_item(calendar_panel, "Cita Urgente", DANGER_COLOR)

# ... (El resto de la clase, incluyendo _add_legend_item, _create_mini_calendar, etc., sigue igual) ...

    # --- MÉTODO FALTANTE (¡ESTE ARREGLA EL ERROR!) ---
    def _add_legend_item(self, parent, text, color, text_color="white"):
        """Crea un ítem de la leyenda."""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkFrame(item_frame, fg_color=color, width=15, height=15, corner_radius=3).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(item_frame, text=text, font=ctk.CTkFont(size=13), text_color="#333333" if color == SOFT_BLUE_FRAME else "#333333").pack(side="left")
    # --------------------------------------------------

    def _create_mini_calendar(self):
        """Genera la vista del mes con botones interactivos."""
        for widget in self.calendar_container.winfo_children():
            widget.destroy()

        cal = calendar.Calendar(firstweekday=6) # 6 = Domingo
        month_days = cal.monthdayscalendar(self.current_date.year, self.current_date.month)
        
        # Header (Botones de mes y etiqueta del mes/año)
        header_frame = ctk.CTkFrame(self.calendar_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(header_frame, text="<", width=25, fg_color=ACCENT_BLUE, hover_color="#3A82D0", command=lambda: self.update_schedule(months=-1)).pack(side="left")
        
        self.month_year_label = ctk.CTkLabel(header_frame, text=self.current_date.strftime("%B %Y").capitalize(), font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333")
        self.month_year_label.pack(side="left", expand=True)
        
        ctk.CTkButton(header_frame, text=">", width=25, fg_color=ACCENT_BLUE, hover_color="#3A82D0", command=lambda: self.update_schedule(months=1)).pack(side="right")
        
        # Días de la semana
        days_of_week = ["D", "L", "M", "X", "J", "V", "S"]
        days_frame = ctk.CTkFrame(self.calendar_container, fg_color="transparent")
        days_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        for i, day in enumerate(days_of_week):
            days_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(days_frame, text=day, font=ctk.CTkFont(size=10, weight="bold"), text_color=ACCENT_BLUE).grid(row=0, column=i, sticky="nsew")
        
        # Días del mes (Botones interactivos)
        day_number_frame = ctk.CTkFrame(self.calendar_container, fg_color="transparent")
        day_number_frame.pack(fill="x", padx=5, pady=(0, 10))
        
        today = datetime.now()
        
        for r, week in enumerate(month_days):
            day_number_frame.grid_rowconfigure(r, weight=1)
            for c, day in enumerate(week):
                day_number_frame.grid_columnconfigure(c, weight=1)
                
                if day != 0:
                    is_today = (day == today.day and self.current_date.month == today.month and self.current_date.year == today.year)
                    is_selected = (day == self.current_date.day)
                    
                    bg_color = ACCENT_BLUE if is_selected else SOFT_BLUE_FRAME if is_today else "transparent"
                    text_color = "white" if is_selected else "#333333"

                    btn = ctk.CTkButton(
                        day_number_frame, 
                        text=str(day), 
                        width=25, height=25, 
                        fg_color=bg_color, 
                        text_color=text_color, 
                        hover_color="#DDDDDD" if not is_selected else "#3A82D0",
                        corner_radius=5,
                        command=lambda d=day: self.select_day(d)
                    )
                    btn.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")

    def select_day(self, day):
        """Establece un día específico y actualiza la vista."""
        new_date = self.current_date.replace(day=day)
        self.current_date = new_date
        self.date_label.configure(text=self.current_date.strftime("%A, %d de %B %Y").capitalize())
        self._create_mini_calendar() 
        self.load_daily_schedule() 

    def update_schedule(self, days=0, months=0):
        """Función para cambiar la fecha o el mes y recargar la agenda."""
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
            
            # Ajustar el día al final del mes si es necesario
            try:
                self.current_date = self.current_date.replace(year=new_year, month=new_month)
            except ValueError:
                last_day = calendar.monthrange(new_year, new_month)[1]
                self.current_date = self.current_date.replace(year=new_year, month=new_month, day=last_day)


        self.date_label.configure(text=self.current_date.strftime("%A, %d de %B %Y").capitalize())
        self._create_mini_calendar()
        self.load_daily_schedule()
        
    # --- Panel Derecho (Agenda Diaria) ---
    def create_schedule_panel(self, parent):
        self.schedule_scroll_frame = ctk.CTkScrollableFrame(parent, fg_color=WHITE_FRAME, corner_radius=10, border_color="#DDDDDD", border_width=1)
        self.schedule_scroll_frame.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=0)
        
        ctk.CTkLabel(self.schedule_scroll_frame, text="Agenda del Día (Horario Completo)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#333333", anchor="w").pack(fill="x", padx=15, pady=(15, 10))

        self.schedule_container = ctk.CTkFrame(self.schedule_scroll_frame, fg_color="transparent")
        self.schedule_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.schedule_container.grid_columnconfigure(0, weight=0) 
        self.schedule_container.grid_columnconfigure(1, weight=1) 

        self.load_daily_schedule()
        
    def load_daily_schedule(self):
        """Carga la agenda para la fecha actual (slots vacíos por defecto)."""
        
        for widget in self.schedule_container.winfo_children():
            widget.destroy()

        start_hour = 8 # 8 AM
        end_hour = 20  # 8 PM (20:00)
        
        appointments = [] # Aquí iría la consulta a la BD

        
        for i in range(start_hour * 2, end_hour * 2): # Iterar en intervalos de 30 minutos
            hour = i // 2
            minute = 30 if i % 2 == 1 else 0
            
            time_dt = datetime(1, 1, 1, hour, minute)
            time_str = time_dt.strftime("%I:%M %p")
            
            self.schedule_container.grid_rowconfigure(i, weight=1)
            
            # Columna 0: Etiqueta de la hora
            if minute == 0:
                time_label_frame = ctk.CTkFrame(self.schedule_container, fg_color="transparent")
                time_label_frame.grid(row=i, column=0, sticky="n", padx=(5, 5))
                ctk.CTkLabel(time_label_frame, text=time_str, font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B6B6B").pack(anchor="n")
                
            
            # Columna 1: Slot de la Cita o Vacío
            appointment_info = next(
                (app for app in appointments if app['hour'] == hour and app['minute'] == minute),
                None
            )
            
            if not appointment_info:
                # Slot VACÍO - Interactividad (Clic para Agendar)
                empty_slot = ctk.CTkFrame(self.schedule_container, fg_color="#F8FAFF", border_color="#DDDDDD", border_width=1, corner_radius=4)
                
                empty_slot.grid(row=i, column=1, rowspan=1, sticky="nsew", padx=(0, 5), pady=(2, 2), ipadx=0, ipady=5)
                
                empty_slot.bind("<Button-1>", lambda event, h=hour, m=minute: self.handle_empty_slot_click(h, m))
                
    def handle_empty_slot_click(self, hour, minute):
        """Maneja el evento de hacer clic en un slot vacío para iniciar el agendamiento."""
        selected_time = datetime(self.current_date.year, self.current_date.month, self.current_date.day, hour, minute)
        
        messagebox.showinfo(
            "Agendar Cita", 
            f"Hora seleccionada: {selected_time.strftime('%I:%M %p')}.\n"
            f"Navegando a la vista de Agendar para el {selected_time.strftime('%d/%m/%Y')}."
        )
        
        # Aquí se llamaría a la función de cambio de vista, por ejemplo:
        # self.master.master.show_view("agendar", date=selected_time.date(), time=selected_time.time())
