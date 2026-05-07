# application/attendance_service.py
"""
Servicio de asistencia.
- Registra asistencia en la tabla `asistencias` de SQLite.
- Evita duplicados: un estudiante sólo puede tener una asistencia
  por curso por día (RF-12).
- Soporta registro automático (por reconocimiento) y manual (RF-13).
"""

from datetime import date, datetime
from typing import List, Tuple, Optional

from infrastructure.database.db_manager import DatabaseManager


class AttendanceService:

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    # ── Registro ─────────────────────────────────────────────────────────────

    def registrar(
        self,
        id_estudiante: int,
        id_curso: int,
        tipo: str = "automatico",          # "automatico" | "manual"
    ) -> Tuple[bool, str]:
        """
        Registra la asistencia de un estudiante.
        Retorna (exito, mensaje).
        """
        hoy = date.today().isoformat()          # "YYYY-MM-DD"
        hora = datetime.now().strftime("%H:%M:%S")

        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            # RF-12: evitar duplicado mismo día + mismo curso
            cursor.execute(
                """SELECT id FROM asistencias
                   WHERE id_estudiante = ? AND id_curso = ? AND fecha = ?""",
                (id_estudiante, id_curso, hoy),
            )
            if cursor.fetchone():
                conn.close()
                return False, "Asistencia ya registrada hoy para este estudiante."

            cursor.execute(
                """INSERT INTO asistencias (id_estudiante, id_curso, fecha, hora, tipo)
                   VALUES (?, ?, ?, ?, ?)""",
                (id_estudiante, id_curso, hoy, hora, tipo),
            )
            conn.commit()
            return True, f"Asistencia registrada ({tipo}) — {hoy} {hora}"
        except Exception as e:
            return False, f"Error al registrar asistencia: {e}"
        finally:
            conn.close()

    # ── Consultas ─────────────────────────────────────────────────────────────

    def listar_por_curso(
        self,
        id_curso: int,
        fecha: Optional[str] = None,
    ) -> List[dict]:
        """
        Devuelve lista de asistencias de un curso.
        Si `fecha` es None, devuelve todo el historial.
        Cada elemento: {id, nombre_estudiante, id_estudiante, id_curso, fecha, hora, tipo}
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        if fecha:
            cursor.execute(
                """SELECT a.id, e.nombre, a.id_estudiante, a.id_curso,
                          a.fecha, a.hora, a.tipo
                   FROM asistencias a
                   JOIN estudiantes e ON e.id = a.id_estudiante
                   WHERE a.id_curso = ? AND a.fecha = ?
                   ORDER BY a.fecha DESC, a.hora DESC""",
                (id_curso, fecha),
            )
        else:
            cursor.execute(
                """SELECT a.id, e.nombre, a.id_estudiante, a.id_curso,
                          a.fecha, a.hora, a.tipo
                   FROM asistencias a
                   JOIN estudiantes e ON e.id = a.id_estudiante
                   WHERE a.id_curso = ?
                   ORDER BY a.fecha DESC, a.hora DESC""",
                (id_curso,),
            )
        rows = cursor.fetchall()
        conn.close()
        keys = ["id", "nombre_estudiante", "id_estudiante", "id_curso", "fecha", "hora", "tipo"]
        return [dict(zip(keys, r)) for r in rows]

    def listar_por_estudiante(self, id_estudiante: int) -> List[dict]:
        """Historial completo de asistencias de un estudiante (RF-16)."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT a.id, e.nombre, a.id_estudiante, a.id_curso,
                      c.nombre_curso, a.fecha, a.hora, a.tipo
               FROM asistencias a
               JOIN estudiantes e ON e.id = a.id_estudiante
               JOIN cursos c ON c.id = a.id_curso
               WHERE a.id_estudiante = ?
               ORDER BY a.fecha DESC, a.hora DESC""",
            (id_estudiante,),
        )
        rows = cursor.fetchall()
        conn.close()
        keys = ["id", "nombre_estudiante", "id_estudiante", "id_curso",
                "nombre_curso", "fecha", "hora", "tipo"]
        return [dict(zip(keys, r)) for r in rows]

    def ya_presente_hoy(self, id_estudiante: int, id_curso: int) -> bool:
        """Retorna True si el estudiante ya tiene asistencia hoy en ese curso."""
        hoy = date.today().isoformat()
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM asistencias WHERE id_estudiante=? AND id_curso=? AND fecha=?",
            (id_estudiante, id_curso, hoy),
        )
        result = cursor.fetchone() is not None
        conn.close()
        return result