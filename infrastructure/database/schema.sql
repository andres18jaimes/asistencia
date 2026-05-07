-- Tabla de profesores (para login y asignación de cursos)
CREATE TABLE IF NOT EXISTS profesores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL
);

-- Tabla de cursos (cada curso pertenece a un profesor)
CREATE TABLE IF NOT EXISTS cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_curso TEXT NOT NULL,
    grupo TEXT,
    id_profesor INTEGER,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id)
);

-- Tabla de estudiantes
CREATE TABLE IF NOT EXISTS estudiantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    identificacion TEXT UNIQUE,
    id_curso INTEGER,
    encoding_facial BLOB,
    FOREIGN KEY (id_curso) REFERENCES cursos(id)
);

-- Tabla de asistencias
CREATE TABLE IF NOT EXISTS asistencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estudiante INTEGER NOT NULL,
    id_curso INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    tipo TEXT DEFAULT 'automatico',
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id),
    FOREIGN KEY (id_curso) REFERENCES cursos(id)
);