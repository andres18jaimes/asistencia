# infrastructure/recognition/face_engine.py

import face_recognition
import cv2

def reconocer(caras_conocidas, nombres):
    camara = cv2.VideoCapture(0)
    registrados = []

    while True:
        ret, frame = camara.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        ubicaciones = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb)

        resultados_finales = []

        for (top, right, bottom, left), face_encoding in zip(ubicaciones, encodings):

            resultados = face_recognition.compare_faces(
                caras_conocidas, face_encoding
            )

            nombre = "Desconocido"

            if True in resultados:
                index = resultados.index(True)
                nombre = nombres[index]

            resultados_finales.append(nombre)

            cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
            cv2.putText(frame, nombre, (left, top-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        cv2.imshow("Reconocimiento", frame)

        if cv2.waitKey(1) == 27:
            break

    camara.release()
    cv2.destroyAllWindows()

    return resultados_finales