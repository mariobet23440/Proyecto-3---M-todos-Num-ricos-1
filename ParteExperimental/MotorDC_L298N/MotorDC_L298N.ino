/*
 * =============================================================================
 *  MOTOR DC JGA25-370 CON L298N: CAPTURA RÁPIDA Y CONTROL PID
 * =============================================================================
 *  Proyecto 3 - Métodos Numéricos 1 · Universidad del Valle de Guatemala
 *  Motor DC: gemelo digital y control PID (parte práctica)
 *
 *  Archivo          : MotorDC_L298N.ino
 *  Fecha de creación: 22/11/2026 (versión 2: driver L298N y PID)
 *  Autores          : Mario Alejandro Betancourt Franco (23440)
 *                     Claude Opus 5.5 (Anthropic), asistente de IA
 *  Placa            : Arduino Nano (ATmega328P a 16 MHz)
 *  Driver           : módulo L298N, canal B (ENB, IN3, IN4 -> OUT3, OUT4)
 *
 * -----------------------------------------------------------------------------
 *  DESCRIPCIÓN
 * -----------------------------------------------------------------------------
 *  El programa tiene dos formas de trabajar.
 *
 *  A) CAPTURA RÁPIDA (orden 'E'): respuesta al escalón y a la desconexión.
 *     El Arduino no procesa nada: envía los DATOS BRUTOS de cada muestra.
 *       - La lectura del ADC (0 a 1023) del sensor de corriente ACS712 de 5 A.
 *       - El nivel lógico de la fase A y de la fase B del encoder (0 o 1).
 *     El ADC trabaja en conversión continua y cada conversión dispara una
 *     interrupción, donde también se leen las fases del encoder. Corriente y
 *     encoder comparten así la misma base de tiempo:
 *       fs = 16 MHz / 32 / 13 ≈ 38 462 muestras/s, a 1 000 000 baudios.
 *     Cada muestra ocupa 2 bytes (14 bits útiles), es decir, 20 bits en la
 *     línea: 0,77 Mbit/s, el 77 % de la capacidad del UART a 1 Mbaud.
 *     El ATmega328P llega a 2 Mbaud (y a ≈ 76 923 muestras/s con prescaler 16),
 *     pero con el adaptador USB-serie del Nano del equipo se perdían entre 100
 *     y 700 tramas por captura en la computadora (el Arduino no perdía
 *     ninguna), lo que producía saltos inválidos en el encoder. A 1 Mbaud se
 *     midieron dos capturas completas sin pérdidas (22/11/2026).
 *     Secuencia: fase previa (motor libre, sirve para medir el cero del
 *     sensor), escalón (PWM fijo) y desconexión (motor libre o frenado).
 *     La posición, la velocidad y la corriente se calculan en la computadora
 *     (ParteExperimental/postprocesamiento.py).
 *
 *  B) TIEMPO REAL (órdenes 'M', 'K', 'R', ...): lazo abierto o PID.
 *     El encoder se cuenta ×4 con la interrupción por cambio de pin, el Timer1
 *     marca el periodo de muestreo Ts del controlador, y en cada periodo:
 *       1) se lee la posición (cuentas) y se estima la velocidad;
 *       2) se promedia la corriente (todas las conversiones del ADC en Ts);
 *       3) se calcula la referencia (constante, seno, cuadrada o triangular);
 *       4) se calcula el voltaje con el PID (o se aplica la referencia
 *          directamente, en lazo abierto) y se aplica con el PWM de ENB;
 *       5) se envía una trama binaria de telemetría a la computadora.
 *
 *  PID (ver UsoIA/ParteExperimental/Controlador_PID.md):
 *       e_k = r_k - y_k                      (error)
 *       E_k = E_{k-1} + e_k                  (error acumulado: memoria)
 *       u_k = Kp·e_k + Ki·Ts·E_k + (Kd/Ts)·(e_k - e_{k-1})
 *     Ts·E_k aproxima la integral del error (suma de rectángulos) y
 *     (e_k - e_{k-1})/Ts su derivada (diferencia hacia atrás). El prompt tenía
 *     Ki/Ts y Kd·Ts; el autor pidió corregirlo a esta forma.
 *
 *  Protocolo serie (1 000 000 baudios): ver la sección 8 y
 *  ParteExperimental/protocolo_motor.py, que es su contraparte en Python.
 *
 * -----------------------------------------------------------------------------
 *  RESUMEN DE LOS PROMPTS QUE ORIGINARON ESTE CÓDIGO
 * -----------------------------------------------------------------------------
 *  Versión 1: código para un Arduino Nano con un driver MOSFET, un motor
 *  JGA25-370 con encoder y un ACS712T de 5 A, para capturar la respuesta al
 *  escalón y a la desconexión con el ADC a la frecuencia más alta posible y
 *  transmitir por UART.
 *  Versión 2 (este archivo): el autor cambió el driver por un L298N (ENB en D3,
 *  IN3 en D4, IN4 en D5), con el ACS712-5 en A0 y las fases A y B del encoder
 *  en D8 y D9. Se pidió enviar los datos brutos del encoder y del sensor a la
 *  frecuencia más alta posible, y después un controlador PID con memoria, con
 *  modos de velocidad y de posición, ajustable desde una aplicación de Python.
 *  Los prompts completos están en UsoIA/ParteExperimental/Programa_L298N.md y
 *  UsoIA/ParteExperimental/Controlador_PID.md.
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
#include <stdlib.h>         // strtod() para leer los números de las órdenes
#include <math.h>           // sinf(), fabsf()

// Obliga al compilador a copiar la función en el lugar donde se llama. Se usa
// en las funciones que corren dentro de la interrupción rápida del ADC: una
// llamada a función obligaría a guardar muchos registros en cada muestra.
#define EN_LINEA inline __attribute__((always_inline))

// =============================================================================
//  1. PINES (cambiar aquí si el cableado es distinto)
// =============================================================================

// Salida analógica (VIOUT) del sensor de corriente ACS712 de 5 A.
const uint8_t PIN_SENSOR_CORRIENTE = A0;

// ENB del L298N (habilita el canal B). Hay que QUITAR el puente (jumper) de ENB
// del módulo para que el Arduino lo controle. D3 es la salida OC2B del Timer2,
// que da PWM por hardware sin afectar a millis() (que usa el Timer0).
const uint8_t PIN_ENB = 3;

// Entradas de dirección del canal B del L298N.
const uint8_t PIN_IN3 = 4;
const uint8_t PIN_IN4 = 5;

// Fases del encoder: A en D8 (PB0) y B en D9 (PB1).
const uint8_t PIN_ENCODER_A = 8;
const uint8_t PIN_ENCODER_B = 9;

// LED de la placa (D13). Se enciende durante la captura rápida.
const uint8_t PIN_LED_CAPTURA = LED_BUILTIN;

// Bit de cada pin dentro de su puerto (D0-D7 -> PORTD, D8-D13 -> PORTB).
constexpr uint8_t bitDePin(uint8_t pin) {
  return pin <= 7 ? pin : (pin <= 13 ? pin - 8 : pin - 14);
}

// ENB tiene que ser D3: el código escribe en los registros del Timer2 (OC2B).
static_assert(PIN_ENB == 3, "ENB debe ir en D3 (salida OC2B del Timer2)");

// IN3 e IN4 se manejan escribiendo en PORTD: deben ir en D2 a D7.
static_assert(PIN_IN3 >= 2 && PIN_IN3 <= 7 && PIN_IN4 >= 2 && PIN_IN4 <= 7,
              "IN3 e IN4 deben ir entre D2 y D7 (puerto D)");

// Las fases del encoder se leen juntas en PINB y usan la interrupción PCINT0,
// que atiende solo a D8-D13. D13 tiene el LED: no usarlo para el encoder.
static_assert(PIN_ENCODER_A >= 8 && PIN_ENCODER_A <= 12 &&
              PIN_ENCODER_B >= 8 && PIN_ENCODER_B <= 12 &&
              PIN_ENCODER_A != PIN_ENCODER_B,
              "Las fases del encoder deben ir en pines distintos entre D8 y D12");

// El sensor debe ir en una entrada analógica del Nano (A0 a A7).
static_assert(PIN_SENSOR_CORRIENTE >= A0 && PIN_SENSOR_CORRIENTE <= A7,
              "El sensor de corriente debe ir en una entrada analogica (A0 a A7)");

static_assert(PIN_ENB != PIN_IN3 && PIN_ENB != PIN_IN4 && PIN_IN3 != PIN_IN4,
              "Hay dos senales del driver asignadas al mismo pin");

// =============================================================================
//  2. CONFIGURACIÓN (valores iniciales; casi todos se cambian por el puerto serie)
// =============================================================================

// --- Captura rápida (orden 'C' para cambiarlos) ---
const uint16_t TIEMPO_PREVIO_MS    = 200;    // Motor libre (cero del sensor)
const uint16_t TIEMPO_ENCENDIDO_MS = 1500;   // Respuesta al escalón
const uint16_t TIEMPO_APAGADO_MS   = 1500;   // Respuesta a la desconexión
const uint8_t  CICLO_TRABAJO_PWM   = 255;    // PWM del escalón (255 = voltaje completo)
const bool     SENTIDO_ADELANTE    = true;   // true: IN3 = 1, IN4 = 0
const bool     APAGADO_CON_FRENO   = false;  // false: motor libre; true: freno dinámico

// --- Controlador (órdenes 'K', 'T', 'F', 'P', 'A') ---
const float    KP_INICIAL     = 0.05f;   // V por unidad de error
const float    KI_INICIAL     = 0.0f;    // V por (unidad de error · s)
const float    KD_INICIAL     = 0.0f;    // V·s por unidad de error
const float    TS_INICIAL_MS  = 2.0f;    // Periodo de muestreo del controlador
const float    TAU_INICIAL_MS = 8.0f;    // Constante de tiempo del filtro de velocidad
// Cuentas del encoder por vuelta del eje que se quiere controlar:
// 4 × (pulsos por vuelta del eje del motor) × (reducción de la caja).
// El valor inicial (4 × 11 × 1) corresponde al eje del MOTOR con un encoder de
// 11 pulsos por vuelta. Hay que confirmarlo con la hoja de datos del motor y
// enviarlo desde la aplicación con la orden 'P'.
const float    CUENTAS_POR_VUELTA_INICIAL = 44.0f;
const float    VOLTAJE_BUS_INICIAL = 12.0f;   // Voltaje de la fuente del L298N
const bool     ANTIWINDUP_INICIAL  = true;    // Congela E_k cuando u se satura
// Si al alimentar el motor ADELANTE la cuenta del encoder baja, el PID se
// realimenta al revés. Con true (u orden 'I 1') se invierte el signo de la
// cuenta en tiempo real. En el montaje del equipo hace falta (22/11/2026).
const bool     INVERTIR_ENCODER_INICIAL = false;

// Si no llega ninguna orden en este tiempo y el motor está en un modo activo,
// el motor pasa a reposo (por si la aplicación se cierra o se desconecta).
// La aplicación envía 'H' cada 0,5 s para mantenerlo activo.
const uint16_t TIEMPO_SIN_COMUNICACION_MS = 2000;

// Velocidad del UART. A 16 MHz, 1 000 000 y 2 000 000 baudios son exactos.
// Con 2 000 000 (y PRESCALER_ADC_RAPIDO = 16) el adaptador USB-serie del Nano
// del equipo perdía bytes en la computadora; con 1 000 000 no se perdió ninguno.
const uint32_t BAUDIOS = 1000000UL;

// Prescaler del ADC en la captura rápida (fs = 16 MHz / prescaler / 13).
const uint8_t PRESCALER_ADC_RAPIDO = 32;     // ≈ 38 462 muestras/s
// Prescaler del ADC en tiempo real: reloj de 125 kHz (resolución completa),
// ≈ 9 615 conversiones/s que se promedian en cada periodo Ts.
const uint8_t PRESCALER_ADC_NORMAL = 128;

// Prescaler del Timer2, que fija la frecuencia del PWM de ENB.
// En modo PWM de fase correcta: f_PWM = 16 MHz / (510 · prescaler).
//   1 -> 31 373 Hz · 8 -> 3 922 Hz · 32 -> 980 Hz · 64 -> 490 Hz (el de Arduino)
const uint16_t PRESCALER_PWM = 64;

// =============================================================================
//  3. CONSTANTES DERIVADAS (no hace falta modificarlas)
// =============================================================================

const uint8_t BYTES_POR_TRAMA_RAPIDA = 2;    // Ver el formato en la sección 6
const uint8_t CICLOS_POR_CONVERSION  = 13;   // Ciclos del ADC por conversión continua

constexpr float FS_RAPIDA_HZ =
    (float)F_CPU / (float)PRESCALER_ADC_RAPIDO / (float)CICLOS_POR_CONVERSION;
constexpr float FRECUENCIA_PWM_HZ = (float)F_CPU / (510.0f * (float)PRESCALER_PWM);

// Convierte un prescaler del ADC a los bits ADPS2:0 del registro ADCSRA.
constexpr uint8_t bitsPrescalerADC(uint8_t p) {
  return p == 2 ? 1 : p == 4 ? 2 : p == 8 ? 3 : p == 16 ? 4 :
         p == 32 ? 5 : p == 64 ? 6 : p == 128 ? 7 : 0xFF;
}
static_assert(bitsPrescalerADC(PRESCALER_ADC_RAPIDO) != 0xFF &&
              bitsPrescalerADC(PRESCALER_ADC_NORMAL) != 0xFF,
              "Los prescalers del ADC deben ser 2, 4, 8, 16, 32, 64 o 128");

// Convierte el prescaler del Timer2 a los bits CS22:0 del registro TCCR2B.
constexpr uint8_t bitsPrescalerTimer2(uint16_t p) {
  return p == 1 ? 1 : p == 8 ? 2 : p == 32 ? 3 : p == 64 ? 4 :
         p == 128 ? 5 : p == 256 ? 6 : p == 1024 ? 7 : 0xFF;
}
static_assert(bitsPrescalerTimer2(PRESCALER_PWM) != 0xFF,
              "PRESCALER_PWM debe ser 1, 8, 32, 64, 128, 256 o 1024");

// El UART debe poder enviar todas las muestras de la captura rápida.
// Cada byte ocupa 10 bits en la línea; se exige usar como máximo el 90 %.
static_assert((F_CPU / PRESCALER_ADC_RAPIDO / CICLOS_POR_CONVERSION) * BYTES_POR_TRAMA_RAPIDA * 10UL
                  <= BAUDIOS * 9UL / 10UL,
              "El UART no alcanza a transmitir todas las muestras: suba BAUDIOS o suba PRESCALER_ADC_RAPIDO");

const uint8_t CANAL_ADC = PIN_SENSOR_CORRIENTE - A0;

// Máscaras de bits de los pines del driver dentro de PORTD.
const uint8_t MASCARA_ENB = 1 << bitDePin(PIN_ENB);
const uint8_t MASCARA_IN3 = 1 << bitDePin(PIN_IN3);
const uint8_t MASCARA_IN4 = 1 << bitDePin(PIN_IN4);

// Máscaras de las fases del encoder dentro de PINB.
const uint8_t MASCARA_FASE_A = 1 << bitDePin(PIN_ENCODER_A);
const uint8_t MASCARA_FASE_B = 1 << bitDePin(PIN_ENCODER_B);

// Bits del primer byte de cada trama rápida (sección 6).
const uint8_t BANDERA_PERDIDA = 0x40;   // Se perdieron tramas justo antes de esta
const uint8_t BANDERA_MOTOR   = 0x20;   // El motor estaba alimentado
const uint8_t BIT_FASE_B      = 0x10;   // Nivel de la fase B del encoder
const uint8_t BIT_FASE_A      = 0x08;   // Nivel de la fase A del encoder

// Buffer circular de la captura rápida. Debe ser 256: los índices son de
// 8 bits y dan la vuelta solos (255 + 1 = 0).
const uint16_t TAMANO_BUFFER = 256;

// Fin de la captura rápida: cuatro bytes 0xFF y la línea de texto "FIN ...".
// En los datos válidos nunca hay dos bytes seguidos con el bit 7 en 1.
const uint8_t BYTE_FIN = 0xFF;
const uint8_t REPETICIONES_FIN = 4;

// =============================================================================
//  4. TABLA DEL DECODIFICADOR DE CUADRATURA (la misma que usa Python)
// =============================================================================
// Estado del encoder: s = (A << 1) | B, de 0 a 3. Índice: (s_anterior << 2) | s.
// Cada entrada vale +1 (avance), -1 (retroceso) o 0 (sin cambio, o un salto
// inválido de dos estados, que se cuenta como error).
// Si el conteo sale con el signo al revés, intercambiar los cables A y B.
const int8_t TABLA_CUADRATURA[16] = {
   0, -1, +1,  0,
  +1,  0,  0, -1,
  -1,  0,  0, +1,
   0, +1, -1,  0
};

// =============================================================================
//  5. VARIABLES GLOBALES
// =============================================================================

// --- Captura rápida (compartidas con la interrupción del ADC) ---
volatile uint8_t  bufferTx[TAMANO_BUFFER];  // Bytes por enviar
volatile uint8_t  cabeza = 0;               // Donde escribe la interrupción
volatile uint8_t  cola = 0;                 // Donde lee el lazo que transmite
volatile uint8_t  banderas = 0;             // BANDERA_MOTOR y BANDERA_PERDIDA actuales
volatile uint8_t  fase = 0;                 // 0 previa, 1 escalón, 2 desconexión, 3 fin
volatile uint8_t  cuentaBaja = 0;           // Contador de 8 bits de la fase (ver 6)
volatile uint16_t bloquesRestantes = 0;     // Bloques de 256 muestras que faltan
volatile bool     capturaActiva = false;    // true mientras el ADC está midiendo
volatile uint32_t tramasPerdidas = 0;       // Total de tramas perdidas (buffer lleno)

// Configuración de la captura rápida (se cambia con la orden 'C').
struct ConfigCaptura {
  uint8_t  pwm;          // Ciclo de trabajo del escalón (0 a 255)
  bool     adelante;     // Sentido de giro
  bool     freno;        // Modo de desconexión
  uint16_t tiempoMs[3];  // Duración de las fases previa, escalón y desconexión
};
ConfigCaptura captura = {CICLO_TRABAJO_PWM, SENTIDO_ADELANTE, APAGADO_CON_FRENO,
                         {TIEMPO_PREVIO_MS, TIEMPO_ENCENDIDO_MS, TIEMPO_APAGADO_MS}};
uint32_t muestrasFase[3];     // Muestras de cada fase (calculadas al iniciar)
uint8_t  bajaFase[3];         // Valor inicial de cuentaBaja de cada fase
uint16_t bloquesFase[3];      // Valor inicial de bloquesRestantes de cada fase

// --- Encoder en tiempo real (compartidas con la interrupción PCINT0) ---
volatile int32_t cuentaEncoder = 0;         // Posición en cuentas (×4)
volatile uint8_t estadoEncoder = 0;         // Último estado (A, B)
volatile uint8_t erroresEncoder = 0;        // Saltos inválidos (se pierden cuentas)

// --- Controlador ---
enum Modo : uint8_t { MODO_REPOSO = 0, MODO_LAZO_ABIERTO = 1, MODO_VELOCIDAD = 2, MODO_POSICION = 3 };
enum TipoReferencia : uint8_t { REF_CONSTANTE = 0, REF_SENO = 1, REF_CUADRADA = 2, REF_TRIANGULAR = 3 };

struct Controlador {
  uint8_t modo;
  float kp, ki, kd;        // Ganancias
  float tsMs;              // Periodo de muestreo en ms
  float tauMs;             // Filtro de velocidad
  float cuentasPorVuelta;  // Cuentas del encoder por vuelta del eje controlado
  float voltajeBus;        // Voltaje máximo que puede aplicar el L298N
  bool  antiwindup;
  bool  invertirEncoder;  // Cambia el signo de la cuenta del encoder
  // Referencia
  uint8_t tipoRef;
  float amplitud, desfase, frecuencia;   // r(t) = desfase + amplitud · forma(2π f t)
  // Memoria del PID
  float errorAcumulado;    // E_k
  float errorAnterior;     // e_{k-1}
  // Estado de la medición
  int32_t cuentaAnterior;
  float   velocidad;       // Velocidad filtrada en rad/s
  float   ultimoADC;       // Último promedio del ADC
  uint32_t k;              // Número de periodo desde que se cambió el modo
  uint32_t kRef;           // Número de periodo desde que se cambió la referencia
  uint8_t  decimacion;     // Enviar telemetría cada 'decimacion' periodos (0 = no)
};
Controlador ctl;

volatile bool    tickControl = false;   // El Timer1 avisa que pasó un periodo Ts
volatile uint8_t ticksAtrasados = 0;    // Periodos que llegaron antes de atender el anterior

uint32_t sumaADC = 0;                   // Suma de conversiones del ADC en el periodo
uint16_t numADC = 0;                    // Cuántas conversiones se sumaron
uint32_t ultimaOrdenMs = 0;             // millis() de la última orden recibida

// =============================================================================
//  6. CAPTURA RÁPIDA
// =============================================================================

// --- Driver (escritura directa en registros, para usarlas en la interrupción) ---
EN_LINEA void conectarPWM()    { TCCR2A |= (1 << COM2B1); }
EN_LINEA void desconectarPWM() { TCCR2A &= ~((1 << COM2B1) | (1 << COM2B0)); }

// IN3/IN4 según el sentido de giro.
EN_LINEA void fijarSentido(bool adelante) {
  if (adelante) PORTD = (PORTD | MASCARA_IN3) & ~MASCARA_IN4;   // IN3 = 1, IN4 = 0
  else          PORTD = (PORTD | MASCARA_IN4) & ~MASCARA_IN3;   // IN3 = 0, IN4 = 1
}

// Motor libre: ENB = 0.
EN_LINEA void soltarMotor() {
  desconectarPWM();                 // ENB deja de seguir al PWM...
  PORTD &= ~MASCARA_ENB;            // ...y queda en 0
}

// Freno dinámico: ENB = 1 e IN3 = IN4 = 0 (bornes del motor en corto).
EN_LINEA void frenarMotor() {
  PORTD &= ~(MASCARA_IN3 | MASCARA_IN4);
  desconectarPWM();
  PORTD |= MASCARA_ENB;
}

// Reposo: ENB = 0, IN3 = IN4 = 0.
EN_LINEA void reposoDriver() {
  soltarMotor();
  PORTD &= ~(MASCARA_IN3 | MASCARA_IN4);
}

// Configura el ADC en conversión continua con el prescaler y la interrupción dados.
void iniciarADC(uint8_t prescaler, bool conInterrupcion) {
  ADMUX = (1 << REFS0) | (CANAL_ADC & 0x07);   // Referencia AVcc, canal del sensor
  ADCSRB = 0;                                  // Disparo automático: modo continuo
  if (CANAL_ADC < 6) DIDR0 |= (1 << CANAL_ADC); // Sin buffer digital en el pin (menos ruido)
  ADCSRA = (1 << ADEN) | (1 << ADIF) | (1 << ADATE)
         | (conInterrupcion ? (1 << ADIE) : 0)
         | bitsPrescalerADC(prescaler);
  ADCSRA |= (1 << ADSC);                       // Arranca la primera conversión
}

// Formato de la trama rápida de 2 bytes (14 bits útiles):
//   byte 0: 1  P  M  B  A  C9 C8 C7   (bit 7 = 1 marca el inicio de la trama)
//   byte 1: 0  C6 C5 C4 C3 C2 C1 C0
//   C9..C0 = lectura del ADC del sensor de corriente (0 a 1023)
//   A, B   = nivel de las fases A y B del encoder (datos brutos)
//   M      = 1 si el motor estaba alimentado al tomar la muestra
//   P      = 1 si se perdieron tramas justo antes de esta (buffer lleno)
//
// Tiempo de cada muestra: t = n / fs, con n el número de trama (desde 0).
// El encoder se lee al entrar a la rutina, unos 11,5 µs (11,5 ciclos del ADC)
// más la latencia de la interrupción después del instante en que el ADC retuvo
// la corriente de la misma trama: menos de un periodo de muestreo (13 µs).
//
// Cuenta de muestras de cada fase: un contador de 8 bits que baja en cada
// muestra y un contador de bloques de 256 que solo se revisa cuando el primero
// llega a 0. Para N muestras: cuentaBaja = N mod 256 (0 equivale a 256) y
// bloques = (N - 1) / 256. Así el caso común cuesta solo unos pocos ciclos.
//
// La rutina tiene que ser corta: entre dos muestras hay 208 ciclos de reloj, y
// el lazo de transmisión necesita parte de ese tiempo para enviar los 2 bytes.
ISR(ADC_vect) {
  const uint8_t pines = PINB;                 // Fases A y B, lo antes posible
  const uint8_t bajo  = ADCL;                 // Hay que leer ADCL antes que ADCH
  const uint8_t alto  = ADCH;                 // Bits 9 y 8 del resultado
  const uint8_t f     = banderas;             // Copia local de las banderas

  uint8_t b0 = 0x80 | f | (uint8_t)(alto << 1) | (uint8_t)(bajo >> 7);
  if (pines & MASCARA_FASE_A) b0 |= BIT_FASE_A;
  if (pines & MASCARA_FASE_B) b0 |= BIT_FASE_B;

  uint8_t h = cabeza;
  if ((uint8_t)(h - cola) < (uint8_t)(TAMANO_BUFFER - BYTES_POR_TRAMA_RAPIDA)) {  // ¿Caben 2 bytes?
    bufferTx[h++] = b0;                       // byte 0
    bufferTx[h++] = bajo & 0x7F;              // byte 1: bits 6..0 del ADC
    cabeza = h;                               // Publica la trama completa
    banderas = f & ~BANDERA_PERDIDA;          // La marca de pérdida ya se envió
  } else {
    banderas = f | BANDERA_PERDIDA;           // Buffer lleno: la trama se pierde
    tramasPerdidas++;
  }

  if (--cuentaBaja == 0) {                    // Una vez cada 256 muestras (o al final de la fase)
    const uint16_t bloques = bloquesRestantes;
    if (bloques != 0) {
      bloquesRestantes = bloques - 1;
    } else {                                  // Se completaron las muestras de la fase
      const uint8_t nueva = fase + 1;
      fase = nueva;
      if (nueva == 1) {                       // Escalón de voltaje
        conectarPWM();
        banderas |= BANDERA_MOTOR;
      } else if (nueva == 2) {                // Desconexión
        if (captura.freno) frenarMotor(); else soltarMotor();
        banderas &= ~BANDERA_MOTOR;
      } else {                                // Fin del ensayo
        ADCSRA &= ~((1 << ADATE) | (1 << ADIE));
        capturaActiva = false;
        return;
      }
      cuentaBaja = bajaFase[nueva];
      bloquesRestantes = bloquesFase[nueva];
    }
  }
}

// Envía por texto la configuración de la captura rápida (pares clave=valor).
void imprimirConfigCaptura() {
  Serial.print(F("fs_hz="));          Serial.print(FS_RAPIDA_HZ, 3);
  Serial.print(F(" n_previas="));     Serial.print(muestrasFase[0]);
  Serial.print(F(" n_encendido="));   Serial.print(muestrasFase[1]);
  Serial.print(F(" n_apagado="));     Serial.print(muestrasFase[2]);
  Serial.print(F(" n_total="));       Serial.print(muestrasFase[0] + muestrasFase[1] + muestrasFase[2]);
  Serial.print(F(" prescaler_adc=")); Serial.print(PRESCALER_ADC_RAPIDO);
  Serial.print(F(" baudios="));       Serial.print(BAUDIOS);
  Serial.print(F(" pwm="));           Serial.print(captura.pwm);
  Serial.print(F(" f_pwm_hz="));      Serial.print(FRECUENCIA_PWM_HZ, 1);
  Serial.print(F(" sentido="));       Serial.print(captura.adelante ? 1 : -1);
  Serial.print(F(" freno="));         Serial.print(captura.freno ? 1 : 0);
  Serial.println();
}

// Calcula las muestras de cada fase a partir de los tiempos configurados.
void calcularFasesCaptura() {
  for (uint8_t i = 0; i < 3; i++) {
    uint32_t n = (uint32_t)((float)captura.tiempoMs[i] * FS_RAPIDA_HZ / 1000.0f);
    if (n == 0) n = 1;                        // Cada fase dura al menos una muestra
    muestrasFase[i] = n;
    bajaFase[i]     = (uint8_t)(n & 0xFF);
    bloquesFase[i]  = (uint16_t)((n - 1) >> 8);
  }
}

void configurarTiempoReal();   // Definida en la sección 7

void ejecutarCaptura() {
  // Motor en reposo y modo de tiempo real apagado.
  ctl.modo = MODO_REPOSO;
  reposoDriver();
  calcularFasesCaptura();

  Serial.print(F("INICIO "));
  imprimirConfigCaptura();
  Serial.flush();                         // Espera a que salga todo el texto

  noInterrupts();
  TIMSK1 = 0;                             // Sin interrupción del controlador
  PCICR &= ~(1 << PCIE0);                 // Sin interrupción del encoder (se lee en el ADC)
  fijarSentido(captura.adelante);         // IN3/IN4 listos; con ENB = 0 no mueven el motor
  OCR2B = captura.pwm;                    // Ciclo de trabajo del escalón
  cabeza = 0;
  cola = 0;
  banderas = 0;
  fase = 0;
  cuentaBaja = bajaFase[0];
  bloquesRestantes = bloquesFase[0];
  tramasPerdidas = 0;
  capturaActiva = true;
  interrupts();

  digitalWrite(PIN_LED_CAPTURA, HIGH);

  // Pausa la interrupción del Timer0 (la de millis()) para que no retrase a la
  // del ADC. millis() no avanza durante la captura; se restaura al final.
  const uint8_t timsk0Guardado = TIMSK0;
  TIMSK0 &= ~(1 << TOIE0);

  iniciarADC(PRESCALER_ADC_RAPIDO, true); // Empieza a muestrear

  // Transmisión directa por UDR0 (más rápida que Serial.write()). Solo este
  // lazo modifica 'cola': se trabaja con una copia local y se publica después
  // de cada byte (la interrupción la lee para saber cuánto espacio hay).
  uint8_t c = 0;
  while (capturaActiva || cabeza != c) {
    if ((UCSR0A & (1 << UDRE0)) && (cabeza != c)) {
      UDR0 = bufferTx[c];
      c++;
      cola = c;
    }
  }

  reposoDriver();
  TIMSK0 = timsk0Guardado;
  digitalWrite(PIN_LED_CAPTURA, LOW);

  for (uint8_t i = 0; i < REPETICIONES_FIN; i++) Serial.write(BYTE_FIN);
  Serial.print(F("\nFIN tramas_enviadas="));
  Serial.print(muestrasFase[0] + muestrasFase[1] + muestrasFase[2] - tramasPerdidas);
  Serial.print(F(" tramas_perdidas="));
  Serial.println(tramasPerdidas);

  configurarTiempoReal();                 // Vuelve al modo de tiempo real (en reposo)
  Serial.println(F("# AVISO la cuenta del encoder se reinicio a 0 despues de la captura"));
}

// =============================================================================
//  7. TIEMPO REAL: ENCODER, MUESTREO DEL CONTROLADOR Y PID
// =============================================================================

// Lee el estado (A << 1) | B del encoder.
EN_LINEA uint8_t leerEstadoEncoder() {
  const uint8_t p = PINB;
  return ((p & MASCARA_FASE_A) ? 2 : 0) | ((p & MASCARA_FASE_B) ? 1 : 0);
}

// Interrupción por cambio de pin del puerto B (solo se habilitan A y B).
ISR(PCINT0_vect) {
  const uint8_t s = leerEstadoEncoder();
  const uint8_t previo = estadoEncoder;
  cuentaEncoder += TABLA_CUADRATURA[(previo << 2) | s];
  if ((uint8_t)(previo ^ s) == 3 && erroresEncoder < 255) erroresEncoder++;  // Salto inválido
  estadoEncoder = s;
}

// Interrupción del Timer1: marca el inicio de un periodo de control.
ISR(TIMER1_COMPA_vect) {
  if (tickControl && ticksAtrasados < 255) ticksAtrasados++;  // El anterior no se atendió
  tickControl = true;
}

// Programa el Timer1 en modo CTC con el periodo Ts (resolución de 4 µs).
void programarTimer1(float tsMs) {
  uint32_t cuentas = (uint32_t)(tsMs * 250.0f + 0.5f);   // 16 MHz / 64 = 250 cuentas por ms
  if (cuentas < 2) cuentas = 2;
  if (cuentas > 65536UL) cuentas = 65536UL;
  noInterrupts();
  TCCR1A = 0;
  TCCR1B = (1 << WGM12) | (1 << CS11) | (1 << CS10);    // CTC, prescaler 64
  OCR1A  = (uint16_t)(cuentas - 1);
  TCNT1  = 0;
  TIFR1  = (1 << OCF1A);
  TIMSK1 = (1 << OCIE1A);
  interrupts();
}

// Deja el Nano listo para el modo de tiempo real (en reposo).
void configurarTiempoReal() {
  reposoDriver();
  iniciarADC(PRESCALER_ADC_NORMAL, false);   // Continuo, sin interrupción (se lee por sondeo)
  noInterrupts();
  cuentaEncoder = 0;
  erroresEncoder = 0;
  estadoEncoder = leerEstadoEncoder();
  PCMSK0 |= MASCARA_FASE_A | MASCARA_FASE_B; // D8-D12 son PCINT0-PCINT4: mismo bit que en PORTB
  PCIFR  = (1 << PCIF0);
  PCICR |= (1 << PCIE0);
  interrupts();
  ctl.cuentaAnterior = 0;
  ctl.velocidad = 0;
  ctl.errorAcumulado = 0;
  ctl.errorAnterior = 0;
  sumaADC = 0;
  numADC = 0;
  programarTimer1(ctl.tsMs);
}

// Suma las conversiones del ADC que ya terminaron (se llama en cada vuelta de loop()).
void acumularADC() {
  if (ADCSRA & (1 << ADIF)) {
    const uint16_t lectura = ADC;
    ADCSRA |= (1 << ADIF);                   // Escribir 1 borra la bandera
    sumaADC += lectura;
    numADC++;
  }
}

// Referencia r(t) = desfase + amplitud · forma(2π f t).
float calcularReferencia(float t) {
  if (ctl.tipoRef == REF_CONSTANTE) return ctl.desfase;
  float ciclo = ctl.frecuencia * t;
  ciclo -= floorf(ciclo);                    // Fracción del ciclo, entre 0 y 1
  float forma;
  if (ctl.tipoRef == REF_SENO)          forma = sinf(6.2831853f * ciclo);
  else if (ctl.tipoRef == REF_CUADRADA) forma = ciclo < 0.5f ? 1.0f : -1.0f;
  else                                  forma = 1.0f - 4.0f * fabsf(ciclo - 0.5f);  // Triangular
  return ctl.desfase + ctl.amplitud * forma;
}

// Aplica un voltaje con signo al motor: sentido con IN3/IN4 y magnitud con el PWM.
void aplicarVoltaje(float u) {
  float ciclo = fabsf(u) / ctl.voltajeBus * 255.0f;
  if (ciclo > 255.0f) ciclo = 255.0f;
  const uint8_t pwm = (uint8_t)(ciclo + 0.5f);
  if (pwm == 0) {
    soltarMotor();
    return;
  }
  fijarSentido(u > 0);
  OCR2B = pwm;
  conectarPWM();
}

// Resetea la memoria del PID (E_k y e_{k-1}).
void reiniciarPID() {
  ctl.errorAcumulado = 0;
  ctl.errorAnterior = 0;
}

// Trama de telemetría (27 bytes, little endian, igual que en protocolo_motor.py).
struct __attribute__((packed)) Telemetria {
  uint8_t  sync0;       // 0xA5
  uint8_t  sync1;       // 0x5A
  uint32_t k;           // Número de periodo desde que se cambió el modo
  int32_t  cuenta;      // Posición en cuentas del encoder
  float    referencia;  // r_k (V en lazo abierto, rad/s o rad en los PID)
  float    velocidad;   // Velocidad filtrada (rad/s del eje configurado)
  float    voltaje;     // u_k aplicado, ya saturado (V)
  uint16_t adc16;       // Promedio del ADC en el periodo × 16
  uint8_t  modo;        // Modo del controlador
  uint8_t  estado;      // bit0 saturado · bit1 error de encoder · bit2 periodo atrasado · bit3 E_k congelado
  uint8_t  suma;        // Suma de los bytes de 'k' a 'estado', módulo 256
};
static_assert(sizeof(Telemetria) == 27, "La trama de telemetria debe ocupar 27 bytes");

// Un periodo del controlador (se ejecuta cuando el Timer1 avisa).
void pasoControl() {
  // 1) Posición y errores del encoder (lectura atómica de la variable de 32 bits).
  noInterrupts();
  const int32_t cuenta = ctl.invertirEncoder ? -cuentaEncoder : cuentaEncoder;
  const uint8_t errores = erroresEncoder;
  erroresEncoder = 0;
  const uint8_t atrasados = ticksAtrasados;
  ticksAtrasados = 0;
  interrupts();

  const float ts = ctl.tsMs * 0.001f;
  const float radPorCuenta = 6.2831853f / ctl.cuentasPorVuelta;
  const float posicion = cuenta * radPorCuenta;

  // 2) Velocidad: diferencia hacia atrás y filtro de primer orden.
  const float velocidadCruda = (float)(cuenta - ctl.cuentaAnterior) * radPorCuenta / ts;
  ctl.cuentaAnterior = cuenta;
  const float alfa = ts / (ts + ctl.tauMs * 0.001f);
  ctl.velocidad += alfa * (velocidadCruda - ctl.velocidad);

  // 3) Corriente: promedio de las conversiones del periodo.
  if (numADC > 0) {
    ctl.ultimoADC = (float)sumaADC / (float)numADC;
    sumaADC = 0;
    numADC = 0;
  }

  // 4) Referencia y ley de control.
  const float r = calcularReferencia(ctl.kRef * ts);
  float u = 0;
  uint8_t estado = 0;
  if (ctl.modo == MODO_LAZO_ABIERTO) {
    u = r;                                   // La referencia es el voltaje
  } else if (ctl.modo == MODO_VELOCIDAD || ctl.modo == MODO_POSICION) {
    const float y = (ctl.modo == MODO_VELOCIDAD) ? ctl.velocidad : posicion;
    const float e = r - y;                               // e_k
    const float acumuladoNuevo = ctl.errorAcumulado + e; // E_k = E_{k-1} + e_k
    // u_k = Kp·e_k + Ki·Ts·E_k + (Kd/Ts)·(e_k - e_{k-1})
    const float gi = ctl.ki * ts;                        // Ts·E_k ≈ integral del error
    const float pd = ctl.kp * e + (ctl.kd / ts) * (e - ctl.errorAnterior);  // (Δe/Ts) ≈ derivada
    u = pd + gi * acumuladoNuevo;
    // Anti-windup por integración condicional: si u se satura y el error lo
    // empujaría más allá del límite, E_k no cambia en este periodo.
    if (ctl.antiwindup && fabsf(u) > ctl.voltajeBus && (u > 0) == (e > 0)) {
      u = pd + gi * ctl.errorAcumulado;
      estado |= 0x08;
    } else {
      ctl.errorAcumulado = acumuladoNuevo;
    }
    ctl.errorAnterior = e;                   // e_{k-1} para el próximo periodo
  }
  if (u > ctl.voltajeBus)  { u = ctl.voltajeBus;  estado |= 0x01; }
  if (u < -ctl.voltajeBus) { u = -ctl.voltajeBus; estado |= 0x01; }

  if (ctl.modo == MODO_REPOSO) reposoDriver();
  else                         aplicarVoltaje(u);

  // 5) Telemetría.
  if (errores)   estado |= 0x02;
  if (atrasados) estado |= 0x04;
  if (ctl.decimacion != 0 && (ctl.k % ctl.decimacion) == 0) {
    Telemetria t;
    t.sync0 = 0xA5;
    t.sync1 = 0x5A;
    t.k = ctl.k;
    t.cuenta = cuenta;
    t.referencia = r;
    t.velocidad = ctl.velocidad;
    t.voltaje = u;
    const float adc16 = ctl.ultimoADC * 16.0f + 0.5f;
    t.adc16 = (uint16_t)(adc16 > 65535.0f ? 65535.0f : adc16);
    t.modo = ctl.modo;
    t.estado = estado;
    uint8_t suma = 0;
    const uint8_t *p = (const uint8_t *)&t;
    for (uint8_t i = 2; i < sizeof(Telemetria) - 1; i++) suma += p[i];
    t.suma = suma;
    if (Serial.availableForWrite() >= (int)sizeof(Telemetria)) {   // No bloquea el lazo
      Serial.write((const uint8_t *)&t, sizeof(Telemetria));
    }
  }
  ctl.k++;
  ctl.kRef++;
}

// =============================================================================
//  8. ÓRDENES POR EL PUERTO SERIE
// =============================================================================
// Cada orden es una línea de texto: una letra y números separados por espacios.
// Las respuestas del Arduino son líneas que empiezan con '#'.
//
// Suma de verificación (opcional): la línea puede terminar en "*HH", con HH la
// suma de los bytes anteriores al '*' módulo 256, en hexadecimal. Si no
// coincide, la orden se descarta y se responde "# ERR SUMA ...". A alta velocidad el
// Arduino tiene unos 10 µs para leer cada byte; si en ese momento atiende otra
// interrupción, el byte se pierde y la orden llega cambiada (se observó "P 44 12"
// recibida como "P 44 2"). La aplicación envía siempre la suma y reenvía la
// orden hasta recibir "# OK". Escrita a mano, sin '*', la orden se acepta igual.
//
//   ?                          Envía la configuración ("# CFG ...")
//   H                          Latido: mantiene activo el modo (ver TIEMPO_SIN_COMUNICACION_MS)
//   X                          Paro: modo reposo
//   M modo                     0 reposo · 1 lazo abierto · 2 PID velocidad · 3 PID posición
//   K kp ki kd                 Ganancias del PID
//   T ts_ms                    Periodo de muestreo del controlador (0,5 a 250 ms)
//   F tau_ms                   Constante de tiempo del filtro de velocidad (0 = sin filtro)
//   P cuentas_vuelta v_bus     Cuentas por vuelta del eje controlado y voltaje de la fuente
//   R tipo amplitud desfase f  Referencia: 0 constante, 1 seno, 2 cuadrada, 3 triangular
//   A 0|1                      Anti-windup
//   I 0|1                      Invierte el signo de la cuenta del encoder
//   S n                        Telemetría cada n periodos (0 = apagada)
//   Z                          Pone la cuenta del encoder en 0
//   C pwm sentido freno t0 t1 t2   Configura la captura rápida (tiempos en ms)
//   E                          Ejecuta la captura rápida

char lineaOrden[64];
uint8_t largoOrden = 0;

void imprimirConfiguracion() {
  Serial.print(F("# CFG modo="));   Serial.print(ctl.modo);
  Serial.print(F(" kp="));          Serial.print(ctl.kp, 6);
  Serial.print(F(" ki="));          Serial.print(ctl.ki, 6);
  Serial.print(F(" kd="));          Serial.print(ctl.kd, 6);
  Serial.print(F(" ts_ms="));       Serial.print(ctl.tsMs, 3);
  Serial.print(F(" tau_ms="));      Serial.print(ctl.tauMs, 3);
  Serial.print(F(" cpr="));         Serial.print(ctl.cuentasPorVuelta, 3);
  Serial.print(F(" vbus="));        Serial.print(ctl.voltajeBus, 3);
  Serial.print(F(" aw="));          Serial.print(ctl.antiwindup ? 1 : 0);
  Serial.print(F(" inv_enc="));     Serial.print(ctl.invertirEncoder ? 1 : 0);
  Serial.print(F(" ref_tipo="));    Serial.print(ctl.tipoRef);
  Serial.print(F(" ref_amp="));     Serial.print(ctl.amplitud, 4);
  Serial.print(F(" ref_off="));     Serial.print(ctl.desfase, 4);
  Serial.print(F(" ref_f="));       Serial.print(ctl.frecuencia, 4);
  Serial.print(F(" decimacion="));  Serial.print(ctl.decimacion);
  Serial.print(F(" cap_pwm="));     Serial.print(captura.pwm);
  Serial.print(F(" cap_sentido=")); Serial.print(captura.adelante ? 1 : -1);
  Serial.print(F(" cap_freno="));   Serial.print(captura.freno ? 1 : 0);
  Serial.print(F(" cap_t0="));      Serial.print(captura.tiempoMs[0]);
  Serial.print(F(" cap_t1="));      Serial.print(captura.tiempoMs[1]);
  Serial.print(F(" cap_t2="));      Serial.print(captura.tiempoMs[2]);
  Serial.print(F(" fs_rapida_hz="));Serial.print(FS_RAPIDA_HZ, 3);
  Serial.print(F(" f_pwm_hz="));    Serial.print(FRECUENCIA_PWM_HZ, 1);
  Serial.println();
}

// Lee hasta 'maximo' números de la línea. Devuelve cuántos encontró.
uint8_t leerNumeros(const char *texto, float *valores, uint8_t maximo) {
  uint8_t n = 0;
  char *fin;
  while (n < maximo) {
    const double v = strtod(texto, &fin);
    if (fin == texto) break;                 // No hay más números
    valores[n++] = (float)v;
    texto = fin;
  }
  return n;
}

// Revisa la suma de verificación "*HH" (si la hay) y la quita de la línea.
// Devuelve false si la suma no coincide.
bool verificarSuma(char *linea) {
  char *asterisco = strchr(linea, '*');
  if (asterisco == nullptr) return true;          // Orden escrita a mano: sin suma
  uint8_t suma = 0;
  for (char *p = linea; p < asterisco; p++) suma += (uint8_t)*p;
  char *fin;
  const long esperada = strtol(asterisco + 1, &fin, 16);
  *asterisco = 0;                                 // La línea queda sin la suma
  return fin != asterisco + 1 && esperada == suma;
}

void ejecutarOrden(char *linea) {
  if (!verificarSuma(linea)) {
    Serial.print(F("# ERR SUMA "));
    Serial.println(linea);
    return;
  }
  while (*linea == ' ') linea++;
  const char orden = (char)toupper(linea[0]);
  if (orden == 0) return;
  float v[6];
  const uint8_t n = leerNumeros(linea + 1, v, 6);
  bool ok = true;

  switch (orden) {
    case '?': imprimirConfiguracion(); return;
    case 'H': return;                        // Latido: solo actualiza ultimaOrdenMs
    case 'X': ctl.modo = MODO_REPOSO; reposoDriver(); reiniciarPID(); break;
    case 'M':
      if (n >= 1 && v[0] >= 0 && v[0] <= 3) {
        ctl.modo = (uint8_t)v[0];
        reiniciarPID();
        ctl.k = 0;
        ctl.kRef = 0;
        if (ctl.modo == MODO_REPOSO) reposoDriver();
      } else ok = false;
      break;
    case 'K':
      if (n >= 3) { ctl.kp = v[0]; ctl.ki = v[1]; ctl.kd = v[2]; } else ok = false;
      break;
    case 'T':
      if (n >= 1 && v[0] >= 0.5f && v[0] <= 250.0f) {
        ctl.tsMs = v[0];
        reiniciarPID();
        programarTimer1(ctl.tsMs);
      } else ok = false;
      break;
    case 'F':
      if (n >= 1 && v[0] >= 0) ctl.tauMs = v[0]; else ok = false;
      break;
    case 'P':
      if (n >= 2 && v[0] > 0 && v[1] > 0) { ctl.cuentasPorVuelta = v[0]; ctl.voltajeBus = v[1]; }
      else ok = false;
      break;
    case 'R':
      if (n >= 4 && v[0] >= 0 && v[0] <= 3) {
        ctl.tipoRef = (uint8_t)v[0]; ctl.amplitud = v[1]; ctl.desfase = v[2]; ctl.frecuencia = v[3];
        ctl.kRef = 0;
      } else ok = false;
      break;
    case 'A': if (n >= 1) ctl.antiwindup = v[0] != 0; else ok = false; break;
    case 'I':
      if (n >= 1) {
        ctl.invertirEncoder = v[0] != 0;
        noInterrupts(); cuentaEncoder = 0; interrupts();   // La posición vuelve a 0
        ctl.cuentaAnterior = 0;
        ctl.velocidad = 0;
        reiniciarPID();
      } else ok = false;
      break;
    case 'S': if (n >= 1 && v[0] >= 0 && v[0] <= 255) ctl.decimacion = (uint8_t)v[0]; else ok = false; break;
    case 'Z':
      noInterrupts(); cuentaEncoder = 0; interrupts();
      ctl.cuentaAnterior = 0;
      reiniciarPID();
      break;
    case 'C':
      if (n >= 6 && v[0] >= 0 && v[0] <= 255 && v[3] >= 1 && v[4] >= 1 && v[5] >= 1 &&
          v[3] <= 60000 && v[4] <= 60000 && v[5] <= 60000) {
        captura.pwm = (uint8_t)v[0];
        captura.adelante = v[1] >= 0;
        captura.freno = v[2] != 0;
        for (uint8_t i = 0; i < 3; i++) captura.tiempoMs[i] = (uint16_t)v[3 + i];
      } else ok = false;
      break;
    case 'E': ejecutarCaptura(); return;
    default: ok = false;
  }
  Serial.print(ok ? F("# OK ") : F("# ERR "));
  Serial.println(linea);
}

// Junta los caracteres que llegan hasta completar una línea.
void leerOrdenes() {
  while (Serial.available() > 0) {
    const char ch = (char)Serial.read();
    ultimaOrdenMs = millis();
    if (ch == '\n' || ch == '\r') {
      if (largoOrden > 0) {
        lineaOrden[largoOrden] = 0;
        largoOrden = 0;
        ejecutarOrden(lineaOrden);
      }
    } else if (largoOrden < sizeof(lineaOrden) - 1) {
      lineaOrden[largoOrden++] = ch;
    }
  }
}

// =============================================================================
//  9. SETUP Y LOOP
// =============================================================================
void setup() {
  // Lo primero: el driver en reposo. ENB = 0 deja el motor sin alimentación.
  digitalWrite(PIN_ENB, LOW);
  digitalWrite(PIN_IN3, LOW);
  digitalWrite(PIN_IN4, LOW);
  pinMode(PIN_ENB, OUTPUT);
  pinMode(PIN_IN3, OUTPUT);
  pinMode(PIN_IN4, OUTPUT);

  // Timer2 en PWM de fase correcta (TOP = 255), con OC2B desconectado hasta usarlo.
  TCCR2A = (1 << WGM20);
  TCCR2B = bitsPrescalerTimer2(PRESCALER_PWM);
  OCR2B  = 0;
  TIMSK2 = 0;

  pinMode(PIN_LED_CAPTURA, OUTPUT);
  digitalWrite(PIN_LED_CAPTURA, LOW);

  // Encoder: entradas con pull-up interno (no estorba si el encoder ya trae el suyo).
  pinMode(PIN_ENCODER_A, INPUT_PULLUP);
  pinMode(PIN_ENCODER_B, INPUT_PULLUP);
  pinMode(PIN_SENSOR_CORRIENTE, INPUT);

  // Controlador con los valores iniciales.
  ctl.modo = MODO_REPOSO;
  ctl.kp = KP_INICIAL; ctl.ki = KI_INICIAL; ctl.kd = KD_INICIAL;
  ctl.tsMs = TS_INICIAL_MS;
  ctl.tauMs = TAU_INICIAL_MS;
  ctl.cuentasPorVuelta = CUENTAS_POR_VUELTA_INICIAL;
  ctl.voltajeBus = VOLTAJE_BUS_INICIAL;
  ctl.antiwindup = ANTIWINDUP_INICIAL;
  ctl.invertirEncoder = INVERTIR_ENCODER_INICIAL;
  ctl.tipoRef = REF_CONSTANTE;
  ctl.amplitud = 0; ctl.desfase = 0; ctl.frecuencia = 0;
  ctl.decimacion = 1;
  ctl.k = 0; ctl.kRef = 0;
  ctl.ultimoADC = 0;
  calcularFasesCaptura();

  Serial.begin(BAUDIOS);
  configurarTiempoReal();

  Serial.println(F("# LISTO Motor JGA25-370 con L298N. Ordenes: ? H X M K T F P R A I S Z C E"));
  imprimirConfiguracion();
  ultimaOrdenMs = millis();
}

void loop() {
  leerOrdenes();
  acumularADC();
  if (tickControl) {
    tickControl = false;
    pasoControl();
  }
  // Seguridad: sin órdenes ni latidos durante un rato, el motor pasa a reposo.
  if (ctl.modo != MODO_REPOSO && (millis() - ultimaOrdenMs) > TIEMPO_SIN_COMUNICACION_MS) {
    ctl.modo = MODO_REPOSO;
    reposoDriver();
    reiniciarPID();
    Serial.println(F("# AVISO sin comunicacion: motor en reposo"));
  }
}
