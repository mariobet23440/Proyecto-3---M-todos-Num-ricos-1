"""
Gráficas animadas con matplotlib dentro de customtkinter.

  * GraficaBarrido: tiempo real, estilo osciloscopio. Un cursor recorre la
    ventana de izquierda a derecha y va reemplazando el barrido anterior.
  * GraficaReproduccion: datos guardados. Las curvas completas quedan fijas y
    un cursor recorre el tiempo (al reproducir o al hacer clic en la gráfica).

Para que la animación sea fluida se usa "blitting": el fondo (ejes, cuadrícula
y curvas fijas) se dibuja una vez y en cada cuadro solo se redibujan las
líneas que cambian y el cursor.

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md).
"""
from __future__ import annotations

import math
import time

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import estilo as E


class _Base:
    def __init__(self, master, n_ejes, etiquetas_y, alto=4.0):
        self.fig = Figure(figsize=(8, alto), dpi=100)
        self.ejes = list(np.atleast_1d(self.fig.subplots(n_ejes, 1, sharex=True)))
        for eje, etiqueta in zip(self.ejes, etiquetas_y):
            eje.set_ylabel(etiqueta)
            eje.grid(True)
            eje.tick_params(length=3, width=1.5)
        self.ejes[-1].set_xlabel("t [s]")
        self.fig.subplots_adjust(left=0.09, right=0.985, top=0.94, bottom=0.11, hspace=0.12)
        self.lienzo = FigureCanvasTkAgg(self.fig, master=master)
        self.lienzo.get_tk_widget().configure(bg=E.PANEL, highlightthickness=0)
        self._fondo = None
        self._animados = []
        self.lienzo.mpl_connect("draw_event", self._al_dibujar)

    def widget(self):
        return self.lienzo.get_tk_widget()

    def _animado(self, artista):
        artista.set_animated(True)
        self._animados.append(artista)
        return artista

    def _al_dibujar(self, _evento):
        self._fondo = self.lienzo.copy_from_bbox(self.fig.bbox)
        self._pintar_animados()

    def _pintar_animados(self):
        for a in self._animados:
            self.fig.draw_artist(a)

    def _blit(self):
        if self._fondo is None:
            self.lienzo.draw()
            return
        self.lienzo.restore_region(self._fondo)
        self._pintar_animados()
        self.lienzo.blit(self.fig.bbox)


class GraficaBarrido(_Base):
    """series_por_eje: [[(clave, nombre, color, estilo), ...], ...] (estilo '-' o '--')."""

    def __init__(self, master, series_por_eje, etiquetas_y, ventana=5.0, alto=4.0):
        super().__init__(master, len(series_por_eje), etiquetas_y, alto)
        self.ventana = ventana
        self.lineas, self.puntos, self.eje_de = {}, {}, {}
        for eje, series in zip(self.ejes, series_por_eje):
            for clave, nombre, color, estilo in series:
                self.lineas[clave] = self._animado(eje.plot([], [], estilo, color=color, lw=1.6, label=nombre)[0])
                self.puntos[clave] = self._animado(eje.plot([], [], "s", color=color, ms=5)[0])
                self.eje_de[clave] = eje
            if len(series) > 1:
                eje.legend(loc="upper left", ncol=len(series), handlelength=1.2)
            eje.set_ylim(-1, 1)
        self.cursores = [self._animado(eje.axvline(0, color=E.AMARILLO, lw=1.5)) for eje in self.ejes]
        self.reloj = self._animado(self.fig.text(0.985, 0.955, "", ha="right", color=E.AMARILLO))
        self.ejes[0].set_xlim(0, ventana)
        self._limites = {id(e): (-1.0, 1.0) for e in self.ejes}
        self._ultimo_reescalado = 0.0

    def fijar_ventana(self, ventana):
        self.ventana = ventana
        self.ejes[0].set_xlim(0, ventana)
        self.lienzo.draw_idle()

    def visibilidad(self, clave, visible):
        self.lineas[clave].set_visible(visible)
        self.puntos[clave].set_visible(visible)

    def refrescar(self, t, series: dict):
        """t: tiempos (crecientes) de los últimos ~2 barridos; series: clave -> valores."""
        if t is None or len(t) == 0:
            return
        W = self.ventana
        t_ult = t[-1]
        t0 = math.floor(t_ult / W) * W
        cursor = t_ult - t0
        actual = t >= t0
        previo = (t >= t0 - W) & (t < t0) & (t - (t0 - W) > cursor + 0.04 * W)
        x = np.concatenate([t[previo] - (t0 - W), [np.nan], t[actual] - t0])
        paso = max(1, len(x) // 900)                                    # Puntos en pantalla (dibujar cuesta)
        rangos = {}
        for clave, linea in self.lineas.items():
            y_todo = series.get(clave)
            if y_todo is None or not linea.get_visible():
                linea.set_data([], [])
                self.puntos[clave].set_data([], [])
                continue
            y = np.concatenate([y_todo[previo], [np.nan], y_todo[actual]])
            linea.set_data(x[::paso], y[::paso])
            self.puntos[clave].set_data([cursor], [y_todo[-1]])
            finitos = y[np.isfinite(y)]
            if len(finitos):
                eje = id(self.eje_de[clave])
                lo, hi = rangos.get(eje, (np.inf, -np.inf))
                rangos[eje] = (min(lo, finitos.min()), max(hi, finitos.max()))
        for c in self.cursores:
            c.set_xdata([cursor, cursor])
        self.reloj.set_text(f"t = {t_ult:8.2f} s")
        if self._reescalar(rangos):
            self.lienzo.draw()          # Redibuja el fondo (llama a _al_dibujar)
        else:
            self._blit()

    def _reescalar(self, rangos):
        """Ajusta los límites en y. Redibujar el fondo es caro: se hace como
        máximo una vez por segundo y con margen amplio (25 %)."""
        ahora = time.time()
        if ahora - self._ultimo_reescalado < 1.0:
            return False
        cambio = False
        for eje in self.ejes:
            if id(eje) not in rangos:
                continue
            lo, hi = rangos[id(eje)]
            margen = max(0.25 * (hi - lo), 1e-3 + 0.05 * max(abs(lo), abs(hi)))
            deseado = (lo - margen, hi + margen)
            actual = self._limites[id(eje)]
            fuera = lo < actual[0] or hi > actual[1]
            muy_holgado = (actual[1] - actual[0]) > 4.0 * (deseado[1] - deseado[0])
            if fuera or muy_holgado:
                self._ultimo_reescalado = ahora
                self._limites[id(eje)] = deseado
                eje.set_ylim(*deseado)
                cambio = True
        return cambio


class GraficaReproduccion(_Base):
    """Curvas fijas y un cursor que recorre el tiempo."""

    def __init__(self, master, etiquetas_y, alto=4.0, al_hacer_clic=None):
        super().__init__(master, len(etiquetas_y), etiquetas_y, alto)
        self.al_hacer_clic = al_hacer_clic
        self.t = None
        self.marcas = []
        self.cursores = [self._animado(eje.axvline(0, color=E.AMARILLO, lw=1.6)) for eje in self.ejes]
        self.reloj = self._animado(self.fig.text(0.985, 0.955, "", ha="right", color=E.AMARILLO))
        self.lienzo.mpl_connect("button_press_event", self._clic)

    def cargar(self, t, series_por_eje, lineas_verticales=()):
        """series_por_eje: [[(nombre, y, color, estilo), ...], ...]"""
        self.t = np.asarray(t)
        for marca, _ in self.marcas:                 # Quita las marcas de la carga anterior
            marca.remove()
            self._animados.remove(marca)
        self.marcas = []
        paso = max(1, len(self.t) // 6000)
        for eje, series in zip(self.ejes, series_por_eje):
            for linea in list(eje.lines):
                if linea not in self._animados:
                    linea.remove()
            if eje.get_legend():
                eje.get_legend().remove()
            for nombre, y, color, estilo in series:
                eje.plot(self.t[::paso], np.asarray(y)[::paso], estilo, color=color, lw=1.4, label=nombre)
            for tv in lineas_verticales:
                eje.axvline(tv, color=E.TENUE, lw=1, ls=":")
            if series:
                y0 = np.asarray(series[0][1])
                self.marcas.append((self._animado(eje.plot([], [], "s", color=series[0][2], ms=6)[0]), y0))
                eje.legend(loc="upper left", ncol=len(series), handlelength=1.2)
                todos = np.concatenate([np.asarray(s[1])[np.isfinite(s[1])] for s in series])
                if len(todos):
                    lo, hi = np.percentile(todos, 0.2), np.percentile(todos, 99.8)
                    m = max(0.1 * (hi - lo), 1e-3)
                    eje.set_ylim(lo - m, hi + m)
        self.ejes[0].set_xlim(self.t[0], self.t[-1])
        self.lienzo.draw()

    def cursor(self, tc):
        if self.t is None:
            return
        for c in self.cursores:
            c.set_xdata([tc, tc])
        for marca, y in self.marcas:
            marca.set_data([tc], [np.interp(tc, self.t, y)])
        self.reloj.set_text(f"t = {tc:8.4f} s")
        self._blit()

    def _clic(self, evento):
        if evento.inaxes is not None and evento.xdata is not None and self.al_hacer_clic:
            self.al_hacer_clic(float(evento.xdata))
