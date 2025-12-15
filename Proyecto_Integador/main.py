import customtkinter as ctk
import sys
from login_view import LoginApp
from dashboard_view import DashboardApp
from ui_utils import LoadingOverlay

# Configuración global de tema
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

def main():
    root = ctk.CTk()
    root.title("Futuras Sonrisas - Gestión")
    
    # Centrar ventana
    w, h = 900, 600
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

    # --- FUNCIÓN DE CIERRE SEGURO CON ANIMACIÓN ---
    def cerrar_programa():
        try:
            # 1. Animación de Desvanecimiento (Fade Out)
            alpha = 1.0
            for i in range(10):
                alpha -= 0.1
                if alpha < 0: alpha = 0
                root.attributes("-alpha", alpha)
                root.update()
                root.after(30) # Pequeña pausa visual (30ms)
            
            # 2. Detener mainloop y destruir
            root.quit()    # Detiene el bucle de eventos
            root.destroy() # Destruye la ventana visualmente
            sys.exit()     # Cierra el proceso de Python
        except Exception as e:
            print(f"Saliendo forzadamente: {e}")
            sys.exit()

    # Conectar la "X" de la ventana a nuestra función segura
    root.protocol("WM_DELETE_WINDOW", cerrar_programa)

    # 1. Poner pantalla de carga inicial
    loader = LoadingOverlay(root, mensaje="INICIANDO SISTEMA...", tipo="barra")
    root.update() 

    def iniciar_login():
        # Verificar que la ventana aún exista
        if not root.winfo_exists(): return
        
        loader.destruir() # Quitar carga
        # Iniciar flujo normal del Login
        LoginApp(root, on_login_success=transicion_a_dashboard)

    def transicion_a_dashboard(datos_usuario):
        if not root.winfo_exists(): return
        
        uid, nom, rol, _ = datos_usuario
        for widget in root.winfo_children(): widget.destroy()
        try: root.state('zoomed')
        except: root.geometry(f"{ws-50}x{hs-100}+25+25")
        DashboardApp(uid, nom, rol, root)

    # Simular carga de 2 segundos y luego mostrar login
    root.after(2000, iniciar_login)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()
