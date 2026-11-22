# Programa de captura: respuesta al escalón y a la desconexión del motor DC

> [!NOTE]
> **Versión 1 (driver MOSFET), reemplazada el 22/11/2026.** El autor cambió el driver por un L298N.
> El programa se renombró a [`MotorDC_L298N.ino`](../../ParteExperimental/MotorDC_L298N/MotorDC_L298N.ino)
> y se reescribió; ver [`Programa_L298N.md`](Programa_L298N.md) y la Entrada 12 de la bitácora.
> Este documento y la copia del código que contiene se conservan como registro de la versión 1;
> sus enlaces a `RespuestaEscalonMotorDC.ino` ya no existen en el repositorio (están en el historial de git).

| Campo | Detalle |
|-------|---------|
| **Título** | Respuesta al escalón y a la desconexión de un motor DC JGA25-370 |
| **Fecha de creación** | 22/11/2026 |
| **Autores** | Mario Alejandro Betancourt Franco (23440) · Claude Opus 5.5 (Anthropic), asistente de IA |
| **Archivos** | [`RespuestaEscalonMotorDC.ino`](../../ParteExperimental/RespuestaEscalonMotorDC/RespuestaEscalonMotorDC.ino) (Arduino Nano) · [`captura_respuesta.py`](../../ParteExperimental/captura_respuesta.py) (computadora) |
| **Circuito** | [`Esquematico_Circuito.md`](Esquematico_Circuito.md) |
| **Bitácora** | [`BitacoraUsoIA.md`](../BitacoraUsoIA.md), Entrada 6 |

---

> [!WARNING]
> **Aviso sobre el uso de IA.** El código de esta parte del proyecto lo generó una herramienta de
> inteligencia artificial (Claude Opus 5.5, de Anthropic) a pedido del autor. **Se compiló para el
> Arduino Nano, pero no se ha probado con el hardware real.** Antes de usarlo, el equipo debe revisar
> el código, las conexiones y las constantes, y probarlo con cuidado, empezando con el motor sin carga.
> La IA puede equivocarse. La responsabilidad sobre el uso del código y sobre los resultados es del equipo.

---

## Descripción

El programa usa el Arduino Nano para medir la respuesta del motor DC JGA25-370 en dos momentos:

1. **Escalón:** el MOSFET conecta el motor al bus de 12 V.
2. **Desconexión:** el MOSFET se apaga. La corriente se descarga por el diodo de rueda libre y el motor gira libre hasta detenerse.

En cada muestra se registran:
- la **corriente**, con el sensor ACS712T de 5 A y el ADC en modo continuo;
- la **posición**, con el encoder en cuadratura, contando ×4.

Los datos se envían en tiempo real a la computadora por el UART. El script de Python los guarda en un CSV.

Un ensayo empieza cuando la computadora envía la letra `E` y tiene tres fases:

| Fase | Duración (constante) | Motor | Para qué sirve |
|------|----------------------|-------|----------------|
| Previa | `TIEMPO_PREVIO_MS` = 200 ms | Apagado | Medir el cero del sensor de corriente |
| Escalón | `TIEMPO_ENCENDIDO_MS` = 1500 ms | Encendido | Respuesta al escalón de voltaje |
| Desconexión | `TIEMPO_APAGADO_MS` = 1500 ms | Apagado | Respuesta a la desconexión |

## Prompts originales

Los prompts se copian textualmente, como los escribió el autor.

**Prompt 1 (22/11/2026):**

```text
Mira. Necesito hacer también una parte práctica del proyecto. Quisiera que me ayudes escribiendo un código para un Arduino Nano, que esté conectado a un driver de MOSFET para un motor JGA25-370 con encoder. El motor tiene conectado un sensor de corriente SENSOR DE CORRIENTE ACS712T, 5 Amperios.

El código debe poder accionar el driver para capturar la respuesta al escalón y a la desconexión del motor DC. Quisiera que esto se haga a través de mediciones del ADC con la frecuencia de muestreo más alta posible y con la transmisión de datos a mi computadora a través del periférico serial UART a un baudaje adecuado.

Por favor crea un md correspondiente, incluyendo este prompt escrito tal y como te lo mando por acá (incluyendo esta parte). Incluye un resumen del prompt escrito en el código de arduino, junto con un disclaimer sobre el uso de IA para esta parte del proyecto, junto con un encabezado con título, fecha de creación, autor (inclúyete tu también), descripción de lo que hace el código y el código en cuestión. 

Quiero que el código resultante esté documentado adecuadamente con límeas de código explicando qué hace cada cosa. 

Quiero que hagas las definiciones de constantes para los pines donde va conectada cada cosa.

Dale, vuele
```

**Prompt 2 (22/11/2026, enviado mientras se trabajaba en el primero; cambió los pines del programa):**

```text
Quisiera que coloques también un esquemático del circuito propuesto. El Arduino tiene conectado a un pin ADC el sensor de corriente y a otro pin una salida a un driver compuesto de un MOSFET IRFZ44N con un resistor de compuerta de 180 ohms y un resistor pull-down de 10k con un diodo de la serie 1N540X. El driver conecta las entradas de potencia del motor DC a un bus de 12 V y a Tierra. Las salidas del encoder del motor van a pines lógicos del arduino. Quisiera, de ser posible, que utilices los pines en un mismo lado del arduino nano.

Para el esquemático, utiliza la librería de símbolos para Inkscape, que dejo adjunta como imagen.

Coloca el MD correspondiente y la documentación respectiva en la parte de uso de IA. No olvides hacer lo mismo para la programación del .ino.
```

*(Con el prompt 2 se adjuntó una imagen de la librería de símbolos ElCompLib para Inkscape.)*

**Prompt 3 (22/11/2026; cambió el pin del driver):**

```text
Tengo una pequeña corrección sobre el esquemático. Me gustaría utilizar un pin del Arduino nano que tenga funcionalidad PWM para la entrada del driver del motor. 

También quisiera que recomienda un circuito de acondicionamiento de señal (quizás otra etapa de un switch con un transistor de gama más baja) para conertir la señal lógica de 0-5V del Arduino Nano en una señal de 0-12 V necesarios para saturar el MOSFET. Considera utilizar un BJT NPN como el 2N3904. Argumentame si este diseño es adecuado o no.

Si el diseño es adecuado, procede con las correcciones sobre el esquemático
```

*(Tras evaluar la etapa de 12 V con simulaciones de LTspice, se decidió mantener el driver original con 5 V directo a la compuerta, porque la corriente del motor se mantiene por debajo de 2 A. Ver [`Simulaciones_Driver.md`](Simulaciones_Driver.md).)*

## Resumen del prompt

Escribir un programa para un Arduino Nano conectado a un driver MOSFET que acciona un motor JGA25-370 con encoder y un sensor de corriente ACS712T de 5 A. El programa debe:
- accionar el driver para capturar la respuesta al escalón y a la desconexión;
- medir con el ADC a la frecuencia de muestreo más alta posible;
- transmitir los datos a la computadora por UART a un baudaje adecuado;
- estar bien documentado, con constantes para los pines;
- de ser posible, usar pines de un mismo lado del Nano;
- usar un pin con PWM para el driver.

## Decisiones de diseño

### Frecuencia de muestreo y baudaje

**El límite real es el UART, no el ADC.**
- **Lo que puede el ADC:** el ATmega328P podría convertir a unas 77 kmuestras/s (prescaler 16).
- **Lo que ocupa cada muestra:** 4 bytes, con la corriente y el conteo del encoder.
- **Por qué hay que transmitir en tiempo real:** un ensayo de unos 3 s no cabe en los 2 KB de RAM del Nano.

| Parámetro | Valor | Motivo |
|-----------|-------|--------|
| Baudaje | **2 000 000** | Máximo exacto a 16 MHz (UBRR0 = 0 con U2X0). El CH340 y el FT232RL del Nano lo soportan |
| Prescaler del ADC | **32** | Reloj del ADC de 500 kHz |
| Frecuencia de muestreo | **≈ 38 462 muestras/s** (Ts ≈ 26 µs) | 16 MHz / 32 / 13 ciclos por conversión |
| Uso del UART | ≈ 77 % | 38 462 × 4 bytes × 10 bits = 1,54 Mbit/s de 2 Mbit/s |

**Si la computadora no acepta 2 Mbaud**, cambiar a `BAUDIOS = 1000000` y `PRESCALER_ADC = 64` (≈ 19 231 muestras/s). El programa comprueba al compilar que el UART alcance a enviar todas las muestras; si no alcanza, no compila.

**Resolución:** con un reloj de ADC mayor a 200 kHz, el ADC pierde algo de resolución efectiva (hoja de datos del ATmega328P, sección 24.4). Con el ACS712 de 5 A (185 mV/A) y referencia de 5 V, 1 LSB equivale a unos 26 mA.

**Tiempo de cada muestra:** el ADC en modo continuo toma una muestra cada 13 ciclos de su reloj, sin importar cuánto tarde la interrupción en atenderse. Por eso no se envía una marca de tiempo: el tiempo es `t = n / fs`.

### Formato de la trama (4 bytes por muestra)

| Byte | Bit 7 | Bit 6 | Bits 5–0 |
|------|-------|-------|----------|
| 0 | 1 (inicio de trama) | M: motor encendido | ADC[9:4] |
| 1 | 0 | ADC[3] | ADC[2:0] · ENC[15:13] |
| 2 | 0 | ENC[12:6] (7 bits) | |
| 3 | 0 | P: se perdieron tramas antes | ENC[5:0] |

- Solo el byte 0 tiene el bit 7 en 1. Así el receptor se resincroniza si pierde un byte.
- Al final se envían dos bytes `0xFF` seguidos, que no pueden aparecer dentro de una trama, y después una línea de texto `FIN tramas_enviadas=… tramas_perdidas=…`.
- El conteo del encoder es de 16 bits y da la vuelta al llegar al límite. El script lo "desenrolla" en un conteo continuo.

### Pines

El sensor y el encoder están en el lado analógico del Nano (A0–A2, 5V y GND), como pidió el autor en el prompt 2. El driver va en **D9**, en el lado digital, porque el prompt 3 pidió un pin con PWM, y en el lado analógico ningún pin tiene PWM por hardware.

| Constante | Pin | Conexión |
|-----------|-----|----------|
| `PIN_SENSOR_CORRIENTE` | A0 | VIOUT del ACS712T |
| `PIN_ENCODER_A` | A1 | Canal A del encoder (interrupción por cambio de pin PCINT9) |
| `PIN_ENCODER_B` | A2 | Canal B del encoder (PCINT10) |
| `PIN_DRIVER_MOTOR` | **D9** | Compuerta del IRFZ44N, a través de R1 = 180 Ω (PWM de Timer1, OC1A) |
| `PIN_LED_CAPTURA` | D13 | LED de la placa (encendido durante la captura) |
| — | 5V, GND | Alimentación del ACS712T y del encoder; tierra común con el bus de 12 V |

- **Por qué D9:** Timer1 genera su PWM y millis() no lo usa, así que su frecuencia (por ejemplo, 20 kHz para el PID) se puede cambiar sin afectar el tiempo. En este programa D9 funciona como salida digital para el escalón.
- **Encoder:** como en el lado analógico no están INT0 ni INT1 (D2 y D3), usa la interrupción por cambio de pin PCINT1. Funciona igual para contar en cuadratura.

## Cómo usarlo

1. Armar el circuito del [esquemático](Esquematico_Circuito.md).
2. Abrir `RespuestaEscalonMotorDC.ino` en el IDE de Arduino.
   - Placa: **Arduino Nano**.
   - Procesador: **ATmega328P**, o **ATmega328P (Old Bootloader)** si la carga falla.
   - Subir el programa.
3. En la computadora, instalar pyserial y ejecutar el script:
   ```powershell
   pip install pyserial
   ```
   ```powershell
   python ParteExperimental\captura_respuesta.py COM5 --salida ensayo1.csv
   ```
   Cambiar `COM5` por el puerto del Nano.
4. El CSV tiene las columnas `n, t_s, motor, adc, corriente_A, pulsos_encoder, perdida`.
   - **Corriente:** se calcula con el cero medido en la fase previa.
   - **Velocidad:** se obtiene derivando numéricamente `pulsos_encoder`. Los pulsos por vuelta del eje de salida son 4 × PPR del encoder × relación de la caja reductora; revisar la hoja del motor.

> El Monitor Serie del IDE no sirve para ver estos datos, porque son binarios. Usar el script.

## Observaciones sobre el hardware

Son advertencias para que el equipo las revise. No son cambios al circuito que propuso el autor.

- **IRFZ44N con 5 V en la compuerta.** El IRFZ44N no es de nivel lógico: su R<sub>DS(on)</sub> solo está garantizada con V<sub>GS</sub> = 10 V. Aun así, la simulación en LTspice con el umbral de peor caso (4 V) muestra que, con la corriente del motor por debajo de 2 A, conduce bien en el ensayo de escalón (V<sub>DS</sub> ≈ 0,125 V, 0,23 W). **Para el PID con PWM a 20 kHz disiparía entre 0,9 y 1,8 W y necesitaría disipador**. Ver el [reporte de simulaciones](../../ParteExperimental/Simulaciones/ReporteSimulaciones.md). Conviene medir V<sub>DS</sub> con el motor encendido. La alternativa de nivel lógico es el IRLZ44N.
- **Diodo 1N540X.** Se interpretó como diodo de rueda libre en paralelo con el motor y el sensor. Es un rectificador de recuperación lenta: sirve para el ensayo de desconexión, pero para PWM conviene un diodo Schottky.
- **Ubicación del sensor.** El ACS712T va dentro del lazo del diodo, en serie con el motor. Así mide tanto la corriente con el motor encendido como la corriente de rueda libre después de la desconexión.
- **Medición radiométrica.** El ACS712T y la referencia del ADC (AVcc) usan los mismos 5 V del Nano. Así las variaciones del voltaje del USB se cancelan en buena parte.
- **Ruido en el ADC.** El driver conmuta grandes corrientes cerca del sensor. En las muestras del instante del escalón y de la desconexión puede verse una perturbación; conviene cablear la potencia lejos de la señal de A0.

## Verificación realizada

- **Compilación.** Se compiló con avr-gcc 7.3.0 y el core Arduino AVR 1.8.6 (variante `eightanaloginputs` del Nano), con `-Wall -Wextra` y **sin advertencias**. Usa 5588 bytes de flash (17,1 %) y 493 bytes de RAM (24,1 %).
- **Tiempo de las interrupciones.** Según el ensamblador, la del ADC dura como máximo unos 15 µs y la del encoder unos 6 µs. Aun seguidas, caben en los 26 µs que hay entre muestras.
- **Decodificador.** Se probó con 5000 tramas sintéticas empaquetadas igual que en el Arduino, con un byte basura y una marca de pérdida. Recuperó todas las muestras exactamente.

**No verificado:**
- el funcionamiento con el hardware real;
- la estabilidad de 2 Mbaud con el adaptador USB-serie y la computadora del equipo;
- el número de pulsos por vuelta del encoder.

## Código del Arduino

Copia de [`RespuestaEscalonMotorDC.ino`](../../ParteExperimental/RespuestaEscalonMotorDC/RespuestaEscalonMotorDC.ino) al 22/11/2026. Si hay diferencias, vale el archivo `.ino`.

```cpp
/*
 * =============================================================================
 *  RESPUESTA AL ESCALÓN Y A LA DESCONEXIÓN DE UN MOTOR DC JGA25-370
 * =============================================================================
 *  Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
 *  Motor DC: gemelo digital y control PID (parte práctica)
 *
 *  Archivo          : RespuestaEscalonMotorDC.ino
 *  Fecha de creación: 22/11/2026
 *  Autores          : Mario Alejandro Betancourt Franco (23440)
 *                     Claude Opus 5.5 (Anthropic), asistente de IA
 *  Placa            : Arduino Nano (ATmega328P a 16 MHz)
 *  Circuito         : ParteExperimental/Esquematico_MotorDC.svg
 *
 * -----------------------------------------------------------------------------
 *  DESCRIPCIÓN
 * -----------------------------------------------------------------------------
 *  Captura la respuesta de un motor DC JGA25-370 con encoder a:
 *    1) un escalón de voltaje (el MOSFET IRFZ44N conecta el motor al bus de 12 V), y
 *    2) la desconexión (el MOSFET se apaga y la corriente circula por el diodo
 *       de rueda libre 1N540X hasta extinguirse; el motor queda libre).
 *
 *  En cada muestra se mide:
 *    - la corriente del motor con el sensor ACS712T de 5 A, usando el ADC en
 *      modo de conversión continua (free running) controlado por interrupción;
 *    - la posición del eje con el encoder de cuadratura (conteo x4 con la
 *      interrupción por cambio de pin PCINT1).
 *
 *  Los datos se envían a la computadora por el UART a 2 000 000 baudios, en
 *  tiempo real, con tramas binarias de 4 bytes. La frecuencia de muestreo es
 *  F_CPU / prescaler / 13 = 16 MHz / 32 / 13 ≈ 38 462 muestras/s. Es la más
 *  alta que el UART puede transmitir sin perder datos: el ADC solo podría ir
 *  al doble (prescaler 16), pero el UART no alcanzaría a enviar esas muestras.
 *
 *  El sensor y el encoder van en el lado analógico del Nano (A0 a A2). El
 *  driver va en D9, del lado digital, porque necesita PWM por hardware.
 *
 *  Secuencia de un ensayo (se inicia al enviar la letra 'E' por el puerto serie):
 *    a) TIEMPO_PREVIO_MS   : motor apagado. Sirve para medir el cero del sensor.
 *    b) TIEMPO_ENCENDIDO_MS: motor encendido. Respuesta al escalón.
 *    c) TIEMPO_APAGADO_MS  : motor apagado. Respuesta a la desconexión.
 *
 *  El script ParteExperimental/captura_respuesta.py recibe los datos, los
 *  decodifica y los guarda en un archivo CSV.
 *
 * -----------------------------------------------------------------------------
 *  RESUMEN DEL PROMPT QUE ORIGINÓ ESTE CÓDIGO
 * -----------------------------------------------------------------------------
 *  Escribir un código para un Arduino Nano conectado a un driver MOSFET que
 *  acciona un motor JGA25-370 con encoder y un sensor de corriente ACS712T de
 *  5 A. El código debe accionar el driver para capturar la respuesta al escalón
 *  y a la desconexión del motor, medir con el ADC a la frecuencia de muestreo
 *  más alta posible y transmitir los datos a la computadora por UART a un
 *  baudaje adecuado. Debe estar bien documentado y definir constantes para los
 *  pines. En un segundo prompt se pidió usar, de ser posible, pines de un
 *  mismo lado del Nano, y se describió el driver (IRFZ44N, 180 Ω de compuerta,
 *  10 kΩ de pull-down y diodo 1N540X, con el motor entre el bus de 12 V y
 *  tierra). En un tercer prompt se pidió usar un pin con PWM para el driver.
 *  Los prompts completos están en
 *  UsoIA/ParteExperimental/Programa_RespuestaEscalon.md.
 *
 * -----------------------------------------------------------------------------
 *  AVISO SOBRE EL USO DE INTELIGENCIA ARTIFICIAL
 * -----------------------------------------------------------------------------
 *  Este código lo generó una herramienta de inteligencia artificial (Claude
 *  Opus 5.5, de Anthropic) a pedido del autor. Se compiló para el Arduino Nano,
 *  pero NO se ha probado con el hardware real. Antes de usarlo, el equipo
 *  debe revisar el código, las conexiones y los valores de las constantes, y
 *  verificar su funcionamiento con cuidado, empezando con el motor sin carga.
 *  La IA puede equivocarse. La responsabilidad sobre el uso de este código y
 *  sobre los resultados del proyecto es del equipo. El uso de IA está
 *  registrado en UsoIA/BitacoraUsoIA.md.
 * =============================================================================
 */

#include <Arduino.h>        // Funciones base de Arduino (pinMode, Serial, etc.)
#include <avr/io.h>         // Nombres de los registros del ATmega328P (ADCSRA, UDR0, ...)
#include <avr/interrupt.h>  // Macro ISR() para escribir rutinas de interrupción

// =============================================================================
//  1. PINES (cambiar aquí si el cableado es distinto)
// =============================================================================
// El sensor y el encoder están en el lado analógico del Nano (A0 a A2, 5V y
// GND). El driver va en D9, en el lado digital, porque ningún pin del lado
// analógico tiene PWM por hardware. A0 a A5 también funcionan como digitales.

// Salida hacia la compuerta del MOSFET IRFZ44N, a través de R1 = 180 Ω (la
// compuerta tiene un pull-down de 10 kΩ). HIGH = motor encendido, LOW = apagado.
// Se usa D9 porque tiene PWM por hardware (Timer1, salida OC1A), necesario
// para el futuro control PID. Timer1 no lo usa millis(), así que su frecuencia
// de PWM se puede cambiar sin afectar el tiempo. D9 está en el lado digital
// del Nano; los demás pines siguen en el lado analógico.
// En este programa D9 se usa como salida digital (escalón): no se llama a
// analogWrite(), así que el pin lo controla el registro PORTB.
const uint8_t PIN_DRIVER_MOTOR = 9;

// Canal A del encoder (A1 = PC1, interrupción por cambio de pin PCINT9).
const uint8_t PIN_ENCODER_A = A1;

// Canal B del encoder (A2 = PC2, interrupción por cambio de pin PCINT10).
const uint8_t PIN_ENCODER_B = A2;

// Salida analógica (VIOUT) del sensor de corriente ACS712T de 5 A.
const uint8_t PIN_SENSOR_CORRIENTE = A0;

// LED de la placa (D13, en el mismo lado). Se enciende durante la captura.
const uint8_t PIN_LED_CAPTURA = LED_BUILTIN;

// El driver debe ir en un pin con PWM de Timer1 (D9 o D10), para el futuro PID.
static_assert(PIN_DRIVER_MOTOR == 9 || PIN_DRIVER_MOTOR == 10,
              "El driver debe ir en D9 o D10 (PWM por hardware de Timer1)");

// El encoder usa la interrupción PCINT1, que atiende solo los pines A0 a A5.
static_assert(PIN_ENCODER_A >= A0 && PIN_ENCODER_A <= A5 &&
              PIN_ENCODER_B >= A0 && PIN_ENCODER_B <= A5,
              "El encoder debe ir en pines entre A0 y A5 (interrupcion PCINT1)");

// El sensor debe ir en una entrada analógica del Nano (A0 a A7).
static_assert(PIN_SENSOR_CORRIENTE >= A0 && PIN_SENSOR_CORRIENTE <= A7,
              "El sensor de corriente debe ir en una entrada analogica (A0 a A7)");

// Cada señal debe tener su propio pin.
static_assert(PIN_SENSOR_CORRIENTE != PIN_ENCODER_A &&
              PIN_SENSOR_CORRIENTE != PIN_ENCODER_B &&
              PIN_SENSOR_CORRIENTE != PIN_DRIVER_MOTOR &&
              PIN_ENCODER_A != PIN_ENCODER_B &&
              PIN_DRIVER_MOTOR != PIN_ENCODER_A &&
              PIN_DRIVER_MOTOR != PIN_ENCODER_B,
              "Hay dos senales asignadas al mismo pin");

// =============================================================================
//  2. CONFIGURACIÓN DEL ENSAYO
// =============================================================================

// Duración de cada fase del ensayo, en milisegundos.
const uint32_t TIEMPO_PREVIO_MS    = 200;    // Motor apagado (cero del sensor)
const uint32_t TIEMPO_ENCENDIDO_MS = 1500;   // Respuesta al escalón
const uint32_t TIEMPO_APAGADO_MS   = 1500;   // Respuesta a la desconexión

// Velocidad del UART. A 16 MHz, 2 000 000 baudios es exacto (UBRR0 = 0 con U2X0).
// El conversor USB-serie del Nano (CH340 o FT232RL) soporta esta velocidad.
// Si la computadora no la acepta, usar 1 000 000 y PRESCALER_ADC = 64.
const uint32_t BAUDIOS = 2000000UL;

// Prescaler del reloj del ADC (2, 4, 8, 16, 32, 64 o 128).
// Reloj del ADC = 16 MHz / 32 = 500 kHz. Cada conversión toma 13 ciclos de ese
// reloj, así que la frecuencia de muestreo es 500 kHz / 13 ≈ 38 462 muestras/s.
// Por encima de 200 kHz de reloj, el ADC pierde algo de resolución efectiva
// (hoja de datos del ATmega328P, sección 24.4).
const uint8_t PRESCALER_ADC = 32;

// =============================================================================
//  3. CONSTANTES DERIVADAS (no hace falta modificarlas)
// =============================================================================

// Bytes que ocupa cada muestra en el UART (ver el formato de trama en la sección 7).
const uint8_t BYTES_POR_TRAMA = 4;

// Ciclos de reloj del ADC por conversión en modo continuo.
const uint8_t CICLOS_POR_CONVERSION = 13;

// Frecuencia de muestreo en Hz, como número real (para el encabezado de texto).
constexpr float FRECUENCIA_MUESTREO_HZ =
    (float)F_CPU / (float)PRESCALER_ADC / (float)CICLOS_POR_CONVERSION;

// Convierte el prescaler a los bits ADPS2:0 del registro ADCSRA.
// Devuelve 0xFF si el valor no es válido.
constexpr uint8_t bitsPrescalerADC(uint8_t prescaler) {
  return prescaler == 2   ? 1 :
         prescaler == 4   ? 2 :
         prescaler == 8   ? 3 :
         prescaler == 16  ? 4 :
         prescaler == 32  ? 5 :
         prescaler == 64  ? 6 :
         prescaler == 128 ? 7 : 0xFF;
}
static_assert(bitsPrescalerADC(PRESCALER_ADC) != 0xFF,
              "PRESCALER_ADC debe ser 2, 4, 8, 16, 32, 64 o 128");

// Comprobación al compilar: el UART debe poder enviar todas las muestras.
// Cada byte ocupa 10 bits en la línea (1 de inicio, 8 de datos, 1 de parada).
// Se exige usar como máximo el 90 % de la capacidad, para dejar margen.
static_assert((F_CPU / PRESCALER_ADC / CICLOS_POR_CONVERSION) * BYTES_POR_TRAMA * 10UL
                  <= BAUDIOS * 9UL / 10UL,
              "El UART no alcanza a transmitir todas las muestras: suba BAUDIOS o suba PRESCALER_ADC");

// Número de muestras de cada fase.
const uint32_t MUESTRAS_PREVIAS =
    (uint32_t)(TIEMPO_PREVIO_MS * FRECUENCIA_MUESTREO_HZ / 1000.0f);
const uint32_t MUESTRAS_ENCENDIDO =
    (uint32_t)(TIEMPO_ENCENDIDO_MS * FRECUENCIA_MUESTREO_HZ / 1000.0f);
const uint32_t MUESTRAS_APAGADO =
    (uint32_t)(TIEMPO_APAGADO_MS * FRECUENCIA_MUESTREO_HZ / 1000.0f);

// Índices en los que cambia el estado del motor, y total de muestras.
const uint32_t MUESTRA_ENCENDER = MUESTRAS_PREVIAS;
const uint32_t MUESTRA_APAGAR   = MUESTRAS_PREVIAS + MUESTRAS_ENCENDIDO;
const uint32_t MUESTRAS_TOTALES = MUESTRA_APAGAR + MUESTRAS_APAGADO;

static_assert(MUESTRAS_PREVIAS > 0 && MUESTRAS_ENCENDIDO > 0 && MUESTRAS_APAGADO > 0,
              "Cada fase del ensayo debe durar al menos una muestra");

// Canal del multiplexor del ADC que corresponde al pin del sensor (A0 -> 0, ...).
const uint8_t CANAL_ADC = PIN_SENSOR_CORRIENTE - A0;

// Tamaño del buffer circular de transmisión. Debe ser 256: los índices son de
// 8 bits y dan la vuelta solos (255 + 1 = 0), sin operaciones extra.
const uint16_t TAMANO_BUFFER = 256;

// Marcador binario de fin de datos: dos bytes con el bit 7 en 1 seguidos.
// No puede aparecer dentro de una trama, porque en una trama solo el primer
// byte tiene el bit 7 en 1.
const uint8_t BYTE_FIN = 0xFF;

// =============================================================================
//  4. TABLA DEL DECODIFICADOR DE CUADRATURA
// =============================================================================
// El estado del encoder se codifica como (A << 1) | B, es decir, 0 a 3.
// El índice de la tabla es (estado_anterior << 2) | estado_actual.
// Cada entrada vale +1 (avance), -1 (retroceso) o 0 (sin cambio, o un salto
// inválido de dos estados, que se ignora).
// Si el conteo sale con el signo al revés, intercambiar los cables A y B.
const int8_t TABLA_CUADRATURA[16] = {
   0, -1, +1,  0,
  +1,  0,  0, -1,
  -1,  0,  0, +1,
   0, +1, -1,  0
};

// =============================================================================
//  5. VARIABLES COMPARTIDAS CON LAS INTERRUPCIONES
// =============================================================================
// Las variables que se usan dentro y fuera de las interrupciones son 'volatile',
// para que el compilador las lea de memoria cada vez.

volatile int16_t  conteoEncoder = 0;        // Posición del encoder, en pulsos (x4)
volatile uint8_t  estadoEncoderPrevio = 0;  // Último estado (A,B) leído

volatile uint8_t  bufferTx[TAMANO_BUFFER];  // Buffer circular de bytes por enviar
volatile uint8_t  cabeza = 0;               // Donde escribe la interrupción del ADC
volatile uint8_t  cola = 0;                 // Donde lee el lazo que transmite

volatile uint32_t indiceMuestra = 0;        // Muestras procesadas en el ensayo
volatile bool     motorEncendido = false;   // Estado actual del driver
volatile bool     capturaActiva = false;    // true mientras el ADC está midiendo
volatile bool     huboPerdida = false;      // Se perdió al menos una trama desde la última enviada
volatile uint16_t tramasPerdidas = 0;       // Total de tramas perdidas (buffer lleno)

// Acceso directo a los registros de los pines, calculado en setup() a partir
// de las constantes de la sección 1. Es mucho más rápido que digitalWrite()
// y digitalRead(), lo que importa dentro de las interrupciones.
volatile uint8_t *registroSalidaMotor;      // Registro PORTx del pin del driver
uint8_t mascaraMotor;                       // Bit del pin del driver en ese registro
volatile uint8_t *registroEntradaEncoder;   // Registro PINx de los pines del encoder
uint8_t mascaraEncoderA;                    // Bit del canal A
uint8_t mascaraEncoderB;                    // Bit del canal B

// =============================================================================
//  6. FUNCIONES AUXILIARES
// =============================================================================

// Enciende el motor: pone en HIGH la compuerta del MOSFET.
inline void encenderMotor() {
  *registroSalidaMotor |= mascaraMotor;     // Pone el bit del pin en 1
  motorEncendido = true;                    // Registra el nuevo estado
}

// Apaga el motor: pone en LOW la compuerta del MOSFET.
inline void apagarMotor() {
  *registroSalidaMotor &= ~mascaraMotor;    // Pone el bit del pin en 0
  motorEncendido = false;                   // Registra el nuevo estado
}

// Lee los dos canales del encoder y devuelve el estado (A << 1) | B (0 a 3).
inline uint8_t leerEstadoEncoder() {
  const uint8_t pines = *registroEntradaEncoder;         // Una sola lectura del puerto
  return ((pines & mascaraEncoderA) ? 2 : 0) |           // Bit 1: canal A
         ((pines & mascaraEncoderB) ? 1 : 0);            // Bit 0: canal B
}

// Configura el ADC en modo continuo, con interrupción al terminar cada conversión.
void iniciarADC() {
  ADMUX = (1 << REFS0)                   // Referencia = AVcc (5 V del Nano)
        | (CANAL_ADC & 0x07);            // Canal del sensor; resultado alineado a la derecha
  ADCSRB = 0;                            // Disparo automático: modo continuo (free running)
  if (CANAL_ADC < 6) {                   // A6 y A7 no tienen buffer digital
    DIDR0 |= (1 << CANAL_ADC);           // Desactiva el buffer digital del pin (menos ruido)
  }
  ADCSRA = (1 << ADEN)                   // Enciende el ADC
         | (1 << ADIF)                   // Escribir 1 borra una interrupción pendiente
         | (1 << ADATE)                  // Disparo automático (conversión continua)
         | (1 << ADIE)                   // Interrupción al terminar cada conversión
         | bitsPrescalerADC(PRESCALER_ADC);  // Prescaler del reloj del ADC
  ADCSRA |= (1 << ADSC);                 // Arranca la primera conversión
}

// Detiene las conversiones continuas y la interrupción del ADC.
inline void detenerADC() {
  ADCSRA &= ~((1 << ADATE) | (1 << ADIE));  // Termina la conversión en curso y no sigue
}

// Envía por texto la configuración del ensayo (una sola línea).
void imprimirConfiguracion() {
  Serial.print(F("fs_hz="));       Serial.print(FRECUENCIA_MUESTREO_HZ, 2);
  Serial.print(F(" n_previas="));  Serial.print(MUESTRAS_PREVIAS);
  Serial.print(F(" n_encendido="));Serial.print(MUESTRAS_ENCENDIDO);
  Serial.print(F(" n_apagado="));  Serial.print(MUESTRAS_APAGADO);
  Serial.print(F(" n_total="));    Serial.print(MUESTRAS_TOTALES);
  Serial.print(F(" prescaler="));  Serial.print(PRESCALER_ADC);
  Serial.print(F(" baudios="));    Serial.print(BAUDIOS);
  Serial.println();
}

// =============================================================================
//  7. RUTINAS DE INTERRUPCIÓN
// =============================================================================

// --- Encoder: se ejecuta en cada cambio de los pines habilitados de A0 a A5 ---
// (solo se habilitan los dos canales del encoder, en setup()).
ISR(PCINT1_vect) {
  const uint8_t estado = leerEstadoEncoder();                 // Estado actual (A,B)
  conteoEncoder += TABLA_CUADRATURA[(estadoEncoderPrevio << 2) | estado];  // +1, -1 o 0
  estadoEncoderPrevio = estado;                               // Guarda para el próximo cambio
}

// --- ADC: se ejecuta al terminar cada conversión, unas 38 462 veces por segundo ---
//
// Formato de la trama de 4 bytes (28 bits útiles):
//   byte 0: 1 M A9 A8 A7 A6 A5 A4   (bit 7 = 1 marca el inicio de la trama)
//   byte 1: 0 A3 A2 A1 A0 E15 E14 E13
//   byte 2: 0 E12 E11 E10 E9 E8 E7 E6
//   byte 3: 0 P E5 E4 E3 E2 E1 E0
// donde:
//   A9..A0 = lectura del ADC (10 bits, 0 a 1023)
//   E15..E0 = conteo del encoder (16 bits con signo; da la vuelta al llegar al límite)
//   M = 1 si el motor estaba encendido al procesar la muestra
//   P = 1 si se perdieron tramas justo antes de esta (buffer lleno)
// Solo el primer byte tiene el bit 7 en 1, así la computadora puede
// resincronizarse si pierde un byte.
//
// Tiempo de cada muestra: t = n / fs, con n el número de trama (desde 0).
// El ADC en modo continuo toma cada muestra a intervalos fijos de 13 ciclos
// de su reloj, sin importar cuánto tarde esta rutina en atenderse.
ISR(ADC_vect) {
  const uint16_t lectura = ADC;                         // Lee ADCL y ADCH (10 bits)
  const uint16_t pulsos = (uint16_t)conteoEncoder;      // Copia del conteo (aquí no la interrumpe el encoder)
  const uint8_t  bitMotor = motorEncendido ? 0x40 : 0;  // Bit M en la posición 6 del byte 0

  uint8_t h = cabeza;                                   // Copia local del índice de escritura
  if ((uint8_t)(h - cola) < (TAMANO_BUFFER - BYTES_POR_TRAMA)) {  // ¿Caben 4 bytes más?
    bufferTx[h++] = 0x80 | bitMotor | (uint8_t)(lectura >> 4);                    // byte 0
    bufferTx[h++] = (uint8_t)((lectura & 0x0F) << 3) | (uint8_t)(pulsos >> 13);  // byte 1
    bufferTx[h++] = (uint8_t)(pulsos >> 6) & 0x7F;                                // byte 2
    bufferTx[h++] = (uint8_t)(pulsos & 0x3F) | (huboPerdida ? 0x40 : 0);          // byte 3
    cabeza = h;                                         // Publica la trama completa
    huboPerdida = false;                                // La marca de pérdida ya se envió
  } else {
    huboPerdida = true;                                 // Buffer lleno: la trama se pierde
    if (tramasPerdidas < 0xFFFF) tramasPerdidas++;      // Cuenta las tramas perdidas
  }

  const uint32_t procesadas = ++indiceMuestra;          // Muestras procesadas hasta ahora
  if (procesadas == MUESTRA_ENCENDER) {                 // Fin de la fase previa:
    encenderMotor();                                    //   escalón de voltaje
  } else if (procesadas == MUESTRA_APAGAR) {            // Fin de la fase encendida:
    apagarMotor();                                      //   desconexión del motor
  } else if (procesadas >= MUESTRAS_TOTALES) {          // Fin del ensayo:
    detenerADC();                                       //   deja de muestrear
    capturaActiva = false;                              //   avisa al lazo de transmisión
  }
}

// =============================================================================
//  8. ENSAYO COMPLETO
// =============================================================================
void ejecutarEnsayo() {
  // --- Encabezado de texto con la configuración, para la computadora ---
  Serial.print(F("INICIO "));
  imprimirConfiguracion();
  Serial.flush();                         // Espera a que salga todo el texto por el UART

  // --- Estado inicial (con interrupciones desactivadas, para que sea consistente) ---
  noInterrupts();
  apagarMotor();                          // Se asegura de que el motor parta apagado
  cabeza = 0;                             // Vacía el buffer de transmisión
  cola = 0;
  indiceMuestra = 0;                      // Reinicia el contador de muestras
  tramasPerdidas = 0;                     // Reinicia el contador de pérdidas
  huboPerdida = false;
  conteoEncoder = 0;                      // La posición inicial del ensayo es 0
  estadoEncoderPrevio = leerEstadoEncoder();  // Estado actual del encoder como referencia
  capturaActiva = true;                   // Marca el inicio de la captura
  interrupts();

  digitalWrite(PIN_LED_CAPTURA, HIGH);    // LED encendido durante la captura

  // Pausa la interrupción de Timer0 (la de millis()) para que no retrase a la
  // del ADC. millis() no avanza durante el ensayo; se restaura al final.
  const uint8_t timsk0Guardado = TIMSK0;
  TIMSK0 &= ~(1 << TOIE0);

  iniciarADC();                           // Empieza a muestrear (las fases las controla la ISR)

  // --- Transmisión: envía bytes mientras se mide y hasta vaciar el buffer ---
  // Se escribe directo en UDR0 (registro de datos del UART) en lugar de usar
  // Serial.write(), que es más lenta. Serial.flush() dejó el UART libre.
  while (capturaActiva || cabeza != cola) {
    if ((UCSR0A & (1 << UDRE0)) && (cabeza != cola)) {  // ¿UART libre y hay datos?
      UDR0 = bufferTx[cola];              // Envía un byte
      cola = cola + 1;                    // Avanza el índice (da la vuelta en 255 -> 0)
    }
  }

  // --- Cierre del ensayo ---
  apagarMotor();                          // Seguridad: el motor queda apagado
  TIMSK0 = timsk0Guardado;                // Reactiva millis()
  digitalWrite(PIN_LED_CAPTURA, LOW);     // Apaga el LED

  Serial.write(BYTE_FIN);                 // Marcador binario de fin de datos
  Serial.write(BYTE_FIN);
  Serial.print(F("\nFIN tramas_enviadas="));   // Resumen de texto del ensayo
  Serial.print(MUESTRAS_TOTALES - tramasPerdidas);
  Serial.print(F(" tramas_perdidas="));
  Serial.println(tramasPerdidas);
}

// =============================================================================
//  9. SETUP Y LOOP
// =============================================================================
void setup() {
  // Lo primero: el motor apagado. Mientras el Nano arranca, el pin queda como
  // entrada (alta impedancia) y el pull-down de 10 kΩ mantiene el MOSFET apagado.
  digitalWrite(PIN_DRIVER_MOTOR, LOW);
  pinMode(PIN_DRIVER_MOTOR, OUTPUT);

  // Registros y máscaras de los pines, a partir de las constantes de la sección 1.
  registroSalidaMotor    = portOutputRegister(digitalPinToPort(PIN_DRIVER_MOTOR));
  mascaraMotor           = digitalPinToBitMask(PIN_DRIVER_MOTOR);
  registroEntradaEncoder = portInputRegister(digitalPinToPort(PIN_ENCODER_A));  // A1 y A2 están en el mismo puerto (C)
  mascaraEncoderA        = digitalPinToBitMask(PIN_ENCODER_A);
  mascaraEncoderB        = digitalPinToBitMask(PIN_ENCODER_B);
  apagarMotor();

  pinMode(PIN_LED_CAPTURA, OUTPUT);       // LED indicador
  digitalWrite(PIN_LED_CAPTURA, LOW);

  // Encoder: entradas con resistencia de pull-up interna.
  pinMode(PIN_ENCODER_A, INPUT_PULLUP);
  pinMode(PIN_ENCODER_B, INPUT_PULLUP);
  estadoEncoderPrevio = leerEstadoEncoder();

  // Interrupción por cambio de pin para los dos canales del encoder.
  *digitalPinToPCMSK(PIN_ENCODER_A) |= (1 << digitalPinToPCMSKbit(PIN_ENCODER_A));  // Habilita el canal A
  *digitalPinToPCMSK(PIN_ENCODER_B) |= (1 << digitalPinToPCMSKbit(PIN_ENCODER_B));  // Habilita el canal B
  PCIFR = (1 << digitalPinToPCICRbit(PIN_ENCODER_A));    // Borra una bandera pendiente
  PCICR |= (1 << digitalPinToPCICRbit(PIN_ENCODER_A));   // Habilita el grupo PCINT1 (A0 a A5)

  // Sensor de corriente: entrada analógica (sin pull-up).
  pinMode(PIN_SENSOR_CORRIENTE, INPUT);

  // UART a la velocidad elegida.
  Serial.begin(BAUDIOS);

  // Mensaje de inicio (texto). La computadora lo puede ignorar.
  Serial.print(F("LISTO Motor JGA25-370. Enviar 'E' para ensayar o '?' para ver la configuracion. "));
  imprimirConfiguracion();
}

void loop() {
  // Espera órdenes de la computadora por el puerto serie.
  if (Serial.available() > 0) {
    const char orden = (char)Serial.read();
    if (orden == 'E' || orden == 'e') {
      ejecutarEnsayo();                   // Escalón + desconexión
    } else if (orden == '?') {
      imprimirConfiguracion();            // Solo muestra la configuración
    }
  }
}
```
