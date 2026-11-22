"""
Corre las simulaciones LTspice del driver del motor y genera las figuras del reporte.

Proyecto 3 - Métodos Numéricos 1 · UVG · 22/11/2026
Autores: Mario Alejandro Betancourt Franco (23440) y Claude Opus 5.5 (Anthropic, IA)
AVISO: script generado con IA (ver UsoIA/BitacoraUsoIA.md).

Uso (desde esta carpeta):
    python correr_simulaciones.py
    python correr_simulaciones.py --ltspice "C:\\ruta\\LTspice.exe"

Genera:
    figuras/*.png              formas de onda
    resultados_mediciones.md   tabla con todas las mediciones .meas
Requiere: LTspice, numpy y matplotlib.
"""
import argparse
import math
import os
import re
import subprocess
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))

# Colores (paleta categórica por defecto, en orden fijo) y tinta del texto
AZUL, NARANJA, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TINTA, TINTA2, REJILLA = "#0b0b0b", "#52514e", "#e4e3df"

CASOS = [
    ("01_directo_5V", "Diseño elegido: 5 V directo", AZUL),
    ("02_npn_inversor", "Un NPN inversor", NARANJA),
    ("03_npn_inversor_pin_flotante", "Un NPN inversor, pin flotante", NARANJA),
    ("04_npn_pnp", "NPN + PNP (12 V)", AQUA),
    ("05_npn_pnp_pin_flotante", "NPN + PNP, pin flotante", AQUA),
    ("06_diodo_directa", "Modelo 1N540X: directa", None),
    ("07_diodo_capacitancia", "Modelo 1N540X: capacitancia", None),
    ("08_directo_pwm20k_50", "Diseño elegido, PWM 20 kHz, 50 %", AZUL),
    ("09_directo_pwm20k_95", "Diseño elegido, PWM 20 kHz, 95 %", AZUL),
    ("10_directo_pwm20k_95_schottky", "PWM 20 kHz, 95 %, diodo Schottky", AZUL),
    ("11_directo_pwm490Hz_95", "PWM 490 Hz, 95 %", AZUL),
]


def buscar_ltspice(ruta):
    candidatos = [ruta] if ruta else []
    local = os.environ.get("LOCALAPPDATA", "")
    candidatos += [
        os.path.join(local, "Programs", "ADI", "LTspice", "LTspice.exe"),
        r"C:\Program Files\ADI\LTspice\LTspice.exe",
        r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe",
    ]
    for c in candidatos:
        if c and os.path.isfile(c):
            return c
    sys.exit("No se encontró LTspice. Use --ltspice para indicar la ruta.")


def leer_texto(ruta):
    """Los .log de LTspice pueden venir en UTF-16 o en UTF-8."""
    crudo = open(ruta, "rb").read()
    if len(crudo) > 1 and crudo[1:2] == b"\x00":
        return crudo.decode("utf-16-le", errors="replace")
    return crudo.decode("utf-8", errors="replace")


def leer_mediciones(ruta_log):
    """Devuelve {nombre: valor} de las líneas 'nombre: ...=valor ...' del .log."""
    med = {}
    for linea in leer_texto(ruta_log).splitlines():
        m = re.match(r"^(\w+):\s.*?=\(([-+0-9.eE]+)dB", linea.strip())
        if m:  # medición de AC en dB: se convierte a magnitud lineal
            med[m.group(1).lower()] = 10 ** (float(m.group(2)) / 20)
            continue
        m = re.match(r"^(\w+):\s.*?=\s*([-+0-9.eE]+)", linea.strip())
        if m:
            med[m.group(1).lower()] = float(m.group(2))
        m = re.match(r"^(\w+)=([-+0-9.eE]+)\s+FROM", linea.strip())  # mediciones TRIG/TARG
        if m:
            med[m.group(1).lower()] = float(m.group(2))
    return med


def leer_mediciones_paso(ruta_log, nombre):
    """Mediciones con .step: devuelve la lista de valores (dB convertidos a lineal)."""
    texto = leer_texto(ruta_log)
    bloque = texto.split("Measurement: " + nombre)[-1]
    valores = []
    for linea in bloque.splitlines()[2:]:
        m = re.match(r"^\s*\d+\s+\(?([-+0-9.eE]+)(dB)?", linea)
        if not m:
            break
        v = float(m.group(1))
        valores.append(10 ** (v / 20) if m.group(2) else v)
    return valores


def leer_raw(ruta):
    """Lee un .raw binario de LTspice (análisis transitorio, sin comprimir)."""
    crudo = open(ruta, "rb").read()
    utf16 = crudo[1:2] == b"\x00"
    marca = "Binary:\n".encode("utf-16-le" if utf16 else "ascii")
    i = crudo.find(marca)
    cabecera = crudo[:i].decode("utf-16-le" if utf16 else "latin-1")
    cuerpo = crudo[i + len(marca):]
    n_var = int(re.search(r"No\. Variables:\s*(\d+)", cabecera).group(1))
    n_pts = int(re.search(r"No\. Points:\s*(\d+)", cabecera).group(1))
    banderas = re.search(r"Flags:\s*(.*)", cabecera).group(1)
    nombres = re.findall(r"^\s*\d+\s+(\S+)\s+\S+\s*$",
                         cabecera.split("Variables:")[-1], re.M)[:n_var]
    if "double" in banderas:
        tipo = np.dtype([(n, "<f8") for n in nombres])
    else:
        tipo = np.dtype([(nombres[0], "<f8")] + [(n, "<f4") for n in nombres[1:]])
    datos = np.frombuffer(cuerpo[: n_pts * tipo.itemsize], dtype=tipo)
    salida = {n.lower(): np.asarray(datos[n], dtype=float) for n in nombres}
    salida["time"] = np.abs(salida["time"])
    return salida


def estilo(ax, titulo, xlabel, ylabel):
    ax.set_title(titulo, loc="left", fontsize=11, color=TINTA)
    ax.set_xlabel(xlabel, color=TINTA2)
    ax.set_ylabel(ylabel, color=TINTA2)
    ax.grid(True, color=REJILLA, linewidth=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(TINTA2)
    ax.tick_params(colors=TINTA2)


def guardar(fig, nombre):
    os.makedirs(os.path.join(AQUI, "figuras"), exist_ok=True)
    fig.savefig(os.path.join(AQUI, "figuras", nombre), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  figura:", nombre)


def figuras(ondas, med):
    lw = 1.6
    # --- 1. Escalón: Vgs y corriente del motor para los tres circuitos ---
    fig, ejes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for caso, titulo, color in [CASOS[0], CASOS[1], CASOS[3]]:
        o = ondas[caso]
        ejes[0].plot(o["time"] * 1e3, o["v(g)"], color=color, lw=lw, label=titulo)
        ejes[1].plot(o["time"] * 1e3, o["i(lm)"], color=color, lw=lw, label=titulo)
    o = ondas[CASOS[0][0]]
    ejes[0].plot(o["time"] * 1e3, o["v(d9)"], color=TINTA2, lw=1, ls="--", label="Pin D9 del Arduino")
    estilo(ejes[0], "Voltaje compuerta-fuente del IRFZ44N (pulso del pin de 0,1 a 1,1 ms)", "", "V_GS (V)")
    estilo(ejes[1], "Corriente del motor (motor de 6 Ω y 2 mH)", "Tiempo (ms)", "Corriente (A)")
    ejes[0].legend(frameon=False, fontsize=9, loc="upper right")
    guardar(fig, "01_escalon_comparacion.png")

    # --- 2. Conmutación: V_DS alineado al flanco que enciende y al que apaga ---
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.2))
    # (caso, t de encendido, t de apagado): el NPN inversor enciende al bajar el pin
    flancos = [(CASOS[0], 100e-6, 1100e-6), (CASOS[1], 1100e-6, 100e-6), (CASOS[3], 100e-6, 1100e-6)]
    for (caso, titulo, color), t_on, t_off in flancos:
        o = ondas[caso]
        for ax, t0, ventana in ((ejes[0], t_on, 3e-6), (ejes[1], t_off, 30e-6)):
            sel = (o["time"] >= t0 - 0.2 * ventana) & (o["time"] <= t0 + ventana)
            ax.plot((o["time"][sel] - t0) * 1e6, o["v(dr)"][sel], color=color, lw=lw, label=titulo)
    estilo(ejes[0], "Encendido: V_DS desde la orden del pin", "Tiempo desde la orden (µs)", "V_DS (V)")
    estilo(ejes[1], "Apagado: V_DS desde la orden del pin", "Tiempo desde la orden (µs)", "V_DS (V)")
    ejes[1].legend(frameon=False, fontsize=9, loc="lower right")
    guardar(fig, "02_conmutacion.png")

    # --- 3. Pin flotante (reset, carga del programa, USB desconectado) ---
    fig, ax = plt.subplots(figsize=(10, 3.6))
    for caso, titulo, color in (CASOS[2], CASOS[4]):
        o = ondas[caso]
        ax.plot(o["time"] * 1e3, o["i(lm)"], color=color, lw=lw, label=titulo)
    estilo(ax, "Corriente del motor con el pin del Arduino en alta impedancia", "Tiempo (ms)", "Corriente (A)")
    ax.legend(frameon=False, fontsize=9, loc="center right")
    guardar(fig, "03_pin_flotante.png")

    # --- 4. PWM a 20 kHz con el diseño elegido ---
    fig, ejes = plt.subplots(2, 2, figsize=(11, 6.5), sharex="col")
    for j, (caso, titulo, _) in enumerate((CASOS[7], CASOS[8])):
        o = ondas[caso]
        sel = (o["time"] >= 2.85e-3) & (o["time"] <= 3e-3)
        t = (o["time"][sel] - 2.85e-3) * 1e6
        ejes[0, j].plot(t, o["v(dr)"][sel], color=AZUL, lw=lw)
        ejes[1, j].plot(t, o["i(lm)"][sel], color=AZUL, lw=lw, label="Motor")
        ejes[1, j].plot(t, o["i(d1)"][sel], color=NARANJA, lw=lw, label="Diodo 1N540X")
        estilo(ejes[0, j], titulo + ": V_DS", "", "V_DS (V)")
        estilo(ejes[1, j], "Corrientes (régimen permanente)", "Tiempo (µs)", "Corriente (A)")
    ejes[1, 0].legend(frameon=False, fontsize=9, loc="center right")
    guardar(fig, "04_pwm_20kHz.png")

    # --- 5. Modelo del diodo 1N540X contra la hoja de datos ---
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.2))
    i = np.logspace(-2, 1.3, 200)
    is_, n, rs = 5e-9, 1.52, 0.019
    vt = 0.025852
    ejes[0].semilogy(n * vt * np.log(i / is_ + 1) + i * rs, i, color=AZUL, lw=lw, label="Modelo (ecuación)")
    pts_sim = [(med["06_diodo_directa"].get(k), c) for k, c in
               (("vf_0p1a", 0.1), ("vf_1a", 1), ("vf_3a", 3), ("vf_10a", 10))]
    ejes[0].semilogy([v for v, _ in pts_sim], [c for _, c in pts_sim], "o", color=AZUL, ms=8,
                     label="LTspice (.meas)")
    ejes[0].semilogy([0.67, 0.77, 1.05], [0.1, 1, 10], "s", color=NARANJA, ms=8, mfc="white",
                     mew=2, label="Hoja Vishay, Fig. 3 (leído)")
    ejes[0].plot([1.2], [3], "v", color=TINTA2, ms=9, label="VF máx. 1,2 V a 3 A")
    estilo(ejes[0], "Directa a 25 °C", "V_F (V)", "I_F (A)")
    ejes[0].legend(frameon=False, fontsize=8, loc="lower right")
    v = np.logspace(-1, 2, 200)
    ejes[1].loglog(v, 48 / (1 + v / 0.7) ** 0.25, color=AZUL, lw=lw, label="Modelo (ecuación)")
    mc = med["07_diodo_capacitancia"]
    ejes[1].loglog([4, 10, 40], [mc[k] / (2 * math.pi * 1e6) * 1e12 for k in ("i4", "i10", "i40")], "o",
                   color=AZUL, ms=8, label="LTspice (.ac a 1 MHz)")
    ejes[1].loglog([4, 10, 100], [30, 24, 14], "s", color=NARANJA, ms=8, mfc="white", mew=2,
                   label="Hoja Vishay (tabla y Fig. 5)")
    estilo(ejes[1], "Capacitancia de unión a 1 MHz", "Voltaje inverso (V)", "C_J (pF)")
    ejes[1].legend(frameon=False, fontsize=8, loc="lower left")
    guardar(fig, "05_modelo_1N540X.png")

    # --- 6. Pérdidas del MOSFET con PWM al 95 % (una sola serie: barras de un color) ---
    fig, ax = plt.subplots(figsize=(8, 3.6))
    etiquetas = ["490 Hz\ndiodo 1N540X", "20 kHz\ndiodo Schottky", "20 kHz\ndiodo 1N540X"]
    valores = [med["11_directo_pwm490Hz_95"]["p_q1_prom"], med["10_directo_pwm20k_95_schottky"]["p_q1_prom"],
               med["09_directo_pwm20k_95"]["p_q1_prom"]]
    barras = ax.bar(etiquetas, valores, color=AZUL, width=0.55)
    for b, v in zip(barras, valores):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.03, f"{v:.2f} W", ha="center", va="bottom", color=TINTA, fontsize=10)
    estilo(ax, "Potencia en el IRFZ44N, PWM al 95 %, motor de 2 A", "", "Potencia (W)")
    ax.grid(False, axis="x")
    ax.set_ylim(0, max(valores) * 1.2)
    guardar(fig, "06_perdidas_pwm.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ltspice", help="Ruta de LTspice.exe")
    args = ap.parse_args()
    exe = buscar_ltspice(args.ltspice)
    os.chdir(AQUI)

    med, ondas = {}, {}
    for caso, titulo, _ in CASOS:
        print("Simulando", caso, "...")
        subprocess.run([exe, "-b", caso + ".cir"], check=True)
        med[caso] = leer_mediciones(caso + ".log")
        if os.path.exists(caso + ".raw") and not caso.startswith("0" + "6") and not caso.startswith("07"):
            ondas[caso] = leer_raw(caso + ".raw")

    figuras(ondas, med)

    with open("resultados_mediciones.md", "w", encoding="utf-8") as f:
        f.write("# Mediciones de LTspice (generado por correr_simulaciones.py)\n\n")
        f.write("Unidades SI: A, V, W, s. Archivo generado automáticamente; no editar a mano.\n\n")
        for caso, titulo, _ in CASOS:
            f.write(f"## {caso}: {titulo}\n\n| Medición | Valor |\n|---|---|\n")
            for k, val in med[caso].items():
                f.write(f"| `{k}` | {val:.4g} |\n")
            f.write("\n")
    print("Listo: resultados_mediciones.md")


if __name__ == "__main__":
    main()
