import customtkinter as ctk
from PIL import Image
import os 
from datetime import datetime, timedelta
from tkinter import messagebox
import calendar
from agendar_controller import AgendarCitaController

# Configuración Estética
BG_MAIN = "#F4F6F9"
WHITE_CARD = "#FFFFFF"
TEXT_DARK = "#333333"
ACCENT_BLUE = "#007BFF"
SOFT_BLUE_BTN = "#89CFF0" 
BORDER_COLOR = "#E0E0E0"
HEADER_CALENDAR = "#E8F0FE"
SUCCESS_COLOR = "#28A745"
WARNING_COLOR = "#FFC107"
DANGER_COLOR = "#DC3545"
INFO_COLOR = "#17A2B8"

current_dir = os.path.dirname(os.path.abspath(__file__))

class AgendarCitaFrame(ctk.CTkFrame):
    
    def __init__(self, master):
        super().__init__(master, fg_color=BG_MAIN)
        self.controller = AgendarCitaController()
        
        self.servicios_agregados = []
        self.selected_date = None           
        self.display_date = datetime.now()  
        self.cliente_existente_id = None 
        self.mapa_pacientes_temp = {}
        
        # Mapa para guardar los horarios divididos (Hora -> Lista Minutos)
        self.mapa_horarios = {}

        self.grid_columnconfigure(0, weight=6) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # Panel Izq
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

        # Panel Der
        self.sidebar = ctk.CTkFrame(self, fg_color="transparent", width=250)
        self.sidebar.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.create_sidebar()

    def create_form(self):
        parent = self.scroll
        for w in parent.winfo_children(): w.destroy()
        
        c = ctk.CTkFrame(parent, fg_color="transparent")
        c.pack(fill="x", expand=True, padx=5, pady=2)
        c.grid_columnconfigure((0, 1), weight=1)

        r = 0 
        ctk.CTkLabel(c, text="📅 Nueva Cita", font=("Segoe UI", 22, "bold"), text_color=ACCENT_BLUE).grid(row=r, column=0, columnspan=2, sticky="w", pady=(0, 5)); r+=1

        self.modo_var = ctk.StringVar(value="Nuevo Paciente")
        self.seg = ctk.CTkSegmentedButton(c, values=["Nuevo Paciente", "Paciente Existente"], variable=self.modo_var, command=self.cambiar_modo, selected_color=ACCENT_BLUE)
        self.seg.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5)); r+=1

        self.frame_bus = ctk.CTkFrame(c, fg_color="#E3F2FD", corner_radius=8, border_color=ACCENT_BLUE, border_width=1)
        self.frame_bus.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
        self.frame_bus.grid_columnconfigure(0, weight=1)
        self.frame_bus.grid_remove()
        
        self.ent_bus = ctk.CTkEntry(self.frame_bus, placeholder_text="🔍 Buscar nombre/teléfono...")
        self.ent_bus.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.ent_bus.bind("<KeyRelease>", self.filtrar_pac)
        self.lst_res = ctk.CTkOptionMenu(self.frame_bus, values=["Escribe..."], command=self.selec_pac, fg_color="white", text_color="#333", button_color="#CCC")
        self.lst_res.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        r+=1 

        self._title(c, "INFORMACIÓN PERSONAL", r); r+=1
        self.ent_nom = ctk.CTkEntry(c, placeholder_text="Nombre Completo *", height=35, border_color=BORDER_COLOR, fg_color="#FAFAFA")
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
        
        # 1. SELECTOR HORA (DIVIDIDO: HORA | MINUTO)
        ctk.CTkLabel(frm_tm, text="1. Hora de Inicio", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0,2))
        
        frm_reloj = ctk.CTkFrame(frm_tm, fg_color="transparent")
        frm_reloj.pack(fill="x", pady=(0, 10))
        
        # Hora (Ej. 11 AM)
        self.cmb_h = ctk.CTkOptionMenu(frm_reloj, values=["--"], width=95, command=self.al_seleccionar_hora_h, fg_color="#E8F0FE", text_color="black")
        self.cmb_h.pack(side="left", padx=(0, 5))
        
        # Minuto (Ej. 05, 10)
        self.cmb_m = ctk.CTkOptionMenu(frm_reloj, values=["--"], width=95, command=self.al_seleccionar_min_m, fg_color="#E8F0FE", text_color="black")
        self.cmb_m.pack(side="left")
        
        # 2. Duración (SLIDER)
        ctk.CTkLabel(frm_tm, text="2. Duración Estimada", font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", pady=(0,2))
        self.lbl_dur_val = ctk.CTkLabel(frm_tm, text="30 min", font=("Arial", 13, "bold"), text_color=ACCENT_BLUE)
        self.lbl_dur_val.pack(anchor="w")
        
        self.slider_dur = ctk.CTkSlider(frm_tm, from_=5, to=300, number_of_steps=59, command=self.actualizar_slider)
        self.slider_dur.set(30)
        self.slider_dur.pack(fill="x", pady=(0, 5))
        
        # 3. Finaliza
        self.lbl_fin_hora = ctk.CTkLabel(frm_tm, text="Finaliza a las: --:--", font=("Arial", 11), text_color="#555")
        self.lbl_fin_hora.pack(anchor="w", pady=(5,0))
        r+=1

        self._sep(c, r); r+=1

        self._title(c, "DETALLES", r); r+=1
        self.tipo_var = ctk.StringVar(value="Presupuesto")
        ctk.CTkSegmentedButton(c, values=["Presupuesto (Gratuito)", "Tratamiento"], variable=self.tipo_var, command=self.toggle_serv, selected_color=ACCENT_BLUE).grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5)); r+=1
        
        self.frm_serv = ctk.CTkFrame(c, fg_color="#FAFAFA", border_color="#EEE", border_width=1)
        self.frm_serv.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10)
        self.frm_serv.grid_remove() 
        
        ctk.CTkButton(self.frm_serv, text="+ Agregar Servicio", fg_color="transparent", border_color=ACCENT_BLUE, border_width=1, text_color=ACCENT_BLUE, command=self.abrir_servicios).pack(fill="x", padx=10, pady=5)
        self.lst_serv = ctk.CTkFrame(self.frm_serv, fg_color="transparent")
        self.lst_serv.pack(fill="x", padx=10, pady=5)
        self.lbl_tot = ctk.CTkLabel(self.frm_serv, text="Total: $0.00", font=("Arial", 12, "bold"), text_color=SUCCESS_COLOR)
        self.lbl_tot.pack(anchor="e", padx=10, pady=5)
        r+=1

        self._sep(c, r); r+=1
        r = self.create_contact(c, r)
        self._sep(c, r); r+=1

        self._title(c, "ADICIONALES", r); r+=1
        self.frm_nota = ctk.CTkFrame(c, fg_color="#FAFAFA", border_color="#CCC", border_width=1, corner_radius=6)
        self.frm_nota.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
        self.frm_nota.grid_columnconfigure(0, weight=1); self.frm_nota.grid_rowconfigure(0, weight=1)
        self.txt_nota = ctk.CTkTextbox(self.frm_nota, height=60, fg_color="#FAFAFA", wrap="word", font=("Segoe UI", 12))
        self.txt_nota.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.lbl_ph = ctk.CTkLabel(self.txt_nota, text="Notas importantes...", text_color="#999", font=("Segoe UI", 12, "italic"))
        self.lbl_ph.place(x=5, y=5)
        self.txt_nota.bind("<FocusIn>", lambda e: self.lbl_ph.place_forget())
        self.txt_nota.bind("<FocusOut>", self.chk_ph)

    # --- LÓGICA DE TIEMPO Y SLIDER ---
    def act_horarios(self):
        """Llena los combos divididos buscando 5 en 5 min."""
        doc = self.cmb_doc.get()
        if not self.selected_date or "Selecciona" in doc: return
        
        raw_slots = self.controller.obtener_horas_inicio_disponibles(self.selected_date, doc)
        self.mapa_horarios = {}
        
        if not raw_slots:
            self.cmb_h.configure(values=["Lleno"]); self.cmb_h.set("Lleno")
            self.cmb_m.configure(values=["--"]); self.cmb_m.set("--")
            return

        # Parsear lista: "11:05 AM" -> H="11 AM", M="05"
        for slot in raw_slots:
            parts = slot.split(":") 
            hora_num = parts[0]
            resto = parts[1].split(" ")
            minu = resto[0]
            ampm = resto[1]
            
            k = f"{hora_num} {ampm}"
            if k not in self.mapa_horarios: self.mapa_horarios[k] = []
            self.mapa_horarios[k].append(minu)

        # Llenar Combo Horas
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
            # Reconstruir "11:05 AM"
            parts = h_txt.split(" ")
            full_str = f"{parts[0]}:{m_txt} {parts[1]}"
            inicio = datetime.strptime(full_str, "%I:%M %p")
            dur = int(self.slider_dur.get())
            fin = inicio + timedelta(minutes=dur)
            self.lbl_fin_hora.configure(text=f"Finaliza: {fin.strftime('%I:%M %p').lstrip('0').replace(' 0',' ')}")
        except: 
            self.lbl_fin_hora.configure(text="Finaliza: --:--")

    # --- HELPERS RESTANTES ---
    def al_cambiar_doc(self, _):
        if "Selecciona" in self.cmb_doc.get(): 
            self.cmb_h.set("--"); self.cmb_m.set("--")
        elif not self.selected_date: 
            pass # Espera fecha
        else: self.act_horarios()

    def _sep(self, p, r): ctk.CTkFrame(p, height=1, fg_color="#E0E0E0").grid(row=r, column=0, columnspan=2, sticky="ew", pady=(8, 0), padx=10)
    def _title(self, p, t, r): ctk.CTkLabel(p, text=t, font=("Segoe UI", 11, "bold"), text_color="#999").grid(row=r, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 2))
    
    def create_contact(self, p, r):
        self._title(p, "CONTACTO Y NOTIFICACIONES", r); r+=1
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.grid(row=r, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5)); r+=1
        f.grid_columnconfigure((0,1), weight=1)
        self.ent_tel = ctk.CTkEntry(f, placeholder_text="Teléfono (WhatsApp) *", fg_color="#FAFAFA", border_color="#CCC")
        self.ent_tel.grid(row=0, column=0, sticky="ew", padx=(0,5))
        self.ent_email = ctk.CTkEntry(f, placeholder_text="Email (Opcional)", fg_color="#FAFAFA", border_color="#CCC")
        self.ent_email.grid(row=0, column=1, sticky="ew", padx=(5,0))
        self.var_notif = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(p, text="Recordatorios activos", variable=self.var_notif, progress_color=SUCCESS_COLOR).grid(row=r, column=0, columnspan=2, sticky="w", padx=20, pady=5); r+=1
        return r
    
    def chk_ph(self, e): 
        if not self.txt_nota.get("1.0", "end-1c").strip(): self.lbl_ph.place(x=5, y=5)

    def create_buttons(self):
        for w in self.bottom_frame.winfo_children(): w.destroy()
        ctk.CTkButton(self.bottom_frame, text="🔄 Limpiar", font=("Segoe UI", 12, "bold"), fg_color=SOFT_BLUE_BTN, hover_color="#76BEE0", width=80, height=50, command=self.reset).pack(side="left", padx=(25,5), pady=10)
        ctk.CTkButton(self.bottom_frame, text="CONFIRMAR CITA", font=("Segoe UI", 15, "bold"), fg_color=ACCENT_BLUE, hover_color="#0056b3", height=50, command=self.guardar).pack(side="left", fill="x", expand=True, padx=(5,25), pady=10)

    # --- LÓGICA GENERAL ---
    def cambiar_modo(self, m):
        if m == "Paciente Existente":
            self.frame_bus.grid()
            self.ent_nom.configure(placeholder_text="Busca arriba para rellenar...")
        else:
            self.frame_bus.grid_remove()
            self.limpiar_per(); self.cliente_existente_id = None
            self.ent_nom.configure(state="normal", placeholder_text="Nombre Completo *")

    def filtrar_pac(self, e):
        q = self.ent_bus.get()
        if len(q) < 3: return
        res = self.controller.buscar_pacientes_existentes(q)
        self.mapa_pacientes_temp = {f"{r['nombre_completo']} ({r['telefono']})": r for r in res}
        vals = list(self.mapa_pacientes_temp.keys()) or ["Sin resultados"]
        self.lst_res.configure(values=vals); self.lst_res.set("Seleccionar...")

    def selec_pac(self, s):
        d = self.mapa_pacientes_temp.get(s)
        if d:
            self.cliente_existente_id = d['id']
            self.ent_nom.delete(0, 'end'); self.ent_nom.insert(0, d['nombre_completo'])
            self.ent_tel.delete(0, 'end'); self.ent_tel.insert(0, d['telefono'] or "")
            self.ent_email.delete(0, 'end'); self.ent_email.insert(0, d['email'] or "")
            if d['rango_edad']: self.cmb_edad.set(d['rango_edad'])
            if d['genero']: self.cmb_gen.set("Masculino" if d['genero']=='m' else "Femenino")

    def guardar(self):
        try:
            nota = self.txt_nota.get("1.0", "end-1c").strip()
            errs = []
            if not self.ent_nom.get().strip(): errs.append("• Nombre del Paciente")
            if self.cmb_edad.get() == "Edad": errs.append("• Edad") 
            if self.cmb_gen.get() == "Género": errs.append("• Género") 
            if "Selecciona" in self.cmb_doc.get(): errs.append("• Doctora")
            if not self.selected_date: errs.append("• Fecha")
            if "Lleno" in self.cmb_h.get() or "--" in self.cmb_m.get(): errs.append("• Hora")
            
            if errs: 
                messagebox.showwarning("Datos Incompletos", "Por favor corrige:\n\n" + "\n".join(errs))
                return

            gen = {"Masculino": "m", "Femenino": "f"}.get(self.cmb_gen.get(), "f")
            
            # Reconstruir Hora
            h_sel = self.cmb_h.get().split(" ") # ["11", "AM"]
            m_sel = self.cmb_m.get()
            hora_final_str = f"{h_sel[0]}:{m_sel} {h_sel[1]}"

            dur_txt = self.lbl_dur_val.cget("text")
            
            datos = {
                'cliente_id_existente': self.cliente_existente_id,
                'nombre': self.ent_nom.get().strip(),
                'genero': gen, 'edad': self.cmb_edad.get(),
                'telefono': self.ent_tel.get().strip(), 'email': self.ent_email.get().strip(),
                'descripcion': nota, 'doctora': self.cmb_doc.get(),
                'fecha': self.selected_date.strftime("%Y-%m-%d"),
                'hora_inicio': hora_final_str, # Enviamos string construido
                'duracion': dur_txt,
                'tipo_cita': self.tipo_var.get(), 'notificar': self.var_notif.get(),
                'previo_desc': self.ent_prev.get() if "Sí" in self.cmb_prev.get() else ""
            }
            
            ok, msg = self.controller.guardar_cita_completa(datos, self.servicios_agregados)
            if ok: 
                messagebox.showinfo("Éxito", msg)
                self.reset()
                self.create_sidebar()
            else: messagebox.showerror("Error", msg)
        except Exception as e: messagebox.showerror("Error", str(e))

    def reset(self):
        self.limpiar_per()
        self.ent_prev.delete(0, 'end'); self.ent_bus.delete(0, 'end')
        self.cmb_doc.set("Selecciona Doctora")
        self.cmb_h.set("--"); self.cmb_m.set("--")
        self.cmb_prev.set("Tratamiento previo: No")
        self.txt_nota.delete("1.0", "end"); self.chk_ph(None)
        
        self.slider_dur.set(30); self.actualizar_slider(30)
        
        self.cliente_existente_id = None; self.selected_date = None
        self.servicios_agregados = []
        self.actualizar_servicios()
        self.tipo_var.set("Presupuesto"); self.modo_var.set("Nuevo Paciente")
        self.cambiar_modo("Nuevo Paciente"); self.toggle_serv("Presupuesto")
        self.render_calendar(); self.toggle_prev("No")

    def limpiar_per(self):
        self.ent_nom.delete(0, 'end'); self.ent_tel.delete(0, 'end')
        self.ent_email.delete(0, 'end'); self.cmb_edad.set("Edad"); self.cmb_gen.set("Género")

    def toggle_serv(self, v):
        # SIEMPRE mostramos la lista si hay items, solo cambiamos etiquetas
        self.frm_serv.grid() # Siempre visible el contenedor base
        
        if v == "Presupuesto":
            # Modo informativo: Ocultamos totales visualmente o cambiamos color
            self.lbl_tot.configure(text="Total Estimado (No genera deuda): $0.00", text_color="gray")
            # Opcional: Podrías iterar sobre los labels de precio y ponerlos en gris
        else:
            # Modo Tratamiento: Recalcular total real
            self.actualizar_ui_servicios()
    
    def toggle_prev(self, v):
        if "Sí" in v: self.ent_prev.pack(side="left", fill="x", padx=(5,0), expand=True)
        else: self.ent_prev.pack_forget()

    def render_calendar(self):
        for w in self.cal_frame.winfo_children(): w.destroy()
        cal = calendar.Calendar(firstweekday=6)
        md = cal.monthdayscalendar(self.display_date.year, self.display_date.month)
        hoy = datetime.now()

        h = ctk.CTkFrame(self.cal_frame, fg_color=HEADER_CALENDAR, corner_radius=5)
        h.pack(fill="x", pady=(0,5))
        ctk.CTkButton(h, text="<", width=25, fg_color="transparent", text_color=ACCENT_BLUE, hover_color="white", command=lambda: self.chg_month(-1)).pack(side="left")
        ctk.CTkLabel(h, text=self.display_date.strftime("%B %Y").capitalize(), font=("Arial", 12, "bold"), text_color="#333").pack(side="left", expand=True)
        ctk.CTkButton(h, text=">", width=25, fg_color="transparent", text_color=ACCENT_BLUE, hover_color="white", command=lambda: self.chg_month(1)).pack(side="right")
        
        g = ctk.CTkFrame(self.cal_frame, fg_color="transparent")
        g.pack(padx=5)
        for i, d in enumerate(["Do","Lu","Ma","Mi","Ju","Vi","Sa"]): 
            ctk.CTkLabel(g, text=d, font=("Arial",9,"bold"), width=30, text_color="#666").grid(row=0, column=i)
        
        for r, w in enumerate(md):
            for c, d in enumerate(w):
                if d == 0: continue
                dt_celda = datetime(self.display_date.year, self.display_date.month, d)
                es_pasado = dt_celda.date() < hoy.date()
                es_hoy = dt_celda.date() == hoy.date()
                es_sel = self.selected_date and dt_celda.date() == self.selected_date.date()

                bg = ACCENT_BLUE if es_sel else "white"
                fg = "white" if es_sel else ("#DDD" if es_pasado else "#333")
                state = "disabled" if es_pasado else "normal"
                border_c = "black" if es_hoy else ("#EEE" if not es_sel else ACCENT_BLUE)
                b_width = 2 if es_hoy else 1

                ctk.CTkButton(g, text=str(d), width=30, height=28, fg_color=bg, text_color=fg, border_color=border_c, border_width=b_width, state=state, font=("Arial", 11, "bold" if es_hoy else "normal"), corner_radius=6, hover_color="#D9EFFF" if state == "normal" else "white", command=lambda x=d: self.sel_day(x)).grid(row=r+1, column=c, padx=2, pady=2)

    def chg_month(self, s):
        m = self.display_date.month + s; y = self.display_date.year
        if m > 12: m=1; y+=1
        elif m < 1: m=12; y-=1
        self.display_date = self.display_date.replace(year=y, month=m, day=1)
        self.render_calendar()

    def sel_day(self, d):
        self.selected_date = datetime(self.display_date.year, self.display_date.month, d)
        self.render_calendar(); self.act_horarios()

    def create_sidebar(self):
        for w in self.sidebar.winfo_children(): w.destroy()
        c1 = ctk.CTkFrame(self.sidebar, fg_color=WHITE_CARD, corner_radius=10, border_color=BORDER_COLOR, border_width=1)
        c1.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(c1, text="🏥 Equipo Médico", font=("Segoe UI", 13, "bold"), text_color=ACCENT_BLUE).pack(pady=10, padx=15, anchor="w")
        for n, d in self.controller.obtener_info_doctoras().items():
            r = ctk.CTkFrame(c1, fg_color="transparent"); r.pack(fill="x", padx=10, pady=2)
            try: ctk.CTkLabel(r, text="", image=ctk.CTkImage(Image.open(os.path.join(current_dir, d['foto'])).resize((35,35)), size=(35,35))).pack(side="left")
            except: ctk.CTkLabel(r, text="👩‍⚕️", font=("Arial", 20)).pack(side="left")
            t = ctk.CTkFrame(r, fg_color="transparent"); t.pack(side="left", padx=5)
            ctk.CTkLabel(t, text=n, font=("Segoe UI", 12, "bold")).pack(anchor="w")
            ctk.CTkLabel(t, text=d['especialidad'], font=("Segoe UI", 11), text_color=ACCENT_BLUE).pack(anchor="w")
        
        c2 = ctk.CTkFrame(self.sidebar, fg_color=WHITE_CARD, corner_radius=10, border_color=BORDER_COLOR, border_width=1)
        c2.pack(fill="x")
        ctk.CTkLabel(c2, text=f"📊 Resumen Hoy", font=("Segoe UI", 13, "bold"), text_color=ACCENT_BLUE).pack(pady=10, padx=15, anchor="w")
        st = self.controller.obtener_resumen_citas()
        for l, c, col in [("Pendientes", st.get('Pendiente',0), WARNING_COLOR), ("En curso", st.get('En curso',0), INFO_COLOR), ("Completadas", st.get('Completada',0), SUCCESS_COLOR), ("Canceladas", st.get('Cancelada',0), DANGER_COLOR)]:
            r = ctk.CTkFrame(c2, fg_color="transparent"); r.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(r, text="●", text_color=col).pack(side="left")
            ctk.CTkLabel(r, text=l, font=("Segoe UI", 12)).pack(side="left", padx=5)
            ctk.CTkLabel(r, text=str(c), font=("Segoe UI", 12, "bold")).pack(side="right")

    def abrir_servicios(self):
        try:
            top = ctk.CTkToplevel(self)
            top.title("Catálogo de Tratamientos"); top.geometry("1000x600")
            top.transient(self.winfo_toplevel()); top.grab_set(); top.lift(); top.focus_force()

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

            def logica_precio(servicio):
                import json
                
                # Intentar leer JSON, si falla usar precio_base simple (retrocompatibilidad)
                opciones = {}
                try:
                    if servicio['opciones_json']:
                        opciones = json.loads(servicio['opciones_json'])
                except: pass
                
                # Si no hay JSON, crear opción default con lo que haya en DB
                if not opciones:
                    u_legacy = servicio['tipo_unidad']
                    p_legacy = float(servicio['precio_base'])
                    opciones = {u_legacy: p_legacy}

                # CASO 1: Solo una opción
                if len(opciones) == 1:
                    u, p = list(opciones.items())[0]
                    # REGLA: Si dice "caso" o precio es 0 -> Manual
                    if "caso" in u.lower() or p == 0:
                        pedir_manual(servicio, u)
                    else:
                        agregar(servicio, p, u)
                    return

                # CASO 2: Múltiples opciones -> POPUP SELECCIÓN
                top_d = ctk.CTkToplevel(top)
                top_d.title("Seleccionar Variante")
                top_d.geometry("400x350")
                top_d.transient(top); top_d.grab_set()
                
                ctk.CTkLabel(top_d, text=f"Servicio: {servicio['nombre']}", font=("bold", 14)).pack(pady=15)
                ctk.CTkLabel(top_d, text="Seleccione la modalidad:", text_color="gray").pack(pady=(0,10))
                
                # Generar botones para cada opción del JSON
                scroll_ops = ctk.CTkScrollableFrame(top_d, fg_color="transparent")
                scroll_ops.pack(fill="both", expand=True, padx=20, pady=10)
                
                for unidad, precio in opciones.items():
                    # REGLA CASO/COTIZAR
                    es_cotizar = "caso" in unidad.lower() or precio == 0
                    
                    txt_btn = f"{unidad} (Cotizar)" if es_cotizar else f"{unidad} - ${precio:,.2f}"
                    col_btn = "gray" if es_cotizar else ACCENT_BLUE
                    
                    if es_cotizar:
                        cmd = lambda u=unidad: [top_d.destroy(), self.after(100, lambda: pedir_manual(servicio, u))]
                    else:
                        cmd = lambda u=unidad, p=precio: [agregar(servicio, p, u), top_d.destroy()]
                    
                    ctk.CTkButton(scroll_ops, text=txt_btn, command=cmd, fg_color=col_btn, height=40).pack(pady=5, fill="x")

            def pedir_manual(s, u):
                d = ctk.CTkInputDialog(text=f"Cotización para {s['nombre']} ({u}):", title="Precio Manual")
                val = d.get_input()
                if val and val.replace('.','',1).isdigit(): agregar(s, float(val), u)

            def agregar(s, p, u):
                # Agregamos a la lista
                self.servicios_agregados.append({
                    'id': s['id'], 'nombre': s['nombre'], 'unidad': u, 
                    'precio_unitario': float(p), 'cantidad': 1, 'precio_total': float(p)
                })
                self.actualizar_ui_servicios()
                messagebox.showinfo("Servicio Agregado", f"Se añadió: {s['nombre']}", parent=top)

            def up_sub(c): 
                combo_sub.configure(values=["Todas"]+self.controller.obtener_subcategorias_por_cat(c) if c!="Todas" else ["Todas"]); combo_sub.set("Todas"); buscar()
            def reset_filtros():
                combo_cat.set("Todas"); combo_sub.configure(values=["Todas"]); entry_search.delete(0, 'end'); buscar()

            combo_cat.configure(command=up_sub); combo_sub.configure(command=buscar); entry_search.bind("<Return>", buscar); buscar()
        except Exception as e: messagebox.showerror("Error", str(e))

    def actualizar_ui_servicios(self):
        # 1. Limpiar visualmente
        for w in self.lst_serv.winfo_children(): w.destroy()
        
        grand_total = 0
        es_presupuesto = (self.tipo_var.get() == "Presupuesto")
        
        # 2. Si vacío
        if not self.servicios_agregados:
            ctk.CTkLabel(self.lst_serv, text="No hay servicios agregados.", text_color="gray").pack(pady=10)
            if es_presupuesto:
                self.lbl_tot.configure(text="Total (Presupuesto): $0.00", text_color="gray")
            else:
                self.lbl_tot.configure(text="Total: $0.00", text_color=SUCCESS_COLOR)
            return

        # 3. Dibujar la lista (SIEMPRE VISIBLE)
        for idx, item in enumerate(self.servicios_agregados):
            row = ctk.CTkFrame(self.lst_serv, fg_color="white", corner_radius=6)
            row.pack(fill="x", pady=2, padx=2)
            
            # Info
            info_frame = ctk.CTkFrame(row, fg_color="transparent", width=200)
            info_frame.pack(side="left", padx=5, pady=5)
            ctk.CTkLabel(info_frame, text=item['nombre'], font=("Segoe UI", 12, "bold"), width=180, anchor="w").pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"({item['unidad']})", font=("Segoe UI", 10), text_color="gray", width=180, anchor="w").pack(anchor="w")

            # Cantidad
            qty_frame = ctk.CTkFrame(row, fg_color="transparent")
            qty_frame.pack(side="left", padx=5)
            ctk.CTkButton(qty_frame, text="-", width=25, height=25, fg_color="#EEE", text_color="black", hover_color="#DDD", command=lambda i=idx: self.cambiar_cantidad(i, -1)).pack(side="left")
            ctk.CTkLabel(qty_frame, text=str(item['cantidad']), width=30, font=("Segoe UI", 12, "bold")).pack(side="left", padx=2)
            ctk.CTkButton(qty_frame, text="+", width=25, height=25, fg_color="#EEE", text_color="black", hover_color="#DDD", command=lambda i=idx: self.cambiar_cantidad(i, 1)).pack(side="left")

            # Precios
            subtotal = item['cantidad'] * item['precio_unitario']
            item['precio_total'] = subtotal 
            grand_total += subtotal
            
            # Estilo condicional (Gris si es presupuesto, Azul si es tratamiento)
            txt_precio = f"${subtotal:,.2f}"
            col_precio = ACCENT_BLUE
            if es_presupuesto:
                col_precio = "gray"
            
            btn_del = ctk.CTkButton(row, text="×", width=25, height=25, fg_color="transparent", text_color=DANGER_COLOR, hover_color="#FFEEEE", command=lambda i=idx: self.eliminar_servicio(i))
            btn_del.pack(side="right", padx=5)

            ctk.CTkLabel(row, text=txt_precio, font=("Segoe UI", 12, "bold"), text_color=col_precio).pack(side="right", padx=10)

        # 4. Total Final (Aquí aplicamos la regla de $0.00)
        if es_presupuesto:
            self.lbl_tot.configure(text="Total a Pagar: $0.00", text_color="gray")
        else:
            self.lbl_tot.configure(text=f"Total a Pagar: ${grand_total:,.2f}", text_color=SUCCESS_COLOR)

    def cambiar_cantidad(self, index, delta):
        item = self.servicios_agregados[index]
        nueva = item['cantidad'] + delta
        if nueva <= 0: self.eliminar_servicio(index)
        else: item['cantidad'] = nueva; self.actualizar_ui_servicios()

    def eliminar_servicio(self, index):
        self.servicios_agregados.pop(index); self.actualizar_ui_servicios()

    def actualizar_servicios(self): # Helper legacy
        self.actualizar_ui_servicios()