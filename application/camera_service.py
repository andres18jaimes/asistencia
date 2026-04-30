# application/camera_service.py

import cv2
import os

class CameraService:

    def capture_faces(self, nombre, max_fotos=20):
        ruta = os.path.join("data/fotos", nombre)

        if not os.path.exists(ruta):
            os.makedirs(ruta)

        face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

        )

        camara = cv2.VideoCapture(0)
        contador = 0

        while True:
            ret, frame = camara.read()
            if not ret:
                break

            gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rostros = face_cascade.detectMultiScale(gris, 1.3, 5)

            for (x, y, w, h) in rostros:
                rostro = frame[y:y+h, x:x+w]

                archivo = os.path.join(ruta, f"foto_{contador}.jpg")
                cv2.imwrite(archivo, rostro)
                contador += 1

                cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)

            cv2.imshow("Registro Facial", frame)

            if cv2.waitKey(1) == 27 or contador >= max_fotos:
                break

        camara.release()
        cv2.destroyAllWindows()

        return True