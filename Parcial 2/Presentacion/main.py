import customtkinter as ctk 
from login_view import LoginApp


def main():
    ctk.set_appearance_mode("System")  
    ctk.set_default_color_theme("blue") 
    
    root = ctk.CTk() 
    
    root.title("Inicio de Sesión")
    root.geometry("400x300")
    root.resizable(True, True)
    
    app = LoginApp(root)
    root.mainloop()  

if __name__ == "__main__":
    main()