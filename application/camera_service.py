"""
application/camera_service.py

Servicio encargado de capturar rostros desde cámara local o cámara IP,
generar encodings faciales y retornarlos como bytes.
"""

import cv2
import time
import numpy as np
from typing import Optional

from config.settings import (
    CAMERA_SOURCE,
    TOTAL_FACE_CAPTURES,
    PAUSE_BETWEEN_CAPTURES,
)


class CameraService:
    TOTAL_CAPTURAS = TOTAL_FACE_CAPTURES
    PAUSA_ENTRE = PAUSE_BETWEEN_CAPTURES
    CAMARA_INDEX = CAMERA_SOURCE
    TOLERANCIA = 0.6

    def capture_faces(
        self,
        nombre: str,
        camera_source=None,
        camera_rotation: int = 0,
    ) -> Optional[bytes]:
        """
        Captura automáticamente varios encodings faciales y devuelve
        el promedio como bytes.

        Permite:
        - Cámara del computador: 0
        - Cámara secundaria: 1
        - Cámara IP del celular: http://IP:PUERTO/video
        - Corrección de rotación: 0, 90, 180, 270
        """
        try:
            import face_recognition
        except ImportError:
            print("[CameraService] Instala face-recognition: pip install face-recognition")
            return None

        source = self.CAMARA_INDEX if camera_source is None else camera_source
        source = self._normalizar_fuente(source)

        print(f"[CameraService] Intentando abrir cámara con fuente: {source}")

        if isinstance(source, str):
            camara = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
        else:
            camara = cv2.VideoCapture(source)

        if not camara.isOpened():
            print(f"[CameraService] No se pudo abrir la cámara con fuente: {source}")
            return None

        try:
            camara.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        encodings_acumulados = []
        ultimo_tiempo = time.time() - self.PAUSA_ENTRE
        nombre_ventana = f"Registro: {nombre} | ESC para cancelar"

        # Si el usuario eligió una rotación, la probamos primero.
        # Luego probamos las demás por si la orientación sigue fallando.
        rotaciones = [camera_rotation, 0, 90, 270, 180]
        rotaciones = list(dict.fromkeys(rotaciones))

        while len(encodings_acumulados) < self.TOTAL_CAPTURAS:
            ret, frame_original = camara.read()

            if not ret or frame_original is None:
                print("[CameraService] No se pudo leer frame de la cámara.")
                break

            frame_detectado = None
            ubicaciones_detectadas = []
            rgb_detectado = None
            angulo_usado = 0

            for angulo in rotaciones:
                frame = self._rotar_frame(frame_original, angulo)

                alto, ancho = frame.shape[:2]

                if ancho > 900:
                    escala = 900 / ancho
                    frame = cv2.resize(frame, (900, int(alto * escala)))

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = np.ascontiguousarray(rgb)

                ubicaciones = face_recognition.face_locations(
                    rgb,
                    number_of_times_to_upsample=2,
                    model="hog",
                )

                if ubicaciones:
                    frame_detectado = frame
                    ubicaciones_detectadas = ubicaciones
                    rgb_detectado = rgb
                    angulo_usado = angulo
                    break

            if frame_detectado is None:
                frame_detectado = self._rotar_frame(frame_original, camera_rotation)

                alto, ancho = frame_detectado.shape[:2]
                if ancho > 900:
                    escala = 900 / ancho
                    frame_detectado = cv2.resize(
                        frame_detectado,
                        (900, int(alto * escala)),
                    )

                cv2.putText(
                    frame_detectado,
                    "No se detecta rostro. Ajuste luz, distancia o rotacion.",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

            else:
                ahora = time.time()

                if (ahora - ultimo_tiempo) >= self.PAUSA_ENTRE:
                    try:
                        encodings = face_recognition.face_encodings(
                            rgb_detectado,
                            ubicaciones_detectadas,
                        )

                        if encodings:
                            encodings_acumulados.append(encodings[0])
                            ultimo_tiempo = ahora

                            print(
                                f"[CameraService] Captura "
                                f"{len(encodings_acumulados)}/{self.TOTAL_CAPTURAS} "
                                f"| rotación usada: {angulo_usado}°"
                            )
                        else:
                            print("[CameraService] Rostro detectado, pero no se pudo generar encoding.")

                    except Exception as e:
                        print(f"[CameraService] Error generando encoding: {e}")

                for (top, right, bottom, left) in ubicaciones_detectadas:
                    cv2.rectangle(
                        frame_detectado,
                        (left, top),
                        (right, bottom),
                        (0, 255, 0),
                        2,
                    )

            h, w = frame_detectado.shape[:2]

            texto_contador = f"{len(encodings_acumulados)}/{self.TOTAL_CAPTURAS}"

            cv2.rectangle(
                frame_detectado,
                (10, h - 50),
                (160, h - 10),
                (0, 0, 0),
                -1,
            )

            cv2.putText(
                frame_detectado,
                texto_contador,
                (25, h - 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame_detectado,
                "ESC: Cancelar",
                (w - 160, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (180, 180, 180),
                1,
            )

            cv2.imshow(nombre_ventana, frame_detectado)

            if cv2.waitKey(1) & 0xFF == 27:
                encodings_acumulados = []
                break

        camara.release()
        cv2.destroyAllWindows()

        if not encodings_acumulados:
            print("[CameraService] Captura cancelada o sin encodings válidos.")
            return None

        encoding_promedio = np.mean(encodings_acumulados, axis=0)
        print(
            f"[CameraService] Encoding final promediado de "
            f"{len(encodings_acumulados)} capturas."
        )

        return encoding_promedio.astype(np.float64).tobytes()

    def _rotar_frame(self, frame, rotation: int):
        if rotation == 90:
            return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        if rotation == 180:
            return cv2.rotate(frame, cv2.ROTATE_180)

        if rotation == 270:
            return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        return frame

    def _normalizar_fuente(self, source):
        """
        Corrige fuentes de cámara IP.
        Ejemplo:
        https://192.168.1.3:8080  ->  http://192.168.1.3:8080/video
        192.168.1.3:8080          ->  http://192.168.1.3:8080/video
        """
        if not isinstance(source, str):
            return source

        source = source.strip()

        if not source.startswith("http://") and not source.startswith("https://"):
            source = "http://" + source

        if source.startswith("https://"):
            source = source.replace("https://", "http://", 1)

        if source.endswith("/"):
            source = source[:-1]

        if not source.endswith("/video"):
            source = source + "/video"

        return source

    # ── Utilidades para reconocimiento ───────────────────────────────────────

    @staticmethod
    def bytes_a_encoding(data: bytes) -> Optional[np.ndarray]:
        if data is None:
            return None
        return np.frombuffer(data, dtype=np.float64)

    @staticmethod
    def encodings_son_iguales(
        encoding_bd: bytes,
        encoding_nuevo: np.ndarray,
        tolerancia: float = 0.6,
    ) -> bool:
        try:
            import face_recognition

            enc_bd = CameraService.bytes_a_encoding(encoding_bd)

            if enc_bd is None:
                return False

            return bool(
                face_recognition.compare_faces(
                    [enc_bd],
                    encoding_nuevo,
                    tolerancia,
                )[0]
            )

        except Exception as e:
            print(f"[CameraService] Error al comparar: {e}")
            return False