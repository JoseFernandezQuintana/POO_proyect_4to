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
        
        # Dibujar el arco inicial
        try:
            self.arc = self.create_arc(5, 5, size-5, size-5, start=0, extent=150, outline=color, width=4, style="arc")
        except: pass
        
        self.after_id = None 

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.animate()

    def stop(self):
        self.is_running = False
        if self.after_id:
            try: self.after_cancel(self.after_id)
            except: pass
            self.after_id = None

    def animate(self):
        # 1. Si ya se detuvo manualmente, salir
        if not self.is_running: return

        # 2. PROTECCIÓN TOTAL: Verificar si la ventana existe antes de tocarla
        try:
            if not self.winfo_exists():
                self.is_running = False
                return
        except:
            self.is_running = False
            return

        # 3. Intentar animar
        try:
            self.angle = (self.angle - 10) % 360
            self.itemconfigure(self.arc, start=self.angle)
            # Guardamos la referencia para poder cancelar si se cierra
            self.after_id = self.after(20, self.animate)
        except Exception:
            # Si falla (ventana cerrada justo en este milisegundo), paramos todo
            self.stop()

class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, master, mensaje="Cargando...", tipo="barra"):
        super().__init__(master, fg_color="#F4F6F9") 
        
        # Intentar colocar y levantar (puede fallar si master se está cerrando)
        try:
            self.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.lift()
        except: return

        self.center_box = ctk.CTkFrame(self, fg_color="transparent")
        self.center_box.place(relx=0.5, rely=0.5, anchor="center")

        self.spinner = None
        self.bar = None

        if tipo == "circulo":
            # --- ESTILO SPINNER (CÍRCULO) ---
            self.spinner = Spinner(self.center_box, size=60, color="#007BFF", bg_color="#F4F6F9")
            self.spinner.pack(pady=(0, 15))
            self.spinner.start()
            
            self.msg = ctk.CTkLabel(self.center_box, text=mensaje, font=("Segoe UI", 14, "bold"), text_color="#555")
            self.msg.pack()

        else:
            # --- ESTILO BARRA (WINDOWS) ---
            self.msg = ctk.CTkLabel(self.center_box, text=mensaje, font=("Segoe UI", 24, "bold"), text_color="#007BFF")
            self.msg.pack(pady=(0, 20))
            
            self.bar = ctk.CTkProgressBar(self.center_box, width=400, height=20, progress_color="#007BFF")
            self.bar.pack()
            self.bar.configure(mode="indeterminate")
            self.bar.start()

    def destruir(self):
        # Detener animaciones antes de destruir para evitar errores zombies
        if self.bar:
            try: self.bar.stop()
            except: pass
        if self.spinner:
            self.spinner.stop()
        
        try: self.destroy()
        except: pass

def mostrar_loading(parent, duracion_ms, callback_final, tipo="barra", mensaje="Cargando..."):
    # 1. Verificar si el padre existe antes de intentar poner el loading
    try:
        if not parent.winfo_exists(): return
    except: return

    # 2. Crear overlay
    overlay = LoadingOverlay(parent, mensaje=mensaje, tipo=tipo)
    
    # 3. Forzar pintado inicial (protegido)
    try: parent.update_idletasks()
    except: pass
    
    def finalizar():
        # A. Ejecutar la carga pesada (callback) MIENTRAS el spinner existe
        try:
            if callback_final:
                callback_final()
            
            # Forzar a la interfaz a procesar los widgets nuevos
            if parent.winfo_exists():
                parent.update_idletasks() 
        except Exception as e:
            print(f"Error carga: {e}")
            
        # B. Destruir el spinner AL FINAL
        try:
            if overlay.winfo_exists():
                overlay.destruir()
        except: pass
            
    # 4. Programar el final (protegido)
    try:
        parent.after(duracion_ms, finalizar)
    except:
        if overlay.winfo_exists(): overlay.destruir()
        