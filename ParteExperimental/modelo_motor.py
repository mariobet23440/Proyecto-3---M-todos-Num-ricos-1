"""
Modelo del motor DC para el gemelo digital (mismas ecuaciones que el cuaderno).

Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
Fecha de creación: 22/11/2026
Autores: Mario Alejandro Betancourt Franco (23440)
         Claude Opus 5.5 (Anthropic), asistente de IA

    L di/dt   = V - R i - Ke ω
    J dω/dt   = Kt i - b ω - τc sign(ω) - τcarga
    dθ/dt     = ω

ω y θ son del eje del MOTOR. El eje de salida de la caja reductora gira N
veces más lento: ω_salida = ω / N. sign(ω) se suaviza con tanh(ω / ε) para que
el lado derecho sea continuo (y Lipschitz), como en la sección 1.4 del cuaderno.

Cuando el L298N deja el motor libre (ENB = 0) el circuito queda abierto y la
corriente se toma como cero: es una aproximación (la corriente real se descarga
por los diodos del módulo en una fracción de milisegundo).

AVISO: los valores de ParametrosMotor son de EJEMPLO, salvo R = 6 Ω (el peor
caso que indicó el autor). L = 2 mH es supuesto. Deben reemplazarse por los
que se identifiquen con los ensayos. Código generado con IA (UsoIA/BitacoraUsoIA.md).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np


@dataclass
class ParametrosMotor:
    R: float = 6.0          # Ω   (peor caso indicado por el autor)
    L: float = 2e-3         # H   (SUPUESTO)
    Ke: float = 0.012       # V/(rad/s)        (ejemplo)
    Kt: float = 0.012       # N·m/A            (ejemplo)
    J: float = 5e-7         # kg·m²            (ejemplo)
    b: float = 1e-6         # N·m·s/rad        (ejemplo)
    tau_c: float = 2e-4     # N·m, fricción de Coulomb (ejemplo)
    eps: float = 1.0        # rad/s, suavizado de sign(ω)
    tau_carga: float = 0.0  # N·m
    N: float = 1.0          # Reducción de la caja (1 = se mide el eje del motor)
    v_bus: float = 12.0     # V, fuente del L298N
    v_caida: float = 2.0    # V, caída interna del L298N (medir)

    def a_dict(self) -> dict:
        return asdict(self)


def voltaje_motor(u: float, p: ParametrosMotor) -> float:
    """Voltaje medio en el motor para un voltaje pedido u (= ciclo · v_bus)."""
    u = max(-p.v_bus, min(p.v_bus, u))
    return u * (p.v_bus - p.v_caida) / p.v_bus


def derivadas(x, v, p: ParametrosMotor, abierto: bool = False):
    """Lado derecho f(x) del sistema. x = [i, ω, θ] (eje del motor)."""
    i, w, _ = x
    friccion = p.tau_c * math.tanh(w / p.eps)
    if abierto:
        return (0.0, (-p.b * w - friccion - p.tau_carga) / p.J, w)
    di = (v - p.R * i - p.Ke * w) / p.L
    dw = (p.Kt * i - p.b * w - friccion - p.tau_carga) / p.J
    return (di, dw, w)


def paso_euler(x, v, h, p, abierto=False):
    d = derivadas(x, v, p, abierto)
    return (0.0 if abierto else x[0] + h * d[0], x[1] + h * d[1], x[2] + h * d[2])


def paso_rk4(x, v, h, p, abierto=False):
    k1 = derivadas(x, v, p, abierto)
    x2 = tuple(x[j] + 0.5 * h * k1[j] for j in range(3))
    k2 = derivadas(x2, v, p, abierto)
    x3 = tuple(x[j] + 0.5 * h * k2[j] for j in range(3))
    k3 = derivadas(x3, v, p, abierto)
    x4 = tuple(x[j] + h * k3[j] for j in range(3))
    k4 = derivadas(x4, v, p, abierto)
    nuevo = tuple(x[j] + h / 6.0 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]) for j in range(3))
    return (0.0, nuevo[1], nuevo[2]) if abierto else nuevo


METODOS = {"Euler": paso_euler, "RK4": paso_rk4}


class GemeloDigital:
    """Integra el modelo en tiempo real con el voltaje que se aplica al motor."""

    def __init__(self, p: ParametrosMotor, metodo: str = "RK4", h: float = 1e-4):
        self.p, self.metodo, self.h = p, metodo, h
        self.x = (0.0, 0.0, 0.0)

    def reiniciar(self, theta_salida: float = 0.0, omega_salida: float = 0.0):
        self.x = (0.0, omega_salida * self.p.N, theta_salida * self.p.N)

    def avanzar(self, dt: float, u: float, abierto: bool = False):
        """Avanza dt segundos con el voltaje pedido u (V) constante."""
        paso = METODOS[self.metodo]
        v = voltaje_motor(u, self.p)
        n = max(1, int(math.ceil(dt / self.h)))
        h = dt / n
        x = self.x
        for _ in range(n):
            x = paso(x, v, h, self.p, abierto)
        if not all(math.isfinite(c) for c in x):      # Euler inestable con h grande
            x = (0.0, 0.0, 0.0)
        self.x = x

    @property
    def corriente(self):
        return self.x[0]

    @property
    def omega_salida(self):
        return self.x[1] / self.p.N

    @property
    def theta_salida(self):
        return self.x[2] / self.p.N


def simular(t: np.ndarray, u: np.ndarray, abierto: np.ndarray, p: ParametrosMotor,
            metodo: str = "RK4", h: float = 1e-4) -> dict:
    """Simula sobre la malla t (uniforme) con u y abierto por muestra.
    Devuelve {'i', 'omega', 'theta'} del eje de salida."""
    g = GemeloDigital(p, metodo, h)
    salida = {k: np.zeros(len(t)) for k in ("i", "omega", "theta")}
    for k in range(len(t)):
        salida["i"][k], salida["omega"][k], salida["theta"][k] = g.corriente, g.omega_salida, g.theta_salida
        if k + 1 < len(t):
            g.avanzar(t[k + 1] - t[k], float(u[k]), bool(abierto[k]))
    return salida
