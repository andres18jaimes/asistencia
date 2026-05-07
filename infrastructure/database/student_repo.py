from typing import Optional, List
from domain.student import Student
from infrastructure.database.db_manager import DatabaseManager


class StudentRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def guardar(self, student: Student) -> int:
        """Inserta un estudiante y retorna su id generado."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO estudiantes (nombre, identificacion, id_curso, encoding_facial)
               VALUES (?, ?, ?, ?)''',
            (student.nombre, student.identificacion,
             student.id_curso, student.encoding_facial)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def actualizar_encoding(self, student_id: int, encoding: bytes) -> None:
        """Actualiza el encoding facial de un estudiante existente."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE estudiantes SET encoding_facial = ? WHERE id = ?',
            (encoding, student_id)
        )
        conn.commit()
        conn.close()

    def actualizar(self, student: Student) -> bool:
        """Actualiza nombre, identificacion e id_curso de un estudiante (RF-04)."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE estudiantes
               SET nombre = ?, identificacion = ?, id_curso = ?
               WHERE id = ?''',
            (student.nombre, student.identificacion, student.id_curso, student.id)
        )
        conn.commit()
        afectadas = cursor.rowcount
        conn.close()
        return afectadas > 0

    def eliminar(self, student_id: int) -> bool:
        """Elimina un estudiante por id. Retorna True si se eliminó."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        # Eliminar también sus asistencias (RF-05)
        cursor.execute('DELETE FROM asistencias WHERE id_estudiante = ?', (student_id,))
        cursor.execute('DELETE FROM estudiantes WHERE id = ?', (student_id,))
        conn.commit()
        afectadas = cursor.rowcount
        conn.close()
        return afectadas > 0

    def buscar_por_id(self, student_id: int) -> Optional[Student]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, nombre, identificacion, id_curso, encoding_facial FROM estudiantes WHERE id = ?',
            (student_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return Student(id=row[0], nombre=row[1], identificacion=row[2],
                           id_curso=row[3], encoding_facial=row[4])
        return None

    def listar_todos(self) -> List[Student]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, nombre, identificacion, id_curso, encoding_facial FROM estudiantes'
        )
        rows = cursor.fetchall()
        conn.close()
        return [Student(id=r[0], nombre=r[1], identificacion=r[2],
                        id_curso=r[3], encoding_facial=r[4]) for r in rows]

    def buscar_por_curso(self, id_curso: int) -> List[Student]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, nombre, identificacion, id_curso, encoding_facial
               FROM estudiantes WHERE id_curso = ?''',
            (id_curso,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [Student(id=r[0], nombre=r[1], identificacion=r[2],
                        id_curso=r[3], encoding_facial=r[4]) for r in rows]

    def obtener_cursos(self, profesor_id: int = None) -> list:
        """
        Retorna lista de (id, nombre_curso, grupo).
        Si se pasa profesor_id, filtra por ese profesor (Prioridad 5).
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        if profesor_id is not None:
            cursor.execute(
                'SELECT id, nombre_curso, grupo FROM cursos WHERE id_profesor = ?',
                (profesor_id,)
            )
        else:
            cursor.execute('SELECT id, nombre_curso, grupo FROM cursos')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def obtener_encodings_por_curso(self, id_curso: int) -> List[tuple]:
        """
        Retorna [(id, nombre, encoding_facial), ...] para reconocimiento facial.
        Solo estudiantes con encoding registrado.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, nombre, encoding_facial FROM estudiantes
               WHERE id_curso = ? AND encoding_facial IS NOT NULL''',
            (id_curso,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows