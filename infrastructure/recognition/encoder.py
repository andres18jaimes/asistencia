import face_recognition
import os

def cargar_encodings_por_curso(curso_id):
    from infrastructure.database.db_manager import DatabaseManager
    db = DatabaseManager(); conn = db.get_connection(); cursor = conn.cursor()
    
    # Obtener solo alumnos de este curso
    cursor.execute("SELECT nombre FROM estudiantes WHERE id_curso = ?", (curso_id,))
    alumnos = cursor.fetchall()
    conn.close()

    caras = []
    nombres = []
    for (nom,) in alumnos:
        ruta_carpeta = os.path.join("data/fotos", nom)
        if os.path.exists(ruta_carpeta):
            for archivo in os.listdir(ruta_carpeta):
                img = face_recognition.load_image_file(os.path.join(ruta_carpeta, archivo))
                enc = face_recognition.face_encodings(img)
                if enc:
                    caras.append(enc[0])
                    nombres.append(nom)
    return caras, nombres