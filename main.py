# main.py
import tkinter as tk
from presentation.login_view import LoginView
from presentation.main_window import MainWindow


def main():
    root = tk.Tk()
    root.title("Sistema de Asistencia Estudiantil")
    root.geometry("900x600")
    root.resizable(False, False)

    # Centrar ventana
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - 900) // 2
    y = (sh - 600) // 2
    root.geometry(f"900x600+{x}+{y}")

    def mostrar_panel(profesor_id, nombre_profesor): # <-- Debe tener estos dos
        for widget in root.winfo_children():
            widget.destroy()
    
        from presentation.main_window import MainWindow
        # Pasamos los datos a la MainWindow
        MainWindow(root, profesor_id, nombre_profesor, on_logout=mostrar_login)

    def mostrar_login():
        for widget in root.winfo_children():
            widget.destroy()
    
        from presentation.login_view import LoginView
        # Aquí conectamos el éxito con la función de arriba
        LoginView(root, on_success=mostrar_panel)

    # --- LAS DOS LÍNEAS QUE FALTABAN ---
    mostrar_login()  # 1. Llamamos a la función para cargar el login al inicio
    root.mainloop()  # 2. Esto mantiene la ventana abierta y escuchando clics


if __name__ == "__main__":
    main()