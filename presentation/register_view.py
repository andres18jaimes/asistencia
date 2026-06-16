import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Callable, Optional

# Paleta de colores consistente (Slate & Emerald)
COLOR_FONDO = "#0f172a"
COLOR_PANEL = "#1e293b"
COLOR_ACCENTO = "#10b981"  # Verde para Guardar
COLOR_PELIGRO = "#ef4444"  # Rojo para Eliminar
COLOR_BOTON_NAV = "#3b82f6" # Azul para captura

class RegisterView(ctk.CTkFrame):
    def __init__(
        self,
        parent: ctk.CTk,
        student_service,
        profesor_id: int,
        on_volver: Callable,
        curso_id: int = None,
        nombre_curso: str = None,
    ):
        super().__init__(parent, fg_color=COLOR_FONDO)

        self.parent = parent
        self.service = student_service
        self.profesor_id = profesor_id
        self.curso_id = curso_id
        self.nombre_curso = nombre_curso
        self.on_volver = on_volver

        try:
            from application.camera_service import CameraService
            self.camera_service = CameraService()
        except Exception:
            self.camera_service = None

        self._student_id_actual: Optional[int] = None
        self._encoding_capturado: Optional[bytes] = None

        self.pack(fill="both", expand=True)
        self._build_ui()
        self._cargar_cursos()

    def _build_ui(self):
        # ── HEADER ──
        self.header = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=COLOR_PANEL)
        self.header.pack(fill="x", side="top")

        self.btn_volver = ctk.CTkButton(
            self.header, text="← Volver", width=100, fg_color="transparent",
            hover_color="#334155", font=("Segoe UI", 14, "bold"), command=self._volver
        )
        self.btn_volver.pack(side="left", padx=20, pady=15)

        self.titulo = ctk.CTkLabel(
            self.header, text="Registro de Nuevos Estudiantes", 
            font=("Segoe UI", 20, "bold"), text_color="#f8fafc"
        )
        self.titulo.pack(side="left", padx=10)

        # ── CUERPO (Dos Columnas Modernas) ──
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=40, pady=30)

        # Configuramos columnas responsivas 50% y 50%
        self.body.grid_columnconfigure(0, weight=1, uniform="col")
        self.body.grid_columnconfigure(1, weight=1, uniform="col")
        self.body.grid_rowconfigure(0, weight=1)

        # PANEL IZQUIERDO: Formulario de Datos
        self.panel_datos = ctk.CTkFrame(self.body, fg_color=COLOR_PANEL, corner_radius=15, border_width=1, border_color="#334155")
        self.panel_datos.grid(row=0, column=0, padx=(0, 15), sticky="nsew", ipadx=20, ipady=20)

        ctk.CTkLabel(self.panel_datos, text="Formulario de Inscripción", font=("Segoe UI", 18, "bold"), text_color="#f8fafc").pack(anchor="w", padx=30, pady=(25, 5))
        
        # Campos de Texto Estilizados
        self._entry_nombre = self._crear_campo(self.panel_datos, "Nombre Completo", "Ingrese nombre y apellidos")
        self._entry_identificacion = self._crear_campo(self.panel_datos, "Documento de Identidad", "Ej: 10023456")

        # Selector de Curso (Combo moderno)
        # Curso actual
        ctk.CTkLabel(
            self.panel_datos,
            text="Curso actual:",
            font=("Segoe UI", 13, "bold"),
            text_color="#94a3b8",
        ).pack(anchor="w", padx=30, pady=(15, 5))

        if self.curso_id is not None:
            self._curso_label = ctk.CTkLabel(
                self.panel_datos,
                text=self.nombre_curso if self.nombre_curso else f"Curso ID {self.curso_id}",
                font=("Segoe UI", 13, "bold"),
                text_color="#f8fafc",
                fg_color="#0f172a",
                corner_radius=8,
                height=40,
                anchor="w",
            )
            self._curso_label.pack(anchor="w", padx=30, fill="x", pady=(0, 15))

            self._combo_curso = None

        else:
            self._combo_curso = ctk.CTkComboBox(
                self.panel_datos,
                state="readonly",
                font=("Segoe UI", 13),
                fg_color="#0f172a",
                width=340,
                height=40,
            )
            self._combo_curso.pack(anchor="w", padx=30, pady=(0, 15))

        # Botones de Acción inferiores
        self.btn_frame = ctk.CTkFrame(self.panel_datos, fg_color="transparent")
        self.btn_frame.pack(anchor="w", padx=30, pady=25)

        self.btn_guardar = ctk.CTkButton(
            self.btn_frame, text="💾  Guardar Datos", font=("Segoe UI", 13, "bold"),
            fg_color=COLOR_ACCENTO, hover_color="#059669", height=42, command=self._guardar
        )
        self.btn_guardar.pack(side="left", padx=(0, 15))

        self.btn_eliminar = ctk.CTkButton(
            self.btn_frame, text="🗑  Eliminar", font=("Segoe UI", 13, "bold"),
            fg_color=COLOR_PELIGRO, hover_color="#dc2626", height=42, command=self._eliminar
        )
        self.btn_eliminar.pack(side="left")

        self._lbl_estado = ctk.CTkLabel(self.panel_datos, text="", font=("Segoe UI", 13))
        self._lbl_estado.pack(anchor="w", padx=30, pady=5)


        # PANEL DERECHO: Captura Biométrica Facial
        self.panel_biometrico = ctk.CTkFrame(self.body, fg_color=COLOR_PANEL, corner_radius=15, border_width=1, border_color="#334155")
        self.panel_biometrico.grid(row=0, column=1, padx=(15, 0), sticky="nsew", ipadx=20, ipady=20)

        ctk.CTkLabel(self.panel_biometrico, text="Escaneo Biométrico", font=("Segoe UI", 18, "bold"), text_color="#f8fafc").pack(anchor="w", padx=30, pady=(25, 20))

        # El área de previsualización (Canvas estilizado para que cuadre con el fondo oscuro)
        self._canvas_preview = ctk.CTkCanvas(
            self.panel_biometrico, bg="#111827", bd=0, highlightthickness=1, 
            highlightbackground="#334155", width=320, height=260
        )
        self._canvas_preview.pack(padx=30, pady=5)
        self._dibujar_icono_usuario()

        ctk.CTkLabel(
            self.panel_biometrico,
            text="Fuente de cámara:",
            font=("Segoe UI", 13, "bold"),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=30, pady=(18, 5))

        self._combo_rotacion = ctk.CTkComboBox(
            self.panel_biometrico,
            values=[
                "Sin rotación",
                "Girar 90° derecha",
                "Girar 180°",
                "Girar 90° izquierda"
            ],
            state="readonly",
            font=("Segoe UI", 13),
            fg_color="#0f172a",
            width=320,
            height=38
        )
        self._combo_rotacion.pack(padx=30, pady=(0, 10))
        self._combo_rotacion.set("Sin rotación")

        self._combo_camara = ctk.CTkComboBox(
            self.panel_biometrico,
            values=[
                "Cámara del computador (0)",
                "Cámara secundaria / DroidCam (1)",
                "Celular por URL"
            ],
            state="readonly",
            font=("Segoe UI", 13),
            fg_color="#0f172a",
            width=320,
            height=38
        )
        self._combo_camara.pack(padx=30, pady=(0, 8))
        self._combo_camara.set("Cámara del computador (0)")

        self._entry_url_camara = ctk.CTkEntry(
            self.panel_biometrico,
            placeholder_text="URL del celular: http://192.168.1.15:8080/video",
            font=("Segoe UI", 12),
            fg_color="#0f172a",
            border_color="#334155",
            width=320,
            height=38
        )
        self._entry_url_camara.pack(padx=30, pady=(0, 12))
        # Botón para activar cámara
        self.btn_camara = ctk.CTkButton(
            self.panel_biometrico, text="📷  Escanear Rostro de Estudiante", font=("Segoe UI", 14, "bold"),
            fg_color=COLOR_BOTON_NAV, hover_color="#2563eb", height=45, width=320, corner_radius=10, command=self._capturar
        )
        self.btn_camara.pack(padx=30, pady=20)

        self._lbl_camara_estado = ctk.CTkLabel(self.panel_biometrico, text="", font=("Segoe UI", 13), text_color="#94a3b8")
        self._lbl_camara_estado.pack(padx=30)

    def _crear_campo(self, parent, label_text, placeholder):
        """Helper para generar campos con estilo de forma limpia y sin placeholders manuales engorrosos"""
        ctk.CTkLabel(parent, text=f"{label_text}:", font=("Segoe UI", 13, "bold"), text_color="#94a3b8").pack(anchor="w", padx=30, pady=(15, 5))
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder, font=("Segoe UI", 13),
            fg_color="#0f172a", border_color="#334155", width=340, height=40, corner_radius=8
        )
        entry.pack(anchor="w", padx=30)
        return entry

    def _dibujar_icono_usuario(self):
        """Mantiene el ícono vectorizado pero adaptado a la paleta oscura"""
        c = self._canvas_preview
        c.delete("all")
        cx, cy = 160, 130
        # Cabeza
        c.create_oval(cx-35, cy-65, cx+35, cy, fill="#4b5563", outline="#4b5563")
        # Cuerpo
        c.create_arc(cx-65, cy+15, cx+65, cy+135, start=0, extent=180, fill="#4b5563", outline="#4b5563")

    # ── MÉTODOS DE NEGOCIO RE-ACOPLADOS ──

    def _obtener_fuente_camara(self):
        opcion = self._combo_camara.get()

        if "(0)" in opcion:
            return 0

        if "(1)" in opcion:
            return 1

        if "URL" in opcion:
            url = self._entry_url_camara.get().strip()
            if not url:
                raise ValueError("Ingrese la URL de la cámara del celular.")
            return url

        return 0
    
    def _obtener_rotacion_camara(self):
        opcion = self._combo_rotacion.get()

        if "90° derecha" in opcion:
            return 90

        if "180" in opcion:
            return 180

        if "90° izquierda" in opcion:
            return 270

        return 0
    def _guardar(self):
        nombre = self._entry_nombre.get().strip()
        identificacion = self._entry_identificacion.get().strip()

        if not nombre:
            self._set_estado("⚠ El nombre es obligatorio.", error=True)
            return

        id_curso = self._get_id_curso_seleccionado()

        if id_curso is None:
            self._set_estado("⚠ No se encontró el curso actual.", error=True)
            return

        exito, mensaje, student_id = self.service.registrar_estudiante(
            nombre=nombre,
            identificacion=identificacion,
            id_curso=id_curso,
            encoding_facial=self._encoding_capturado,
        )

        if exito:
            self._student_id_actual = student_id
            self._set_estado(f"✓ {mensaje}. Ahora puede escanear el rostro.", error=False)
        else:
            self._set_estado(f"✗ {mensaje}", error=True)

    def _eliminar(self):
        if self._student_id_actual is None:
            self._set_estado("⚠ Primero guarde o seleccione un estudiante.", error=True)
            return

        confirmar = messagebox.askyesno("Confirmación", "¿Desea eliminar permanentemente a este estudiante?")
        if not confirmar: return

        exito, mensaje = self.service.eliminar_estudiante(self._student_id_actual)
        if exito:
            self._student_id_actual = None
            self._encoding_capturado = None
            self._entry_nombre.delete(0, "end")
            self._entry_identificacion.delete(0, "end")
            self._dibujar_icono_usuario()
            self._lbl_camara_estado.configure(text="")
            self._set_estado(f"✓ {mensaje}", error=False)
        else:
            self._set_estado(f"✗ {mensaje}", error=True)

    def _capturar(self):
        if self._student_id_actual is None:
            self._set_estado("⚠ Guarde los datos del estudiante antes del escaneo facial.", error=True)
            return

        self._lbl_camara_estado.configure(text="Iniciando cámara...", text_color="#3b82f6")
        self.update()

        try:
            nombre = self._entry_nombre.get().strip()
            camera_source = self._obtener_fuente_camara()
            camera_rotation = self._obtener_rotacion_camara()

            encoding = self.camera_service.capture_faces(
                nombre,
                camera_source=camera_source,
                camera_rotation=camera_rotation
            )

            if encoding is not None:
                self._encoding_capturado = encoding
                exito, msg = self.service.actualizar_encoding(self._student_id_actual, encoding)
                self._lbl_camara_estado.configure(
                    text=f"✓ {msg}" if exito else f"✗ {msg}",
                    text_color=COLOR_ACCENTO if exito else COLOR_PELIGRO
                )
            else:
                self._lbl_camara_estado.configure(text="No se detectó rostro. Intente de nuevo.", text_color=COLOR_PELIGRO)
        except Exception as e:
            self._lbl_camara_estado.configure(text=f"Error: {str(e)}", text_color=COLOR_PELIGRO)

    def _cargar_cursos(self):
        if self.curso_id is not None:
            self._cursos_data = []
            return

        try:
            cursos = self.service.obtener_cursos(self.profesor_id)
            self._cursos_data = cursos

            opciones = [f"{c[1]} – {c[2]}" for c in cursos]

            if self._combo_curso is not None:
                self._combo_curso.configure(values=opciones)

                if opciones:
                    self._combo_curso.set(opciones[0])
                else:
                    self._combo_curso.set("Sin cursos disponibles")

        except Exception as e:
            self._cursos_data = []
            self._set_estado(f"Error al cargar cursos: {e}", error=True)

    def _get_id_curso_seleccionado(self) -> Optional[int]:
        if self.curso_id is not None:
            return self.curso_id

        if self._combo_curso is None:
            return None

        texto_sel = self._combo_curso.get()

        if hasattr(self, "_cursos_data"):
            for c in self._cursos_data:
                if f"{c[1]} – {c[2]}" == texto_sel:
                    return c[0]

        return None

    def _set_estado(self, texto: str, error: bool = False):
        self._lbl_estado.configure(text=texto, text_color=COLOR_PELIGRO if error else COLOR_ACCENTO)

    def _volver(self):
        self.destroy()
        self.on_volver()