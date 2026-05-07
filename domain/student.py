from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    nombre: str
    identificacion: Optional[str] = None   # RF-01: código/cédula del estudiante
    id_curso: Optional[int] = None
    encoding_facial: Optional[bytes] = None
    id: Optional[int] = None

    def es_valido(self) -> bool:
        return bool(self.nombre and self.nombre.strip())