"""
Postprocesamiento de la captura rápida: posición, velocidad angular y corriente.

Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
Fecha de creación: 22/11/2026
Autores: Mario Alejandro Betancourt Franco (23440)
         Claude Opus 5.5 (Anthropic), asistente de IA

Lee los datos brutos que guardó captura_respuesta.py (o la aplicación) y calcula:

  1) Posición θ: decodifica en cuadratura las fases A y B (×4) con la misma
     tabla que usa el Arduino, y la convierte a radianes con
         θ = 2π · cuenta / (4 · PPR · N),
     con PPR los pulsos por vuelta del encoder en el eje del motor y N la
     reducción de la caja (θ del eje de salida; N = 1 da el eje del motor).
  2) Velocidad ω, con dos métodos:
       - diferencia centrada con paso h:  ω_k = (θ_{k+m} - θ_{k-m}) / (2 m Δt),
         m = h·fs. Es O(h²), pero la cuantización de θ (un paso q = 2π/CPR)
         aporta un error de hasta q / (2h): h no puede ser muy chico.
       - por tiempo entre flancos: ω = 4q / (t_i - t_{i-4}), con t_i el instante
         del flanco i. Usar 4 flancos (un ciclo completo de A y B) cancela la
         asimetría entre los flancos de A y de B. Entre flancos se interpola, y
         si el motor se detiene se acota |ω| ≤ 4q / (t - t_{j-3}).
  3) Corriente: i = (ADC - cero) · Vref / 1024 / S, con el cero medido en la
     fase previa (motor libre) y S la sensibilidad del ACS712 (5 A: 0,185 V/A).

Uso:
    python postprocesamiento.py datos/ensayo --ppr 11 --reduccion 34

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md). Se probó con datos
sintéticos; no con mediciones reales. Los valores de PPR y N deben confirmarse
con la hoja de datos del motor.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from protocolo_motor import cargar_captura_rapida

# Misma tabla que el Arduino (sección 4 del .ino): índice (s_anterior << 2) | s.
TABLA_CUADRATURA = np.array([0, -1, +1, 0, +1, 0, 0, -1, -1, 0, 0, +1, 0, +1, -1, 0], dtype=np.int8)


def decodificar_cuadratura(a, b, invertir=False, corregir_saltos=True):
    """Devuelve (cuenta acumulada por muestra, número de saltos inválidos).

    Un salto inválido (A y B cambian a la vez entre dos muestras) significa que
    se saltó un estado del encoder. Con el motor del proyecto hay unas 25
    muestras por estado, así que no es por muestrear lento: en las capturas
    reales del equipo los saltos coincidieron con tramas perdidas en el
    puerto USB. Con corregir_saltos=True, cada salto se cuenta como ±2 en el
    sentido del último paso válido (el motor no invierte su giro en una
    muestra); con False, se cuenta como 0, como antes.
    """
    s = (np.asarray(a, dtype=np.int16) << 1) | np.asarray(b, dtype=np.int16)
    if len(s) < 2:
        return np.zeros(len(s), dtype=np.int64), 0
    previo, actual = s[:-1], s[1:]
    pasos = TABLA_CUADRATURA[(previo << 2) | actual].astype(np.int64)
    saltos = (previo ^ actual) == 3
    invalidos = int(np.count_nonzero(saltos))
    if corregir_saltos and invalidos:
        # Sentido del último paso válido antes de cada muestra (0 si no hubo ninguno).
        indices = np.where(pasos != 0, np.arange(len(pasos)), -1)
        ultimo = np.maximum.accumulate(indices)
        sentido = np.where(ultimo >= 0, pasos[np.clip(ultimo, 0, None)], 0)
        pasos = np.where(saltos, 2 * sentido, pasos)
    cuenta = np.concatenate([[0], np.cumsum(pasos)])
    return (-cuenta if invertir else cuenta), invalidos


def velocidad_centrada(theta, fs, h):
    """Diferencia centrada con paso h (s); en los bordes, diferencias laterales."""
    theta = np.asarray(theta, dtype=float)
    m = max(1, int(round(h * fs)))
    w = np.full(len(theta), np.nan)
    if len(theta) <= 2 * m:
        return np.gradient(theta, 1 / fs) if len(theta) > 1 else np.zeros(len(theta))
    w[m:-m] = (theta[2 * m:] - theta[:-2 * m]) * fs / (2 * m)
    w[:m] = (theta[m:2 * m] - theta[:m]) * fs / m
    w[-m:] = (theta[-m:] - theta[-2 * m:-m]) * fs / m
    return w


def velocidad_flancos(cuenta, fs, rad_por_cuenta, k=4):
    """Velocidad a partir del tiempo entre flancos del encoder (ver el encabezado)."""
    cuenta = np.asarray(cuenta)
    t = np.arange(len(cuenta)) / fs
    flancos = np.nonzero(np.diff(cuenta))[0] + 1
    w = np.zeros(len(cuenta))
    if len(flancos) <= k:
        return w
    tf, cf = flancos / fs, cuenta[flancos].astype(float)
    wi = (cf[k:] - cf[:-k]) * rad_por_cuenta / (tf[k:] - tf[:-k])
    tm = 0.5 * (tf[k:] + tf[:-k])
    w = np.interp(t, tm, wi, left=0.0, right=wi[-1])
    # Cota cuando no llegan flancos: si el próximo flanco todavía no ocurrió en t,
    # la velocidad media desde el flanco j-k+1 es menor que k·q / (t - t_{j-k+1}).
    j = np.searchsorted(flancos, np.arange(len(cuenta)), side="right") - 1
    base = np.clip(j - k + 1, 0, None)
    dt = t - tf[base]
    with np.errstate(divide="ignore", invalid="ignore"):
        cota = np.where((j >= 0) & (dt > 0), k * rad_por_cuenta / dt, 0.0)
    cota[j < 0] = 0.0
    return np.sign(w) * np.minimum(np.abs(w), cota)


def suavizar(x, n):
    """Promedio móvil centrado de n muestras (n <= 1: sin cambio)."""
    if n <= 1:
        return np.asarray(x, dtype=float)
    ventana = np.ones(n) / n
    return np.convolve(np.asarray(x, dtype=float), ventana, mode="same")


def indices_de_fase(motor):
    """Índice del escalón (primer motor = 1) y de la desconexión (primer 0 después)."""
    motor = np.asarray(motor)
    encendidos = np.nonzero(motor)[0]
    if len(encendidos) == 0:
        return None, None
    k_on = int(encendidos[0])
    apagados = np.nonzero(motor[k_on:] == 0)[0]
    k_off = int(k_on + apagados[0]) if len(apagados) else None
    return k_on, k_off


def tiempo_hasta(t, y, k0, objetivo, subiendo=True):
    """Primer tiempo desde t[k0] en el que y cruza el objetivo."""
    tramo = y[k0:]
    cruces = np.nonzero(tramo >= objetivo if subiendo else tramo <= objetivo)[0]
    return float(t[k0 + cruces[0]] - t[k0]) if len(cruces) else float("nan")


def procesar(crudos: dict, meta: dict, ppr=11.0, reduccion=1.0, vref=5.0, sensibilidad=0.185,
             invertir_encoder=False, invertir_corriente=False, h=2e-3, suavizado=0.5e-3):
    """Calcula θ, ω (dos métodos) e i. Devuelve (resultados, resumen)."""
    fs = float(meta["encabezado"]["fs_hz"])
    n = len(crudos["adc"])
    t = np.arange(n) / fs
    cpr = 4.0 * ppr * reduccion
    q = 2 * np.pi / cpr

    cuenta, invalidos = decodificar_cuadratura(crudos["a"], crudos["b"], invertir_encoder)
    theta = cuenta * q
    w_flancos = velocidad_flancos(cuenta, fs, q)
    w_centrada = velocidad_centrada(theta, fs, h)

    k_on, k_off = indices_de_fase(crudos["motor"])
    previas = crudos["adc"][:k_on] if k_on else crudos["adc"][: max(1, n // 20)]
    cero = float(np.mean(previas))
    signo = -1.0 if invertir_corriente else 1.0
    i = signo * (crudos["adc"].astype(float) - cero) * vref / 1024.0 / sensibilidad
    i_suave = suavizar(i, int(round(suavizado * fs)))

    resultados = {"t_s": t, "motor": crudos["motor"], "cuenta": cuenta, "theta_rad": theta,
                  "omega_flancos_rad_s": w_flancos, "omega_centrada_rad_s": w_centrada,
                  "corriente_A": i, "corriente_suave_A": i_suave}

    resumen = {"muestras": n, "fs_hz": fs, "duracion_s": n / fs, "cuentas_por_vuelta": cpr,
               "saltos_invalidos_encoder": invalidos, "marcas_de_perdida": int(np.sum(crudos["perdida"])),
               "cero_adc": cero, "k_escalon": k_on, "k_desconexion": k_off}
    if k_on is not None:
        fin_on = k_off if k_off is not None else n
        tramo = slice(k_on + int(0.8 * (fin_on - k_on)), fin_on)
        w_final = float(np.mean(w_flancos[tramo]))
        resumen.update({
            "omega_regimen_rad_s": w_final,
            "corriente_regimen_A": float(np.mean(i_suave[tramo])),
            "corriente_pico_A": float(np.max(np.abs(i_suave[k_on:fin_on]))),
            "t_63_escalon_s": tiempo_hasta(t, np.abs(w_flancos), k_on, 0.632 * abs(w_final)),
        })
        if k_off is not None:
            w0 = abs(float(np.mean(w_flancos[max(k_on, k_off - int(0.01 * fs)):k_off])))
            resumen["t_37_desconexion_s"] = tiempo_hasta(t, np.abs(w_flancos), k_off, 0.368 * w0, subiendo=False)
    return resultados, resumen


def guardar_procesado(base: Path, resultados: dict):
    columnas = list(resultados)
    tabla = np.column_stack([resultados[c] for c in columnas])
    np.savetxt(Path(str(base) + "_procesado.csv"), tabla, delimiter=",", header=",".join(columnas),
               comments="", fmt="%.7g")


def graficar(resultados: dict, resumen: dict, archivo=None):
    import matplotlib.pyplot as plt
    with plt.style.context("dark_background"):
        fig, ejes = plt.subplots(3, 1, sharex=True, figsize=(10, 8))
        t = resultados["t_s"]
        ejes[0].plot(t, resultados["theta_rad"], color="#39ff14", drawstyle="steps-post")
        ejes[0].set_ylabel("θ [rad]")
        ejes[1].plot(t, resultados["omega_centrada_rad_s"], color="#ff2bd6", lw=0.8, alpha=0.7,
                     label="diferencia centrada")
        ejes[1].plot(t, resultados["omega_flancos_rad_s"], color="#00e5ff", lw=1.2, label="tiempo entre flancos")
        ejes[1].set_ylabel("ω [rad/s]")
        ejes[1].legend(loc="best")
        ejes[2].plot(t, resultados["corriente_A"], color="#ffb000", lw=0.4, alpha=0.4, label="cruda")
        ejes[2].plot(t, resultados["corriente_suave_A"], color="#ffe600", lw=1.2, label="promedio móvil")
        ejes[2].set_ylabel("i [A]")
        ejes[2].set_xlabel("t [s]")
        ejes[2].legend(loc="best")
        for eje in ejes:
            eje.grid(alpha=0.2)
            for k in (resumen.get("k_escalon"), resumen.get("k_desconexion")):
                if k is not None:
                    eje.axvline(t[k], color="white", lw=0.6, ls="--")
        fig.tight_layout()
        if archivo:
            fig.savefig(archivo, dpi=130)
        return fig


def main():
    ap = argparse.ArgumentParser(description="Calcula θ, ω e i a partir de una captura rápida.")
    ap.add_argument("base", help="Ruta de la captura sin extensión (p. ej. datos/ensayo1)")
    ap.add_argument("--ppr", type=float, default=11.0, help="Pulsos por vuelta del encoder en el eje del motor")
    ap.add_argument("--reduccion", type=float, default=1.0, help="Reducción N de la caja (1 = eje del motor)")
    ap.add_argument("--vref", type=float, default=5.0, help="Voltaje de referencia del ADC (5 V del Nano, medido)")
    ap.add_argument("--sensibilidad", type=float, default=0.185, help="ACS712 de 5 A: 0.185 V/A")
    ap.add_argument("--h-ms", type=float, default=2.0, help="Paso h de la diferencia centrada (ms)")
    ap.add_argument("--suavizado-ms", type=float, default=0.5, help="Ventana del promedio móvil de i (ms)")
    ap.add_argument("--invertir-encoder", action="store_true")
    ap.add_argument("--invertir-corriente", action="store_true")
    ap.add_argument("--sin-graficas", action="store_true")
    args = ap.parse_args()

    base = Path(args.base)
    if base.suffix in (".bin", ".json"):
        base = base.with_suffix("")
    crudos, meta = cargar_captura_rapida(base)
    resultados, resumen = procesar(crudos, meta, args.ppr, args.reduccion, args.vref, args.sensibilidad,
                                   args.invertir_encoder, args.invertir_corriente,
                                   args.h_ms / 1000, args.suavizado_ms / 1000)
    guardar_procesado(base, resultados)
    Path(str(base) + "_resumen.json").write_text(json.dumps(resumen, indent=2), encoding="utf-8")
    for clave, valor in resumen.items():
        print(f"{clave:28s} {valor}")
    if resumen["saltos_invalidos_encoder"]:
        print("ADVERTENCIA: hubo saltos inválidos en el encoder (cuentas perdidas).")
    if resumen["marcas_de_perdida"]:
        print("ADVERTENCIA: se perdieron tramas; los tiempos después de la pérdida no son exactos.")
    if not args.sin_graficas:
        graficar(resultados, resumen, Path(str(base) + "_graficas.png"))
        print(f"Gráficas: {base}_graficas.png")
    print(f"Datos procesados: {base}_procesado.csv")


if __name__ == "__main__":
    main()
