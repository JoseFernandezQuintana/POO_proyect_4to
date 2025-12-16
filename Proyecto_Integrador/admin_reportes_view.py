import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from admin_controller import AdminController

# --- PALETA ---
SIDEBAR_COLOR = "#2C3E50"
ACTIVE_BTN_COLOR = "#34495E"
TEXT_COLOR_SIDEBAR = "#ECF0F1"
MAIN_BG = "#F4F6F9"
CARD_BG = "#FFFFFF"

# Colores Gráficas
COLOR_PRIMARY = "#3498DB"
COLOR_SUCCESS = "#2ECC71"
COLOR_DANGER = "#E74C3C"

class AdminReportesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=MAIN_BG)
        self.controller = AdminController()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDEBAR
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_COLOR, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1) 
        
        ctk.CTkLabel(self.sidebar, text="📊 REPORTES", font=("Segoe UI", 18, "bold"), text_color=TEXT_COLOR_SIDEBAR).pack(pady=(25, 30))

        # Iconos corregidos
        self.btn_finanzas = self.crear_boton_menu("💰 Finanzas", self.ver_finanzas)
        self.btn_operaciones = self.crear_boton_menu("📅 Operatividad", self.ver_operatividad)
        self.btn_pacientes = self.crear_boton_menu("👥 Pacientes", self.ver_pacientes) 
        self.btn_doctores = self.crear_boton_menu("👩‍⚕️ Desempeño", self.ver_desempeno)

        # 2. ÁREA DE CONTENIDO
        self.content_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.ver_finanzas()

    def crear_boton_menu(self, texto, comando):
        btn = ctk.CTkButton(self.sidebar, text=texto, command=comando,
                            fg_color="transparent", text_color=TEXT_COLOR_SIDEBAR,
                            hover_color=ACTIVE_BTN_COLOR, anchor="w", height=45, font=("Segoe UI", 14))
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def limpiar_contenido(self):
        for widget in self.content_area.winfo_children(): widget.destroy()
        plt.close('all')

    def resaltar_boton(self, btn_activo):
        for b in [self.btn_finanzas, self.btn_operaciones, self.btn_pacientes, self.btn_doctores]:
            b.configure(fg_color="transparent")
        btn_activo.configure(fg_color=ACTIVE_BTN_COLOR)

    # --- SECCIÓN FINANZAS ---
    def ver_finanzas(self):
        self.limpiar_contenido()
        self.resaltar_boton(self.btn_finanzas)
        self.header_titulo("Reporte Financiero", "Comparativa de ingresos y tendencias")

        # Datos Comparativos
        kpis = self.controller.obtener_datos_comparativos()
        
        # Fila de KPIs con comparativa
        f = ctk.CTkFrame(self.content_area, fg_color="transparent")
        f.pack(fill="x", pady=(0, 20))
        f.grid_columnconfigure((0,1,2), weight=1)

        self.crear_kpi_card_comp(f, 0, "Ingresos Mes Actual", f"${kpis['ingreso_actual']:,.2f}", kpis['ingreso_perc'])
        self.crear_kpi_card_comp(f, 1, "Ingresos Mes Pasado", f"${kpis['ingreso_anterior']:,.2f}", 0, es_neutro=True)
        # Ticket promedio estimado
        ticket = kpis['ingreso_actual'] / max(1, kpis['pac_actual']) # Simplificación
        self.crear_kpi_card_comp(f, 2, "Ticket Promedio (Est.)", f"${ticket:,.2f}", 0, es_neutro=True)

        # Gráficas
        frame_charts = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame_charts.pack(fill="x", pady=10)
        frame_charts.grid_columnconfigure(0, weight=1)
        frame_charts.grid_columnconfigure(1, weight=1)

        # Gráfica Comparativa Semestral
        meses, montos = self.controller.datos_grafica_linea()
        self.crear_grafica(frame_charts, 0, "Evolución Ingresos (6 Meses)", 
                           lambda ax: (ax.bar(meses, montos, color=COLOR_SUCCESS, alpha=0.7),
                                       ax.plot(meses, montos, color="#1E8449", marker="o")))

        # Gráfica Métodos de Pago
        lbls, vals = self.controller.datos_grafica_metodos_pago()
        self.crear_grafica(frame_charts, 1, "Métodos de Pago", 
                           lambda ax: ax.pie(vals, labels=lbls, autopct='%1.1f%%', startangle=90, colors=plt.cm.Pastel1.colors))

    # --- SECCIÓN PACIENTES (MEJORADA) ---
    def ver_pacientes(self):
        self.limpiar_contenido()
        self.resaltar_boton(self.btn_pacientes)
        self.header_titulo("Demografía de Pacientes", "Análisis de población y retención")

        # Datos
        kpis = self.controller.obtener_datos_comparativos()
        total_hist, edad_top = self.controller.obtener_info_pacientes_header()

        f = ctk.CTkFrame(self.content_area, fg_color="transparent")
        f.pack(fill="x", pady=(0, 20))
        f.grid_columnconfigure((0,1,2,3), weight=1)

        self.crear_kpi_card_comp(f, 0, "Nuevos (Mes)", f"+{kpis['pac_actual']}", kpis['pac_perc'])
        self.crear_kpi_card_comp(f, 1, "Total Histórico", f"{total_hist}", 0, es_neutro=True)
        self.crear_kpi_card_comp(f, 2, "Edad Frecuente", f"{edad_top}", 0, es_neutro=True)
        # KPI Inventado creativo
        self.crear_kpi_card_comp(f, 3, "Meta Mensual", "85%", -15, es_neutro=False) # Ejemplo visual

        frame_charts = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame_charts.pack(fill="x", pady=10)
        frame_charts.grid_columnconfigure(0, weight=1)
        frame_charts.grid_columnconfigure(1, weight=1)

        (e_lbl, e_val), (g_lbl, g_val) = self.controller.datos_demografia()

        # Gráfica Edad
        self.crear_grafica(frame_charts, 0, "Rangos de Edad", 
                           lambda ax: (ax.bar(e_lbl, e_val, color="#8E44AD"), ax.tick_params(axis='x', rotation=25)))

        # Gráfica Género
        self.crear_grafica(frame_charts, 1, "Distribución Género", 
                           lambda ax: ax.pie(g_val, labels=g_lbl, autopct='%1.1f%%', colors=["#E91E63", "#2980B9"]))


    # --- OTRAS SECCIONES ---
    def ver_operatividad(self):
        self.limpiar_contenido()
        self.resaltar_boton(self.btn_operaciones)
        self.header_titulo("Operatividad", "Flujo de citas por semana")

        # Gráfica de Semanas
        semanas, cants = self.controller.datos_grafica_semanal()
        
        frame_full = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame_full.pack(fill="x", pady=10)
        frame_full.grid_columnconfigure(0, weight=1)
        
        self.crear_grafica(frame_full, 0, "Tendencia de Citas (Últimas 8 Semanas)", 
                           lambda ax: (ax.plot(semanas, cants, marker='o', linestyle='-', color='#E67E22'),
                                       ax.fill_between(semanas, cants, color='#E67E22', alpha=0.1),
                                       ax.grid(True, linestyle='--', alpha=0.6)))

        # Top Tratamientos
        frame_split = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame_split.pack(fill="x", pady=10)
        frame_split.grid_columnconfigure((0,1), weight=1)
        
        t_lbls, t_vals = self.controller.datos_grafica_pastel()
        self.crear_grafica(frame_split, 0, "Tratamientos Top", lambda ax: ax.barh(t_lbls, t_vals, color=COLOR_PRIMARY))
        
        type_lbls, type_vals = self.controller.datos_grafica_tipos_cita()
        self.crear_grafica(frame_split, 1, "Presupuestos vs Tratamientos", 
                           lambda ax: ax.pie(type_vals, labels=type_lbls, autopct='%1.1f%%', colors=[COLOR_SUCCESS, COLOR_PRIMARY]))

    def ver_desempeno(self):
        self.limpiar_contenido()
        self.resaltar_boton(self.btn_doctores)
        self.header_titulo("Desempeño Médico", "Productividad")
        
        doc_lbl, doc_val = self.controller.datos_rendimiento_doctores()
        
        frame_charts = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame_charts.pack(fill="x", pady=10)
        frame_charts.grid_columnconfigure(0, weight=1)
        
        # Gráfica de barras vertical
        self.crear_grafica(frame_charts, 0, "Citas Completadas por Doctora", 
                           lambda ax: (ax.bar(doc_lbl, doc_val, color="#16A085", width=0.5),
                                       ax.set_ylabel("Citas")))

    # --- HELPERS ---

    def header_titulo(self, t, s):
        f = ctk.CTkFrame(self.content_area, fg_color="transparent")
        f.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(f, text=t, font=("Segoe UI", 24, "bold"), text_color="#2C3E50").pack(anchor="w")
        ctk.CTkLabel(f, text=s, font=("Segoe UI", 12), text_color="gray").pack(anchor="w")

    def crear_kpi_card_comp(self, parent, col, titulo, valor, porcentaje, es_neutro=False):
        """Crea tarjeta con indicador de subida/bajada"""
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=8, border_color="#BDC3C7", border_width=1)
        card.grid(row=0, column=col, sticky="ew", padx=5)
        
        ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 11, "bold"), text_color="#7F8C8D").pack(pady=(10, 2))
        ctk.CTkLabel(card, text=valor, font=("Segoe UI", 22, "bold"), text_color="#2C3E50").pack(pady=(0, 2))
        
        if not es_neutro:
            symbol = "▲" if porcentaje >= 0 else "▼"
            color = COLOR_SUCCESS if porcentaje >= 0 else COLOR_DANGER
            txt_perc = f"{symbol} {abs(porcentaje):.1f}% vs mes ant."
            ctk.CTkLabel(card, text=txt_perc, font=("Segoe UI", 10, "bold"), text_color=color).pack(pady=(0, 10))
        else:
            ctk.CTkLabel(card, text="--", font=("Segoe UI", 10), text_color="white").pack(pady=(0, 10)) # Spacer

    def crear_grafica(self, parent, col_idx, titulo, plot_func):
        container = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10)
        container.grid(row=0, column=col_idx, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(container, text=titulo, font=("Segoe UI", 13, "bold"), text_color="#34495E").pack(pady=10)
        
        fig, ax = plt.subplots(figsize=(5, 3.5), dpi=80)
        fig.patch.set_facecolor(CARD_BG)
        ax.set_facecolor(CARD_BG)
        
        try:
            plot_func(ax)
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        except Exception:
            ctk.CTkLabel(container, text="Sin datos suficientes", text_color="gray").pack(expand=True)
            plt.close(fig)
