# main.py
import customtkinter as ctk
from presentation.theme import apply_root_style


def main():
    root = ctk.CTk()
    apply_root_style(root, title="Sistema de Asistencia Estudiantil", geometry="1100x700")

    def mostrar_panel(profesor_id, nombre_profesor):
        for widget in root.winfo_children():
            widget.destroy()

        from presentation.main_window import MainWindow
        MainWindow(root, profesor_id, nombre_profesor, on_logout=mostrar_login)

    def mostrar_login():
        for widget in root.winfo_children():
            widget.destroy()

        from presentation.login_view import LoginView
        LoginView(root, on_success=mostrar_panel)

    mostrar_login()
    root.mainloop()


if __name__ == "__main__":
    main()