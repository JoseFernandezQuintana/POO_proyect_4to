import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from admin_controller import AdminController

class AdminReportesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F4F6F9")
        self.controller = AdminController()
        
        # Título
        ctk.CTkLabel(self, text="📊 Inteligencia de Negocio", font=("Segoe UI", 20, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=15)
        
        # --- KPIs ---
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", padx=15, pady=5)
        kpi_row.grid_columnconfigure((0,1,2), weight=1)
        
        mes, total, nuevos = self.controller.obtener_kpis()
        self.kpi_card(kpi_row, 0, "Ingresos Mes", f"${mes:,.2f}", "#28A745")
        self.kpi_card(kpi_row, 1, "Total Histórico", f"${total:,.2f}", "#17A2B8")
        self.kpi_card(kpi_row, 2, "Pacientes Nuevos (Mes)", str(nuevos), "#FFC107")

        # --- GRÁFICAS ---
        # Contenedor Grid 2x1
        graphs = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        graphs.pack(fill="both", expand=True, padx=20, pady=20)
        graphs.grid_columnconfigure(0, weight=1)
        graphs.grid_columnconfigure(1, weight=1)
        graphs.grid_rowconfigure(0, weight=1)
        
        # Gráfica 1
        self.plot_barras(graphs, 0)
        # Gráfica 2
        self.plot_linea(graphs, 1)

    def kpi_card(self, parent, col, titulo, valor, color):
        c = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, border_color=color, border_width=2)
        c.grid(row=0, column=col, sticky="ew", padx=5)
        ctk.CTkLabel(c, text=titulo, font=("Arial", 12), text_color="gray").pack(pady=(10,0))
        ctk.CTkLabel(c, text=valor, font=("Arial", 22, "bold"), text_color="#333").pack(pady=(0,10))

    def plot_barras(self, parent, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=0, column=col, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(f, text="Top Tratamientos", font=("bold",14)).pack()
        
        lbls, vals = self.controller.datos_grafica_pastel()
        if not lbls: 
            ctk.CTkLabel(f, text="Sin datos suficientes").pack(expand=True)
            return

        fig, ax = plt.subplots(figsize=(4,3), dpi=100)
        ax.barh(lbls, vals, color="#007BFF")
        plt.tight_layout()
        
        canv = FigureCanvasTkAgg(fig, master=f)
        canv.draw(); canv.get_tk_widget().pack(fill="both", expand=True)

    def plot_linea(self, parent, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=0, column=col, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(f, text="Ingresos (6 Meses)", font=("bold",14)).pack()
        
        meses, montos = self.controller.datos_grafica_linea()
        if not meses: 
            ctk.CTkLabel(f, text="Sin datos financieros").pack(expand=True)
            return

        fig, ax = plt.subplots(figsize=(4,3), dpi=100)
        ax.plot(meses, montos, marker='o', color="#28A745")
        ax.fill_between(meses, montos, color="#28A745", alpha=0.1)
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        canv = FigureCanvasTkAgg(fig, master=f)
        canv.draw(); canv.get_tk_widget().pack(fill="both", expand=True)