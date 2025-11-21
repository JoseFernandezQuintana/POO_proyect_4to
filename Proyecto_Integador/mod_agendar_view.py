import customtkinter as ctk
from tkinter import messagebox 
from datetime import datetime, timedelta
import calendar
import os
from mod_agendar_controller import ModificarCitaController 

# --- CONFIGURACIÓN DE COLORES (Igual que agendar_view) ---
BG_COLOR = "#F0F8FF"
WHITE_FRAME = "white"
ACCENT_BLUE = "#007BFF"
SOFT_BLUE_FRAME = "#D9EFFF"
VISIBLE_BORDER = "#C8CDD6"
DEFAULT_BORDER_WIDTH = 1
SUCCESS_COLOR = "#28A745"
DANGER_COLOR = "#DC3545"

class ModificarCitaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_COLOR)
        self.master = master
        self.controller = ModificarCitaController() 
        self.active_appointment_id = None
        
        # Variables de calendario
        self.selected_date = None
        self.current_cal_date = datetime.now()

        # Layout Principal
        main_card = ctk.CTkFrame(self, fg_color=WHITE_FRAME, corner_radius=15, border_color=VISIBLE_BORDER, border_width=1)
        main_card.pack(fill="both", expand=True, padx=5, pady=10) 
        main_card.grid_columnconfigure(0, weight=1)
        main_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(main_card, text=" ✏️ Modificación y Reagendamiento", font=ctk.CTkFont(size=20, weight="bold"), text_color=ACCENT_BLUE, anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        self.content_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.create_search_panel(self.content_frame, row=0)
        
        self.edit_form_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.edit_form_container.grid(row=1, column=0, sticky="nsew")
        
        self.initial_message = ctk.CTkLabel(self.edit_form_container, text="Busca un paciente para editar su cita.", text_color="#6B6B6B", font=ctk.CTkFont(size=14, slant="italic"))
        self.initial_message.pack(pady=50)

    # -----------------------------------------------
    # 1. PANEL DE BÚSQUEDA
    # -----------------------------------------------
    def create_search_panel(self, parent, row):
        search_card = ctk.CTkFrame(parent, fg_color=SOFT_BLUE_FRAME, corner_radius=10, border_color=ACCENT_BLUE, border_width=1)
        search_card.grid(row=row, column=0, sticky="ew", pady=(0, 15))
        search_card.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(search_card, placeholder_text="Buscar por nombre o teléfono...", font=ctk.CTkFont(size=14), fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        self.search_entry.bind("<Return>", self.perform_search)
        
        ctk.CTkButton(search_card, text="🔍 Buscar", command=self.perform_search, fg_color=ACCENT_BLUE, width=100).grid(row=0, column=1, padx=(0, 15), pady=15)
        
        self.results_dropdown = ctk.CTkOptionMenu(search_card, values=["Sin resultados"], command=self.select_patient_from_search, fg_color=WHITE_FRAME, text_color="#333", button_color=WHITE_FRAME, button_hover_color=SOFT_BLUE_FRAME)
        self.results_dropdown.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 15))
        self.results_dropdown.set("Resultados de búsqueda...")
        self.last_search_map = {}

    def perform_search(self, event=None):
        query = self.search_entry.get().strip()
        resultados = self.controller.buscar_citas_flexibles(query)
        
        self.last_search_map = {}
        values = []
        if not resultados:
            values = ["No se encontraron citas"]
        else:
            for r in resultados:
                self.last_search_map[r['display']] = r['id']
                values.append(r['display'])
        
        self.results_dropdown.configure(values=values)
        self.results_dropdown.set(values[0] if values else "Sin resultados")

    def select_patient_from_search(self, display_text):
        if display_text in self.last_search_map:
            cita_id = self.last_search_map[display_text]
            data = self.controller.obtener_datos_cita(cita_id)
            if data:
                self.active_appointment_id = cita_id
                self.load_form(data)
            else:
                messagebox.showerror("Error", "No se pudo cargar la cita.")

    # -----------------------------------------------
    # 2. FORMULARIO DE EDICIÓN (Estilo Agendar)
    # -----------------------------------------------
    def load_form(self, data):
        # Limpiar anterior
        for w in self.edit_form_container.winfo_children(): w.destroy()
        
        scroll_wrapper = ctk.CTkFrame(self.edit_form_container, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=8)
        scroll_wrapper.pack(fill="both", expand=True)
        
        inner = ctk.CTkScrollableFrame(scroll_wrapper, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=10)
        inner.grid_columnconfigure((0, 1), weight=1)

        # Variables de Control
        self.var_nombre = ctk.StringVar(value=data['nombre_completo'])
        self.var_doctora = ctk.StringVar(value=data['doctora'])
        self.var_motivo = ctk.StringVar(value=data['motivo'])
        
        # 1. Nombre (Solo lectura visualmente)
        self._add_field(inner, "Paciente (No editable)", 0, 0, var=self.var_nombre, state="disabled")
        
        # 2. Doctora
        doctoras = self.controller.obtener_doctoras()
        self._add_dropdown(inner, "Doctora Asignada", doctoras, 2, 0, var=self.var_doctora)
        
        # 3. Fecha y Hora (Mini Calendario)
        # Inicializamos las variables del calendario con los datos de la BD
        self.selected_date = data['fecha_obj']
        self.current_cal_date = data['fecha_obj']
        self._create_date_time_section(inner, 4, initial_time=data['hora'])

        # 4. Motivo
        self._add_field(inner, "Motivo / Tratamiento", 6, 0, columnspan=2, var=self.var_motivo)
        
        # 5. Notas
        self._add_notes_field(inner, 8, initial_text=data['notas'])

        # Botones de Acción
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.grid(row=10, column=0, columnspan=2, sticky="ew", pady=20)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="💾 Guardar Cambios", command=self.save_changes, fg_color=SUCCESS_COLOR, height=40).grid(row=0, column=0, sticky="ew", padx=5)
        ctk.CTkButton(btn_frame, text="🚫 Cancelar Cita", command=self.cancel_appointment, fg_color=DANGER_COLOR, height=40).grid(row=0, column=1, sticky="ew", padx=5)

    # -----------------------------------------------
    # 3. HELPERS DE UI (Copiados y adaptados)
    # -----------------------------------------------
    def _add_field(self, parent, label, row, col, columnspan=1, var=None, state="normal"):
        ctk.CTkLabel(parent, text=label, font=("Arial", 14, "bold"), text_color="#333").grid(row=row, column=col, sticky="w", pady=(10, 0), padx=5)
        e = ctk.CTkEntry(parent, textvariable=var, state=state, height=35, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER)
        e.grid(row=row+1, column=col, sticky="ew", padx=5, pady=(5, 10), columnspan=columnspan)

    def _add_dropdown(self, parent, label, values, row, col, columnspan=2, var=None):
        ctk.CTkLabel(parent, text=label, font=("Arial", 14, "bold"), text_color="#333").grid(row=row, column=col, sticky="w", pady=(10, 0), padx=5)
        w = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=1, corner_radius=6)
        w.grid(row=row+1, column=col, sticky="ew", padx=5, pady=(5, 10), columnspan=columnspan)
        ctk.CTkOptionMenu(w, values=values, variable=var, fg_color=WHITE_FRAME, button_color=WHITE_FRAME, text_color="#333", button_hover_color=SOFT_BLUE_FRAME).pack(fill="both", expand=True, padx=5, pady=2)

    def _create_date_time_section(self, parent, row, initial_time):
        ctk.CTkLabel(parent, text="Fecha y Hora *", font=("Arial", 14, "bold"), text_color="#333").grid(row=row, column=0, sticky="w", pady=(10, 0), padx=5)
        
        cont = ctk.CTkFrame(parent, fg_color="transparent")
        cont.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 10))
        cont.grid_columnconfigure((0, 1), weight=1)

        # Botón Fecha
        date_str = self.selected_date.strftime('%d/%m/%Y')
        self.btn_date = ctk.CTkButton(cont, text=f"📅 {date_str}", fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=1, text_color="#333", hover_color=SOFT_BLUE_FRAME, command=self.toggle_calendar)
        self.btn_date.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Selector Hora
        self.var_hora = ctk.StringVar(value=initial_time)
        self.combo_hora = ctk.CTkOptionMenu(cont, variable=self.var_hora, values=[initial_time], fg_color=ACCENT_BLUE) # Se llenará al abrir calendario
        self.combo_hora.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Frame Calendario (Oculto)
        self.cal_frame = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=1)
        self.cal_row = row + 2
        
        # Cargar horas disponibles para la fecha actual por si solo quiere cambiar hora
        self.update_hours_for_date(self.selected_date)

    def toggle_calendar(self):
        if self.cal_frame.winfo_ismapped():
            self.cal_frame.grid_forget()
        else:
            self.cal_frame.grid(row=self.cal_row, column=0, columnspan=2, sticky="w", padx=10)
            self.render_calendar()

    def render_calendar(self):
        for w in self.cal_frame.winfo_children(): w.destroy()
        
        # Header
        h = ctk.CTkFrame(self.cal_frame, fg_color="transparent")
        h.pack(fill="x")
        ctk.CTkButton(h, text="<", width=30, fg_color="transparent", text_color="black", command=lambda: self.change_month(-1)).pack(side="left")
        ctk.CTkLabel(h, text=self.current_cal_date.strftime("%B %Y"), font=("Arial", 12, "bold")).pack(side="left", expand=True)
        ctk.CTkButton(h, text=">", width=30, fg_color="transparent", text_color="black", command=lambda: self.change_month(1)).pack(side="right")

        # Days
        d_frame = ctk.CTkFrame(self.cal_frame, fg_color="transparent")
        d_frame.pack(pady=5)
        cal = calendar.Calendar(firstweekday=0)
        days = cal.monthdayscalendar(self.current_cal_date.year, self.current_cal_date.month)
        
        for r, week in enumerate(days):
            for c, day in enumerate(week):
                if day != 0:
                    dt = datetime(self.current_cal_date.year, self.current_cal_date.month, day)
                    color = ACCENT_BLUE if dt.date() == self.selected_date.date() else "transparent"
                    fg = "white" if dt.date() == self.selected_date.date() else "black"
                    ctk.CTkButton(d_frame, text=str(day), width=30, fg_color=color, text_color=fg, hover_color=SOFT_BLUE_FRAME, command=lambda d=dt: self.select_date(d)).grid(row=r, column=c, padx=1, pady=1)

    def change_month(self, m):
        nm = self.current_cal_date.month + m
        ny = self.current_cal_date.year
        if nm > 12: nm=1; ny+=1
        elif nm < 1: nm=12; ny-=1
        self.current_cal_date = self.current_cal_date.replace(year=ny, month=nm, day=1)
        self.render_calendar()

    def select_date(self, dt):
        self.selected_date = dt
        self.btn_date.configure(text=f"📅 {dt.strftime('%d/%m/%Y')}")
        self.cal_frame.grid_forget()
        self.update_hours_for_date(dt)

    def update_hours_for_date(self, dt):
        horas = self.controller.generar_horarios_disponibles(dt)
        if not horas: horas = ["Cerrado"]
        self.combo_hora.configure(values=horas)
        # Si la hora actual seleccionada no está en la nueva lista, poner la primera
        if self.var_hora.get() not in horas:
            self.var_hora.set(horas[0])

    def _add_notes_field(self, parent, row, initial_text=""):
        ctk.CTkLabel(parent, text="Notas", font=("Arial", 14, "bold"), text_color="#333").grid(row=row, column=0, sticky="w", pady=(10, 0), padx=5)
        cont = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=1)
        cont.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.notes_textbox = ctk.CTkTextbox(cont, height=80, fg_color=WHITE_FRAME, wrap="word")
        self.notes_textbox.pack(fill="both", padx=2, pady=2)
        self.notes_textbox.insert("1.0", initial_text)

    # -----------------------------------------------
    # 4. LÓGICA GUARDAR / CANCELAR
    # -----------------------------------------------
    def save_changes(self):
        datos = {
            'doctora': self.var_doctora.get(),
            'fecha_obj': self.selected_date,
            'hora': self.var_hora.get(),
            'motivo': self.var_motivo.get(),
            'notas': self.notes_textbox.get("1.0", "end-1c")
        }
        success, msg = self.controller.guardar_modificacion(self.active_appointment_id, datos)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.perform_search() # Refrescar
        else:
            messagebox.showerror("Error", msg)

    def cancel_appointment(self):
        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de cancelar esta cita?")
        if confirm:
            success, msg = self.controller.cancelar_cita(self.active_appointment_id)
            if success:
                messagebox.showinfo("Cancelada", msg)
                # Limpiar formulario
                for w in self.edit_form_container.winfo_children(): w.destroy()
                self.initial_message = ctk.CTkLabel(self.edit_form_container, text="Cita cancelada.", text_color="red")
                self.initial_message.pack(pady=50)
            else:
                messagebox.showerror("Error", msg)

