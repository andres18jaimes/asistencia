"""
face_engine.py

Bucle de reconocimiento facial en vivo usando Haarcascade para detección
y face_recognition para extracción y comparación de encodings.
Registra asistencia automáticamente al detectar a un estudiante conocido.
"""

import cv2
import face_recognition
import numpy as np
import os
import time
from typing import List, Tuple, Set

from infrastructure.database.db_manager import DatabaseManager
from infrastructure.database.student_repo import StudentRepository
from application.attendance_service import AttendanceService
from application.camera_service import CameraService
from config.settings import CAMERA_SOURCE


# Ruta absoluta al clasificador Haar, relativa a este archivo
_CASCADE_PATH = os.path.join(
    os.path.dirname(__file__), "models", "haarcascade_frontalface_default.xml"
)


def reconocer_y_registrar(
    id_curso: int,
    db_manager: DatabaseManager,
    callback_progreso=None,
    camera_source=None,
) -> List[Tuple[int, str]]:
    """
    Abre la cámara, reconoce estudiantes del curso dado y registra su asistencia.
    """
    # 1. Cargar encodings desde BD
    repo = StudentRepository(db_manager)
    datos = repo.obtener_encodings_por_curso(id_curso)

    if not datos:
        print("[FaceEngine] No hay estudiantes con encoding en este curso.")
        return []

    conocidos: List[np.ndarray] = []
    nombres: List[str] = []
    ids: List[int] = []

    for id_est, nombre, enc_bytes in datos:
        if enc_bytes is None:
            continue
        encoding = CameraService.bytes_a_encoding(enc_bytes)
        if encoding is not None:
            conocidos.append(encoding)
            nombres.append(nombre)
            ids.append(id_est)

    if not conocidos:
        print("[FaceEngine] No se pudieron cargar encodings válidos.")
        return []

    # 2. Cargar Haarcascade
    if not os.path.exists(_CASCADE_PATH):
        print(f"[FaceEngine] ERROR: No se encuentra {_CASCADE_PATH}")
        return []

    face_cascade = cv2.CascadeClassifier(_CASCADE_PATH)
    if face_cascade.empty():
        print("[FaceEngine] ERROR: No se pudo cargar el clasificador Haarcascade.")
        return []

    # 3. Servicio de asistencia
    attendance_svc = AttendanceService(db_manager)
    ya_registrados_hoy: Set[int] = set()
    resultados_ventana: List[Tuple[int, str]] = []

    # 4. Cámara
    from config.settings import CAMERA_SOURCE

    source = CAMERA_SOURCE if camera_source is None else camera_source
    camara = cv2.VideoCapture(source)

    if not camara.isOpened():
        print("[FaceEngine] No se pudo abrir la cámara.")
        return []

    # Variables de diagnóstico
    tiempo_ultimo_deteccion = time.time()
    frames_sin_deteccion = 0

    print("[FaceEngine] Reconocimiento iniciado con Haarcascade. ESC para salir.")

    while True:
        ret, frame = camara.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Parámetros más sensibles (ajusta si aún no detecta)
        rostros = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,      # antes 1.1 (más sensible)
            minNeighbors=5,        # antes 5 (menos vecinos necesarios)
            minSize=(60, 60),      # antes 60 (acepta caras más pequeñas)
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        num_detecciones = len(rostros)

        # Diagnóstico: mostrar contador de caras detectadas
        cv2.putText(
            frame, f"Caras detectadas: {num_detecciones}",
            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2,
        )

        # Si no se detecta nada por más de 3 segundos, avisar en consola
        if num_detecciones == 0:
            frames_sin_deteccion += 1
            if time.time() - tiempo_ultimo_deteccion > 3:
                print("[FaceEngine] Sin detección por más de 3s. Revisa iluminación y ángulo.")
                tiempo_ultimo_deteccion = time.time()  # evitar spam
        else:
            frames_sin_deteccion = 0
            tiempo_ultimo_deteccion = time.time()

        for (x, y, w, h) in rostros:
            # Evitar caras demasiado pequeñas (< 50 píxeles) para face_recognition
            if w < 50 or h < 50:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                cv2.putText(frame, "Muy pequeña", (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                continue

            rostro_rgb = rgb[y : y + h, x : x + w]

            # Asegurar que la imagen sea contigua (requerido por dlib)
            rostro_rgb = np.ascontiguousarray(rostro_rgb)

            # Intentar extraer encoding
            try:
                encodings_rostro = face_recognition.face_encodings(rostro_rgb)
            except Exception as e:
                print(f"[FaceEngine] Error extrayendo encoding: {e}")
                encodings_rostro = []
            
            if not encodings_rostro:
                # Dibujar rectángulo azul si no se pudo extraer encoding
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                cv2.putText(frame, "Sin encoding", (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                continue

            encoding_actual = encodings_rostro[0]
            coincidencias = face_recognition.compare_faces(
                conocidos, encoding_actual, tolerance=0.6
            )

            nombre_mostrado = "Desconocido"
            color = (0, 0, 255)

            if True in coincidencias:
                idx = coincidencias.index(True)
                nombre_mostrado = nombres[idx]
                id_est = ids[idx]

                if (
                    not attendance_svc.ya_presente_hoy(id_est, id_curso)
                    and id_est not in ya_registrados_hoy
                ):
                    exito, msg = attendance_svc.registrar(
                        id_est, id_curso, tipo="automatico"
                    )
                    if exito:
                        ya_registrados_hoy.add(id_est)
                        resultados_ventana.append((id_est, nombre_mostrado))
                        if callback_progreso:
                            callback_progreso(msg, [r[0] for r in resultados_ventana])
                        print(f"[FaceEngine] {msg}")
                    else:
                        print(f"[FaceEngine] Error: {msg}")
                color = (0, 255, 0)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, nombre_mostrado, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Contador de registrados
        cv2.putText(frame, f"Registrados hoy: {len(ya_registrados_hoy)}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "ESC: Salir", (frame.shape[1] - 130, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

        cv2.imshow("Asistencia - Reconocimiento Facial", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    camara.release()
    cv2.destroyAllWindows()
    print(f"[FaceEngine] Sesión finalizada. Asistencias registradas: {len(resultados_ventana)}")
    return resultados_ventana