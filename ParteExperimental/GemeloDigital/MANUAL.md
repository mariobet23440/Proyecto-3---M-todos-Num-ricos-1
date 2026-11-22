# Manual de la aplicación del gemelo digital

Aplicación de escritorio para el motor DC JGA25-370 con L298N:

- ver el motor en tiempo real (y su modelo, el **gemelo digital**);
- controlarlo con el PID del Arduino;
- y, sobre todo, **capturar datos**.

> [!WARNING]
> La aplicación y el programa del Arduino se generaron con IA y se probaron con un **Arduino
> simulado**, no con el motor real. La primera vez, pruebe con el motor sin carga y con la mano
> cerca del botón **STOP** (o del cable de la fuente).

---

## Índice

1. [Antes de empezar](#1-antes-de-empezar)
2. [La ventana](#2-la-ventana)
3. [Primer uso: conectar y configurar](#3-primer-uso-conectar-y-configurar)
4. [**Cómo capturar datos**](#4-cómo-capturar-datos)
5. [Tablero: el gemelo digital en vivo](#5-tablero-el-gemelo-digital-en-vivo)
6. [Control PID](#6-control-pid)
7. [Ver y reproducir resultados](#7-ver-y-reproducir-resultados)
8. [Modelo](#8-modelo)
9. [Problemas comunes](#9-problemas-comunes)

---

## 1. Antes de empezar

**Una sola vez:**

1. Instale las librerías de Python (desde la carpeta `ParteExperimental/GemeloDigital`):
   ```powershell
   pip install -r requirements.txt
   ```
2. Cargue en el Arduino Nano el programa
   [`MotorDC_L298N.ino`](../MotorDC_L298N/MotorDC_L298N.ino) con el IDE de Arduino.
3. *(Opcional)* Para que toda la interfaz tenga letra pixelada, copie las fuentes en
   `fuentes/` (ver [`fuentes/LEEME.md`](fuentes/LEEME.md)).

**Cada vez que arme el circuito, revise:**

- [ ] El **puente (jumper) de ENB** del L298N está **quitado** (ENB va a D3).
- [ ] IN3 en D4, IN4 en D5, el ACS712 en A0, la fase A del encoder en D8 y la B en D9.
- [ ] **Todas las tierras unidas:** Nano, L298N, fuente del motor, ACS712 y encoder.
- [ ] El encoder y el ACS712 están alimentados con 5 V.

**Para abrir la aplicación:**

```powershell
python app.py
```

La ventana se abre maximizada.

---

## 2. La ventana

- **Menú de la izquierda.** Cambia entre las seis páginas:

  | Botón | Para qué sirve |
  |-------|----------------|
  | **CONEXION** | Conectar el Arduino (o el simulado), datos del hardware, consola |
  | **TABLERO** | Ver todo en vivo: animación del motor y gráficas |
  | **CONTROL PID** | Elegir el modo de control, mover las perillas y arrancar |
  | **ENSAYOS** | Escalón, desconexión, seguir un movimiento y ver resultados |
  | **CAPTURA** | Grabar la telemetría y ver los archivos guardados |
  | **MODELO** | Parámetros del modelo del motor y simulación |

- **STOP (rojo).** Siempre está a la vista. Pone el motor en reposo de inmediato.
- **Estado, abajo a la izquierda:**
  - **CONECTADO COM5** (verde), **SIMULADO** (amarillo) o **DESCONECTADO** (rojo);
  - **MODO**: lo que está haciendo el Arduino;
  - **TRAMAS**: cuántos datos por segundo llegan (unos 500/s con Ts = 2 ms);
  - **MALAS**: tramas dañadas (debe quedarse en 0 o casi).

> **Seguridad.** La aplicación le avisa al Arduino que sigue viva cada medio segundo. Si se
> cierra o se desconecta el cable, el Arduino detiene el motor solo, en 2 s.

---

## 3. Primer uso: conectar y configurar

Página **CONEXION**.

### 3.1 Conectar

1. Conecte el Nano por USB.
2. Presione **BUSCAR** y elija el puerto (por ejemplo `COM5`).
3. Deje **BAUDIOS** en `2000000` y presione **CONECTAR**.
4. Espere unos 2 s: el Nano se reinicia al abrir el puerto. En la consola debe aparecer una
   línea `# LISTO ...` y después `# CFG ...`.

**Sin el motor:** presione **SIMULADO**. La aplicación funciona igual, con un Arduino y un motor
simulados. Sirve para practicar todo este manual antes de tocar el hardware.

**SALIR** desconecta (y antes detiene el motor).

### 3.2 Datos del hardware (sección HARDWARE)

| Casilla | Qué poner |
|---------|-----------|
| **PULSOS/VUELTA ENCODER (EJE MOTOR)** | Pulsos por vuelta del encoder en el eje del motor (PPR). Suele ser 11 en el JGA25-370, pero **confírmelo** con la hoja de datos de su motor. |
| **REDUCCION N DE LA CAJA** | La reducción de la caja (por ejemplo 34 si es 1:34). Con N = 1, la posición y la velocidad son las del **eje del motor**; con la N real, las del **eje de salida**. |
| **VREF DEL ADC [V]** | El 5 V real del Nano, medido con multímetro entre 5V y GND. |
| **SENSIBILIDAD ACS712 [V/A]** | 0.185 para el ACS712 de 5 A. |
| **CERO DEL SENSOR** | Lo llena el botón **CALIBRAR CERO**. |
| **VOLTAJE DE LA FUENTE [V]** | El de la fuente del L298N (por ejemplo 12). |

Luego:

1. Presione **APLICAR**. Abajo aparece `CUENTAS/VUELTA = 4 x PPR x N`.
2. Con el motor **quieto** y conectado, presione **CALIBRAR CERO**: mide el sensor de corriente
   sin corriente.
3. Si la corriente sale con el signo al revés, active **INVERTIR SIGNO DE LA CORRIENTE**.
4. Si la posición crece al revés de lo que espera, **intercambie los cables A y B del
   encoder**. No basta con el interruptor «INVERTIR ENCODER»: ese solo afecta a la captura
   rápida, y el PID usa el signo del Arduino.

Todo esto se guarda solo para la próxima vez.

### 3.3 Consola

Muestra los mensajes del Arduino (`# OK`, `# ERR`, `# AVISO`). Abajo puede escribir órdenes
a mano (por ejemplo `?` para ver la configuración) y presionar **ENVIAR**.

---

## 4. Cómo capturar datos

Hay **tres formas** de capturar datos. Elija según lo que necesite:

| Forma | Dónde | Qué guarda | Muestras/s | Para qué |
|-------|-------|------------|------------|----------|
| **A. Captura rápida** (escalón o desconexión) | ENSAYOS → **ESCALON** o **DESCONEXION** | Datos **brutos**: ADC del sensor y fases A/B del encoder | **≈ 76 923** | Identificar el motor: constantes de tiempo, corriente de arranque, R, L, Ke... |
| **B. Seguir un movimiento** | ENSAYOS → **SEGUIR MOVIMIENTO** | Telemetría del PID durante unos segundos | 1/Ts (500 con Ts = 2 ms) | Evaluar el controlador con una referencia senoidal, cuadrada o triangular |
| **C. Grabación libre** | CAPTURA → **GRABAR** | Telemetría de lo que esté pasando, hasta que usted la detenga | 1/Ts | Cualquier cosa: pruebas a mano, PID con perillas, lazo abierto |

Todos los archivos van a la **carpeta de datos**: por defecto `ParteExperimental/datos/`; se
cambia en CAPTURA → **CAMBIAR CARPETA**.

### Lista rápida antes de cualquier captura

- [ ] Conectado (estado verde) y con **MALAS** en 0.
- [ ] Datos del hardware aplicados (3.2) y **CERO** calibrado hace poco.
- [ ] Motor sin carga (o con la carga que quiera medir) y nada que pueda engancharse.

---

### A. Captura rápida: respuesta al escalón y a la desconexión

Es la captura más importante para el proyecto: guarda **todo** a la máxima frecuencia, en datos
brutos, y la aplicación calcula después la posición, la velocidad y la corriente.

**Qué hace el Arduino.** Durante la captura no hace nada más (el PID y las gráficas en vivo se
pausan). Tiene tres fases:

```
  motor libre          escalón (PWM fijo)          desconexión
|<---- PREVIA ---->|<-------- ESCALON -------->|<---- DESCONEXION ---->|
  mide el cero         respuesta al escalón        el motor se frena solo
  del sensor                                       (o con freno dinámico)
```

**Pasos:**

1. Vaya a **ENSAYOS**.
2. En el recuadro **ESCALON / DESCONEXION**, ajuste:
   - **PWM** (perilla): 255 = voltaje completo. Valores menores aplican un PWM de 490 Hz y la
     corriente se ve con rizado.
   - **PREVIA [ms]**: 200 está bien (sirve para medir el cero del sensor).
   - **ESCALON [ms]**: lo suficiente para que el motor llegue a velocidad constante. Empiece
     con 1500.
   - **DESCONEXION [ms]**: lo suficiente para que el motor se detenga. Empiece con 1500.
   - **ADELANTE / REVERSA**: sentido de giro.
   - **FRENAR AL DESCONECTAR**: apagado, el motor queda libre (se frena por fricción);
     encendido, el L298N pone los bornes en corto (frenado dinámico).
3. Presione:
   - **ESCALON**: le interesa el arranque. La fase de desconexión se recorta a 300 ms como
     máximo para no esperar de más.
   - **DESCONEXION**: le interesa el frenado. Usa todo el tiempo de DESCONEXION.
4. Espere. Debajo de los botones verá:
   1. `ESPERANDO A QUE EL MOTOR SE DETENGA...`: la aplicación detiene el motor y espera a que
      esté quieto (hasta 8 s), para que el ensayo empiece desde el reposo.
   2. `CAPTURA RAPIDA EN CURSO...` con la barra naranja avanzando. El LED de la placa del Nano
      se enciende.
   3. `PROCESANDO...`
   4. `LISTO: ESCALON` (o `DESCONEXION`). Se abre la reproducción (sección 7).
5. Revise el **resumen** (abajo a la izquierda). Si aparece en rojo **SALTOS INVALIDOS EN EL
   ENCODER** o **SE PERDIERON TRAMAS**, lea la sección 9.

**Archivos que se guardan** (`<tipo>` es `escalon` o `desconexion`, con fecha y hora):

| Archivo | Contenido |
|---------|-----------|
| `<tipo>_AAAAMMDD_HHMMSS.bin` | Los bytes tal como llegaron del Arduino. Permite reprocesar todo si hace falta. |
| `<tipo>_..._crudo.csv` | **Datos brutos**: `n, t_s, motor, adc, fase_a, fase_b, perdida` |
| `<tipo>_....json` | Configuración del ensayo (fs, número de muestras de cada fase, PWM, sentido, freno) |
| `<tipo>_..._procesado.csv` | `t_s, motor, cuenta, theta_rad, omega_flancos_rad_s, omega_centrada_rad_s, corriente_A, corriente_suave_A` |
| `<tipo>_..._resumen.json` | Velocidad y corriente de régimen, pico de corriente, t al 63 % (escalón), t al 37 % (desconexión) |

- **Columnas brutas:** `motor` = 1 mientras el motor estaba alimentado; `adc` va de 0 a 1023;
  `fase_a`/`fase_b` valen 0 o 1; `perdida` = 1 si se perdieron datos justo antes.
- **Velocidad:** `omega_flancos` (tiempo entre flancos) es la más precisa;
  `omega_centrada` es la diferencia centrada con h = 2 ms, para comparar métodos.
- **Corriente:** `corriente_suave` es un promedio móvil de 0,5 ms.

> Los archivos crudos se pueden reprocesar sin la aplicación, por ejemplo con otra reducción:
> ```powershell
> python ..\postprocesamiento.py ..\datos\escalon_20261122_172135 --ppr 11 --reduccion 34
> ```

---

### B. Seguir un movimiento (con el PID)

Mueve el motor siguiendo una referencia y graba todo durante el tiempo que usted diga.

1. **Primero sintonice el PID** en la página **CONTROL PID** (sección 6). Este botón usa las
   ganancias, Ts y el filtro que estén allí.
2. Vaya a **ENSAYOS**, recuadro **SEGUIR MOVIMIENTO (USA EL PID)**:
   - **POSICION** o **VELOCIDAD**: qué se controla.
   - **SENO**, **CUADRADA** o **TRIANGULAR**: la forma de la referencia.
   - **AMPLITUD**, **DESFASE** y **FRECUENCIA [Hz]**: la referencia es
     `r(t) = DESFASE + AMPLITUD · forma(2π·f·t)`. Se mide en **rad** (posición) o **rad/s**
     (velocidad), del eje que configuró con N. Ejemplo: una vuelta de ida y vuelta es
     SENO, AMPLITUD 3.14, DESFASE 0, FRECUENCIA 0.5.
   - **DURACION [s]**: cuánto tiempo grabar.
3. Presione **SEGUIR MOVIMIENTO**. La aplicación:
   1. pone la cuenta del encoder en cero;
   2. envía las ganancias y la referencia;
   3. arranca el PID y graba;
   4. al terminar, detiene el motor y abre la reproducción, con la referencia en verde.

**Archivos:** `seguimiento_AAAAMMDD_HHMMSS.csv` y `.json` (columnas en la tabla de la parte C).
El resumen incluye el **error RMS** y el **% del tiempo saturado**: si es alto, el motor no da
más y la referencia pide demasiado.

---

### C. Grabación libre de la telemetría

Graba lo que esté pasando en tiempo real: el PID que usted mueve con las perillas, el lazo
abierto o el motor girado a mano en reposo.

1. Ponga el motor en el estado que quiera (por ejemplo, arranque un PID en **CONTROL PID**).
2. Vaya a **CAPTURA**. *(Opcional)* Escriba un **NOMBRE** para el archivo.
3. Presione **GRABAR**. El texto cambia a `GRABANDO  N MUESTRAS  T S`.
4. Puede cambiar de página y mover perillas: **sigue grabando**.
5. Vuelva a **CAPTURA** y presione **DETENER**. El archivo se guarda solo y aparece en la lista.

**Archivos:** `<NOMBRE>.csv` y `.json`, o `tiempo_real_AAAAMMDD_HHMMSS` si no puso nombre.

| Columna | Significado |
|---------|-------------|
| `t_s` | Tiempo (s) |
| `k` | Número de periodo del Arduino |
| `cuenta` | Posición en cuentas del encoder |
| `theta_rad` | Posición (rad) |
| `referencia` | r(t) (V en lazo abierto, rad/s o rad en los PID) |
| `omega_rad_s` | Velocidad filtrada que usa el PID (rad/s) |
| `voltaje_V` | Voltaje que pidió el controlador, ya saturado (V) |
| `adc` | Promedio del ADC en el periodo (cuentas) |
| `corriente_A` | Corriente (A) |
| `modo` | 0 reposo · 1 lazo abierto · 2 velocidad · 3 posición |
| `estado` | Bits: 1 saturado · 2 error del encoder · 4 periodo atrasado · 8 E_k congelado (anti-windup) |
| `gemelo_*` | Lo mismo según el modelo (gemelo digital) |

El `.json` guarda toda la configuración de la aplicación y del Arduino en ese momento
(ganancias, Ts, PPR, N...), para saber después con qué se midió.

---

### Abrir capturas guardadas

- **CAPTURA** muestra todos los archivos de la carpeta de datos (los más nuevos arriba). Naranja
  = captura rápida; cian = tiempo real. **VER** los abre en la reproducción de ENSAYOS.
- O bien: ENSAYOS → **ABRIR ARCHIVO** y elija el `.json`.
- **ABRIR CARPETA** abre la carpeta en el Explorador de Windows.

> Las capturas rápidas se **reprocesan al abrirlas** con los datos del hardware que estén en
> CONEXION en ese momento. Si cambia PPR o N, al volver a abrirlas cambian las unidades.

---

## 5. Tablero: el gemelo digital en vivo

- **Animación** (arriba a la izquierda):
  - el L298N, con su LED verde que brilla según el PWM;
  - el ACS712 y los cables, con «electrones» amarillos que corren según la corriente;
  - el motor y la caja;
  - el **disco del encoder** con sus imanes y los sensores **A** y **B**, que se encienden con
    los datos reales;
  - el **disco de salida**: la marca amarilla es la posición medida, el cuadrado rosado la del
    gemelo y el punto verde la referencia (en modo posición).
- **Lecturas:** posición, velocidad, corriente, voltaje y referencia.
- **Gráficas de barrido** (θ, ω, i, u): como en un osciloscopio, el **cursor amarillo** avanza
  y va borrando el barrido anterior. Línea de color = medida; verde = referencia; blanca
  punteada = **gemelo**.
- Controles:
  - **GEMELO DIGITAL**: enciende o apaga el modelo en vivo.
  - **PAUSAR GRAFICAS**: congela las gráficas (los datos se siguen recibiendo).
  - **SINCRONIZAR**: pone el gemelo en la posición y la velocidad medidas. Úselo cuando se
    separen mucho: el modelo no sabe lo que usted hizo con la mano.
  - **CERO ENCODER**: la posición actual pasa a ser 0.
  - **VENTANA [S]**: segundos que caben en la gráfica (escriba el valor y presione Enter).

---

## 6. Control PID

### Las perillas

- **Arrastrar** hacia arriba o abajo: cambia el valor. Con **Shift**, el cambio es fino.
- **Rueda del ratón** sobre la perilla: pasos pequeños.
- **Doble clic**, o escribir en la casilla de abajo y presionar Enter: valor exacto.
- **KP, KI, KD** usan escala logarítmica: girarlas toda a la izquierda da exactamente 0.
- Con **ENVIAR AL SOLTAR LA PERILLA** activado, cada cambio se manda al Arduino al soltar, y se
  puede sintonizar con el motor girando.

### Cómo usarlo

1. **MODO**:
   - **LAZO ABIERTO**: la referencia es directamente el voltaje (V). Sirve para probar el
     driver.
   - **VELOCIDAD**: la referencia está en rad/s.
   - **POSICION**: la referencia está en rad.
2. **GANANCIAS**: KP, KI, KD, **TS** (periodo de muestreo, ms) y **FILTRO** (constante de tiempo
   del filtro de la velocidad, ms). Arriba se ve la fórmula que se usa:
   `u = Kp e + Ki Ts E + (Kd/Ts)(e - e_ant)`, con `E = E_ant + e` y u en voltios.
   - **ANTI-WINDUP**: si el voltaje se satura, deja de acumular el error.
3. **REFERENCIA r(t)**: CONSTANTE, SENO, CUADRADA o TRIANGULAR, con AMPLITUD, DESFASE y
   FRECUENCIA. En CONSTANTE, la referencia es el **DESFASE**.
4. **ARRANCAR** manda todo y arranca. **DETENER** (o STOP) pone el motor en reposo y borra la
   memoria del PID.

Cambiar de modo o de TS pone en cero la memoria del PID (E y e_ant).

**Sugerencia para empezar:** en VELOCIDAD, con KI y KD en 0, suba KP poco a poco hasta que
responda rápido sin oscilar. Luego agregue KI para quitar el error permanente. Pruébelo
primero con el **SIMULADO**.

---

## 7. Ver y reproducir resultados

Página **ENSAYOS**, parte de abajo. Después de una captura, o al abrir un archivo:

- **Gráficas:** θ, ω e i medidos (color), el **gemelo** (blanco punteado) y la referencia
  (verde, si la hay). Las líneas verticales punteadas marcan el escalón y la desconexión.
- **Cursor amarillo:** recorre el tiempo. La **animación del motor** muestra lo que pasaba en
  ese instante.
- Controles:
  - **PLAY / PAUSA**.
  - **|<**: vuelve al inicio.
  - **Velocidad** (0.01x a 1x): una captura rápida dura unos segundos pero pasa casi todo en
    milisegundos, por eso empieza en 0.02x (cámara lenta).
  - **Barra deslizante** o **clic sobre una gráfica**: salta a ese instante.
  - **PNG**: guarda la gráfica en la carpeta de datos.
- **Resumen:** los números del ensayo y avisos en rojo si algo salió mal.

---

## 8. Modelo

Parámetros del modelo del cuaderno:

```
L di/dt = V - R i - Ke ω
J dω/dt = Kt i - b ω - τc sign(ω) - τcarga
dθ/dt   = ω
```

- **Los valores iniciales son de EJEMPLO** (solo R = 6 Ω viene del equipo y L = 2 mH es
  supuesto). Reemplácelos por los que identifiquen con las capturas rápidas.
- **CAIDA L298N [V]**: el L298N «se come» un par de voltios. Mida el voltaje real en los bornes
  del motor y ajústelo.
- **INTEGRADOR**: **Euler** o **RK4**, con el paso **h**. Abajo se ven los valores propios, las
  constantes de tiempo y el **h máximo para que Euler sea estable**. Pruebe un h mayor a ese
  límite con Euler y vea qué pasa (la aplicación reinicia el gemelo si diverge).
- **APLICAR**: usa estos valores en el gemelo.
- **SIMULAR**: un escalón con el voltaje de la fuente.
- **COMPARAR CON LA ULTIMA CAPTURA**: superpone el modelo a la última captura rápida. Es la
  forma de ajustar los parámetros a mano.

---

## 9. Problemas comunes

| Síntoma | Qué revisar |
|---------|-------------|
| No aparece el puerto | Cable USB de datos (no solo de carga), driver CH340 instalado, **BUSCAR** otra vez. |
| Conecta, pero TRAMAS = 0 y la consola vacía | ¿El Nano tiene cargado `MotorDC_L298N.ino`? ¿Baudios = 2000000? Algunos adaptadores no llegan a 2 Mbaud: en el `.ino` ponga `BAUDIOS = 1000000UL` y `PRESCALER_ADC_RAPIDO = 32`, vuelva a cargarlo y conecte con 1000000. |
| MALAS sube sin parar | Cable USB largo o con ruido; tierra común; pruebe 1000000 baudios. |
| El motor no gira | Jumper de ENB todavía puesto (ENB debe venir de D3), fuente del L298N apagada, IN3/IN4 mal conectados. |
| La posición crece al revés | Intercambie los cables A y B del encoder. |
| La corriente sale negativa al acelerar hacia adelante | Active **INVERTIR SIGNO DE LA CORRIENTE**, o dé vuelta al ACS712. |
| La corriente no es 0 con el motor quieto | **CALIBRAR CERO** (con el motor quieto). |
| **SALTOS INVALIDOS EN EL ENCODER** | El encoder cambió más rápido de lo que se muestreó, o hay ruido en los cables A/B. Cables más cortos, tierra común; si el motor va muy rápido, baje el PWM. |
| **SE PERDIERON TRAMAS** | El UART no alcanzó. Los tiempos después de la pérdida no son exactos: repita el ensayo. Si se repite, use 1000000 baudios y `PRESCALER_ADC_RAPIDO = 32` (38 461 muestras/s). |
| «El motor no se detuvo en 8 s» | El motor seguía girando (o el encoder vibra en un flanco). El ensayo empieza igual; revise que el motor esté quieto. |
| El motor se detuvo solo con `# AVISO sin comunicacion` | La aplicación dejó de responder más de 2 s (o se desconectó el cable). Es la protección del Arduino. |
| El gemelo se va lejos de la medición | Normal si los parámetros son de ejemplo. **SINCRONIZAR** y ajuste el modelo (sección 8). |
| La interfaz va lenta | Cierre otros programas pesados; suba **TS** (menos datos por segundo) o use una **VENTANA** más corta. |
