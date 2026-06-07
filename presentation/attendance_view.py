import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Callable
from datetime import date

# Configuración de colores modernos (Slate & Emerald)
COLOR_FONDO = "#0f172a"  # Azul muy oscuro
COLOR_PANEL = "#1e293b"  # Azul grisáceo
COLOR_ACCENTO = "#10b981" # Verde esmeralda (Éxito)
COLOR_BOTON_NORMAL = "#3b82f6" # Azul moderno

class AttendanceView(ctk.CTkFrame):
    def __init__(
        self,
        parent: ctk.CTk,
        profesor_id: int,
        db_manager,
        on_volver: Callable,
    ):
        # Heredamos de CTKFrame para que sea un componente moderno
        super().__init__(parent, fg_color=COLOR_FONDO)
        
        self.parent = parent
        self.profesor_id = profesor_id
        self.db = db_manager
        self.on_volver = on_volver
        self.pack(fill="both", expand=True)

        self._build_ui()
        self._cargar_cursos()
        self._cargar_asistencias_hoy()

    def _build_ui(self):
        # ── HEADER MODERNO ──
        self.header = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=COLOR_PANEL)
        self.header.pack(fill="x", side="top")

        self.btn_volver = ctk.CTkButton(
            self.header, 
            text="← Volver", 
            width=100,
            fg_color="transparent",
            hover_color="#334155",
            font=("Segoe UI", 14, "bold"),
            command=self._volver
        )
        self.btn_volver.pack(side="left", padx=20, pady=15)

        self.titulo = ctk.CTkLabel(
            self.header, 
            text="Toma de Asistencia Facial", 
            font=("Segoe UI", 20, "bold"),
            text_color="#f8fafc"
        )
        self.titulo.pack(side="left", padx=10)

        # ── CUERPO PRINCIPAL ──
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=40, pady=30)

        # Panel Superior: Controles
        self.panel_controles = ctk.CTkFrame(self.container, fg_color=COLOR_PANEL, corner_radius=15, border_width=1, border_color="#334155")
        self.panel_controles.pack(fill="x", pady=(0, 20), ipady=15)

        # Selección de Curso
        label_curso = ctk.CTkLabel(self.panel_controles, text="Curso Activo:", font=("Segoe UI", 13, "bold"))
        label_curso.pack(side="left", padx=(25, 10))

        self._combo_curso = ctk.CTkComboBox(
            self.panel_controles, 
            width=250, 
            values=[], 
            state="readonly",
            font=("Segoe UI", 13),
            fg_color="#0f172a"
        )
        self._combo_curso.pack(side="left", padx=10)

        # Botón de Inicio con Estilo
        self._btn_iniciar = ctk.CTkButton(
            self.panel_controles,
            text="▶  INICIAR RECONOCIMIENTO",
            font=("Segoe UI", 14, "bold"),
            fg_color=COLOR_BOTON_NORMAL,
            hover_color="#2563eb",
            height=45,
            corner_radius=10,
            command=self._iniciar_captura
        )
        self._btn_iniciar.pack(side="left", padx=30)

        self._lbl_estado = ctk.CTkLabel(self.panel_controles, text="Listo", text_color="#94a3b8")
        self._lbl_estado.pack(side="left", padx=10)

        # ── TABLA DE ASISTENCIAS (TREEVIEW ESTILIZADO) ──
        # Nota: TTK Treeview sigue siendo necesario, pero le aplicamos un tema oscuro
        self.panel_tabla = ctk.CTkFrame(self.container, fg_color=COLOR_PANEL, corner_radius=15, border_width=1, border_color="#334155")
        self.panel_tabla.pack(fill="both", expand=True)

        ctk.CTkLabel(self.panel_tabla, text="Registros de hoy", font=("Segoe UI", 16, "bold"), text_color=COLOR_ACCENTO).pack(anchor="w", padx=25, pady=(20, 10))

        # Estilo para que el Treeview se vea oscuro
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
            background=COLOR_PANEL, 
            foreground="white", 
            fieldbackground=COLOR_PANEL, 
            borderwidth=0,
            rowheight=35,
            font=("Segoe UI", 11)
        )
        style.map("Treeview", background=[('selected', COLOR_BOTON_NORMAL)])
        style.configure("Treeview.Heading", background="#334155", foreground="white", relief="flat", font=("Segoe UI", 12, "bold"))

        columnas = ("nombre", "hora", "tipo")
        self._tree = ttk.Treeview(self.panel_tabla, columns=columnas, show="headings")
        self._tree.heading("nombre", text="Estudiante")
        self._tree.heading("hora", text="Hora de Entrada")
        self._tree.heading("tipo", text="Método")
        
        self._tree.column("nombre", width=350)
        self._tree.column("hora", width=150, anchor="center")
        self._tree.column("tipo", width=150, anchor="center")

        self._tree.pack(fill="both", expand=True, padx=25, pady=(0, 25))

    # ── MÉTODOS DE LÓGICA (Manteniendo tu estructura original) ──

    def _cargar_cursos(self):
        from infrastructure.database.student_repo import StudentRepository
        repo = StudentRepository(self.db)
        cursos = repo.obtener_cursos(self.profesor_id)
        self._cursos_data = cursos
        opciones = [f"{c[1]} – {c[2]}" for c in cursos]
        self._combo_curso.configure(values=opciones)
        if opciones:
            self._combo_curso.set(opciones[0])

    def _cargar_asistencias_hoy(self):
        for item in self._tree.get_children():
            self._tree.delete(item)

        idx_text = self._combo_curso.get()
        if not idx_text or not hasattr(self, '_cursos_data'):
            return

        # Buscamos el ID del curso basándonos en el texto seleccionado
        id_curso = next((c[0] for c in self._cursos_data if f"{c[1]} – {c[2]}" == idx_text), None)
        if not id_curso: return

        hoy = date.today().isoformat()
        from application.attendance_service import AttendanceService
        svc = AttendanceService(self.db)
        registros = svc.listar_por_curso(id_curso, fecha=hoy)
        for r in registros:
            self._tree.insert("", "end", values=(r["nombre_estudiante"], r["hora"], r["tipo"].capitalize()))

    def _iniciar_captura(self):
        # Desactivar botón mientras captura para evitar doble proceso
        self._btn_iniciar.configure(state="disabled", text="CÁMARA ACTIVA...")
        self._lbl_estado.configure(text="Reconociendo...", text_color=COLOR_ACCENTO)
        self.update()

        try:
            from infrastructure.recognition.face_engine import reconocer_y_registrar
            idx_text = self._combo_curso.get()
            id_curso = next((c[0] for c in self._cursos_data if f"{c[1]} – {c[2]}" == idx_text), None)
            
            # Tu lógica de reconocimiento facial
            registrados = reconocer_y_registrar(id_curso, self.db)
            
            self._lbl_estado.configure(text=f"¡Éxito! {len(registrados)} nuevos registros.", text_color=COLOR_ACCENTO)
            self._cargar_asistencias_hoy()
        except Exception as e:
            messagebox.showerror("Error de Cámara", f"No se pudo iniciar el reconocimiento: {e}")
        finally:
            self._btn_iniciar.configure(state="normal", text="▶  INICIAR RECONOCIMIENTO")

    def _volver(self):
        self.destroy()
        self.on_volver()