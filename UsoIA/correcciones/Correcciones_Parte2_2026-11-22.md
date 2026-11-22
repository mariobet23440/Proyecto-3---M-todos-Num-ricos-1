# Correcciones breves: texto nuevo de las secciones 1.3, 1.4 y Parte 2

| Campo | Detalle |
|-------|---------|
| **Documento revisado** | `Proyecto3MetodosNumericos.ipynb`, versión de Colab del autor (commit `da60a24`, 22/11/2026 14:57) |
| **Elaborado con** | Claude Opus 5.5 (Anthropic), a pedido de Mario Betancourt. Ver [`BitacoraUsoIA.md`](../BitacoraUsoIA.md), Entrada 11 |
| **Revisor** | Mario Alejandro Betancourt Franco (23440) |

> [!WARNING]
> Son **propuestas**. Se aplican al cuaderno solo las que el revisor apruebe. La IA puede equivocarse.

Gravedad: 🔴 error de contenido · 🟠 precisión o algo incompleto · 🟡 ortografía o redacción.

| ID | Dónde | Qué cambiar | Propuesta | Decisión del revisor |
|----|-------|-------------|-----------|----------------------|
| C2-01 🟡 | 1.3, primer párrafo | "de que en nuestro sistema de ecuaciones: tenemos" | "de que, en nuestro sistema de ecuaciones, tengamos al menos una ecuación…" | |
| C2-02 🟠 | 1.4, párrafo "Para ser completamente honestos…" | La frase queda cortada: "esta sugirió que la \*\*\*\*" | Completar. Por ejemplo: "…sugirió separar los papeles: el método se escribe con el campo vectorial $\mathbf f$, y el Jacobiano aparece solo al analizar cómo se propaga el error. Para el caso no lineal sin derivadas, se usa la condición de Lipschitz (sección 1.5)". Citar como "Claude (Anthropic, 2026)" y remitir a la bitácora | |
| C2-03 🟠 | Parte 2, introducción | "permite medir en tiempo real la velocidad angular": el encoder mide **posición** (cuenta flancos); la velocidad se obtiene **derivando** | "permite medir la posición angular del eje (…). La velocidad angular se obtiene derivando numéricamente esa posición, que es el tema de esta parte" | |
| C2-04 🟡 | 2.1 | "alterantes"; "En otros tipos encoders"; "un canal de índice de número Z"; "posición angular el tiempo real" | "alternantes"; "En otros tipos de encoders"; "un canal de índice (canal Z)"; "en tiempo real" | |
| C2-05 🟡 | 2.1, cálculo de $N$ | "Suponga que los sensores contienen $N$ imanes": los imanes están en la rueda | "Suponga que la rueda contiene $N$ imanes (polos)…" | |
| C2-06 🔴 | 2.1, fórmula de $N$ | $N = n_F/2$ está invertida. Con $N$ polos alternos, un canal está en alto durante los $N/2$ sectores de una polaridad, así que hay $N/2$ flancos positivos por vuelta: $n_F = N/2$ | $N = 2\,n_F$. Si se cuentan los flancos de ambos tipos, $N = n_{\text{flancos}}$, que es lo que dice el párrafo anterior. Por ejemplo, si el fabricante indica 11 pulsos por vuelta en un canal, $n_F = 11$ y $N = 22$ | |
| C2-07 🔴 | 2.2, pseudocódigo | `A_prev` nunca se inicializa ni se actualiza. El sentido se toma de `SIGN(omega)`, que es justo lo que se quiere calcular (razonamiento circular) | Inicializar `A_prev = READ(PIN_A)` antes del ciclo y actualizarlo al final. El sentido sale de la cuadratura: en un flanco de A, si $B \neq A$ se suma 1 y si $B = A$ se resta 1 (o al revés, según el cableado). El programa del Arduino ya lo hace con interrupciones en ambos canales, con resolución $\pi/N$ | |
| C2-08 🟠 | 2.2, condición de viabilidad | Compara constantes de tiempo mecánicas y eléctricas, pero eso no decide la viabilidad | "…siempre y cuando el microcontrolador lea el pin más rápido de lo que ocurren los flancos a la velocidad máxima del motor. Con interrupciones, como en el programa del Arduino, no hace falta leer el pin continuamente" | |
| C2-09 🟡 | 2.2 | "siempre y cuándo"; "del sistemas on"; "constantes de tiempo característicos"; "más alla" | "siempre y cuando"; "del sistema son"; "características"; "más allá" | |
| C2-10 🟠 | 2.2, cuantización | "fuerza a no tratar a la velocidad angular como continua": lo cuantizado es la **posición** | La velocidad estimada hereda un error de cuantización del orden de $\Delta\theta/(k\,h)$, que **crece** al reducir el paso. Eso compite con el error de truncamiento, que crece con $k\,h$, y obliga a elegir la ventana $k$. Es lo que muestra el experimento de Grettel y Deyler | |
| C2-11 🟠 | 2.3.1 | "Hacia atras". "Centradas (…) es más preferido": tiene tres salvedades | "atrás". La centrada es $O(h^2)$ solo con paso uniforme, no es causal (no sirve en tiempo real para el PID) y, con posición cuantizada, un $h$ más pequeño no siempre reduce el error | |
| C2-12 🔴 | 2.3.2, Richardson | "se elimine al hacer la suma $\Phi(h) + \Phi(h/2)$": no es una suma. También dice "cálulo" | "…al hacer la combinación $\frac{4}{3}\Phi(h/2) - \frac{1}{3}\Phi(h)$"; "cálculo" | |
| C2-13 🟠 | 2.3.2, "NO SÉ QUE HACER AYUDA" | "supone que el tamaño de paso es finito": se quiere decir **uniforme** | (a) Con datos tabulados no existe $\Phi(h/2)$, así que se usa el par $\Phi(h)$ y $\Phi(2h)$: $\frac{4\Phi(h) - \Phi(2h)}{3}$. Es lo que hace `d_richardson`. (b) El programa del Arduino muestrea con el ADC en modo continuo, así que el paso es uniforme ($t = n/f_s$) y Richardson se aplica directamente. (c) Si el paso no fuera uniforme, se interpolan los datos a una malla uniforme (por ejemplo, con un spline cúbico) antes de derivar | |
| C2-14 🟠 | 2.3.3, conteo en ventana | La tasa $n/W$ está en flancos por segundo, no en rad/s | $\omega \approx \pm\,n\,\Delta\theta / W$, con el signo de la cuadratura. Agregar que es la **diferencia hacia atrás con ventana**: $\omega_j \approx \frac{\theta_j - \theta_{j-k}}{t_j - t_{j-k}}$ | |
| C2-15 🟡 | 2.3, último encabezado | "2.2.4. Implementación en Python" | "2.3.4. Implementación en Python" | |
| C2-16 🟠 | Última celda de la Parte 2 | Queda cortada: "Por sí solo, un encoder de cuadratura permite" | Completar o borrar | |
| C2-17 🟡 | Imagen de la Parte 2 | No tiene pie ni fuente | Agregar "Figura 1. …" y la fuente, si la imagen no es propia | |

## Respuesta a la nota de Grettel (cuaderno importado, celda 12)

> "revisar si mi suposición de que se verifica que sea una función diferenciable y por ende que sea funciones analíticas realmente si aplica"

No hace falta que la función sea **analítica**. Basta con que tenga suficientes derivadas continuas para escribir el desarrollo de Taylor con residuo:
- **Adelante y atrás**, error $O(h)$: se necesitan dos derivadas continuas.
- **Centrada**, error $O(h^2)$: se necesitan tres.
- **Richardson**, error $O(h^4)$: se necesitan cinco.

Con los datos del encoder, la diferenciabilidad es una **suposición del modelo**: el movimiento real del eje es suave, pero la medición está cuantizada. Por eso, a escalas muy pequeñas, el error de cuantización domina sobre el de truncamiento (ver C2-10).

## Cambios ya aplicados al importar el código de Grettel y Deyler

Estos no requieren decisión; se describen para que el equipo los conozca:
- **Ubicación:** las funciones de derivación pasaron de la celda de "Modelación" a la sección 2.3.4, con docstrings y comentarios.
- **Validación de entradas:** las funciones rechazan una ventana $k$ inválida y un $t$ desordenado.
- **Tabla de métodos corregida:** la centrada es $O(h^2)$ solo con paso uniforme. Se comprobó numéricamente que con paso irregular baja a $O(h)$.
- **Richardson** acepta ventana $k$; con $k = 1$ da el mismo resultado que el original.
- **`omega_completa`** se reemplazó por `derivada_sin_bordes(t, y, k)`, que no depende de variables globales ni de un DataFrame.
- **La verificación con $\sin x$** usa solo numpy y confirma los órdenes 1, 1, 2 y 4.
