# Bitácora de uso de IA

Registro de cada uso de herramientas de inteligencia artificial en el Proyecto 3 de Métodos Numéricos 1: qué se pidió, qué hizo la herramienta y qué decidió el equipo.

> Todo lo que produzca la IA es una **propuesta**. Solo se incorpora al cuaderno lo que los miembros del equipo revisen y aprueben.

---

## Entrada 1 — 21/11/2026

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Versión revisada** | `Proyecto3MetodosNumericos.ipynb`, commit `7b05bf5` |

### Solicitud
1. Listar los archivos de la carpeta del proyecto.
2. Revisar el desarrollo matemático del cuaderno y detectar errores.
3. Crear esta bitácora.
4. Organizar los archivos del repositorio.
5. No subir nada a GitHub todavía.

### Lo que hizo la IA
- **Lectura del cuaderno.** Leyó las 14 celdas: Introducción, modelo del motor y secciones 1.1 a 1.4. La celda de código está vacía.
- **Revisión matemática.** Encontró 16 observaciones, clasificadas por gravedad:
  - **4 errores conceptuales.** Entre ellos: la igualdad $\mathbf{y}' = J\mathbf{y}$ de la sección 1.2 confunde el Jacobiano con el campo vectorial $\mathbf{f}$; la forma $(1+hJ)\mathbf{y}_k$ solo vale para sistemas lineales; el símbolo $J$ se usa para la inercia y para el Jacobiano; y hay un índice incorrecto ($\mathbf{y}_{k+1}$ por $\mathbf{y}_k$) en la ecuación del error de 1.4.
  - **4 imprecisiones.** Linealización de $\mathbf f$, justificación para descartar el error de truncamiento, resto de Taylor vectorial, y no diferenciabilidad de $\operatorname{sign}(\omega)$.
  - **8 observaciones de notación, LaTeX y redacción.**
  - El detalle está en [`correcciones/Correcciones_DesarrolloMatematico_2026-11-21.md`](correcciones/Correcciones_DesarrolloMatematico_2026-11-21.md) (ver Entrada 2).
- **Organización del repositorio.**
  - Creó `README.md` con la descripción del proyecto, el botón de Colab y la estructura.
  - Creó `.gitignore` para Jupyter, Python y archivos del sistema operativo.
  - Dejó el cuaderno en la raíz para no romper el enlace de Colab ni el flujo *Guardar una copia en GitHub*.
- **Esta bitácora.** Creó `BitacoraUsoIA.md`.

### Lo que la IA NO hizo
- **No modificó el cuaderno.**
- **No hizo commit ni push** a GitHub.

### Corrección a una respuesta anterior de la IA
Al listar los archivos, la IA dijo que parecía faltar la sección 1.3. Era un error: la sección 1.3 ("Sistemas de EDOs de orden superior") existe y está dentro de la misma celda que la 1.2.

---

## Entrada 2 — 22/11/2026

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Versión revisada** | `Proyecto3MetodosNumericos.ipynb`, commit `7b05bf5` (sin cambios desde la Entrada 1) |

### Solicitud
1. Generar un documento completo con el detalle de las correcciones.
2. Incluir:
   - un aviso de que las revisiones deben ser aprobadas por los miembros del equipo;
   - un espacio para los datos del revisor;
   - una sección final para las observaciones del revisor.
3. Subirlo a GitHub en una carpeta de correcciones, junto con esta bitácora.
4. **No aplicar las correcciones al cuaderno.** Van en un documento aparte.

### Lo que hizo la IA
- **Documento de correcciones.** Creó [`correcciones/Correcciones_DesarrolloMatematico_2026-11-21.md`](correcciones/Correcciones_DesarrolloMatematico_2026-11-21.md), con:
  - el aviso de aprobación obligatoria por el equipo;
  - una tabla para los datos de los revisores;
  - 16 correcciones (C-01 a C-16), cada una con ubicación, texto original, corrección propuesta, justificación, una casilla de decisión (aprobada / con cambios / rechazada) y un espacio para comentarios;
  - una tabla resumen de decisiones;
  - la sección final *Observaciones del revisor*;
  - una tabla de aprobación final del equipo.
- **Reorganización.**
  - Movió esta bitácora a la carpeta `correcciones/`.
  - Eliminó `docs/RevisionMatematica_2026-11-21.md`, un borrador de la Entrada 1 que nunca se subió. Su contenido quedó dentro del nuevo documento.
- **GitHub.** Hizo commit y push a la rama `main`, solo con la carpeta `correcciones/` (este documento y el de correcciones).

### Lo que la IA NO hizo
- **No modificó el cuaderno.**
- **No subió `README.md` ni `.gitignore`.** Quedan solo en la copia local, pendientes de que el equipo decida.
- **No verificó la referencia a Nise** (C-15), porque no tuvo acceso al libro. El equipo debe confirmarla.

### Decisiones del equipo
- *(pendiente: anotar qué correcciones se aprueban, cuáles se rechazan y por qué. Ver la tabla "Resumen de decisiones" del documento de correcciones)*

---

## Entrada 3 — 22/11/2026

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Material proporcionado** | PDF de N. S. Nise, *Control Systems Engineering*, 7.ª ed. (copia local del equipo) |

### Solicitud
1. Poner las correcciones en una carpeta de uso de IA.
2. Agregar la referencia al libro de Norman Nise en un archivo `.md` de referencias, enlazado desde el documento de correcciones.
3. Hacer commit de esos cambios.

### Lo que hizo la IA
- **Reorganización.** Movió todo a la carpeta `UsoIA/`:
  - `UsoIA/BitacoraUsoIA.md` (esta bitácora);
  - `UsoIA/correcciones/Correcciones_DesarrolloMatematico_2026-11-21.md`;
  - `UsoIA/correcciones/Referencias.md` (nuevo).
- **Consulta del libro.** Revisó en el PDF:
  - la página legal (edición, año, editorial e ISBN);
  - el índice;
  - las secciones §2.8 (motor DC, pp. 77–83), §2.10 (no linealidades, pp. 86–87) y §2.11 (linealización);
  - la nota al pie 8 de la p. 65 (fricción viscosa, no de Coulomb).
- **Referencias.md.** Contiene:
  - la referencia en formatos IEEE y APA, con ISBN;
  - una tabla con las secciones y páginas relevantes y su relación con el proyecto;
  - las equivalencias de notación entre Nise y el cuaderno;
  - las citas sugeridas para las celdas 7 y 8.
- **Documento de correcciones.**
  - **C-15** queda verificada: el motor DC está en el cap. 2, §2.8, no en el cap. 4 como decía el cuaderno.
  - ~~**C-03** y **C-16** tienen ahora respaldo del libro: la notación $J_m$ y la igualdad $K_t = K_b$ en unidades consistentes.~~ **Retirado: era un error de la IA. Ver Entrada 4.**
  - Se actualizaron los enlaces a la nueva estructura.
- **Commit local** con estos cambios.

### Lo que la IA NO hizo
- **No modificó el cuaderno.**
- **No subió el PDF del libro**, porque está protegido por derechos de autor. Solo se cita.
- **No hizo push** a GitHub; solo el commit local.
- **No incluyó `README.md` ni `.gitignore`** en el commit.

### Decisiones del equipo
- *(pendiente)*

---

## Entrada 4 — 22/11/2026 · Fe de erratas

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Detectado por** | Mario Betancourt |
| **Commits afectados** | `0bf8fa9` (ya publicado en GitHub) |

### Error de la IA
En la Entrada 3, la IA presentó el libro de Nise como **respaldo de las correcciones propuestas**. Esto era incorrecto:

- `Referencias.md` empezaba diciendo que la bibliografía "respalda las correcciones propuestas".
- **C-03** decía tener "respaldo bibliográfico" porque Nise usa $J_m$ para la inercia. La corrección trata de un choque de notación dentro del cuaderno, y que Nise use $J_m$ no la justifica.
- **C-16** citaba a Nise para la igualdad $K_t = K_b$. Es una observación física opcional, no una corrección del desarrollo matemático.
- `Referencias.md` asociaba las secciones §2.10 y §2.11 y la nota al pie 8 con C-08 y con la discusión de la celda 8. Esa relación no existe.

**Por qué era un error:** las correcciones C-01 a C-14 tratan de **métodos numéricos**: el método de Euler para sistemas, el Jacobiano, la estabilidad numérica y la notación matemática. El libro de Nise trata de modelado y control. No aborda esos temas y no puede respaldarlas. La IA vinculó el libro a las correcciones solo porque compartían términos (motor, inercia, linealización), sin que hubiera una relación real de respaldo.

### Lo que hizo la IA para corregirlo
- **`Referencias.md`.** Ahora es solo la referencia bibliográfica del modelo del motor que cita el cuaderno (celdas 7 y 8). Tiene una fe de erratas visible. Se quitaron las filas de p. 79, §2.10 y §2.11, y todas las menciones de que respalda C-03, C-08 o C-16.
- **Documento de correcciones.**
  - **C-03:** se eliminó la nota de "respaldo bibliográfico".
  - **C-16:** se eliminó la cita a Nise.
  - **C-15:** se limita a completar la cita (cap. 2, §2.8, pp. 77–83) y se dice que no afecta el contenido matemático.
  - **Encabezado:** ahora aclara que la referencia no respalda las demás correcciones.
- **Esta bitácora.** Se tachó la afirmación de la Entrada 3, sin borrarla, para que quede registro del error.

### Lo que sigue siendo válido
- Los datos bibliográficos del libro (7.ª ed., Wiley, 2015, ISBN) y la ubicación del modelo del motor (§2.8, pp. 77–83), que es lo que pide completar C-15.
- Las correcciones C-01 a C-16 **no dependían** del libro. Su contenido matemático no cambia con esta fe de erratas, y sigue pendiente de la revisión del equipo.

### Decisiones del equipo
- *(pendiente)*

---

## Entrada 5 — 22/11/2026 · Aplicación de correcciones aprobadas

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Insumo** | Rama `MarioBetancourt04-patch-1` (commit `a9b6dcf`), con las decisiones y los comentarios del revisor |

### Solicitud
1. Ejecutar las correcciones según los comentarios del revisor.
2. Hacer merge de la rama de revisión a `main`.

### Pregunta del autor antes de aplicar
El autor preguntó si C-01 era correcta, porque le hacía sentido que fuera el Jacobiano. La IA la verificó de nuevo con dos pruebas:
- **Contraejemplo escalar.** Para $y' = y^2$, el Jacobiano es $J = 2y$, así que $Jy = 2y^2 \neq y'$.
- **Simulación del motor desde el reposo con 12 V.** Con Euler, el motor arranca. Con $(I+hJ)\mathbf y_k$, el estado se queda en cero, porque los términos constantes ($V/L$) no caben en el Jacobiano.

El revisor aprobó C-01 con ese mismo argumento.

### Lo que hizo la IA
- **Merge.** Hizo merge de `MarioBetancourt04-patch-1` en `main`. Hubo un conflicto en C-03: se conservaron la decisión y el comentario del revisor, y se mantuvo retirada la nota de "respaldo bibliográfico" de Nise (fe de erratas, Entrada 4).
- **Cuaderno (commit `760c312`).** Aplicó las 14 correcciones aprobadas, siguiendo las instrucciones de los comentarios:
  - **C-01:** reemplazó el Jacobiano por el campo vectorial $\mathbf f$ en la deducción del método (1.2) y movió la definición del Jacobiano a la sección de estabilidad (1.4). El revisor lo pidió así: *"reemplazar todas las apariciones del Jacobiano en las deducciones del método por el campo vectorial f, excepto en la sección de análisis de estabilidad"*.
  - **C-02:** quitó $(1+hJ)\mathbf y_k$ sin presentar el caso lineal.
  - **C-06:** separó la propagación del error y el error local, **sin** agregar el criterio de valores propios. La diagonalización la revisará el autor.
  - **C-08:** agregó la observación sobre la fricción de Coulomb, con el matiz del revisor sobre el punto de operación, y sin análisis de valores propios.
  - **C-13:** atendió la nota escondida del autor, "(revisar notación de conjunto)".
  - **C-03, C-04, C-05, C-07, C-09, C-10, C-11, C-14 y C-16:** aplicadas como estaban propuestas.
- **No aplicó** las correcciones rechazadas:
  - **C-12:** se mantiene $x$ en las demostraciones.
  - **C-15:** el texto pendiente de la cita a Nise queda como está.
- **Verificación.**
  - Solo cambiaron los textos de las celdas 4, 6, 7, 8, 10, 11 y 12. Los ids, los metadatos y el enlace de Colab siguen igual.
  - Las 136 expresiones LaTeX del cuaderno compilan en MathJax 3.2.2 sin errores, y no queda ningún `$` sin cerrar.
- **Documento de correcciones.**
  - Llenó la tabla *Resumen de decisiones* con lo que indicó el revisor.
  - Eliminó la sección *Aprobación final del equipo*, como pidió el revisor.
  - Actualizó el aviso y el estado del encabezado.

### Lo que la IA NO hizo
- **No completó la lista de integrantes** ("Pongan sus nombres y (carnets)"), porque no conoce los nombres.
- **No agregó la observación física $K_e = K_t$** (C-16, opcional), porque el cuaderno todavía no tiene parámetros numéricos.
- **No hizo push** a GitHub.

### Decisiones del equipo
- Las 16 decisiones están en el documento de correcciones (revisor: Mario Alejandro Betancourt Franco).

---

## Entrada 6 — 22/11/2026 · Parte experimental: programa y esquemático

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Documentación** | [`ParteExperimental/Programa_RespuestaEscalon.md`](ParteExperimental/Programa_RespuestaEscalon.md) · [`ParteExperimental/Esquematico_Circuito.md`](ParteExperimental/Esquematico_Circuito.md) (ambos tienen los prompts textuales) |

### Solicitud
1. **Programa para el Arduino Nano** que accione un driver MOSFET y capture la respuesta al escalón y a la desconexión del motor JGA25-370:
   - corriente medida con un ACS712T de 5 A, con el ADC a la frecuencia de muestreo más alta posible;
   - posición medida con el encoder;
   - datos enviados por UART;
   - código documentado, con constantes de pines y encabezado con resumen del prompt y aviso de IA.
2. **Esquemático del circuito** con el driver IRFZ44N (180 Ω de compuerta, 10 kΩ de pull-down, diodo 1N540X, motor entre el bus de 12 V y tierra), dibujado con la librería ElCompLib para Inkscape (se adjuntó como imagen). De ser posible, todos los pines en un mismo lado del Nano.
3. **Documentación** en la carpeta de uso de IA.

### Lo que hizo la IA
- **Programa** [`ParteExperimental/RespuestaEscalonMotorDC/RespuestaEscalonMotorDC.ino`](../ParteExperimental/RespuestaEscalonMotorDC/RespuestaEscalonMotorDC.ino):
  - **Muestreo:** el ADC trabaja en modo continuo por interrupción a ≈ 38 462 muestras/s.
  - **Transmisión:** el UART va a 2 Mbaud, el máximo exacto a 16 MHz, con tramas binarias de 4 bytes en tiempo real. El límite de la frecuencia de muestreo lo pone el UART, no el ADC.
  - **Encoder:** cuenta en cuadratura ×4.
  - **Pines:** todos en el lado analógico del Nano (A0 sensor, A1/A2 encoder, A3 driver), como pidió el autor.
- **Receptor** [`ParteExperimental/captura_respuesta.py`](../ParteExperimental/captura_respuesta.py): recibe los datos y los guarda en CSV. No se pidió explícitamente, pero sin él no se pueden leer los datos binarios.
- **Esquemático** [`ParteExperimental/Esquematico_MotorDC.svg`](../ParteExperimental/Esquematico_MotorDC.svg): SVG editable en Inkscape. Los símbolos se redibujaron al estilo de ElCompLib, porque solo se tenía una imagen de la librería.
- **Documentación:** dos md en `UsoIA/ParteExperimental/`, con los prompts copiados textualmente, encabezado, aviso, decisiones de diseño, observaciones del hardware y verificación. El md del programa incluye una copia del código.

### Verificación
- **Compilación:**
  - Se compiló con avr-gcc 7.3.0 y el core AVR 1.8.6 (variante del Nano), con `-Wall -Wextra` y sin advertencias.
  - Usa 5588 B de flash (17,1 %) y 493 B de RAM (24,1 %).
  - Según el ensamblador, las interrupciones caben en los 26 µs entre muestras: unos 15 µs la del ADC y unos 6 µs la del encoder, como máximo.
- **Decodificador:** se probó con 5000 tramas sintéticas, más un byte basura y una marca de pérdida. Las recuperó todas.
- **Esquemático:** el XML es válido y se revisó visualmente.

### Lo que la IA NO hizo o no pudo verificar
- **No probó nada con el hardware real.** Tampoco verificó que 2 Mbaud funcione con el adaptador USB-serie y la computadora del equipo.
- **Interpretó dos puntos que el prompt no especificaba**, que el equipo debe confirmar:
  - el diodo 1N540X como diodo de rueda libre en paralelo con el motor;
  - el ACS712T dentro del lazo de ese diodo.
- **Dejó observaciones sin cambiar el diseño del autor:**
  - el IRFZ44N no es de nivel lógico;
  - el 1N540X es de recuperación lenta;
  - A3 no tiene PWM por hardware, lo que importa para el futuro PID.
- **No hizo commit ni push.**

### Decisiones del equipo
- *(pendiente)*

---

## Entrada 7 — 22/11/2026 · Driver del motor: pin PWM, análisis y simulaciones LTspice

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic; LTspice 24.0.12 |
| **Solicitada por** | Mario Betancourt |
| **Documentación** | [`ParteExperimental/Simulaciones_Driver.md`](ParteExperimental/Simulaciones_Driver.md) (prompts textuales) · [`ReporteSimulaciones.md`](../ParteExperimental/Simulaciones/ReporteSimulaciones.md) (resultados) |

### Solicitud
1. **Pin con PWM** para la entrada del driver del motor.
2. **Evaluar una etapa con un BJT 2N3904** para llevar la compuerta del IRFZ44N a 12 V y, si era adecuada, aplicarla al esquemático.
3. **Simulaciones en GitHub:** subir las simulaciones de LTspice, creando con las hojas de datos los modelos que faltaran.
4. **Evaluar las alternativas** que propuso el autor: el driver IR2153PBF, un push-pull lineal de un proyecto anterior (IE3036) y un controlador PWM.
5. **Reporte** con las formas de onda de LTspice.
6. **Cierre:** subir todo lo pendiente a GitHub y apagar la computadora al terminar.

### Lo que hizo la IA
- **Análisis de la etapa de 12 V.**
  - **Un solo NPN:** se descartó porque enciende el motor con el pin en 0 V o flotando. Se verificó en LTspice: 2 A con el pin flotante.
  - **NPN + PNP:** se simuló como alternativa no inversora.
  - **IR2153PBF:** se descartó con su hoja de datos (oscila solo al 50 % y no tiene entrada lógica).
  - **Push-pull lineal y puentes H:** se discutieron.
- **Decisión del autor.** Con su dato de que la corriente se mantiene por debajo de 2 A, se mantuvo **el driver original (5 V directo a la compuerta)**, con la entrada en **D9** (PWM de Timer1).
- **Programa:** `PIN_DRIVER_MOTOR = 9`, con una comprobación al compilar de que el pin sea D9 o D10, y el encabezado actualizado. Compila sin advertencias (5588 B de flash y 493 B de RAM).
- **Esquemático:** la señal del driver sale de D9 por el lado digital del Nano. A3 queda libre.
- **Simulaciones** (`ParteExperimental/Simulaciones/`):
  - 11 netlists;
  - modelos de la librería de LTspice;
  - un **modelo del 1N540X creado con la hoja de Vishay** y verificado contra ella;
  - el script `correr_simulaciones.py`, que corre todo y genera 6 figuras y la tabla de mediciones;
  - el reporte con las formas de onda.
- **README y `.gitignore`:** se actualizó la estructura y se excluyeron los archivos de salida de LTspice.

### Resultados principales (motor modelado como 6 Ω y 2 mH)
- **Escalón con 5 V directo:** V<sub>DS</sub> = 0,125 V y 0,23 W en el MOSFET; apaga en 0,48 µs. Es adecuado.
- **PWM a 20 kHz al 95 %:** 1,77 W en el MOSFET con el 1N540X y 0,92 W con un Schottky. Con 490 Hz, 0,27 W. **Para el PID a 20 kHz hace falta disipador** y conviene un diodo Schottky.

### Errores de la IA corregidos en esta entrada
- **"Compuerta mal manejada".** En el chat dijo que la compuerta del diseño original estaba "mal manejada". Era una exageración: el diseño es correcto.
- **Pérdidas con PWM.** En el chat estimó "unas décimas de watt" a 20 kHz sin simular. La simulación dio entre 0,9 y 1,8 W.
- **Una medición de potencia mal definida (5,9 W falsos)** y **un netlist de capacitancia mal armado.** Las dos se corrigieron antes de publicar.
- **Pines en un mismo lado.** La recomendación de la Entrada 6 de poner todos los pines del lado analógico se revirtió en parte: el driver pasó a D9 por el PWM.

### Lo que la IA NO hizo
- **No probó nada con hardware.** La inductancia del motor y el t<sub>rr</sub> del 1N540X siguen siendo supuestos.
- **No simuló** el push-pull lineal de IE3036 ni los puentes H; solo se discutieron.

### Decisiones del equipo
- **Driver:** se mantiene el driver original (IRFZ44N, 180 Ω, 10 kΩ, 1N540X) con la entrada en D9 (decisión del autor, 22/11/2026).
- *(pendiente: driver y frecuencia de PWM para el PID)*

---

## Entrada 8 — 22/11/2026 · Referencia a Nise en el cuaderno

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |

### Solicitud
```text
Hey podrías actualizar la parte de la referencia de Nise en el cuadernillo principal
```

### Lo que hizo la IA
- **Celda 7 (Introducción):** reemplazó el texto pendiente "(AGREGAR REFERENCIA POR FAVOR, capítulo 4 no recuerdo donde estaba)" por la cita *"véase Nise [1, cap. 2, §2.8, pp. 77–83]"*, presentada como referencia del modelo **en su versión lineal**.
- **Celda 8:** reemplazó "(no sé, no sé, no sé)" por *"[1, §2.8]"* en la comparación con el modelo lineal.
- **Celda nueva al final:** agregó la sección **REFERENCIAS** con la entrada en formato IEEE: N. S. Nise, *Control Systems Engineering*, 7th ed., Wiley, 2015.
- **Historial de revisiones del cuaderno:** agregó la línea del cambio.
- **Documento de correcciones:** actualizó la fila de C-15 en el resumen de decisiones.

### Criterio
- **Qué se cita:** solo lo que el libro cubre, el modelo lineal del motor DC controlado por armadura (§2.8). No se presenta como respaldo de la fricción de Coulomb ni de los métodos numéricos (ver Entrada 4).
- **Coherencia con la revisión:** C-15 se había rechazado porque Nise "se utiliza únicamente para comparar el modelo con un modelo lineal". La cita respeta ese uso.
- **Datos verificados:** el capítulo, la sección y las páginas se tomaron del PDF de la 7.ª edición que tiene el equipo (Entrada 3).

### Lo que la IA NO hizo
- No cambió otro texto del cuaderno ni las fórmulas.
- No hizo commit ni push.

### Decisiones del equipo
- *(pendiente)*

---

## Entrada 9 — 22/11/2026 · Secciones 1.4 y 1.5 (estabilidad, Jacobiano y Lipschitz)

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Documentación** | [`redacciones/Secciones_1.4_y_1.5.md`](redacciones/Secciones_1.4_y_1.5.md) (prompts textuales y copia del texto) |

### Solicitud
```text
Ok. Quisiera que me ayudes redactando eso. Ya entiendo qué sucede. Cometí el error de utilizarlo en la deducción del método de Euler. Entiendo que lo usas en la parte de estabilidad porque f(Y)-f(y) approx J(Y-y) = Je y de ahi resulta lo que normalmente se obtiene. Aprovechando que introdujiste la condición de Lipschitz, quisiera que lo incluyas también, definiendo lo que significa que una función sea Lipschitz (que sea una transformación entre espacios métricos que no explote en el siguiente paso). Quisiera que también definas qué es el espacio métrico y su relación con funciones distancia. La parte de Lipschitz quisiera que vaya en una subsección más, la sección 1.5, dado que es un bonus que generaliza la solución de la estabilidad del método. Incluye este Prompt, corrige mi observación sobre C-01 y sube todo al repositorio
```

### Contexto
El autor había quitado el Jacobiano de su borrador de la 1.4 por ser el sistema no lineal, y preguntó por qué se descartaba $\mathbf T_k$. La IA le explicó tres cosas:
- **$\mathbf f$ y el Jacobiano tienen papeles distintos:** $\mathbf f$ se usa para calcular la solución, y el Jacobiano para analizar el error.
- **$\mathbf T_k$ no se ignora:** es una fuente de error, y no decide la estabilidad.
- **Sin derivadas, sirve la condición de Lipschitz**, y la $\tanh$ hace al modelo diferenciable.

### Lo que hizo la IA
- **Sección 1.4** del cuaderno, reescrita sobre el borrador del autor:
  - corrigió la descripción de los componentes del error y la definición de estabilidad;
  - explicó el papel del Jacobiano y por qué la estabilidad no depende de $\mathbf T_k$;
  - incluyó el criterio $|1 + h\lambda_i| \le 1$ y el Jacobiano del motor con la fricción regularizada con $\tanh$.
- **Sección 1.5 nueva (bonus):** espacio métrico y función distancia, funciones Lipschitz, relación con el Jacobiano, cota del error global de Euler, alcances y limitaciones.
- **Historial de revisiones del cuaderno:** se agregó la línea del cambio.
- **Comentario del revisor en C-01:** se corrigió, a pedido del autor, para reflejar el entendimiento actual (el error fue usar el Jacobiano en la deducción del método; el Jacobiano pertenece al análisis de estabilidad). La versión original queda en el historial de git.
- **Verificación:** las 240 expresiones LaTeX del cuaderno compilan en MathJax sin errores.

### Lo que la IA NO hizo
- **No calculó los valores propios del motor:** el autor dijo que eso lo revisaría él (C-06).
- **No modificó otras celdas del cuaderno.**
- **No cambió el comentario del revisor en C-02**, aunque contiene una imprecisión: dice que el sistema es no lineal "por los términos constantes". Los términos constantes lo hacen afín; la no linealidad viene de $\text{sign}(\omega)$. Queda para que el autor decida.

### Advertencia
La versión del cuaderno en Colab del autor tenía cambios en la 1.4 que no estaban en GitHub. El texto subido incluye ese borrador de la 1.4, pero si en Colab hay cambios en otras celdas, hay que copiarlos antes de recargar el cuaderno desde GitHub.

### Decisiones del equipo
- *(pendiente)*

---

## Entrada 10 — 22/11/2026 · Animaciones de Euler, estabilidad y Lipschitz

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Archivos** | [`Animaciones/`](../Animaciones/) (tres GIF y el script `generar_animaciones.py`) |

### Solicitud
```text
Oye, podrías generar una animación que ayude a explicar los conceptos de Euler, estabilidad y Lipschitz. Por favor coloca que tu las hiciste. ¿Puedes incluirlas como gifs en el cuadernillo?
```

### Lo que hizo la IA
- **Tres animaciones GIF** generadas con matplotlib, todas sobre el circuito eléctrico del motor ($L\,di/dt = V - R\,i$, con 12 V, 6 Ω y 2 mH):
  - `euler_paso_a_paso.gif`: el método de Euler paso a paso, con la tangente de cada paso y el error frente a la solución exacta.
  - `estabilidad_euler.gif`: el punto $h\lambda$ entra y sale del disco $|1 + h\lambda| \le 1$ al crecer $h$, junto con la solución numérica correspondiente.
  - `lipschitz_cono.gif`: el "cono" de pendiente $\pm\mathcal{L}$ recorre $\tanh(\omega/\varepsilon)$ sin salirse, y falla en el salto de $\text{sign}(\omega)$.
- **Crédito:** cada GIF lleva el texto "Animación: Claude Opus 5.5 (Anthropic)", y cada celda del cuaderno, una nota de autoría.
- **Cuaderno:**
  - se insertaron tres celdas, después de las secciones 1.1, 1.4 y 1.5;
  - los GIF se enlazan con la URL de GitHub (`raw.githubusercontent.com`), porque Colab no resuelve rutas relativas;
  - se agregó la línea al historial de revisiones.
- **Verificación:** las 263 expresiones LaTeX del cuaderno compilan en MathJax sin errores, y se revisaron cuadros de cada GIF.

### Error de la IA corregido en esta entrada
- **Caracteres de control.** Al escribir textos con barras invertidas a través de un heredoc de bash, algunos comandos LaTeX se convirtieron en caracteres de control: `\frac`, `\tau` y `\right` en una celda nueva del cuaderno, y `\tanh` y `\text` en la Entrada 9 y en `redacciones/Secciones_1.4_y_1.5.md`, ya publicados en el commit `856eaee`. Se detectó al revisar las fórmulas, se corrigió en todos los archivos y se verificó que ningún archivo de texto del repositorio tenga caracteres de control.

### Lo que la IA NO hizo
- No cambió el texto de las secciones del cuaderno.

### Advertencia
Los GIF solo se ven en Colab después de subirlos a GitHub, porque se cargan desde la URL del repositorio.

### Decisiones del equipo
- *(pendiente)*

---

## Entrada 11 — 22/11/2026 · Combinación con la versión de Colab, funciones de derivación y correcciones de la Parte 2

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Documentación** | [`correcciones/Correcciones_Parte2_2026-11-22.md`](correcciones/Correcciones_Parte2_2026-11-22.md) |

### Solicitud
```text
Sí por favor, combínalos. Por favor revisa el código de Grettel y Deyler (Import) y ayúdame a importar sus funciones a mi cuadernillo. Por ahora haz eso sólo para la parte de derivación. Quiero que en una celda coloques primero las funciones para aplicar cada uno de los métodos descritos en el documento. Revisa por favor lo nuevo que escribí en el documento y dime si debo hacer correcciones. Haz un documento de correcciones breves y preséntamelas acá para qeu yo las llene contigo
```
```text
Por favor quiero que la incorporación sea tan ordenada como sea posible. Siento que el código que me dieron está un poco desorganizado y le falta documentación. Comenta por favor.
```
```text
Hey creo qeu te faltaron las imágenes para ilustrar conceptos que te pedí ayer. Tampoco puedo ver los cambios de Lipschitz. Por favor revisa que esos cambios que te pedí aparezcan en el documento. Creo que no se finalizaron o algo así
```

### Contexto: por qué faltaban las animaciones y la sección 1.5
El autor guardó el cuaderno desde Colab tres veces (commits `1512690`, `13885a5` y `da60a24`) a partir de una copia que no tenía los cambios del commit `856eaee`: la sección 1.5, las Referencias y las citas a Nise. Esos guardados los reemplazaron en GitHub. Además, GitHub Desktop guardó en un stash los cambios de la IA que todavía no tenían commit (las animaciones y la Entrada 10). No se perdió nada: todo se recuperó del stash y del historial.

### Lo que hizo la IA
- **Combinación del cuaderno**, por celda y por id de Colab, con la versión del autor (`da60a24`) como base:
  - **Se conservaron sin cambios** todas las celdas del autor, salvo las cinco previstas, y su orden.
  - **Se restauraron:**
    - las citas a Nise (celdas 7 y 8);
    - la sección 1.5;
    - las tres animaciones (después de 1.1, 1.4 y 1.5);
    - la sección de Referencias (al final);
    - las líneas del historial de revisiones.
  - **En la 1.4** se mantuvo la celda del autor y se completó la segunda con los componentes del error corregidos, la definición de estabilidad y la continuación (Jacobiano, $\mathbf T_k$, criterio, $\tanh$). El párrafo del autor "Para ser completamente honestos…" se conservó palabra por palabra, incluida la frase sin terminar.
- **Funciones de derivación** (sección 2.3.4, en la celda de código vacía que dejó el autor):
  - **Origen:** se importaron de la celda 14 del cuaderno de Grettel y Deyler: `d_adelante_k`, `d_atras_k`, `d_centrada_k`, `d_richardson` y `derivada_sin_bordes`.
  - **Mejoras:** docstrings, comentarios, validación de entradas y una tabla de métodos corregida (la centrada es $O(h^2)$ solo con paso uniforme).
  - **Verificación:** se agregó una celda que prueba las funciones con $\sin x$.
- **Revisión del texto nuevo del autor:** 17 correcciones breves en `correcciones/Correcciones_Parte2_2026-11-22.md`. Entre ellas, dos errores de contenido:
  - la fórmula $N = n_F/2$, que debe ser $N = 2\,n_F$;
  - el pseudocódigo, que no actualiza `A_prev` y obtiene el sentido de giro de la velocidad, que es lo que se quiere calcular.

  También se respondió la nota de Grettel sobre diferenciabilidad y analiticidad.

### Verificación
- **Celdas del autor:** solo cambiaron las cinco previstas, y se conservó su orden.
- **Código:** las dos celdas de código corren sin errores. Los órdenes observados son 1,00; 1,00; 2,00 y 4,00. Con paso no uniforme, la centrada baja a orden 1.
- **LaTeX:** las 317 expresiones del cuaderno compilan en MathJax sin errores.
- **Caracteres de control:** ningún archivo de texto del repositorio los tiene.

### Lo que la IA NO hizo
- **No aplicó las 17 correcciones** de la Parte 2: el revisor las va a decidir.
- **No importó otras partes** del cuaderno de Grettel y Deyler (integración, simulación, gemelo digital).
- **No borró el stash de GitHub Desktop** (`stash@{0}`). Se puede borrar después de confirmar que todo está en GitHub.

### Recomendación de flujo
Después de cada push de la IA, abrir el cuaderno en Colab desde GitHub antes de seguir editando. Guardar una copia vieja desde Colab reemplaza los cambios que no tenga.

### Decisiones del equipo
- *(pendiente: decisiones de C2-01 a C2-17)*

---

## Entrada 12 — 22/11/2026 · Driver L298N, captura de datos brutos, PID y aplicación del gemelo digital

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Documentación** | [`ParteExperimental/Programa_L298N.md`](ParteExperimental/Programa_L298N.md) · [`ParteExperimental/Controlador_PID.md`](ParteExperimental/Controlador_PID.md) (ambos tienen los prompts textuales) |

### Solicitud
1. **Programa del Arduino para el L298N** (ENB en D3, IN3 en D4, IN4 en D5, ACS712-5 en A0, encoder en D8 y D9):
   - enviar los datos brutos de las fases del encoder y del sensor de corriente, a la frecuencia más alta posible;
   - un receptor de Python que los guarde;
   - otro script que calcule la posición, la velocidad y la corriente;
   - decir qué hace falta para que funcione.
2. **PID en el Arduino**, con memoria y modos de velocidad y de posición, y una **aplicación de Python** con:
   - customtkinter, estilo oscuro y varias páginas;
   - perillas para sintonizar el PID;
   - botones de escalón, desconexión, seguimiento de un movimiento y captura de datos;
   - las funciones del receptor anterior;
   - una animación del motor en pixel art, con fuente pixelada;
   - gráficas animadas con un cursor que avanza en el tiempo.
3. Un md con el prompt textual del PID, que diga que la documentación está pendiente.
4. Un manual de uso de la interfaz, con énfasis en cómo capturar datos (prompt textual en `Controlador_PID.md`).

### Lo que hizo la IA
- **Firmware** [`MotorDC_L298N.ino`](../ParteExperimental/MotorDC_L298N/MotorDC_L298N.ino). Antes era `RespuestaEscalonMotorDC.ino`; se renombró con `git mv`.
  - **Captura rápida:** ≈ 76 923 muestras/s con tramas de 2 bytes de datos brutos (ADC, A, B). El límite lo pone el UART a 2 Mbaud.
  - **Modo de tiempo real:** encoder ×4 por interrupción, periodo Ts con el Timer1, PID, generador de referencia y telemetría de 27 bytes.
  - **Órdenes de texto** para configurar todo desde la computadora.
- **Python** en `ParteExperimental/`:
  - `protocolo_motor.py` (protocolo compartido);
  - `captura_respuesta.py` (receptor; guarda `.bin`, `_crudo.csv` y `.json`);
  - `postprocesamiento.py` (θ, ω por dos métodos, e i);
  - `modelo_motor.py` (modelo del cuaderno con Euler y RK4);
  - `arduino_simulado.py` (imita al firmware byte a byte para probar sin hardware).
- **Aplicación** [`GemeloDigital/app.py`](../ParteExperimental/GemeloDigital/app.py), con seis páginas:
  - conexión;
  - tablero (gemelo en tiempo real);
  - control PID;
  - ensayos;
  - captura;
  - modelo.
- **Manual** [`GemeloDigital/MANUAL.md`](../ParteExperimental/GemeloDigital/MANUAL.md): conexión, configuración, las tres formas de capturar datos (con los archivos y columnas que se guardan), cada página y problemas comunes.
- **PID:** se implementó $u = K_p e + K_i T_s E + (K_d/T_s)\Delta e$ como forma por defecto. La forma literal del prompt ($K_i/T_s$, $K_d T_s$) quedó disponible con un interruptor. Ver la sección «Diferencia con la fórmula del prompt» de `Controlador_PID.md`.

### Verificación
- **Compilación:**
  - avr-gcc 7.3.0, core AVR 1.8.6, con `-Wall -Wextra` y sin advertencias.
  - 13 056 B de flash (39,8 %) y 692 B de RAM (33,8 %).
- **Margen de tiempo:**
  - La interrupción del ADC usa unos 114 de los 208 ciclos entre muestras (revisado en el ensamblador).
  - Una simulación ciclo a ciclo del UART no muestra pérdidas.
- **Decodificador y postprocesamiento** con datos sintéticos:
  - recuperan exactamente las cuentas;
  - se resincronizan tras perder un byte;
  - la velocidad por flancos tiene un error medio de 0,37 %.
- **Aplicación con el Arduino simulado:**
  - el PID de velocidad sigue una onda cuadrada;
  - el escalón y el seguimiento de una senoidal de posición se guardan y se reproducen;
  - no hubo excepciones.
  - Se perfiló y se optimizó el dibujo para que la interfaz no se atrase.

### Lo que la IA NO hizo o no pudo verificar
- **No probó nada con el hardware real.** Tampoco verificó 2 Mbaud con el adaptador del equipo.
- **No sintonizó el PID del motor real.** Las ganancias iniciales son de prueba.
- **No identificó los parámetros del modelo.** Son de ejemplo, salvo R = 6 Ω; L = 2 mH es supuesto.
- **No actualizó el esquemático** `Esquematico_MotorDC.svg` ni las simulaciones LTspice. Corresponden al driver MOSFET anterior.
- **No incluyó los archivos de fuentes pixeladas** (hay que descargarlos; ver `GemeloDigital/fuentes/LEEME.md`).
- **No escribió la documentación completa del PID.** El autor pidió dejarla pendiente.
- **No hizo commit ni push.**

### Decisiones del equipo
- 22/11/2026: el autor pidió corregir el PID. Queda solo la forma $u = K_p e + K_i T_s E + (K_d/T_s)\Delta e$, con $E_k = E_{k-1} + e_k$ (ver Entrada 13).

---

## Entrada 13 — 22/11/2026 · PID corregido, esquemático con L298N y retiro de las simulaciones

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Documentación** | [`ParteExperimental/Controlador_PID.md`](ParteExperimental/Controlador_PID.md) · [`ParteExperimental/Esquematico_Circuito.md`](ParteExperimental/Esquematico_Circuito.md) · [`ParteExperimental/Simulaciones_Driver.md`](ParteExperimental/Simulaciones_Driver.md) |

### Solicitud
```text
Corrige el PID, y los esquemáticos. Ya no necesito simulaciones (quítalas)
```

### Lo que hizo la IA
- **PID:** se dejó solo la forma $u_k = K_p e_k + K_i T_s E_k + (K_d/T_s)(e_k - e_{k-1})$, con $E_k = E_{k-1} + e_k$. Se quitó la forma del prompt ($K_i/T_s$, $K_d T_s$) de:
  - el firmware (constante `FORMA_DEL_PROMPT` y orden `Q`);
  - la aplicación (interruptor);
  - el Arduino simulado;
  - el manual.
- **Esquemático** [`Esquematico_MotorDC.svg`](../ParteExperimental/Esquematico_MotorDC.svg), redibujado para el L298N con los pines del programa:
  - ENB en D3, IN3 en D4 e IN4 en D5;
  - el ACS712-5 en serie con el motor (OUT3 → IP+ → IP− → M1+) y su salida en A0;
  - el encoder en D8 y D9;
  - la fuente de 12 V en el módulo y la tierra común.

  Se mantuvo el estilo ElCompLib y se usaron etiquetas de red para evitar cruces. El md del esquemático conserva los prompts de la versión 1.
- **Simulaciones:** se borró `ParteExperimental/Simulaciones/`: netlists, modelos, script, figuras, reporte y las salidas de LTspice no versionadas. También se quitaron las reglas de LTspice del `.gitignore` y la carpeta del README. `Simulaciones_Driver.md` y las Entradas 7 y 6 se conservan como registro, con una nota.

### Verificación
- **Firmware:** compila sin advertencias. Usa 12 926 B de flash (39,4 %) y 691 B de RAM (33,7 %).
- **Arduino simulado:**
  - la orden `Q` ahora responde `# ERR`;
  - el PID de velocidad llega a 300,05 rad/s con referencia 300;
  - el de posición llega a 9,996 rad con referencia 10.
- **Aplicación:** recorre las seis páginas, el escalón y el seguimiento sin errores.
- **Esquemático:** revisado visualmente en el navegador.

### Lo que la IA NO hizo
- **No quitó el Arduino simulado** (`arduino_simulado.py`). Es parte de la aplicación y no es una simulación de LTspice.
- **No probó el circuito ni el PID con el hardware real.**
- **No hizo push** en ese momento. Después, a pedido del autor, la rama se subió y se unió a `main` (ver la Entrada 14).

### Decisiones del equipo
- *(pendiente)*

---

## Entrada 14 — 22/11/2026 · Merge a main, librerías y primer error de montaje

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Documentación** | [`ParteExperimental/GemeloDigital/MANUAL.md`](../ParteExperimental/GemeloDigital/MANUAL.md) (secciones 1 y 9) · [`ParteExperimental/Esquematico_Circuito.md`](ParteExperimental/Esquematico_Circuito.md) |

### Solicitud
```text
haz merge con main
```
```text
puedes descargar las librerias en mni python 3.12
```
```text
Puedes documentar eso. Conecté por accidente VIn a GND
```

### Lo que hizo la IA
- **Git:**
  - subió la rama `l298n-pid-gemelo-digital`;
  - unió la rama a `main` (avance directo, sin conflictos) y subió `main`, con lo que el PR #1 quedó como *Merged*.
- **Python 3.12:** instaló las librerías de `GemeloDigital/requirements.txt`.
- **Montaje:** ayudó a diagnosticar el primer montaje. El L298N se calentaba sin que el motor girara, y el LED del ACS712 no encendía. El autor encontró la causa del LED: un cable de GND conectado por error a VIN.
- **Documentación** del error:
  - en el manual, en la lista de revisión (sección 1) y en problemas comunes (sección 9), junto con la revisión paso a paso de cada pieza;
  - en el md del esquemático.

### Verificación
- **Aplicación:** con Python 3.12 (numpy 2.5, matplotlib 3.11, Pillow 13) recorre todas las páginas sin errores, con el Arduino simulado.

### Lo que la IA NO pudo verificar
- **Calentamiento del L298N:** no se confirmó que viniera de la misma causa que el LED apagado.
- **Daños:** tampoco se confirmó si el error dañó alguna pieza.
- **Hardware:** el circuito y el PID siguen sin probarse con el hardware real.

### Decisiones del equipo
- *(pendiente)*

---

## Entrada 15 — 22/11/2026 · Órdenes dañadas en el puerto serie y diagnóstico de la «lógica invertida»

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |
| **Documentación** | [`ParteExperimental/GemeloDigital/MANUAL.md`](../ParteExperimental/GemeloDigital/MANUAL.md) (secciones 2 y 9) · sección 8 de [`MotorDC_L298N.ino`](../ParteExperimental/MotorDC_L298N/MotorDC_L298N.ino) |

### Solicitud
```text
Mira ya tengo el motor conectado pero por alguna razón hay como una lógica invertida. Si le doy arrancar se detiene y si le doy detener arranca. Tampoco sigue ninguna de las funciones de referencia del PID. Podrías revisarlo?
```
```text
Quieres jugar con la conexión física. Te doy permiso de usar la app
```
```text
Yo pienso que hay un cuello de botella por la comunicación o algo así. Ya desconecté COM7 en teoría. La lógica está invertida. Intenta conectarte y arreglar las cosas
```

### Lo que hizo la IA
- **Análisis de las capturas reales del equipo** (`ParteExperimental/datos/`, 18:02 a 18:12):
  - durante el escalón el encoder no contó nada, aunque la corriente subía;
  - en la fase previa el motor venía girando y se frenaba solo.
- **Prueba por el puerto serie** con el Arduino del equipo (COM7), con permiso del autor: lazo abierto, máximo 6 V, siempre terminando en reposo.
- **Problema de comunicación encontrado:**
  - el Arduino recibió `P 44 12` como `P 44 2`, porque a 2 Mbaud se pierde un byte si llega mientras se atiende otra interrupción;
  - **corrección:** las órdenes llevan una suma de verificación (`*HH`);
  - el firmware rechaza las dañadas (`# ERR SUMA`);
  - `protocolo_motor.EnlaceSerie.enviar_confirmado()` reenvía hasta recibir `# OK`;
  - la aplicación, el receptor y el Arduino simulado usan este mecanismo, y la app muestra el contador **REENVIOS**.
- **Firmware:** se cargó el nuevo en el Nano con avrdude (13 664 B, verificado).
- **Diagnóstico de la «lógica invertida»:**
  - con las órdenes ya correctas, en reposo (ENB, IN3 e IN4 en 0) el motor giraba a ~590 rad/s sin corriente por el ACS712;
  - con el driver encendido, el motor quedaba quieto y la corriente sí pasaba por el sensor;
  - el programa manda los estados correctos (lo confirma la telemetría), así que la causa es el **cableado**: el motor recibe energía por otro camino.
- **Documentación** en el manual: el contador REENVIOS y dos filas nuevas en problemas comunes.

### Verificación
- **Firmware:** compila sin advertencias (13 664 B de flash, 41,7 %).
- **Prueba con el Arduino real:** las 5 órdenes de configuración se confirmaron y hubo 7 reenvíos en total.
- **Arduino simulado:**
  - una orden dañada a propósito se rechaza;
  - la app recorre todas sus páginas sin errores;
  - el receptor recibe una captura completa sin pérdidas.

### Lo que la IA NO pudo hacer o verificar
- **No vio el cableado**, así que no sabe cuál conexión exacta está mal. Dejó la lista de revisión en el manual.
- **El cero del ACS712** sigue en ~645 cuentas, en vez de cerca de 512. Puede ser una tierra mal conectada o un daño del sensor por el error de cableado anterior; no está confirmado.
- **No hizo commit.**

### Decisiones del equipo
- *(pendiente)*

---

## Entrada 16 — 22/11/2026 · Ensayos reales del tema 4, 1 Mbaud, signo del encoder y sintonía del PID

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic (incluye búsqueda web) |
| **Solicitada por** | Mario Betancourt |
| **Documentación** | [`ParteExperimental/datos/tema4_20261122/LEEME.md`](../ParteExperimental/datos/tema4_20261122/LEEME.md) |

### Solicitud
```text
Listo. Fue problema de tierras. Podrías lograr que siga una referencia. Que el PID funcione. Hay algunos casos donde el modo de ensayos produce saltos de encoder inválidos. Podrías buscar en internet información sobre cuántos polos magnéticos hay en la rueda del encoder y la escala de corriente del sensor de corriente
```
```text
Podrías hacer una grabación para que pueda pasársela a mis compañeros. Ya me desconecté del puerto COM. No tienes que simular. Puede sutilizar la aplicación. Ya corroboré que las corrientes son seguras. Puedes realizar los experimentos que pide la guía del proyecto para capturar los datos por favor. Nosotros escogimos el tema 4. Quiero que me indiques el archivo donde se guarde la captura. Por favor corrobora que todo funcione bien. Quiero que también hagas que el PID funcione adecuadamente. Vuele
```
```text
Hey pero el motor parece estar girando en una sola dirección en estos ensayos. Sí se nota el cambio de velocidad. pero el giro no se invierte
```

### Lo que hizo la IA
- **Saltos inválidos del encoder:**
  - Coincidían con tramas perdidas en la computadora; el Arduino reportó 0 pérdidas.
  - Se pasó a **1 Mbaud** (38 461 muestras/s). Antes, a 2 Mbaud, se perdían de 100 a 730 tramas por captura.
  - `postprocesamiento.py` corrige cada salto como ±2 en el sentido del movimiento.
  - La app deja de dibujar durante la captura.
  - Siguen perdiéndose algunas tramas en ~1 de cada 3 capturas; está documentado.
- **Retraso de la app:**
  - El driver FTDI retenía los datos hasta ~0,3 s con la telemetría a 500 Hz.
  - Corrección: la telemetría se limita a una trama cada ~10 ms y las confirmaciones esperan hasta 0,5 s por intento.
- **PID:**
  - El encoder del montaje cuenta al revés respecto del voltaje, y eso hacía que el PID se realimentara al revés.
  - Se agregó la orden `I` (invertir el signo) y el interruptor «INVERTIR ENCODER».
- **Ensayos reales** (con permiso del autor, que confirmó que las corrientes eran seguras):
  - (a) escalones a 5 niveles y (b) desaceleración libre y con freno, con `ensayos_tema4.py`;
  - PID de velocidad y de posición con `prueba_pid.py`;
  - sintonía en el motor real;
  - figuras con `figuras_tema4.py` y un LEEME con los resultados.
- **Aplicación:** ganancias por modo, valores por defecto sintonizados, apertura de las pruebas del PID (con el gemelo simulado) y listado de las subcarpetas.
- **Búsqueda web:**
  - Pulsos por vuelta del encoder: 11 (Abra Electronics).
  - Polos del disco: 22 según la tabla de CHIHAI; no es la hoja de datos de este motor.
  - Escala del ACS712-05B: 185 mV/A (Allegro).

### Verificación
- **Firmware:** compila y quedó cargado en el Nano (13 848 B).
- **Captura a 1 Mbaud:** dos capturas de prueba completas, sin saltos.
- **PID de velocidad** (200 ↔ 400 rad/s): 6,5 % de sobreimpulso, 0,19 s de establecimiento.
- **PID de posición** (±1 vuelta): 1,8 % de sobreimpulso, 66 ms de establecimiento. En el seguimiento de ±5 vueltas, error RMS de 0,33 rad.
- **Inversión de giro:** confirmada con los datos (−12 a +12 V, ±300 rad/s).
- **Aplicación:** abre los archivos reales y recorre todas las páginas sin errores.

### Lo que la IA NO hizo o no pudo verificar
- **No hizo la prueba (c) con carga inercial:** requiere montar el disco.
- **No midió** la resistencia del devanado ni el voltaje en los bornes.
- **No confirmó** los pulsos por vuelta ni la reducción de este motor.
- **No ajustó** los parámetros del modelo: es trabajo del equipo.
- **No hizo commit.**

### Decisiones del equipo
- *(pendiente)*

---

## Entrada 17 — 22/11/2026 · Ensayos sin carga, integración del cuadernillo y secciones nuevas

| Campo | Detalle |
|-------|---------|
| **Herramienta** | Claude Code (app de escritorio), modelo Claude Opus 5.5 de Anthropic |
| **Solicitada por** | Mario Betancourt |

### Solicitud
- **Ensayos:** repetir la secuencia de ensayos sin carga (las mediciones anteriores eran con un cilindro de PVC).
- **Cuadernillo:** integrar el cuadernillo de Grettel y Deyler (`Import/GrettelDeyler2`) y rehacer el análisis con y sin cilindro.
- **Secciones y gráficas:**
  - objetivos y conclusiones;
  - Heun, RK2 y RK4 en la Parte 1;
  - métodos propios contra la medición;
  - Euler con el campo vectorial variando h;
  - error de derivación contra h;
  - Richardson contra conteo en ventana;
  - tabla de integrales;
  - PID real con las constantes y el diagrama de bloques.

### Lo que hizo la IA
- **Ensayos sin carga** con el motor real: `ParteExperimental/datos/tema4_sin_carga_20261122/` (escalones a 5 niveles, desaceleración libre y con freno). Las 4 pruebas del PID sin carga **no se pudieron hacer**: el puerto estaba ocupado por la app.
- **Excel** `mediciones_motor_dc.xlsx` (en la raíz):
  - pruebas SC (sin carga, hoy) y CC (cilindro de PVC, antes), remuestreadas a ~2 kHz;
  - se conservaron los parámetros que llenó el equipo (R = 6,4 Ω y el cilindro);
  - R, los pulsos por vuelta y J se escribieron como valores, porque Python no lee fórmulas sin calcular.
- **Cuadernillo:**
  - base: el de Grettel y Deyler, más el enlace de Colab;
  - se corrigieron dos funciones para los datos reales: `validar_tests` (aceptaba ningún retroceso del encoder) y `regimen_estacionario` (tomaba el final de la prueba, que es la fase libre);
  - se agregaron 18 celdas: objetivos, 1.3, 2.7, 2.8, 3.6.1, 4.1.1, 4.4, 5.2, 5.2.1 y conclusiones.
- **Ejecución:** el cuadernillo se ejecutó completo con nbconvert, con 0 errores.

### Verificación
- **Consistencia de los métodos:** Euler, Heun, RK2 y RK4 coinciden entre sí (diferencia máxima de 1,7 rad/s), pero difieren de la medición (RMSE de ≈ 97 rad/s). La discrepancia es del modelo o de los parámetros (voltaje real no proporcional al PWM), no del método.
- **Estabilidad de Euler:** paso crítico de 0,64 ms con los parámetros estimados.

### Lo que la IA NO hizo o no pudo verificar
- **Conclusiones y textos nuevos:** son borradores generados por la IA; el equipo debe revisarlos y poder explicarlos.
- **Inercia del cilindro:** no se confirmó la reducción de la caja. El efecto casi nulo del cilindro se explica como una hipótesis (inercia reflejada entre N²).
- **Informe IEEE y video:** no se hicieron.
- **No hizo commit.**

---

## Plantilla para nuevas entradas

```markdown
## Entrada N — DD/MM/AAAA

| Campo | Detalle |
|-------|---------|
| **Herramienta** | |
| **Solicitada por** | |
| **Versión revisada** | |

### Solicitud
### Lo que hizo la IA
### Lo que la IA NO hizo
### Decisiones del equipo
```
