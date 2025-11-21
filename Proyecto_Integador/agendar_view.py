# agendar_view.py
import customtkinter as ctk
from PIL import Image
import os 
import calendar
from datetime import datetime, timedelta
from tkinter import messagebox
from agendar_controller import AgendarCitaController

# --- CONFIGURACIÓN DE COLORES Y RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
BG_COLOR = "#F0F8FF"
WHITE_FRAME = "white"
ACCENT_BLUE = "#007BFF"
SOFT_BLUE_FRAME = "#D9EFFF"
BLUE_GRADIENT_START = "#00C6FF"

# Colores de Estado (Para el Resumen)
SUCCESS_COLOR = "#28A745" # Completadas
WARNING_COLOR = "#FFC107" # Pendientes
DANGER_COLOR = "#DC3545"  # Canceladas
INFO_COLOR = "#17A2B8"    # En curso

# Bordes discretos
VISIBLE_BORDER = "#C8CDD6"
DEFAULT_BORDER_WIDTH = 1

ICON_CALENDAR_PATH = os.path.join(current_dir, "icon_calendar.jpg") 

# Rutas de doctoras
DR_IMAGES = {
    "Dra. Raquel Guzmán Reyes (Ortodoncia)": os.path.join(current_dir, "doctora_1.jpg"),
    "Dra. Paola Jazmin Vera Guzmán (Endodoncia)": os.path.join(current_dir, "doctora_2.jpg"),
    "Dra. María Fernanda Cabrera (Cirugía General)": os.path.join(current_dir, "doctora_3.jpg"),
}

def load_doctor_image(name):
    path = DR_IMAGES.get(name)
    if path and os.path.exists(path):
        try:
            return ctk.CTkImage(Image.open(path).convert("RGB").resize((40, 40)), size=(40, 40))
        except Exception:
            pass
    return ctk.CTkImage(Image.new("RGB", (40, 40), "#AAAAAA"), size=(40, 40))


class AgendarCitaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.controller = AgendarCitaController() 
        
        # Variables de estado para el calendario
        self.selected_date = None
        self.current_cal_date = datetime.now()

        # Layout Principal
        self.content_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.content_frame.pack(fill="both", expand=True)
        
        self.content_frame.grid_columnconfigure(0, weight=1) # Izquierda (Form) expande
        self.content_frame.grid_columnconfigure(1, weight=0) # Derecha (Cards) fijo
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.create_form_panel()
        self.create_card_panel()

    def _obtener_rangos_edad(self):
        return ["Selecciona un rango", "0 - 3 años", "3 - 6 años", "6 - 12 años", "12 - 18 años", "18 - 35 años", "35 - 60 años", "60+ años"]

    # --- PANEL IZQUIERDO: FORMULARIO ---
    def create_form_panel(self):
        self.form_panel = ctk.CTkFrame(self.content_frame, fg_color=WHITE_FRAME, corner_radius=15, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH)
        self.form_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 20), pady=10) 
        
        # Header
        header_form = ctk.CTkFrame(self.form_panel, fg_color="transparent")
        header_form.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(header_form, text=" 📅 Agendar Nueva Cita", font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT_BLUE, anchor="w").pack(fill="x")
        ctk.CTkLabel(header_form, text="Completa el formulario para agendar tu cita", font=ctk.CTkFont(size=13), text_color="#6B6B6B", anchor="w").pack(fill="x")

        # Scroll Wrapper
        scroll_wrapper = ctk.CTkFrame(self.form_panel, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=8)
        scroll_wrapper.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        
        self.inner_form_frame = ctk.CTkScrollableFrame(scroll_wrapper, fg_color="transparent")
        self.inner_form_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self.inner_form_frame.grid_columnconfigure((0, 1), weight=1)
        
        doctoras = self.controller.obtener_doctoras()
        
        # 1. Nombre
        self.entry_nombre = self._add_form_field(self.inner_form_frame, "Nombre Completo *", "Ingresa tu nombre completo", 0, 0)
        
        # 2. Edad
        self.age_var = ctk.StringVar(value=self._obtener_rangos_edad()[0])
        self._add_form_dropdown(self.inner_form_frame, "Rango de Edad *", self._obtener_rangos_edad(), 0, 1, variable=self.age_var)
        
        # 3. Tratamiento Previo
        self.tratamiento_previo_var = ctk.StringVar(value="Selecciona una opción")
        self._add_form_dropdown(self.inner_form_frame, "¿Tratamiento previo? *", ["Selecciona una opción", "Sí", "No"], 2, 0, variable=self.tratamiento_previo_var, command=self.toggle_prev_treatment)
        self.prev_treatment_frame = ctk.CTkFrame(self.inner_form_frame, fg_color="transparent")
        
        # 4. Doctora
        self.doctora_var = ctk.StringVar(value="Selecciona una doctora")
        self._add_form_dropdown(self.inner_form_frame, "Doctora encargada *", ["Selecciona una doctora"] + doctoras, 2, 1, variable=self.doctora_var)
        
        # 5. FECHA Y HORA (Nueva Sección)
        self._create_date_time_section(self.inner_form_frame, 6) 

        # 6. Motivo (Presupuesto)
        self.entry_motivo = self._add_form_field(self.inner_form_frame, "Presupuesto o tratamiento *", "Ej: Brackets, Limpieza, Consulta", 8, 0, columnspan=2)
        
        # 7. Tipo Visita (Pago)
        self.tipo_visita_var = ctk.StringVar(value="Presupuesto (Gratuito)")
        self._add_form_dropdown(self.inner_form_frame, "Tipo de visita *", ["Presupuesto (Gratuito)", "Tratamiento (Con costo)"], 10, 0, columnspan=2, variable=self.tipo_visita_var, command=self.toggle_payment_info)
        self.payment_info_frame = ctk.CTkFrame(self.inner_form_frame, fg_color="transparent")
        
        # 8. Notas y Recordatorio
        self._add_notes_field(self.inner_form_frame, 12, offset=1) 
        self._add_reminder_section(self.inner_form_frame, 14, offset=1)

    # --- PANEL DERECHO: CARDS ---
    def create_card_panel(self):
        self.card_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.card_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10) 

        # Tarjeta Equipo Médico
        self._add_medical_team_card(self.card_panel, 0)
        
        # Tarjeta Resumen (NUEVA)
        self._add_summary_table_card(self.card_panel, 1)

    # --- LÓGICA DE FECHA Y HORA ---
    def _create_date_time_section(self, parent, row):
        ctk.CTkLabel(parent, text="Fecha y Hora de la Cita *", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row, column=0, sticky="w", pady=(15, 5), padx=(0, 10))
        
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row + 1, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 15))
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_columnconfigure(2, weight=1)

        # Botón Fecha
        self.btn_date = ctk.CTkButton(container, text="📅 Seleccionar Fecha", height=35, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, text_color="#6B6B6B", hover_color=SOFT_BLUE_FRAME, command=self.toggle_calendar)
        self.btn_date.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Hora Inicio (Con Borde)
        wrapper_start = ctk.CTkFrame(container, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=6)
        wrapper_start.grid(row=0, column=1, sticky="ew", padx=5)
        self.time_start_var = ctk.StringVar(value="--:--")
        self.combo_start = ctk.CTkOptionMenu(wrapper_start, variable=self.time_start_var, values=["Selecciona Fecha"], height=33, fg_color=WHITE_FRAME, button_color=WHITE_FRAME, button_hover_color=SOFT_BLUE_FRAME, text_color="#333333", command=self.update_end_times)
        self.combo_start.pack(fill="both", expand=True, padx=2, pady=2)

        # Hora Fin (Con Borde)
        wrapper_end = ctk.CTkFrame(container, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=6)
        wrapper_end.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        self.time_end_var = ctk.StringVar(value="--:--")
        self.combo_end = ctk.CTkOptionMenu(wrapper_end, variable=self.time_end_var, values=["--:--"], height=33, fg_color=WHITE_FRAME, button_color=WHITE_FRAME, button_hover_color=SOFT_BLUE_FRAME, text_color="#333333")
        self.combo_end.pack(fill="both", expand=True, padx=2, pady=2)

        # Mini Calendario (Oculto por defecto)
        self.calendar_frame = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=8)
        self.calendar_frame_row = row + 2 
        self.render_mini_calendar()

    def toggle_calendar(self):
        if self.calendar_frame.winfo_ismapped():
            self.calendar_frame.grid_forget()
        else:
            self.calendar_frame.grid(row=self.calendar_frame_row, column=0, columnspan=2, sticky="w", padx=0, pady=5)
            self.calendar_frame.lift()

    def render_mini_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Header del Calendario
        header = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        header.pack(fill="x", pady=5)
        ctk.CTkButton(header, text="<", width=30, fg_color="transparent", text_color="black", hover_color="#EEE", command=lambda: self.change_month(-1)).pack(side="left", padx=5)
        ctk.CTkLabel(header, text=self.current_cal_date.strftime("%B %Y").capitalize(), font=("Arial", 12, "bold")).pack(side="left", expand=True)
        ctk.CTkButton(header, text=">", width=30, fg_color="transparent", text_color="black", hover_color="#EEE", command=lambda: self.change_month(1)).pack(side="right", padx=5)

        # Días de la semana
        days_frame = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        days_frame.pack(padx=5, pady=5)
        dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]
        for i, dia in enumerate(dias_semana):
            ctk.CTkLabel(days_frame, text=dia, width=30, font=("Arial", 10, "bold"), text_color="#666").grid(row=0, column=i)

        # Días numéricos
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(self.current_cal_date.year, self.current_cal_date.month)

        for r, week in enumerate(month_days):
            for c, day in enumerate(week):
                if day != 0:
                    date_obj = datetime(self.current_cal_date.year, self.current_cal_date.month, day)
                    is_sunday = date_obj.weekday() == 6
                    is_past = date_obj.date() < datetime.now().date()
                    
                    state = "disabled" if (is_sunday or is_past) else "normal"
                    color = "#DDDDDD" if state == "disabled" else "transparent"
                    text_col = "#AAAAAA" if state == "disabled" else "black"
                    
                    if self.selected_date and date_obj.date() == self.selected_date.date():
                        color = ACCENT_BLUE
                        text_col = "white"

                    btn = ctk.CTkButton(
                        days_frame, text=str(day), width=30, height=25, fg_color=color, text_color=text_col,
                        state=state, hover_color=SOFT_BLUE_FRAME if state == "normal" else "#DDDDDD",
                        command=lambda d=date_obj: self.select_date(d)
                    )
                    btn.grid(row=r+1, column=c, padx=1, pady=1)

    def change_month(self, amount):
        new_month = self.current_cal_date.month + amount
        new_year = self.current_cal_date.year
        if new_month > 12: new_month = 1; new_year += 1
        elif new_month < 1: new_month = 12; new_year -= 1
        self.current_cal_date = self.current_cal_date.replace(year=new_year, month=new_month, day=1)
        self.render_mini_calendar()

    def select_date(self, date_obj):
        self.selected_date = date_obj
        self.btn_date.configure(text=f"📅 {date_obj.strftime('%d/%m/%Y')}", fg_color=SOFT_BLUE_FRAME, border_color=ACCENT_BLUE)
        self.calendar_frame.grid_forget()
        
        # Generar horarios disponibles usando el controlador
        horarios = self.controller.generar_horarios_disponibles(date_obj)
        
        if horarios:
            self.combo_start.configure(values=horarios)
            self.time_start_var.set(horarios[0])
            self.update_end_times(horarios[0])
        else:
            self.combo_start.configure(values=["Cerrado"])
            self.time_start_var.set("Cerrado")
            self.combo_end.configure(values=["--:--"])
            self.time_end_var.set("--:--")

    def update_end_times(self, start_time):
        if start_time in ["--:--", "Cerrado", "Selecciona Fecha"]: return
        start_dt = datetime.strptime(start_time, "%H:%M")
        possible_ends = []
        current = start_dt + timedelta(minutes=15)
        limit = start_dt + timedelta(hours=2) # Máx 2 horas
        
        # Hora cierre según día (Sábado vs Semana)
        cierre_hora = 16 if self.selected_date and self.selected_date.weekday() == 5 else 20
        limit_cierre = start_dt.replace(hour=cierre_hora, minute=0)

        while current <= limit and current <= limit_cierre:
            possible_ends.append(current.strftime("%H:%M"))
            current += timedelta(minutes=15)
        
        self.combo_end.configure(values=possible_ends)
        if possible_ends: self.time_end_var.set(possible_ends[0])

    # --- TARJETA DE RESUMEN ---
    def _add_summary_table_card(self, parent, row):
        # Limpiar si ya existe (para recargar)
        for widget in parent.grid_slaves(row=row, column=0):
            widget.destroy()

        card = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=15, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(card, text=" 📊 Resumen Global", font=ctk.CTkFont(size=15, weight="bold"), text_color=ACCENT_BLUE, anchor="w").pack(fill="x", padx=15, pady=(15, 10))
        ctk.CTkLabel(card, text="Estado de citas (Todas las Doctoras)", font=ctk.CTkFont(size=12), text_color="#6B6B6B", anchor="w").pack(fill="x", padx=15, pady=(0, 15))

        summary_list = ctk.CTkFrame(card, fg_color="transparent")
        summary_list.pack(fill="x", padx=15, pady=(0, 15))
        summary_list.grid_columnconfigure(1, weight=1)

        # Obtener Datos Reales
        conteo = self.controller.obtener_datos_resumen()
        
        summary_data = {
            "Total de citas": (conteo.get('Total', 0), None),
            "Pendientes": (conteo.get('Pendiente', 0), WARNING_COLOR),
            "En curso": (conteo.get('En curso', 0), INFO_COLOR),
            "Completadas": (conteo.get('Completada', 0), SUCCESS_COLOR),
            "Canceladas": (conteo.get('Cancelada', 0), DANGER_COLOR),
        }

        for i, (key, (value, color)) in enumerate(summary_data.items()):
            item_frame = ctk.CTkFrame(summary_list, fg_color="transparent")
            item_frame.grid(row=i, column=0, sticky="ew", pady=4)
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Bullet
            col = color if color else "#333333"
            ctk.CTkLabel(item_frame, text="●", text_color=col, font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(0, 5), sticky="w")
            
            ctk.CTkLabel(item_frame, text=key, font=ctk.CTkFont(size=13), text_color="#333333", anchor="w").grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(item_frame, text=str(value), font=ctk.CTkFont(size=13, weight="bold"), text_color="#333333").grid(row=0, column=2, sticky="e", padx=5)

    # --- ACCIÓN DE GUARDAR ---
    def accion_agendar(self):
        # Recopilar datos
        datos = {
            'nombre': self.entry_nombre.get(),
            'doctora': self.doctora_var.get(),
            'fecha': self.selected_date.strftime('%d/%m/%Y') if self.selected_date else None,
            'fecha_obj': self.selected_date,
            'hora': self.time_start_var.get(),
            'motivo': self.entry_motivo.get(),
            'notas': self.notes_textbox.get("1.0", "end-1c")
        }
        
        exito, mensaje = self.controller.guardar_cita(datos)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            # Recargar el resumen para mostrar el +1
            self._add_summary_table_card(self.card_panel, 1)
            # Limpiar formulario (opcional)
            self.entry_nombre.delete(0, 'end')
            self.entry_motivo.delete(0, 'end')
            self.notes_textbox.delete("1.0", "end")
        else:
            messagebox.showerror("Error", mensaje)

    # --- HELPERS ---
    def _add_medical_team_card(self, parent, row):
        card = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=15, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH)
        card.grid(row=row, column=0, sticky="ew", pady=(10, 20))
        ctk.CTkLabel(card, text=" ⚕️ Nuestro Equipo Médico", font=ctk.CTkFont(size=15, weight="bold"), text_color=ACCENT_BLUE, anchor="w").pack(fill="x", padx=15, pady=(15, 10))
        
        for doc_info in self.controller.obtener_doctoras():
            name, specialty = doc_info.split(" (")
            specialty = specialty.replace(")", "")
            
            f = ctk.CTkFrame(card, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=5)
            
            full_name = f"{name} ({specialty})"
            img = load_doctor_image(full_name)
            if img: ctk.CTkLabel(f, text="", image=img).pack(side="left", padx=(0, 10))
            else: ctk.CTkLabel(f, text="👩‍⚕️", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
            
            info = ctk.CTkFrame(f, fg_color="transparent")
            info.pack(side="left")
            ctk.CTkLabel(info, text=name, font=("Arial", 12, "bold"), text_color="#333").pack(anchor="w")
            ctk.CTkLabel(info, text=specialty, font=("Arial", 11), text_color=ACCENT_BLUE).pack(anchor="w")

    def toggle_prev_treatment(self, choice):
        for w in self.prev_treatment_frame.winfo_children(): w.destroy()
        if choice == "Sí":
            self.prev_treatment_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
            ctk.CTkLabel(self.prev_treatment_frame, text="Describe tu tratamiento previo *", font=("Arial", 14, "bold"), anchor="w", text_color="#333").pack(fill="x", pady=(15, 5))
            ctk.CTkEntry(self.prev_treatment_frame, placeholder_text="Ej: Brackets", height=35, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH).pack(fill="x", pady=(0, 15))
        else:
            self.prev_treatment_frame.grid_forget()

    def toggle_payment_info(self, choice):
        if choice == "Tratamiento (Con costo)":
            self.payment_info_frame.grid(row=12, column=0, columnspan=2, sticky="ew")
            self.payment_info_frame.lift()
            self._add_payment_fields(self.payment_info_frame)
        else:
            self.payment_info_frame.grid_forget()
            for w in self.payment_info_frame.winfo_children(): w.destroy()

    def _add_payment_fields(self, parent):
        for w in parent.winfo_children(): w.destroy()
        pc = ctk.CTkFrame(parent, fg_color="#E9F5FF", corner_radius=10, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH)
        pc.pack(fill="x", pady=(15, 10), padx=0)
        ctk.CTkLabel(pc, text="Información de pago", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkEntry(pc, placeholder_text="Costo Total", height=30, fg_color="white", border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH).pack(fill="x", padx=15, pady=5)
        ctk.CTkEntry(pc, placeholder_text="Pago Inicial", height=30, fg_color="white", border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH).pack(fill="x", padx=15, pady=5)

    def _add_form_field(self, parent, label, ph, row, col, columnspan=1):
        ctk.CTkLabel(parent, text=label, font=("Arial", 14, "bold"), text_color="#333").grid(row=row, column=col, sticky="w", pady=(15, 5), padx=(0, 10))
        e = ctk.CTkEntry(parent, placeholder_text=ph, height=35, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH)
        e.grid(row=row+1, column=col, sticky="ew", padx=(0, 10), pady=(0, 15), columnspan=columnspan)
        return e

    def _add_form_dropdown(self, parent, label, vals, row, col, columnspan=1, variable=None, command=None):
        ctk.CTkLabel(parent, text=label, font=("Arial", 14, "bold"), text_color="#333").grid(row=row, column=col, sticky="w", pady=(15, 5), padx=(0, 10))
        w = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=6)
        w.grid(row=row+1, column=col, sticky="ew", padx=(0, 10), pady=(0, 15), columnspan=columnspan)
        ctk.CTkOptionMenu(w, values=vals, height=35, fg_color=WHITE_FRAME, button_color=WHITE_FRAME, button_hover_color=SOFT_BLUE_FRAME, text_color="#6B6B6B", variable=variable, command=command).pack(fill="both", expand=True, padx=6, pady=2)

    def _add_notes_field(self, parent, row, offset=0):
        ctk.CTkLabel(parent, text="Notas adicionales", font=("Arial", 14, "bold"), text_color="#333").grid(row=row+offset, column=0, columnspan=2, sticky="w", pady=(15, 5))
        nc = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=6)
        nc.grid(row=row+1+offset, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.notes_textbox = ctk.CTkTextbox(nc, height=80, fg_color=WHITE_FRAME, wrap="word")
        self.notes_textbox.pack(fill="both", padx=1, pady=1)
        self.placeholder_label = ctk.CTkLabel(nc, text="Información adicional...", text_color="#AAAAAA", font=("Arial", 14, "italic"))
        self.placeholder_label.place(x=10, y=10)
        self.notes_textbox.bind("<FocusIn>", lambda e: self.placeholder_label.place_forget())
        self.notes_textbox.bind("<FocusOut>", lambda e: self.placeholder_label.place(x=10, y=10) if not self.notes_textbox.get("1.0", "end-1c").strip() else None)

    def _add_reminder_section(self, parent, row, offset=0):
        rf = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=10, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH)
        rf.grid(row=row+offset, column=0, columnspan=2, sticky="ew", pady=(20, 10))
        rf.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(rf, text=" 🔔 Recordatorio de cita", font=("Arial", 14), text_color="#333").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        self.reminder_switch = ctk.CTkSwitch(rf, text="", command=self.toggle_contact_info, progress_color=ACCENT_BLUE)
        self.reminder_switch.grid(row=0, column=1, sticky="e", padx=20, pady=10)
        
        self.contact_info_container = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Botón Agendar - CONECTADO
        ctk.CTkButton(parent, text=" 🕒 Agendar Cita", height=45, corner_radius=10, fg_color=ACCENT_BLUE, font=("Arial", 16, "bold"), command=self.accion_agendar).grid(row=row+2+offset, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def toggle_contact_info(self):
        if self.reminder_switch.get() == 1:
            self.contact_info_container.grid(row=16, column=0, columnspan=2, sticky="ew")
            for w in self.contact_info_container.winfo_children(): w.destroy()
            cf = ctk.CTkFrame(self.contact_info_container, fg_color="#E9F5FF", border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH)
            cf.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(cf, text="Contacto", font=("Arial", 13, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=10)
            ctk.CTkEntry(cf, placeholder_text="Teléfono", fg_color="white").pack(fill="x", padx=20, pady=5)
            ctk.CTkEntry(cf, placeholder_text="Email", fg_color="white").pack(fill="x", padx=20, pady=5)
        else:
            self.contact_info_container.grid_forget()