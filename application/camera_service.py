import cv2
import os

class CameraService:
    def capture_faces(self, nombre, curso_id, max_fotos=15):
        ruta = os.path.join("data/fotos", nombre)
        if not os.path.exists(ruta): os.makedirs(ruta)

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        camara = cv2.VideoCapture(0)
        contador = 0

        while contador < max_fotos:
            ret, frame = camara.read()
            if not ret: break
            gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rostros = face_cascade.detectMultiScale(gris, 1.3, 5)

            for (x, y, w, h) in rostros:
                rostro = frame[y:y+h, x:x+w]
                cv2.imwrite(os.path.join(ruta, f"{contador}.jpg"), rostro)
                contador += 1
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

            cv2.imshow("Registrando Rostro - Presione ESC para salir", frame)
            if cv2.waitKey(1) == 27: break

        camara.release()
        cv2.destroyAllWindows()

        # Registro en Base de Datos
        try:
            from infrastructure.database.db_manager import DatabaseManager
            db = DatabaseManager(); conn = db.get_connection(); cursor = conn.cursor()
            cursor.execute("INSERT INTO estudiantes (nombre, id_curso) VALUES (?, ?)", (nombre, curso_id))
            conn.commit(); conn.close()
            return True
        except Exception as e:
            print(f"Error BD: {e}"); return False