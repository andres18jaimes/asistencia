# infrastructure/recognition/encoder.py

import face_recognition
import os

def cargar_encodings(ruta="data/fotos"):
    caras = []
    nombres = []

    for nombre in os.listdir(ruta):
        carpeta = os.path.join(ruta, nombre)

        for archivo in os.listdir(carpeta):
            img_path = os.path.join(carpeta, archivo)
            imagen = face_recognition.load_image_file(img_path)
            encoding = face_recognition.face_encodings(imagen)

            if encoding:
                caras.append(encoding[0])
                nombres.append(nombre)

    return caras, nombres