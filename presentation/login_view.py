# presentation/login_view.py
import customtkinter as ctk
from tkinter import messagebox

from presentation.theme import (
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_PANEL_2,
    COLOR_BORDE,
    COLOR_TEXTO,
    COLOR_TEXTO_SEC,
    COLOR_PRIMARIO,
    COLOR_PRIMARIO_HOVER,
    COLOR_EXITO,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_TEXT,
    FONT_TEXT_BOLD,
    FONT_BUTTON,
    input_text,
    primary_button,
)


class LoginView(ctk.CTkFrame):
    def __init__(self, root, on_success=None):
        super().__init__(root, fg_color=COLOR_FONDO)
        self.root = root
        self.on_success = on_success

        self.pack(fill="both", expand=True)
        self._build_ui()

    def _build_ui(self):
        # Fondo general dividido visualmente
        self.container = ctk.CTkFrame(self, fg_color=COLOR_FONDO)
        self.container.pack(fill="both", expand=True)

        self.card = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_PANEL,
            corner_radius=22,
            border_width=1,
            border_color=COLOR_BORDE,
            width=420,
            height=560,
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # Icono superior
        self.icon_box = ctk.CTkFrame(
            self.card,
            width=92,
            height=92,
            corner_radius=28,
            fg_color=COLOR_PRIMARIO,
        )
        self.icon_box.pack(pady=(35, 18))
        self.icon_box.pack_propagate(False)

        ctk.CTkLabel(
            self.icon_box,
            text="🔐",
            font=("Segoe UI Emoji", 36),
            text_color=COLOR_TEXTO,
        ).pack(expand=True)

        ctk.CTkLabel(
            self.card,
            text="Sistema de Asistencia",
            font=FONT_TITLE,
            text_color=COLOR_TEXTO,
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            self.card,
            text="Ingreso seguro para docentes",
            font=FONT_TEXT,
            text_color=COLOR_TEXTO_SEC,
        ).pack(pady=(0, 30))

        # Campo correo
        ctk.CTkLabel(
            self.card,
            text="Correo electrónico",
            font=FONT_TEXT_BOLD,
            text_color=COLOR_TEXTO_SEC,
        ).pack(anchor="w", padx=45, pady=(0, 6))

        self.correo_entry = input_text(
            self.card,
            placeholder="ejemplo@correo.com",
        )
        self.correo_entry.pack(fill="x", padx=45, pady=(0, 18))

        # Campo PIN
        ctk.CTkLabel(
            self.card,
            text="PIN de seguridad",
            font=FONT_TEXT_BOLD,
            text_color=COLOR_TEXTO_SEC,
        ).pack(anchor="w", padx=45, pady=(0, 6))

        self.pin_entry = input_text(
            self.card,
            placeholder="Ingrese su PIN",
            show="●",
        )
        self.pin_entry.pack(fill="x", padx=45, pady=(0, 28))

        self.pin_entry.bind("<Return>", lambda e: self._ingresar())
        self.correo_entry.bind("<Return>", lambda e: self._ingresar())

        self.btn_ingresar = primary_button(
            self.card,
            text="INGRESAR",
            command=self._ingresar,
        )
        self.btn_ingresar.configure(
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
        )
        self.btn_ingresar.pack(fill="x", padx=45, pady=(0, 22))

        self.btn_registro = ctk.CTkButton(
            self.card,
            text="¿No tienes cuenta? Regístrate aquí",
            fg_color="transparent",
            hover_color=COLOR_PANEL_2,
            text_color=COLOR_EXITO,
            font=FONT_TEXT_BOLD,
            command=self._ir_a_registro,
        )
        self.btn_registro.pack(pady=(0, 10))

        ctk.CTkLabel(
            self.card,
            text="Reconocimiento facial • Cursos • Reportes",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXTO_SEC,
        ).pack(side="bottom", pady=22)

    def _ir_a_registro(self):
        self.destroy()
        from presentation.profesor_register_view import ProfesorRegisterView
        ProfesorRegisterView(self.root, on_back=self._volver_al_login)

    def _volver_al_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        LoginView(self.root, on_success=self.on_success)

    def _ingresar(self):
        correo = self.correo_entry.get().strip()
        pin = self.pin_entry.get().strip()

        if not correo or not pin:
            messagebox.showwarning("Atención", "Ingrese correo y PIN.")
            return

        try:
            from infrastructure.database.db_manager import DatabaseManager

            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, nombre FROM profesores WHERE correo = ? AND pin = ?",
                (correo, pin),
            )
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                if self.on_success:
                    self.on_success(resultado[0], resultado[1])
            else:
                messagebox.showerror("Error", "Correo o PIN incorrectos.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar sesión:\n{e}")