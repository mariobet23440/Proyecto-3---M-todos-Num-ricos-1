"""
GEMELO DIGITAL DEL MOTOR DC JGA25-370 · aplicación de escritorio.

Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
Fecha de creación: 22/11/2026
Autores: Mario Alejandro Betancourt Franco (23440)
         Claude Opus 5.5 (Anthropic), asistente de IA

Páginas (menú de la izquierda):
  CONEXIÓN  puerto serie o Arduino simulado, datos del hardware y consola.
  TABLERO   gemelo digital en tiempo real: animación del motor y gráficas
            con cursor (medición y modelo, lado a lado).
  PID       modo de control (lazo abierto, velocidad, posición), perillas
            para Kp, Ki, Kd, Ts y el filtro, y generador de referencia.
  ENSAYOS   respuesta al escalón, a la desconexión y seguimiento de un
            movimiento; reproducción animada de los resultados.
  CAPTURA   grabación de la telemetría y archivos guardados.
  MODELO    parámetros del modelo, método de integración y simulación.

Uso:
    pip install customtkinter pyserial numpy matplotlib pillow
    python app.py

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md). Se probó con el
Arduino simulado; NO se ha probado con el hardware real.
"""
from __future__ import annotations

import json
import math
import os
import queue
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA))
sys.path.insert(0, str(CARPETA.parent))        # protocolo_motor, modelo_motor, postprocesamiento

import numpy as np
import customtkinter as ctk

import estilo as E

FAMILIAS = E.cargar_fuentes()
E.estilo_matplotlib(FAMILIAS)

import protocolo_motor as P                    # noqa: E402
import postprocesamiento as PP                 # noqa: E402
from modelo_motor import GemeloDigital, ParametrosMotor, simular   # noqa: E402
from graficas import GraficaBarrido, GraficaReproduccion           # noqa: E402
from pixel import MotorPixel, PerillaPixel, imagen_texto, mezclar  # noqa: E402

ARCHIVO_CONFIG = CARPETA / "config_app.json"
CONFIG_INICIAL = {
    "puerto": "", "baudios": P.BAUDIOS,
    "ppr": 11.0, "reduccion": 1.0, "vref": 5.0, "sensibilidad": 0.185, "cero_adc": 512.0,
    "invertir_encoder": False, "invertir_corriente": False,
    "kp": 0.05, "ki": 0.0, "kd": 0.0, "ts_ms": 2.0, "tau_ms": 8.0,
    "antiwindup": True, "envio_automatico": True,
    "modo_pid": 2, "ref_tipo": 0, "ref_amp": 0.0, "ref_off": 100.0, "ref_f": 0.5,
    "cap_pwm": 255, "cap_sentido": 1, "cap_freno": 0, "cap_t0": 200, "cap_t1": 1500, "cap_t2": 1500,
    "seguir_modo": 3, "seguir_tipo": 1, "seguir_amp": 6.28, "seguir_off": 0.0, "seguir_f": 0.5,
    "seguir_duracion": 6.0,
    "motor": ParametrosMotor().a_dict(), "metodo": "RK4", "h_modelo": 2.5e-4,
    "carpeta_datos": str(CARPETA.parent / "datos"), "ventana_s": 5.0,
}


def hexa(rgb):
    return "#%02x%02x%02x" % tuple(rgb)


# =============================================================================
#  Pequeños constructores de widgets con el estilo de la aplicación
# =============================================================================
def boton(master, texto, comando, color=E.CIAN, ancho=150, alto=36):
    return ctk.CTkButton(master, text=texto, command=comando, corner_radius=0, border_width=2,
                         border_color=color, fg_color=E.PANEL_2, hover_color=hexa(mezclar(E.PANEL_2, color, 0.3)),
                         text_color=color, font=E.fuente(titulo=True), width=ancho, height=alto)


def etiqueta(master, texto, color=E.TEXTO, titulo=False, tamano=None, **kw):
    return ctk.CTkLabel(master, text=texto, text_color=color, font=E.fuente(tamano, titulo=titulo), **kw)


def casilla(master, valor, ancho=100):
    c = ctk.CTkEntry(master, width=ancho, corner_radius=0, fg_color=E.FONDO, border_color=E.BORDE,
                     text_color=E.TEXTO, font=E.fuente())
    c.insert(0, str(valor))
    return c


def marco(master, **kw):
    return ctk.CTkFrame(master, fg_color=E.PANEL, corner_radius=0, border_width=2, border_color=E.BORDE, **kw)


def interruptor(master, texto, valor, comando=None, color=E.CIAN):
    var = tk.BooleanVar(value=bool(valor))
    s = ctk.CTkSwitch(master, text=texto, variable=var, command=comando, font=E.fuente(), text_color=E.TEXTO,
                      progress_color=color, button_color=E.TEXTO, fg_color=E.BORDE, corner_radius=0)
    return s, var


def segmentado(master, valores, comando=None, color=E.CIAN):
    return ctk.CTkSegmentedButton(master, values=valores, command=comando, corner_radius=0, font=E.fuente(),
                                  selected_color=hexa(mezclar(E.PANEL_2, color, 0.55)),
                                  selected_hover_color=hexa(mezclar(E.PANEL_2, color, 0.7)),
                                  unselected_color=E.PANEL_2, unselected_hover_color=E.BORDE,
                                  fg_color=E.BORDE, text_color=E.TEXTO)


def titulo_pixel(master, texto, color=E.CIAN, escala=3, fondo=E.PANEL):
    img = imagen_texto(texto, color=color, escala=escala, sombra=hexa(mezclar(E.MAGENTA, fondo, 0.35)), fondo=fondo)
    lbl = tk.Label(master, image=img, bg=fondo, bd=0)
    lbl.imagen = img
    return lbl


def leer_float(c, defecto):
    try:
        return float(c.get().replace(",", "."))
    except (ValueError, AttributeError):
        return defecto


# =============================================================================
#  Almacén de la telemetría (arreglo circular)
# =============================================================================
class Anillo:
    CAMPOS = ("t", "theta", "omega", "ref", "u", "i", "adc", "modo", "estado", "cuenta",
              "g_theta", "g_omega", "g_i")

    def __init__(self, capacidad=400_000):
        self.cap = capacidad
        self.d = {c: np.full(capacidad, np.nan) for c in self.CAMPOS}
        self.n = 0

    def agregar(self, **valores):
        j = self.n % self.cap
        for c, v in valores.items():
            self.d[c][j] = v
        self.n += 1

    def ultimos(self, m):
        m = min(m, self.n, self.cap)
        idx = np.arange(self.n - m, self.n) % self.cap
        return {c: a[idx] for c, a in self.d.items()}

    def limpiar(self):
        self.n = 0


# =============================================================================
#  Aplicación
# =============================================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Gemelo digital · Motor DC JGA25-370 · Métodos Numéricos UVG")
        self.geometry("1400x860")
        self.minsize(1000, 640)
        if sys.platform.startswith("win"):
            self.after(50, lambda: self.state("zoomed"))     # Maximizada: se adapta a la pantalla
        self.configure(fg_color=E.FONDO)

        self.cfg = dict(CONFIG_INICIAL)
        if ARCHIVO_CONFIG.exists():
            try:
                self.cfg.update(json.loads(ARCHIVO_CONFIG.read_text(encoding="utf-8")))
            except Exception:
                pass
        self.enlace: P.EnlaceSerie | None = None
        self.simulado = False
        self.datos = Anillo()
        self.cfg_arduino = {}
        self.ultimo = {"t": 0.0, "theta": 0.0, "omega": 0.0, "i": 0.0, "u": 0.0, "ref": 0.0, "modo": 0,
                       "cuenta": 0, "estado": 0, "g_theta": None}
        self._t = 0.0
        self._k_prev = None
        self._u_prev, self._abierto_prev = 0.0, True
        self.gemelo_activo = True
        self.gemelo = GemeloDigital(self.parametros_motor(), self.cfg["metodo"], self.cfg["h_modelo"])
        self.grabando = None              # Lista de filas mientras se graba
        self._fin_grabacion = None        # (tiempo, función) para grabaciones con duración
        self._tareas = queue.Queue()      # Resultados de hilos de cálculo
        self._tramas_seg, self._bytes_ant, self._t_estado = 0, 0, time.time()

        self._construir()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self.after(25, self._bucle_eventos)
        self.after(40, self._bucle_animacion)
        self.after(500, self._bucle_lento)

    # --- Configuración derivada ---
    def cuentas_por_vuelta(self):
        return 4.0 * self.cfg["ppr"] * self.cfg["reduccion"]

    def parametros_motor(self):
        datos = dict(self.cfg["motor"])
        datos["N"] = self.cfg["reduccion"]
        return ParametrosMotor(**datos)

    def guardar_cfg(self):
        try:
            ARCHIVO_CONFIG.write_text(json.dumps(self.cfg, indent=2), encoding="utf-8")
        except Exception as e:
            self.log(f"! No se pudo guardar la configuración: {e}")

    def corriente_de_adc(self, adc):
        signo = -1.0 if self.cfg["invertir_corriente"] else 1.0
        return signo * (adc - self.cfg["cero_adc"]) * self.cfg["vref"] / 1024.0 / self.cfg["sensibilidad"]

    # --- Interfaz ---
    def _construir(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        lateral = ctk.CTkFrame(self, fg_color=E.PANEL, corner_radius=0, width=240, border_width=2,
                               border_color=E.BORDE)
        lateral.grid(row=0, column=0, sticky="ns")
        lateral.grid_propagate(False)
        titulo_pixel(lateral, "MOTOR DC", E.CIAN, 4).pack(pady=(18, 2))
        titulo_pixel(lateral, "GEMELO DIGITAL", E.MAGENTA, 2).pack(pady=(0, 16))

        self.contenedor = ctk.CTkFrame(self, fg_color=E.FONDO, corner_radius=0)
        self.contenedor.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.paginas = {
            "conexion": PaginaConexion(self.contenedor, self),
            "tablero": PaginaTablero(self.contenedor, self),
            "pid": PaginaPID(self.contenedor, self),
            "ensayos": PaginaEnsayos(self.contenedor, self),
            "captura": PaginaCaptura(self.contenedor, self),
            "modelo": PaginaModelo(self.contenedor, self),
        }
        self.botones_menu = {}
        for clave, texto, color in (("conexion", "CONEXION", E.CIAN), ("tablero", "TABLERO", E.VERDE),
                                    ("pid", "CONTROL PID", E.AMARILLO), ("ensayos", "ENSAYOS", E.NARANJA),
                                    ("captura", "CAPTURA", E.MAGENTA), ("modelo", "MODELO", E.MORADO)):
            b = boton(lateral, "> " + texto, lambda c=clave: self.mostrar(c), color, ancho=210, alto=42)
            b.pack(pady=4, padx=14)
            self.botones_menu[clave] = (b, color)

        boton(lateral, "STOP", self.paro, E.ROJO, ancho=210, alto=56).pack(pady=(22, 8), padx=14)
        self.lbl_estado = etiqueta(lateral, "DESCONECTADO", E.ROJO, justify="left", anchor="w")
        self.lbl_estado.pack(fill="x", padx=16, pady=(12, 2))
        self.lbl_info = etiqueta(lateral, "", E.TENUE, justify="left", anchor="w")
        self.lbl_info.pack(fill="x", padx=16)
        etiqueta(lateral, "UVG · METODOS NUMERICOS\nPROYECTO 3", E.TENUE, tamano=None).pack(side="bottom", pady=14)

        self.pagina_actual = None
        self.mostrar("conexion")

    def mostrar(self, clave):
        if self.pagina_actual:
            self.paginas[self.pagina_actual].grid_remove()
        self.pagina_actual = clave
        self.paginas[clave].grid(row=0, column=0, sticky="nsew")
        self.paginas[clave].al_mostrar()
        for c, (b, color) in self.botones_menu.items():
            b.configure(fg_color=hexa(mezclar(E.PANEL_2, color, 0.35)) if c == clave else E.PANEL_2)

    def log(self, texto):
        self.paginas["conexion"].consola_agregar(texto)

    # --- Conexión ---
    def conectar(self, puerto, baudios):
        self.desconectar()
        try:
            self.enlace = P.EnlaceSerie.abrir(puerto, baudios)
        except Exception as e:
            messagebox.showerror("Conexión", f"No se pudo abrir {puerto}:\n{e}")
            return
        self.simulado = False
        self.cfg["puerto"], self.cfg["baudios"] = puerto, baudios
        self.guardar_cfg()
        self.log(f"> Puerto {puerto} abierto a {baudios} baudios. Esperando al Arduino (se reinicia)...")
        self.after(2200, self.enviar_configuracion)

    def conectar_simulado(self):
        from arduino_simulado import ArduinoSimulado
        self.desconectar()
        p = self.parametros_motor()
        planta = ParametrosMotor(**{**p.a_dict(), "J": p.J * 1.2, "b": p.b * 1.3})
        self.enlace = P.EnlaceSerie(ArduinoSimulado(planta, ppr=self.cfg["ppr"], cero_adc=511.6))
        self.simulado = True
        self.log("> Arduino SIMULADO. La planta simulada usa J x1.2 y b x1.3 respecto del modelo,")
        self.log("  para que el gemelo y la 'medicion' no coincidan exactamente.")
        self.enviar_configuracion()

    def desconectar(self):
        if self.enlace:
            try:
                self.enlace.enviar(P.orden("X"))
            except Exception:
                pass
            self.enlace.cerrar()
            self.log("> Desconectado.")
        self.enlace = None
        self._k_prev = None

    def enviar(self, letra, *valores):
        if not self.enlace:
            return False
        try:
            self.enlace.enviar(P.orden(letra, *valores))
            return True
        except Exception as e:
            self.log(f"! Error al enviar: {e}")
            return False

    def enviar_configuracion(self):
        c = self.cfg
        self.enviar("X")
        self.enviar("S", 1)
        self.enviar("P", float(self.cuentas_por_vuelta()), float(self.cfg["motor"]["v_bus"]))
        self.enviar("T", float(c["ts_ms"]))
        self.enviar("F", float(c["tau_ms"]))
        self.enviar("K", float(c["kp"]), float(c["ki"]), float(c["kd"]))
        self.enviar("A", int(c["antiwindup"]))
        self.enviar("?")
        self._k_prev = None

    def paro(self):
        self.enviar("X")
        self.log("> STOP: motor en reposo.")

    # --- Bucles ---
    def _bucle_eventos(self):
        if self.enlace:
            for _ in range(5000):
                try:
                    tipo, valor = self.enlace.eventos.get_nowait()
                except queue.Empty:
                    break
                if tipo == "telem":
                    self._telemetria(valor)
                elif tipo == "texto":
                    self._texto(valor)
                elif tipo == "captura":
                    self.paginas["ensayos"].captura_recibida(valor)
                elif tipo == "progreso":
                    self.paginas["ensayos"].progreso(valor)
                elif tipo == "error":
                    self.log("! " + str(valor))
                elif tipo == "desconectado":
                    self.desconectar()
                    break
        while not self._tareas.empty():
            funcion = self._tareas.get_nowait()
            funcion()
        if self._fin_grabacion and self._t >= self._fin_grabacion[0]:
            _, accion = self._fin_grabacion
            self._fin_grabacion = None
            accion()
        self.after(25, self._bucle_eventos)

    def _bucle_animacion(self):
        try:
            self.paginas[self.pagina_actual].refrescar()
        except Exception as e:                      # Un error de dibujo no debe parar la app
            self.log(f"! Error al dibujar: {e}")
        self.after(40, self._bucle_animacion)

    def _bucle_lento(self):
        ahora = time.time()
        if self.enlace:
            self.enviar("H")                        # Latido (ver TIEMPO_SIN_COMUNICACION_MS)
            dt = ahora - self._t_estado
            kbs = (self.enlace.bytes_recibidos - self._bytes_ant) / dt / 1000
            self._bytes_ant = self.enlace.bytes_recibidos
            self.lbl_estado.configure(text="SIMULADO" if self.simulado else f"CONECTADO {self.cfg['puerto']}",
                                      text_color=E.AMARILLO if self.simulado else E.VERDE)
            self.lbl_info.configure(text=f"MODO  {P.MODOS.get(self.ultimo['modo'], '?')}\n"
                                         f"TRAMAS {self._tramas_seg / dt:6.0f}/s\nRX    {kbs:6.1f} kB/s\n"
                                         f"MALAS {self.enlace.parser.tramas_malas}")
        else:
            self.lbl_estado.configure(text="DESCONECTADO", text_color=E.ROJO)
            self.lbl_info.configure(text="")
        self._tramas_seg, self._t_estado = 0, ahora
        self.after(500, self._bucle_lento)

    # --- Datos que llegan ---
    def _texto(self, linea):
        self.log(linea)
        if linea.startswith("# CFG"):
            self.cfg_arduino = P.leer_parametros(linea)

    def _telemetria(self, tel: P.Telemetria):
        self._tramas_seg += 1
        ts = self.cfg["ts_ms"] / 1000
        if self._k_prev is None or tel.k <= self._k_prev:
            dk = 1
        else:
            dk = tel.k - self._k_prev
        self._k_prev = tel.k
        dt = dk * ts
        self._t += dt
        q = 2 * math.pi / self.cuentas_por_vuelta()
        theta = tel.cuenta * q
        i = self.corriente_de_adc(tel.adc)
        if self.gemelo_activo:
            self.gemelo.avanzar(dt, self._u_prev, self._abierto_prev)
        self._u_prev = tel.voltaje
        self._abierto_prev = tel.modo == 0 or abs(tel.voltaje) < 1e-3
        g = self.gemelo
        self.datos.agregar(t=self._t, theta=theta, omega=tel.velocidad, ref=tel.referencia, u=tel.voltaje,
                           i=i, adc=tel.adc, modo=tel.modo, estado=tel.estado, cuenta=tel.cuenta,
                           g_theta=g.theta_salida, g_omega=g.omega_salida, g_i=g.corriente)
        self.ultimo = {"t": self._t, "theta": theta, "omega": tel.velocidad, "i": i, "u": tel.voltaje,
                       "ref": tel.referencia, "modo": tel.modo, "cuenta": tel.cuenta, "estado": tel.estado,
                       "g_theta": g.theta_salida if self.gemelo_activo else None}
        if self.grabando is not None:
            self.grabando.append((self._t, tel.k, tel.cuenta, theta, tel.referencia, tel.velocidad, tel.voltaje,
                                  tel.adc, i, tel.modo, tel.estado, g.theta_salida, g.omega_salida, g.corriente))

    def sincronizar_gemelo(self):
        self.gemelo = GemeloDigital(self.parametros_motor(), self.cfg["metodo"], self.cfg["h_modelo"])
        self.gemelo.reiniciar(self.ultimo["theta"], self.ultimo["omega"])

    def ultimos_segundos(self, segundos):
        paso = max(self.cfg["ts_ms"] / 1000, 1e-4)
        return self.datos.ultimos(int(segundos / paso) + 20)

    # --- Grabación de la telemetría ---
    COLUMNAS_GRABACION = ("t_s", "k", "cuenta", "theta_rad", "referencia", "omega_rad_s", "voltaje_V", "adc",
                          "corriente_A", "modo", "estado", "gemelo_theta_rad", "gemelo_omega_rad_s",
                          "gemelo_corriente_A")

    def iniciar_grabacion(self, duracion=None, al_terminar=None):
        self.grabando = []
        if duracion:
            self._fin_grabacion = (self._t + duracion, al_terminar or self.detener_grabacion)

    def detener_grabacion(self):
        filas, self.grabando = self.grabando or [], None
        self._fin_grabacion = None
        return filas

    def guardar_grabacion(self, filas, nombre=None):
        if not filas:
            return None
        carpeta = Path(self.cfg["carpeta_datos"])
        carpeta.mkdir(parents=True, exist_ok=True)
        base = carpeta / (nombre or f"tiempo_real_{time.strftime('%Y%m%d_%H%M%S')}")
        np.savetxt(str(base) + ".csv", np.array(filas, dtype=float), delimiter=",",
                   header=",".join(self.COLUMNAS_GRABACION), comments="", fmt="%.7g")
        meta = {"tipo": "tiempo_real", "fecha": time.strftime("%Y-%m-%d %H:%M:%S"), "configuracion_app": self.cfg,
                "configuracion_arduino": self.cfg_arduino, "columnas": self.COLUMNAS_GRABACION,
                "simulado": self.simulado}
        base.with_suffix(".json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log(f"> Guardado {base}.csv")
        return base

    def en_hilo(self, trabajo, al_terminar):
        """Ejecuta trabajo() en otro hilo y al_terminar(resultado) en el hilo de la interfaz."""
        def correr():
            try:
                resultado = trabajo()
                self._tareas.put(lambda: al_terminar(resultado))
            except Exception as e:
                self._tareas.put(lambda e=e: self.log(f"! Error de cálculo: {e}"))
        threading.Thread(target=correr, daemon=True).start()

    def _cerrar(self):
        self.guardar_cfg()
        self.desconectar()
        self.destroy()


# =============================================================================
#  Páginas
# =============================================================================
class Pagina(ctk.CTkFrame):
    def __init__(self, master, app: App, titulo, color):
        super().__init__(master, fg_color=E.FONDO, corner_radius=0)
        self.app = app
        cabecera = ctk.CTkFrame(self, fg_color=E.FONDO, corner_radius=0)
        cabecera.pack(fill="x", pady=(0, 6))
        titulo_pixel(cabecera, titulo, color, 3, E.FONDO).pack(side="left", padx=4)
        self.cabecera = cabecera

    def al_mostrar(self):
        pass

    def refrescar(self):
        pass


# -----------------------------------------------------------------------------
class PaginaConexion(Pagina):
    def __init__(self, master, app):
        super().__init__(master, app, "CONEXION", E.CIAN)
        cuerpo = ctk.CTkFrame(self, fg_color=E.FONDO)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)
        izq = ctk.CTkScrollableFrame(cuerpo, fg_color=E.FONDO, width=430, corner_radius=0)
        izq.grid(row=0, column=0, sticky="nsw")

        m = marco(izq)
        m.pack(fill="x", pady=4)
        etiqueta(m, "PUERTO SERIE", E.CIAN, titulo=True).pack(anchor="w", padx=10, pady=(8, 4))
        fila = ctk.CTkFrame(m, fg_color=E.PANEL)
        fila.pack(fill="x", padx=10)
        self.menu_puertos = ctk.CTkOptionMenu(fila, values=["(ninguno)"], width=180, corner_radius=0,
                                              font=E.fuente(), fg_color=E.PANEL_2, button_color=E.BORDE,
                                              dropdown_font=E.fuente())
        self.menu_puertos.pack(side="left", pady=4)
        boton(fila, "BUSCAR", self.buscar_puertos, E.TENUE, ancho=110, alto=30).pack(side="left", padx=6)
        fila = ctk.CTkFrame(m, fg_color=E.PANEL)
        fila.pack(fill="x", padx=10, pady=4)
        etiqueta(fila, "BAUDIOS").pack(side="left")
        self.c_baudios = casilla(fila, app.cfg["baudios"], 120)
        self.c_baudios.pack(side="left", padx=8)
        fila = ctk.CTkFrame(m, fg_color=E.PANEL)
        fila.pack(fill="x", padx=10, pady=(4, 10))
        boton(fila, "CONECTAR", self._conectar, E.VERDE, ancho=125).pack(side="left")
        boton(fila, "SIMULADO", app.conectar_simulado, E.AMARILLO, ancho=125).pack(side="left", padx=6)
        boton(fila, "SALIR", app.desconectar, E.ROJO, ancho=110).pack(side="left")

        m = marco(izq)
        m.pack(fill="x", pady=8)
        etiqueta(m, "HARDWARE", E.CIAN, titulo=True).pack(anchor="w", padx=10, pady=(8, 4))
        self.casillas = {}
        for clave, texto in (("ppr", "PULSOS/VUELTA ENCODER (EJE MOTOR)"), ("reduccion", "REDUCCION N DE LA CAJA"),
                             ("vref", "VREF DEL ADC [V] (MEDIR 5V)"), ("sensibilidad", "SENSIBILIDAD ACS712 [V/A]"),
                             ("cero_adc", "CERO DEL SENSOR [CUENTAS]")):
            fila = ctk.CTkFrame(m, fg_color=E.PANEL)
            fila.pack(fill="x", padx=10, pady=2)
            etiqueta(fila, texto, E.TEXTO).pack(side="left")
            self.casillas[clave] = casilla(fila, app.cfg[clave], 90)
            self.casillas[clave].pack(side="right")
        fila = ctk.CTkFrame(m, fg_color=E.PANEL)
        fila.pack(fill="x", padx=10, pady=2)
        etiqueta(fila, "VOLTAJE DE LA FUENTE [V]").pack(side="left")
        self.c_vbus = casilla(fila, app.cfg["motor"]["v_bus"], 90)
        self.c_vbus.pack(side="right")
        self.sw_inv_i, self.v_inv_i = interruptor(m, "INVERTIR SIGNO DE LA CORRIENTE", app.cfg["invertir_corriente"])
        self.sw_inv_i.pack(anchor="w", padx=10, pady=4)
        self.sw_inv_e, self.v_inv_e = interruptor(m, "INVERTIR ENCODER (SOLO CAPTURA RAPIDA)", app.cfg["invertir_encoder"])
        self.sw_inv_e.pack(anchor="w", padx=10, pady=4)
        etiqueta(m, "Si el encoder cuenta al reves en tiempo real,\nintercambiar los cables A y B (el PID usa ese signo).",
                 E.TENUE, justify="left").pack(anchor="w", padx=10)
        fila = ctk.CTkFrame(m, fg_color=E.PANEL)
        fila.pack(fill="x", padx=10, pady=10)
        boton(fila, "APLICAR", self._aplicar, E.VERDE, ancho=130).pack(side="left")
        boton(fila, "CALIBRAR CERO", self._calibrar_cero, E.AMARILLO, ancho=190).pack(side="left", padx=6)
        self.lbl_cpr = etiqueta(m, "", E.TENUE)
        self.lbl_cpr.pack(anchor="w", padx=10, pady=(0, 8))

        der = marco(cuerpo)
        der.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        etiqueta(der, "CONSOLA", E.CIAN, titulo=True).pack(anchor="w", padx=10, pady=(8, 4))
        self.consola = ctk.CTkTextbox(der, fg_color=E.FONDO, text_color=E.VERDE, font=E.fuente(), corner_radius=0,
                                      border_width=0, wrap="word")
        self.consola.pack(fill="both", expand=True, padx=10)
        fila = ctk.CTkFrame(der, fg_color=E.PANEL)
        fila.pack(fill="x", padx=10, pady=10)
        self.c_orden = casilla(fila, "?", 300)
        self.c_orden.pack(side="left", fill="x", expand=True)
        self.c_orden.bind("<Return>", lambda e: self._orden_manual())
        boton(fila, "ENVIAR", self._orden_manual, E.CIAN, ancho=110, alto=30).pack(side="left", padx=6)
        etiqueta(der, "Ordenes: ? H X M K T F P R A S Z C E (ver la seccion 8 del .ino)", E.TENUE).pack(
            anchor="w", padx=10, pady=(0, 8))
        self.buscar_puertos()
        self._actualizar_cpr()

    def buscar_puertos(self):
        try:
            from serial.tools import list_ports
            puertos = [p.device for p in list_ports.comports()]
        except Exception:
            puertos = []
        self.menu_puertos.configure(values=puertos or ["(ninguno)"])
        actual = self.app.cfg.get("puerto")
        self.menu_puertos.set(actual if actual in puertos else (puertos[0] if puertos else "(ninguno)"))

    def _conectar(self):
        puerto = self.menu_puertos.get()
        if not puerto or puerto == "(ninguno)":
            messagebox.showwarning("Conexión", "No hay puertos. Conecte el Arduino y presione BUSCAR.")
            return
        self.app.conectar(puerto, int(leer_float(self.c_baudios, P.BAUDIOS)))

    def _aplicar(self):
        cfg = self.app.cfg
        for clave, c in self.casillas.items():
            cfg[clave] = leer_float(c, cfg[clave])
        cfg["motor"]["v_bus"] = leer_float(self.c_vbus, cfg["motor"]["v_bus"])
        cfg["invertir_corriente"] = self.v_inv_i.get()
        cfg["invertir_encoder"] = self.v_inv_e.get()
        self.app.guardar_cfg()
        self.app.sincronizar_gemelo()
        self.app.enviar("P", float(self.app.cuentas_por_vuelta()), float(cfg["motor"]["v_bus"]))
        self._actualizar_cpr()
        self.app.log("> Configuración del hardware aplicada.")

    def _actualizar_cpr(self):
        self.lbl_cpr.configure(text=f"CUENTAS/VUELTA = 4 x PPR x N = {self.app.cuentas_por_vuelta():.1f}")

    def _calibrar_cero(self):
        if self.app.ultimo["modo"] != 0 or self.app.datos.n == 0:
            messagebox.showinfo("Cero del sensor", "Conecte el Arduino y deje el motor en reposo (STOP).")
            return
        d = self.app.ultimos_segundos(0.5)
        cero = float(np.nanmean(d["adc"]))
        self.casillas["cero_adc"].delete(0, "end")
        self.casillas["cero_adc"].insert(0, f"{cero:.2f}")
        self._aplicar()

    def _orden_manual(self):
        texto = self.c_orden.get().strip()
        if texto and self.app.enlace:
            self.app.enlace.enviar((texto + "\n").encode("ascii", "replace"))
            self.consola_agregar("< " + texto)

    def consola_agregar(self, texto):
        self.consola.insert("end", texto + "\n")
        lineas = int(self.consola.index("end-1c").split(".")[0])
        if lineas > 600:
            self.consola.delete("1.0", f"{lineas - 500}.0")
        self.consola.see("end")


# -----------------------------------------------------------------------------
class PaginaTablero(Pagina):
    def __init__(self, master, app):
        super().__init__(master, app, "TABLERO // GEMELO DIGITAL", E.VERDE)
        arriba = ctk.CTkFrame(self, fg_color=E.FONDO)
        arriba.pack(fill="x")
        caja = marco(arriba)
        caja.pack(side="left")
        self.motor = MotorPixel(caja, aumento=2)
        self.motor.widget().pack(padx=4, pady=4)

        lecturas = marco(arriba)
        lecturas.pack(side="left", fill="both", expand=True, padx=(8, 0))
        self.lecturas = {}
        for fila, (clave, nombre, color) in enumerate((("theta", "POSICION  [RAD]", E.MAGENTA),
                                                       ("omega", "VELOCIDAD [RAD/S]", E.CIAN),
                                                       ("i", "CORRIENTE [A]", E.AMARILLO),
                                                       ("u", "VOLTAJE   [V]", E.VERDE),
                                                       ("ref", "REFERENCIA", E.NARANJA))):
            etiqueta(lecturas, nombre, E.TENUE).grid(row=fila, column=0, sticky="w", padx=12, pady=3)
            self.lecturas[clave] = etiqueta(lecturas, "--", color, titulo=True, tamano=16)
            self.lecturas[clave].grid(row=fila, column=1, sticky="e", padx=12)
        lecturas.grid_columnconfigure(1, weight=1)
        opciones = ctk.CTkFrame(lecturas, fg_color=E.PANEL)
        opciones.grid(row=0, column=2, rowspan=5, sticky="ns", padx=10, pady=8)
        self.sw_gemelo, self.v_gemelo = interruptor(opciones, "GEMELO DIGITAL", True, self._gemelo, E.MAGENTA)
        self.sw_gemelo.pack(anchor="w", pady=4)
        self.sw_pausa, self.v_pausa = interruptor(opciones, "PAUSAR GRAFICAS", False)
        self.sw_pausa.pack(anchor="w", pady=4)
        boton(opciones, "SINCRONIZAR", app.sincronizar_gemelo, E.MAGENTA, ancho=170, alto=30).pack(pady=4)
        boton(opciones, "CERO ENCODER", lambda: (app.enviar("Z"), app.sincronizar_gemelo()), E.TENUE,
              ancho=170, alto=30).pack(pady=4)
        fila = ctk.CTkFrame(opciones, fg_color=E.PANEL)
        fila.pack(pady=4)
        etiqueta(fila, "VENTANA [S]").pack(side="left")
        self.c_ventana = casilla(fila, app.cfg["ventana_s"], 60)
        self.c_ventana.pack(side="left", padx=4)
        self.c_ventana.bind("<Return>", self._ventana)

        caja = marco(self)
        caja.pack(fill="both", expand=True, pady=(8, 0))
        self.grafica = GraficaBarrido(caja, [
            [("theta", "MEDIDA", E.MAGENTA, "-"), ("ref_theta", "REF", E.VERDE, "-"), ("g_theta", "GEMELO", E.TEXTO, "--")],
            [("omega", "MEDIDA", E.CIAN, "-"), ("ref_omega", "REF", E.VERDE, "-"), ("g_omega", "GEMELO", E.TEXTO, "--")],
            [("i", "MEDIDA", E.AMARILLO, "-"), ("g_i", "GEMELO", E.TEXTO, "--")],
            [("u", "APLICADO", E.VERDE, "-")],
        ], ["θ [rad]", "ω [rad/s]", "i [A]", "u [V]"], ventana=app.cfg["ventana_s"], alto=5.0)
        self.grafica.widget().pack(fill="both", expand=True, padx=4, pady=4)

    def _gemelo(self):
        self.app.gemelo_activo = self.v_gemelo.get()
        if self.app.gemelo_activo:
            self.app.sincronizar_gemelo()
        for clave in ("g_theta", "g_omega", "g_i"):
            self.grafica.visibilidad(clave, self.app.gemelo_activo)

    def _ventana(self, _=None):
        v = max(0.5, min(60.0, leer_float(self.c_ventana, 5.0)))
        self.app.cfg["ventana_s"] = v
        self.grafica.fijar_ventana(v)

    def refrescar(self):
        app, u = self.app, self.app.ultimo
        modo = u["modo"]
        unidad = {1: "V", 2: "rad/s", 3: "rad"}.get(modo, "")
        self.motor.actualizar(theta=u["theta"], omega=u["omega"], corriente=u["i"], voltaje=u["u"],
                              v_bus=app.cfg["motor"]["v_bus"], reduccion=app.cfg["reduccion"], cuenta=int(u["cuenta"]),
                              modo=P.MODOS.get(modo, "?"), t=u["t"], theta_gemelo=u["g_theta"],
                              referencia=u["ref"], unidad_ref=unidad)
        for clave in ("theta", "omega", "i", "u"):
            self.lecturas[clave].configure(text=f"{u[clave]:+10.3f}")
        self.lecturas["ref"].configure(text=f"{u['ref']:+10.3f} {unidad}" if modo else "--")
        if self.v_pausa.get() or app.datos.n < 2:
            return
        d = app.ultimos_segundos(2.05 * self.grafica.ventana)
        modo_arr = d["modo"]
        d["ref_theta"] = np.where(modo_arr == 3, d["ref"], np.nan)
        d["ref_omega"] = np.where(modo_arr == 2, d["ref"], np.nan)
        self.grafica.refrescar(d["t"], d)


# -----------------------------------------------------------------------------
class PaginaPID(Pagina):
    MODOS = {"LAZO ABIERTO": 1, "VELOCIDAD": 2, "POSICION": 3}
    TIPOS = {"CONSTANTE": 0, "SENO": 1, "CUADRADA": 2, "TRIANGULAR": 3}

    def __init__(self, master, app):
        super().__init__(master, app, "CONTROL PID", E.AMARILLO)
        cfg = app.cfg
        cuerpo = ctk.CTkFrame(self, fg_color=E.FONDO)
        cuerpo.pack(fill="both", expand=True)
        izq = ctk.CTkScrollableFrame(cuerpo, fg_color=E.FONDO, width=560, corner_radius=0)
        izq.pack(side="left", fill="y")
        der = ctk.CTkFrame(cuerpo, fg_color=E.FONDO)
        der.pack(side="left", fill="both", expand=True, padx=(8, 0))

        m = marco(izq)
        m.pack(fill="x", pady=4)
        etiqueta(m, "MODO", E.AMARILLO, titulo=True).pack(anchor="w", padx=10, pady=(8, 4))
        self.seg_modo = segmentado(m, list(self.MODOS), self._cambiar_modo, E.AMARILLO)
        self.seg_modo.pack(fill="x", padx=10, pady=(0, 10))
        self.seg_modo.set({v: k for k, v in self.MODOS.items()}.get(cfg["modo_pid"], "VELOCIDAD"))

        m = marco(izq)
        m.pack(fill="x", pady=4)
        etiqueta(m, "GANANCIAS", E.AMARILLO, titulo=True).pack(anchor="w", padx=10, pady=(8, 2))
        self.lbl_formula = etiqueta(m, "", E.TENUE, justify="left")
        self.lbl_formula.pack(anchor="w", padx=10)
        rejilla = ctk.CTkFrame(m, fg_color=E.PANEL)
        rejilla.pack(padx=6, pady=6)
        self.p_kp = PerillaPixel(rejilla, "KP", 1e-4, 100, cfg["kp"], "log", "", E.CIAN, self._ganancias)
        self.p_ki = PerillaPixel(rejilla, "KI", 1e-4, 1000, cfg["ki"], "log", "", E.MAGENTA, self._ganancias)
        self.p_kd = PerillaPixel(rejilla, "KD", 1e-6, 10, cfg["kd"], "log", "", E.VERDE, self._ganancias)
        self.p_ts = PerillaPixel(rejilla, "TS", 0.5, 50, cfg["ts_ms"], "lin", "ms", E.AMARILLO, self._periodo, "{:.2f}")
        self.p_tau = PerillaPixel(rejilla, "FILTRO", 0, 100, cfg["tau_ms"], "lin", "ms", E.NARANJA, self._filtro, "{:.1f}")
        for k, p in enumerate((self.p_kp, self.p_ki, self.p_kd, self.p_ts, self.p_tau)):
            p.grid(row=k // 3, column=k % 3, padx=4, pady=4)
        self.sw_aw, self.v_aw = interruptor(m, "ANTI-WINDUP (CONGELA E_K AL SATURAR)", cfg["antiwindup"], self._opciones)
        self.sw_aw.pack(anchor="w", padx=10, pady=2)
        self.sw_auto, self.v_auto = interruptor(m, "ENVIAR AL SOLTAR LA PERILLA", cfg["envio_automatico"])
        self.sw_auto.pack(anchor="w", padx=10, pady=(2, 10))

        m = marco(izq)
        m.pack(fill="x", pady=4)
        etiqueta(m, "REFERENCIA r(t)", E.AMARILLO, titulo=True).pack(anchor="w", padx=10, pady=(8, 4))
        self.seg_tipo = segmentado(m, list(self.TIPOS), lambda _: self._referencia(), E.VERDE)
        self.seg_tipo.pack(fill="x", padx=10)
        self.seg_tipo.set({v: k for k, v in self.TIPOS.items()}[cfg["ref_tipo"]])
        etiqueta(m, "r = DESFASE + AMPLITUD * FORMA(2 PI F t)", E.TENUE).pack(anchor="w", padx=10, pady=2)
        rejilla = ctk.CTkFrame(m, fg_color=E.PANEL)
        rejilla.pack(padx=6, pady=6)
        self.p_amp = PerillaPixel(rejilla, "AMPLITUD", 0, 100, cfg["ref_amp"], "lin", "", E.VERDE, lambda v: self._referencia())
        self.p_off = PerillaPixel(rejilla, "DESFASE", -100, 100, cfg["ref_off"], "lin", "", E.VERDE, lambda v: self._referencia())
        self.p_f = PerillaPixel(rejilla, "FRECUENCIA", 0.01, 20, cfg["ref_f"], "log", "Hz", E.VERDE, lambda v: self._referencia())
        for k, p in enumerate((self.p_amp, self.p_off, self.p_f)):
            p.grid(row=0, column=k, padx=4, pady=4)

        fila = ctk.CTkFrame(izq, fg_color=E.FONDO)
        fila.pack(fill="x", pady=8)
        boton(fila, "ARRANCAR", self.arrancar, E.VERDE, ancho=170, alto=44).pack(side="left", padx=2)
        boton(fila, "DETENER", app.paro, E.ROJO, ancho=170, alto=44).pack(side="left", padx=2)
        boton(fila, "CERO ENC.", lambda: (app.enviar("Z"), app.sincronizar_gemelo()), E.TENUE,
              ancho=170, alto=44).pack(side="left", padx=2)

        caja = marco(der)
        caja.pack(fill="x")
        self.motor = MotorPixel(caja, aumento=2)
        self.motor.widget().pack(padx=4, pady=4)
        caja = marco(der)
        caja.pack(fill="both", expand=True, pady=(8, 0))
        self.grafica = GraficaBarrido(caja, [
            [("y", "MEDIDA", E.CIAN, "-"), ("ref", "REFERENCIA", E.VERDE, "-"), ("g_y", "GEMELO", E.TEXTO, "--")],
            [("u", "u = PID", E.AMARILLO, "-")],
        ], ["y", "u [V]"], ventana=app.cfg["ventana_s"], alto=3.6)
        self.grafica.widget().pack(fill="both", expand=True, padx=4, pady=4)
        self._ajustar_rangos()
        self._formula()

    def modo(self):
        return self.MODOS[self.seg_modo.get()]

    def _formula(self):
        texto = "u = Kp e + Ki Ts E + (Kd/Ts) (e - e_ant)"
        unidad = {1: "", 2: "  e en rad/s", 3: "  e en rad"}[self.modo()]
        self.lbl_formula.configure(text=texto + "\nE = E_ant + e   u en V" + unidad)

    def _ajustar_rangos(self):
        modo = self.modo()
        n = max(self.app.cfg["reduccion"], 1e-6)
        limite = {1: self.app.cfg["motor"]["v_bus"], 2: max(20.0, round(1000.0 / n)), 3: 60.0}[modo]
        for p, lo in ((self.p_amp, 0.0), (self.p_off, -limite)):
            p.vmin, p.vmax = lo, limite
            p.unidades = {1: "V", 2: "rad/s", 3: "rad"}[modo]
            p.fijar(p.valor, avisar=False)

    def _cambiar_modo(self, _=None):
        self.app.cfg["modo_pid"] = self.modo()
        self._ajustar_rangos()
        self._formula()

    def _ganancias(self, _=None):
        cfg = self.app.cfg
        cfg["kp"], cfg["ki"], cfg["kd"] = self.p_kp.valor, self.p_ki.valor, self.p_kd.valor
        if self.v_auto.get():
            self.app.enviar("K", cfg["kp"], cfg["ki"], cfg["kd"])

    def _periodo(self, valor):
        self.app.cfg["ts_ms"] = valor
        if self.v_auto.get():
            self.app.enviar("T", float(valor))

    def _filtro(self, valor):
        self.app.cfg["tau_ms"] = valor
        if self.v_auto.get():
            self.app.enviar("F", float(valor))

    def _opciones(self):
        cfg = self.app.cfg
        cfg["antiwindup"] = self.v_aw.get()
        self.app.enviar("A", int(cfg["antiwindup"]))
        self._formula()

    def _referencia(self):
        cfg = self.app.cfg
        cfg["ref_tipo"] = self.TIPOS[self.seg_tipo.get()]
        cfg["ref_amp"], cfg["ref_off"], cfg["ref_f"] = self.p_amp.valor, self.p_off.valor, self.p_f.valor
        if self.v_auto.get():
            self.app.enviar("R", cfg["ref_tipo"], float(cfg["ref_amp"]), float(cfg["ref_off"]), float(cfg["ref_f"]))

    def arrancar(self):
        if not self.app.enlace:
            messagebox.showwarning("PID", "Primero conecte el Arduino (o el simulado) en CONEXION.")
            return
        cfg = self.app.cfg
        self._cambiar_modo()
        cfg["ref_tipo"] = self.TIPOS[self.seg_tipo.get()]
        cfg["ref_amp"], cfg["ref_off"], cfg["ref_f"] = self.p_amp.valor, self.p_off.valor, self.p_f.valor
        cfg["kp"], cfg["ki"], cfg["kd"] = self.p_kp.valor, self.p_ki.valor, self.p_kd.valor
        cfg["ts_ms"], cfg["tau_ms"] = self.p_ts.valor, self.p_tau.valor
        a = self.app
        a.enviar("T", float(cfg["ts_ms"]))
        a.enviar("F", float(cfg["tau_ms"]))
        a.enviar("K", float(cfg["kp"]), float(cfg["ki"]), float(cfg["kd"]))
        a.enviar("A", int(self.v_aw.get()))
        a.enviar("R", cfg["ref_tipo"], float(cfg["ref_amp"]), float(cfg["ref_off"]), float(cfg["ref_f"]))
        a.enviar("M", self.modo())
        a.guardar_cfg()
        a.log(f"> Arranque: {self.seg_modo.get()}  Kp={cfg['kp']:.4g} Ki={cfg['ki']:.4g} Kd={cfg['kd']:.4g} "
              f"Ts={cfg['ts_ms']:.3g} ms")

    def refrescar(self):
        app, u = self.app, self.app.ultimo
        modo = u["modo"]
        unidad = {1: "V", 2: "rad/s", 3: "rad"}.get(modo, "")
        self.motor.actualizar(theta=u["theta"], omega=u["omega"], corriente=u["i"], voltaje=u["u"],
                              v_bus=app.cfg["motor"]["v_bus"], reduccion=app.cfg["reduccion"], cuenta=int(u["cuenta"]),
                              modo=P.MODOS.get(modo, "?"), t=u["t"], theta_gemelo=u["g_theta"],
                              referencia=u["ref"], unidad_ref=unidad)
        if app.datos.n < 2:
            return
        d = app.ultimos_segundos(2.05 * self.grafica.ventana)
        m = d["modo"]
        d["y"] = np.where(m == 3, d["theta"], d["omega"])
        d["g_y"] = np.where(m == 3, d["g_theta"], d["g_omega"])
        d["ref"] = np.where(m >= 1, d["ref"], np.nan)
        self.grafica.refrescar(d["t"], d)


# -----------------------------------------------------------------------------
class PaginaEnsayos(Pagina):
    def __init__(self, master, app):
        super().__init__(master, app, "ENSAYOS", E.NARANJA)
        cfg = app.cfg
        self.resultado = None
        self.tc, self.reproduciendo, self.velocidad = 0.0, False, 0.05
        self._t_pared = time.time()
        self._tipo_ensayo = "escalon"

        arriba = ctk.CTkFrame(self, fg_color=E.FONDO)
        arriba.pack(fill="x")
        # Botones de ensayo
        m = marco(arriba)
        m.pack(side="left", fill="y")
        boton(m, "ESCALON", lambda: self.ensayo("escalon"), E.NARANJA, ancho=230, alto=46).pack(padx=10, pady=(10, 4))
        boton(m, "DESCONEXION", lambda: self.ensayo("desconexion"), E.CIAN, ancho=230, alto=46).pack(padx=10, pady=4)
        boton(m, "SEGUIR MOVIMIENTO", self.seguir, E.VERDE, ancho=230, alto=46).pack(padx=10, pady=4)
        boton(m, "ABRIR ARCHIVO", self.abrir_archivo, E.TENUE, ancho=230, alto=34).pack(padx=10, pady=(4, 10))
        self.barra = ctk.CTkProgressBar(m, corner_radius=0, progress_color=E.NARANJA, fg_color=E.BORDE, width=230)
        self.barra.pack(padx=10)
        self.barra.set(0)
        self.lbl_estado = etiqueta(m, "LISTO", E.TENUE, wraplength=230, justify="left")
        self.lbl_estado.pack(padx=10, pady=(4, 10), anchor="w")

        # Parámetros de la captura rápida
        m = marco(arriba)
        m.pack(side="left", fill="y", padx=8)
        etiqueta(m, "ESCALON / DESCONEXION", E.NARANJA, titulo=True).grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(8, 2))
        self.p_pwm = PerillaPixel(m, "PWM", 0, 255, cfg["cap_pwm"], "lin", "", E.NARANJA, None, "{:.0f}")
        self.p_pwm.grid(row=1, column=0, rowspan=4, padx=8, pady=4)
        self.c_cap = {}
        for fila, (clave, texto) in enumerate((("cap_t0", "PREVIA [ms]"), ("cap_t1", "ESCALON [ms]"),
                                               ("cap_t2", "DESCONEXION [ms]")), start=1):
            etiqueta(m, texto).grid(row=fila, column=1, sticky="w", padx=4)
            self.c_cap[clave] = casilla(m, cfg[clave], 80)
            self.c_cap[clave].grid(row=fila, column=2, padx=4, pady=2)
        self.seg_sentido = segmentado(m, ["ADELANTE", "REVERSA"], None, E.NARANJA)
        self.seg_sentido.set("ADELANTE" if cfg["cap_sentido"] >= 0 else "REVERSA")
        self.seg_sentido.grid(row=4, column=1, columnspan=2, sticky="ew", padx=4, pady=2)
        self.sw_freno, self.v_freno = interruptor(m, "FRENAR AL DESCONECTAR", cfg["cap_freno"], None, E.NARANJA)
        self.sw_freno.grid(row=5, column=0, columnspan=3, sticky="w", padx=10, pady=(2, 8))

        # Parámetros del seguimiento
        m = marco(arriba)
        m.pack(side="left", fill="both", expand=True)
        etiqueta(m, "SEGUIR MOVIMIENTO (USA EL PID)", E.VERDE, titulo=True).grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(8, 2))
        self.seg_seguir_modo = segmentado(m, ["POSICION", "VELOCIDAD"], None, E.VERDE)
        self.seg_seguir_modo.set("POSICION" if cfg["seguir_modo"] == 3 else "VELOCIDAD")
        self.seg_seguir_modo.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=2)
        self.seg_seguir_tipo = segmentado(m, ["SENO", "CUADRADA", "TRIANGULAR"], None, E.VERDE)
        self.seg_seguir_tipo.set({1: "SENO", 2: "CUADRADA", 3: "TRIANGULAR"}.get(cfg["seguir_tipo"], "SENO"))
        self.seg_seguir_tipo.grid(row=2, column=0, columnspan=4, sticky="ew", padx=10, pady=2)
        self.c_seg = {}
        for k, (clave, texto) in enumerate((("seguir_amp", "AMPLITUD"), ("seguir_off", "DESFASE"),
                                            ("seguir_f", "FRECUENCIA [Hz]"), ("seguir_duracion", "DURACION [s]"))):
            etiqueta(m, texto).grid(row=3 + k // 2, column=2 * (k % 2), sticky="w", padx=10, pady=2)
            self.c_seg[clave] = casilla(m, cfg[clave], 80)
            self.c_seg[clave].grid(row=3 + k // 2, column=2 * (k % 2) + 1, padx=4, pady=2)
        etiqueta(m, "Las ganancias son las de la pagina CONTROL PID.", E.TENUE).grid(
            row=5, column=0, columnspan=4, sticky="w", padx=10, pady=(2, 8))

        # Visor de resultados
        abajo = ctk.CTkFrame(self, fg_color=E.FONDO)
        abajo.pack(fill="both", expand=True, pady=(8, 0))
        lado = ctk.CTkFrame(abajo, fg_color=E.FONDO)
        lado.pack(side="left", fill="y")
        caja = marco(lado)
        caja.pack()
        self.motor = MotorPixel(caja, aumento=2)
        self.motor.widget().pack(padx=4, pady=4)
        controles = marco(lado)
        controles.pack(fill="x", pady=(8, 0))
        fila = ctk.CTkFrame(controles, fg_color=E.PANEL)
        fila.pack(fill="x", padx=8, pady=8)
        self.b_play = boton(fila, "PLAY", self.alternar, E.VERDE, ancho=110, alto=34)
        self.b_play.pack(side="left")
        boton(fila, "|<", lambda: self.ir_a(None), E.TENUE, ancho=50, alto=34).pack(side="left", padx=4)
        self.menu_vel = ctk.CTkOptionMenu(fila, values=["0.01x", "0.02x", "0.05x", "0.1x", "0.25x", "0.5x", "1x"],
                                          command=self._velocidad, width=90, corner_radius=0, font=E.fuente(),
                                          fg_color=E.PANEL_2, button_color=E.BORDE, dropdown_font=E.fuente())
        self.menu_vel.set("0.05x")
        self.menu_vel.pack(side="left", padx=4)
        boton(fila, "PNG", self.exportar_png, E.TENUE, ancho=60, alto=34).pack(side="left", padx=4)
        self.deslizador = ctk.CTkSlider(controles, from_=0, to=1, command=self._deslizar, progress_color=E.NARANJA,
                                        button_color=E.AMARILLO, corner_radius=0, button_corner_radius=0)
        self.deslizador.pack(fill="x", padx=8, pady=(0, 8))
        self.resumen = ctk.CTkTextbox(lado, width=440, height=150, fg_color=E.PANEL, text_color=E.TEXTO,
                                      font=E.fuente(), corner_radius=0, border_width=2, border_color=E.BORDE)
        self.resumen.pack(fill="both", expand=True, pady=(8, 0))

        caja = marco(abajo)
        caja.pack(side="left", fill="both", expand=True, padx=(8, 0))
        self.grafica = GraficaReproduccion(caja, ["θ [rad]", "ω [rad/s]", "i [A]"], alto=4.6, al_hacer_clic=self.ir_a)
        self.grafica.widget().pack(fill="both", expand=True, padx=4, pady=4)

    # --- Ensayos ---
    def _leer_parametros(self):
        cfg = self.app.cfg
        cfg["cap_pwm"] = int(round(self.p_pwm.valor))
        for clave, c in self.c_cap.items():
            cfg[clave] = int(max(1, min(60000, leer_float(c, cfg[clave]))))
        cfg["cap_sentido"] = 1 if self.seg_sentido.get() == "ADELANTE" else -1
        cfg["cap_freno"] = int(self.v_freno.get())
        for clave, c in self.c_seg.items():
            cfg[clave] = leer_float(c, cfg[clave])
        cfg["seguir_modo"] = 3 if self.seg_seguir_modo.get() == "POSICION" else 2
        cfg["seguir_tipo"] = {"SENO": 1, "CUADRADA": 2, "TRIANGULAR": 3}[self.seg_seguir_tipo.get()]
        self.app.guardar_cfg()

    def ensayo(self, tipo):
        if not self.app.enlace:
            messagebox.showwarning("Ensayos", "Primero conecte el Arduino (o el simulado) en CONEXION.")
            return
        self._leer_parametros()
        cfg, a = self.app.cfg, self.app
        t2 = cfg["cap_t2"] if tipo == "desconexion" else min(cfg["cap_t2"], 300)
        self._tipo_ensayo = tipo
        a.enviar("X")
        self.barra.set(0)
        self.lbl_estado.configure(text="ESPERANDO A QUE EL MOTOR SE DETENGA...", text_color=E.AMARILLO)
        datos_c = (cfg["cap_pwm"], cfg["cap_sentido"], cfg["cap_freno"], cfg["cap_t0"], cfg["cap_t1"], t2)
        self._esperar_reposo(time.time(), datos_c)

    def _esperar_reposo(self, inicio, datos_c):
        """El ensayo debe partir con el motor detenido: espera hasta que la
        velocidad medida sea casi cero durante 0,3 s (como máximo 8 s)."""
        a = self.app
        d = a.ultimos_segundos(0.3)
        quieto = a.datos.n > 10 and np.nanmax(np.abs(d["omega"])) < 0.5
        if not (quieto or time.time() - inicio > 8.0):
            self.after(100, lambda: self._esperar_reposo(inicio, datos_c))
            return
        if not quieto:
            a.log("! El motor no se detuvo en 8 s; el ensayo empieza igual.")
        a.enviar("S", 0)
        a.enviar("C", *datos_c)
        a.enlace.iniciar_captura()
        self.lbl_estado.configure(text="CAPTURA RAPIDA EN CURSO...", text_color=E.AMARILLO)

    def progreso(self, fraccion):
        self.barra.set(fraccion)

    def captura_recibida(self, captura):
        a = self.app
        a.enviar("S", 1)
        a._k_prev = None
        carpeta = Path(a.cfg["carpeta_datos"])
        base = carpeta / f"{self._tipo_ensayo}_{time.strftime('%Y%m%d_%H%M%S')}"
        meta = P.guardar_captura_rapida(base, captura["datos"], captura["encabezado"], captura["resumen"])
        a.log(f"> Captura guardada: {base}.bin / _crudo.csv / .json ({meta['tramas_recibidas']} tramas)")
        self.lbl_estado.configure(text="PROCESANDO...", text_color=E.AMARILLO)
        a.en_hilo(lambda: self._procesar_rapida(base), self.mostrar_resultado)

    def _procesar_rapida(self, base):
        cfg = self.app.cfg
        crudos, meta = P.cargar_captura_rapida(base)
        res, resumen = PP.procesar(crudos, meta, cfg["ppr"], cfg["reduccion"], cfg["vref"], cfg["sensibilidad"],
                                   cfg["invertir_encoder"], cfg["invertir_corriente"])
        PP.guardar_procesado(base, res)
        Path(str(base) + "_resumen.json").write_text(json.dumps(resumen, indent=2), encoding="utf-8")
        enc = meta["encabezado"]
        t = res["t_s"]
        # Gemelo: misma entrada que el ensayo, simulado en una malla de 4 kHz.
        p = self.app.parametros_motor()
        paso = max(1, int(enc["fs_hz"] / 4000))
        ts = t[::paso]
        motor = crudos["motor"][::paso].astype(bool)
        k_on, k_off = resumen["k_escalon"], resumen["k_desconexion"]
        u = np.where(motor, enc.get("sentido", 1) * enc.get("pwm", 255) / 255 * p.v_bus, 0.0)
        despues = np.zeros(len(ts), dtype=bool)
        if k_off is not None:
            despues[k_off // paso:] = True
        abierto = ~motor & ~(despues & bool(enc.get("freno", 0)))
        sim = simular(ts, u, abierto, p, self.app.cfg["metodo"], self.app.cfg["h_modelo"])
        tipo = "desconexion" if "desconexion" in Path(base).name else "escalon"
        inicio = t[k_off] if (tipo == "desconexion" and k_off) else (t[k_on] if k_on else 0.0)
        return {"titulo": Path(base).name, "base": str(base), "t": t, "theta": res["theta_rad"], "omega": res["omega_flancos_rad_s"],
                "i": res["corriente_suave_A"], "u": np.interp(t, ts, u), "cuenta": res["cuenta"],
                "g_t": ts, "g_theta": sim["theta"], "g_omega": sim["omega"], "g_i": sim["i"],
                "verticales": [t[k] for k in (k_on, k_off) if k is not None], "inicio": max(0.0, inicio - 0.02),
                "resumen": resumen, "tipo": tipo, "velocidad": 0.02}

    def seguir(self):
        a = self.app
        if not a.enlace:
            messagebox.showwarning("Ensayos", "Primero conecte el Arduino (o el simulado) en CONEXION.")
            return
        self._leer_parametros()
        cfg = a.cfg
        a.enviar("X")
        a.enviar("T", float(cfg["ts_ms"]))
        a.enviar("F", float(cfg["tau_ms"]))
        a.enviar("K", float(cfg["kp"]), float(cfg["ki"]), float(cfg["kd"]))
        a.enviar("Z")
        a.sincronizar_gemelo()
        a.gemelo.reiniciar(0.0, 0.0)
        a.enviar("R", cfg["seguir_tipo"], float(cfg["seguir_amp"]), float(cfg["seguir_off"]), float(cfg["seguir_f"]))
        a.enviar("M", cfg["seguir_modo"])
        self.lbl_estado.configure(text=f"SIGUIENDO EL MOVIMIENTO ({cfg['seguir_duracion']:.1f} s)...", text_color=E.AMARILLO)
        a.iniciar_grabacion(cfg["seguir_duracion"], self._fin_seguir)

    def _fin_seguir(self):
        a = self.app
        a.enviar("X")
        filas = a.detener_grabacion()
        # Descarta la telemetría que llegó antes de que el Arduino cambiara de modo.
        modo = a.cfg["seguir_modo"]
        primera = next((j for j, f in enumerate(filas) if int(f[9]) == modo), len(filas))
        filas = [f for f in filas[primera:] if int(f[9]) == modo]
        if len(filas) < 3:
            self.lbl_estado.configure(text="NO LLEGO TELEMETRIA", text_color=E.ROJO)
            return
        base = a.guardar_grabacion(filas, f"seguimiento_{time.strftime('%Y%m%d_%H%M%S')}")
        self.mostrar_resultado(self._desde_tiempo_real(np.array(filas, dtype=float), base.name, a.cfg["seguir_modo"]))

    def _desde_tiempo_real(self, x, titulo, modo):
        t = x[:, 0] - x[0, 0]
        ref = x[:, 4]
        resumen = {"muestras": len(t), "duracion_s": float(t[-1]),
                   "error_rms": float(np.sqrt(np.mean((ref - (x[:, 3] if modo == 3 else x[:, 5])) ** 2))),
                   "saturado_%": float(100 * np.mean((x[:, 10].astype(int) & 1) > 0))}
        return {"titulo": titulo, "t": t, "theta": x[:, 3], "omega": x[:, 5], "i": x[:, 8], "u": x[:, 6],
                "cuenta": x[:, 2], "g_t": t, "g_theta": x[:, 11], "g_omega": x[:, 12], "g_i": x[:, 13],
                "ref_theta": ref if modo == 3 else None, "ref_omega": ref if modo == 2 else None,
                "verticales": [], "inicio": 0.0, "resumen": resumen, "tipo": "seguimiento", "velocidad": 1.0}

    def abrir_archivo(self, ruta=None):
        ruta = ruta or filedialog.askopenfilename(initialdir=self.app.cfg["carpeta_datos"],
                                                  filetypes=[("Capturas", "*.json")])
        if not ruta:
            return
        ruta = Path(ruta)
        try:
            meta = json.loads(ruta.read_text(encoding="utf-8"))
        except Exception as e:
            messagebox.showerror("Abrir", f"No se pudo leer {ruta.name}: {e}")
            return
        self.app.mostrar("ensayos")
        if meta.get("tipo") == "captura_rapida":
            self.lbl_estado.configure(text="PROCESANDO...", text_color=E.AMARILLO)
            self.app.en_hilo(lambda: self._procesar_rapida(ruta.with_suffix("")), self.mostrar_resultado)
        else:
            x = np.loadtxt(ruta.with_suffix(".csv"), delimiter=",", skiprows=1, ndmin=2)
            modo = int(np.nanmax(x[:, 9])) if len(x) else 3
            self.mostrar_resultado(self._desde_tiempo_real(x, ruta.stem, modo))

    # --- Reproducción ---
    def mostrar_resultado(self, r):
        self.resultado = r
        g = lambda clave: np.interp(r["t"], r["g_t"], r[clave])   # noqa: E731
        series = [
            [("MEDIDA", r["theta"], E.MAGENTA, "-"), ("GEMELO", g("g_theta"), E.TEXTO, "--")],
            [("MEDIDA", r["omega"], E.CIAN, "-"), ("GEMELO", g("g_omega"), E.TEXTO, "--")],
            [("MEDIDA", r["i"], E.AMARILLO, "-"), ("GEMELO", g("g_i"), E.TEXTO, "--")],
        ]
        if r.get("ref_theta") is not None:
            series[0].insert(1, ("REF", r["ref_theta"], E.VERDE, "-"))
        if r.get("ref_omega") is not None:
            series[1].insert(1, ("REF", r["ref_omega"], E.VERDE, "-"))
        self.grafica.cargar(r["t"], series, r["verticales"])
        self.velocidad = r["velocidad"]
        self.menu_vel.set(f"{self.velocidad:g}x")
        self.ir_a(r["inicio"])
        self.reproduciendo = True
        self.b_play.configure(text="PAUSA")
        self.resumen.delete("1.0", "end")
        self.resumen.insert("end", f"{r['titulo']}\n")
        for clave, valor in r["resumen"].items():
            texto = f"{valor:.5g}" if isinstance(valor, float) else str(valor)
            self.resumen.insert("end", f"{clave:26s} {texto}\n")
        avisos = []
        if r["resumen"].get("saltos_invalidos_encoder"):
            avisos.append("! SALTOS INVALIDOS EN EL ENCODER")
        if r["resumen"].get("marcas_de_perdida"):
            avisos.append("! SE PERDIERON TRAMAS")
        self.lbl_estado.configure(text="\n".join(avisos) or f"LISTO: {r['tipo'].upper()}",
                                  text_color=E.ROJO if avisos else E.VERDE)
        self.barra.set(1)

    def alternar(self):
        self.reproduciendo = not self.reproduciendo
        self.b_play.configure(text="PAUSA" if self.reproduciendo else "PLAY")

    def _velocidad(self, valor):
        self.velocidad = float(valor.rstrip("x"))

    def _deslizar(self, f):
        if self.resultado is not None:
            t = self.resultado["t"]
            self.tc = t[0] + f * (t[-1] - t[0])
            self._dibujar()

    def ir_a(self, tc):
        if self.resultado is None:
            return
        t = self.resultado["t"]
        self.tc = t[0] if tc is None else min(max(tc, t[0]), t[-1])
        self._dibujar()

    def exportar_png(self):
        if self.resultado is None:
            return
        destino = Path(self.app.cfg["carpeta_datos"]) / f"{self.resultado['titulo']}_reproduccion.png"
        self.grafica.fig.savefig(destino, dpi=130, facecolor=E.PANEL)
        self.app.log(f"> Gráfica guardada: {destino}")

    def refrescar(self):
        ahora = time.time()
        dt, self._t_pared = ahora - self._t_pared, ahora
        if self.resultado is None:
            self.motor.actualizar(modo="SIN DATOS", t=0.0)
            return
        if self.reproduciendo:
            t = self.resultado["t"]
            self.tc += dt * self.velocidad
            if self.tc > t[-1]:
                self.tc = t[0]
            self.deslizador.set((self.tc - t[0]) / max(t[-1] - t[0], 1e-9))
        self._dibujar()

    def _dibujar(self):
        r, tc = self.resultado, self.tc
        t = r["t"]
        k = min(len(t) - 1, max(0, int(np.searchsorted(t, tc))))
        theta_g = float(np.interp(tc, r["g_t"], r["g_theta"]))
        ref = r.get("ref_theta")
        self.motor.actualizar(theta=float(np.interp(tc, t, r["theta"])), omega=float(np.interp(tc, t, r["omega"])),
                              corriente=float(np.interp(tc, t, r["i"])), voltaje=float(r["u"][k]),
                              v_bus=self.app.cfg["motor"]["v_bus"], reduccion=self.app.cfg["reduccion"],
                              cuenta=int(r["cuenta"][k]), modo=r["tipo"].upper(), t=tc, theta_gemelo=theta_g,
                              referencia=None if ref is None else float(ref[k]), unidad_ref="rad")
        self.grafica.cursor(tc)


# -----------------------------------------------------------------------------
class PaginaCaptura(Pagina):
    def __init__(self, master, app):
        super().__init__(master, app, "CAPTURA DE DATOS", E.MAGENTA)
        arriba = marco(self)
        arriba.pack(fill="x")
        etiqueta(arriba, "GRABAR TELEMETRIA EN TIEMPO REAL", E.MAGENTA, titulo=True).pack(anchor="w", padx=10, pady=(8, 4))
        fila = ctk.CTkFrame(arriba, fg_color=E.PANEL)
        fila.pack(fill="x", padx=10, pady=(0, 10))
        self.b_grabar = boton(fila, "GRABAR", self.alternar, E.ROJO, ancho=170, alto=44)
        self.b_grabar.pack(side="left")
        etiqueta(fila, "NOMBRE").pack(side="left", padx=(16, 4))
        self.c_nombre = casilla(fila, "", 260)
        self.c_nombre.pack(side="left")
        self.lbl = etiqueta(fila, "DETENIDO", E.TENUE)
        self.lbl.pack(side="left", padx=16)
        etiqueta(arriba, "Columnas: " + ", ".join(App.COLUMNAS_GRABACION), E.TENUE, wraplength=1100,
                 justify="left").pack(anchor="w", padx=10, pady=(0, 8))

        m = marco(self)
        m.pack(fill="both", expand=True, pady=(8, 0))
        fila = ctk.CTkFrame(m, fg_color=E.PANEL)
        fila.pack(fill="x", padx=10, pady=8)
        etiqueta(fila, "ARCHIVOS GUARDADOS", E.MAGENTA, titulo=True).pack(side="left")
        boton(fila, "ACTUALIZAR", self.listar, E.TENUE, ancho=140, alto=30).pack(side="right")
        boton(fila, "ABRIR CARPETA", self.abrir_carpeta, E.TENUE, ancho=170, alto=30).pack(side="right", padx=6)
        boton(fila, "CAMBIAR CARPETA", self.cambiar_carpeta, E.TENUE, ancho=190, alto=30).pack(side="right")
        self.lbl_carpeta = etiqueta(m, app.cfg["carpeta_datos"], E.TENUE)
        self.lbl_carpeta.pack(anchor="w", padx=10)
        self.lista = ctk.CTkScrollableFrame(m, fg_color=E.FONDO, corner_radius=0)
        self.lista.pack(fill="both", expand=True, padx=10, pady=10)

    def al_mostrar(self):
        self.listar()

    def alternar(self):
        a = self.app
        if a.grabando is None:
            if not a.enlace:
                messagebox.showwarning("Captura", "Primero conecte el Arduino (o el simulado).")
                return
            a.iniciar_grabacion()
            self.b_grabar.configure(text="DETENER")
        else:
            filas = a.detener_grabacion()
            nombre = self.c_nombre.get().strip() or None
            a.guardar_grabacion(filas, nombre)
            self.b_grabar.configure(text="GRABAR")
            self.listar()

    def refrescar(self):
        g = self.app.grabando
        if g is None:
            self.lbl.configure(text="DETENIDO", text_color=E.TENUE)
        else:
            dur = g[-1][0] - g[0][0] if len(g) > 1 else 0.0
            self.lbl.configure(text=f"GRABANDO  {len(g)} MUESTRAS  {dur:7.2f} S", text_color=E.ROJO)

    def listar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        carpeta = Path(self.app.cfg["carpeta_datos"])
        archivos = sorted(carpeta.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True) if carpeta.is_dir() else []
        archivos = [a for a in archivos if not a.name.endswith("_resumen.json")]
        if not archivos:
            etiqueta(self.lista, "(no hay capturas todavia)", E.TENUE).pack(anchor="w")
        for ruta in archivos[:200]:
            try:
                tipo = json.loads(ruta.read_text(encoding="utf-8")).get("tipo", "?")
            except Exception:
                tipo = "?"
            fila = ctk.CTkFrame(self.lista, fg_color=E.PANEL, corner_radius=0)
            fila.pack(fill="x", pady=2)
            color = E.NARANJA if tipo == "captura_rapida" else E.CIAN
            etiqueta(fila, f"{ruta.stem:42s} {tipo:16s} {time.strftime('%d/%m %H:%M', time.localtime(ruta.stat().st_mtime))}",
                     color).pack(side="left", padx=8)
            boton(fila, "VER", lambda r=ruta: self.app.paginas["ensayos"].abrir_archivo(r), color,
                  ancho=80, alto=28).pack(side="right", padx=4, pady=2)

    def abrir_carpeta(self):
        carpeta = Path(self.app.cfg["carpeta_datos"])
        carpeta.mkdir(parents=True, exist_ok=True)
        if hasattr(os, "startfile"):
            os.startfile(carpeta)

    def cambiar_carpeta(self):
        nueva = filedialog.askdirectory(initialdir=self.app.cfg["carpeta_datos"])
        if nueva:
            self.app.cfg["carpeta_datos"] = nueva
            self.app.guardar_cfg()
            self.lbl_carpeta.configure(text=nueva)
            self.listar()


# -----------------------------------------------------------------------------
class PaginaModelo(Pagina):
    CAMPOS = (("R", "R [OHM]"), ("L", "L [H]"), ("Ke", "KE [V S/RAD]"), ("Kt", "KT [N M/A]"), ("J", "J [KG M2]"),
              ("b", "B [N M S/RAD]"), ("tau_c", "TAU_C [N M]"), ("eps", "EPS SIGN [RAD/S]"),
              ("tau_carga", "TAU CARGA [N M]"), ("v_caida", "CAIDA L298N [V]"))

    def __init__(self, master, app):
        super().__init__(master, app, "MODELO DEL MOTOR", E.MORADO)
        cuerpo = ctk.CTkFrame(self, fg_color=E.FONDO)
        cuerpo.pack(fill="both", expand=True)
        izq = ctk.CTkScrollableFrame(cuerpo, fg_color=E.FONDO, width=420, corner_radius=0)
        izq.pack(side="left", fill="y")
        m = marco(izq)
        m.pack(fill="x")
        etiqueta(m, "PARAMETROS (EJE DEL MOTOR)", E.MORADO, titulo=True).pack(anchor="w", padx=10, pady=(8, 2))
        etiqueta(m, "VALORES DE EJEMPLO: reemplazar por los\nidentificados con los ensayos.", E.ROJO,
                 justify="left").pack(anchor="w", padx=10, pady=(0, 4))
        self.casillas = {}
        for clave, texto in self.CAMPOS:
            fila = ctk.CTkFrame(m, fg_color=E.PANEL)
            fila.pack(fill="x", padx=10, pady=2)
            etiqueta(fila, texto).pack(side="left")
            self.casillas[clave] = casilla(fila, f"{app.cfg['motor'][clave]:.6g}", 120)
            self.casillas[clave].pack(side="right")
        etiqueta(m, "L di/dt = V - R i - Ke w\nJ dw/dt = Kt i - b w - tau_c sign(w) - tau_carga\n"
                    "d(theta)/dt = w      (sign suavizado con tanh(w/eps))", E.TENUE, justify="left").pack(
            anchor="w", padx=10, pady=6)
        m = marco(izq)
        m.pack(fill="x", pady=8)
        etiqueta(m, "INTEGRADOR", E.MORADO, titulo=True).pack(anchor="w", padx=10, pady=(8, 4))
        self.seg_metodo = segmentado(m, ["Euler", "RK4"], None, E.MORADO)
        self.seg_metodo.set(app.cfg["metodo"])
        self.seg_metodo.pack(fill="x", padx=10)
        fila = ctk.CTkFrame(m, fg_color=E.PANEL)
        fila.pack(fill="x", padx=10, pady=6)
        etiqueta(fila, "PASO h [S]").pack(side="left")
        self.c_h = casilla(fila, f"{app.cfg['h_modelo']:.3g}", 120)
        self.c_h.pack(side="right")
        self.lbl_estabilidad = etiqueta(m, "", E.AMARILLO, justify="left")
        self.lbl_estabilidad.pack(anchor="w", padx=10, pady=(0, 8))
        fila = ctk.CTkFrame(izq, fg_color=E.FONDO)
        fila.pack(fill="x", pady=4)
        boton(fila, "APLICAR", self.aplicar, E.VERDE, ancho=200).pack(side="left", padx=2)
        boton(fila, "SIMULAR", self.simular_escalon, E.MORADO, ancho=200).pack(side="left", padx=2)
        boton(izq, "COMPARAR CON LA ULTIMA CAPTURA", self.comparar, E.NARANJA, ancho=404).pack(pady=4)

        caja = marco(cuerpo)
        caja.pack(side="left", fill="both", expand=True, padx=(8, 0))
        self.grafica = GraficaReproduccion(caja, ["ω [rad/s]", "i [A]"], alto=5.5)
        self.grafica.widget().pack(fill="both", expand=True, padx=4, pady=4)
        self._estabilidad()

    def aplicar(self):
        cfg = self.app.cfg
        for clave, c in self.casillas.items():
            cfg["motor"][clave] = leer_float(c, cfg["motor"][clave])
        cfg["metodo"] = self.seg_metodo.get()
        cfg["h_modelo"] = max(1e-7, leer_float(self.c_h, cfg["h_modelo"]))
        self.app.guardar_cfg()
        self.app.sincronizar_gemelo()
        self._estabilidad()
        self.app.log("> Modelo aplicado al gemelo digital.")

    def _estabilidad(self):
        """Paso máximo de Euler para la parte lineal: |1 + h λ| < 1 para cada valor propio λ."""
        p = self.app.parametros_motor()
        A = np.array([[-p.R / p.L, -p.Ke / p.L], [p.Kt / p.J, -p.b / p.J]])
        lam = np.linalg.eigvals(A)
        h_max = min(-2 * l.real / abs(l) ** 2 for l in lam if l.real < 0) if all(l.real < 0 for l in lam) else float("nan")
        tau = sorted(-1 / l.real for l in lam if l.real < 0)
        self.lbl_estabilidad.configure(
            text=f"VALORES PROPIOS: {lam[0]:.4g}, {lam[1]:.4g}\nCONSTANTES DE TIEMPO: "
                 + ", ".join(f"{1000 * x:.3g} ms" for x in tau)
                 + f"\nEULER ESTABLE SI h < {h_max:.3g} s (PARTE LINEAL)")

    def simular_escalon(self):
        self.aplicar()
        p = self.app.parametros_motor()
        t = np.linspace(0, 1.0, 4001)
        u = np.where(t >= 0.05, p.v_bus, 0.0)
        sim = simular(t, u, t < 0.05, p, self.app.cfg["metodo"], self.app.cfg["h_modelo"])
        self.grafica.cargar(t, [[("MODELO", sim["omega"], E.CIAN, "-")], [("MODELO", sim["i"], E.AMARILLO, "-")]], [0.05])
        self.grafica.cursor(0.05)

    def comparar(self):
        r = self.app.paginas["ensayos"].resultado
        if r is None or r["tipo"] == "seguimiento":
            messagebox.showinfo("Modelo", "Primero haga un ensayo de escalón o de desconexión (o abra uno).")
            return
        self.aplicar()
        pagina = self.app.paginas["ensayos"]
        self.app.en_hilo(lambda: pagina._procesar_rapida(Path(r["base"])), self._mostrar_comparacion)

    def _mostrar_comparacion(self, r):
        self.app.paginas["ensayos"].mostrar_resultado(r)
        g = lambda c: np.interp(r["t"], r["g_t"], r[c])   # noqa: E731
        self.grafica.cargar(r["t"], [[("MEDIDA", r["omega"], E.CIAN, "-"), ("MODELO", g("g_omega"), E.TEXTO, "--")],
                                     [("MEDIDA", r["i"], E.AMARILLO, "-"), ("MODELO", g("g_i"), E.TEXTO, "--")]],
                            r["verticales"])
        self.grafica.cursor(r["t"][0])


if __name__ == "__main__":
    App().mainloop()
