import customtkinter as ctk
import tkinter as tk

class Spinner(tk.Canvas):
    def __init__(self, master, size=60, color="#007BFF", bg_color=None):
        if bg_color is None:
            try: bg_color = master.cget("fg_color")
            except: bg_color = "#F4F6F9"
            
        super().__init__(master, width=size, height=size, bg=bg_color, highlightthickness=0)
        self.size = size
        self.color = color
        self.angle = 0
        self.is_running = False
        self.arc = self.create_arc(5, 5, size-5, size-5, start=0, extent=150, outline=color, width=4, style="arc")

    def start(self):
        self.is_running = True
        self.animate()

    def stop(self):
        self.is_running = False

    def animate(self):
        # 1. Si se detuvo manualmente, salir
        if not self.is_running: return

        # 2. PROTECCIÓN CONTRA CIERRE DE VENTANA (EL FIX)
        try:
            if not self.winfo_exists():
                self.is_running = False
                return
        except:
            self.is_running = False
            return

        try:
            # Rotar el arco
            self.angle = (self.angle - 10) % 360
            self.itemconfigure(self.arc, start=self.angle)
            self.after(20, self.animate)
        except:
            # Si falla al configurar (ventana destruida), paramos silenciosamente
            self.stop()

class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, master, mensaje="Cargando...", tipo="barra"):
        super().__init__(master, fg_color="#F4F6F9") 
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Intentar levantar, si falla no importa
        try: self.lift() 
        except: pass

        self.center_box = ctk.CTkFrame(self, fg_color="transparent")
        self.center_box.place(relx=0.5, rely=0.5, anchor="center")

        self.spinner = None
        self.bar = None

        if tipo == "circulo":
            self.spinner = Spinner(self.center_box, size=60, color="#007BFF", bg_color="#F4F6F9")
            self.spinner.pack(pady=(0, 15))
            self.spinner.start()
            self.msg = ctk.CTkLabel(self.center_box, text=mensaje, font=("Segoe UI", 14, "bold"), text_color="#555")
            self.msg.pack()
        else:
            self.msg = ctk.CTkLabel(self.center_box, text=mensaje, font=("Segoe UI", 24, "bold"), text_color="#007BFF")
            self.msg.pack(pady=(0, 20))
            self.bar = ctk.CTkProgressBar(self.center_box, width=400, height=20, progress_color="#007BFF")
            self.bar.pack()
            self.bar.configure(mode="indeterminate")
            self.bar.start()

    def destruir(self):
        # Detener animaciones antes de destruir
        if self.bar: 
            try: self.bar.stop()
            except: pass
        if self.spinner: 
            self.spinner.stop()
        
        try: self.destroy()
        except: pass

def mostrar_loading(parent, duracion_ms, callback_final, tipo="barra", mensaje="Cargando..."):
    # Verificar si el padre existe antes de intentar poner el loading
    try:
        if not parent.winfo_exists(): return
    except: return

    overlay = LoadingOverlay(parent, mensaje=mensaje, tipo=tipo)
    try: parent.update_idletasks()
    except: pass
    
    def finalizar():
        # Verificar si el overlay sigue vivo antes de destruirlo
        try:
            if overlay.winfo_exists():
                overlay.destruir()
        except: pass
        
        # Ejecutar lo siguiente
        if callback_final:
            callback_final()
            
    parent.after(duracion_ms, finalizar)
