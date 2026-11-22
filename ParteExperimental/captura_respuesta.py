"""
Receptor de la respuesta al escalón y a la desconexión del motor DC JGA25-370.

Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
Fecha de creación: 22/11/2026
Autores: Mario Alejandro Betancourt Franco (23440)
         Claude Opus 5.5 (Anthropic), asistente de IA

Abre el puerto serie del Arduino Nano que corre RespuestaEscalonMotorDC.ino,
inicia un ensayo (envía 'E'), recibe las tramas binarias, las decodifica y
guarda un CSV con: muestra, tiempo, estado del motor, lectura del ADC,
corriente estimada, conteo del encoder y marca de pérdida.

AVISO: código generado con IA (ver UsoIA/BitacoraUsoIA.md). No se ha probado
con el hardware real; solo se probó el decodificador con datos sintéticos.

Uso:
    pip install pyserial
    python captura_respuesta.py COM5 --salida ensayo1.csv

Requiere pyserial (pip install pyserial).
"""
import argparse
import csv
import sys
import time

FIN = 0xFF  # Marcador de fin: dos bytes seguidos con el bit 7 en 1


def buscar_fin(datos, desde):
    """Devuelve la posición del marcador de fin (dos bytes >= 0x80 seguidos), o -1."""
    for i in range(max(desde, 0), len(datos) - 1):
        if datos[i] >= 0x80 and datos[i + 1] >= 0x80:
            return i
    return -1


def decodificar(datos):
    """Convierte los bytes recibidos en una lista de tramas (motor, adc, pulsos16, perdida).

    Trama de 4 bytes (ver la sección 7 del .ino):
      b0 = 1 M A9..A4 | b1 = 0 A3..A0 E15..E13 | b2 = 0 E12..E6 | b3 = 0 P E5..E0
    Si un byte se pierde, se descarta hasta el siguiente byte con el bit 7 en 1.
    """
    tramas, descartados, i = [], 0, 0
    while i + 3 < len(datos):
        b0, b1, b2, b3 = datos[i], datos[i + 1], datos[i + 2], datos[i + 3]
        if b0 < 0x80 or b1 >= 0x80 or b2 >= 0x80 or b3 >= 0x80:
            descartados += 1          # Fuera de sincronía: avanza un byte
            i += 1
            continue
        motor = (b0 >> 6) & 1
        adc = ((b0 & 0x3F) << 4) | (b1 >> 3)
        pulsos = ((b1 & 0x07) << 13) | (b2 << 6) | (b3 & 0x3F)
        perdida = (b3 >> 6) & 1
        tramas.append((motor, adc, pulsos, perdida))
        i += 4
    return tramas, descartados


def desenrollar(pulsos16):
    """Convierte el conteo de 16 bits (que da la vuelta) en un conteo continuo."""
    salida, total, previo = [], 0, None
    for p in pulsos16:
        if previo is None:
            total = p - 65536 if p >= 32768 else p
        else:
            d = (p - previo) & 0xFFFF
            total += d - 65536 if d >= 32768 else d
        salida.append(total)
        previo = p
    return salida


def leer_parametros(linea):
    """Convierte 'INICIO fs_hz=38461.54 n_previas=...' en un diccionario."""
    pares = (t.split("=", 1) for t in linea.split() if "=" in t)
    return {k: float(v) for k, v in pares}


def main():
    ap = argparse.ArgumentParser(description="Captura la respuesta al escalón del motor DC.")
    ap.add_argument("puerto", help="Puerto serie del Arduino (p. ej. COM5 o /dev/ttyUSB0)")
    ap.add_argument("--baudios", type=int, default=2_000_000)
    ap.add_argument("--salida", default="ensayo.csv", help="Archivo CSV de salida")
    ap.add_argument("--vref", type=float, default=5.0, help="Voltaje de referencia del ADC (AVcc medido)")
    ap.add_argument("--sensibilidad", type=float, default=0.185, help="ACS712 de 5 A: 0.185 V/A")
    args = ap.parse_args()

    import serial  # pyserial

    with serial.Serial(args.puerto, args.baudios, timeout=0.5) as ser:
        time.sleep(2.0)                 # El Nano se reinicia al abrir el puerto
        ser.reset_input_buffer()
        ser.write(b"E")                 # Orden de ensayo

        # Encabezado de texto: ignora líneas hasta la que empieza con INICIO
        limite = time.time() + 5
        while True:
            linea = ser.readline().decode("ascii", errors="replace").strip()
            if linea.startswith("INICIO"):
                break
            if time.time() > limite:
                sys.exit("No llegó el encabezado INICIO. ¿Puerto o baudios correctos?")
        p = leer_parametros(linea)
        fs, n_previas, n_total = p["fs_hz"], int(p["n_previas"]), int(p["n_total"])
        print(f"Ensayo: fs = {fs:.2f} Hz, {n_total} muestras ({n_total / fs:.2f} s)")

        # Datos binarios hasta el marcador de fin
        datos, fin = bytearray(), -1
        limite = time.time() + n_total / fs + 10
        while fin < 0:
            bloque = ser.read(max(1, ser.in_waiting))
            if bloque:
                desde = len(datos) - 1
                datos += bloque
                fin = buscar_fin(datos, desde)
            elif time.time() > limite:
                sys.exit("Tiempo agotado esperando el fin de los datos.")
        # Resumen de texto "FIN ...": puede haber llegado ya en el último bloque leído
        resto = bytes(datos[fin + 2:])
        limite = time.time() + 2
        while (b"FIN" not in resto or not resto.split(b"FIN", 1)[1].endswith(b"\n")) \
                and time.time() < limite:
            resto += ser.read(max(1, ser.in_waiting))
        print(resto.decode("ascii", errors="replace").strip())

    tramas, descartados = decodificar(datos[:fin])
    perdidas = sum(t[3] for t in tramas)
    if len(tramas) != n_total or descartados or perdidas:
        print(f"ADVERTENCIA: {len(tramas)} tramas de {n_total}, {descartados} bytes descartados, "
              f"{perdidas} marcas de pérdida. Los tiempos después de una pérdida no son exactos.")

    # Cero del sensor: promedio de la fase previa (motor apagado)
    previas = [t[1] for t in tramas[:n_previas] if t[0] == 0]
    cero = sum(previas) / len(previas)
    pulsos = desenrollar([t[2] for t in tramas])

    with open(args.salida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n", "t_s", "motor", "adc", "corriente_A", "pulsos_encoder", "perdida"])
        for n, ((motor, adc, _, perdida), cuenta) in enumerate(zip(tramas, pulsos)):
            corriente = (adc - cero) * args.vref / 1024 / args.sensibilidad
            w.writerow([n, f"{n / fs:.7f}", motor, adc, f"{corriente:.4f}", cuenta, perdida])
    print(f"Guardado {args.salida}: {len(tramas)} muestras. Cero del sensor = {cero:.2f} cuentas.")


if __name__ == "__main__":
    main()
