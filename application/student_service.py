from typing import Optional, List, Tuple
from domain.student import Student
from infrastructure.database.student_repo import StudentRepository


class StudentService:
    def __init__(self, student_repo: StudentRepository):
        self.repo = student_repo

    def registrar_estudiante(
        self,
        nombre: str,
        id_curso: Optional[int] = None,
        encoding_facial: Optional[bytes] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Registra un nuevo estudiante.
        Retorna (exito, mensaje, id_generado).
        """
        nombre = nombre.strip()
        if not nombre:
            return False, "El nombre no puede estar vacío.", None

        student = Student(nombre=nombre, id_curso=id_curso, encoding_facial=encoding_facial)

        if not student.es_valido():
            return False, "Datos del estudiante inválidos.", None

        try:
            new_id = self.repo.guardar(student)
            return True, f"Estudiante '{nombre}' registrado correctamente.", new_id
        except Exception as e:
            return False, f"Error al registrar: {str(e)}", None

    def actualizar_encoding(self, student_id: int, encoding: bytes) -> Tuple[bool, str]:
        """Guarda el encoding facial capturado después del registro."""
        try:
            self.repo.actualizar_encoding(student_id, encoding)
            return True, "Rostro guardado correctamente."
        except Exception as e:
            return False, f"Error al guardar rostro: {str(e)}"

    def eliminar_estudiante(self, student_id: int) -> Tuple[bool, str]:
        try:
            eliminado = self.repo.eliminar(student_id)
            if eliminado:
                return True, "Estudiante eliminado correctamente."
            return False, "No se encontró el estudiante."
        except Exception as e:
            return False, f"Error al eliminar: {str(e)}"

    def obtener_estudiante(self, student_id: int) -> Optional[Student]:
        return self.repo.buscar_por_id(student_id)

    def listar_estudiantes(self) -> List[Student]:
        return self.repo.listar_todos()

    def obtener_cursos(self):
        """Devuelve la lista de cursos disponibles para el combo de la vista."""
        return self.repo.obtener_cursos()