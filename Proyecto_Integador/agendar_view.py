# agendar_view.py
import customtkinter as ctk
from PIL import Image
import os 
from agendar_controller import AgendarCitaController

# --- CONFIGURACIÓN DE COLORES Y RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
BG_COLOR = "#F0F8FF"
WHITE_FRAME = "white"
ACCENT_BLUE = "#007BFF"
SOFT_BLUE_FRAME = "#D9EFFF" 
BLUE_GRADIENT_START = "#00C6FF"

# Rutas de imágenes (usando los archivos subidos)
ICON_CALENDAR_PATH = os.path.join(current_dir, "icon_calendar.jpg") 
# Rutas reales de doctoras
DR_IMAGES = {
    "Dra. Raquel Guzmán Reyes (Ortodoncia)": os.path.join(current_dir, "doctora_1.jpg"),
    "Dra. Paola Jazmin Vera Guzmán (Endodoncia)": os.path.join(current_dir, "doctora_2.jpg"),
    "Dra. María Fernanda Cabrera (Cirugía General)": os.path.join(current_dir, "doctora_3.jpg"),
}

# Helper para cargar imagen de doctora
def load_doctor_image(name):
    path = DR_IMAGES.get(name)
    if path and os.path.exists(path):
        try:
            # Usar LUMINOSITY para evitar el color de fondo extraño de las fotos de identificación
            return ctk.CTkImage(Image.open(path).convert("RGB").resize((40, 40)), size=(40, 40))
        except Exception:
            pass
    # Fallback si falla la carga específica
    return ctk.CTkImage(Image.new("RGB", (40, 40), "#AAAAAA"), size=(40, 40)) # Imagen gris genérica


class AgendarCitaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.controller = AgendarCitaController() 

        self.content_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.content_frame.pack(fill="both", expand=True)
        self.content_frame.grid_columnconfigure(0, weight=2) 
        self.content_frame.grid_columnconfigure(1, weight=1) 
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.create_form_panel()
        self.create_card_panel()

    def create_form_panel(self):
        # Panel Izquierdo (Formulario)
        self.form_panel = ctk.CTkFrame(self.content_frame, fg_color=WHITE_FRAME, corner_radius=15, border_color=SOFT_BLUE_FRAME, border_width=1)
        self.form_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=10)
        
        # Header del formulario
        header_form = ctk.CTkFrame(self.form_panel, fg_color="transparent")
        header_form.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(header_form, text=" 📅 Agendar Nueva Cita", font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT_BLUE, anchor="w").pack(fill="x")
        ctk.CTkLabel(header_form, text="Completa el formulario para agendar tu cita", font=ctk.CTkFont(size=13), text_color="#6B6B6B", anchor="w").pack(fill="x")

        # Contenedor desplazable para los campos
        inner_form_frame = ctk.CTkScrollableFrame(self.form_panel, fg_color="transparent")
        inner_form_frame.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        inner_form_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Campos del formulario
        doctoras = self.controller.obtener_doctoras()
        
        # Nombre Completo
        self._add_form_field(inner_form_frame, "Nombre Completo *", "Ingresa tu nombre completo", 0, 0)
        
        # Edad (Implementación de validación)
        self.age_entry = self._add_form_field(inner_form_frame, "Edad *", "Tu edad", 0, 1, validate_age=True)
        
        # Tratamiento previo (Dropdown)
        self.tratamiento_previo_var = ctk.StringVar(value="Selecciona una opción")
        self._add_form_dropdown(inner_form_frame, "¿Tratamiento previo? *", ["Selecciona una opción", "Sí", "No"], 2, 0, variable=self.tratamiento_previo_var, command=self.toggle_prev_treatment)
        
        # Contenedor del campo de Tratamiento Previo (invisible por defecto)
        self.prev_treatment_frame = ctk.CTkFrame(inner_form_frame, fg_color="transparent")
        self.prev_treatment_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
        
        # Doctora
        self._add_form_dropdown(inner_form_frame, "Doctora encargada *", ["Selecciona una doctora"] + doctoras, 2, 1)
        self._add_date_time_fields(inner_form_frame, 6) # Ajuste de fila por el nuevo campo

        # Presupuesto o tratamiento
        self._add_form_field(inner_form_frame, "Presupuesto o tratamiento *", "Ej: Brackets, Limpieza, Consulta", 8, 0, columnspan=2)
        
        # Tipo de visita
        self.tipo_visita_var = ctk.StringVar(value="Presupuesto (Gratuito)")
        self._add_form_dropdown(inner_form_frame, "Tipo de visita *", ["Presupuesto (Gratuito)", "Tratamiento (Con costo)"], 10, 0, columnspan=2, variable=self.tipo_visita_var, command=self.toggle_payment_info)
        
        self.payment_info_frame = ctk.CTkFrame(inner_form_frame, fg_color="transparent")
        self.payment_info_frame.grid(row=12, column=0, columnspan=2, sticky="ew") # Fila ajustada
        
        self._add_notes_field(inner_form_frame, 12, offset=1) # Fila ajustada
        self._add_reminder_section(inner_form_frame, 14, offset=1) # Fila ajustada

    def create_card_panel(self):
        # Panel Derecho (Tarjetas)
        self.card_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.card_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=10)
        
        self._add_estimated_time_card(self.card_panel, 0)
        self._add_medical_team_card(self.card_panel, 1)
        self._add_my_appointments_card(self.card_panel, 2)
        
    # --- Métodos de Contrucción de UI y Lógica ---

    def validate_age_input(self, text):
        # Permite números y una cadena vacía (para borrar)
        if text.isdigit() or text == "":
            if text == "" or int(text) >= 0:
                return True
        return False
    
    def toggle_prev_treatment(self, choice):
        # Muestra/oculta el campo de descripción del tratamiento previo
        for widget in self.prev_treatment_frame.winfo_children():
            widget.destroy()
            
        if choice == "Sí":
            ctk.CTkLabel(self.prev_treatment_frame, text="Describe tu tratamiento previo *", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").pack(fill="x", pady=(15, 5))
            ctk.CTkEntry(
                self.prev_treatment_frame, placeholder_text="Ej: Usé Brackets por 2 años", height=35, fg_color=WHITE_FRAME, border_color="#DDDDDD", border_width=1
            ).pack(fill="x", pady=(0, 15))

    def toggle_payment_info(self, choice):
        # Muestra/oculta la sección de pago
        if choice == "Tratamiento (Con costo)":
            self._add_payment_fields(self.payment_info_frame)
        else:
            for widget in self.payment_info_frame.winfo_children():
                widget.destroy()

    def _add_payment_fields(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        payment_card = ctk.CTkFrame(parent, fg_color="#E9F5FF", corner_radius=10, border_color="#D0E8FF", border_width=1)
        payment_card.pack(fill="x", pady=(15, 10), padx=0)
        payment_card.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(payment_card, text="Información de pago del tratamiento", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333", anchor="w").grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 5))
        
        # Costo total
        ctk.CTkLabel(payment_card, text="Costo total del tratamiento *", font=ctk.CTkFont(size=12), text_color="#6B6B6B", anchor="w").grid(row=1, column=0, sticky="w", padx=(15, 10), pady=(5, 0))
        ctk.CTkEntry(payment_card, placeholder_text="Ej: 5000", height=30, fg_color="white", border_color="#DDDDDD", border_width=1).grid(row=2, column=0, sticky="ew", padx=(15, 10), pady=(0, 15))
        
        # Pago en esta sesión
        ctk.CTkLabel(payment_card, text="Pago en esta sesión *", font=ctk.CTkFont(size=12), text_color="#6B6B6B", anchor="w").grid(row=1, column=1, sticky="w", padx=(0, 15), pady=(5, 0))
        ctk.CTkEntry(payment_card, placeholder_text="Ej: 1000", height=30, fg_color="white", border_color="#DDDDDD", border_width=1).grid(row=2, column=1, sticky="ew", padx=(10, 15), pady=(0, 15))
        
        # Tratamientos Realizados
        ctk.CTkLabel(payment_card, text="Tratamientos realizados", font=ctk.CTkFont(size=12), text_color="#6B6B6B", anchor="w").grid(row=3, column=0, sticky="w", padx=15, pady=(5, 0))
        tratamientos_frame = ctk.CTkFrame(payment_card, fg_color="transparent")
        tratamientos_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 15))
        tratamientos_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(tratamientos_frame, placeholder_text="Limpieza dental, Extracción", height=30, fg_color="white", border_color="#DDDDDD", border_width=1).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(tratamientos_frame, text="Agregar", fg_color="#00C6FF", hover_color="#00AADD", width=80, height=30, font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, sticky="e")
        

    def _add_form_field(self, parent, label_text, placeholder, row, col, columnspan=1, validate_age=False):
        ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row, column=col, sticky="w", pady=(15, 5), padx=(0, 10))
        
        vcmd = (parent.register(self.validate_age_input), '%P') if validate_age else None
        
        entry = ctk.CTkEntry(
            parent, 
            placeholder_text=placeholder, 
            height=35, 
            fg_color=WHITE_FRAME, 
            border_color="#DDDDDD", 
            border_width=1,
            validate="key", 
            validatecommand=vcmd
        )
        entry.grid(row=row + 1, column=col, sticky="ew", padx=(0, 10), pady=(0, 15), columnspan=columnspan)
        
        return entry

    def _add_form_dropdown(self, parent, label_text, values, row, col, columnspan=1, variable=None, command=None):
        ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row, column=col, sticky="w", pady=(15, 5), padx=(0, 10))
        ctk.CTkOptionMenu(
            parent, values=values, height=35, fg_color=WHITE_FRAME, button_color=WHITE_FRAME, 
            button_hover_color=SOFT_BLUE_FRAME, text_color="#6B6B6B", variable=variable, command=command
        ).grid(row=row + 1, column=col, sticky="ew", padx=(0, 10), pady=(0, 15), columnspan=columnspan)

    def _add_date_time_fields(self, parent, row):
        ctk.CTkLabel(parent, text="Fecha de la cita *", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row, column=0, sticky="w", pady=(15, 5))
        
        # Campo Fecha
        date_frame = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color="#DDDDDD", border_width=1, corner_radius=6, height=35)
        date_frame.grid(row=row + 1, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))

        try:
            icon_calendar = ctk.CTkImage(Image.open(ICON_CALENDAR_PATH).resize((18, 18)), size=(18, 18))
            ctk.CTkLabel(date_frame, text="", image=icon_calendar).pack(side="left", padx=(10, 5))
        except:
            ctk.CTkLabel(date_frame, text="📅", font=ctk.CTkFont(size=16)).pack(side="left", padx=(10, 5))
            
        ctk.CTkButton(date_frame, text="Seleccionar fecha", fg_color=WHITE_FRAME, hover_color=SOFT_BLUE_FRAME, text_color="#6B6B6B", font=ctk.CTkFont(size=14, weight="normal"), width=200).pack(side="left", expand=True, fill="x", pady=0)

        # Campo Hora
        ctk.CTkLabel(parent, text="Hora de entrada *", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row, column=1, sticky="w", pady=(15, 5))
        ctk.CTkOptionMenu(
            parent, values=["Seleccionar hora"], height=35, fg_color=WHITE_FRAME, button_color=WHITE_FRAME, 
            button_hover_color=SOFT_BLUE_FRAME, text_color="#6B6B6B"
        ).grid(row=row + 1, column=1, sticky="ew", padx=(0, 10), pady=(0, 15))

    def _add_notes_field(self, parent, row, offset=0):
        ctk.CTkLabel(parent, text="Notas adicionales", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row + offset, column=0, columnspan=2, sticky="w", pady=(15, 5))
        
        # Contenedor de Textbox para simular placeholder
        notes_container = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color="#DDDDDD", border_width=1, corner_radius=6)
        notes_container.grid(row=row + 1 + offset, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        notes_container.grid_columnconfigure(0, weight=1)
        notes_container.grid_rowconfigure(0, weight=1)
        
        self.notes_textbox = ctk.CTkTextbox(notes_container, height=80, fg_color=WHITE_FRAME, wrap="word")
        self.notes_textbox.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        # Placeholder Label
        self.placeholder_label = ctk.CTkLabel(
            notes_container, 
            text="Información adicional sobre la cita...", 
            text_color="#AAAAAA", 
            font=ctk.CTkFont(size=14, slant="italic"),
            anchor="nw"
        )
        self.placeholder_label.place(x=10, y=10)
        
        # Eventos para ocultar/mostrar placeholder
        self.notes_textbox.bind("<FocusIn>", self._hide_placeholder)
        self.notes_textbox.bind("<FocusOut>", self._check_placeholder)

    def _hide_placeholder(self, event):
        self.placeholder_label.place_forget()

    def _check_placeholder(self, event):
        if not self.notes_textbox.get("1.0", "end-1c").strip():
            self.placeholder_label.place(x=10, y=10)

    def _add_reminder_section(self, parent, row, offset=0):
        # Frame de Recordatorio (switch)
        reminder_toggle_frame = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=10, border_color="#DDDDDD", border_width=1)
        reminder_toggle_frame.grid(row=row + offset, column=0, columnspan=2, sticky="ew", pady=(20, 10), padx=0)
        reminder_toggle_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(reminder_toggle_frame, text=" 🔔 Recordatorio de cita\nRecibe notificación antes de tu cita", font=ctk.CTkFont(size=14), text_color="#333333", anchor="w", justify="left").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        self.reminder_switch = ctk.CTkSwitch(
            reminder_toggle_frame, text="", width=35, height=20, fg_color="#AAAAAA", progress_color=ACCENT_BLUE,
            command=self.toggle_contact_info
        )
        self.reminder_switch.grid(row=0, column=1, sticky="e", padx=20, pady=10)
        
        self.contact_info_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.contact_info_container.grid(row=row + 1 + offset, column=0, columnspan=2, sticky="ew")

        # Botón Agendar Cita
        ctk.CTkButton(parent, text=" 🕒 Agendar Cita", height=45, corner_radius=10, fg_color=ACCENT_BLUE, hover_color="#3A82D0", font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=row + 2 + offset, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def toggle_contact_info(self):
        # Muestra/Oculta la sección de contacto
        if self.reminder_switch.get() == 1:
            self._add_contact_fields(self.contact_info_container)
        else:
            for widget in self.contact_info_container.winfo_children():
                widget.destroy()

    def _add_contact_fields(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        contact_info_card = ctk.CTkFrame(parent, fg_color="#E9F5FF", corner_radius=10, border_color="#D0E8FF", border_width=1)
        contact_info_card.pack(fill="x", pady=(0, 15), padx=0)
        contact_info_card.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(contact_info_card, text="Información de contacto para recordatorio *", font=ctk.CTkFont(size=13, weight="bold"), text_color="#333333").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 0))
        
        # Teléfono
        ctk.CTkLabel(contact_info_card, text="Teléfono *", font=ctk.CTkFont(size=13, weight="bold"), text_color="#333333").grid(row=1, column=0, sticky="w", padx=(20, 10), pady=(10, 0))
        ctk.CTkEntry(contact_info_card, placeholder_text="Ej: 3331234567", height=30, border_width=1, border_color="#DDDDDD", fg_color="white").grid(row=2, column=0, sticky="ew", padx=(20, 10), pady=(0, 10))
        
        # Correo Electrónico
        ctk.CTkLabel(contact_info_card, text="Correo Electrónico *", font=ctk.CTkFont(size=13, weight="bold"), text_color="#333333").grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(10, 0))
        ctk.CTkEntry(contact_info_card, placeholder_text="ejemplo@correo.com", height=30, border_width=1, border_color="#DDDDDD", fg_color="white").grid(row=2, column=1, sticky="ew", padx=(0, 20), pady=(0, 10))


    def _add_estimated_time_card(self, parent, row):
        # Simulación del gradiente azul intenso
        card = ctk.CTkFrame(parent, corner_radius=15, fg_color=BLUE_GRADIENT_START) 
        card.grid(row=row, column=0, sticky="ew", pady=(10, 20))
        card.grid_columnconfigure(0, weight=1)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content, text="Tiempo de atención estimado", font=ctk.CTkFont(size=13), text_color="white", anchor="w").pack(fill="x")
        ctk.CTkLabel(content, text="30 minutos", font=ctk.CTkFont(size=28, weight="bold"), text_color="white", anchor="w").pack(fill="x")
        ctk.CTkLabel(content, text="🕒", font=ctk.CTkFont(size=30), text_color="white").place(relx=0.9, rely=0.5, anchor="e")


    def _add_medical_team_card(self, parent, row):
        card = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=15, border_color="#DDDDDD", border_width=1)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(card, text=" ⚕️ Nuestro Equipo Médico", font=ctk.CTkFont(size=15, weight="bold"), text_color=ACCENT_BLUE, anchor="w").pack(fill="x", padx=15, pady=(15, 10))
        
        # Obtener la lista de doctoras completa (nombre y especialidad)
        doctoras = self.controller.obtener_doctoras()
        
        for doc_info in doctoras:
            name, specialty = doc_info.split(" (")
            specialty = specialty.replace(")", "")
            self._add_doctor_info(card, name, specialty)

    def _add_doctor_info(self, parent, name, specialty):
        doctor_frame = ctk.CTkFrame(parent, fg_color="transparent")
        doctor_frame.pack(fill="x", padx=15, pady=5)
        
        full_name = f"{name} ({specialty})" # Usar el nombre completo para la búsqueda en el diccionario
        dr_img = load_doctor_image(full_name) 
        if dr_img:
            ctk.CTkLabel(doctor_frame, text="", image=dr_img).pack(side="left", padx=(0, 10))
        else:
            ctk.CTkLabel(doctor_frame, text="👩‍⚕️", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        
        info_frame = ctk.CTkFrame(doctor_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="y")
        ctk.CTkLabel(info_frame, text=name, font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").pack(fill="x")
        ctk.CTkLabel(info_frame, text=specialty, font=ctk.CTkFont(size=12), anchor="w", text_color=ACCENT_BLUE).pack(fill="x")

    def _add_my_appointments_card(self, parent, row):
        card = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, corner_radius=15, border_color="#DDDDDD", border_width=1)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(card, text=" 🗓️ Mis Citas (0)", font=ctk.CTkFont(size=15, weight="bold"), text_color=ACCENT_BLUE, anchor="w").pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(card, text="Citas programadas", font=ctk.CTkFont(size=13), text_color="#6B6B6B", anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        # Placeholder de No hay citas
        no_citas_frame = ctk.CTkFrame(card, fg_color=SOFT_BLUE_FRAME, corner_radius=10)
        no_citas_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        ctk.CTkLabel(no_citas_frame, text="🗓️", font=ctk.CTkFont(size=50), text_color=ACCENT_BLUE).pack(pady=(20, 5))
        ctk.CTkLabel(no_citas_frame, text="No hay citas programadas", font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").pack()
        ctk.CTkLabel(no_citas_frame, text="¡Agenda tu primera cita!", font=ctk.CTkFont(size=12, slant="italic"), text_color="#6B6B6B").pack(pady=(0, 20))
        