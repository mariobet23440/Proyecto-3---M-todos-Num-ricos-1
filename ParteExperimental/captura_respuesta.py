"""
Receptor de la captura rápida (respuesta al escalón y a la desconexión).

Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
Fecha de creación: 22/11/2026 (versión 2: L298N y datos brutos)
Autores: Mario Alejandro Betancourt Franco (23440)
         Claude Opus 5.5 (Anthropic), asistente de IA

Abre el puerto serie del Arduino Nano que corre MotorDC_L298N.ino, configura
la captura (orden 'C'), la inicia (orden 'E') y guarda los DATOS BRUTOS:

    <salida>.bin        bytes tal cual llegaron (para reprocesar si hace falta)
    <salida>_crudo.csv  n, t_s, motor, adc, fase_a, fase_b, perdida
    <salida>.json       configuración del ensayo y resumen del Arduino

El cálculo de θ, ω e i lo hace postprocesamiento.py (se puede llamar al final
con --procesar).

Uso:
    pip install pyserial numpy matplotlib
    python captura_respuesta.py COM5 --salida datos/ensayo1
    python captura_respuesta.py COM5 --pwm 180 --t1 1000 --t2 2000 --freno
    python captura_respuesta.py SIM --procesar          (Arduino simulado)

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md). No se ha probado
con el hardware real; se probó con el Arduino simulado.
"""
import argparse
import sys
import time
from pathlib import Path

from protocolo_motor import BAUDIOS, EnlaceSerie, guardar_captura_rapida, orden


def main():
    ap = argparse.ArgumentParser(description="Captura la respuesta al escalón y a la desconexión del motor DC.")
    ap.add_argument("puerto", help="Puerto serie del Arduino (COM5, /dev/ttyUSB0) o SIM para el simulador")
    ap.add_argument("--baudios", type=int, default=BAUDIOS)
    ap.add_argument("--salida", default=None, help="Ruta base de los archivos (sin extensión)")
    ap.add_argument("--pwm", type=int, default=255, help="Ciclo de trabajo del escalón (0 a 255)")
    ap.add_argument("--reversa", action="store_true", help="Girar en sentido contrario")
    ap.add_argument("--freno", action="store_true", help="Frenar el motor al desconectar (si no, queda libre)")
    ap.add_argument("--t0", type=int, default=200, help="Fase previa, ms (motor libre, cero del sensor)")
    ap.add_argument("--t1", type=int, default=1500, help="Escalón, ms")
    ap.add_argument("--t2", type=int, default=1500, help="Desconexión, ms")
    ap.add_argument("--procesar", action="store_true", help="Ejecutar postprocesamiento.py al terminar")
    ap.add_argument("--ppr", type=float, default=11.0)
    ap.add_argument("--reduccion", type=float, default=1.0)
    args = ap.parse_args()

    salida = Path(args.salida or f"datos/captura_{time.strftime('%Y%m%d_%H%M%S')}")

    if args.puerto.upper() == "SIM":
        from arduino_simulado import ArduinoSimulado
        enlace = EnlaceSerie(ArduinoSimulado(ppr=args.ppr))
    else:
        enlace = EnlaceSerie.abrir(args.puerto, args.baudios)
        time.sleep(2.0)                      # El Nano se reinicia al abrir el puerto

    try:
        enlace.enviar(orden("X"))            # Motor en reposo
        enlace.enviar(orden("S", 0))         # Sin telemetría durante la configuración
        enlace.enviar(orden("C", args.pwm, -1 if args.reversa else 1, int(args.freno), args.t0, args.t1, args.t2))
        time.sleep(0.3)
        enlace.iniciar_captura()
        print("Captura en curso...")
        limite = time.time() + (args.t0 + args.t1 + args.t2) / 1000 + 20
        captura = None
        while captura is None:
            if time.time() > limite:
                sys.exit("Tiempo agotado: no llegó la captura. ¿Puerto, baudios o programa correctos?")
            try:
                tipo, valor = enlace.eventos.get(timeout=0.5)
            except Exception:
                continue
            if tipo == "captura":
                captura = valor
            elif tipo == "texto" and ("ERR" in valor or "AVISO" in valor):
                print(valor)
            elif tipo == "error":
                sys.exit(valor)
            elif tipo == "progreso":
                print(f"\r  {100 * valor:5.1f} %", end="", flush=True)
        print()
        enlace.enviar(orden("S", 1))         # Vuelve a la telemetría normal
    finally:
        enlace.cerrar()

    meta = guardar_captura_rapida(salida, captura["datos"], captura["encabezado"], captura["resumen"])
    enc = meta["encabezado"]
    print(f"{captura['resumen']}")
    print(f"Guardado {salida}.bin / _crudo.csv / .json: {meta['tramas_recibidas']} tramas "
          f"de {int(enc['n_total'])} a {enc['fs_hz']:.1f} Hz.")
    if meta["tramas_recibidas"] != int(enc["n_total"]) or meta["bytes_descartados"] or meta["marcas_de_perdida"]:
        print(f"ADVERTENCIA: {meta['bytes_descartados']} bytes descartados, "
              f"{meta['marcas_de_perdida']} marcas de pérdida. Los tiempos después de una pérdida no son exactos.")

    if args.procesar:
        import subprocess
        subprocess.run([sys.executable, str(Path(__file__).with_name("postprocesamiento.py")), str(salida),
                        "--ppr", str(args.ppr), "--reduccion", str(args.reduccion)], check=False)


if __name__ == "__main__":
    main()
