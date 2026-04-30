# 🎓 Sistema de Asistencia Estudiantil con Reconocimiento Facial

Sistema desarrollado en Python que permite registrar la asistencia de estudiantes mediante reconocimiento facial en tiempo real.

---

## 🚀 Descripción

Este proyecto implementa un sistema de control de asistencia que utiliza visión por computadora para identificar estudiantes automáticamente a través de una cámara.

El sistema permite:

- Registrar estudiantes mediante captura de imágenes
- Detectar y reconocer rostros en tiempo real
- Registrar asistencia automáticamente
- Generar reportes de asistencia

---

## 🧠 Tecnologías utilizadas

- Python 3.10 / 3.11
- OpenCV
- face_recognition (basado en dlib)
- Tkinter (interfaz gráfica)
- SQLite (en futuras versiones)

---

## 📁 Estructura del proyecto

```bash
asistencia/
├── application/       # Lógica de negocio
├── infrastructure/    # Reconocimiento y base de datos
├── presentation/      # Interfaz gráfica (GUI)
├── domain/            # Entidades del sistema
├── shared/            # Utilidades
├── assets/            # Iconos e imágenes
├── data/              # Datos (no incluidos en git)
├── docs/              # Documentación del proyecto
├── main.py            # Punto de entrada
└── requirements.txt
```

## ⚙️ Instalación
Clona el repositorio (reemplaza TU_USUARIO):
```bash
git clone https://github.com/TU_USUARIO/asistencia.git
cd asistencia
```

## En Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## En Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Ejecución
Linux (si tienes problemas con Wayland)
```bash
QT_QPA_PLATFORM=xcb python main.py
```

## Linux (estándar) y Windows
```bash
python main.py
```

- La carpeta data/fotos/ no se incluye en el repositorio por privacidad.
- La base de datos (SQLite) tampoco se incluye; se generará automáticamente al ejecutar el sistema.
- Se requiere una cámara funcional para el reconocimiento facial.

## Trabajo futuro
- Implementación completa con base de datos SQLite
- Mejora en la precisión del reconocimiento facial
- Interfaz gráfica más avanzada (estilos, notificaciones)
- Exportación de reportes a PDF o Excel

## 📄 Licencia
Uso académico – libre para fines educativos y de investigación.
No se permite el uso comercial sin autorización expresa de los autores.
