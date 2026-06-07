import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Callable

# Paleta de colores unificada
COLOR_FONDO = "#0f172a"
COLOR_PANEL = "#1e293b"
COLOR_ACCENTO = "#10b981"
COLOR_BOTON_NORMAL = "#3b82f6"

class HistoryView(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTk, curso_id: int, db_manager, on_volver: Callable):
        super().__init__(parent, fg_color=COLOR_FONDO)
        self.parent = parent
        self.curso_id = curso_id
        self.db = db_manager
        self.on_volver = on_volver
        self._estudiantes_data = []

        self.pack(fill="both", expand=True)
        self._build_ui()
        self._cargar_estudiantes()
        self._cargar_fechas_disponibles()

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
            self.header, text="Historial Avanzado de Asistencias", 
            font=("Segoe UI", 20, "bold"), text_color="#f8fafc"
        )
        self.titulo.pack(side="left", padx=10)

        # ── CUERPO ──
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=40, pady=30)

        # Panel de Filtros Superior
        self.panel_filtros = ctk.CTkFrame(self.container, fg_color=COLOR_PANEL, corner_radius=15, border_width=1, border_color="#334155")
        self.panel_filtros.pack(fill="x", pady=(0, 20), ipady=10)

        # Filtro por Fecha
        lbl_fecha = ctk.CTkLabel(self.panel_filtros, text="📅 Por Fecha:", font=("Segoe UI", 13, "bold"))
        lbl_fecha.pack(side="left", padx=(25, 10), pady=15)
        
        self._combo_fechas = ctk.CTkComboBox(
            self.panel_filtros, width=160, values=[], state="readonly", 
            fg_color="#0f172a", font=("Segoe UI", 13), command=lambda e: self._filtrar_por_fecha()
        )
        self._combo_fechas.pack(side="left", padx=10)

        # Separador Estético
        lbl_sep = ctk.CTkLabel(self.panel_filtros, text="│", text_color="#334155", font=("Segoe UI", 16))
        lbl_sep.pack(side="left", padx=15)

        # Filtro por Estudiante
        lbl_est = ctk.CTkLabel(self.panel_filtros, text="👤 Por Estudiante:", font=("Segoe UI", 13, "bold"))
        lbl_est.pack(side="left", padx=(10, 10))

        self._combo_estudiantes = ctk.CTkComboBox(
            self.panel_filtros, width=260, values=[], state="readonly", 
            fg_color="#0f172a", font=("Segoe UI", 13), command=lambda e: self._filtrar_por_estudiante()
        )
        self._combo_estudiantes.pack(side="left", padx=10)

        # Panel de Tabla Inferior
        self.panel_tabla = ctk.CTkFrame(self.container, fg_color=COLOR_PANEL, corner_radius=15, border_width=1, border_color="#334155")
        self.panel_tabla.pack(fill="both", expand=True)

        self._lbl_titulo_tabla = ctk.CTkLabel(
            self.panel_tabla, text="Selecciona un filtro para empezar", 
            font=("Segoe UI", 16, "bold"), text_color=COLOR_ACCENTO
        )
        self._lbl_titulo_tabla.pack(anchor="w", padx=25, pady=(20, 10))

        # Estilo Tabla Oscura
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
            background=COLOR_PANEL, foreground="white", fieldbackground=COLOR_PANEL, 
            borderwidth=0, rowheight=35, font=("Segoe UI", 11)
        )
        style.map("Treeview", background=[('selected', COLOR_BOTON_NORMAL)])
        style.configure("Treeview.Heading", background="#334155", foreground="white", relief="flat", font=("Segoe UI", 12, "bold"))

        columnas = ("fecha", "identificacion", "nombre", "hora", "tipo")
        self._tree = ttk.Treeview(self.panel_tabla, columns=columnas, show="headings")
        
        self._tree.heading("fecha", text="Fecha")
        self._tree.heading("identificacion", text="Identificación")
        self._tree.heading("nombre", text="Estudiante")
        self._tree.heading("hora", text="Hora")
        self._tree.heading("tipo", text="Método")
        
        self._tree.column("fecha", width=120, anchor="center")
        self._tree.column("identificacion", width=130, anchor="center")
        self._tree.column("nombre", width=300, anchor="w")
        self._tree.column("hora", width=110, anchor="center")
        self._tree.column("tipo", width=130, anchor="center")

        self._tree.pack(fill="both", expand=True, padx=25, pady=(0, 25))

    # ── LÓGICA DE NEGOCIO (Mantiene tus consultas SQLite intactas) ──
    def _cargar_fechas_disponibles(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT fecha FROM asistencias WHERE id_curso = ? ORDER BY fecha DESC", (self.curso_id,))
            fechas = [row[0] for row in cursor.fetchall()]
            conn.close()
            if fechas:
                self._combo_fechas.configure(values=fechas)
                self._combo_fechas.set("Elegir fecha...")
            else:
                self._combo_fechas.set("Sin clases")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar fechas:\n{e}")

    def _cargar_estudiantes(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM estudiantes WHERE id_curso = ? ORDER BY nombre ASC", (self.curso_id,))
            self._estudiantes_data = cursor.fetchall()
            conn.close()
            opciones = [est[1] for est in self._estudiantes_data]
            if opciones:
                self._combo_estudiantes.configure(values=opciones)
                self._combo_estudiantes.set("Seleccionar alumno...")
            else:
                self._combo_estudiantes.set("Sin alumnos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar alumnos:\n{e}")

    def _filtrar_por_fecha(self):
        self._combo_estudiantes.set("Seleccionar alumno...")
        for item in self._tree.get_children(): self._tree.delete(item)
        fecha_sel = self._combo_fechas.get()
        if not fecha_sel or fecha_sel == "Elegir fecha...": return

        self._lbl_titulo_tabla.configure(text=f"Asistencias del día: {fecha_sel}")
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """
                SELECT a.fecha, e.identificacion, e.nombre, a.hora, a.tipo
                FROM asistencias a INNER JOIN estudiantes e ON a.id_estudiante = e.id
                WHERE a.id_curso = ? AND a.fecha = ? ORDER BY e.nombre ASC
            """
            cursor.execute(query, (self.curso_id, fecha_sel))
            for r in cursor.fetchall():
                ident = r[1] if r[1] else "N/A"
                self._tree.insert("", "end", values=(r[0], ident, r[2], r[3], r[4].capitalize()))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def _filtrar_por_estudiante(self):
        self._combo_fechas.set("Elegir fecha...")
        for item in self._tree.get_children(): self._tree.delete(item)
        
        nombre_sel = self._combo_estudiantes.get()
        idx = next((i for i, est in enumerate(self._estudiantes_data) if est[1] == nombre_sel), -1)
        if idx < 0: return

        id_estudiante_sel = self._estudiantes_data[idx][0]
        self._lbl_titulo_tabla.configure(text=f"Historial completo de: {nombre_sel}")

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """
                SELECT a.fecha, e.identificacion, e.nombre, a.hora, a.tipo
                FROM asistencias a INNER JOIN estudiantes e ON a.id_estudiante = e.id
                WHERE a.id_curso = ? AND a.id_estudiante = ? ORDER BY a.fecha DESC
            """
            cursor.execute(query, (self.curso_id, id_estudiante_sel))
            for r in cursor.fetchall():
                ident = r[1] if r[1] else "N/A"
                self._tree.insert("", "end", values=(r[0], ident, r[2], r[3], r[4].capitalize()))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def _volver(self):
        self.destroy()
        self.on_volver()