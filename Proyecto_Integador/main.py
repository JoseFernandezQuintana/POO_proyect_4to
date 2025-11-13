import customtkinter as ctk
from login_view import LoginApp
from dashboard_view import DashboardApp


def abrir_dashboard(username):
    """
    Crea una nueva raíz (ventana principal) para el Dashboard.
    Se ejecuta después de cerrar el login.
    """
    dashboard_root = ctk.CTk()
    dashboard_root.geometry("1400x900")
    dashboard_root.title(f"Dashboard | Bienvenido, {username}")
    DashboardApp(username, dashboard_root)
    dashboard_root.mainloop()


def cerrar_y_abrir_dashboard(root, username):
    """
    Cierra la ventana de login de forma segura y abre el Dashboard.
    Cancela todos los procesos 'after' activos antes de destruir la ventana.
    """
    try:
        after_ids = root.tk.call('after', 'info')
        # Si devuelve una cadena (versiones antiguas de tkinter)
        if isinstance(after_ids, str):
            after_ids = after_ids.split()
        # Si devuelve una tupla (versiones nuevas)
        elif not isinstance(after_ids, (list, tuple)):
            after_ids = [after_ids]

        for after_id in after_ids:
            try:
                root.after_cancel(after_id)
            except Exception:
                pass
    except Exception:
        pass

    # Destruye la ventana del login
    root.destroy()

    # Abre el Dashboard en una nueva ventana
    abrir_dashboard(username)


def main():
    """
    Punto de entrada principal de la aplicación.
    Inicia el login y conecta la transición segura al dashboard.
    """
    # Configuración global de tema y apariencia
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Crear ventana principal (Login)
    root = ctk.CTk()
    root.geometry("1100x650")
    root.resizable(False, False)
    root.title("Sistema de Gestión de Citas - Ortho Guzmán")

    # Crear la instancia del login
    app = LoginApp(root)

    # --- Integración segura entre Login y Dashboard ---
    # Agregamos una referencia para que LoginApp pueda llamar a esta función
    app.cerrar_y_abrir_dashboard = lambda username: cerrar_y_abrir_dashboard(root, username)

    # Ejecutar la interfaz
    root.mainloop()


if __name__ == "__main__":
    main()



    