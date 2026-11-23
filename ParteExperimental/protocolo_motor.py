"""
Protocolo serie del Arduino Nano que corre MotorDC_L298N.ino.

Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
Fecha de creación: 22/11/2026
Autores: Mario Alejandro Betancourt Franco (23440)
         Claude Opus 5.5 (Anthropic), asistente de IA

Este módulo es la contraparte en Python de las secciones 6, 7 y 8 del .ino.
Lo usan el receptor de línea de comandos (captura_respuesta.py), el
postprocesamiento y la aplicación del gemelo digital.

  * Captura rápida: tramas de 2 bytes con los datos brutos (ADC, fases A y B).
  * Tiempo real: tramas de telemetría de 27 bytes y líneas de texto con '#'.
  * Órdenes: líneas de texto ("K 0.1 0.5 0.001\\n", ...).
  * EnlaceSerie: hilo que lee el puerto y entrega eventos en una cola.

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md). No se ha probado
con el hardware real; se probó con datos sintéticos y con el Arduino simulado.
"""
from __future__ import annotations

import json
import queue
import struct
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

BAUDIOS = 1_000_000   # Ver la sección 2 del .ino: a 2 Mbaud el adaptador USB del equipo perdía bytes

# --- Captura rápida -----------------------------------------------------------
BANDERA_PERDIDA = 0x40
BANDERA_MOTOR = 0x20
BIT_FASE_B = 0x10
BIT_FASE_A = 0x08
MARCADOR_FIN = b"\xff\xff\xff\xff\nFIN"

# --- Tiempo real ----------------------------------------------------------------
SYNC = b"\xa5\x5a"
TELEMETRIA = struct.Struct("<IifffHBB")   # k, cuenta, ref, velocidad, voltaje, adc16, modo, estado
LARGO_TRAMA = 2 + TELEMETRIA.size + 1    # sync + datos + suma = 27 bytes

MODOS = {0: "REPOSO", 1: "LAZO ABIERTO", 2: "PID VELOCIDAD", 3: "PID POSICION"}
REFERENCIAS = {0: "CONSTANTE", 1: "SENO", 2: "CUADRADA", 3: "TRIANGULAR"}
ESTADO_SATURADO, ESTADO_ERROR_ENCODER, ESTADO_ATRASADO, ESTADO_CONGELADO = 1, 2, 4, 8


# =============================================================================
#  Captura rápida
# =============================================================================
def leer_parametros(linea: str) -> dict:
    """'INICIO fs_hz=76923.08 n_previas=...' -> {'fs_hz': 76923.08, ...}."""
    salida = {}
    for token in linea.split():
        if "=" in token:
            clave, valor = token.split("=", 1)
            try:
                salida[clave] = float(valor)
            except ValueError:
                salida[clave] = valor
    return salida


def decodificar_rapida(datos: bytes) -> tuple[dict, int]:
    """Convierte los bytes de la captura rápida en arreglos de datos brutos.

    Trama (sección 6 del .ino):  b0 = 1 P M B A C9 C8 C7 · b1 = 0 C6..C0
    Devuelve ({'adc', 'a', 'b', 'motor', 'perdida'}, bytes_descartados).
    Si los bytes están alineados se decodifica todo de una vez con numpy; si
    se perdió algún byte, se resincroniza con el siguiente byte con el bit 7 en 1.
    """
    x = np.frombuffer(bytes(datos), dtype=np.uint8)
    descartados = 0
    if len(x) % 2 == 0 and np.all(x[0::2] >= 0x80) and np.all(x[1::2] < 0x80):
        b0, b1 = x[0::2], x[1::2]
    else:
        inicios, i, n = [], 0, len(x)
        while i + 1 < n:
            if x[i] >= 0x80 and x[i + 1] < 0x80:
                inicios.append(i)
                i += 2
            else:
                descartados += 1
                i += 1
        inicios = np.asarray(inicios, dtype=np.int64)
        b0, b1 = x[inicios], x[inicios + 1]
    b0 = b0.astype(np.uint16)
    b1 = b1.astype(np.uint16)
    crudos = {
        "adc": ((b0 & 0x07) << 7) | b1,
        "a": ((b0 & BIT_FASE_A) != 0).astype(np.uint8),
        "b": ((b0 & BIT_FASE_B) != 0).astype(np.uint8),
        "motor": ((b0 & BANDERA_MOTOR) != 0).astype(np.uint8),
        "perdida": ((b0 & BANDERA_PERDIDA) != 0).astype(np.uint8),
    }
    return crudos, descartados


def empaquetar_rapida(adc, a, b, motor, perdida=None) -> bytes:
    """Inverso de decodificar_rapida (lo usan el simulador y las pruebas)."""
    adc = np.clip(np.asarray(adc), 0, 1023).astype(np.uint16)
    perdida = np.zeros_like(adc) if perdida is None else np.asarray(perdida)
    b0 = (0x80 | (np.asarray(perdida) != 0) * BANDERA_PERDIDA | (np.asarray(motor) != 0) * BANDERA_MOTOR
          | (np.asarray(b) != 0) * BIT_FASE_B | (np.asarray(a) != 0) * BIT_FASE_A | (adc >> 7))
    salida = np.empty(2 * len(adc), dtype=np.uint8)
    salida[0::2] = b0
    salida[1::2] = adc & 0x7F
    return salida.tobytes()


def guardar_captura_rapida(base: Path, datos: bytes, encabezado: dict, resumen: str) -> dict:
    """Guarda una captura rápida: <base>.bin (bytes tal cual llegaron),
    <base>_crudo.csv (datos brutos decodificados) y <base>.json (configuración).
    Devuelve el diccionario de metadatos."""
    base = Path(base)
    base.parent.mkdir(parents=True, exist_ok=True)
    base.with_suffix(".bin").write_bytes(bytes(datos))
    crudos, descartados = decodificar_rapida(datos)
    fs = float(encabezado.get("fs_hz", 38461.538))
    n = np.arange(len(crudos["adc"]))
    tabla = np.column_stack([n, n / fs, crudos["motor"], crudos["adc"], crudos["a"], crudos["b"], crudos["perdida"]])
    np.savetxt(base.with_name(base.name + "_crudo.csv"), tabla, delimiter=",",
               header="n,t_s,motor,adc,fase_a,fase_b,perdida", comments="",
               fmt=["%d", "%.7f", "%d", "%d", "%d", "%d", "%d"])
    meta = {
        "tipo": "captura_rapida",
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
        "encabezado": encabezado,
        "resumen_arduino": resumen,
        "tramas_recibidas": int(len(n)),
        "bytes_descartados": int(descartados),
        "marcas_de_perdida": int(crudos["perdida"].sum()),
        "formato_trama": "b0 = 1 P M B A C9 C8 C7 | b1 = 0 C6..C0",
    }
    base.with_suffix(".json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def cargar_captura_rapida(base: Path) -> tuple[dict, dict]:
    """Lee <base>.bin y <base>.json. Devuelve (crudos, meta)."""
    base = Path(base)
    if base.suffix in (".bin", ".json"):
        base = base.with_suffix("")
    meta = json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))
    crudos, _ = decodificar_rapida(base.with_suffix(".bin").read_bytes())
    return crudos, meta


# =============================================================================
#  Tiempo real
# =============================================================================
@dataclass
class Telemetria:
    k: int
    cuenta: int
    referencia: float
    velocidad: float
    voltaje: float
    adc: float          # Promedio del ADC en el periodo (cuentas, 0 a 1023)
    modo: int
    estado: int


def empaquetar_telemetria(k, cuenta, ref, vel, u, adc, modo, estado) -> bytes:
    """Construye una trama de 27 bytes igual a la del Arduino."""
    datos = TELEMETRIA.pack(k & 0xFFFFFFFF, int(cuenta), ref, vel, u,
                            int(min(65535, max(0, adc * 16 + 0.5))), modo, estado)
    return SYNC + datos + bytes([sum(datos) & 0xFF])


class ParserTiempoReal:
    """Separa el flujo de bytes del modo de tiempo real en tramas y líneas de texto."""

    def __init__(self):
        self.buffer = bytearray()
        self.tramas_malas = 0

    def alimentar(self, datos: bytes) -> list:
        """Devuelve una lista de eventos ('telem', Telemetria) o ('texto', str)."""
        self.buffer += datos
        eventos, buf, i, n = [], self.buffer, 0, len(self.buffer)
        while i < n:
            c = buf[i]
            if c == 0xA5:
                if i + LARGO_TRAMA > n:
                    break                                  # Trama incompleta: esperar
                if buf[i + 1] == 0x5A:
                    cuerpo = bytes(buf[i + 2:i + 2 + TELEMETRIA.size])
                    if (sum(cuerpo) & 0xFF) == buf[i + LARGO_TRAMA - 1]:
                        k, cuenta, r, w, u, adc16, modo, estado = TELEMETRIA.unpack(cuerpo)
                        eventos.append(("telem", Telemetria(k, cuenta, r, w, u, adc16 / 16.0, modo, estado)))
                        i += LARGO_TRAMA
                        continue
                self.tramas_malas += 1
                i += 1
            elif c == 0x23:                                  # '#': línea de texto
                fin = buf.find(b"\n", i, i + 400)
                if fin < 0:
                    if n - i >= 400:                        # Demasiado larga: no era texto
                        i += 1
                        continue
                    break                                   # Línea incompleta: esperar
                linea = bytes(buf[i:fin]).rstrip(b"\r")
                if all(0x20 <= ch <= 0x7E for ch in linea):
                    eventos.append(("texto", linea.decode("ascii")))
                    i = fin + 1
                else:
                    i += 1                                  # Basura que empezaba con '#'
            else:
                i += 1
        del self.buffer[:i]
        return eventos


# =============================================================================
#  Órdenes
# =============================================================================
def texto_orden(letra: str, *valores) -> str:
    """texto_orden('K', 0.1, 0.5, 0.001) -> 'K 0.1 0.5 0.001'"""
    partes = [letra] + [f"{v:.6g}" if isinstance(v, float) else str(int(v)) for v in valores]
    return " ".join(partes)


def suma_verificacion(texto: str) -> str:
    """Suma de los bytes módulo 256, en hexadecimal (ver la sección 8 del .ino)."""
    return f"{sum(texto.encode('ascii')) & 0xFF:02X}"


def orden(letra: str, *valores) -> bytes:
    """orden('K', 0.1, 0.5, 0.001) -> b'K 0.1 0.5 0.001*HH' + salto de línea.

    HH es la suma de verificación. A alta velocidad el Arduino a veces pierde un byte
    de lo que recibe; con la suma, una orden dañada se rechaza en vez de
    aplicarse con otro valor.
    """
    texto = texto_orden(letra, *valores)
    return f"{texto}*{suma_verificacion(texto)}\n".encode("ascii")


def decimacion_telemetria(ts_ms: float, intervalo_ms: float = 10.0) -> int:
    """Cada cuántos periodos enviar telemetría para que haya una trama cada
    ~10 ms. El adaptador FTDI del Nano entrega los datos a la computadora
    cuando hay una pausa de ~16 ms; con tramas cada 2 ms nunca hay pausa y el
    driver junta bloques de 4 KB: la app veía el motor con ~0,3 s de atraso
    (medido el 22/11/2026)."""
    return max(1, min(255, int(round(intervalo_ms / max(ts_ms, 0.1)))))


# =============================================================================
#  Enlace serie con hilo de lectura
# =============================================================================
class EnlaceSerie:
    """Lee el puerto en un hilo y deja los eventos en self.eventos (queue.Queue).

    Eventos: ('telem', Telemetria) · ('texto', str) · ('captura', dict) ·
             ('progreso', fracción) · ('error', str) · ('desconectado', None)

    'puerto' puede ser un serial.Serial o cualquier objeto con read(), write(),
    in_waiting y close() (por ejemplo el Arduino simulado).
    """

    def __init__(self, puerto):
        self.puerto = puerto
        self.eventos: queue.Queue = queue.Queue()
        self.parser = ParserTiempoReal()
        self._vivo = True
        self._bloqueo = threading.Lock()
        self._en_captura = False
        self._captura = None
        self.bytes_recibidos = 0
        self.reintentos = 0                       # Órdenes que hubo que reenviar
        self._respuestas = []                     # Últimas líneas "# OK ..." / "# ERR ..."
        self._hay_respuesta = threading.Condition()
        self._hilo = threading.Thread(target=self._leer, daemon=True)
        self._hilo.start()

    @classmethod
    def abrir(cls, nombre: str, baudios: int = BAUDIOS) -> "EnlaceSerie":
        import serial  # pyserial
        puerto = serial.Serial(nombre, baudios, timeout=0.05)
        if hasattr(puerto, "set_buffer_size"):
            try:
                puerto.set_buffer_size(rx_size=1 << 20, tx_size=4096)   # Solo en Windows
            except Exception:
                pass
        return cls(puerto)

    def enviar(self, datos: bytes):
        with self._bloqueo:
            self.puerto.write(datos)

    def enviar_confirmado(self, letra: str, *valores, intentos: int = 4, espera: float = 0.5) -> bool:
        """Envía una orden y espera "# OK <orden>". Si no llega (o llega otra
        cosa, porque se perdió un byte), la reenvía. Devuelve True si se confirmó.
        La espera es larga a propósito: el driver FTDI de Windows retiene los
        datos hasta ~0,3 s cuando la telemetría llega sin pausas (ver
        decimacion_telemetria()).
        No sirve para '?', 'H' ni 'E', que no responden "# OK"."""
        esperado = "# OK " + texto_orden(letra, *valores)
        datos = orden(letra, *valores)
        for intento in range(intentos):
            with self._hay_respuesta:
                self._respuestas.clear()
            if intento:
                self.reintentos += 1
            self.enviar(datos)
            limite = time.time() + espera
            with self._hay_respuesta:
                while True:
                    if esperado in self._respuestas:
                        return True
                    resto = limite - time.time()
                    if resto <= 0:
                        break
                    self._hay_respuesta.wait(resto)
        return False

    def _anotar_respuestas(self, eventos):
        """Guarda las respuestas "# OK" / "# ERR" para enviar_confirmado()."""
        for tipo, valor in eventos:
            if tipo == "texto" and (valor.startswith("# OK ") or valor.startswith("# ERR")):
                with self._hay_respuesta:
                    self._respuestas.append(valor)
                    del self._respuestas[:-50]
                    self._hay_respuesta.notify_all()

    @property
    def en_captura(self) -> bool:
        """True mientras llega una captura rápida."""
        return self._en_captura

    def iniciar_captura(self):
        """Envía 'E' y cambia el lector al modo de captura rápida."""
        self._captura = {"estado": "esperando", "datos": bytearray(), "encabezado": None,
                         "inicio": time.time()}
        self._en_captura = True
        self.enviar(b"E\n")

    def cerrar(self):
        self._vivo = False
        try:
            self._hilo.join(timeout=1.0)
        except RuntimeError:
            pass
        try:
            self.puerto.close()
        except Exception:
            pass

    # --- Hilo ---
    def _leer(self):
        while self._vivo:
            try:
                n = self.puerto.in_waiting
                bloque = self.puerto.read(n if n > 0 else 1)
            except Exception as e:      # Puerto desconectado
                self.eventos.put(("error", f"Error al leer el puerto: {e}"))
                self.eventos.put(("desconectado", None))
                return
            if not bloque:
                if self._en_captura and time.time() - self._captura["inicio"] > 90:
                    self.eventos.put(("error", "Tiempo agotado esperando la captura rápida"))
                    self._en_captura = False
                continue
            self.bytes_recibidos += len(bloque)
            if self._en_captura:
                self._leer_captura(bloque)
            else:
                eventos = self.parser.alimentar(bloque)
                self._anotar_respuestas(eventos)
                for ev in eventos:
                    self.eventos.put(ev)

    def _leer_captura(self, bloque: bytes):
        cap = self._captura
        cap["datos"] += bloque
        datos = cap["datos"]
        if cap["estado"] == "esperando":
            j = datos.find(b"INICIO ")
            if j < 0:
                del datos[:max(0, len(datos) - 8)]          # Telemetría vieja: se descarta
                return
            fin_linea = datos.find(b"\n", j)
            if fin_linea < 0:
                return
            cap["encabezado"] = leer_parametros(datos[j:fin_linea].decode("ascii", "replace"))
            del datos[:fin_linea + 1]
            cap["estado"] = "datos"
            cap["total_bytes"] = 2 * int(cap["encabezado"].get("n_total", 1))
        if cap["estado"] == "datos":
            k = datos.find(MARCADOR_FIN, max(0, len(datos) - len(bloque) - 16))
            if k < 0:
                fraccion = min(1.0, len(datos) / cap["total_bytes"])
                if fraccion - cap.get("ultimo_progreso", -1.0) >= 0.02:
                    cap["ultimo_progreso"] = fraccion
                    self.eventos.put(("progreso", fraccion))
                return
            fin_linea = datos.find(b"\n", k + len(MARCADOR_FIN))
            if fin_linea < 0:
                return
            resumen = datos[k + 5:fin_linea].decode("ascii", "replace").strip()
            binario = bytes(datos[:k])
            resto = bytes(datos[fin_linea + 1:])
            self._en_captura = False
            self.eventos.put(("captura", {"datos": binario, "encabezado": cap["encabezado"],
                                          "resumen": resumen}))
            eventos = self.parser.alimentar(resto)
            self._anotar_respuestas(eventos)
            for ev in eventos:
                self.eventos.put(ev)
