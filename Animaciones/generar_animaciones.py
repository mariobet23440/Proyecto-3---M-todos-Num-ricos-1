"""
Animaciones didácticas para el cuaderno del Proyecto 3 (Métodos Numéricos 1, UVG).

    1. euler_paso_a_paso.gif   Método de Euler en el circuito RL del motor.
    2. estabilidad_euler.gif   Región de estabilidad |1 + h*lambda| <= 1 al variar h.
    3. lipschitz_cono.gif      Condición de Lipschitz: tanh(w/eps) frente a sign(w).

Autor de las animaciones: Claude Opus 5.5 (Anthropic), asistente de IA, a pedido de
Mario Alejandro Betancourt Franco (23440). Fecha: 22/11/2026.
Ver UsoIA/BitacoraUsoIA.md.

Uso (desde esta carpeta):  python generar_animaciones.py
Requiere numpy, matplotlib y Pillow.
"""
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle, Polygon

AQUI = os.path.dirname(os.path.abspath(__file__))

# Paleta categórica (orden fijo) y tinta
AZUL, NARANJA, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TINTA, TINTA2, REJILLA, GRIS = "#0b0b0b", "#52514e", "#e4e3df", "#8a8984"
CREDITO = "Animación: Claude Opus 5.5 (Anthropic) · Proyecto 3, Métodos Numéricos 1, UVG"

# Circuito RL del motor (rotor detenido): L di/dt = V - R i
V, R, L = 12.0, 6.0, 2e-3
TAU = L / R                  # constante de tiempo eléctrica: 0,333 ms
I_FIN = V / R                # corriente final: 2 A
LAMBDA = -R / L              # valor propio del sistema: -3000 1/s


def f(t, i):
    """Campo vectorial (aquí escalar): di/dt."""
    return (V - R * i) / L


def i_exacta(t):
    return I_FIN * (1 - np.exp(-t / TAU))


def euler(h, n):
    t = np.arange(n + 1) * h
    i = np.zeros(n + 1)
    for k in range(n):
        i[k + 1] = i[k] + h * f(t[k], i[k])
    return t, i


def estilo(ax):
    ax.grid(True, color=REJILLA, linewidth=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(TINTA2)
    ax.tick_params(colors=TINTA2)


def credito(fig):
    fig.text(0.995, 0.008, CREDITO, ha="right", va="bottom", fontsize=7.5, color=GRIS)


def guardar(anim, nombre, fps):
    ruta = os.path.join(AQUI, nombre)
    anim.save(ruta, writer=PillowWriter(fps=fps), dpi=80)
    print(f"  {nombre}: {os.path.getsize(ruta) / 1e6:.2f} MB")


# ---------------------------------------------------------------------------
# 1. Método de Euler paso a paso
# ---------------------------------------------------------------------------
def animacion_euler():
    h, n = 0.1e-3, 10                          # h = 0,3 tau
    t, i = euler(h, n)
    sub = 6                                    # cuadros por paso (dibujar la tangente)
    pausa = 3                                  # cuadros de pausa al final de cada paso
    cuadros = n * (sub + pausa) + 12

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.14)
    tt = np.linspace(0, n * h, 300)
    ax.plot(tt * 1e3, i_exacta(tt), color=GRIS, lw=2, ls="--", label="Solución exacta $i(t)$")
    linea_num, = ax.plot([], [], "o-", color=AZUL, lw=2, ms=6, label="Euler $i_k$")
    tangente, = ax.plot([], [], color=NARANJA, lw=2, label="Tangente $f(t_k, i_k)$")
    error = ax.vlines([], [], [], color=NARANJA, lw=1.2, ls=":")
    texto = ax.text(0.02, 0.96, "", transform=ax.transAxes, va="top", fontsize=11, color=TINTA,
                    bbox=dict(boxstyle="round", fc="white", ec=REJILLA))
    ax.set_xlim(-0.03, n * h * 1e3 + 0.05)
    ax.set_ylim(-0.1, 2.35)
    ax.set_xlabel("Tiempo (ms)", color=TINTA2)
    ax.set_ylabel("Corriente (A)", color=TINTA2)
    estilo(ax)
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    fig.suptitle("Método de Euler en el circuito del motor:  $L\\,di/dt = V - R\\,i$", x=0.08, ha="left",
                 fontsize=13, color=TINTA)
    ax.set_title(f"$h$ = {h * 1e3:.1f} ms = {h / TAU:.1f}$\\,\\tau$   (V = 12 V, R = 6 Ω, L = 2 mH)",
                 loc="left", fontsize=10, color=TINTA2)
    credito(fig)
    estado = {"error": error}

    def cuadro(c):
        k, r = divmod(c, sub + pausa)
        if k >= n:
            k, r = n - 1, sub + pausa - 1
        frac = min(r / (sub - 1), 1.0)
        # Puntos ya calculados
        hasta = k + 1 if r >= sub - 1 else k
        linea_num.set_data(t[: hasta + 1] * 1e3, i[: hasta + 1])
        # Tangente desde (t_k, i_k) con la pendiente f(t_k, i_k)
        t1 = t[k] + frac * h
        tangente.set_data([t[k] * 1e3, t1 * 1e3], [i[k], i[k] + (t1 - t[k]) * f(t[k], i[k])])
        # Error global en los puntos ya calculados
        estado["error"].remove()
        estado["error"] = ax.vlines(t[1: hasta + 1] * 1e3, i[1: hasta + 1], i_exacta(t[1: hasta + 1]),
                                    color=NARANJA, lw=1.2, ls=":")
        texto.set_text(
            f"Paso k = {k}\n"
            f"$i_{{k+1}} = i_k + h\\,f(t_k, i_k)$\n"
            f"$i_{{{k + 1}}}$ = {i[k]:.3f} + {h * 1e3:.1f} ms × {f(t[k], i[k]):,.0f} A/s = {i[k + 1]:.3f} A\n"
            f"Error: $i(t_{{{k + 1}}}) - i_{{{k + 1}}}$ = {i_exacta(t[k + 1]) - i[k + 1]:+.3f} A")
        return linea_num, tangente, texto

    guardar(FuncAnimation(fig, cuadro, frames=cuadros, blit=False), "euler_paso_a_paso.gif", fps=6)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Estabilidad: el punto h*lambda entra y sale de la región |1 + h*lambda| <= 1
# ---------------------------------------------------------------------------
def animacion_estabilidad():
    hs = np.concatenate([np.linspace(0.1, 2.3, 70), np.full(14, 2.3)]) * TAU
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1, 1.6]})
    fig.subplots_adjust(left=0.06, right=0.98, top=0.82, bottom=0.14, wspace=0.25)

    ax1.add_patch(Circle((-1, 0), 1, fc="#d6e6f8", ec=AZUL, lw=2))
    ax1.axhline(0, color=TINTA2, lw=0.8)
    ax1.axvline(0, color=TINTA2, lw=0.8)
    ax1.text(-1, 0.45, "Región estable\n$|1 + h\\lambda| \\leq 1$", ha="center", fontsize=10, color=TINTA)
    punto, = ax1.plot([], [], "o", ms=12, mec="white", mew=2)
    ax1.set_xlim(-2.7, 0.6)
    ax1.set_ylim(-1.4, 1.4)
    ax1.set_aspect("equal")
    ax1.set_xlabel("Re$(h\\lambda)$", color=TINTA2)
    ax1.set_ylabel("Im$(h\\lambda)$", color=TINTA2)
    estilo(ax1)
    ax1.set_title("Plano complejo de $h\\lambda$", loc="left", fontsize=11, color=TINTA)

    tt = np.linspace(0, 3e-3, 400)
    ax2.plot(tt * 1e3, i_exacta(tt), color=GRIS, lw=2, ls="--", label="Solución exacta")
    num, = ax2.plot([], [], "o-", color=AZUL, lw=1.8, ms=4, label="Euler")
    ax2.set_xlim(0, 3)
    ax2.set_ylim(-3, 7)
    ax2.set_xlabel("Tiempo (ms)", color=TINTA2)
    ax2.set_ylabel("Corriente (A)", color=TINTA2)
    estilo(ax2)
    ax2.legend(loc="upper right", frameon=False, fontsize=10)
    titulo2 = ax2.set_title("", loc="left", fontsize=11, color=TINTA)
    veredicto = ax2.text(0.02, 0.95, "", transform=ax2.transAxes, va="top", fontsize=12, fontweight="bold")

    fig.suptitle("Estabilidad del método de Euler:  $i_{k+1} - i_\\infty = (1 + h\\lambda)(i_k - i_\\infty)$,"
                 "  con $\\lambda = -R/L$", x=0.06, ha="left", fontsize=13, color=TINTA)
    credito(fig)

    def cuadro(c):
        h = hs[c]
        z = h * LAMBDA
        g = abs(1 + z)
        estable = g <= 1
        color = AZUL if estable else NARANJA
        punto.set_data([z], [0])
        punto.set_color(color)
        n = int(3e-3 / h)
        t, i = euler(h, n)
        num.set_data(t * 1e3, np.clip(i, -10, 10))
        num.set_color(color)
        titulo2.set_text(f"$h$ = {h / TAU:.2f}$\\,\\tau$   →   $|1 + h\\lambda|$ = {g:.2f}")
        if g < 1 and z > -1:
            txt = "Estable: se acerca sin oscilar"
        elif g <= 1:
            txt = "Estable: oscila, pero el error se atenúa"
        else:
            txt = "Inestable: el error crece en cada paso"
        veredicto.set_text(txt)
        veredicto.set_color(color)
        return punto, num, titulo2, veredicto

    guardar(FuncAnimation(fig, cuadro, frames=len(hs), blit=False), "estabilidad_euler.gif", fps=8)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Condición de Lipschitz: el "cono" de pendiente L
# ---------------------------------------------------------------------------
def animacion_lipschitz():
    eps = 0.5
    lip = 1 / eps                                  # constante de Lipschitz de tanh(w/eps)
    a_vals = np.concatenate([np.linspace(-2.5, 2.5, 60), np.full(6, 2.5),
                             np.linspace(2.5, 0.08, 30), np.full(16, 0.08)])
    x = np.linspace(-3, 3, 1201)
    funciones = [
        (lambda w: np.tanh(w / eps), f"$g(\\omega) = \\tanh(\\omega/\\varepsilon)$,  $\\varepsilon$ = {eps}",
         f"Lipschitz: la gráfica nunca sale del cono ($\\mathcal{{L}} = 1/\\varepsilon$ = {lip:.0f})"),
        (np.sign, "$g(\\omega) = \\mathrm{sign}(\\omega)$",
         "No es Lipschitz: cerca del salto, ningún $\\mathcal{L}$ alcanza"),
    ]
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.78, bottom=0.14, wspace=0.08)
    artistas = []
    for ax, (g, titulo, _) in zip(ejes, funciones):
        ax.plot(x, g(x), color=TINTA, lw=2.2, zorder=3)
        cono = Polygon([[0, 0]], closed=True, fc="#d6e6f8", ec=AZUL, lw=1.2, alpha=0.9, zorder=1)
        ax.add_patch(cono)
        fuera, = ax.plot([], [], ".", color=NARANJA, ms=5, zorder=4)
        centro, = ax.plot([], [], "o", color=AZUL, ms=9, mec="white", mew=2, zorder=5)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-2.2, 2.2)
        ax.set_xlabel("$\\omega$", color=TINTA2)
        ax.set_title(titulo, loc="left", fontsize=11, color=TINTA)
        estilo(ax)
        nota = ax.text(0.02, 0.04, "", transform=ax.transAxes, fontsize=9.5, color=TINTA,
                       bbox=dict(boxstyle="round", fc="white", ec=REJILLA))
        artistas.append((g, cono, fuera, centro, nota))
    ejes[0].set_ylabel("$g(\\omega)$", color=TINTA2)
    fig.suptitle("Condición de Lipschitz:  $|g(\\omega) - g(a)| \\leq \\mathcal{L}\\,|\\omega - a|$"
                 f"   (cono azul de pendiente $\\pm\\mathcal{{L}}$ = ±{lip:.0f} centrado en $a$)",
                 x=0.06, ha="left", fontsize=12.5, color=TINTA)
    fig.text(0.06, 0.855, "Si la gráfica se queda dentro del cono para todo $a$, la función no 'estira' "
             "distancias más que un factor $\\mathcal{L}$.", fontsize=10, color=TINTA2)
    credito(fig)

    def cuadro(c):
        a = a_vals[c]
        salida = []
        for (g, cono, fuera, centro, nota), (_, _, msg) in zip(artistas, funciones):
            ga = float(g(np.array([a]))[0])
            d = 3.2
            cono.set_xy([[a, ga], [a - d, ga + lip * d], [a - d, ga - lip * d], [a, ga],
                         [a + d, ga + lip * d], [a + d, ga - lip * d]])
            viola = np.abs(g(x) - ga) > lip * np.abs(x - a) + 1e-9
            fuera.set_data(x[viola], g(x)[viola])
            centro.set_data([a], [ga])
            nota.set_text(f"a = {a:+.2f}   " + ("Se sale del cono: falla la condición" if viola.any() else msg))
            nota.set_color(NARANJA if viola.any() else TINTA)
            salida += [cono, fuera, centro, nota]
        return salida

    guardar(FuncAnimation(fig, cuadro, frames=len(a_vals), blit=False), "lipschitz_cono.gif", fps=10)
    plt.close(fig)


if __name__ == "__main__":
    print("Generando animaciones...")
    animacion_euler()
    animacion_estabilidad()
    animacion_lipschitz()
    print("Listo.")
