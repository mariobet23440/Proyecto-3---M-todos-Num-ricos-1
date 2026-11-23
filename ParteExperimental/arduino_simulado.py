"""
Arduino simulado: imita a MotorDC_L298N.ino con el modelo del motor.

Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
Fecha de creación: 22/11/2026
Autores: Mario Alejandro Betancourt Franco (23440)
         Claude Opus 5.5 (Anthropic), asistente de IA

Se comporta como un puerto serie (read, write, in_waiting, close): recibe las
mismas órdenes y devuelve los mismos bytes que el Arduino (telemetría, texto y
captura rápida). Sirve para probar la aplicación y el receptor sin hardware.
El "motor real" de la simulación es el modelo de modelo_motor.py con ruido en
el ADC; no reemplaza una medición.

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md).
"""
from __future__ import annotations

import math
import random
import threading
import time

import numpy as np

from modelo_motor import GemeloDigital, ParametrosMotor, voltaje_motor
from protocolo_motor import empaquetar_rapida, empaquetar_telemetria, suma_verificacion

FS_RAPIDA = 16e6 / 32 / 13
ESTADOS_CUADRATURA = (0, 2, 3, 1)   # Estado (A<<1)|B para cuenta mod 4 (sentido +1 de la tabla)


class ArduinoSimulado:
    def __init__(self, p: ParametrosMotor | None = None, ppr: float = 11.0, cero_adc: float = 511.6,
                 ruido_adc: float = 2.5, vref: float = 5.0, sensibilidad: float = 0.185):
        self.p = p or ParametrosMotor()
        self.ppr, self.cero, self.ruido = ppr, cero_adc, ruido_adc
        self.cuentas_adc_por_A = sensibilidad * 1024.0 / vref
        self.motor = GemeloDigital(self.p, "RK4", 2.5e-4)
        self._salida = bytearray()
        self._bloqueo = threading.Lock()
        self._entrada = ""
        self._vivo = True
        self._ocupado = False
        # Estado del "firmware"
        self.modo, self.kp, self.ki, self.kd = 0, 0.05, 0.0, 0.0
        self.ts_ms, self.tau_ms, self.cpr, self.vbus = 2.0, 8.0, 44.0, self.p.v_bus
        self.aw = True
        self.inv_enc = False
        self.ref = (0, 0.0, 0.0, 0.0)
        self.decimacion = 1
        self.cap = [255, 1, 0, 200, 1500, 1500]
        self._reiniciar_estado()
        self._ultima_orden = time.time()
        self._escribir_texto("# LISTO Motor JGA25-370 con L298N (SIMULADO). Ordenes: ? H X M K T F P R A I S Z C E")
        self._escribir_cfg()
        self._hilo = threading.Thread(target=self._correr, daemon=True)
        self._hilo.start()

    # --- Interfaz de puerto serie ---
    @property
    def in_waiting(self):
        with self._bloqueo:
            return len(self._salida)

    def read(self, n=1):
        fin = time.time() + 0.05
        while self._vivo:
            with self._bloqueo:
                if self._salida:
                    datos = bytes(self._salida[:n])
                    del self._salida[:n]
                    return datos
            if time.time() > fin:
                return b""
            time.sleep(0.002)
        return b""

    def write(self, datos: bytes):
        self._ultima_orden = time.time()
        self._entrada += datos.decode("ascii", "replace")
        while "\n" in self._entrada:
            linea, self._entrada = self._entrada.split("\n", 1)
            linea = linea.strip()
            if linea:
                self._orden(linea)
        return len(datos)

    def close(self):
        self._vivo = False

    # --- Salida ---
    def _escribir(self, datos: bytes):
        with self._bloqueo:
            self._salida += datos

    def _escribir_texto(self, linea: str):
        self._escribir((linea + "\n").encode("ascii", "replace"))

    def _escribir_cfg(self):
        tipo, amp, off, f = self.ref
        self._escribir_texto(
            f"# CFG modo={self.modo} kp={self.kp:.6f} ki={self.ki:.6f} kd={self.kd:.6f} ts_ms={self.ts_ms:.3f} "
            f"tau_ms={self.tau_ms:.3f} cpr={self.cpr:.3f} vbus={self.vbus:.3f} aw={int(self.aw)} "
            f"ref_tipo={tipo} ref_amp={amp:.4f} ref_off={off:.4f} "
            f"ref_f={f:.4f} decimacion={self.decimacion} cap_pwm={self.cap[0]} cap_sentido={self.cap[1]} "
            f"cap_freno={self.cap[2]} cap_t0={self.cap[3]} cap_t1={self.cap[4]} cap_t2={self.cap[5]} "
            f"fs_rapida_hz={FS_RAPIDA:.3f} f_pwm_hz=490.2")

    # --- Órdenes (igual que la sección 8 del .ino) ---
    def _orden(self, linea: str):
        if "*" in linea:                                   # Suma de verificación (sección 8 del .ino)
            cuerpo, _, suma = linea.partition("*")
            if suma.strip().upper() != suma_verificacion(cuerpo):
                self._escribir_texto("# ERR SUMA " + cuerpo); return
            linea = cuerpo.strip()
        if not linea:
            return
        letra = linea[0].upper()
        try:
            v = [float(x) for x in linea[1:].split()]
        except ValueError:
            v = []
        ok = True
        if letra == "?":
            self._escribir_cfg(); return
        if letra == "H":
            return
        if letra == "X":
            self.modo = 0; self._reiniciar_pid()
        elif letra == "M" and v and 0 <= v[0] <= 3:
            self.modo = int(v[0]); self._reiniciar_pid(); self.k = 0; self.k_ref = 0
        elif letra == "K" and len(v) >= 3:
            self.kp, self.ki, self.kd = v[:3]
        elif letra == "T" and v and 0.5 <= v[0] <= 250:
            self.ts_ms = v[0]; self._reiniciar_pid(); self._t_inicio = time.time(); self._ticks = 0
        elif letra == "F" and v and v[0] >= 0:
            self.tau_ms = v[0]
        elif letra == "P" and len(v) >= 2 and v[0] > 0 and v[1] > 0:
            self.cpr, self.vbus = v[0], v[1]
        elif letra == "R" and len(v) >= 4 and 0 <= v[0] <= 3:
            self.ref = (int(v[0]), v[1], v[2], v[3]); self.k_ref = 0
        elif letra == "A" and v:
            self.aw = v[0] != 0
        elif letra == "I" and v:
            self.inv_enc = v[0] != 0
            self.cuenta_cero = self._cuenta_bruta(); self.cuenta_ant = 0; self.vel = 0.0; self._reiniciar_pid()
        elif letra == "S" and v and 0 <= v[0] <= 255:
            self.decimacion = int(v[0])
        elif letra == "Z":
            self.cuenta_cero = self._cuenta_bruta(); self.cuenta_ant = 0; self._reiniciar_pid()
        elif letra == "C" and len(v) >= 6:
            self.cap = [int(v[0]), 1 if v[1] >= 0 else -1, int(v[2] != 0), int(v[3]), int(v[4]), int(v[5])]
        elif letra == "E":
            self._ocupado = True
            threading.Thread(target=self._captura_rapida, daemon=True).start()
            return
        else:
            ok = False
        self._escribir_texto(("# OK " if ok else "# ERR ") + linea)

    def _reiniciar_pid(self):
        self.E, self.e_ant = 0.0, 0.0

    def _reiniciar_estado(self):
        self._reiniciar_pid()
        self.k = self.k_ref = 0
        self.cuenta_cero = self._cuenta_bruta()
        self.cuenta_ant = 0
        self.vel = 0.0
        self.u_aplicado, self.abierto = 0.0, True
        self._t_inicio, self._ticks = time.time(), 0

    def _cuenta_bruta(self):
        return math.floor(self.motor.x[2] * 4 * self.ppr / (2 * math.pi))

    def _referencia(self, t):
        tipo, amp, off, f = self.ref
        if tipo == 0:
            return off
        c = (f * t) % 1.0
        forma = math.sin(2 * math.pi * c) if tipo == 1 else (1.0 if c < 0.5 else -1.0) if tipo == 2 \
            else 1.0 - 4.0 * abs(c - 0.5)
        return off + amp * forma

    # --- Lazo de tiempo real ---
    def _correr(self):
        while self._vivo:
            time.sleep(0.005)
            if self._ocupado:
                continue
            if self.modo != 0 and time.time() - self._ultima_orden > 2.0:
                self.modo = 0; self._reiniciar_pid()
                self._escribir_texto("# AVISO sin comunicacion: motor en reposo")
            debidos = int((time.time() - self._t_inicio) / (self.ts_ms / 1000)) - self._ticks
            for _ in range(min(debidos, 200)):
                self._paso()
                self._ticks += 1
            if debidos > 200:
                self._t_inicio, self._ticks = time.time(), 0

    def _paso(self):
        ts = self.ts_ms / 1000
        self.motor.avanzar(ts, self.u_aplicado, self.abierto)
        cuenta = self._cuenta_bruta() - self.cuenta_cero
        if self.inv_enc:
            cuenta = -cuenta
        q = 2 * math.pi / self.cpr
        vel_cruda = (cuenta - self.cuenta_ant) * q / ts
        self.cuenta_ant = cuenta
        alfa = ts / (ts + self.tau_ms / 1000)
        self.vel += alfa * (vel_cruda - self.vel)
        n_adc = max(1, int(9615 * ts))
        adc = self.cero + self.motor.corriente * self.cuentas_adc_por_A + random.gauss(0, self.ruido / math.sqrt(n_adc))
        r = self._referencia(self.k_ref * ts)
        u, estado = 0.0, 0
        if self.modo == 1:
            u = r
        elif self.modo in (2, 3):
            y = self.vel if self.modo == 2 else cuenta * q
            e = r - y
            nuevo = self.E + e
            gi = self.ki * ts                                  # u = Kp e + Ki Ts E + (Kd/Ts) Δe
            pd = self.kp * e + (self.kd / ts) * (e - self.e_ant)
            u = pd + gi * nuevo
            if self.aw and abs(u) > self.vbus and (u > 0) == (e > 0):
                u = pd + gi * self.E
                estado |= 8
            else:
                self.E = nuevo
            self.e_ant = e
        if abs(u) > self.vbus:
            u = math.copysign(self.vbus, u); estado |= 1
        pwm = round(min(255.0, abs(u) / self.vbus * 255))
        self.abierto = self.modo == 0 or pwm == 0
        self.u_aplicado = 0.0 if self.abierto else math.copysign(pwm / 255 * self.vbus, u)
        if self.decimacion and self.k % self.decimacion == 0:
            self._escribir(empaquetar_telemetria(self.k, cuenta, r, self.vel, u, adc, self.modo, estado))
        self.k += 1
        self.k_ref += 1

    # --- Captura rápida ---
    def _captura_rapida(self):
        pwm, sentido, freno, t0, t1, t2 = self.cap
        n = [max(1, int(t * FS_RAPIDA / 1000)) for t in (t0, t1, t2)]
        total = sum(n)
        self.modo = 0
        self._escribir_texto(
            f"INICIO fs_hz={FS_RAPIDA:.3f} n_previas={n[0]} n_encendido={n[1]} n_apagado={n[2]} n_total={total} "
            f"prescaler_adc=32 baudios=1000000 pwm={pwm} f_pwm_hz=490.2 sentido={sentido} freno={freno}")
        h = 1 / FS_RAPIDA
        p = self.p
        v_on = voltaje_motor(sentido * pwm / 255 * self.vbus, p)
        i, w, th = self.motor.x
        corriente, angulo = np.empty(total), np.empty(total)
        motor = np.zeros(total, dtype=np.uint8)
        motor[n[0]:n[0] + n[1]] = 1
        for k in range(total):              # Euler con h = 1/fs (13 µs, estable para L/R)
            corriente[k], angulo[k] = i, th
            fric = p.tau_c * math.tanh(w / p.eps)
            if motor[k]:
                di = (v_on - p.R * i - p.Ke * w) / p.L
            elif k >= n[0] and freno:
                di = (0.0 - p.R * i - p.Ke * w) / p.L
            else:
                di, i = 0.0, 0.0
            dw = (p.Kt * i - p.b * w - fric - p.tau_carga) / p.J
            i, w, th = i + h * di, w + h * dw, th + h * w
        self.motor.x = (0.0, w, th)
        cuenta = np.floor(angulo * 4 * self.ppr / (2 * np.pi)).astype(np.int64)
        s = np.take(ESTADOS_CUADRATURA, np.mod(cuenta, 4))
        adc = np.round(self.cero + corriente * self.cuentas_adc_por_A + np.random.normal(0, self.ruido, total))
        datos = empaquetar_rapida(adc, s >> 1, s & 1, motor)
        for j in range(0, len(datos), 16384):              # A unos 160 kB/s, como el UART real
            self._escribir(datos[j:j + 16384])
            time.sleep(0.1)
        self._escribir(b"\xff\xff\xff\xff\nFIN tramas_enviadas=%d tramas_perdidas=0\n" % total)
        self._escribir_texto("# AVISO la cuenta del encoder se reinicio a 0 despues de la captura")
        self._reiniciar_estado()
        self._ocupado = False
