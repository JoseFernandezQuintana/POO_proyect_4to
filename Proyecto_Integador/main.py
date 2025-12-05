import customtkinter as ctk
from login_view import LoginApp
from dashboard_view import DashboardApp

def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    while True:
        # 1. Abrir Login
        root_login = ctk.CTk()
        login_app = LoginApp(root_login)
        root_login.mainloop()

        # 2. Verificar resultado del Login
        if login_app.login_exitoso:
            datos_usuario = login_app.datos_usuario
            # Destruimos la ventana de login completamente antes de abrir dashboard
            try: root_login.destroy()
            except: pass 
            
            # 3. Abrir Dashboard
            root_dash = ctk.CTk()
            app = DashboardApp(datos_usuario['nombre_completo'], datos_usuario['rol'], root_dash)
            root_dash.mainloop()
            
            # 4. Verificar si cerró sesión (Loop) o cerró App (Break)
            if app.app_closed_completely:
                break # Salir del ciclo While
        else:
            # Si cerró la ventana de login sin entrar
            break

# Configuración inicial de apariencia
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

def main():
    # 1. Creamos la ventana PRINCIPAL (Solo existirá una en todo el programa)
    root = ctk.CTk()
    root.title("Sistema de Gestión - Ortho Guzmán")
    
    # Ajustamos tamaño inicial para el Login
    width = 900
    height = 600
    center_window(root, width, height)

    # ---------------------------------------------------------
    # FUNCIÓN DE TRANSICIÓN: Del Login -> al Dashboard
    # ---------------------------------------------------------
    def abrir_dashboard(nombre_usuario, rol_usuario):
        print(f"Login exitoso. Iniciando Dashboard para: {nombre_usuario} ({rol_usuario})")
        
        # A. Limpiamos la ventana (Borramos el Login)
        for widget in root.winfo_children():
            widget.destroy()

        # B. Redimensionamos para el Dashboard (Más grande)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width-100}x{screen_height-100}+50+50")
        root.state('zoomed') # Maximizar ventana (en Windows)

        # C. Cargamos el Dashboard en la MISMA ventana
        # Nota: Asegúrate de que tu DashboardApp acepte (nombre, rol, root)
        DashboardApp(nombre_usuario, rol_usuario, root)

    # 2. Iniciamos la App mostrando primero el Login
    # Le pasamos la función 'abrir_dashboard' para que el Login sepa qué hacer al terminar
    app = LoginApp(root, on_login_success=abrir_dashboard)

    # 3. Mantenemos el programa vivo
    root.mainloop()

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

if __name__ == "__main__":
    main()



    