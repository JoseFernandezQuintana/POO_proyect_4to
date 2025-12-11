import customtkinter as ctk
from tkinter import messagebox
from pagos_controller import PagosController

# --- CONFIGURACIÓN DE COLORES ---
BG_MAIN = "#F4F6F9"
WHITE_CARD = "#FFFFFF"
ACCENT_BLUE = "#007BFF"
TEXT_DARK = "#333333"
SUCCESS_COLOR = "#28A745"
BORDER_COLOR = "#E0E0E0"
DANGER_COLOR = "#DC3545"

class PagosFrame(ctk.CTkFrame):
    
    def __init__(self, master):
        super().__init__(master, fg_color=BG_MAIN)
        self.controller = PagosController()
        self.cita_seleccionada = None
        
        # Grid Principal: 2 Columnas
        self.grid_columnconfigure(0, weight=4) # Lista
        self.grid_columnconfigure(1, weight=6) # Detalle
        self.grid_rowconfigure(0, weight=1)

        # --- IZQUIERDA: LISTA DE DEUDAS ---
        self.left_panel = ctk.CTkFrame(self, fg_color=WHITE_CARD, corner_radius=15, border_color=BORDER_COLOR, border_width=1)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.left_panel.grid_rowconfigure(2, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        # Evento para quitar foco
        self.left_panel.bind("<Button-1>", lambda e: self.focus_set())

        # Título
        ctk.CTkLabel(self.left_panel, text="📂 Cuentas por Cobrar", font=("Segoe UI", 18, "bold"), text_color=ACCENT_BLUE).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # --- CAMBIO: CONTENEDOR PARA BUSCADOR Y BOTÓN JUNTOS ---
        frame_busqueda = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        frame_busqueda.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Buscador (se expande a la izquierda)
        self.ent_search = ctk.CTkEntry(frame_busqueda, placeholder_text="🔍 Buscar por nombre...", height=35, fg_color="#FAFAFA")
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_search.bind("<KeyRelease>", self.filtrar_deudores)

        # Botón Actualizar (pequeño a la derecha)
        ctk.CTkButton(frame_busqueda, text="🔄", width=40, height=35, fg_color="transparent", border_color=ACCENT_BLUE, border_width=1, text_color=ACCENT_BLUE, hover_color="#E6F0FF", command=self.cargar_datos_iniciales).pack(side="right")

        # Lista Scrollable
        self.scroll_deudas = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.scroll_deudas.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # --- DERECHA: FORMULARIO DE COBRO ---
        # CAMBIO AQUÍ: Usamos CTkScrollableFrame en lugar de CTkFrame
        self.right_panel = ctk.CTkScrollableFrame(self, fg_color="transparent") 
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        
        # Estas configuraciones de grid ya no son estrictamente necesarias para el scroll, 
        # pero ayudan a centrar el contenido.
        self.right_panel.grid_columnconfigure(0, weight=1)

        # Tarjeta de Detalle (Se mantiene igual, pero ahora dentro del scroll)
        self.detail_card = ctk.CTkFrame(self.right_panel, fg_color=WHITE_CARD, corner_radius=15, border_color=BORDER_COLOR, border_width=1)
        self.detail_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.detail_card.bind("<Button-1>", lambda e: self.focus_set())
        
        # Contenido Detalle
        self.frm_detalle = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        self.frm_detalle.pack(fill="both", expand=True, padx=20, pady=20)
        self.crear_placeholder_detalle()

        # Tarjeta de Pago (Se mantiene igual)
        self.pay_card = ctk.CTkFrame(self.right_panel, fg_color=WHITE_CARD, corner_radius=15, border_color=BORDER_COLOR, border_width=1)
        self.pay_card.grid(row=1, column=0, sticky="ew")
        self.pay_card.bind("<Button-1>", lambda e: self.focus_set())
        
        self.crear_formulario_pago()
        self.cargar_datos_iniciales()

    def crear_placeholder_detalle(self):
        for w in self.frm_detalle.winfo_children(): w.destroy()
        ctk.CTkLabel(self.frm_detalle, text="👈 Selecciona un paciente\npara ver el detalle de su deuda.", font=("Segoe UI", 16), text_color="gray").pack(expand=True)

    def crear_formulario_pago(self):
        p = self.pay_card
        # Header con botón Cancelar Selección
        h = ctk.CTkFrame(p, fg_color="transparent")
        h.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(h, text="💳 Registrar Pago", font=("Segoe UI", 16, "bold"), text_color="#333").pack(side="left")
        self.btn_cancelar_sel = ctk.CTkButton(h, text="✖ Cancelar Selección", width=120, fg_color=DANGER_COLOR, command=self.limpiar_seleccion, state="disabled")
        self.btn_cancelar_sel.pack(side="right")
        
        # Grid interno
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=(0, 20))
        
        # Monto
        ctk.CTkLabel(f, text="Monto a Pagar ($):", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.ent_monto = ctk.CTkEntry(f, placeholder_text="0.00", height=40, font=("Segoe UI", 14), fg_color="#FAFAFA")
        self.ent_monto.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        
        # Método
        ctk.CTkLabel(f, text="Método de Pago:", font=("Segoe UI", 12, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 5))
        self.cmb_metodo = ctk.CTkOptionMenu(f, values=["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia", "Cheque"], height=40, fg_color="#FAFAFA", text_color="#333", button_color="#CCC")
        self.cmb_metodo.grid(row=1, column=1, sticky="ew")
        
        # Nota
        ctk.CTkLabel(f, text="Nota / Referencia:", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 5))
        self.ent_nota = ctk.CTkEntry(f, placeholder_text="Opcional...", height=40, fg_color="#FAFAFA")
        self.ent_nota.grid(row=3, column=0, columnspan=2, sticky="ew")

        f.grid_columnconfigure((0, 1), weight=1)

        # Botón Grande
        self.btn_pagar = ctk.CTkButton(p, text="SELECCIONA PACIENTE", height=50, fg_color=SUCCESS_COLOR, hover_color="#218838", font=("Segoe UI", 15, "bold"), state="disabled", command=self.procesar_pago)
        self.btn_pagar.pack(fill="x", padx=20, pady=(0, 20))

    # --- LÓGICA DE LISTA ---
    def cargar_datos_iniciales(self):
        self.ent_search.delete(0, 'end')
        self.buscar_deudores()

    def filtrar_deudores(self, event=None):
        # Búsqueda en tiempo real
        query = self.ent_search.get()
        self.buscar_deudores(query)

    def buscar_deudores(self, query=""):
        citas = self.controller.buscar_pacientes_con_deuda(query)
        
        for w in self.scroll_deudas.winfo_children(): w.destroy()
        
        if not citas:
            ctk.CTkLabel(self.scroll_deudas, text="No se encontraron deudas.", text_color="gray").pack(pady=20)
            return

        for c in citas:
            self._crear_tarjeta_deuda(c)

    def _crear_tarjeta_deuda(self, data):
        card = ctk.CTkFrame(self.scroll_deudas, fg_color=WHITE_CARD, corner_radius=8, border_color=BORDER_COLOR, border_width=1)
        card.pack(fill="x", pady=5)
        
        # Evento click para seleccionar
        card.bind("<Button-1>", lambda e: self.cargar_detalle(data))
        
        h = ctk.CTkFrame(card, fg_color="transparent")
        h.pack(fill="x", padx=10, pady=5)
        
        fecha_obj = data['fecha_cita']
        fecha_str = fecha_obj.strftime("%d/%m/%Y") if hasattr(fecha_obj, 'strftime') else str(fecha_obj)
        
        ctk.CTkLabel(h, text=f"📅 {fecha_str}", font=("bold", 11), text_color="#555").pack(side="left")
        ctk.CTkLabel(h, text=f"Deuda: ${data['saldo_pendiente']:,.2f}", font=("bold", 12), text_color="#DC3545").pack(side="right")
        
        ctk.CTkLabel(card, text=data['nombre_completo'], font=("Segoe UI", 13, "bold"), text_color=ACCENT_BLUE).pack(anchor="w", padx=10)
        
        tratamiento = data.get('tratamiento') or "Consulta General"
        if len(tratamiento) > 30: tratamiento = tratamiento[:30] + "..."
        ctk.CTkLabel(card, text=tratamiento, font=("Segoe UI", 11), text_color="gray").pack(anchor="w", padx=10, pady=(0, 5))
        
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: self.cargar_detalle(data))

    # --- LÓGICA DE SELECCIÓN ---
    def cargar_detalle(self, data):
        self.cita_seleccionada = data['id']
        self.btn_cancelar_sel.configure(state="normal")
        
        # Limpiar panel detalle
        for w in self.frm_detalle.winfo_children(): w.destroy()
        
        # Encabezado
        ctk.CTkLabel(self.frm_detalle, text="Detalle de Servicios", font=("Segoe UI", 16, "bold"), text_color=ACCENT_BLUE).pack(anchor="w")
        ctk.CTkLabel(self.frm_detalle, text=f"Paciente: {data['nombre_completo']}", font=("Segoe UI", 14)).pack(anchor="w")
        
        items = self.controller.obtener_items_cita(data['id'])
        scroll = ctk.CTkScrollableFrame(self.frm_detalle, fg_color="#F9F9F9", height=200)
        scroll.pack(fill="x", pady=10)
        
        for item in items:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"• {item['nombre']}", font=("Segoe UI", 12)).pack(side="left")
            ctk.CTkLabel(row, text=f"${item['subtotal']:,.2f}", font=("Segoe UI", 12, "bold")).pack(side="right")

        f_tot = ctk.CTkFrame(self.frm_detalle, fg_color="transparent")
        f_tot.pack(fill="x", pady=10)
        
        ctk.CTkLabel(f_tot, text=f"Total Cita: ${data['monto_total']:,.2f}", font=("bold", 12)).pack(anchor="e")
        ctk.CTkLabel(f_tot, text=f"Pagado: -${data['monto_pagado']:,.2f}", font=("bold", 12), text_color="green").pack(anchor="e")
        ctk.CTkLabel(f_tot, text=f"PENDIENTE: ${data['saldo_pendiente']:,.2f}", font=("bold", 16), text_color="#DC3545").pack(anchor="e")

        # Preparar formulario
        self.ent_monto.delete(0, 'end')
        self.ent_monto.insert(0, f"{data['saldo_pendiente']:.2f}")
        self.btn_pagar.configure(state="normal", text=f"PAGAR ${data['saldo_pendiente']:,.2f}")
        self.ent_monto.bind("<KeyRelease>", self.actualizar_btn_pago)

    def limpiar_seleccion(self):
        self.cita_seleccionada = None
        self.crear_placeholder_detalle()
        self.btn_cancelar_sel.configure(state="disabled")
        self.btn_pagar.configure(state="disabled", text="SELECCIONA PACIENTE")
        self.ent_monto.delete(0, 'end')
        self.ent_nota.delete(0, 'end')

    def actualizar_btn_pago(self, e):
        try:
            val = float(self.ent_monto.get())
            self.btn_pagar.configure(text=f"PAGAR ${val:,.2f}")
        except:
            self.btn_pagar.configure(text="PAGAR")

    def procesar_pago(self):
        if not self.cita_seleccionada: return
        
        try:
            # Obtener ID desde la app principal
            usuario_actual_id = self.master.master.user_id
        except:
            usuario_actual_id = None
        
        ok, msg = self.controller.procesar_pago(
            self.cita_seleccionada,
            self.ent_monto.get(),
            self.cmb_metodo.get(),
            self.ent_nota.get(),
            usuario_actual_id
        )
        
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.limpiar_seleccion()
            self.cargar_datos_iniciales()
        else:
            messagebox.showerror("Error", msg)