# Controlador PID y aplicación del gemelo digital

| Campo | Detalle |
|-------|---------|
| **Título** | Controlador PID en el Arduino y aplicación de escritorio del gemelo digital |
| **Fecha de creación** | 22/11/2026 |
| **Autores** | Mario Alejandro Betancourt Franco (23440) · Claude Opus 5.5 (Anthropic), asistente de IA |
| **Archivos** | [`MotorDC_L298N.ino`](../../ParteExperimental/MotorDC_L298N/MotorDC_L298N.ino) (sección 7) · [`GemeloDigital/`](../../ParteExperimental/GemeloDigital/) · [`modelo_motor.py`](../../ParteExperimental/modelo_motor.py) · [`arduino_simulado.py`](../../ParteExperimental/arduino_simulado.py) |
| **Antecedente** | [`Programa_L298N.md`](Programa_L298N.md) |
| **Bitácora** | [`BitacoraUsoIA.md`](../BitacoraUsoIA.md), Entrada 12 |

---

> [!IMPORTANT]
> **Documentación pendiente.** Este documento solo registra el prompt y resume cómo se implementó
> el PID. La documentación completa de esta parte (análisis, sintonización, resultados con el
> hardware real) está **pendiente**.

> [!WARNING]
> **Aviso sobre el uso de IA.** El código lo generó Claude Opus 5.5 (Anthropic) a pedido del autor.
> Se compiló para el Arduino Nano y se probó con un Arduino simulado en Python, **no con el motor
> real**. La responsabilidad sobre su uso y sobre los resultados es del equipo.

---

## Prompt original

Copiado textualmente, como lo escribió el autor.

```text
Quiero que también hagas una APP con Python que me permita ver las gráficas en tiempo real de los datos que te pido, básicamente un gemelo digital. También quiero que implementes un controlador PID en el Arduino de la siguiente forma.

* Durante cada iteración del PID
* kp * ek
* ki /Ts * E_k
* kd*Ts * (e_k-e_k_1)

Donde E_k es el error acumulado. E_k = E_k - 1
y e_k_1 es el error en el paso anterior. El PID tendrá memoria. Quiero que en la GUI hagas un menú para tunear el PID usando una especie de perillas. También quiero que coloques botones para probar la respuesta al escalón, a la desconexión y para seguir un movimiento particular. Quiero que hagas modos de PID para control de velocidad y control de posición. Quiero que coloques botones para capturar datos. 

La interfaz gráfica debe tener un estilo oscuro.

Puedes utilizar customtkinter

Me gustaría que la app tenga múltiples ventanas hijas (o Frames distintos) donde pueda ver las distintas partes del proyecto. Quiero que tenga las funcionalidades del código receptor que hiciimos antes. Quisiera que hagas una animación del motor moviéndose mientras se muestran las gráficas. Hazla con el estilo pixel art de los videos que generan contigo en Instagram sobre ciencia y así. Que esto aplique también para la fuente. Las gráficas deben verse animadas, con un cursor moviéndose en el tiempo.

Por favor coloca este prompt tal cual en un md donde describas cómo hicimos el PID. Pon que la documentación de esta parte estará pendiente.
```

## Cómo se implementó el PID

En cada periodo de muestreo $T_s$ (lo marca el Timer1 del Nano), el Arduino:

1. **Mide la posición:** lee la cuenta del encoder. En tiempo real el encoder se cuenta ×4 con la interrupción por cambio de pin, con la misma tabla de cuadratura que usa Python.
2. **Estima la velocidad:** diferencia hacia atrás de la posición, suavizada con un filtro de primer orden de constante $\tau$ (perilla FILTRO).
3. **Calcula la referencia** $r_k$: constante, seno, cuadrada o triangular.
4. **Calcula el error y su memoria:**

$$
e_k = r_k - y_k, \qquad E_k = E_{k-1} + e_k
$$

   La medición $y_k$ es la velocidad (modo velocidad) o la posición (modo posición). El prompt escribe «E_k = E_k - 1»; se interpretó como $E_k = E_{k-1} + e_k$, el error acumulado. **El equipo debe confirmarlo.**

5. **Calcula el voltaje y lo aplica** con el PWM de ENB, saturado a $\pm V_{bus}$:

$$
u_k = K_p\,e_k + K_i\,T_s\,E_k + \frac{K_d}{T_s}\,(e_k - e_{k-1})
$$

6. **Guarda** $e_k$ como $e_{k-1}$ del siguiente periodo y envía una trama de telemetría.

### Diferencia con la fórmula del prompt (para que el equipo decida)

El prompt pide $\dfrac{K_i}{T_s}E_k$ y $K_d\,T_s\,(e_k - e_{k-1})$. La IA dejó como **forma por defecto** la de arriba, $K_i T_s E_k$ y $\dfrac{K_d}{T_s}(e_k - e_{k-1})$, por esta razón:

- $T_s E_k = T_s\sum e_j$ es la suma de rectángulos que aproxima $\int e\,dt$.
- $(e_k - e_{k-1})/T_s$ es la diferencia hacia atrás que aproxima $de/dt$.

Con la forma del prompt, $K_i$ y $K_d$ quedan multiplicados por $1/T_s^2$ y por $T_s^2$ respecto de las ganancias continuas, y cambiar $T_s$ cambiaría el controlador.

**La forma del prompt está implementada:** se activa con el interruptor «FORMA DEL PROMPT» de la página CONTROL PID (orden `Q 1`), o con la constante `FORMA_DEL_PROMPT = true` del .ino. La decisión es del equipo.

### Agregados que el prompt no pidió

Se pueden quitar o desactivar.

- **Anti-windup por integración condicional:** si $u$ se satura y el error lo empujaría más allá del límite, $E_k$ no cambia en ese periodo. Interruptor «ANTI-WINDUP» (orden `A 0` para desactivarlo).
- **Memoria en cero al cambiar de modo, de $T_s$ o de forma:** $E_k$ y $e_{k-1}$ vuelven a cero.
- **Seguridad:** si la aplicación deja de enviar el latido `H` durante 2 s, el motor pasa a reposo.
- **Modo lazo abierto:** la referencia es directamente el voltaje. Sirve para probar el driver sin el PID.

## La aplicación (resumen)

[`ParteExperimental/GemeloDigital/app.py`](../../ParteExperimental/GemeloDigital/app.py), con customtkinter y estilo oscuro de pixel art. Tiene seis páginas:

| Página | Contenido |
|--------|-----------|
| CONEXIÓN | Puerto serie o **Arduino simulado**, datos del hardware (PPR, N, Vref, sensibilidad, cero del sensor) y consola de órdenes. |
| TABLERO | Gemelo digital en tiempo real. Animación pixelada del L298N, el ACS712, el motor, el encoder y la caja. Gráficas de barrido con cursor (θ, ω, i, u): medición, referencia y modelo. |
| CONTROL PID | Modos lazo abierto, velocidad y posición. Perillas para Kp, Ki, Kd, Ts, el filtro y la referencia (amplitud, desfase y frecuencia). |
| ENSAYOS | Botones de escalón, desconexión y «seguir movimiento». Reproducción animada con cursor, comparación con el gemelo y resumen. |
| CAPTURA | Grabar la telemetría y lista de archivos guardados. |
| MODELO | Parámetros del modelo, Euler o RK4, paso h, límite de estabilidad de Euler y simulación. |

La fuente pixelada de la interfaz se carga si se copian los `.ttf` en `GemeloDigital/fuentes/` (ver el LEEME de esa carpeta). La animación usa siempre su propia fuente de 5×7 píxeles.

**Manual de uso:** [`GemeloDigital/MANUAL.md`](../../ParteExperimental/GemeloDigital/MANUAL.md). Se pidió con este prompt (copiado textualmente):

```text
Por favor haz un manual describiendo cómo utilizar la interfaz. Sé que está bonita pero tiene un montón de cosas JAJAJA. Es muy importante que describas qué  debo hacer para capturar datos
```

## Pendiente

- **Documentación completa de esta parte.**
- **Pruebas con el hardware real** y sintonización de las ganancias.
- **Decisión del equipo** sobre la forma del PID (estándar o la del prompt) y sobre $E_k = E_{k-1} + e_k$.
- **Parámetros del modelo:** los de `modelo_motor.py` son de ejemplo (solo R = 6 Ω viene del autor, y L = 2 mH es supuesto). Hay que identificarlos con los ensayos.
