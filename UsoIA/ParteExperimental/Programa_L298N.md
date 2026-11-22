# Programa con L298N: captura rápida de datos brutos y postprocesamiento

| Campo | Detalle |
|-------|---------|
| **Título** | Motor DC JGA25-370 con L298N: captura rápida y postprocesamiento |
| **Fecha de creación** | 22/11/2026 |
| **Autores** | Mario Alejandro Betancourt Franco (23440) · Claude Opus 5.5 (Anthropic), asistente de IA |
| **Archivos** | [`MotorDC_L298N.ino`](../../ParteExperimental/MotorDC_L298N/MotorDC_L298N.ino) · [`protocolo_motor.py`](../../ParteExperimental/protocolo_motor.py) · [`captura_respuesta.py`](../../ParteExperimental/captura_respuesta.py) · [`postprocesamiento.py`](../../ParteExperimental/postprocesamiento.py) · [`arduino_simulado.py`](../../ParteExperimental/arduino_simulado.py) |
| **Versión anterior** | [`Programa_RespuestaEscalon.md`](Programa_RespuestaEscalon.md) (driver MOSFET) |
| **Bitácora** | [`BitacoraUsoIA.md`](../BitacoraUsoIA.md), Entrada 12 |
| **Continúa en** | [`Controlador_PID.md`](Controlador_PID.md) (PID y aplicación del gemelo digital) |

---

> [!WARNING]
> **Aviso sobre el uso de IA.** Este código lo generó una herramienta de inteligencia artificial
> (Claude Opus 5.5, de Anthropic) a pedido del autor. **Se compiló para el Arduino Nano y se probó
> con datos sintéticos y con un Arduino simulado, pero no con el hardware real.** El equipo debe
> revisar el código, las conexiones y las constantes, y probarlo con cuidado, empezando con el
> motor sin carga. La IA puede equivocarse. La responsabilidad sobre el uso del código y sobre los
> resultados es del equipo.

---

## Prompt original

Copiado textualmente, como lo escribió el autor.

```text
Hola Claude. Al final decidí utilizar un L298N. Por favor quiero que me ayudes modificando la progra del arduino.

* Salida del sensor de corriente ACS712-5 en A0
* ENB del L298N en D3
* IN3 en D4
* IN4 en D5
* FASE A de encoder en D8
* FASE B de encoder en D9


Quiero que con el código receptor de Python recibamos información de los datos brutos de las fases del encoder encoder y datos brutos del sensor de corriente. Quiero que la transmisión de datos sea a la frecuencia más alta posible. Quiero que en el código de Python almacenes los resultados y en otro script hagas el postprocesamiento necesario para calcular la posición angular, la velocidad angular y la corriente.

Dime qué debo obtener para que eso funcione
```

## Conexiones

| Señal | Pin del Nano | Notas |
|-------|--------------|-------|
| VIOUT del ACS712-5 | A0 | El ACS712 va en serie con el motor (entre OUT3 u OUT4 y el motor). |
| ENB del L298N | D3 | Salida OC2B del Timer2 (PWM). **Quitar el puente (jumper) de ENB del módulo.** |
| IN3 | D4 | |
| IN4 | D5 | |
| Fase A del encoder | D8 | Pull-up interno activado. |
| Fase B del encoder | D9 | Pull-up interno activado. |
| GND | GND | **Tierra común**: Nano, L298N, fuente del motor, ACS712 y encoder. |

## Cómo funciona la captura rápida

- **Muestreo:** el ADC trabaja en conversión continua a 16 MHz / 16 / 13 ≈ **76 923 muestras/s**. En la interrupción de cada conversión se leen también las fases A y B (una sola lectura de `PINB`). Así corriente y encoder comparten la base de tiempo.
- **Trama:** 2 bytes por muestra con los **datos brutos**: 10 bits del ADC, el nivel de A y de B, un bit de motor encendido y un bit de pérdida. El primer byte tiene el bit 7 en 1, lo que permite resincronizar.
- **Por qué es la frecuencia más alta:**
  - El UART del ATmega328P a 16 MHz llega como máximo a 2 Mbaud, y 2 bytes por muestra son 20 bits en la línea: 1,54 Mbit/s (77 % del UART).
  - El siguiente prescaler del ADC (8) pediría 3,08 Mbit/s, que el UART no alcanza.
  - A 1 MHz de reloj, el ADC pierde algo de resolución efectiva (hoja de datos, sección 24.4).
- **Ensayo:** tres fases.
  - **Previa:** motor libre; sirve para medir el cero del sensor.
  - **Escalón:** PWM fijo en ENB.
  - **Desconexión:** motor libre, o freno dinámico si se elige.

  Las duraciones, el PWM y el sentido se cambian con la orden `C`, sin volver a programar el Nano.

## Postprocesamiento

[`postprocesamiento.py`](../../ParteExperimental/postprocesamiento.py) calcula:

1. **Posición:** decodifica la cuadratura ×4 con la misma tabla del Arduino. La convierte con θ = 2π·cuenta/(4·PPR·N). Cuenta los saltos inválidos (A y B cambian a la vez), que indican que se muestreó demasiado lento.
2. **Velocidad,** por dos métodos:
   - **Diferencia centrada** con paso h (O(h²)). La cuantización de θ agrega un error de hasta q/(2h).
   - **Tiempo entre flancos,** con 4 flancos (un ciclo completo de A y B, lo que cancela la asimetría entre fases). Cuando el motor se detiene, la estimación se acota.
3. **Corriente:** i = (ADC − cero)·Vref/1024/S. El cero se mide en la fase previa y S = 0,185 V/A (ACS712 de 5 A).

## Decisiones de diseño

- **Pines del encoder:** D8 y D9 están en el mismo puerto (B), así que una sola lectura toma las dos fases en el mismo instante.
- **Interrupción del ADC:**
  - Se revisó en el ensamblador. Usa unos 114 ciclos de los 208 que hay entre muestras.
  - El contador de muestras de cada fase se partió en un byte y bloques de 256, para no hacer una resta de 32 bits en cada muestra.
  - Las funciones del driver se forzaron en línea: una llamada obligaba a guardar 12 registros por muestra.
- **Margen del UART:** se simuló ciclo a ciclo (UART con doble buffer, interrupción y lazo de transmisión). El buffer nunca pasa de 2 bytes ocupados; empezaría a perder datos con una interrupción de unos 150 ciclos.
- **Datos guardados:** el receptor guarda los bytes tal cual llegaron (`.bin`), los datos brutos decodificados (`_crudo.csv`) y la configuración (`.json`). El cálculo físico queda en otro script, como se pidió.

## Qué hace falta para que funcione

- **Hardware:**
  - quitar el jumper de ENB;
  - unir todas las tierras;
  - alimentar el encoder con 5 V.
- **Datos del motor:** pulsos por vuelta del encoder (PPR) en el eje del motor y reducción N de la caja. El código asume 11 PPR como valor común, pero hay que confirmarlo.
- **Mediciones:**
  - el 5 V real del Nano (Vref del ADC);
  - el voltaje real en los bornes del motor, porque el L298N tiene una caída interna de un par de voltios.
- **Software:**
  - Arduino IDE con el driver del adaptador USB-serie (CH340 o FT232);
  - Python con `pyserial`, `numpy` y `matplotlib`;
  - comprobar que la computadora acepta 2 000 000 baudios. Si no, usar 1 000 000 y `PRESCALER_ADC_RAPIDO = 32`.

## Uso

```text
python ParteExperimental/captura_respuesta.py COM5 --salida datos/ensayo1 --procesar --ppr 11 --reduccion 34
python ParteExperimental/postprocesamiento.py datos/ensayo1 --ppr 11 --reduccion 34
python ParteExperimental/captura_respuesta.py SIM --procesar      (sin hardware: Arduino simulado)
```

## Verificación

- **Compilación:**
  - avr-gcc 7.3.0, core AVR 1.8.6 (Nano), con `-Wall -Wextra` y sin advertencias.
  - Versión con PID corregido: 12 926 B de flash (39,4 %) y 691 B de RAM (33,7 %).
- **Decodificador** (200 000 tramas sintéticas):
  - recupera exactamente el ADC, el bit del motor y la cuenta del encoder;
  - con un byte perdido y uno basura, se resincroniza y pierde una sola trama.
- **Velocidad** (perfil conocido): error relativo medio de 0,37 % por flancos y de 1,8 % por diferencia centrada (h = 2 ms).
- **Cadena completa con el Arduino simulado:**
  - 138 460 tramas sin pérdidas;
  - la velocidad de régimen (792 rad/s) coincide con la que se calcula a mano con el modelo (≈ 791,6 rad/s).
- **No se probó con el hardware real.**
