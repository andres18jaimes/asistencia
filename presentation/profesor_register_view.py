import tkinter as tk
from tkinter import messagebox
# Importamos el gestor de base de datos que creamos antes
from infrastructure.database.db_manager import DatabaseManager

class ProfesorRegisterView:
    def __init__(self, root, on_back=None):
        self.root = root
        self.on_back = on_back # Función para regresar al Login
        self.db = DatabaseManager()
        self._build_ui()

    def _build_ui(self):
        # Tarjeta principal de registro
        self.card = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=520)

        tk.Label(self.card, text="Crear Cuenta de Profesor", font=("Georgia", 16, "bold"), 
                 bg="white", fg="#4F79A7").pack(pady=(20, 10))

        # Campos del formulario
        self.nombre_var = self._create_field("Nombre Completo:")
        self.correo_var = self._create_field("Correo Electrónico:")
        self.inst_var = self._create_field("Institución Educativa:")
        self.pin_var = self._create_field("PIN de Seguridad (4 dígitos):", show="●")

        # Botón Registrar
        tk.Button(self.card, text="Registrarme", font=("Arial", 12, "bold"),
                  bg="#5CB85C", fg="white", relief="flat", cursor="hand2",
                  command=self._registrar_profesor).pack(fill="x", padx=40, ipady=10, pady=(20, 10))

        # Enlace para volver al login
        btn_back = tk.Label(self.card, text="¿Ya tienes cuenta? Inicia sesión", 
                            font=("Arial", 9, "underline"), bg="white", fg="#4F79A7", cursor="hand2")
        btn_back.pack()
        btn_back.bind("<Button-1>", lambda e: self.on_back())

    def _create_field(self, label_text, show=""):
        tk.Label(self.card, text=label_text, font=("Arial", 9, "bold"), 
                 bg="white", fg="#333333").pack(anchor="w", padx=40)
        var = tk.StringVar()
        entry = tk.Entry(self.card, textvariable=var, font=("Arial", 11), 
                         relief="solid", bd=1, show=show)
        entry.pack(fill="x", padx=40, ipady=6, pady=(2, 12))
        return var

    def _registrar_profesor(self):
        # Validación simple
        if not all([self.nombre_var.get(), self.correo_var.get(), self.pin_var.get()]):
            messagebox.showwarning("Error", "Por favor llena los campos obligatorios.")
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO profesores (nombre, correo, pin, institucion)
                VALUES (?, ?, ?, ?)
            ''', (self.nombre_var.get(), self.correo_var.get(), self.pin_var.get(), self.inst_var.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Cuenta creada. Ahora puedes iniciar sesión.")
            self.on_back() # Volver al login tras el éxito
        except Exception as e:
            messagebox.showerror("Error", f"El correo ya está registrado o hubo un error: {e}")