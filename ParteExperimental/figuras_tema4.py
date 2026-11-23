"""
Gráficas de la serie de ensayos del tema 4 (datos reales del 22/11/2026).

Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
Fecha de creación: 22/11/2026
Autores: Mario Alejandro Betancourt Franco (23440)
         Claude Opus 5.5 (Anthropic), asistente de IA

Lee las capturas de <carpeta>/a_escalones, b_desaceleracion y c_pid y guarda
las figuras en <carpeta>/figuras. No hace ningún ajuste de parámetros: solo
grafica lo medido (el ajuste del modelo es trabajo del equipo).

Uso:
    python figuras_tema4.py datos/tema4_20261122

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md).
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from protocolo_motor import cargar_captura_rapida
from postprocesamiento import procesar

COLORES = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]


def cargar(base):
    crudos, meta = cargar_captura_rapida(base)
    res, resumen = procesar(crudos, meta, invertir_encoder=True)   # En el montaje del equipo el encoder cuenta al revés
    return res, resumen, meta


def figura_escalones(carpeta, destino):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for color, pwm in zip(COLORES, (64, 115, 166, 217, 255)):
        base = carpeta / "a_escalones" / f"escalon_pwm{pwm:03d}_r1"
        if not base.with_suffix(".json").exists():
            continue
        r, s, _ = cargar(base)
        t = r["t_s"] - r["t_s"][s["k_escalon"]]
        a1.plot(t, r["omega_flancos_rad_s"], color=color, lw=1.2, label=f"PWM {pwm} ({100 * pwm / 255:.0f} %)")
        a2.plot(t, r["corriente_suave_A"], color=color, lw=1.0)
    a1.set_ylabel("ω eje del motor [rad/s]")
    a2.set_ylabel("i [A] (promedio móvil 0,5 ms)")
    a2.set_xlabel("t desde el escalón [s]")
    a1.legend(loc="lower right")
    a1.set_title("(a) Respuesta al escalón a 5 niveles de PWM · L298N, 12 V, motor sin carga")
    for a in (a1, a2):
        a.grid(alpha=0.3)
        a.axvline(0, color="k", lw=0.6, ls="--")
    fig.tight_layout()
    fig.savefig(destino / "a_escalones.png", dpi=130)
    plt.close(fig)


def figura_desaceleracion(carpeta, destino):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for color, (nombre, etiqueta) in zip(COLORES, (("libre_pwm255_r1", "libre desde PWM 255"),
                                                   ("libre_pwm166_r1", "libre desde PWM 166"),
                                                   ("freno_pwm255_r1", "freno dinámico desde PWM 255"))):
        base = carpeta / "b_desaceleracion" / nombre
        if not base.with_suffix(".json").exists():
            continue
        r, s, _ = cargar(base)
        t = r["t_s"] - r["t_s"][s["k_desconexion"]]
        sel = t > -0.2
        ax.plot(t[sel], r["omega_flancos_rad_s"][sel], color=color, lw=1.2, label=etiqueta)
    ax.axvline(0, color="k", lw=0.6, ls="--")
    ax.set_xlabel("t desde la desconexión [s]")
    ax.set_ylabel("ω eje del motor [rad/s]")
    ax.set_title("(b) Desaceleración libre y con freno dinámico")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(destino / "b_desaceleracion.png", dpi=130)
    plt.close(fig)


def figura_pid(carpeta, destino):
    casos = (("velocidad_cuadrada_200_400", "vel"), ("velocidad_cuadrada_50_150", "vel"),
             ("velocidad_cuadrada_menos200_200", "vel"), ("posicion_cuadrada_1vuelta", "pos"),
             ("posicion_cuadrada_5vueltas", "pos"), ("posicion_seno_5vueltas", "pos"))
    fig, ejes = plt.subplots(len(casos), 1, figsize=(10, 2.3 * len(casos)))
    for ax, (nombre, modo) in zip(ejes, casos):
        archivo = carpeta / "c_pid" / f"{nombre}.csv"
        if not archivo.exists():
            ax.set_visible(False)
            continue
        x = np.loadtxt(archivo, delimiter=",", skiprows=1)
        t, ref = x[:, 0], x[:, 4]
        y = x[:, 5] if modo == "vel" else x[:, 3]
        ax.plot(t, ref, color="#2ca02c", lw=1.2, label="referencia")
        ax.plot(t, y, color="#1f77b4", lw=1.0, label="medida")
        ax2 = ax.twinx()
        ax2.plot(t, x[:, 6], color="#ff7f0e", lw=0.6, alpha=0.6)
        ax2.set_ylabel("u [V]", color="#ff7f0e")
        ax.set_ylabel("ω [rad/s]" if modo == "vel" else "θ [rad]")
        ax.set_title(nombre.replace("_", " "), fontsize=9)
        ax.grid(alpha=0.3)
    ejes[0].legend(loc="upper right", fontsize=8)
    ejes[-1].set_xlabel("t [s]")
    fig.tight_layout()
    fig.savefig(destino / "c_pid.png", dpi=120)
    plt.close(fig)


def main():
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else "datos/tema4_20261122")
    destino = carpeta / "figuras"
    destino.mkdir(exist_ok=True)
    figura_escalones(carpeta, destino)
    figura_desaceleracion(carpeta, destino)
    figura_pid(carpeta, destino)
    print(f"Figuras en {destino}")


if __name__ == "__main__":
    main()
