# presentation/profesor_register_view.py
import customtkinter as ctk
from tkinter import messagebox

from infrastructure.database.db_manager import DatabaseManager
from presentation.theme import (
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_PANEL_2,
    COLOR_BORDE,
    COLOR_TEXTO,
    COLOR_TEXTO_SEC,
    COLOR_EXITO,
    COLOR_EXITO_HOVER,
    COLOR_ERROR,
    FONT_TITLE,
    FONT_TEXT,
    FONT_TEXT_BOLD,
    FONT_BUTTON,
    input_text,
    success_button,
    transparent_button,
)


class ProfesorRegisterView(ctk.CTkFrame):
    def __init__(self, root, on_back=None):
        super().__init__(root, fg_color=COLOR_FONDO)
        self.root = root
        self.on_back = on_back
        self.db = DatabaseManager()

        self.pack(fill="both", expand=True)
        self._build_ui()

    def _build_ui(self):
        self.card = ctk.CTkFrame(
            self,
            fg_color=COLOR_PANEL,
            corner_radius=22,
            border_width=1,
            border_color=COLOR_BORDE,
            width=450,
            height=610,
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        ctk.CTkLabel(
            self.card,
            text="Crear cuenta de profesor",
            font=FONT_TITLE,
            text_color=COLOR_TEXTO,
        ).pack(pady=(35, 8))

        ctk.CTkLabel(
            self.card,
            text="Registra tus datos para gestionar cursos y asistencia",
            font=FONT_TEXT,
            text_color=COLOR_TEXTO_SEC,
        ).pack(pady=(0, 25))

        self.nombre_entry = self._crear_campo(
            "Nombre completo",
            "Ingrese nombre y apellidos",
        )

        self.correo_entry = self._crear_campo(
            "Correo electrónico",
            "ejemplo@correo.com",
        )

        self.inst_entry = self._crear_campo(
            "Institución educativa",
            "Nombre de la institución",
        )

        self.pin_entry = self._crear_campo(
            "PIN de seguridad",
            "4 dígitos",
            show="●",
        )

        self.btn_registrar = success_button(
            self.card,
            text="CREAR CUENTA",
            command=self._registrar_profesor,
        )
        self.btn_registrar.configure(
            fg_color=COLOR_EXITO,
            hover_color=COLOR_EXITO_HOVER,
        )
        self.btn_registrar.pack(fill="x", padx=45, pady=(18, 12))

        self.btn_volver = transparent_button(
            self.card,
            text="← Volver al inicio de sesión",
            command=self._volver,
        )
        self.btn_volver.pack(fill="x", padx=45)

    def _crear_campo(self, label_text, placeholder, show=None):
        ctk.CTkLabel(
            self.card,
            text=label_text,
            font=FONT_TEXT_BOLD,
            text_color=COLOR_TEXTO_SEC,
        ).pack(anchor="w", padx=45, pady=(8, 6))

        entry = input_text(
            self.card,
            placeholder=placeholder,
            show=show,
        )
        entry.pack(fill="x", padx=45, pady=(0, 10))
        return entry

    def _registrar_profesor(self):
        nombre = self.nombre_entry.get().strip()
        correo = self.correo_entry.get().strip()
        institucion = self.inst_entry.get().strip()
        pin = self.pin_entry.get().strip()

        if not nombre or not correo or not pin:
            messagebox.showwarning(
                "Atención",
                "Complete nombre, correo y PIN.",
            )
            return

        if not pin.isdigit() or len(pin) != 4:
            messagebox.showwarning(
                "PIN inválido",
                "El PIN debe tener exactamente 4 números.",
            )
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO profesores (nombre, correo, pin, institucion)
                VALUES (?, ?, ?, ?)
                """,
                (nombre, correo, pin, institucion),
            )
            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Éxito",
                "Cuenta creada correctamente. Ahora puedes iniciar sesión.",
            )
            self._volver()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"El correo ya está registrado o hubo un error:\n{e}",
            )

    def _volver(self):
        self.destroy()
        if self.on_back:
            self.on_back()