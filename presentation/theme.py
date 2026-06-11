# presentation/theme.py
import customtkinter as ctk

# ─────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────

APP_NAME = "Sistema de Asistencia Facial"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─────────────────────────────────────────────
# COLORES PRINCIPALES
# ─────────────────────────────────────────────

COLOR_FONDO = "#0f172a"        # Fondo general
COLOR_PANEL = "#1e293b"        # Paneles / cards
COLOR_PANEL_2 = "#111827"      # Panel más oscuro
COLOR_BORDE = "#334155"        # Bordes suaves

COLOR_TEXTO = "#f8fafc"        # Texto principal
COLOR_TEXTO_SEC = "#94a3b8"    # Texto secundario
COLOR_MUTED = "#64748b"        # Texto apagado

COLOR_PRIMARIO = "#3b82f6"     # Azul moderno
COLOR_PRIMARIO_HOVER = "#2563eb"

COLOR_EXITO = "#10b981"        # Verde esmeralda
COLOR_EXITO_HOVER = "#059669"

COLOR_ADVERTENCIA = "#f59e0b"
COLOR_ERROR = "#ef4444"
COLOR_ERROR_HOVER = "#dc2626"

COLOR_TRANSPARENTE = "transparent"

# ─────────────────────────────────────────────
# FUENTES
# ─────────────────────────────────────────────

FONT_FAMILY = "Segoe UI"

FONT_TITLE = (FONT_FAMILY, 24, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 18, "bold")
FONT_TEXT = (FONT_FAMILY, 13)
FONT_TEXT_BOLD = (FONT_FAMILY, 13, "bold")
FONT_BUTTON = (FONT_FAMILY, 14, "bold")
FONT_SMALL = (FONT_FAMILY, 11)

# ─────────────────────────────────────────────
# TAMAÑOS
# ─────────────────────────────────────────────

SIDEBAR_WIDTH = 280
HEADER_HEIGHT = 70

RADIUS_PANEL = 16
RADIUS_BUTTON = 10
RADIUS_INPUT = 8

BTN_HEIGHT = 42
INPUT_HEIGHT = 40

PAD_MAIN_X = 40
PAD_MAIN_Y = 30

# ─────────────────────────────────────────────
# HELPERS VISUALES
# ─────────────────────────────────────────────

def apply_root_style(root, title=APP_NAME, geometry="1100x700"):
    root.title(title)
    root.geometry(geometry)
    root.minsize(1000, 650)
    root.configure(fg_color=COLOR_FONDO)


def card(parent, **kwargs):
    return ctk.CTkFrame(
        parent,
        fg_color=kwargs.get("fg_color", COLOR_PANEL),
        corner_radius=kwargs.get("corner_radius", RADIUS_PANEL),
        border_width=kwargs.get("border_width", 1),
        border_color=kwargs.get("border_color", COLOR_BORDE),
    )


def primary_button(parent, text, command=None, **kwargs):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=kwargs.get("height", BTN_HEIGHT),
        corner_radius=kwargs.get("corner_radius", RADIUS_BUTTON),
        font=kwargs.get("font", FONT_BUTTON),
        fg_color=kwargs.get("fg_color", COLOR_PRIMARIO),
        hover_color=kwargs.get("hover_color", COLOR_PRIMARIO_HOVER),
        text_color=COLOR_TEXTO,
    )


def success_button(parent, text, command=None, **kwargs):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=kwargs.get("height", BTN_HEIGHT),
        corner_radius=kwargs.get("corner_radius", RADIUS_BUTTON),
        font=kwargs.get("font", FONT_BUTTON),
        fg_color=COLOR_EXITO,
        hover_color=COLOR_EXITO_HOVER,
        text_color=COLOR_TEXTO,
    )


def danger_button(parent, text, command=None, **kwargs):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=kwargs.get("height", BTN_HEIGHT),
        corner_radius=kwargs.get("corner_radius", RADIUS_BUTTON),
        font=kwargs.get("font", FONT_BUTTON),
        fg_color=COLOR_ERROR,
        hover_color=COLOR_ERROR_HOVER,
        text_color=COLOR_TEXTO,
    )


def transparent_button(parent, text, command=None, **kwargs):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=kwargs.get("height", BTN_HEIGHT),
        corner_radius=kwargs.get("corner_radius", RADIUS_BUTTON),
        font=kwargs.get("font", FONT_BUTTON),
        fg_color="transparent",
        hover_color=COLOR_BORDE,
        text_color=COLOR_TEXTO,
    )


def input_text(parent, placeholder="", show=None, **kwargs):
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        show=show,
        height=kwargs.get("height", INPUT_HEIGHT),
        corner_radius=RADIUS_INPUT,
        font=FONT_TEXT,
        fg_color=COLOR_PANEL_2,
        border_color=COLOR_BORDE,
        text_color=COLOR_TEXTO,
        placeholder_text_color=COLOR_MUTED,
    )