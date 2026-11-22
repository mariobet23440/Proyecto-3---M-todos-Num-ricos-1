"""
Pixel art de la aplicación: fuente de mapa de bits, perillas y animación del motor.

Todo se dibuja con Pillow en una imagen de baja resolución (sin suavizado) y se
amplía con el vecino más cercano, para que cada píxel se vea como un bloque.

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md).
"""
from __future__ import annotations

import math
import time
import tkinter as tk
import unicodedata

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk

import estilo as E

# =============================================================================
#  Fuente de mapa de bits 5×7 (cada número es una fila de 5 bits)
# =============================================================================
GLIFOS = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11), "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E), "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F), "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F), "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E), "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11), "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11), "N": (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E), "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D), "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E), "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E), "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A), "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04), "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E), "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F), "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02), "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E), "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E), "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0), ".": (0, 0, 0, 0, 0, 0x0C, 0x0C), ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0), "-": (0, 0, 0, 0x1F, 0, 0, 0), "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10), "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "%": (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03), "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08), "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04), ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02), "_": (0, 0, 0, 0, 0, 0, 0x1F),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A), "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E), "*": (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    "|": (0x04,) * 7, "'": (0x04, 0x04, 0, 0, 0, 0, 0), "°": (0x0C, 0x12, 0x12, 0x0C, 0, 0, 0),
    "Θ": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x0E), "Ω": (0, 0, 0x11, 0x11, 0x15, 0x15, 0x0A),
    "·": (0, 0, 0, 0x04, 0, 0, 0),
}


def _normalizar(caracter: str) -> str:
    if caracter in GLIFOS:
        return caracter
    c = caracter.upper()
    if c in ("Θ", "θ"):
        return "Θ"
    if c in ("Ω", "ω"):
        return "Ω"
    base = unicodedata.normalize("NFD", c)[0]
    return base if base in GLIFOS else "?"


def ancho_texto(texto: str, escala: int = 1) -> int:
    return len(texto) * 6 * escala - escala


def texto_pixel(dibujo: ImageDraw.ImageDraw, x: int, y: int, texto: str, color, escala: int = 1, sombra=None):
    """Escribe texto con la fuente 5×7 (escala = tamaño del píxel de la letra)."""
    if sombra is not None:
        texto_pixel(dibujo, x + escala, y + escala, texto, sombra, escala)
    for caracter in texto:
        filas = GLIFOS[_normalizar(caracter)]
        for fila, bits in enumerate(filas):
            for columna in range(5):
                if bits & (0x10 >> columna):
                    px, py = x + columna * escala, y + fila * escala
                    dibujo.rectangle([px, py, px + escala - 1, py + escala - 1], fill=color)
        x += 6 * escala


def imagen_texto(texto: str, color=E.CIAN, escala: int = 3, sombra=E.MAGENTA, fondo=E.PANEL) -> ImageTk.PhotoImage:
    """Imagen con texto pixelado (para títulos)."""
    ancho, alto = ancho_texto(texto, escala) + escala + 2, 7 * escala + escala + 2
    img = Image.new("RGB", (ancho, alto), fondo)
    texto_pixel(ImageDraw.Draw(img), 1, 1, texto, color, escala, sombra)
    return ImageTk.PhotoImage(img)


def _rgb(color: str):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def mezclar(c1, c2, f: float):
    """Mezcla dos colores (f = 0 -> c1, f = 1 -> c2)."""
    a, b = _rgb(c1) if isinstance(c1, str) else c1, _rgb(c2) if isinstance(c2, str) else c2
    f = max(0.0, min(1.0, f))
    return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


# =============================================================================
#  Perilla pixelada
# =============================================================================
class PerillaPixel(ctk.CTkFrame):
    """Perilla que se gira arrastrando el ratón hacia arriba o abajo.

    - Arrastrar: cambia el valor (con Shift, cambio fino).
    - Rueda del ratón: pasos pequeños.
    - Doble clic o la casilla: escribir el valor exacto.
    escala = 'lin' o 'log' (en 'log', el extremo izquierdo es 0).
    """

    BASE, AUMENTO = 34, 3

    def __init__(self, master, titulo, vmin, vmax, valor, escala="lin", unidades="", color=E.CIAN,
                 al_cambiar=None, formato="{:.4g}"):
        super().__init__(master, fg_color=E.PANEL_2, corner_radius=0, border_width=2, border_color=E.BORDE)
        self.vmin, self.vmax, self.escala, self.color = vmin, vmax, escala, color
        self.unidades, self.al_cambiar, self.formato = unidades, al_cambiar, formato
        self.valor = valor
        ctk.CTkLabel(self, text=titulo, font=E.fuente(titulo=True, tamano=None), text_color=color).pack(pady=(6, 0))
        lado = self.BASE * self.AUMENTO
        self.lienzo = tk.Canvas(self, width=lado, height=lado, bg=E.PANEL_2, highlightthickness=0, cursor="sb_v_double_arrow")
        self.lienzo.pack(padx=8)
        self.casilla = ctk.CTkEntry(self, width=110, justify="center", font=E.fuente(), corner_radius=0,
                                    fg_color=E.FONDO, border_color=E.BORDE, text_color=E.TEXTO)
        self.casilla.pack(pady=(2, 8))
        self.casilla.bind("<Return>", self._desde_casilla)
        self.casilla.bind("<FocusOut>", self._desde_casilla)
        self.lienzo.bind("<ButtonPress-1>", self._presionar)
        self.lienzo.bind("<B1-Motion>", self._arrastrar)
        self.lienzo.bind("<ButtonRelease-1>", lambda e: self._avisar())
        self.lienzo.bind("<MouseWheel>", self._rueda)
        self.lienzo.bind("<Double-Button-1>", lambda e: (self.casilla.focus_set(), self.casilla.select_range(0, "end")))
        self._imagen = None
        self._dibujar()

    # --- Conversión valor <-> posición (0 a 1) ---
    def _a_posicion(self, v):
        if self.escala == "log":
            if v <= 0:
                return 0.0
            v = max(self.vmin, min(self.vmax, v))
            return 0.04 + 0.96 * math.log(v / self.vmin) / math.log(self.vmax / self.vmin)
        return (max(self.vmin, min(self.vmax, v)) - self.vmin) / (self.vmax - self.vmin)

    def _a_valor(self, p):
        p = max(0.0, min(1.0, p))
        if self.escala == "log":
            if p < 0.04:
                return 0.0
            return self.vmin * (self.vmax / self.vmin) ** ((p - 0.04) / 0.96)
        return self.vmin + p * (self.vmax - self.vmin)

    # --- Eventos ---
    def _presionar(self, e):
        self._y0, self._p0 = e.y, self._a_posicion(self.valor)

    def _arrastrar(self, e):
        fino = 600 if (e.state & 0x0001) else 160
        self.fijar(self._a_valor(self._p0 + (self._y0 - e.y) / fino), avisar=False)

    def _rueda(self, e):
        self.fijar(self._a_valor(self._a_posicion(self.valor) + (0.01 if e.delta > 0 else -0.01)))

    def _desde_casilla(self, _=None):
        try:
            texto = self.casilla.get().replace(self.unidades, "").strip().replace(",", ".")
            self.fijar(float(texto))
        except ValueError:
            self._dibujar()

    def _avisar(self):
        if self.al_cambiar:
            self.al_cambiar(self.valor)

    def fijar(self, valor, avisar=True):
        valor = float(valor)
        if self.escala == "log" and valor <= 0:
            self.valor = 0.0
        else:
            self.valor = max(self.vmin, min(self.vmax, valor))
        self._dibujar()
        if avisar:
            self._avisar()

    def obtener(self):
        return self.valor

    # --- Dibujo ---
    def _dibujar(self):
        b = self.BASE
        img = Image.new("RGB", (b, b), E.PANEL_2)
        d = ImageDraw.Draw(img)
        c = b // 2
        p = self._a_posicion(self.valor)
        segmentos = 22
        for k in range(segmentos):                       # Anillo de LEDs de 270°
            f = k / (segmentos - 1)
            ang = math.radians(225 - 270 * f)
            x, y = round(c + 14 * math.cos(ang)), round(c - 14 * math.sin(ang))
            encendido = f <= p + 1e-9 and p > 0
            col = mezclar(self.color, "#ffffff", 0.25 * f) if encendido else mezclar(E.BORDE, E.PANEL_2, 0.3)
            d.rectangle([x - 1, y - 1, x, y], fill=col)
        d.ellipse([c - 10, c - 10, c + 9, c + 9], fill=mezclar(E.BORDE, "#000000", 0.4))   # Sombra
        d.ellipse([c - 10, c - 11, c + 9, c + 8], fill="#4a4470")                         # Cuerpo
        d.ellipse([c - 8, c - 9, c + 6, c + 5], fill="#5d5690")
        d.rectangle([c - 6, c - 8, c - 3, c - 7], fill="#8f88c8")                         # Brillo
        ang = math.radians(225 - 270 * p)
        for r in range(2, 9):                                                             # Indicador
            x, y = round(c - 0.5 + r * math.cos(ang)), round(c - 1.5 - r * math.sin(ang))
            d.point((x, y), fill=self.color)
        grande = img.resize((b * self.AUMENTO, b * self.AUMENTO), Image.NEAREST)
        self._imagen = ImageTk.PhotoImage(grande)
        self.lienzo.delete("all")
        self.lienzo.create_image(0, 0, image=self._imagen, anchor="nw")
        self.casilla.delete(0, "end")
        self.casilla.insert(0, self.formato.format(self.valor) + (f" {self.unidades}" if self.unidades else ""))


# =============================================================================
#  Animación del motor
# =============================================================================
class MotorPixel:
    """Escena pixelada del sistema: L298N, ACS712, motor, encoder, caja y disco.

    actualizar(...) recibe el estado y dibuja un cuadro. El disco del eje de
    salida gira con θ; el disco magnético del encoder gira con θ·N (eje del
    motor) y los sensores A y B se encienden según la cuenta. Los puntos que
    corren por los cables representan la corriente.
    """

    ANCHO, ALTO = 220, 124

    def __init__(self, master, aumento=3, fondo=E.FONDO):
        self.aumento = aumento
        self.lienzo = tk.Canvas(master, width=self.ANCHO * aumento, height=self.ALTO * aumento,
                                bg=fondo, highlightthickness=0)
        self._imagen = None
        self._fase_corriente = 0.0
        self._t_ultimo = time.time()
        self._historial = []
        self._estrellas = [((i * 37) % self.ANCHO, (i * 53) % 46, i % 3) for i in range(28)]
        # Máscara de líneas de barrido (estilo CRT), calculada una sola vez.
        tamano = (self.ANCHO * aumento, self.ALTO * aumento)
        self._negro = Image.new("RGB", tamano, (0, 0, 0))
        self._mascara = Image.new("L", tamano, 0)
        dm = ImageDraw.Draw(self._mascara)
        for y in range(0, tamano[1], aumento):
            dm.line([(0, y), (tamano[0], y)], fill=70)

    def widget(self):
        return self.lienzo

    def actualizar(self, theta=0.0, omega=0.0, corriente=0.0, voltaje=0.0, v_bus=12.0, reduccion=1.0,
                   cuenta=0, modo="REPOSO", t=0.0, theta_gemelo=None, referencia=None, unidad_ref=""):
        ahora = time.time()
        dt = min(0.2, ahora - self._t_ultimo)
        self._t_ultimo = ahora
        W, H = self.ANCHO, self.ALTO
        img = Image.new("RGB", (W, H), E.FONDO)
        d = ImageDraw.Draw(img)

        # Fondo: estrellas que titilan y cuadrícula de puntos.
        for x, y, k in self._estrellas:
            brillo = 0.35 + 0.35 * math.sin(ahora * (1.5 + k) + x)
            d.point((x, y + 2), fill=mezclar(E.FONDO, E.TENUE, brillo))
        for x in range(0, W, 8):
            for y in range(56, H - 22, 8):
                d.point((x, y), fill=mezclar(E.FONDO, E.BORDE, 0.5))
        d.rectangle([0, H - 21, W, H - 21], fill=E.BORDE)                       # Piso

        # Título y modo.
        texto_pixel(d, 4, 3, "JGA25-370", E.CIAN, sombra=mezclar(E.MAGENTA, E.FONDO, 0.3))
        etiqueta = modo[:14]
        ancho = ancho_texto(etiqueta) + 6
        d.rectangle([W - ancho - 4, 2, W - 4, 12], outline=E.AMARILLO)
        texto_pixel(d, W - ancho - 1, 4, etiqueta, E.AMARILLO)

        # --- Driver L298N ---
        x0, y0 = 6, 56
        d.rectangle([x0, y0, x0 + 40, y0 + 34], fill="#1d5e38", outline="#2f8a55")          # Placa
        d.rectangle([x0 + 10, y0 - 14, x0 + 30, y0 + 4], fill="#202020")                    # Disipador
        for k in range(6):
            d.rectangle([x0 + 11 + 3 * k, y0 - 14, x0 + 12 + 3 * k, y0 + 2], fill="#3a3a3a")
        d.rectangle([x0 + 12, y0 + 6, x0 + 28, y0 + 16], fill="#111111")                    # Chip
        texto_pixel(d, x0 + 3, y0 + 25, "L298N", "#bff5d0")
        for k in range(3):                                                                  # Borneras
            d.rectangle([x0 + 34, y0 + 4 + 8 * k, x0 + 39, y0 + 9 + 8 * k], fill=E.AZUL)
        ciclo = min(1.0, abs(voltaje) / max(v_bus, 1e-6))
        d.rectangle([x0 + 3, y0 + 4, x0 + 5, y0 + 6], fill=E.ROJO)                          # LED de encendido
        d.rectangle([x0 + 3, y0 + 10, x0 + 5, y0 + 12],
                    fill=mezclar("#14301f", E.VERDE, ciclo))                                 # LED del PWM

        # --- Cables con la corriente ---
        ruta = [(x0 + 40, y0 + 8), (62, y0 + 8), (62, 64), (96, 64)]                        # Cable rojo
        ruta2 = [(x0 + 40, y0 + 16), (66, y0 + 16), (66, 78), (96, 78)]                     # Cable negro
        for r, col in ((ruta, "#c8283c"), (ruta2, "#5a5a6e")):
            for a, b2 in zip(r[:-1], r[1:]):
                d.line([a, b2], fill=col, width=2)
        d.rectangle([70, 58, 86, 70], fill="#b3202f", outline="#ff5266")                     # ACS712
        texto_pixel(d, 70, 50, "ACS", E.ROJO)
        self._fase_corriente = (self._fase_corriente + dt * corriente * 40.0) % 8.0
        if abs(corriente) > 0.02:
            for r in (ruta, ruta2[::-1]):
                largo = sum(abs(b2[0] - a[0]) + abs(b2[1] - a[1]) for a, b2 in zip(r[:-1], r[1:]))
                s = self._fase_corriente
                while s < largo:
                    x, y = _punto_en_ruta(r, s)
                    d.rectangle([x - 1, y - 1, x, y], fill=E.AMARILLO if corriente > 0 else E.CIAN)
                    s += 8

        # --- Motor ---
        mx0, mx1, my0, my1 = 96, 146, 58, 86
        for y in range(my0, my1 + 1):                                                       # Cilindro metálico
            f = abs((y - my0) / (my1 - my0) - 0.3)
            d.line([(mx0, y), (mx1, y)], fill=mezclar("#e6e6f0", "#4d4d66", f * 1.3))
        d.rectangle([mx0 - 4, my0 + 3, mx0, my1 - 3], fill="#2b2b3d")                       # Tapa trasera
        for k in range(3):
            d.line([(mx0 + 12 + 12 * k, my0 + 2), (mx0 + 12 + 12 * k, my1 - 2)], fill=mezclar("#e6e6f0", "#4d4d66", 0.8))
        texto_pixel(d, mx0 + 8, my0 + 11, "12V DC", "#26263a")

        # --- Encoder (vista de frente, arriba del motor) ---
        ex, ey, er = 112, 32, 12
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill="#161626", outline=E.BORDE)
        theta_motor = theta * reduccion
        polos = 11
        for k in range(2 * polos):
            a = theta_motor + k * math.pi / polos
            x, y = round(ex + (er - 3) * math.cos(a)), round(ey - (er - 3) * math.sin(a))
            d.rectangle([x - 1, y - 1, x, y], fill=E.MAGENTA if k % 2 == 0 else E.AZUL)
        estado = (0, 2, 3, 1)[cuenta % 4]
        for nombre, bit, sx in (("A", 2, ex + er + 4), ("B", 1, ex + er + 13)):
            activo = bool(estado & bit)
            d.rectangle([sx, ey - 3, sx + 6, ey + 3], fill=E.VERDE if activo else "#173326", outline=E.BORDE)
            texto_pixel(d, sx + 1, ey + 6, nombre, E.VERDE if activo else E.TENUE)
        d.line([(ex, ey + er), (ex, my0)], fill=E.BORDE)

        # --- Caja reductora y eje ---
        d.rectangle([mx1 + 1, my0 + 2, mx1 + 14, my1 - 2], fill="#c99a2e", outline="#ffd36b")
        for k in range(3):
            d.line([(mx1 + 4 + 4 * k, my0 + 4), (mx1 + 4 + 4 * k, my1 - 4)], fill="#8a6514")
        d.rectangle([mx1 + 15, 70, mx1 + 22, 73], fill="#d0d0e0")

        # --- Disco del eje de salida (de frente) ---
        cx, cy, r = 190, 72, 22
        rapido = abs(omega) > 40
        d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill="#0a0a18")
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#2a2550", outline=E.CIAN)
        if rapido:                                                                       # Desenfoque de movimiento
            for k in range(1, 4):
                for s in range(4):
                    a = theta - k * 0.12 * math.copysign(1, omega) + s * math.pi / 2
                    d.line([(cx, cy), (cx + (r - 2) * math.cos(a), cy - (r - 2) * math.sin(a))],
                           fill=mezclar("#2a2550", E.CIAN, 0.5 - 0.12 * k))
        for s in range(4):                                                                # Rayos
            a = theta + s * math.pi / 2
            d.line([(cx, cy), (round(cx + (r - 2) * math.cos(a)), round(cy - (r - 2) * math.sin(a)))], fill=E.CIAN)
        mx, my = round(cx + (r - 5) * math.cos(theta)), round(cy - (r - 5) * math.sin(theta))
        d.rectangle([mx - 2, my - 2, mx + 2, my + 2], fill=E.AMARILLO)                    # Marca medida
        if theta_gemelo is not None:                                                     # Marca del gemelo
            gx, gy = round(cx + (r - 11) * math.cos(theta_gemelo)), round(cy - (r - 11) * math.sin(theta_gemelo))
            d.rectangle([gx - 2, gy - 2, gx + 2, gy + 2], outline=E.MAGENTA)
        d.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill="#d0d0e0")
        if referencia is not None and unidad_ref == "rad":                               # Referencia de posición
            ax, ay = round(cx + (r + 4) * math.cos(referencia)), round(cy - (r + 4) * math.sin(referencia))
            d.rectangle([ax - 1, ay - 1, ax + 1, ay + 1], fill=E.VERDE)

        # --- Panel de lecturas ---
        yb = H - 18
        texto_pixel(d, 4, yb, f"V{voltaje:+6.2f}", E.VERDE)
        texto_pixel(d, 56, yb, f"I{corriente:+6.3f}", E.AMARILLO)
        texto_pixel(d, 114, yb, f"Ω{omega:+8.1f}", E.CIAN)
        texto_pixel(d, 4, yb + 9, f"Θ{theta:+9.2f} RAD", E.MAGENTA)
        texto_pixel(d, 114, yb + 9, f"T{t:8.2f} S", E.TENUE)
        _barra(d, 4, H - 24, 48, ciclo, E.VERDE)
        _barra(d, 56, H - 24, 48, min(1.0, abs(corriente) / 2.0), E.AMARILLO)

        # Líneas de barrido estilo pantalla CRT y ampliación sin suavizado.
        grande = img.resize((W * self.aumento, H * self.aumento), Image.NEAREST)
        grande.paste(self._negro, (0, 0), self._mascara)
        self._imagen = ImageTk.PhotoImage(grande)
        self.lienzo.delete("all")
        self.lienzo.create_image(0, 0, image=self._imagen, anchor="nw")


def _barra(d, x, y, ancho, f, color):
    d.rectangle([x, y, x + ancho, y + 3], outline=E.BORDE)
    lleno = int((ancho - 2) * max(0.0, min(1.0, f)))
    if lleno > 0:
        d.rectangle([x + 1, y + 1, x + lleno, y + 2], fill=color)


def _punto_en_ruta(ruta, s):
    """Punto a distancia s (en píxeles) a lo largo de una ruta de segmentos rectos."""
    for (x0, y0), (x1, y1) in zip(ruta[:-1], ruta[1:]):
        largo = abs(x1 - x0) + abs(y1 - y0)
        if s <= largo:
            f = s / largo if largo else 0
            return round(x0 + (x1 - x0) * f), round(y0 + (y1 - y0) * f)
        s -= largo
    return ruta[-1]
