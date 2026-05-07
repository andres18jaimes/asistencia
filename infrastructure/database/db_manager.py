import sqlite3
import os
from pathlib import Path

# Ruta absoluta a la BD, relativa a este archivo para independencia del CWD
_BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = _BASE_DIR / "asistencia.db"


class DatabaseManager:
    def __init__(self, db_name: str = None):
        self.db_name = str(db_name) if db_name else str(DB_PATH)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        # Activar claves foráneas en cada conexión
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Tabla de Profesores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profesores (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre     TEXT NOT NULL,
                correo     TEXT UNIQUE NOT NULL,
                pin        TEXT NOT NULL,
                institucion TEXT
            )
        ''')

        # 2. Tabla de Cursos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cursos (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_curso TEXT NOT NULL,
                grupo        TEXT NOT NULL,
                id_profesor  INTEGER,
                FOREIGN KEY (id_profesor) REFERENCES profesores (id)
            )
        ''')

        # 3. Tabla de Estudiantes — incluye identificacion (RF-01)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre           TEXT NOT NULL,
                identificacion   TEXT,
                id_curso         INTEGER,
                encoding_facial  BLOB,
                FOREIGN KEY (id_curso) REFERENCES cursos (id)
            )
        ''')

        # 4. Tabla de Asistencias (RF-10, RF-11) — antes no existía
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asistencias (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                id_estudiante  INTEGER NOT NULL,
                id_curso       INTEGER NOT NULL,
                fecha          TEXT NOT NULL,    -- "YYYY-MM-DD"
                hora           TEXT NOT NULL,    -- "HH:MM:SS"
                tipo           TEXT DEFAULT "automatico",  -- "automatico" | "manual"
                FOREIGN KEY (id_estudiante) REFERENCES estudiantes (id),
                FOREIGN KEY (id_curso)      REFERENCES cursos (id),
                UNIQUE (id_estudiante, id_curso, fecha)    -- RF-12: sin duplicados por día
            )
        ''')

        conn.commit()

        # ── Migración segura: agregar columna 'identificacion' si no existe ──
        # (para bases de datos ya creadas sin esa columna)
        cursor.execute("PRAGMA table_info(estudiantes)")
        columnas = [col[1] for col in cursor.fetchall()]
        if "identificacion" not in columnas:
            cursor.execute(
                "ALTER TABLE estudiantes ADD COLUMN identificacion TEXT"
            )
            conn.commit()
            print("[DB] Columna 'identificacion' agregada a tabla estudiantes.")

        conn.close()
        print(f"[DB] Base de datos lista → {self.db_name}")