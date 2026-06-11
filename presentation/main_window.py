# presentation/main_window.py
import customtkinter as ctk
from tkinter import messagebox

from presentation.theme import (
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_PANEL_2,
    COLOR_BORDE,
    COLOR_TEXTO,
    COLOR_TEXTO_SEC,
    COLOR_MUTED,
    COLOR_PRIMARIO,
    COLOR_PRIMARIO_HOVER,
    COLOR_EXITO,
    COLOR_EXITO_HOVER,
    COLOR_ADVERTENCIA,
    COLOR_ERROR,
    COLOR_ERROR_HOVER,
    SIDEBAR_WIDTH,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_TEXT,
    FONT_TEXT_BOLD,
    FONT_BUTTON,
    primary_button,
    success_button,
    danger_button,
    transparent_button,
)


class MainWindow(ctk.CTkFrame):
    def __init__(self, root, profesor_id, nombre_profesor, on_logout=None):
        super().__init__(root, fg_color=COLOR_FONDO)

        self.root = root
        self.profesor_id = profesor_id
        self.nombre_profesor = nombre_profesor
        self.on_logout = on_logout

        self.root.title(f"Asistencia - Prof. {self.nombre_profesor}")

        try:
            self.root.state("zoomed")
        except Exception:
            self.root.geometry("1200x750")

        self.pack(fill="both", expand=True)
        self._build_ui()

    def _build_ui(self):
        # Layout principal
        self.sidebar = ctk.CTkFrame(
            self,
            width=SIDEBAR_WIDTH,
            fg_color=COLOR_PANEL,
            corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_container = ctk.CTkFrame(
            self,
            fg_color=COLOR_FONDO,
            corner_radius=0,
        )
        self.main_container.pack(side="right", fill="both", expand=True)

        self._build_sidebar()
        self._show_dashboard()

    def _build_sidebar(self):
        # Encabezado del profesor
        self.user_box = ctk.CTkFrame(
            self.sidebar,
            fg_color=COLOR_PANEL_2,
            corner_radius=18,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        self.user_box.pack(fill="x", padx=18, pady=(25, 20))

        ctk.CTkLabel(
            self.user_box,
            text="👨‍🏫",
            font=("Segoe UI Emoji", 34),
        ).pack(pady=(18, 4))

        ctk.CTkLabel(
            self.user_box,
            text="Bienvenido",
            font=FONT_TEXT,
            text_color=COLOR_TEXTO_SEC,
        ).pack()

        ctk.CTkLabel(
            self.user_box,
            text=self.nombre_profesor,
            font=FONT_TEXT_BOLD,
            text_color=COLOR_TEXTO,
            wraplength=210,
        ).pack(pady=(2, 18))

        # Menú
        self._menu_button("🏠  Panel de control", self._show_dashboard)
        self._menu_button("📚  Gestión de cursos", self._show_cursos)

        ctk.CTkLabel(
            self.sidebar,
            text="Sistema de asistencia facial",
            font=("Segoe UI", 11),
            text_color=COLOR_MUTED,
        ).pack(side="bottom", pady=(0, 8))

        self.btn_logout = danger_button(
            self.sidebar,
            text="Cerrar sesión",
            command=self.on_logout,
        )
        self.btn_logout.configure(
            fg_color=COLOR_ERROR,
            hover_color=COLOR_ERROR_HOVER,
        )
        self.btn_logout.pack(side="bottom", fill="x", padx=18, pady=(10, 20))

    def _menu_button(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            command=command,
            height=44,
            corner_radius=12,
            anchor="w",
            font=FONT_TEXT_BOLD,
            fg_color="transparent",
            hover_color=COLOR_BORDE,
            text_color=COLOR_TEXTO,
        )
        btn.pack(fill="x", padx=18, pady=5)

    # ─────────────────────────────────────
    # VISTAS
    # ─────────────────────────────────────

    def _show_dashboard(self):
        self._limpiar()

        header = self._header_page(
            titulo="Panel de control",
            subtitulo=f"Bienvenido, Prof. {self.nombre_profesor}. Administra cursos, estudiantes y reportes.",
        )

        stats_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        stats_frame.pack(fill="x", padx=40, pady=(10, 20))

        resumen = self._obtener_resumen_dashboard()

        self._stat_card(
            stats_frame,
            "Cursos activos",
            str(resumen["cursos"]),
            "📚",
            COLOR_PRIMARIO,
            0,
        )
        self._stat_card(
            stats_frame,
            "Estudiantes",
            str(resumen["estudiantes"]),
            "👥",
            COLOR_EXITO,
            1,
        )
        self._stat_card(
            stats_frame,
            "Asistencias hoy",
            str(resumen["asistencias_hoy"]),
            "✅",
            COLOR_ADVERTENCIA,
            2,
        )

        info = ctk.CTkFrame(
            self.main_container,
            fg_color=COLOR_PANEL,
            corner_radius=18,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        info.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        ctk.CTkLabel(
            info,
            text="Inicio rápido",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXTO,
        ).pack(anchor="w", padx=28, pady=(25, 8))

        ctk.CTkLabel(
            info,
            text="Selecciona Gestión de cursos para crear cursos, registrar estudiantes, pasar asistencia facial y generar reportes.",
            font=FONT_TEXT,
            text_color=COLOR_TEXTO_SEC,
            wraplength=780,
            justify="left",
        ).pack(anchor="w", padx=28, pady=(0, 25))

        btn = primary_button(
            info,
            text="Ir a Gestión de cursos",
            command=self._show_cursos,
        )
        btn.pack(anchor="w", padx=28, pady=(0, 25))

    def _show_cursos(self):
        self._limpiar()

        header = self._header_page(
            titulo="Mis cursos",
            subtitulo="Crea, consulta y administra los grupos asociados a tu cuenta.",
        )

        btn_crear = success_button(
            header,
            text="+ Crear nuevo curso",
            command=self._crear_curso_modal,
        )
        btn_crear.pack(side="right", padx=40, pady=22)

        self.cursos_container = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color="transparent",
        )
        self.cursos_container.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        try:
            from infrastructure.database.db_manager import DatabaseManager

            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, nombre_curso, grupo
                FROM cursos
                WHERE id_profesor = ?
                ORDER BY nombre_curso ASC
                """,
                (self.profesor_id,),
            )
            cursos = cursor.fetchall()
            conn.close()

            if not cursos:
                self._empty_state(
                    self.cursos_container,
                    "No tienes cursos creados aún.",
                    "Crea tu primer curso para empezar a registrar estudiantes.",
                )
                return

            for curso_id, nombre, grupo in cursos:
                self._curso_item(
                    self.cursos_container,
                    curso_id,
                    nombre,
                    grupo,
                )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudieron cargar los cursos:\n{e}",
            )

    def _abrir_menu_curso(self, curso_id, nombre_curso):
        self._limpiar()

        header = self._header_page(
            titulo=f"Gestionando: {nombre_curso}",
            subtitulo="Selecciona una acción para este curso.",
        )

        btn_volver = transparent_button(
            header,
            text="← Volver a cursos",
            command=self._show_cursos,
        )
        btn_volver.pack(side="right", padx=40, pady=22)

        grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        grid.pack(expand=True)

        opciones = [
            {
                "titulo": "Registrar estudiantes",
                "subtitulo": "Agregar datos y escaneo facial",
                "icono": "👤",
                "color": COLOR_EXITO,
                "command": lambda: self._action_registrar(curso_id, nombre_curso),
            },
            {
                "titulo": "Pasar asistencia",
                "subtitulo": "Reconocimiento facial en vivo",
                "icono": "📷",
                "color": COLOR_PRIMARIO,
                "command": lambda: self._action_asistencia(curso_id, nombre_curso),
            },
            {
                "titulo": "Ver asistencias",
                "subtitulo": "Historial por fecha o estudiante",
                "icono": "📋",
                "color": COLOR_ADVERTENCIA,
                "command": lambda: self._action_ver_asistencias(curso_id, nombre_curso),
            },
            {
                "titulo": "Reportes del curso",
                "subtitulo": "Exportar sábana consolidada",
                "icono": "📊",
                "color": "#8b5cf6",
                "command": lambda: self._action_reportes(curso_id, nombre_curso),
            },
        ]

        for i, item in enumerate(opciones):
            row, col = divmod(i, 2)
            self._action_card(grid, item, row, col)

    # ─────────────────────────────────────
    # COMPONENTES VISUALES
    # ─────────────────────────────────────

    def _header_page(self, titulo, subtitulo):
        header = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
            height=100,
        )
        header.pack(fill="x", padx=0, pady=(0, 10))
        header.pack_propagate(False)

        text_box = ctk.CTkFrame(header, fg_color="transparent")
        text_box.pack(side="left", padx=40, pady=18)

        ctk.CTkLabel(
            text_box,
            text=titulo,
            font=FONT_TITLE,
            text_color=COLOR_TEXTO,
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_box,
            text=subtitulo,
            font=FONT_TEXT,
            text_color=COLOR_TEXTO_SEC,
        ).pack(anchor="w", pady=(4, 0))

        return header

    def _stat_card(self, parent, title, value, icon, color, column):
        parent.grid_columnconfigure(column, weight=1)

        card = ctk.CTkFrame(
            parent,
            fg_color=COLOR_PANEL,
            corner_radius=18,
            border_width=1,
            border_color=COLOR_BORDE,
            height=130,
        )
        card.grid(row=0, column=column, sticky="ew", padx=8)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=icon,
            font=("Segoe UI Emoji", 28),
        ).pack(anchor="w", padx=22, pady=(18, 0))

        ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 28, "bold"),
            text_color=color,
        ).pack(anchor="w", padx=22)

        ctk.CTkLabel(
            card,
            text=title,
            font=FONT_TEXT,
            text_color=COLOR_TEXTO_SEC,
        ).pack(anchor="w", padx=22)

    def _curso_item(self, parent, curso_id, nombre, grupo):
        frame = ctk.CTkFrame(
            parent,
            fg_color=COLOR_PANEL,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        frame.pack(fill="x", pady=8)

        left = ctk.CTkFrame(frame, fg_color="transparent")
        left.pack(side="left", padx=22, pady=18)

        ctk.CTkLabel(
            left,
            text=f"{nombre}",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXTO,
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=f"Grupo {grupo}",
            font=FONT_TEXT,
            text_color=COLOR_TEXTO_SEC,
        ).pack(anchor="w", pady=(3, 0))

        btn = primary_button(
            frame,
            text="Abrir curso",
            command=lambda: self._abrir_menu_curso(curso_id, f"{nombre} – Grupo {grupo}"),
        )
        btn.pack(side="right", padx=22, pady=18)

    def _action_card(self, parent, item, row, col):
        card = ctk.CTkFrame(
            parent,
            width=300,
            height=190,
            fg_color=COLOR_PANEL,
            corner_radius=20,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        card.grid(row=row, column=col, padx=18, pady=18)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=item["icono"],
            font=("Segoe UI Emoji", 34),
        ).pack(pady=(22, 6))

        ctk.CTkLabel(
            card,
            text=item["titulo"],
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXTO,
        ).pack()

        ctk.CTkLabel(
            card,
            text=item["subtitulo"],
            font=FONT_TEXT,
            text_color=COLOR_TEXTO_SEC,
        ).pack(pady=(4, 14))

        btn = ctk.CTkButton(
            card,
            text="Abrir",
            command=item["command"],
            fg_color=item["color"],
            hover_color=self._darken(item["color"]),
            height=36,
            corner_radius=10,
            font=FONT_TEXT_BOLD,
        )
        btn.pack(padx=22, fill="x")

    def _empty_state(self, parent, titulo, subtitulo):
        box = ctk.CTkFrame(
            parent,
            fg_color=COLOR_PANEL,
            corner_radius=18,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        box.pack(fill="x", pady=20)

        ctk.CTkLabel(
            box,
            text="📭",
            font=("Segoe UI Emoji", 42),
        ).pack(pady=(35, 8))

        ctk.CTkLabel(
            box,
            text=titulo,
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXTO,
        ).pack()

        ctk.CTkLabel(
            box,
            text=subtitulo,
            font=FONT_TEXT,
            text_color=COLOR_TEXTO_SEC,
        ).pack(pady=(5, 35))

    # ─────────────────────────────────────
    # MODAL CURSO
    # ─────────────────────────────────────

    def _crear_curso_modal(self):
        modal = ctk.CTkToplevel(self.root)
        modal.title("Nuevo curso")
        modal.geometry("420x330")
        modal.resizable(False, False)
        modal.configure(fg_color=COLOR_FONDO)
        modal.grab_set()

        frame = ctk.CTkFrame(
            modal,
            fg_color=COLOR_PANEL,
            corner_radius=18,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        frame.pack(fill="both", expand=True, padx=22, pady=22)

        ctk.CTkLabel(
            frame,
            text="Crear nuevo curso",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXTO,
        ).pack(pady=(25, 18))

        nombre_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Asignatura",
            height=42,
            fg_color=COLOR_PANEL_2,
            border_color=COLOR_BORDE,
            text_color=COLOR_TEXTO,
        )
        nombre_entry.pack(fill="x", padx=30, pady=(0, 14))

        grupo_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Grupo, ejemplo: A",
            height=42,
            fg_color=COLOR_PANEL_2,
            border_color=COLOR_BORDE,
            text_color=COLOR_TEXTO,
        )
        grupo_entry.pack(fill="x", padx=30, pady=(0, 22))

        def guardar():
            asignatura = nombre_entry.get().strip()
            grupo = grupo_entry.get().strip().upper()

            if not asignatura or not grupo:
                messagebox.showwarning(
                    "Atención",
                    "Completa asignatura y grupo.",
                )
                return

            try:
                from infrastructure.database.db_manager import DatabaseManager

                db = DatabaseManager()
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO cursos (nombre_curso, grupo, id_profesor)
                    VALUES (?, ?, ?)
                    """,
                    (asignatura, grupo, self.profesor_id),
                )
                conn.commit()
                conn.close()

                messagebox.showinfo(
                    "Éxito",
                    f"Curso '{asignatura}' – Grupo {grupo} creado.",
                )
                modal.destroy()
                self._show_cursos()

            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"No se pudo guardar el curso:\n{e}",
                )

        btn_guardar = success_button(
            frame,
            text="Guardar curso",
            command=guardar,
        )
        btn_guardar.pack(fill="x", padx=30)

    # ─────────────────────────────────────
    # ACCIONES
    # ─────────────────────────────────────

    def _action_registrar(self, curso_id, nombre_curso):
        self._limpiar()
        try:
            from infrastructure.database.db_manager import DatabaseManager
            from infrastructure.database.student_repo import StudentRepository
            from application.student_service import StudentService
            from presentation.register_view import RegisterView

            db = DatabaseManager()
            repo = StudentRepository(db)
            service = StudentService(repo)

            RegisterView(
                parent=self.main_container,
                student_service=service,
                profesor_id=self.profesor_id,
                curso_id=curso_id,
                nombre_curso=nombre_curso,
                on_volver=lambda: self._abrir_menu_curso(curso_id, nombre_curso),
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el registro:\n{e}",
        )

    def _action_asistencia(self, curso_id, nombre_curso):
        self._limpiar()
        try:
            from infrastructure.database.db_manager import DatabaseManager
            from presentation.attendance_view import AttendanceView

            db = DatabaseManager()

            AttendanceView(
                parent=self.main_container,
                profesor_id=self.profesor_id,
                db_manager=db,
                on_volver=lambda: self._abrir_menu_curso(curso_id, nombre_curso),
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir la toma de asistencia:\n{e}",
            )

    def _action_ver_asistencias(self, curso_id, nombre_curso):
        self._limpiar()
        try:
            from infrastructure.database.db_manager import DatabaseManager
            from presentation.history_view import HistoryView

            db = DatabaseManager()

            HistoryView(
                parent=self.main_container,
                curso_id=curso_id,
                db_manager=db,
                on_volver=lambda: self._abrir_menu_curso(curso_id, nombre_curso),
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el historial:\n{e}",
            )

    def _action_reportes(self, curso_id, nombre_curso):
        self._limpiar()
        try:
            from infrastructure.database.db_manager import DatabaseManager
            from presentation.report_view import ReportView

            db = DatabaseManager()

            ReportView(
                parent=self.main_container,
                curso_id=curso_id,
                db_manager=db,
                on_volver=lambda: self._abrir_menu_curso(curso_id, nombre_curso),
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir reportes:\n{e}",
            )

    # ─────────────────────────────────────
    # DATOS DASHBOARD
    # ─────────────────────────────────────

    def _obtener_resumen_dashboard(self):
        resumen = {
            "cursos": 0,
            "estudiantes": 0,
            "asistencias_hoy": 0,
        }

        try:
            from datetime import date
            from infrastructure.database.db_manager import DatabaseManager

            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM cursos WHERE id_profesor = ?",
                (self.profesor_id,),
            )
            resumen["cursos"] = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(e.id)
                FROM estudiantes e
                INNER JOIN cursos c ON e.id_curso = c.id
                WHERE c.id_profesor = ?
                """,
                (self.profesor_id,),
            )
            resumen["estudiantes"] = cursor.fetchone()[0]

            hoy = date.today().isoformat()
            cursor.execute(
                """
                SELECT COUNT(a.id)
                FROM asistencias a
                INNER JOIN cursos c ON a.id_curso = c.id
                WHERE c.id_profesor = ? AND a.fecha = ?
                """,
                (self.profesor_id, hoy),
            )
            resumen["asistencias_hoy"] = cursor.fetchone()[0]

            conn.close()

        except Exception:
            pass

        return resumen

    # ─────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────

    def _limpiar(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    @staticmethod
    def _darken(hex_color, factor=0.85):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        return f"#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}"