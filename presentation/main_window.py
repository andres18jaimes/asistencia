import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

ASSETS_DIR = "assets"
TAMANO_ICONO = (50, 50)

class MainWindow:
    def __init__(self, root, profesor_id, nombre_profesor, on_logout=None):
        self.root = root
        self.profesor_id = profesor_id
        self.nombre_profesor = nombre_profesor
        self.on_logout = on_logout

        self.root.title(f"Asistencia - Prof. {self.nombre_profesor}")
        self.root.configure(bg="#F5F6FA")
        self.root.attributes('-zoomed', True)

        self.iconos = {}
        self._preparar_iconos()
        self._build_ui()

    def _preparar_iconos(self):
        iconos_a_cargar = {
            "registrar": "user.png",
            "rostro":    "face.png",
            "lista":     "list.png",
            "reporte":   "report.png"
        }
        for clave, archivo in iconos_a_cargar.items():
            try:
                ruta = os.path.join(ASSETS_DIR, archivo)
                img = Image.open(ruta).convert("RGBA")
                img = img.resize(TAMANO_ICONO, Image.Resampling.LANCZOS)
                self.iconos[clave] = ImageTk.PhotoImage(img)
            except Exception:
                self.iconos[clave] = None

    def _build_ui(self):
        self.sidebar = tk.Frame(self.root, bg="#2C3E50", width=250)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(
            self.sidebar,
            text=f"Bienvenido,\n{self.nombre_profesor}",
            font=("Arial", 12, "bold"), bg="#2C3E50", fg="white", justify="center"
        ).pack(pady=30, padx=10)

        self._menu_button("Panel de Control", self._show_dashboard)
        self._menu_button("Gestión de Cursos", self._show_cursos)

        tk.Button(
            self.sidebar, text="Cerrar Sesión", bg="#D9534F", fg="white",
            relief="flat", font=("Arial", 10, "bold"), cursor="hand2",
            command=self.on_logout
        ).pack(side="bottom", fill="x", pady=20, padx=20, ipady=8)

        self.main_container = tk.Frame(self.root, bg="#F5F6FA")
        self.main_container.pack(side="right", expand=True, fill="both")

        self._show_dashboard()

    def _menu_button(self, text, command):
        tk.Button(
            self.sidebar, text=text, font=("Arial", 11),
            bg="#34495E", fg="white", relief="flat", activebackground="#4F79A7",
            cursor="hand2", command=command
        ).pack(fill="x", pady=2, padx=15, ipady=10)

    # ── Vistas ───────────────────────────────────────────────────────────────

    def _show_dashboard(self):
        self._limpiar()
        tk.Label(
            self.main_container, text="Panel de Control",
            font=("Arial", 28, "bold"), bg="#F5F6FA", fg="#2C3E50"
        ).pack(pady=(50, 10), padx=60, anchor="w")

        tk.Label(
            self.main_container,
            text=f"Bienvenido, Prof. {self.nombre_profesor}. Seleccione su curso para trabajar.",
            font=("Arial", 12), bg="#F5F6FA", fg="#7F8C8D"
        ).pack(pady=(0, 40), padx=60, anchor="w")

    def _show_cursos(self):
        self._limpiar()

        header_frame = tk.Frame(self.main_container, bg="#F5F6FA")
        header_frame.pack(fill="x", padx=40, pady=20)

        tk.Label(
            header_frame, text="Mis Cursos",
            font=("Arial", 22, "bold"), bg="#F5F6FA", fg="#2C3E50"
        ).pack(side="left")

        tk.Button(
            header_frame, text="+ Crear Nuevo Curso", bg="#27AE60", fg="white",
            font=("Arial", 10, "bold"), relief="flat", padx=15,
            command=self._crear_curso_modal
        ).pack(side="right")

        try:
            from infrastructure.database.db_manager import DatabaseManager
            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nombre_curso, grupo FROM cursos WHERE id_profesor = ?",
                (self.profesor_id,)
            )
            cursos = cursor.fetchall()
            conn.close()

            if not cursos:
                tk.Label(
                    self.main_container,
                    text="No tienes cursos creados aún.",
                    font=("Arial", 12), bg="#F5F6FA", fg="#7F8C8D"
                ).pack(pady=40)
            else:
                for curso_id, nombre, grupo in cursos:
                    self._create_curso_item(
                        self.main_container, curso_id, f"{nombre}  –  Grupo {grupo}"
                    )

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los cursos:\n{e}")

    def _abrir_menu_curso(self, curso_id, nombre_curso):
        self._limpiar()

        header = tk.Frame(self.main_container, bg="#F5F6FA")
        header.pack(fill="x", padx=40, pady=20)

        tk.Button(
            header, text="← Volver a Cursos", command=self._show_cursos,
            bg="#95a5a6", fg="white", relief="flat"
        ).pack(side="left")

        tk.Label(
            header, text=f"Gestionando: {nombre_curso}",
            font=("Arial", 18, "bold"), bg="#F5F6FA", fg="#2C3E50"
        ).pack(side="left", padx=20)

        grid_frame = tk.Frame(self.main_container, bg="#F5F6FA")
        grid_frame.pack(expand=True)

        opciones = [
            ("Registrar Estudiantes", "#5CB85C", "registrar",
             lambda cid=curso_id, nc=nombre_curso: self._action_registrar(cid, nc)),
            ("Pasar Asistencia",      "#5BC0DE", "rostro",
             lambda cid=curso_id, nc=nombre_curso: self._action_asistencia(cid, nc)),
            ("Ver Asistencias",       "#F0AD4E", "lista",
             lambda cid=curso_id: self._action_ver_asistencias(cid)),
            ("Reportes del Curso",    "#4E79A7", "reporte",
             lambda cid=curso_id: self._action_reportes(cid)),
        ]

        for i, (text, color, icon, cmd) in enumerate(opciones):
            row, col = divmod(i, 2)
            self._create_card(grid_frame, text, color, row, col, self.iconos.get(icon), cmd)

    # ── Widgets reutilizables ────────────────────────────────────────────────

    def _create_card(self, parent, text, color, row, col, image, command):
        card = tk.Frame(parent, bg="white", bd=0, cursor="hand2", width=220, height=180)
        card.grid(row=row, column=col, padx=20, pady=20)
        card.pack_propagate(False)

        inner = tk.Frame(card, bg=color)
        inner.place(relx=0, rely=0, relwidth=1, relheight=1)

        if image:
            tk.Label(inner, image=image, bg=color).pack(pady=(25, 5))

        tk.Label(inner, text=text, bg=color, fg="white", font=("Arial", 11, "bold")).pack()

        color_hover = self._darken(color)
        for w in (card, inner, *inner.winfo_children()):
            w.bind("<Button-1>", lambda e, c=command: c())
            w.bind("<Enter>",    lambda e, ci=inner, ch=color_hover: ci.configure(bg=ch))
            w.bind("<Leave>",    lambda e, ci=inner, co=color:       ci.configure(bg=co))

    def _create_curso_item(self, parent, curso_id, nombre_completo):
        frame = tk.Frame(parent, bg="white", bd=1, relief="solid", cursor="hand2")
        frame.pack(fill="x", pady=5, padx=40, ipady=15)

        label = tk.Label(frame, text=nombre_completo, font=("Arial", 12, "bold"), bg="white")
        label.pack(side="left", padx=20)

        for widget in (frame, label):
            widget.bind(
                "<Button-1>",
                lambda e, cid=curso_id, nc=nombre_completo: self._abrir_menu_curso(cid, nc)
            )

    # ── Modal crear curso ────────────────────────────────────────────────────

    def _crear_curso_modal(self):
        modal = tk.Toplevel(self.root)
        modal.title("Nuevo Curso / Grupo")
        modal.geometry("350x300")
        modal.configure(bg="white")
        modal.grab_set()

        tk.Label(modal, text="Asignatura:", bg="white", font=("Arial", 10, "bold")).pack(pady=(15, 0))
        nombre_var = tk.StringVar()
        tk.Entry(modal, textvariable=nombre_var, font=("Arial", 11), relief="solid", bd=1).pack(pady=5, padx=30, fill="x")

        tk.Label(modal, text="Grupo (A, B, C...):", bg="white", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        grupo_var = tk.StringVar()
        tk.Entry(modal, textvariable=grupo_var, font=("Arial", 11), relief="solid", bd=1).pack(pady=5, padx=30, fill="x")

        def guardar():
            asignatura = nombre_var.get().strip()
            grupo      = grupo_var.get().strip().upper()
            if not asignatura or not grupo:
                messagebox.showwarning("Atención", "Completa Asignatura y Grupo.")
                return
            try:
                from infrastructure.database.db_manager import DatabaseManager
                db = DatabaseManager()
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO cursos (nombre_curso, grupo, id_profesor) VALUES (?, ?, ?)",
                    (asignatura, grupo, self.profesor_id)
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", f"Curso '{asignatura}' – Grupo {grupo} creado.")
                modal.destroy()
                self._show_cursos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el curso:\n{e}")

        tk.Button(
            modal, text="Guardar Curso", bg="#27AE60", fg="white",
            font=("Arial", 10, "bold"), command=guardar
        ).pack(pady=25)

    # ── Acciones ─────────────────────────────────────────────────────────────

    def _action_registrar(self, curso_id, nombre_curso):
        self._limpiar()
        try:
            from infrastructure.database.db_manager import DatabaseManager
            from infrastructure.database.student_repo import StudentRepository
            from application.student_service import StudentService
            from presentation.register_view import RegisterView

            db      = DatabaseManager()
            repo    = StudentRepository(db)
            service = StudentService(repo)

            RegisterView(
                parent          = self.main_container,
                student_service = service,
                profesor_id     = self.profesor_id,
                on_volver       = self._show_cursos,
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el registro:\n{e}")

    def _action_asistencia(self, curso_id, nombre_curso):
        self._limpiar()
        try:
            from infrastructure.database.db_manager import DatabaseManager
            from presentation.attendance_view import AttendanceView

            db = DatabaseManager()

            AttendanceView(
                parent      = self.main_container,
                profesor_id = self.profesor_id,
                db_manager  = db,
                on_volver   = self._show_cursos,
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la toma de asistencia:\n{e}")

    def _action_ver_asistencias(self, curso_id):
        messagebox.showinfo("Próximamente", f"Ver asistencias del curso {curso_id}")

    def _action_reportes(self, curso_id):
        messagebox.showinfo("Próximamente", f"Reporte del curso {curso_id}")

    # ── Utilidades ───────────────────────────────────────────────────────────

    def _limpiar(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    @staticmethod
    def _darken(hex_color, factor=0.85):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"