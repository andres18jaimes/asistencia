from typing import Optional, List, Tuple
from domain.student import Student
from infrastructure.database.student_repo import StudentRepository


# application/student_service.py
from domain.student import Student


class StudentService:
    def __init__(self, repository):
        self.repository = repository

    def registrar_estudiante(
        self,
        nombre: str,
        identificacion: str = "",
        id_curso: int = None,
        encoding_facial: bytes = None,
    ):
        if not nombre or not nombre.strip():
            return False, "El nombre del estudiante es obligatorio.", None

        if id_curso is None:
            return False, "Debe seleccionar un curso.", None

        estudiante = Student(
            id=None,
            nombre=nombre.strip(),
            identificacion=identificacion.strip() if identificacion else "",
            id_curso=id_curso,
            encoding_facial=encoding_facial,
        )

        try:
            student_id = self.repository.guardar(estudiante)
            return True, "Estudiante registrado correctamente.", student_id
        except Exception as e:
            return False, f"No se pudo registrar el estudiante: {e}", None

    def actualizar_encoding(self, student_id: int, encoding: bytes):
        try:
            self.repository.actualizar_encoding(student_id, encoding)
            return True, "Rostro registrado correctamente."
        except Exception as e:
            return False, f"No se pudo guardar el rostro: {e}"

    def eliminar_estudiante(self, student_id: int):
        try:
            eliminado = self.repository.eliminar(student_id)
            if eliminado:
                return True, "Estudiante eliminado correctamente."
            return False, "No se encontró el estudiante."
        except Exception as e:
            return False, f"No se pudo eliminar el estudiante: {e}"

    def obtener_cursos(self, profesor_id=None):
        return self.repository.obtener_cursos(profesor_id)