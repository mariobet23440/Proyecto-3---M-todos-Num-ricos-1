"""
Prueba del PID en el motor real: aplica una referencia, graba la telemetría y
calcula las métricas de desempeño.

Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
Fecha de creación: 22/11/2026
Autores: Mario Alejandro Betancourt Franco (23440)
         Claude Opus 5.5 (Anthropic), asistente de IA

Guarda <salida>.csv (mismas columnas que la grabación de la aplicación, sin
las del gemelo) y <salida>.json (configuración y métricas). Métricas por cada
escalón de la referencia: sobreimpulso, tiempo de establecimiento (banda del
5 %) y error medio en el último 20 % del tramo.

Uso:
    python prueba_pid.py COM7 --modo vel --kp 0.04 --ki 0.4 --tipo cuadrada --amp 100 --off 300 --f 0.5
    python prueba_pid.py COM7 --modo pos --kp 2 --kd 0.05 --tipo cuadrada --amp 6.28 --off 0 --f 0.5

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md).
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

from protocolo_motor import BAUDIOS, EnlaceSerie, orden

TIPOS = {"constante": 0, "seno": 1, "cuadrada": 2, "triangular": 3}
COLUMNAS = ("t_s", "k", "cuenta", "theta_rad", "referencia", "omega_rad_s", "voltaje_V", "adc", "corriente_A",
            "modo", "estado")


def metricas_escalones(t, r, y, banda=0.05):
    """Métricas de cada cambio brusco de la referencia (escalones de la onda cuadrada)."""
    cambios = np.nonzero(np.abs(np.diff(r)) > 1e-6)[0] + 1
    limites = list(cambios) + [len(r)]
    resultado = []
    for a, b in zip(limites[:-1], limites[1:]):
        if b - a < 10:
            continue
        r0, r1 = r[a - 1], r[a]
        salto = r1 - r0
        tramo = y[a:b]
        tt = t[a:b] - t[a]
        exceso = (tramo - r1) * np.sign(salto)
        sobre = max(0.0, float(np.max(exceso))) / abs(salto) * 100
        fuera = np.nonzero(np.abs(tramo - r1) > banda * abs(salto))[0]
        t_est = float(tt[fuera[-1] + 1]) if len(fuera) and fuera[-1] + 1 < len(tt) else (float("nan") if len(fuera) else 0.0)
        final = tramo[int(0.8 * len(tramo)):]
        resultado.append({"t_inicio_s": round(float(t[a]), 4), "de": round(float(r0), 4), "a": round(float(r1), 4),
                          "sobreimpulso_%": round(sobre, 2), "t_establecimiento_5%_s": round(t_est, 4),
                          "error_final_medio": round(float(np.mean(r1 - final)), 4),
                          "rizado_final_std": round(float(np.std(final)), 4)})
    return resultado


def main():
    ap = argparse.ArgumentParser(description="Prueba del PID en el motor real.")
    ap.add_argument("puerto")
    ap.add_argument("--baudios", type=int, default=BAUDIOS)
    ap.add_argument("--modo", choices=("vel", "pos", "abierto"), default="vel")
    ap.add_argument("--kp", type=float, default=0.04)
    ap.add_argument("--ki", type=float, default=0.4)
    ap.add_argument("--kd", type=float, default=0.0)
    ap.add_argument("--ts", type=float, default=5.0, help="Periodo de muestreo (ms)")
    ap.add_argument("--tau", type=float, default=10.0, help="Filtro de velocidad (ms)")
    ap.add_argument("--tipo", choices=tuple(TIPOS), default="cuadrada")
    ap.add_argument("--amp", type=float, default=100.0)
    ap.add_argument("--off", type=float, default=300.0)
    ap.add_argument("--f", type=float, default=0.5)
    ap.add_argument("--duracion", type=float, default=6.0)
    ap.add_argument("--cpr", type=float, default=44.0, help="Cuentas por vuelta del eje controlado")
    ap.add_argument("--vbus", type=float, default=12.0)
    ap.add_argument("--invertir-encoder", type=int, default=1)
    ap.add_argument("--antiwindup", type=int, default=1)
    ap.add_argument("--vref", type=float, default=5.0)
    ap.add_argument("--sensibilidad", type=float, default=0.185)
    ap.add_argument("--cero", type=float, default=None, help="Cero del ADC (por defecto se mide en reposo)")
    ap.add_argument("--decimacion", type=int, default=1, help="Telemetría cada n periodos (1 = todos)")
    ap.add_argument("--salida", default=None)
    args = ap.parse_args()

    modo = {"abierto": 1, "vel": 2, "pos": 3}[args.modo]
    salida = Path(args.salida or f"datos/pid_{args.modo}_{time.strftime('%Y%m%d_%H%M%S')}")
    salida.parent.mkdir(parents=True, exist_ok=True)

    e = EnlaceSerie.abrir(args.puerto, args.baudios)
    time.sleep(2.2)
    filas = []

    def recoger(segundos, guardar):
        fin, lat = time.time() + segundos, 0.0
        while time.time() < fin:
            if time.time() - lat > 0.5:
                e.enviar(orden("H"))
                lat = time.time()
            try:
                tipo, v = e.eventos.get(timeout=0.05)
            except Exception:
                continue
            if tipo == "telem" and guardar is not None:
                guardar.append(v)

    try:
        # Todo se configura con la telemetría apagada: así las confirmaciones
        # llegan rápido (ver decimacion_telemetria en protocolo_motor.py).
        config = (("X",), ("S", 0), ("P", args.cpr, args.vbus), ("T", args.ts), ("F", args.tau),
                  ("K", args.kp, args.ki, args.kd), ("A", args.antiwindup), ("I", args.invertir_encoder),
                  ("Z",), ("R", TIPOS[args.tipo], args.amp, args.off, args.f), ("S", args.decimacion))
        for letra, *v in config:
            if not e.enviar_confirmado(letra, *v):
                sys.exit(f"El Arduino no confirmó la orden {letra}")
        reposo = []
        recoger(1.0, reposo)                                   # Motor quieto: cero del sensor
        cero = args.cero if args.cero is not None else float(np.mean([t.adc for t in reposo]))
        if not e.enviar_confirmado("M", modo):
            sys.exit("El Arduino no confirmó la orden M")
        tel = []
        recoger(args.duracion, tel)
    finally:
        e.enviar(orden("X"))
        time.sleep(0.2)
        reintentos = e.reintentos
        e.cerrar()

    tel = [t for t in tel if t.modo == modo]
    if len(tel) < 10:
        sys.exit("Llegó muy poca telemetría.")
    k = np.array([t.k for t in tel], dtype=float)
    ts = args.ts / 1000
    t = (k - k[0]) * ts
    q = 2 * math.pi / args.cpr
    cuenta = np.array([t_.cuenta for t_ in tel], dtype=float)
    theta = cuenta * q
    ref = np.array([t_.referencia for t_ in tel])
    w = np.array([t_.velocidad for t_ in tel])
    u = np.array([t_.voltaje for t_ in tel])
    adc = np.array([t_.adc for t_ in tel])
    i = (adc - cero) * args.vref / 1024 / args.sensibilidad
    estado = np.array([t_.estado for t_ in tel])
    tabla = np.column_stack([t, k, cuenta, theta, ref, w, u, adc, i, np.full(len(t), modo), estado])
    np.savetxt(str(salida) + ".csv", tabla, delimiter=",", header=",".join(COLUMNAS), comments="", fmt="%.7g")

    y = w if modo == 2 else theta
    met = metricas_escalones(t, ref, y) if args.tipo == "cuadrada" else []
    resumen = {"error_rms": round(float(np.sqrt(np.mean((ref - y) ** 2))), 4),
               "saturado_%": round(float(100 * np.mean((estado & 1) > 0)), 2),
               "periodos_atrasados_%": round(float(100 * np.mean((estado & 4) > 0)), 2),
               "reenvios_de_ordenes": reintentos,
               "tramas": len(t), "huecos_en_k": int(np.sum(np.diff(k) > 1))}
    meta = {"tipo": "prueba_pid", "fecha": time.strftime("%Y-%m-%d %H:%M:%S"), "argumentos": vars(args),
            "cero_adc": cero, "resumen": resumen, "escalones": met}
    Path(str(salida) + ".json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False))
    for m in met:
        print("  ", m)
    print(f"Guardado {salida}.csv / .json")


if __name__ == "__main__":
    main()
