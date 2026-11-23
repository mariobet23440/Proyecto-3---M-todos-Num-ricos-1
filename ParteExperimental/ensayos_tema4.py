"""
Serie de ensayos del tema 4 (captura rápida): escalones a varios niveles y
desaceleración libre.

Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
Fecha de creación: 22/11/2026
Autores: Mario Alejandro Betancourt Franco (23440)
         Claude Opus 5.5 (Anthropic), asistente de IA

Abre el puerto una sola vez y, para cada ensayo: espera a que el motor esté
quieto (con la telemetría), configura la captura (orden 'C'), la ejecuta
(orden 'E') y guarda los datos brutos con guardar_captura_rapida(). Al final
escribe un resumen (resumen_ensayos.csv) con el postprocesamiento de cada uno.

Uso:
    python ensayos_tema4.py COM7 --carpeta datos/tema4_20261122 --repeticiones 2
    python ensayos_tema4.py SIM  --carpeta datos/prueba_sim          (sin hardware)

Si el disco de carga inercial está montado, use --sufijo carga para que los
archivos queden marcados.

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md).
"""
import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np

from protocolo_motor import BAUDIOS, EnlaceSerie, cargar_captura_rapida, guardar_captura_rapida, orden
from postprocesamiento import procesar


def esperar_reposo(enlace, maximo=8.0, umbral=0.5):
    """Espera hasta que la velocidad medida sea casi cero durante 0,3 s."""
    inicio, quieto_desde = time.time(), None
    while time.time() - inicio < maximo:
        try:
            tipo, valor = enlace.eventos.get(timeout=0.1)
        except Exception:
            continue
        if tipo != "telem":
            continue
        if abs(valor.velocidad) < umbral:
            quieto_desde = quieto_desde or time.time()
            if time.time() - quieto_desde > 0.3:
                return True
        else:
            quieto_desde = None
    return False


def capturar(enlace, pwm, sentido, freno, t0, t1, t2, base):
    for letra, *v in (("X",), ("S", 1)):
        enlace.enviar_confirmado(letra, *v)
    if not esperar_reposo(enlace):
        print("   (el motor no se detuvo en 8 s; se captura igual)")
    for letra, *v in (("S", 0), ("C", pwm, sentido, freno, t0, t1, t2)):
        if not enlace.enviar_confirmado(letra, *v):
            raise RuntimeError(f"El Arduino no confirmó la orden {letra}")
    time.sleep(0.05)
    while not enlace.eventos.empty():
        enlace.eventos.get_nowait()
    enlace.iniciar_captura()
    limite = time.time() + (t0 + t1 + t2) / 1000 + 20
    while time.time() < limite:
        try:
            tipo, valor = enlace.eventos.get(timeout=0.5)
        except Exception:
            continue
        if tipo == "captura":
            meta = guardar_captura_rapida(base, valor["datos"], valor["encabezado"], valor["resumen"])
            return meta
        if tipo == "error":
            raise RuntimeError(valor)
    raise RuntimeError("Tiempo agotado esperando la captura")


def main():
    ap = argparse.ArgumentParser(description="Ensayos de escalón y desaceleración libre del tema 4.")
    ap.add_argument("puerto")
    ap.add_argument("--baudios", type=int, default=BAUDIOS)
    ap.add_argument("--carpeta", default=f"datos/tema4_{time.strftime('%Y%m%d')}")
    ap.add_argument("--repeticiones", type=int, default=2)
    ap.add_argument("--niveles", default="64,115,166,217,255", help="PWM de los escalones (0-255)")
    ap.add_argument("--sufijo", default="", help="Texto que se agrega al nombre (p. ej. carga)")
    ap.add_argument("--invertir-encoder", action="store_true", help="Para el resumen: encoder con signo invertido")
    ap.add_argument("--ppr", type=float, default=11.0)
    ap.add_argument("--reduccion", type=float, default=1.0)
    args = ap.parse_args()

    carpeta = Path(args.carpeta)
    sufijo = f"_{args.sufijo}" if args.sufijo else ""
    niveles = [int(x) for x in args.niveles.split(",")]
    plan = []
    for pwm in niveles:                                      # (a) escalones
        for r in range(1, args.repeticiones + 1):
            plan.append((f"a_escalones/escalon_pwm{pwm:03d}{sufijo}_r{r}", pwm, 1, 0, 300, 1500, 1500))
    for pwm in (255, 166):                                   # (b) desaceleración libre
        for r in range(1, args.repeticiones + 1):
            plan.append((f"b_desaceleracion/libre_pwm{pwm:03d}{sufijo}_r{r}", pwm, 1, 0, 300, 1500, 3000))
    plan.append((f"b_desaceleracion/freno_pwm255{sufijo}_r1", 255, 1, 1, 300, 1500, 1500))   # Comparación

    if args.puerto.upper() == "SIM":
        from arduino_simulado import ArduinoSimulado
        enlace = EnlaceSerie(ArduinoSimulado())
    else:
        enlace = EnlaceSerie.abrir(args.puerto, args.baudios)
        time.sleep(2.2)
    filas = []
    try:
        for nombre, pwm, sentido, freno, t0, t1, t2 in plan:
            base = carpeta / nombre
            print(f"-> {nombre}: PWM {pwm}, freno {freno}, fases {t0}/{t1}/{t2} ms")
            meta = capturar(enlace, pwm, sentido, freno, t0, t1, t2, base)
            crudos, meta = cargar_captura_rapida(base)
            _, res = procesar(crudos, meta, args.ppr, args.reduccion, invertir_encoder=args.invertir_encoder)
            enc = meta["encabezado"]
            fila = {"archivo": nombre, "pwm": pwm, "freno": freno,
                    "tramas": meta["tramas_recibidas"], "esperadas": int(enc["n_total"]),
                    "saltos_encoder": res["saltos_invalidos_encoder"], "cero_adc": round(res["cero_adc"], 2)}
            for clave in ("omega_regimen_rad_s", "corriente_regimen_A", "corriente_pico_A",
                          "t_63_escalon_s", "t_37_desconexion_s"):
                valor = res.get(clave)
                fila[clave] = round(valor, 5) if isinstance(valor, float) and np.isfinite(valor) else valor
            filas.append(fila)
            print("   ", {k: v for k, v in fila.items() if k not in ("archivo",)})
    finally:
        enlace.enviar(orden("X"))
        time.sleep(0.2)
        enlace.cerrar()
    if filas:
        with open(carpeta / f"resumen_ensayos{sufijo}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
        print(f"Resumen: {carpeta / f'resumen_ensayos{sufijo}.csv'}")


if __name__ == "__main__":
    main()
