# presentation/register_view.py

import tkinter as tk
from application.camera_service import CameraService

class RegisterView:

    def __init__(self, root):
        self.root = root
        self.camera_service = CameraService()

        self.frame = tk.Frame(root)
        self.frame.pack()

        self.label = tk.Label(self.frame, text="Nombre:")
        self.label.pack()

        self.entry = tk.Entry(self.frame)
        self.entry.pack()

        self.btn = tk.Button(
            self.frame,
            text="Registrar",
            command=self.registrar
        )
        self.btn.pack()

    def registrar(self):
        nombre = self.entry.get()
        self.camera_service.capture_faces(nombre)