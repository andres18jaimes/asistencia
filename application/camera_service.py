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


class CameraService:

    TOTAL_CAPTURAS  = 10     # <-- ahora 20
    PAUSA_ENTRE     = 0.3   # segundos entre cada captura automática (ajústalo a tu gusto)
    CAMARA_INDEX    = 0
    TOLERANCIA      = 0.6

    def capture_faces(self, nombre: str) -> Optional[bytes]:
        """
        Abre la cámara y captura automáticamente 20 encodings.
        Ventana limpia: solo rectángulo, contador pequeño y opción de cancelar.
        """
        try:
            import face_recognition
        except ImportError:
            print("[CameraService] Instala face-recognition: pip install face-recognition")
            return None

        camara = cv2.VideoCapture(self.CAMARA_INDEX)
        if not camara.isOpened():
            print("[CameraService] No se pudo abrir la cámara.")
            return None

        encodings_acumulados  = []
        ultimo_tiempo         = time.time() - self.PAUSA_ENTRE  # primera captura inmediata

        nombre_ventana = f"Registro: {nombre}  |  ESC para cancelar"

        while len(encodings_acumulados) < self.TOTAL_CAPTURAS:
            ret, frame = camara.read()
            if not ret:
                break

            rgb         = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ubicaciones = face_recognition.face_locations(rgb, model="hog")
            ahora       = time.time()

            # Intento de captura automática
            if ubicaciones and (ahora - ultimo_tiempo) >= self.PAUSA_ENTRE:
                encodings = face_recognition.face_encodings(rgb, ubicaciones)
                if encodings:
                    encodings_acumulados.append(encodings[0])
                    ultimo_tiempo = ahora
                    print(f"[CameraService] Captura {len(encodings_acumulados)}/{self.TOTAL_CAPTURAS}")

            # Dibujar rectángulo verde alrededor de cada rostro
            for (top, right, bottom, left) in ubicaciones:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            h, w = frame.shape[:2]

            # Pequeño contador discreto (esquina inferior derecha)
            capturadas = len(encodings_acumulados)
            texto_contador = f"{capturadas}/{self.TOTAL_CAPTURAS}"
            (tw, th), _ = cv2.getTextSize(texto_contador, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            # fondo semitransparente para que se lea bien
            cv2.rectangle(frame, (w - tw - 20, h - th - 20), (w - 5, h - 5), (0, 0, 0), -1)
            cv2.putText(frame, texto_contador,
                        (w - tw - 10, h - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # “ESC: Cancelar” arriba a la derecha
            cv2.putText(frame, "ESC: Cancelar",
                        (w - 155, 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1)

            cv2.imshow(nombre_ventana, frame)

            if cv2.waitKey(1) & 0xFF == 27:
                encodings_acumulados = []
                break

        camara.release()
        cv2.destroyAllWindows()

        if not encodings_acumulados:
            print("[CameraService] Captura cancelada o sin rostros detectados.")
            return None

        encoding_promedio = np.mean(encodings_acumulados, axis=0)
        print(f"[CameraService] Encoding final promediado de {len(encodings_acumulados)} capturas.")
        return encoding_promedio.tobytes()

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