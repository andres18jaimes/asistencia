import tkinter as tk
from tkinter import PhotoImage

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Asistencia Estudiantil")
        self.root.geometry("900x600")
        self.root.configure(bg="#EDEDED")

        # 🔥 CARGA DE IMÁGENES (Opcional: Si no tienes imágenes, el código manejará el error)
        self.img_registrar = None
        self.img_reconocimiento = None
        self.img_asistencias = None
        self.img_reportes = None

        # Intentar cargar imágenes si existen
        try:
            # Asegúrate de tener archivos como 'icono_usuario.png' en la misma carpeta o ajustar la ruta
            self.img_registrar = PhotoImage(file="user.png")
            self.img_reconocimiento = PhotoImage(file="face.png")
            self.img_asistencias = PhotoImage(file="list.png")
            self.img_reportes = PhotoImage(file="report.png")
        except tk.TclError:
            print("Advertencia: No se encontraron las imágenes. Se mostrarán solo texto.")

        self.build_ui()

    def build_ui(self):
        self.create_header()
        self.create_welcome()
        self.create_buttons()

    # 🔷 HEADER
    def create_header(self):
        header = tk.Frame(self.root, bg="#4F79A7", height=60)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="Sistema de Asistencia Estudiantil",
            bg="#4F79A7",
            fg="white",
            font=("Arial", 16, "bold")
        )
        title.pack(side="left", padx=20, pady=10)

        exit_btn = tk.Button(
            header,
            text="Salir",
            bg="#D9534F",
            fg="white",
            command=self.root.quit
        )
        exit_btn.pack(side="right", padx=20, pady=10)

    # 🧾 BIENVENIDA
    def create_welcome(self):
        frame = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        frame.pack(padx=40, pady=20, fill="x")

        title = tk.Label(
            frame,
            text="Panel Principal",
            font=("Arial", 14, "bold"),
            bg="white"
        )
        title.pack(anchor="w", padx=20, pady=(10, 0))

        subtitle = tk.Label(
            frame,
            text="Seleccione una opción",
            bg="white",
            fg="gray"
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 10))

    # 🔲 BOTONES
    def create_buttons(self):
        container = tk.Frame(self.root, bg="#EDEDED")
        container.pack(padx=40, pady=10)

        self.create_card(container, "Registrar Estudiante", "#5CB85C", 0, 0, self.img_registrar)
        self.create_card(container, "Iniciar Reconocimiento", "#5BC0DE", 0, 1, self.img_reconocimiento)
        self.create_card(container, "Ver Asistencias", "#F0AD4E", 1, 0, self.img_asistencias)
        self.create_card(container, "Reportes", "#4E79A7", 1, 1, self.img_reportes)

    # 🧩 COMPONENTE REUTILIZABLE
    def create_card(self, parent, text, color, row, col, image=None):
        frame = tk.Frame(parent, bg="white", bd=1, relief="solid", width=280, height=140)
        frame.grid(row=row, column=col, padx=20, pady=20)
        frame.grid_propagate(False)  # 🔥 clave

        btn = tk.Button(
            frame,
            text=text,
            bg=color,
            fg="white",
            font=("Arial", 11, "bold"),
            compound="top"
        )

        if image:
            btn.config(image=image)

        btn.pack(expand=True, fill="both", padx=10, pady=10)