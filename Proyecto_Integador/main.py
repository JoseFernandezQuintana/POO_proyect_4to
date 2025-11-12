import customtkinter as ctk
from login_view import LoginApp

def main():
    # Establecer la apariencia clara (light) y tema azul (blue)
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    # El título se define en LoginApp para que se asocie a la ventana principal.
    # root.title("Sistema de Gestión de Citas - Ortho Guzmán") 
    
    # Geometría más grande para el diseño de dos paneles
    root.geometry("1100x650") 
    root.resizable(False, False)

    # Inicializar la aplicación de login
    app = LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

    