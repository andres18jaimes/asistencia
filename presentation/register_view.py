"""
presentation/register_view.py

Vista de Registro de Estudiante.
Fiel al mockup: panel izquierdo con datos, panel derecho con captura facial.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from application.student_service import StudentService
from application.camera_service import CameraService


# ── Paleta de colores (consistente con main_window) ─────────────────────────
AZUL_HEADER  = "#4A7BA7"
AZUL_BOTON   = "#5B9BD5"
VERDE        = "#4CAF50"
ROJO         = "#E53935"
GRIS_FONDO   = "#F0F0F0"
GRIS_PANEL   = "#FFFFFF"
GRIS_BORDE   = "#CCCCCC"
GRIS_ICONO   = "#AAAAAA"
TEXTO_DARK   = "#333333"
TEXTO_LABEL  = "#555555"
FUENTE       = "Courier"          # igual que el mockup (monospace)


class RegisterView:
    """
    Ventana / frame de registro de estudiante.

    Parámetros
    ----------
    parent : tk.Widget
        Contenedor padre (Frame o Toplevel).
    student_service : StudentService
        Servicio de aplicación para operar sobre estudiantes.
    profesor_id : int
        Id del profesor actualmente autenticado.
    on_volver : Callable
        Callback que se llama al presionar "← Volver".
    """

    def __init__(
        self,
        parent: tk.Widget,
        student_service: StudentService,
        profesor_id: int,
        on_volver: Callable,
    ):
        self.parent          = parent
        self.service         = student_service
        self.profesor_id     = profesor_id
        self.on_volver       = on_volver
        self.camera_service  = CameraService()

        # Estado interno
        self._student_id_actual: Optional[int] = None   # id del estudiante recién guardado
        self._encoding_capturado: Optional[bytes] = None

        # Construir UI
        self._build()
        self._cargar_cursos()

    # ── Construcción de la UI ────────────────────────────────────────────────

    def _build(self):
        # Frame raíz de esta vista (ocupa todo el padre)
        self.frame = tk.Frame(self.parent, bg=GRIS_FONDO)
        self.frame.pack(fill="both", expand=True)

        self._build_header()
        self._build_body()

    def _build_header(self):
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
            text="Registro de Estudiante",
            font=(FUENTE, 14, "bold"),
            bg=AZUL_HEADER,
            fg="white",
        ).pack(side="left", pady=10)

    def _build_body(self):
        body = tk.Frame(self.frame, bg=GRIS_FONDO)
        body.pack(fill="both", expand=True, padx=30, pady=24)

        # Dos columnas
        self._build_panel_datos(body)
        self._build_panel_camara(body)

    # ── Panel izquierdo: datos del estudiante ────────────────────────────────

    def _build_panel_datos(self, parent):
        panel = tk.Frame(parent, bg=GRIS_PANEL, bd=1, relief="solid")
        panel.pack(side="left", fill="both", expand=True, padx=(0, 12))

        tk.Label(
            panel,
            text="Datos del Estudiante",
            font=(FUENTE, 13, "bold"),
            bg=GRIS_PANEL,
            fg=TEXTO_DARK,
        ).pack(anchor="w", padx=20, pady=(18, 4))

        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=20, pady=(0, 16))

        # Nombre
        self._campo(panel, "Nombre Completo:", "Ej: Juan Pérez López", "_entry_nombre")

        # Identificación
        self._campo(panel, "Identificación:", "Ej: 12345678", "_entry_identificacion")

        # Curso / Asignatura (combo)
        tk.Label(
            panel,
            text="Curso/Asignatura:",
            font=(FUENTE, 10),
            bg=GRIS_PANEL,
            fg=TEXTO_LABEL,
        ).pack(anchor="w", padx=20, pady=(10, 4))

        self._combo_curso = ttk.Combobox(
            panel,
            state="readonly",
            font=(FUENTE, 10),
            width=36,
        )
        self._combo_curso.pack(anchor="w", padx=20)
        self._combo_curso.set("Selecciona un curso…")

        # Botones
        btn_frame = tk.Frame(panel, bg=GRIS_PANEL)
        btn_frame.pack(anchor="w", padx=20, pady=24)

        tk.Button(
            btn_frame,
            text="💾  Guardar",
            font=(FUENTE, 11, "bold"),
            bg=VERDE,
            fg="white",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            activebackground="#388E3C",
            activeforeground="white",
            command=self._guardar,
        ).pack(side="left", padx=(0, 12))

        tk.Button(
            btn_frame,
            text="🗑  Eliminar",
            font=(FUENTE, 11, "bold"),
            bg=ROJO,
            fg="white",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            activebackground="#B71C1C",
            activeforeground="white",
            command=self._eliminar,
        ).pack(side="left")

        # Etiqueta de estado (feedback al usuario)
        self._lbl_estado = tk.Label(
            panel,
            text="",
            font=(FUENTE, 9),
            bg=GRIS_PANEL,
            fg=VERDE,
            wraplength=320,
            justify="left",
        )
        self._lbl_estado.pack(anchor="w", padx=20, pady=(0, 12))

    def _campo(self, parent, label_txt, placeholder, attr_name):
        """Crea un label + entry con placeholder y lo guarda en self.<attr_name>."""
        tk.Label(
            parent,
            text=label_txt,
            font=(FUENTE, 10),
            bg=GRIS_PANEL,
            fg=TEXTO_LABEL,
        ).pack(anchor="w", padx=20, pady=(10, 4))

        entry = tk.Entry(
            parent,
            font=(FUENTE, 10),
            fg=GRIS_ICONO,
            bd=1,
            relief="solid",
            width=38,
        )
        entry.insert(0, placeholder)
        entry.pack(anchor="w", padx=20)

        # Comportamiento placeholder
        def _on_focus_in(e, ent=entry, ph=placeholder):
            if ent.get() == ph:
                ent.delete(0, "end")
                ent.config(fg=TEXTO_DARK)

        def _on_focus_out(e, ent=entry, ph=placeholder):
            if not ent.get():
                ent.insert(0, ph)
                ent.config(fg=GRIS_ICONO)

        entry.bind("<FocusIn>",  _on_focus_in)
        entry.bind("<FocusOut>", _on_focus_out)

        setattr(self, attr_name, entry)

    # ── Panel derecho: captura facial ────────────────────────────────────────

    def _build_panel_camara(self, parent):
        panel = tk.Frame(parent, bg=GRIS_PANEL, bd=1, relief="solid", width=340)
        panel.pack(side="left", fill="both", expand=True)
        panel.pack_propagate(False)

        tk.Label(
            panel,
            text="Captura Facial",
            font=(FUENTE, 13, "bold"),
            bg=GRIS_PANEL,
            fg=TEXTO_DARK,
        ).pack(anchor="w", padx=20, pady=(18, 4))

        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=20, pady=(0, 12))

        # Área de preview
        self._canvas_preview = tk.Canvas(
            panel,
            bg="#E8E8E8",
            bd=0,
            highlightthickness=1,
            highlightbackground=GRIS_BORDE,
            width=280,
            height=240,
        )
        self._canvas_preview.pack(padx=20, pady=(0, 0))
        self._dibujar_icono_usuario()

        # Botón capturar
        tk.Button(
            panel,
            text="📷  Capturar Rostro",
            font=(FUENTE, 11, "bold"),
            bg=AZUL_BOTON,
            fg="white",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            activebackground="#3a7ab5",
            activeforeground="white",
            command=self._capturar,
        ).pack(fill="x", padx=20, pady=16)

        self._lbl_camara_estado = tk.Label(
            panel,
            text="",
            font=(FUENTE, 9),
            bg=GRIS_PANEL,
            fg=TEXTO_LABEL,
        )
        self._lbl_camara_estado.pack(padx=20)

    def _dibujar_icono_usuario(self):
        """Dibuja el ícono genérico de persona en el canvas."""
        c = self._canvas_preview
        c.delete("all")
        cx, cy = 140, 120
        # Cabeza
        c.create_oval(cx-32, cy-72, cx+32, cy-8,
                      fill=GRIS_ICONO, outline=GRIS_ICONO)
        # Cuerpo (arco)
        c.create_arc(cx-56, cy+10, cx+56, cy+110,
                     start=0, extent=180,
                     fill=GRIS_ICONO, outline=GRIS_ICONO)

    # ── Acciones ─────────────────────────────────────────────────────────────

    def _guardar(self):
        nombre = self._entry_nombre.get().strip()
        identificacion = self._entry_identificacion.get().strip()

        # Ignorar placeholders
        PLACEHOLDER_NOMBRE = "Ej: Juan Pérez López"
        PLACEHOLDER_ID     = "Ej: 12345678"
        if nombre == PLACEHOLDER_NOMBRE:
            nombre = ""
        if identificacion == PLACEHOLDER_ID:
            identificacion = ""

        if not nombre:
            self._set_estado("⚠ El nombre es obligatorio.", error=True)
            return

        # Obtener id_curso seleccionado
        id_curso = self._get_id_curso_seleccionado()

        exito, mensaje, student_id = self.service.registrar_estudiante(
            nombre=nombre,
            id_curso=id_curso,
            encoding_facial=self._encoding_capturado,
        )

        if exito:
            self._student_id_actual = student_id
            self._set_estado(f"✓ {mensaje}", error=False)
        else:
            self._set_estado(f"✗ {mensaje}", error=True)

    def _eliminar(self):
        if self._student_id_actual is None:
            self._set_estado("⚠ Primero guarda un estudiante.", error=True)
            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar este estudiante?",
        )
        if not confirmar:
            return

        exito, mensaje = self.service.eliminar_estudiante(self._student_id_actual)
        if exito:
            self._student_id_actual = None
            self._encoding_capturado = None
            self._limpiar_formulario()
            self._set_estado(f"✓ {mensaje}", error=False)
        else:
            self._set_estado(f"✗ {mensaje}", error=True)

    def _capturar(self):
        """Llama al CameraService para capturar el encoding facial."""
        if self._student_id_actual is None:
            self._set_estado("⚠ Guarda los datos primero antes de capturar el rostro.", error=True)
            return

        self._lbl_camara_estado.config(text="Abriendo cámara…", fg=TEXTO_LABEL)
        self.frame.update()

        try:
            nombre = self._entry_nombre.get().strip()
            encoding = self.camera_service.capture_faces(nombre)

            if encoding is not None:
                self._encoding_capturado = encoding
                exito, msg = self.service.actualizar_encoding(self._student_id_actual, encoding)
                estado = f"✓ {msg}" if exito else f"✗ {msg}"
                self._lbl_camara_estado.config(
                    text=estado,
                    fg=VERDE if exito else ROJO,
                )
            else:
                self._lbl_camara_estado.config(
                    text="No se detectó ningún rostro. Intenta de nuevo.",
                    fg=ROJO,
                )
        except Exception as e:
            self._lbl_camara_estado.config(text=f"Error: {str(e)}", fg=ROJO)

    def _volver(self):
        self.frame.destroy()
        self.on_volver()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _cargar_cursos(self):
        """Carga los cursos disponibles en el ComboBox."""
        try:
            cursos = self.service.obtener_cursos()
            self._cursos_data = cursos   # [(id, nombre_curso, grupo), ...]
            opciones = [f"{c[1]} – {c[2]}" for c in cursos]
            self._combo_curso["values"] = opciones
            if opciones:
                self._combo_curso.set(opciones[0])
        except Exception:
            self._cursos_data = []

    def _get_id_curso_seleccionado(self) -> Optional[int]:
        idx = self._combo_curso.current()
        if idx >= 0 and self._cursos_data:
            return self._cursos_data[idx][0]
        return None

    def _set_estado(self, texto: str, error: bool = False):
        self._lbl_estado.config(text=texto, fg=ROJO if error else VERDE)

    def _limpiar_formulario(self):
        for attr, ph in [
            ("_entry_nombre",        "Ej: Juan Pérez López"),
            ("_entry_identificacion","Ej: 12345678"),
        ]:
            entry = getattr(self, attr)
            entry.delete(0, "end")
            entry.insert(0, ph)
            entry.config(fg=GRIS_ICONO)
        self._combo_curso.set("Selecciona un curso…")
        self._dibujar_icono_usuario()
        self._lbl_camara_estado.config(text="")