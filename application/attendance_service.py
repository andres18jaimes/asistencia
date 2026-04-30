# application/attendance_service.py

import csv
from datetime import datetime

from infrastructure.recognition.encoder import cargar_encodings
from infrastructure.recognition.face_engine import reconocer


class AttendanceService:

    def guardar(self, nombre):
        with open("data/asistencia.csv", "a", newline="") as archivo:
            writer = csv.writer(archivo)

            ahora = datetime.now()
            writer.writerow([
                nombre,
                ahora.strftime("%Y-%m-%d"),
                ahora.strftime("%H:%M:%S")
            ])

    def reconocer_y_guardar(self):
        print("Cargando rostros...")

        caras, nombres = cargar_encodings()

        print(f"Rostros cargados: {len(nombres)}")

        if len(nombres) == 0:
            print("No hay rostros registrados")
            return

        resultados = reconocer(caras, nombres)

        for nombre in resultados:
            if nombre != "Desconocido":
                self.guardar(nombre)

        print("Asistencia registrada")