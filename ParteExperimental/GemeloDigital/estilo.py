"""
Estilo oscuro "pixel art" de la aplicación: colores, fuentes y estilo de matplotlib.

Fuentes: si en la carpeta GemeloDigital/fuentes/ hay archivos .ttf, se cargan.
La aplicación busca, en este orden:
  - títulos: "Press Start 2P"  (PressStart2P-Regular.ttf)
  - texto  : "VT323"           (VT323-Regular.ttf), o "Silkscreen"
Las tres son de Google Fonts con licencia SIL Open Font License. Si no están,
se usa Consolas / Courier New. La animación del motor usa siempre su propia
fuente de mapa de bits (pixel.py), así que se ve pixelada en cualquier caso.

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md).
"""
from __future__ import annotations

from pathlib import Path

CARPETA_FUENTES = Path(__file__).with_name("fuentes")

# Paleta: fondo morado muy oscuro y acentos de neón.
FONDO = "#0d0b1e"
PANEL = "#16132d"
PANEL_2 = "#211c44"
BORDE = "#3d3478"
TEXTO = "#ece9ff"
TENUE = "#8c86bd"
CIAN = "#2de2e6"
MAGENTA = "#ff3cac"
AMARILLO = "#ffd319"
VERDE = "#39ff88"
NARANJA = "#ff8c42"
ROJO = "#ff2a4d"
MORADO = "#9b5de5"
AZUL = "#4d7cff"

FUENTE_TITULO = "Consolas"
FUENTE_TEXTO = "Consolas"
TAMANO_TEXTO = 14          # Se ajusta si se carga VT323 (es más pequeña a igual tamaño)


def cargar_fuentes():
    """Carga los .ttf de la carpeta de fuentes y elige las familias."""
    global FUENTE_TITULO, FUENTE_TEXTO, TAMANO_TEXTO
    familias = {}
    if CARPETA_FUENTES.is_dir():
        try:
            import customtkinter as ctk
            from PIL import ImageFont
        except ImportError:
            return familias
        for ttf in sorted(CARPETA_FUENTES.glob("*.ttf")):
            try:
                nombre = ImageFont.truetype(str(ttf), 12).getname()[0]
                ctk.FontManager.load_font(str(ttf))
                familias[nombre] = ttf
            except Exception:
                pass
    if "Press Start 2P" in familias:
        FUENTE_TITULO = "Press Start 2P"
    elif "Silkscreen" in familias:
        FUENTE_TITULO = "Silkscreen"
    if "VT323" in familias:
        FUENTE_TEXTO, TAMANO_TEXTO = "VT323", 20
    elif "Silkscreen" in familias:
        FUENTE_TEXTO, TAMANO_TEXTO = "Silkscreen", 12
    elif FUENTE_TITULO != "Consolas":
        FUENTE_TEXTO, TAMANO_TEXTO = FUENTE_TITULO, 9
    return familias


def fuente(tamano: int | None = None, titulo: bool = False, negrita: bool = False):
    """Tupla de fuente para customtkinter."""
    familia = FUENTE_TITULO if titulo else FUENTE_TEXTO
    if tamano is None:
        tamano = 11 if titulo and familia != "Consolas" else TAMANO_TEXTO
    return (familia, tamano, "bold") if negrita else (familia, tamano)


def estilo_matplotlib(familias: dict):
    """Ajusta matplotlib al estilo de la aplicación."""
    import matplotlib
    from matplotlib import font_manager
    familia = "monospace"
    for nombre in ("VT323", "Silkscreen", "Press Start 2P"):
        if nombre in familias:
            try:
                font_manager.fontManager.addfont(str(familias[nombre]))
                familia = nombre
                break
            except Exception:
                pass
    matplotlib.rcParams.update({
        "font.family": familia,
        "font.size": 13 if familia == "VT323" else 9,
        "figure.facecolor": PANEL,
        "axes.facecolor": FONDO,
        "axes.edgecolor": BORDE,
        "axes.labelcolor": TEXTO,
        "axes.linewidth": 1.5,
        "xtick.color": TENUE,
        "ytick.color": TENUE,
        "grid.color": BORDE,
        "grid.linestyle": ":",
        "grid.alpha": 0.7,
        "text.color": TEXTO,
        "legend.facecolor": PANEL_2,
        "legend.edgecolor": BORDE,
        "legend.fontsize": 11 if familia == "VT323" else 8,
        "lines.antialiased": False,      # Líneas sin suavizado: aspecto pixelado
        "lines.solid_joinstyle": "miter",
        "axes.unicode_minus": False,
    })
