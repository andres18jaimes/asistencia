import sqlite3

class DatabaseManager:
    def __init__(self, db_name="asistencia.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Tabla de Profesores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profesores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT UNIQUE NOT NULL,
                pin TEXT NOT NULL,
                institucion TEXT
            )
        ''')

        # 2. Tabla de Cursos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_curso TEXT NOT NULL,
                grupo TEXT NOT NULL,  -- <--- Columna añadida
                id_profesor INTEGER,
                FOREIGN KEY (id_profesor) REFERENCES profesores (id)
            )
        ''')

        # 3. Tabla de Estudiantes (Aquí guardaremos el rostro)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                id_curso INTEGER,
                encoding_facial BLOB, 
                FOREIGN KEY (id_curso) REFERENCES cursos (id)
            )
        ''')

        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente.")