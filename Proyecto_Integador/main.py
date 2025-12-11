import customtkinter as ctk
from login_view import LoginApp
from dashboard_view import DashboardApp
from ui_utils import LoadingOverlay

# Configuración global de tema
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

def main():
    root = ctk.CTk()
    root.title("Futuras Sonrisas - Gestión")
    
    w, h = 900, 600
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

    # Poner pantalla de carga inicial
    # Se mostrará inmediatamente al abrir
    loader = LoadingOverlay(root, mensaje="INICIANDO SISTEMA...")
    root.update() 

    def iniciar_login():
        loader.destruir() # Quitar carga
        # Iniciar flujo normal del Login
        LoginApp(root, on_login_success=transicion_a_dashboard)

    def transicion_a_dashboard(datos_usuario):
        uid, nom, rol, _ = datos_usuario
        for widget in root.winfo_children(): widget.destroy()
        try: root.state('zoomed')
        except: root.geometry(f"{ws-50}x{hs-100}+25+25")
        DashboardApp(uid, nom, rol, root)

    # Simular carga de 2 segundos (2000ms) y luego mostrar login
    root.after(2000, iniciar_login)
    
    root.mainloop()

if __name__ == "__main__":
    main()
    