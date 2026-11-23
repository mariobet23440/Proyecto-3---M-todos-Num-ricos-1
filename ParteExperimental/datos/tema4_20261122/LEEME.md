# Ensayos del tema 4 · Motor DC JGA25-370 con L298N · 22/11/2026

Datos **reales** medidos en el montaje del equipo (Arduino Nano, L298N, ACS712-5, encoder Hall del JGA25-370, fuente de 12 V). Ningún dato de esta carpeta es simulado. Los tomó Claude Opus 5.5 (asistente de IA) desde la computadora del autor, con su permiso, usando `ensayos_tema4.py` y `prueba_pid.py` (ver la Entrada 16 de la bitácora de IA).

> **Antes de usarlos en el informe**, lean la sección «Limitaciones y lo que falta medir». La prueba (c) con carga inercial **no** está aquí, porque requiere montar el disco.

## Montaje y configuración

| Elemento | Valor |
|---|---|
| Programa | `ParteExperimental/MotorDC_L298N/MotorDC_L298N.ino` (versión del 22/11/2026, 1 Mbaud) |
| Driver | L298N, canal B: ENB = D3 (PWM a 490 Hz), IN3 = D4, IN4 = D5 |
| Fuente | 12 V nominal (no se midió el voltaje en los bornes del motor) |
| Sensor de corriente | ACS712 de 5 A en A0, en serie con el motor. Sensibilidad típica: 185 mV/A. Cero medido: ≈ 516 cuentas |
| Encoder | Hall, fases A y B en D8 y D9. Se asumieron **11 pulsos por vuelta** del eje del motor (44 cuentas) |
| Reducción de la caja | **No confirmada.** Todos los ángulos y velocidades son del **eje del motor** |
| Signo del encoder | En este montaje el encoder cuenta al revés respecto del voltaje. Los datos se procesaron con `invertir_encoder=True` y el PID usa la orden `I 1` |
| Carga | Ninguna (motor sin carga) |

## Qué se midió

| Carpeta | Ensayo de la guía | Detalle |
|---|---|---|
| `a_escalones/` | (a) Escalón a ≥ 4 niveles | PWM 64, 115, 166, 217 y 255 (de 25 % a 100 %), 2–3 repeticiones por nivel. Fases: 300 ms en reposo, 1500 ms de escalón y 1500 ms libre |
| `b_desaceleracion/` | (b) Desaceleración libre | Desde PWM 255 y 166, con 3000 ms libres; más una con **freno dinámico** para comparar |
| `c_pid/` | PID en el microcontrolador | Velocidad (media, baja y cruzando por cero; seno) y posición (±1 y ±5 vueltas; seno) |
| `c_pid/sintonia/` | Sintonía | Pruebas con otras ganancias, usadas para elegir las finales |
| `figuras/` | — | `a_escalones.png`, `b_desaceleracion.png` y `c_pid.png` (generadas con `figuras_tema4.py`) |
| `resumen_ensayos.csv` | — | Una fila por captura de (a) y (b) |

Muestreo de (a) y (b): **38 461,5 muestras/s**, con los datos brutos (ADC y fases A/B) de cada muestra. Telemetría del PID: **Ts = 5 ms (200 Hz)**.

## Archivos y columnas

**Captura rápida** (`a_escalones/` y `b_desaceleracion/`):

- `<nombre>.bin`: los bytes tal como llegaron.
- `<nombre>_crudo.csv`: **datos brutos** `n, t_s, motor, adc, fase_a, fase_b, perdida`.
- `<nombre>.json`: configuración del ensayo.
- `<nombre>_procesado.csv`: θ, ω e i calculados.

**PID** (`c_pid/`): `<nombre>.csv` con las columnas `t_s, k, cuenta, theta_rad, referencia, omega_rad_s, voltaje_V, adc, corriente_A, modo, estado`, y `<nombre>.json` con las ganancias, la referencia y las métricas. `voltaje_V` es el voltaje que pidió el controlador (ciclo × 12 V).

**Cómo abrirlos:**

- En la aplicación: **CAPTURA** → **VER** (lista también las subcarpetas), o **ENSAYOS** → **ABRIR ARCHIVO**.
- Por línea de comandos:

```powershell
python ParteExperimental/postprocesamiento.py ParteExperimental/datos/tema4_20261122/a_escalones/escalon_pwm255_r1 --invertir-encoder
```

```powershell
python ParteExperimental/figuras_tema4.py ParteExperimental/datos/tema4_20261122
```

## Resultados de (a) y (b)

Velocidad calculada por tiempo entre flancos, en el eje del motor. Corriente con promedio móvil de 0,5 ms. «t 63 %» se mide desde el escalón y «t 37 %» desde la desconexión.

| Archivo | PWM | Tramas recibidas / enviadas | Saltos | ω régimen [rad/s] | i régimen [A] | i pico [A] | t 63 % [ms] | t 37 % [ms] |
|---|---|---|---|---|---|---|---|---|
| `a_escalones/escalon_pwm064_r1` | 64 | 126896 / 126922 | 1 | 256.7 | 0.046 | 0.44 | 157 | 171 |
| `a_escalones/escalon_pwm064_r2` | 64 | 126774 / 126922 | 0 | 257.0 | 0.040 | 0.42 | 172 | 175 |
| `a_escalones/escalon_pwm064_r3` | 64 | 126696 / 126922 | 0 | 264.2 | 0.046 | 0.43 | 170 | 186 |
| `a_escalones/escalon_pwm115_r1` | 115 | 126922 / 126922 | 0 | 429.3 | 0.051 | 0.81 | 88 | 264 |
| `a_escalones/escalon_pwm115_r2` | 115 | 126922 / 126922 | 0 | 427.3 | 0.057 | 0.81 | 90 | 256 |
| `a_escalones/escalon_pwm166_r1` | 166 | 126922 / 126922 | 0 | 488.5 | 0.057 | 0.87 | 56 | 282 |
| `a_escalones/escalon_pwm166_r2` | 166 | 126667 / 126922 | 2 | 489.7 | 0.055 | 0.93 | 58 | 283 |
| `a_escalones/escalon_pwm166_r3` | 166 | 126922 / 126922 | 0 | 491.8 | 0.059 | 0.83 | 57 | 296 |
| `a_escalones/escalon_pwm217_r1` | 217 | 126922 / 126922 | 0 | 513.4 | 0.058 | 1.03 | 37 | 298 |
| `a_escalones/escalon_pwm217_r2` | 217 | 126922 / 126922 | 0 | 513.4 | 0.055 | 1.22 | 37 | 298 |
| `a_escalones/escalon_pwm255_r1` | 255 | 126922 / 126922 | 0 | 546.8 | 0.063 | 1.21 | 21 | 306 |
| `a_escalones/escalon_pwm255_r2` | 255 | 126819 / 126922 | 0 | 547.5 | 0.060 | 1.19 | 21 | 313 |
| `a_escalones/escalon_pwm255_r3` | 255 | 126922 / 126922 | 0 | 548.1 | 0.054 | 1.20 | 21 | 317 |
| `b_desaceleracion/libre_pwm255_r1` | 255 | 184608 / 184614 | 0 | 548.0 | 0.063 | 1.22 | 21 | 312 |
| `b_desaceleracion/libre_pwm255_r2` | 255 | 183680 / 184614 | 0 | 547.9 | 0.062 | 1.32 | 21 | 314 |
| `b_desaceleracion/libre_pwm255_r3` | 255 | 184614 / 184614 | 0 | 548.3 | 0.058 | 1.25 | 21 | 322 |
| `b_desaceleracion/libre_pwm166_r1` | 166 | 184614 / 184614 | 0 | 491.2 | 0.059 | 0.89 | 57 | 295 |
| `b_desaceleracion/libre_pwm166_r2` | 166 | 184614 / 184614 | 0 | 492.0 | 0.057 | 0.93 | 57 | 298 |
| `b_desaceleracion/freno_pwm255_r1` | 255 | 126922 / 126922 | 0 | 548.3 | 0.061 | 1.23 | 21 | 25 |

**Observaciones** (para discutir en el informe; no son conclusiones cerradas):

- **La velocidad no es proporcional al PWM:** pasa de 257 a 547 rad/s entre 25 % y 100 %, y la constante de tiempo aparente baja de ~160 ms a ~21 ms. Una explicación probable es el PWM de 490 Hz: cuando ENB se apaga, la corriente del motor puede llegar a cero antes del siguiente pulso, así que el voltaje medio en los bornes no es ciclo × 12 V. Medirlo con el multímetro lo confirmaría.
- **La desaceleración libre** (t 37 % ≈ 0,26–0,32 s) es mucho más lenta que con freno dinámico (25 ms).
- **Pérdidas:** en 6 de las 19 capturas faltan entre 6 y 934 tramas. El Arduino no perdió ninguna: se pierden en el adaptador USB. Los tiempos después de cada hueco quedan corridos unos milisegundos. Cada condición tiene al menos dos repeticiones completas o casi completas.
- **Artefacto:** el pico de la curva de PWM 64 en `a_escalones.png` (t ≈ 1,15 s) viene de un hueco en `escalon_pwm064_r1`.

## Resultados del PID

**Ley de control** en el Arduino: u = Kp·e + Ki·Ts·E + (Kd/Ts)·(e − e_anterior), con E la suma de los errores. Tiene anti-windup y saturación a ±12 V, con Ts = 5 ms.

**Ganancias elegidas** (ya cargadas en la aplicación, por modo):

| Modo | Kp | Ki | Kd | Unidades |
|---|---|---|---|---|
| Velocidad | 0,04 | 0,4 | 0 | V por rad/s |
| Posición | 3 | 5 | 0,06 | V por rad |

| Archivo | Modo | Kp / Ki / Kd | Referencia | Sobreimpulso medio [%] | Establecimiento 5 % medio [s] | Error final medio | Error RMS | Saturado [%] |
|---|---|---|---|---|---|---|---|---|
| `velocidad_cuadrada_200_400` | vel | 0.04 / 0.4 / 0.0 | cuadrada 300 ± 100 rad/s, 0,5 Hz | 6.5 | 0.189 | 0.191 | 35.084 | 0.19 |
| `velocidad_cuadrada_50_150` | vel | 0.04 / 0.4 / 0.0 | cuadrada 100 ± 50 rad/s, 0,5 Hz | 23.0 | 0.953 | 0.180 | 18.032 | 0.0 |
| `velocidad_cuadrada_menos200_200` | vel | 0.04 / 0.4 / 0.0 | cuadrada 0 ± 200 rad/s, 0,5 Hz | 3.7 | 0.259 | 0.129 | 53.097 | 0.9 |
| `velocidad_seno_300` | vel | 0.04 / 0.4 / 0.0 | seno 300 ± 100 rad/s, 0,5 Hz | — | — | — | 17.166 | 0.0 |
| `posicion_cuadrada_1vuelta` | pos | 3.0 / 5.0 / 0.06 | cuadrada 0 ± 6,28 rad, 0,5 Hz | 1.8 | 0.066 | 0.143 | 1.917 | 2.06 |
| `posicion_cuadrada_5vueltas` | pos | 3.0 / 5.0 / 0.06 | cuadrada 0 ± 31,4 rad, 0,25 Hz | 1.0 | 0.136 | 0.323 | 10.910 | 6.16 |
| `posicion_seno_5vueltas` | pos | 3.0 / 5.0 / 0.06 | seno 0 ± 31,4 rad, 0,25 Hz | — | — | — | 0.332 | 0.0 |

Notas:

- **Promedios:** el sobreimpulso y el establecimiento son promedios sobre todos los escalones de cada onda cuadrada.
- **Error RMS:** en las ondas cuadradas está dominado por los transitorios; en los senos sí mide el seguimiento.
- **Baja velocidad:** a 50–150 rad/s el sobreimpulso sube a ~23 % y el rizado a ±4–5 rad/s. A 50 rad/s el encoder cambia solo ~1,75 cuentas cada 5 ms, y además pesa la fricción de Coulomb.

## Limitaciones y lo que falta medir

- **(c) Carga inercial:** no se hizo. Con el disco montado, se repite con:
  `python ensayos_tema4.py COM7 --carpeta datos/tema4_20261122 --sufijo carga --invertir-encoder`
- **Resistencia del devanado:** medirla con el multímetro entre los dos cables de potencia, con el motor desconectado.
- **Pulsos por vuelta y reducción:** confirmarlos con la etiqueta o la hoja de datos del motor.
  - **Pulsos por vuelta:** se usaron 11, que es lo que reporta el repuesto JGA25-370-E de Abra Electronics.
  - **Polos del disco magnético:** según la tabla de un fabricante de encoders (CHIHAI), 11 pulsos por vuelta corresponden a 22 polos alternados.
  - Ninguna de las dos fuentes es la hoja de datos de *este* motor.
- **Voltaje aplicado:** se registró el voltaje **pedido** (ciclo × 12 V), no el medido en los bornes del motor.
- **ACS712:** se usó la sensibilidad típica de 185 mV/A (la hoja de datos da 178–193 mV/A). El ruido de la corriente cruda es de ±0,1 A aproximadamente.

## Fuentes

- Allegro MicroSystems, *ACS712 datasheet*: tabla de selección (05B: ±5 A, 185 mV/A).
- Abra Electronics, *JGA25-370-E DC Motor Hall Effect Speed Encoder*: 11 pulsos por vuelta por fase.
- CHIHAI, *Magnetic Hall motor encoder boards & magnets*: relación entre polos y pulsos por vuelta.
