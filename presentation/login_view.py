# presentation/login_view.py
import tkinter as tk
from tkinter import messagebox

PIN_CORRECTO = "1234"


class LoginView:
    def __init__(self, root, on_success=None):
        """
        root       : tk.Tk() compartido (gestionado desde main.py)
        on_success : callable que se ejecuta cuando el PIN es correcto
        """
        self.root = root
        self.on_success = on_success
        self.root.configure(bg="white")
        self._placeholder_active = False
        self._build_ui()

    def _build_ui(self):
        card = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        card.place(relx=0.5, rely=0.5, anchor="center", width=320, height=380)

        self._draw_lock_icon(card)

        tk.Label(
            card,
            text="Sistema de Asistencia",
            font=("Georgia", 17),
            bg="white", fg="#1a1a1a"
        ).pack(pady=(10, 2))

        tk.Label(
            card,
            text="Ingrese su PIN para continuar",
            font=("Arial", 10),
            bg="white", fg="#666666"
        ).pack(pady=(0, 18))

        tk.Label(
            card,
            text="PIN:",
            font=("Arial", 10, "bold"),
            bg="white", fg="#1a1a1a",
            anchor="w"
        ).pack(fill="x", padx=30)

        self.pin_var = tk.StringVar()
        self.entry = tk.Entry(
            card,
            textvariable=self.pin_var,
            font=("Arial", 12),
            relief="solid", bd=1,
            fg="#333333",
        )
        self.entry.pack(fill="x", padx=30, ipady=8, pady=(4, 16))
        self.entry.bind("<Return>", lambda e: self._ingresar())
        self.entry.focus_set()

        self._add_placeholder(self.entry, "Ingrese PIN")

        tk.Button(
            card,
            text="Ingresar",
            font=("Arial", 12, "bold"),
            bg="#4F79A7", fg="white",
            activebackground="#3a5f8a", activeforeground="white",
            relief="flat", cursor="hand2",
            command=self._ingresar
        ).pack(fill="x", padx=30, ipady=10)

        tk.Label(
            card,
            text="PIN de prueba: 1234",
            font=("Arial", 9),
            bg="white", fg="#999999"
        ).pack(pady=(14, 0))

    def _draw_lock_icon(self, parent):
        SIZE = 72
        c = tk.Canvas(parent, width=SIZE, height=SIZE,
                      bg="white", highlightthickness=0)
        c.pack(pady=(28, 4))

        R = 12
        c.create_rectangle(R, R, SIZE - R, SIZE - R,
                            fill="#4F79A7", outline="")
        corners = [(0, 0), (SIZE - 2*R, 0), (0, SIZE - 2*R), (SIZE - 2*R, SIZE - 2*R)]
        starts   = [90, 0, 180, 270]
        for (x, y), start in zip(corners, starts):
            c.create_arc(x, y, x + 2*R, y + 2*R,
                         start=start, extent=90,
                         fill="#4F79A7", outline="")

        CX, CY = SIZE // 2, SIZE // 2 - 4
        c.create_arc(CX - 13, CY - 14, CX + 13, CY + 10,
                     start=0, extent=180,
                     style="arc", outline="white", width=4)
        c.create_rectangle(CX - 14, CY + 2, CX + 14, CY + 22,
                            fill="white", outline="")
        c.create_oval(CX - 4, CY + 8, CX + 4, CY + 16,
                      fill="#4F79A7", outline="")

    def _add_placeholder(self, entry, placeholder):
        entry.config(show="", fg="#aaaaaa")
        entry.insert(0, placeholder)
        self._placeholder_active = True

        def on_focus_in(e):
            if self._placeholder_active:
                entry.delete(0, tk.END)
                entry.config(show="●", fg="#333333")
                self._placeholder_active = False

        def on_focus_out(e):
            if not entry.get():
                entry.config(show="", fg="#aaaaaa")
                entry.insert(0, placeholder)
                self._placeholder_active = True

        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _ingresar(self):
        if self._placeholder_active:
            messagebox.showwarning("Atención", "Ingrese su PIN.")
            return

        pin = self.pin_var.get().strip()
        if pin == PIN_CORRECTO:
            if self.on_success:
                self.on_success()
        else:
            messagebox.showerror("Error", "PIN incorrecto. Intente nuevamente.")
            self.pin_var.set("")
            self.entry.config(show="", fg="#aaaaaa")
            self.entry.insert(0, "Ingrese PIN")
            self._placeholder_active = True