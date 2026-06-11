"""
application/camera_service.py

Captura automática de 10 encodings faciales.
- Sin barra de progreso.
- Sin mensajes intrusivos, solo el rectángulo de detección y un contador pequeño.
- Retorna el promedio de los encodings como bytes (sin guardar fotos en disco).
"""

import cv2
import time
import numpy as np
from typing import Optional
from config.settings import CAMERA_SOURCE, TOTAL_FACE_CAPTURES, PAUSE_BETWEEN_CAPTURES


class CameraService:

    from config.settings import CAMERA_SOURCE, TOTAL_FACE_CAPTURES, PAUSE_BETWEEN_CAPTURES

    TOTAL_CAPTURAS = TOTAL_FACE_CAPTURES
    PAUSA_ENTRE = PAUSE_BETWEEN_CAPTURES
    CAMARA_INDEX = CAMERA_SOURCE
    TOLERANCIA      = 0.6

    def capture_faces(self, nombre: str, camera_source=None) -> Optional[bytes]:
        """
        #Abre la cámara y captura automáticamente encodings faciales.
        Versión mejorada para cámara de PC y cámara IP del celular.
        Prueba rotaciones para corregir imagen lateral del celular.
        """
        try:
            import face_recognition
        except ImportError:
            print("[CameraService] Instala face-recognition: pip install face-recognition")
            return None

        source = self.CAMARA_INDEX if camera_source is None else camera_source

        print(f"[CameraService] Intentando abrir cámara con fuente: {source}")

        camara = cv2.VideoCapture(source)

        if not camara.isOpened():
            print(f"[CameraService] No se pudo abrir la cámara con fuente: {source}")
            return None

        encodings_acumulados = []
        ultimo_tiempo = time.time() - self.PAUSA_ENTRE

        nombre_ventana = f"Registro: {nombre} | ESC para cancelar"

        def rotar_frame(frame, angulo):
            if angulo == 90:
                return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            if angulo == 180:
                return cv2.rotate(frame, cv2.ROTATE_180)
            if angulo == 270:
                return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            return frame

        while len(encodings_acumulados) < self.TOTAL_CAPTURAS:
            ret, frame_original = camara.read()

            if not ret or frame_original is None:
                print("[CameraService] No se pudo leer frame de la cámara.")
                break

            frame_detectado = None
            ubicaciones_detectadas = []
            rgb_detectado = None
            angulo_usado = 0

            # Probamos varias rotaciones porque el celular a veces manda imagen acostada
            for angulo in [0, 90, 270, 180]:
                frame = rotar_frame(frame_original, angulo)

                # Reducimos un poco si el frame es muy grande para mejorar rendimiento
                alto, ancho = frame.shape[:2]
                if ancho > 900:
                    escala = 900 / ancho
                    frame = cv2.resize(frame, (900, int(alto * escala)))

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = np.ascontiguousarray(rgb)

                ubicaciones = face_recognition.face_locations(
                    rgb,
                    number_of_times_to_upsample=2,
                    model="hog"
                )

                if ubicaciones:
                    frame_detectado = frame
                    ubicaciones_detectadas = ubicaciones
                    rgb_detectado = rgb
                    angulo_usado = angulo
                    break

            if frame_detectado is None:
                frame_detectado = frame_original
                alto, ancho = frame_detectado.shape[:2]
                if ancho > 900:
                    escala = 900 / ancho
                    frame_detectado = cv2.resize(frame_detectado, (900, int(alto * escala)))

                cv2.putText(
                    frame_detectado,
                    "No se detecta rostro. Ajuste luz, distancia o giro del celular.",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )
            else:
                ahora = time.time()

                if ubicaciones_detectadas and (ahora - ultimo_tiempo) >= self.PAUSA_ENTRE:
                    try:
                        encodings = face_recognition.face_encodings(
                            rgb_detectado,
                            ubicaciones_detectadas
                        )

                        if encodings:
                            # Tomamos el primer rostro detectado
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

                # Dibujar rectángulos
                for (top, right, bottom, left) in ubicaciones_detectadas:
                    cv2.rectangle(
                        frame_detectado,
                        (left, top),
                        (right, bottom),
                        (0, 255, 0),
                        2
                    )

            h, w = frame_detectado.shape[:2]

            texto_contador = f"{len(encodings_acumulados)}/{self.TOTAL_CAPTURAS}"
            cv2.rectangle(frame_detectado, (10, h - 50), (150, h - 10), (0, 0, 0), -1)
            cv2.putText(
                frame_detectado,
                texto_contador,
                (25, h - 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame_detectado,
                "ESC: Cancelar",
                (w - 160, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (180, 180, 180),
                1
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
        print(f"[CameraService] Encoding final promediado de {len(encodings_acumulados)} capturas.")

        return encoding_promedio.astype(np.float64).tobytes()

    # ── Utilidades para reconocimiento ───────────────────────────────────────

    @staticmethod
    def bytes_a_encoding(data: bytes) -> Optional[np.ndarray]:
        if data is None:
            return None
        return np.frombuffer(data, dtype=np.float64)

    @staticmethod
    def encodings_son_iguales(encoding_bd: bytes, encoding_nuevo: np.ndarray,
                               tolerancia: float = 0.6) -> bool:
        try:
            import face_recognition
            enc_bd = CameraService.bytes_a_encoding(encoding_bd)
            if enc_bd is None:
                return False
            return bool(face_recognition.compare_faces([enc_bd], encoding_nuevo, tolerancia)[0])
        except Exception as e:
            print(f"[CameraService] Error al comparar: {e}")
            return False