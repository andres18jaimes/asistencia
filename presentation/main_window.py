# presentation/main_window.py
import os
import tkinter as tk
from PIL import Image, ImageTk

ASSETS_DIR = "assets"
TAMANO_ICONO = (56, 56)


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#EDEDED")

        self.img_registrar      = None
        self.img_reconocimiento = None
        self.img_asistencias    = None
        self.img_reportes       = None

        try:
            self.img_registrar      = self._cargar_icono("user.png")
            self.img_reconocimiento = self._cargar_icono("face.png")
            self.img_asistencias    = self._cargar_icono("list.png")
            self.img_reportes       = self._cargar_icono("report.png")
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar las imágenes. {e}")

        self._build_ui()

    def _cargar_icono(self, nombre_archivo):
        ruta = os.path.join(ASSETS_DIR, nombre_archivo)
        img = Image.open(ruta).convert("RGBA")
        img = img.resize(TAMANO_ICONO, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def _build_ui(self):
        self._create_header()
        self._create_welcome()
        self._create_buttons()

    # ── HEADER ───────────────────────────────────────────────
    def _create_header(self):
        header = tk.Frame(self.root, bg="#4F79A7", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Sistema de Asistencia Estudiantil",
            bg="#4F79A7", fg="white",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=20, pady=10)

        tk.Button(
            header,
            text="Salir",
            bg="#D9534F", fg="white",
            activebackground="#C9302C", activeforeground="white",
            relief="flat", padx=10, pady=4,
            command=self.root.quit
        ).pack(side="right", padx=20, pady=12)

    # ── BIENVENIDA ───────────────────────────────────────────
    def _create_welcome(self):
        frame = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        frame.pack(padx=40, pady=(20, 10), fill="x")

        tk.Label(
            frame, text="Panel Principal",
            font=("Arial", 14, "bold"), bg="white"
        ).pack(anchor="w", padx=20, pady=(10, 0))

        tk.Label(
            frame, text="Seleccione una opción",
            bg="white", fg="gray"
        ).pack(anchor="w", padx=20, pady=(2, 10))

    # ── BOTONES ──────────────────────────────────────────────
    def _create_buttons(self):
        outer = tk.Frame(self.root, bg="#EDEDED")
        outer.pack(expand=True, fill="both")

        container = tk.Frame(outer, bg="#EDEDED")
        container.place(relx=0.5, rely=0.5, anchor="center")

        cards = [
            ("Registrar Estudiante",   "#5CB85C", 0, 0, self.img_registrar),
            ("Iniciar Reconocimiento", "#5BC0DE", 0, 1, self.img_reconocimiento),
            ("Ver Asistencias",        "#F0AD4E", 1, 0, self.img_asistencias),
            ("Reportes",               "#4E79A7", 1, 1, self.img_reportes),
        ]
        for text, color, row, col, image in cards:
            self._create_card(container, text, color, row, col, image)

    # ── TARJETA ──────────────────────────────────────────────
    def _create_card(self, parent, text, color, row, col, image=None):
        CARD_W, CARD_H = 200, 160

        frame = tk.Frame(
            parent, bg="white", bd=2, relief="solid",
            width=CARD_W, height=CARD_H
        )
        frame.grid(row=row, column=col, padx=20, pady=20)
        frame.grid_propagate(False)

        inner = tk.Frame(frame, bg=color)
        inner.place(relx=0, rely=0, relwidth=1, relheight=1)

        if image:
            tk.Label(inner, image=image, bg=color).pack(pady=(18, 6))

        tk.Label(
            inner,
            text=text,
            bg=color, fg="white",
            font=("Arial", 10, "bold"),
            wraplength=CARD_W - 20,
            justify="center"
        ).pack(pady=(0, 10))

        for widget in (inner, *inner.winfo_children()):
            widget.bind("<Button-1>", lambda e, t=text: self._on_card_click(t))
            widget.bind("<Enter>",    lambda e, f=inner, c=color: f.configure(bg=self._darken(c)))
            widget.bind("<Leave>",    lambda e, f=inner, c=color: f.configure(bg=c))

    def _on_card_click(self, text):
        print(f"Acción: {text}")

    @staticmethod
    def _darken(hex_color, factor=0.85):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = (int(c * factor) for c in (r, g, b))
        return f"#{r:02x}{g:02x}{b:02x}"