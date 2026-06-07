import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import csv
from typing import Callable

# Paleta de colores unificada
COLOR_FONDO = "#0f172a"
COLOR_PANEL = "#1e293b"
COLOR_ACCENTO = "#10b981" # Verde Esmeralda
COLOR_BOTON_NORMAL = "#3b82f6"

class ReportView(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTk, curso_id: int, db_manager, on_volver: Callable):
        super().__init__(parent, fg_color=COLOR_FONDO)
        self.parent = parent
        self.curso_id = curso_id
        self.db = db_manager
        self.on_volver = on_volver

        self.pack(fill="both", expand=True)
        self._build_ui()
        self._calcular_resumen()

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
            self.header, text="Módulo Analítico de Reportes", 
            font=("Segoe UI", 20, "bold"), text_color="#f8fafc"
        )
        self.titulo.pack(side="left", padx=10)

        # ── CUERPO ──
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=40, pady=30)

        # Panel Superior de Exportación
        self.panel_exportar = ctk.CTkFrame(self.container, fg_color=COLOR_PANEL, corner_radius=15, border_width=1, border_color="#334155")
        self.panel_exportar.pack(fill="x", pady=(0, 20), ipady=10)

        tk_lbl = ctk.CTkLabel(
            self.panel_exportar, text="Exportar sábana consolidada final en formato de hoja de cálculo:",
            font=("Segoe UI", 13), text_color="#94a3b8"
        )
        tk_lbl.pack(side="left", padx=25, pady=20)

        self.btn_csv = ctk.CTkButton(
            self.panel_exportar, text="📥  Descargar CSV (Excel)", font=("Segoe UI", 13, "bold"),
            fg_color=COLOR_ACCENTO, hover_color="#059669", height=42, corner_radius=10, command=self._exportar_csv
        )
        self.btn_csv.pack(side="right", padx=25, pady=15)

        # Panel Inferior de Tabla Resumen
        self.panel_tabla = ctk.CTkFrame(self.container, fg_color=COLOR_PANEL, corner_radius=15, border_width=1, border_color="#334155")
        self.panel_tabla.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.panel_tabla, text="Métricas Generales de Rendimiento", 
            font=("Segoe UI", 16, "bold"), text_color=COLOR_BOTON_NORMAL
        ).pack(anchor="w", padx=25, pady=(20, 10))

        # Estilo de Tabla
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
            background=COLOR_PANEL, foreground="white", fieldbackground=COLOR_PANEL, 
            borderwidth=0, rowheight=35, font=("Segoe UI", 11)
        )
        style.map("Treeview", background=[('selected', COLOR_BOTON_NORMAL)])
        style.configure("Treeview.Heading", background="#334155", foreground="white", relief="flat", font=("Segoe UI", 12, "bold"))

        columnas = ("identificacion", "nombre", "presencias", "ausencias")
        self._tree = ttk.Treeview(self.panel_tabla, columns=columnas, show="headings")
        self._tree.heading("identificacion", text="Identificación")
        self._tree.heading("nombre", text="Nombre del Estudiante")
        self._tree.heading("presencias", text="Clases Asistidas")
        self._tree.heading("ausencias", text="Inasistencias")

        self._tree.column("identificacion", width=150, anchor="center")
        self._tree.column("nombre", width=320, anchor="w")
        self._tree.column("presencias", width=140, anchor="center")
        self._tree.column("ausencias", width=140, anchor="center")

        self._tree.pack(fill="both", expand=True, padx=25, pady=(0, 25))

    # ── LÓGICA DE PROCESAMIENTO BI ──
    def _calcular_resumen(self):
        for item in self._tree.get_children(): self._tree.delete(item)
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(DISTINCT fecha) FROM asistencias WHERE id_curso = ?", (self.curso_id,))
            total_dias_clase = cursor.fetchone()[0]

            cursor.execute("SELECT id, identificacion, nombre FROM estudiantes WHERE id_curso = ? ORDER BY nombre ASC", (self.curso_id,))
            estudiantes = cursor.fetchall()

            self.datos_reporte = []
            for est_id, identificacion, nombre in estudiantes:
                cursor.execute("SELECT COUNT(*) FROM asistencias WHERE id_estudiante = ? AND id_curso = ?", (est_id, self.curso_id))
                asistencias_alumno = cursor.fetchone()[0]
                inasistencias = max(0, total_dias_clase - asistencias_alumno)
                identificacion_clean = identificacion if identificacion else "N/A"
                
                self._tree.insert("", "end", values=(identificacion_clean, nombre, asistencias_alumno, inasistencias))
                
                self.datos_reporte.append({
                    "Identificacion": identificacion_clean,
                    "Estudiante": nombre,
                    "Asistencias": asistencias_alumno,
                    "Faltas": inasistencias
                })
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular: {e}")

    def _exportar_csv(self):
        if not hasattr(self, 'datos_reporte') or not self.datos_reporte:
            messagebox.showwarning("Atención", "No hay datos para procesar.")
            return

        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")], title="Guardar Reporte"
        )
        if not ruta_archivo: return

        try:
            with open(ruta_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
                columnas = ["Identificacion", "Estudiante", "Asistencias", "Faltas"]
                writer = csv.DictWriter(f, fieldnames=columnas, delimiter=";")
                writer.writeheader()
                for fila in self.datos_reporte: writer.writerow(fila)
            messagebox.showinfo("Éxito", "Reporte analítico exportado con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al escribir archivo: {e}")

    def _volver(self):
        self.destroy()
        self.on_volver()