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

    def mostrar_login():
        # Limpiar ventana
        for widget in root.winfo_children():
            widget.destroy()
        LoginView(root, on_success=mostrar_panel)

    def mostrar_panel():
        # Limpiar ventana
        for widget in root.winfo_children():
            widget.destroy()
        MainWindow(root)

    mostrar_login()
    root.mainloop()


if __name__ == "__main__":
    main()