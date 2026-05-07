"""
presentation/attendance_view.py

Vista de Toma de Asistencia.
Permite seleccionar un curso, iniciar el reconocimiento facial y
ver los registros del día.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from datetime import date

from infrastructure.database.db_manager import DatabaseManager
from infrastructure.database.student_repo import StudentRepository
from infrastructure.recognition.face_engine import reconocer_y_registrar

# Paleta de colores consistente
AZUL_HEADER  = "#4A7BA7"
AZUL_BOTON   = "#5B9BD5"
VERDE        = "#4CAF50"
ROJO         = "#E53935"
GRIS_FONDO   = "#F0F0F0"
GRIS_PANEL   = "#FFFFFF"
TEXTO_DARK   = "#333333"
TEXTO_LABEL  = "#555555"
FUENTE       = "Courier"


class AttendanceView:
    def __init__(
        self,
        parent: tk.Widget,
        profesor_id: int,
        db_manager: DatabaseManager,
        on_volver: Callable,
    ):
        self.parent = parent
        self.profesor_id = profesor_id
        self.db = db_manager
        self.on_volver = on_volver

        self._build()
        self._cargar_cursos()
        self._cargar_asistencias_hoy()

    # ── Construcción de UI ──────────────────────────────────────────────────
    def _build(self):
        self.frame = tk.Frame(self.parent, bg=GRIS_FONDO)
        self.frame.pack(fill="both", expand=True)

        # Header
        header = tk.Frame(self.frame, bg=AZUL_HEADER, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        btn_volver = tk.Button(
            header,
            text="← Volver",
            font=(FUENTE, 11, "bold"),
            bg=AZUL_HEADER,
            fg="white",
            bd=0,
            activebackground="#3a6a96",
            activeforeground="white",
            cursor="hand2",
            padx=14,
            command=self._volver,
        )
        btn_volver.pack(side="left", pady=10)

        tk.Label(
            header,
            text="Toma de Asistencia",
            font=(FUENTE, 14, "bold"),
            bg=AZUL_HEADER,
            fg="white",
        ).pack(side="left", pady=10)

        # Cuerpo
        body = tk.Frame(self.frame, bg=GRIS_FONDO)
        body.pack(fill="both", expand=True, padx=30, pady=20)

        # Panel superior: selección de curso y botón
        panel_top = tk.Frame(body, bg=GRIS_PANEL, bd=1, relief="solid")
        panel_top.pack(fill="x", pady=(0, 12))

        tk.Label(
            panel_top,
            text="Curso:",
            font=(FUENTE, 10),
            bg=GRIS_PANEL,
            fg=TEXTO_LABEL,
        ).pack(side="left", padx=(20, 6), pady=10)

        self._combo_curso = ttk.Combobox(
            panel_top,
            state="readonly",
            font=(FUENTE, 10),
            width=30,
        )
        self._combo_curso.pack(side="left", pady=10, padx=(0, 20))

        self._btn_iniciar = tk.Button(
            panel_top,
            text="▶  Iniciar Captura de Asistencia",
            font=(FUENTE, 11, "bold"),
            bg=AZUL_BOTON,
            fg="white",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            activebackground="#3a7ab5",
            activeforeground="white",
            command=self._iniciar_captura,
        )
        self._btn_iniciar.pack(side="left", pady=10, padx=(0, 20))

        self._lbl_estado = tk.Label(
            panel_top,
            text="",
            font=(FUENTE, 9),
            bg=GRIS_PANEL,
            fg=TEXTO_DARK,
        )
        self._lbl_estado.pack(side="left", pady=10)

        # Panel inferior: tabla de asistencias de hoy
        panel_bottom = tk.Frame(body, bg=GRIS_PANEL, bd=1, relief="solid")
        panel_bottom.pack(fill="both", expand=True)

        tk.Label(
            panel_bottom,
            text="Asistencias de hoy",
            font=(FUENTE, 12, "bold"),
            bg=GRIS_PANEL,
            fg=TEXTO_DARK,
        ).pack(anchor="w", padx=20, pady=(14, 4))

        ttk.Separator(panel_bottom, orient="horizontal").pack(fill="x", padx=20, pady=(0, 8))

        # Treeview
        columnas = ("nombre", "hora", "tipo")
        self._tree = ttk.Treeview(panel_bottom, columns=columnas, show="headings", height=12)
        self._tree.heading("nombre", text="Estudiante")
        self._tree.heading("hora", text="Hora")
        self._tree.heading("tipo", text="Tipo")
        self._tree.column("nombre", width=220)
        self._tree.column("hora", width=100)
        self._tree.column("tipo", width=100)

        scrollbar = ttk.Scrollbar(panel_bottom, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=(0, 20))

    # ── Lógica ──────────────────────────────────────────────────────────────
    def _cargar_cursos(self):
        repo = StudentRepository(self.db)
        cursos = repo.obtener_cursos(self.profesor_id)
        self._cursos_data = cursos  # [(id, nombre_curso, grupo), ...]
        opciones = [f"{c[1]} – {c[2]}" for c in cursos]
        self._combo_curso["values"] = opciones
        if opciones:
            self._combo_curso.set(opciones[0])

    def _cargar_asistencias_hoy(self):
        """Limpia la tabla y carga asistencias del día para el curso seleccionado."""
        for item in self._tree.get_children():
            self._tree.delete(item)

        idx = self._combo_curso.current()
        if idx < 0 or not self._cursos_data:
            return
        id_curso = self._cursos_data[idx][0]
        hoy = date.today().isoformat()

        from application.attendance_service import AttendanceService
        svc = AttendanceService(self.db)
        registros = svc.listar_por_curso(id_curso, fecha=hoy)
        for r in registros:
            self._tree.insert("", "end", values=(r["nombre_estudiante"], r["hora"], r["tipo"]))

    def _iniciar_captura(self):
        idx = self._combo_curso.current()
        if idx < 0:
            messagebox.showwarning("Aviso", "Selecciona un curso primero.")
            return

        id_curso = self._cursos_data[idx][0]
        self._lbl_estado.config(text="Reconocimiento en curso...")

        # Ejecutar el reconocimiento (bloquea la UI hasta que se cierre la cámara)
        try:
            registrados = reconocer_y_registrar(id_curso, self.db)
            self._lbl_estado.config(text=f"Captura finalizada. {len(registrados)} nuevos registros.")
            self._cargar_asistencias_hoy()
        except Exception as e:
            self._lbl_estado.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"Ocurrió un error durante el reconocimiento:\n{e}")

    def _volver(self):
        self.frame.destroy()
        self.on_volver()