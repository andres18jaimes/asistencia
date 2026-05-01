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
        # 1. Creamos una ÚNICA tarjeta centrada
        self.card = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=520)

        # 2. Dibujamos el icono dentro de self.card
        self._draw_lock_icon(self.card)

        # 3. Título del sistema
        tk.Label(
            self.card, text="Sistema de Asistencia",
            font=("Georgia", 17, "bold"), bg="white", fg="#1a1a1a"
        ).pack(pady=(10, 20))

        # 4. Campo de Correo Electrónico
        tk.Label(
            self.card, text="Correo Electrónico:", font=("Arial", 9, "bold"), 
            bg="white", fg="#333333"
        ).pack(anchor="w", padx=40)
        
        self.correo_var = tk.StringVar()
        self.correo_entry = tk.Entry(
            self.card, textvariable=self.correo_var, font=("Arial", 11), 
            relief="solid", bd=1
        )
        self.correo_entry.pack(fill="x", padx=40, ipady=7, pady=(2, 15))

        # 5. Campo de PIN
        tk.Label(
            self.card, text="PIN de Seguridad:", font=("Arial", 9, "bold"), 
            bg="white", fg="#333333"
        ).pack(anchor="w", padx=40)

        self.pin_var = tk.StringVar()
        self.entry = tk.Entry(
            self.card, textvariable=self.pin_var, font=("Arial", 11), 
            relief="solid", bd=1, show="●"
        )
        self.entry.pack(fill="x", padx=40, ipady=7, pady=(2, 25))
        
        # Configuramos el foco inicial y el Enter
        self.entry.bind("<Return>", lambda e: self._ingresar())
        
        # 6. Botón de Ingresar (ahora sí visible en self.card)
        tk.Button(
            self.card, text="INGRESAR", font=("Arial", 11, "bold"),
            bg="#4F79A7", fg="white", relief="flat", cursor="hand2",
            activebackground="#3a5f8a", activeforeground="white",
            command=self._ingresar
        ).pack(fill="x", padx=40, ipady=10)

        # 7. Enlace para registro
        btn_reg = tk.Label(
            self.card, text="¿No tienes cuenta? Regístrate aquí", 
            font=("Arial", 9, "underline"), bg="white", fg="#4F79A7", cursor="hand2"
        )
        btn_reg.pack(pady=20)
        btn_reg.bind("<Button-1>", lambda e: self._ir_a_registro())

    def _ir_a_registro(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        # Fíjate bien en las mayúsculas aquí:
        from presentation.profesor_register_view import ProfesorRegisterView
        ProfesorRegisterView(self.root, on_back=lambda: self._volver_al_login())

    def _volver_al_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.__init__(self.root, self.on_success)

#        tk.Label(
#            card,
#            text="PIN de prueba: 1234",
#            font=("Arial", 9),
#            bg="white", fg="#999999"
#        ).pack(pady=(14, 0))

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
        correo = self.correo_var.get().strip()
        pin = self.pin_var.get().strip()

        if not correo or not pin:
            messagebox.showwarning("Atención", "Ingrese correo y PIN.")
            return

        from infrastructure.database.db_manager import DatabaseManager
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Validamos ambos campos
        cursor.execute("SELECT id, nombre FROM profesores WHERE correo = ? AND pin = ?", (correo, pin))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            # resultado[0] es el ID, resultado[1] es el Nombre
            print(f"Bienvenido Profesor {resultado[1]}")
            if self.on_success:
                # IMPORTANTE: Pasamos los datos del profesor al éxito
                self.on_success(resultado[0], resultado[1]) 
        else:
            messagebox.showerror("Error", "Correo o PIN incorrectos.")