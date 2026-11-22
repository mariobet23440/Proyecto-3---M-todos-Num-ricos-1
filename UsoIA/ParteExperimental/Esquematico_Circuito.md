# Esquemático del circuito: motor DC JGA25-370 con L298N

| Campo | Detalle |
|-------|---------|
| **Título** | Esquemático del motor DC JGA25-370 con driver L298N, sensor ACS712-5 y encoder |
| **Fecha de creación** | 22/11/2026 (versión 1: driver MOSFET · versión 2: L298N) |
| **Autores** | Mario Alejandro Betancourt Franco (23440) · Claude Opus 5.5 (Anthropic), asistente de IA |
| **Archivo** | [`ParteExperimental/Esquematico_MotorDC.svg`](../../ParteExperimental/Esquematico_MotorDC.svg) (SVG editable en Inkscape) |
| **Programa** | [`Programa_L298N.md`](Programa_L298N.md) · [`MotorDC_L298N.ino`](../../ParteExperimental/MotorDC_L298N/MotorDC_L298N.ino) |
| **Bitácora** | [`BitacoraUsoIA.md`](../BitacoraUsoIA.md), Entradas 6 (versión 1) y 13 (versión 2) |

---

> [!WARNING]
> **Aviso sobre el uso de IA.** Este esquemático lo dibujó una herramienta de inteligencia artificial
> (Claude Opus 5.5, de Anthropic) a partir de la descripción del autor. **Revisen cada conexión antes de
> armar el circuito**, en especial las interpretaciones de la IA (abajo). La responsabilidad sobre el
> circuito armado es del equipo.

---

![Esquemático del motor DC con L298N](../../ParteExperimental/Esquematico_MotorDC.svg)

## Versión 2: driver L298N

### Prompts

Se copian textualmente. Los pines vienen del prompt del cambio al L298N (completo en [`Programa_L298N.md`](Programa_L298N.md)):

```text
* Salida del sensor de corriente ACS712-5 en A0
* ENB del L298N en D3
* IN3 en D4
* IN4 en D5
* FASE A de encoder en D8
* FASE B de encoder en D9
```

Pedido de actualizar el esquemático (22/11/2026):

```text
Corrige el PID, y los esquemáticos. Ya no necesito simulaciones (quítalas)
```

### Descripción del circuito

- **Driver.** Se usa el canal B del módulo L298N (U3):
  - D5 → IN4, D4 → IN3 y D3 (PWM del Timer2) → ENB;
  - el **puente (jumper) de ENB del módulo se quita** para que ENB lo controle el Nano;
  - la fuente de 12 V (V1) va a los bornes 12V y GND del módulo;
  - la salida de 5 V del módulo **no se conecta**.
- **Sensor de corriente.** El ACS712-5 (U2) va **en serie con el motor**: OUT3 → IP+ → IP− → terminal + del motor; OUT4 → terminal − del motor. Su salida OUT va a A0 (etiqueta `I_SEN`).
- **Encoder.** Las fases A y B del encoder Hall van a D8 y D9 (etiquetas `ENC_A` y `ENC_B`). Se alimenta con 5 V y GND del Nano.
- **Alimentación y tierra.**
  - El Nano se alimenta por USB; el ACS712 y el encoder toman 5 V del pin 5V del Nano.
  - **Todas las tierras son un solo nodo:** Nano, GND del módulo, negativo de V1, ACS712 y encoder.
- **Etiquetas de red.** Para que no se crucen cables, las conexiones largas usan etiquetas: **las etiquetas con el mismo nombre son el mismo nodo**.

### Pines del Nano

| Pin del Nano | Conexión | Constante en el `.ino` |
|--------------|----------|------------------------|
| A0 | OUT del ACS712 (`I_SEN`) | `PIN_SENSOR_CORRIENTE` |
| **D3 (PWM)** | ENB del L298N | `PIN_ENB` |
| D4 | IN3 del L298N | `PIN_IN3` |
| D5 | IN4 del L298N | `PIN_IN4` |
| D8 | Fase A del encoder (`ENC_A`) | `PIN_ENCODER_A` |
| D9 | Fase B del encoder (`ENC_B`) | `PIN_ENCODER_B` |
| 5V | VCC del ACS712 y del encoder | — |
| GND (los dos) | Tierra común | — |
| D13 | LED de la placa (sin conexión externa) | `PIN_LED_CAPTURA` |

### Lista de conexiones

| Nodo | Conecta |
|------|---------|
| ENB / IN3 / IN4 | D3 / D4 / D5 del Nano con ENB / IN3 / IN4 del módulo |
| OUT3 | OUT3 del módulo, IP+ de U2 |
| Motor + | IP− de U2, terminal + de M1 |
| OUT4 | OUT4 del módulo, terminal − de M1 |
| 12 V | Borne 12V del módulo, V1 (+) |
| `I_SEN` | OUT de U2, A0 del Nano |
| `ENC_A` / `ENC_B` | Fase A → D8, fase B → D9 |
| +5V | 5V del Nano, VCC de U2, VCC del encoder |
| GND | GND del Nano, GND del módulo, V1 (−), GND de U2, GND del encoder |

### Lista de componentes

| Ref. | Componente | Valor / modelo |
|------|------------|----------------|
| U1 | Arduino Nano | ATmega328P, 16 MHz |
| U2 | Sensor de corriente | ACS712, 5 A (185 mV/A), en módulo |
| U3 | Driver de puente H | Módulo L298N (canal B) |
| M1 | Motor DC con caja reductora | JGA25-370 |
| ENC | Encoder Hall de cuadratura | Integrado en el JGA25-370 |
| V1 | Fuente de alimentación | 12 V |

### Interpretaciones de la IA

El equipo debe confirmarlas:

1. **El ACS712 va del lado de OUT3.** El prompt no dice dónde va. Como mide en los dos sentidos, también sirve del lado de OUT4. Si la corriente sale con el signo al revés, se intercambian IP+ e IP− o se usa «INVERTIR SIGNO DE LA CORRIENTE» en la aplicación.
2. **El 5 V lógico viene del Nano, no del regulador del módulo.** Así se evita unir dos fuentes de 5 V mientras el Nano está conectado por USB.
3. **El encoder se alimenta con 5 V.** Revisen en la hoja del motor su rango de alimentación (suele aceptar 3,3–5 V).

### Sobre los símbolos

Se mantuvo el estilo de la versión 1: la IA redibujó los símbolos imitando ElCompLib (trazo de 3,5 px, fuente DejaVu Sans Mono). El módulo L298N y el ACS712 se dibujaron como bloques con sus bornes. Cada componente está en un grupo con su nombre (U1, U2, U3, M1, ENC, V1).

### Verificación realizada

- **SVG:** se revisó visualmente en el navegador. Se acortaron dos líneas del cuadro de título que se salían del recuadro.
- **Coherencia con el programa:** los pines del esquemático coinciden con las constantes del `.ino`.

**No verificado:** el circuito no se ha armado ni probado.

---

## Versión 1: driver MOSFET (reemplazada)

El esquemático original tenía:

- un driver de lado bajo con un MOSFET IRFZ44N (180 Ω de compuerta, 10 kΩ de pull-down);
- un diodo de rueda libre 1N540X;
- el ACS712T en A0 y el encoder en A1 y A2;
- la señal del driver en D9.

Se reemplazó cuando el autor cambió al L298N, y sigue disponible en el historial de git (commit `7ed3b88` y anteriores). Sus prompts se conservan aquí como registro.

```text
Quisiera que coloques también un esquemático del circuito propuesto. El Arduino tiene conectado a un pin ADC el sensor de corriente y a otro pin una salida a un driver compuesto de un MOSFET IRFZ44N con un resistor de compuerta de 180 ohms y un resistor pull-down de 10k con un diodo de la serie 1N540X. El driver conecta las entradas de potencia del motor DC a un bus de 12 V y a Tierra. Las salidas del encoder del motor van a pines lógicos del arduino. Quisiera, de ser posible, que utilices los pines en un mismo lado del arduino nano.

Para el esquemático, utiliza la librería de símbolos para Inkscape, que dejo adjunta como imagen.

Coloca el MD correspondiente y la documentación respectiva en la parte de uso de IA. No olvides hacer lo mismo para la programación del .ino.
```

*(Se adjuntó una imagen de la librería de símbolos ElCompLib para Inkscape, de Filip Dominec y colaboradores, de dominio público.)*

**Prompt de corrección (22/11/2026):**

```text
Tengo una pequeña corrección sobre el esquemático. Me gustaría utilizar un pin del Arduino nano que tenga funcionalidad PWM para la entrada del driver del motor. 

También quisiera que recomienda un circuito de acondicionamiento de señal (quizás otra etapa de un switch con un transistor de gama más baja) para conertir la señal lógica de 0-5V del Arduino Nano en una señal de 0-12 V necesarios para saturar el MOSFET. Considera utilizar un BJT NPN como el 2N3904. Argumentame si este diseño es adecuado o no.

Si el diseño es adecuado, procede con las correcciones sobre el esquemático
```

*(En la versión 1 se decidió mantener 5 V directo a la compuerta, a partir de simulaciones de LTspice que ya se retiraron del repositorio; ver [`Simulaciones_Driver.md`](Simulaciones_Driver.md).)*
