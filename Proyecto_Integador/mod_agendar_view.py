import customtkinter as ctk
from tkinter import messagebox 
from datetime import datetime
from mod_agendar_controller import ModificarCitaController 
from typing import List, Dict, Any, Union

# --- CONFIGURACIÓN DE COLORES (Mantenida) ---
BG_COLOR = "#F0F8FF"
WHITE_FRAME = "white"
ACCENT_BLUE = "#007BFF"
SOFT_BLUE_FRAME = "#D9EFFF"
VISIBLE_BORDER = "#C8CDD6"
DEFAULT_BORDER_WIDTH = 1
# ... (Otras configuraciones de color e imagen si son necesarias)

class ModificarCitaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_COLOR)
        self.master = master
        self.controller = ModificarCitaController() # Instancia del nuevo controlador
        self.active_appointment_id = None
        
        main_card = ctk.CTkFrame(self, fg_color=WHITE_FRAME, corner_radius=15, border_color=VISIBLE_BORDER, border_width=1)
        main_card.pack(fill="both", expand=True, padx=5, pady=10) 
        
        main_card.grid_columnconfigure(0, weight=1)
        main_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(main_card, text="✏️ Modificación y Reagendamiento de Citas", 
                      font=ctk.CTkFont(size=20, weight="bold"), 
                      text_color=ACCENT_BLUE, 
                      compound="left", 
                      anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        self.content_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)
        
        # Diccionario para almacenar las variables del formulario
        self.form_vars = {} # Almacenará variables como self.form_vars['nombre_completo']
        self.form_entries = {} # Almacenará referencias a los widgets de entrada

        self.create_search_panel(self.content_frame, row=0)
        
        # El contenedor del formulario se crea vacío y se llena al seleccionar una cita
        self.edit_form_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.edit_form_container.grid(row=1, column=0, sticky="nsew")
        
        # Opcional: Mostrar un mensaje inicial
        self.initial_message = ctk.CTkLabel(self.edit_form_container, text="Use la barra de búsqueda para encontrar una cita a modificar.", text_color="#6B6B6B", font=ctk.CTkFont(size=14, slant="italic"))
        self.initial_message.pack(pady=50)

    # -----------------------------------------------
    # 1. Lógica de Búsqueda Flexible
    # -----------------------------------------------
    def create_search_panel(self, parent, row):
        # ... (El código de create_search_panel es el mismo que el anterior, solo se ajusta la llamada a perform_search)
        search_card = ctk.CTkFrame(parent, fg_color=SOFT_BLUE_FRAME, corner_radius=10, border_color=ACCENT_BLUE, border_width=1)
        search_card.grid(row=row, column=0, sticky="ew", pady=(0, 15))
        search_card.grid_columnconfigure(0, weight=1)
        search_card.grid_columnconfigure(1, weight=0)
        
        self.search_entry = ctk.CTkEntry(
            search_card, 
            placeholder_text="Buscar paciente por nombre o teléfono (ej: 'Juana' o '871555')",
            font=ctk.CTkFont(size=14),
            fg_color=WHITE_FRAME,
            border_color="#DDDDDD",
            border_width=1,
            corner_radius=8
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        
        # Al soltar una tecla se llama a perform_search
        self.search_entry.bind("<KeyRelease>", self.perform_search)
        
        ctk.CTkButton(
            search_card, 
            text="🔍 Buscar", 
            command=self.perform_search, # Se llama a perform_search sin KeyRelease
            fg_color=ACCENT_BLUE, 
            hover_color="#3A82D0", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            corner_radius=8,
            width=100
        ).grid(row=0, column=1, sticky="e", padx=(0, 15), pady=15)
        
        self.results_dropdown = ctk.CTkOptionMenu(
            search_card,
            values=["No hay resultados"],
            command=self.select_patient_from_search,
            fg_color=WHITE_FRAME,
            button_color=WHITE_FRAME,
            button_hover_color="#F0F0F0",
            text_color="#333333",
            font=ctk.CTkFont(size=13),
            dynamic_resizing=False,
            dropdown_fg_color=WHITE_FRAME, 
            dropdown_text_color="#333333"
        )
        self.results_dropdown.set("Escriba para buscar una cita")
        self.results_dropdown.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 15))
        self.last_search_results = {}
        
    def perform_search(self, event=None):
        query = self.search_entry.get().strip()
        
        # La lógica de filtrado está en el controlador
        resultados = self.controller.buscar_citas_flexibles(query)
        
        self.last_search_results = {}
        dropdown_values = ["Seleccione una cita..."]
        
        if not resultados:
            dropdown_values = ["No se encontraron citas"]
            self.results_dropdown.set(dropdown_values[0])
            self.results_dropdown.configure(values=dropdown_values)
            return

        for cita in resultados:
            # Almacenamos el ID para poder recuperarlo después de la selección
            self.last_search_results[cita['display']] = cita['id']
            dropdown_values.append(cita['display'])
            
        self.results_dropdown.configure(values=dropdown_values)
        self.results_dropdown.set(f"Se encontraron {len(resultados)} resultados")


    def select_patient_from_search(self, display_text: str):
        """Maneja la selección de un resultado y carga los datos en el formulario."""
        if display_text not in self.last_search_results:
            return

        cita_id = self.last_search_results[display_text]
        cita_data = self.controller.obtener_datos_cita(cita_id)

        if cita_data:
            self.active_appointment_id = cita_id
            self.load_form_fields(cita_data)
        else:
            messagebox.showerror("Error", "No se pudieron cargar los datos de la cita.")
            
    # -----------------------------------------------
    # 2. Reutilización del Formulario de Agendar
    # -----------------------------------------------
    def load_form_fields(self, cita_data: Union[Dict[str, Any], None]):
        """
        Destruye el contenido anterior y reutiliza la estructura de AgendarCitaFrame
        para cargar los campos con los datos de la cita.
        """
        # Destruir widgets antiguos (y mensaje inicial)
        for widget in self.edit_form_container.winfo_children():
            widget.destroy()
            
        # El código del formulario reutilizado va aquí
        scroll_wrapper = ctk.CTkFrame(self.edit_form_container, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=8)
        scroll_wrapper.pack(fill="both", expand=True, padx=0, pady=0)
        
        inner_form_frame = ctk.CTkScrollableFrame(scroll_wrapper, fg_color="transparent")
        inner_form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        inner_form_frame.grid_columnconfigure((0, 1), weight=1)
        
        # --- CAMPOS REUTILIZADOS Y CARGA DE DATOS ---
        doctoras = self.controller.obtener_doctoras()
        
        # 1. Nombre Completo
        self.form_vars['nombre_completo'] = ctk.StringVar(value=cita_data.get('nombre_completo', ''))
        self.form_entries['nombre'] = self._add_form_field(inner_form_frame, "Nombre Completo *", "Ingresa tu nombre completo", 0, 0, var=self.form_vars['nombre_completo'])
        
        # 2. Doctora (Se carga la asignada)
        self.form_vars['doctora'] = ctk.StringVar(value=cita_data.get('doctora', "Selecciona una doctora"))
        self._add_form_dropdown(inner_form_frame, "Doctora encargada *", ["Selecciona una doctora"] + doctoras, 0, 1, variable=self.form_vars['doctora'])
        
        # 3. Fecha y Hora (Se cargan los valores actuales)
        self._add_date_time_fields(inner_form_frame, 2, cita_data.get('fecha_cita'), cita_data.get('hora_cita')) 

        # 4. Tratamiento/Presupuesto
        self.form_vars['tratamiento'] = ctk.StringVar(value=cita_data.get('tratamiento', ''))
        self.form_entries['tratamiento'] = self._add_form_field(inner_form_frame, "Presupuesto o tratamiento *", "Ej: Brackets, Limpieza, Consulta", 4, 0, columnspan=2, var=self.form_vars['tratamiento'])
        
        # 5. Costo de Sesión (Usado como 'pago en esta sesión')
        self.form_vars['costo_sesion'] = ctk.StringVar(value=cita_data.get('costo_sesion', '0.00'))
        self.form_entries['costo'] = self._add_form_field(inner_form_frame, "Costo de esta sesión *", "Ej: 800.00", 6, 0, var=self.form_vars['costo_sesion'])

        # 6. Notas
        self._add_notes_field(inner_form_frame, 8) 
        # Cargar nota en el Textbox (se requiere un método especial si usa un placeholder)
        self.notes_textbox.delete("1.0", "end")
        self.notes_textbox.insert("1.0", cita_data.get('nota', ''))
        self._check_placeholder(None) # Asegurar que el placeholder se oculte/muestre correctamente

        # Botón de Modificación
        ctk.CTkButton(inner_form_frame, text=f"✅ Modificar Cita #{cita_data['id']}", height=45, corner_radius=10, 
                      fg_color="#4CAF50", hover_color="#388E3C", font=ctk.CTkFont(size=16, weight="bold"),
                      command=lambda: self.save_modification(cita_data['id'])
        ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(20, 10))

        ctk.CTkButton(inner_form_frame, text=f"❌ Cancelar Cita #{cita_data['id']}", height=35, corner_radius=10, 
                      fg_color="#D32F2F", hover_color="#B71C1C", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(0, 10))

    # -----------------------------------------------
    # 3. MÉTODOS AUXILIARES REQUERIDOS (DEBEN EXISTIR EN AMBAS VISTAS)
    # -----------------------------------------------
    
    # *** Aquí irían los métodos de _add_form_field, _add_form_dropdown, _add_date_time_fields, etc.
    #     Puedes copiar y pegar de agendar_view.py, simplificando el _add_date_time_fields 
    #     para aceptar valores iniciales (date_value y time_value).

    def _add_form_field(self, parent, label_text, placeholder, row, col, columnspan=1, var=None):
        ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row, column=col, sticky="w", pady=(15, 5), padx=(0, 10))
        entry = ctk.CTkEntry(
            parent, 
            placeholder_text=placeholder, 
            height=35, 
            fg_color=WHITE_FRAME, 
            border_color=VISIBLE_BORDER, 
            border_width=DEFAULT_BORDER_WIDTH,
            textvariable=var # Vinculación con la variable de control
        )
        entry.grid(row=row + 1, column=col, sticky="ew", padx=(0, 10), pady=(0, 15), columnspan=columnspan)
        return entry
    
    def _add_form_dropdown(self, parent, label_text, values, row, col, columnspan=1, variable=None, command=None):
        ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row, column=col, sticky="w", pady=(15, 5), padx=(0, 10))
        wrapper = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=6)
        wrapper.grid(row=row + 1, column=col, sticky="ew", padx=(0, 10), pady=(0, 15), columnspan=columnspan)
        ctk.CTkOptionMenu(
        wrapper, values=values, height=35, fg_color=WHITE_FRAME, button_color=WHITE_FRAME, 
        button_hover_color=SOFT_BLUE_FRAME, text_color="#6B6B6B", variable=variable, command=command
        ).pack(fill="both", expand=True, padx=6, pady=2)

    def _add_date_time_fields(self, parent, row, date_value="Seleccionar fecha", time_value="Seleccionar hora"):
        # Campo Fecha
        ctk.CTkLabel(parent, text="Fecha de la cita *", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row, column=0, sticky="w", pady=(15, 5))
        date_frame = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=6, height=35)
        date_frame.grid(row=row + 1, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))
        date_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(date_frame, text="📅", font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=(10, 5), pady=0, sticky="w")
        ctk.CTkButton(
            date_frame, text=date_value, 
            fg_color=WHITE_FRAME, hover_color=SOFT_BLUE_FRAME, 
            text_color="#6B6B6B", font=ctk.CTkFont(size=14, weight="normal"), 
            width=1, height=33
        ).grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=1)

        # Campo Hora
        ctk.CTkLabel(parent, text="Hora de entrada *", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row, column=1, sticky="w", pady=(15, 5))
        time_wrapper = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=6)
        time_wrapper.grid(row=row + 1, column=1, sticky="ew", padx=(0, 10), pady=(0, 15))
        ctk.CTkOptionMenu(
            time_wrapper, values=[time_value], height=35, fg_color=WHITE_FRAME, button_color=WHITE_FRAME, 
            button_hover_color=SOFT_BLUE_FRAME, text_color="#6B6B6B"
        ).pack(fill="both", expand=True, padx=6, pady=2)
        
    def _add_notes_field(self, parent, row, offset=0):
        # Implementación de Notas (similar a agendar_view.py, asegurando self.notes_textbox y self.placeholder_label)
        ctk.CTkLabel(parent, text="Notas adicionales", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="#333333").grid(row=row + offset, column=0, columnspan=2, sticky="w", pady=(15, 5))
        notes_container = ctk.CTkFrame(parent, fg_color=WHITE_FRAME, border_color=VISIBLE_BORDER, border_width=DEFAULT_BORDER_WIDTH, corner_radius=6)
        notes_container.grid(row=row + 1 + offset, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        notes_container.grid_columnconfigure(0, weight=1)
        notes_container.grid_rowconfigure(0, weight=1)
        self.notes_textbox = ctk.CTkTextbox(notes_container, height=80, fg_color=WHITE_FRAME, wrap="word")
        self.notes_textbox.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        self.placeholder_label = ctk.CTkLabel(notes_container, text="Información adicional sobre la cita...", text_color="#AAAAAA", font=ctk.CTkFont(size=14, slant="italic"), anchor="nw")
        self.placeholder_label.place(x=10, y=10)
        self.notes_textbox.bind("<FocusIn>", self._hide_placeholder)
        self.notes_textbox.bind("<FocusOut>", self._check_placeholder)
        
    def _hide_placeholder(self, event):
        self.placeholder_label.place_forget()

    def _check_placeholder(self, event):
        if not self.notes_textbox.get("1.0", "end-1c").strip():
            self.placeholder_label.place(x=10, y=10)
            
    # -----------------------------------------------
    # 4. Lógica de Guardado (Ejemplo)
    # -----------------------------------------------
    def save_modification(self, cita_id: int):
        """Recupera los datos de las variables y simula la actualización."""
        
        # Recuperar datos de las variables (ejemplo)
        nuevo_nombre = self.form_vars['nombre_completo'].get()
        nueva_doctora = self.form_vars['doctora'].get()
        nueva_nota = self.notes_textbox.get("1.0", "end-1c").strip()
        
        # Validación de ejemplo
        if not nuevo_nombre or nueva_doctora == "Selecciona una doctora":
            messagebox.showwarning("Faltan datos", "El nombre y la doctora son obligatorios.")
            return

        # SIMULACIÓN: Actualizar DB
        print(f"Modificando cita ID {cita_id}:")
        print(f"  Nombre: {nuevo_nombre}")
        print(f"  Doctora: {nueva_doctora}")
        print(f"  Nota: {nueva_nota}")
        
        messagebox.showinfo("Éxito", f"Cita ID {cita_id} modificada con éxito.")
