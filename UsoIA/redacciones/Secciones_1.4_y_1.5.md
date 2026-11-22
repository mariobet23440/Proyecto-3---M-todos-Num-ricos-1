# Redacción de las secciones 1.4 y 1.5 del cuaderno

| Campo | Detalle |
|-------|---------|
| **Fecha** | 22/11/2026 |
| **Autores** | Mario Alejandro Betancourt Franco (23440) · Claude Opus 5.5 (Anthropic), asistente de IA |
| **Dónde está** | Ya está aplicado en `Proyecto3MetodosNumericos.ipynb`. Abajo hay una copia del texto para pegarlo en Colab si hace falta |
| **Bitácora** | [`BitacoraUsoIA.md`](../BitacoraUsoIA.md), Entrada 9 |

> [!WARNING]
> **Aviso sobre el uso de IA.** Este texto lo redactó una herramienta de IA a partir del borrador y de las
> preguntas del autor. El equipo debe revisar las definiciones y las deducciones antes de entregarlo.

---

## Prompts

Se copian textualmente, en orden (22/11/2026).

**1.** Junto con el borrador de la sección 1.4 escrito por el autor, que se usó como base del texto:
```text
De nuevo explícame lo de esta parte. Por qué ignoraría Tk. Dado que el sistema es no lineal quité toda la parte del jacobiano
```

**2.**
```text
Qué tal si uso tanh. ¿Podría ser el Jacobiano ahi?
```

**3.**
```text
Pero no entiendo, por qué originalmente usamos f y ahora el Jacobiano si el sistema es no lineal. O el campo vectorial f se usa cuando el sistema es no derivable y el Jacobiano cuando sí
```

**4. Prompt de la redacción:**
```text
Ok. Quisiera que me ayudes redactando eso. Ya entiendo qué sucede. Cometí el error de utilizarlo en la deducción del método de Euler. Entiendo que lo usas en la parte de estabilidad porque f(Y)-f(y) approx J(Y-y) = Je y de ahi resulta lo que normalmente se obtiene. Aprovechando que introdujiste la condición de Lipschitz, quisiera que lo incluyas también, definiendo lo que significa que una función sea Lipschitz (que sea una transformación entre espacios métricos que no explote en el siguiente paso). Quisiera que también definas qué es el espacio métrico y su relación con funciones distancia. La parte de Lipschitz quisiera que vaya en una subsección más, la sección 1.5, dado que es un bonus que generaliza la solución de la estabilidad del método. Incluye este Prompt, corrige mi observación sobre C-01 y sube todo al repositorio
```

## Qué se cambió respecto del borrador del autor

- **Se conservó** el texto del autor hasta la ecuación del error.
- **Se corrigieron dos puntos:**
  - el primer componente del error: es $[\mathbf Y(x_k) - \mathbf y_k] = \mathbf e_k$, no $\mathbf Y(x_{k+1}) - \mathbf y_{k+1}$;
  - la definición de estabilidad: se separó de la de convergencia.
- **Se completó la frase** "La definición de $\mathbf e_{k+1}$ sugiere que el error en el paso…".
- **Se agregó en la 1.4:**
  - por qué el Jacobiano aparece en el análisis del error y no en el método;
  - por qué la estabilidad no depende de $\mathbf T_k$;
  - el criterio $|1 + h\lambda_i| \le 1$;
  - la regularización de la fricción de Coulomb con $\tanh$ y el Jacobiano del motor.
- **Quedó pendiente, como pidió el autor en C-06:** el cálculo de los valores propios del motor.
- **Sección 1.5 nueva:**
  - espacio métrico y función distancia;
  - funciones Lipschitz y su relación con el Jacobiano;
  - la cota del error global de Euler con $e^{\mathcal L(x_n - x_0)}$;
  - alcances y limitaciones.
- **Notación:** la constante de Lipschitz es $\mathcal L$, para no confundirla con la inductancia $L$, y el amortiguamiento efectivo es $b_{ef}(\omega)$, para no confundirlo con la función distancia $d$.

## Verificación

- Las 240 expresiones LaTeX del cuaderno compilan en MathJax 3.2.2 sin errores.
- No se modificó ninguna otra celda, salvo el historial de revisiones.

---

## Copia del texto: sección 1.4

## **1.4. Estabilidad Numérica del Método de Euler**
Suponga que la solución exacta del sistema de EDOs en $x_k$ es $\mathbf{Y}(x_k)$ (observe que se usó una letra mayúscula). Esta puede calcularse de forma exacta en las cercanías de $x_k$ al utilizar series de Taylor y agregar un término de error local $\mathbf{T}_k$ por los términos de orden superior:

$$\mathbf{Y}(x_{k+1}) = \mathbf{Y}(x_k) + h\,\mathbf{f}(x_k, \mathbf{Y}(x_k)) + \mathbf{T}_k$$

Como $\mathbf{Y}$ es una función vectorial, el residuo de Taylor se escribe componente a componente: cada componente tiene su propio punto intermedio $\epsilon_i \in (x_k, x_{k+1})$,

$$(\mathbf{T}_k)_i = \frac{h^2}{2}\,Y_i''(\epsilon_i), \qquad i = 1, 2, \dots, N$$

En general no existe un único $\epsilon$ que sirva para todas las componentes a la vez. Lo que sí se puede afirmar es la cota

$$\|\mathbf{T}_k\| \le \frac{h^2}{2}\max_{x\in[x_k,x_{k+1}]}\|\mathbf{Y}''(x)\|$$

Definimos el error en el paso $k$ como $\mathbf{e}_{k} = \mathbf{Y}(x_{k}) - \mathbf{y}_{k}$. Al restar la fórmula de Euler $\mathbf{y}_{k+1} = \mathbf{y}_k + h\,\mathbf{f}(x_k, \mathbf{y}_k)$ de la expansión de Taylor, el error en el paso $k+1$ es:

$$\mathbf{e}_{k+1} = \mathbf{Y}(x_{k+1}) - \mathbf{y}_{k+1} = [\mathbf{Y}(x_k)-\mathbf{y}_{k}] + h[\mathbf{f}(x_k, \mathbf{Y}(x_k)) - \mathbf{f}(x_k, \mathbf{y}_k)] + \mathbf{T}_k$$

Este error tiene tres componentes:
- $[\mathbf{Y}(x_k) - \mathbf{y}_k] = \mathbf{e}_k$ es el error global acumulado hasta el paso $k$.
- $h[\mathbf{f}(x_k, \mathbf{Y}(x_k)) - \mathbf{f}(x_k, \mathbf{y}_k)]$ es el error propagado por la pendiente: muestra cómo el error en el paso anterior influye en el error de la pendiente del paso siguiente.
- $\mathbf{T}_k$ es el error de truncamiento local, se agrega por la Serie de Taylor.

Un método de resolución de sistemas de EDOs es **numéricamente estable** si, conforme $k$ aumenta, los errores que ya existen no crecen sin control: la solución numérica no "explota" (en pocas palabras). No hay que confundir esto con la **convergencia**, que pide que la solución numérica se acerque a la analítica cuando $h \to 0$. Las dos ideas se relacionan: un método *consistente* (cuyo error local cumple $\mathbf{T}_k/h \to \mathbf{0}$) y estable es convergente.

La definición de $\mathbf{e}_{k+1}$ sugiere que el error en el paso $k+1$ depende del error en el paso $k$ a través de la pendiente. Para saber si ese error crece o se atenúa hay que responder una pregunta: **¿cuánto cambia $\mathbf{f}$ cuando su argumento pasa de $\mathbf{y}_k$ a $\mathbf{Y}(x_k)$?** Esa es justamente la pregunta que responde la derivada de $\mathbf{f}$.

### **El Jacobiano: la derivada del campo vectorial**

Observe la diferencia de papeles. El método de Euler se calcula siempre con el campo vectorial $\mathbf{f}$, sea el sistema lineal o no. El Jacobiano, que es la derivada de $\mathbf{f}$, no forma parte del método: aparece solo al analizar cómo se propaga el error.

Recuerde cómo se define. Sea $\mathbf{f}: \mathbb{R}^n \to \mathbb{R}^m$ una función vectorial diferenciable definida por $\mathbf{f}(\mathbf{x}) = (f_1(\mathbf{x}), f_2(\mathbf{x}), \dots, f_m(\mathbf{x}))$, donde $\mathbf{x} = (x_1, x_2, \dots, x_n)$. La *matriz jacobiana* de $\mathbf{f}$ en $\mathbf{x}$, denotada por $\mathbf{J}_{\mathbf{f}}(\mathbf{x})$ o $\frac{\partial \mathbf{f}}{\partial \mathbf{x}}$, es la matriz de $m \times n$ de sus primeras derivadas parciales:

$$
\mathbf{J}_{\mathbf{f}}(\mathbf{x}) = \frac{\partial (f_1, \dots, f_m)}{\partial (x_1, \dots, x_n)} =
\begin{pmatrix}
\frac{\partial f_1}{\partial x_1} & \frac{\partial f_1}{\partial x_2} & \cdots & \frac{\partial f_1}{\partial x_n} \\
\frac{\partial f_2}{\partial x_1} & \frac{\partial f_2}{\partial x_2} & \cdots & \frac{\partial f_2}{\partial x_n} \\
\vdots & \vdots & \ddots & \vdots \\
\frac{\partial f_m}{\partial x_1} & \frac{\partial f_m}{\partial x_2} & \cdots & \frac{\partial f_m}{\partial x_n}
\end{pmatrix}
$$

En nuestro caso interesa el Jacobiano del campo vectorial respecto de las variables dependientes $\mathbf{y}$, que es una matriz de $N \times N$:

$$
\mathbf{J}_{\mathbf{f}}(x,\mathbf{y}) = \frac{\partial \mathbf{f}}{\partial \mathbf{y}} =
\begin{pmatrix}
\frac{\partial f_1}{\partial y_1} & \cdots & \frac{\partial f_1}{\partial y_N} \\
\vdots & \ddots & \vdots \\
\frac{\partial f_N}{\partial y_1} & \cdots & \frac{\partial f_N}{\partial y_N}
\end{pmatrix}
$$

Por el teorema del valor medio en su forma integral, si $\mathbf{f}$ es diferenciable respecto de $\mathbf{y}$:

$$\mathbf{f}(x_k,\mathbf{Y}(x_k)) - \mathbf{f}(x_k,\mathbf{y}_k) = \left[\int_0^1 \mathbf{J}_{\mathbf{f}}\big(x_k,\ \mathbf{y}_k + s\,\mathbf{e}_k\big)\,ds\right]\mathbf{e}_k \approx \mathbf{J}_k\,\mathbf{e}_k$$

donde $\mathbf{J}_k := \mathbf{J}_{\mathbf{f}}(x_k,\mathbf{y}_k)$ es el Jacobiano evaluado en el paso $k$. La aproximación es exacta si $\mathbf{f}$ es afín en $\mathbf{y}$ (lineal más una constante); en general, el error que se comete es $O(\|\mathbf{e}_k\|^2)$. Al sustituir en la ecuación del error:

$$\mathbf{e}_{k+1} \approx \underbrace{(\mathbf{I} + h\mathbf{J}_k)\,\mathbf{e}_k}_{\text{propagación del error}} + \underbrace{\mathbf{T}_k}_{\text{error local nuevo}}$$

donde $\mathbf{I}$ es la matriz identidad de $N \times N$. La matriz $(\mathbf{I} + h\mathbf{J}_k)$ es la **matriz de amplificación**: dice cuánto se amplifica o se atenúa, en un paso, el error que ya existía.

### **¿Por qué la estabilidad no depende de $\mathbf{T}_k$?**

$\mathbf{T}_k$ no se ignora: es el error nuevo que se inyecta en cada paso, de tamaño $O(h^2)$. Pero no decide si el método es estable. Para verlo, suponga por simplicidad que el Jacobiano es constante, $\mathbf{J}_k = \mathbf{J}$, y desenrolle la recurrencia:

$$\mathbf{e}_n = (\mathbf{I} + h\mathbf{J})^n\,\mathbf{e}_0 + \sum_{j=0}^{n-1}(\mathbf{I} + h\mathbf{J})^{n-1-j}\,\mathbf{T}_j$$

Cada error que entra (el inicial $\mathbf{e}_0$ y cada $\mathbf{T}_j$) queda multiplicado por potencias de la misma matriz de amplificación:
- Si $(\mathbf{I} + h\mathbf{J})$ no amplifica, los errores locales simplemente se acumulan: $n$ términos de tamaño $O(h^2)$, con $n = (x_n - x_0)/h$, dan un error global $O(h)$. El método es estable.
- Si $(\mathbf{I} + h\mathbf{J})$ amplifica, sus potencias crecen sin control y hacen explotar tanto $\mathbf{e}_0$ como cada $\mathbf{T}_j$. El método es inestable.

Por eso el análisis de estabilidad estudia solo la parte de propagación, $\mathbf{e}_{k+1} \approx (\mathbf{I} + h\mathbf{J}_k)\,\mathbf{e}_k$. Si $\mathbf{J}$ es diagonalizable, con valores propios $\lambda_1, \dots, \lambda_N$, se obtiene el resultado usual, el **criterio de estabilidad absoluta** del método de Euler:

$$|1 + h\lambda_i| \le 1 \qquad \text{para todo } i = 1, \dots, N$$

Cuando $\mathbf{J}_k$ cambia de un paso a otro (sistema no lineal), el error acumulado es un producto de matrices distintas, $(\mathbf{I}+h\mathbf{J}_{n-1})\cdots(\mathbf{I}+h\mathbf{J}_1)(\mathbf{I}+h\mathbf{J}_0)\,\mathbf{e}_0$, y el criterio se aplica de forma local, con los valores propios del Jacobiano en cada zona de operación.

### **El caso del motor: la fricción de Coulomb**

El análisis anterior supone que $\mathbf{f}$ es diferenciable. En el modelo del motor esto falla en $\omega = 0$, donde $\text{sign}(\omega)$ salta de $-1$ a $1$ y no tiene derivada. Una solución habitual es **regularizar** la fricción con una función suave:

$$\text{sign}(\omega) \approx \tanh\left(\frac{\omega}{\varepsilon}\right), \qquad \varepsilon > 0 \text{ pequeño}$$

Esto es un cambio en el modelo, y conviene declararlo junto con el valor de $\varepsilon$ que se use. Como $\tanh$ es diferenciable, el Jacobiano existe en todas partes. Con el vector de estado $\mathbf{y} = [i,\ \omega,\ \theta]^T$:

$$
\mathbf{J}_{\mathbf{f}}(\omega) =
\begin{pmatrix}
-\dfrac{R}{L} & -\dfrac{K_e}{L} & 0 \\[6pt]
\dfrac{K_t}{J_m} & -\dfrac{b_{ef}(\omega)}{J_m} & 0 \\[6pt]
0 & 1 & 0
\end{pmatrix},
\qquad
b_{ef}(\omega) = b + \frac{\tau_c}{\varepsilon}\,\text{sech}^2\left(\frac{\omega}{\varepsilon}\right)
$$

La fricción de Coulomb aparece como un amortiguamiento efectivo $b_{ef}(\omega)$ que depende de la velocidad:
- Lejos de cero ($|\omega| \gg \varepsilon$), $\text{sech}^2 \to 0$ y $b_{ef} \approx b$: el Jacobiano es la matriz constante del modelo sin fricción de Coulomb.
- Cerca de cero, $b_{ef} \approx b + \tau_c/\varepsilon$, un valor muy grande. Ese término vuelve al sistema **rígido** cerca de $\omega = 0$: obligará a usar pasos $h$ pequeños, tanto más pequeños cuanto menor sea $\varepsilon$.

El cálculo de los valores propios de $\mathbf{J}_{\mathbf{f}}(\omega)$ con los parámetros del motor, y el paso máximo que resulta del criterio de estabilidad absoluta, se desarrollará más adelante.

---

## Copia del texto: sección 1.5

## **1.5. Bonus: estabilidad del método de Euler con la condición de Lipschitz**

El análisis de la sección 1.4 tiene dos limitaciones: necesita que $\mathbf{f}$ sea diferenciable, y es local, porque se apoya en la aproximación $\mathbf{f}(x_k,\mathbf{Y}(x_k)) - \mathbf{f}(x_k,\mathbf{y}_k) \approx \mathbf{J}_k\,\mathbf{e}_k$. En esta sección se generaliza el resultado con una herramienta que no necesita derivadas: la **condición de Lipschitz**. Para enunciarla hay que precisar antes qué significa "distancia".

### **Espacios métricos y funciones distancia**

Un **espacio métrico** es un par $(M, d)$ formado por un conjunto $M$ y una **función distancia** (o métrica) $d: M \times M \to \mathbb{R}$ que, para todos $a, b, c \in M$, cumple:

1. **No negatividad:** $d(a,b) \ge 0$, y $d(a,b) = 0$ si y solo si $a = b$.
2. **Simetría:** $d(a,b) = d(b,a)$.
3. **Desigualdad triangular:** $d(a,c) \le d(a,b) + d(b,c)$.

La función distancia formaliza la idea intuitiva de "qué tan lejos" están dos elementos del conjunto. El ejemplo que nos interesa es $\mathbb{R}^N$ con la distancia inducida por una norma:

$$d(\mathbf{a},\mathbf{b}) = \|\mathbf{a} - \mathbf{b}\|$$

Cualquier norma sirve; por ejemplo, la euclidiana $\|\mathbf{v}\|_2 = \sqrt{v_1^2 + \dots + v_N^2}$ o la del máximo $\|\mathbf{v}\|_\infty = \max_i |v_i|$. Con esta notación, la norma del error es una distancia: $\|\mathbf{e}_k\| = d\big(\mathbf{Y}(x_k), \mathbf{y}_k\big)$ mide qué tan lejos está la solución numérica de la exacta en el paso $k$.

### **Funciones Lipschitz**

Sean $(X, d_X)$ y $(Z, d_Z)$ dos espacios métricos. Una función $g: X \to Z$ es **Lipschitz** si existe una constante $\mathcal{L} \ge 0$ tal que

$$d_Z\big(g(a), g(b)\big) \le \mathcal{L}\, d_X(a, b) \qquad \text{para todos } a, b \in X$$

La menor constante que cumple esta desigualdad se llama **constante de Lipschitz**. (Se usa $\mathcal{L}$ para no confundirla con la inductancia $L$ del motor.) La interpretación es directa: una función Lipschitz no "estira" las distancias más que un factor $\mathcal{L}$. Dos puntos cercanos siguen cercanos después de aplicar $g$: en un solo paso, la distancia entre las imágenes no puede crecer más de $\mathcal{L}$ veces, así que no puede explotar.

Para un sistema de EDOs se usa esta condición respecto de las variables dependientes: $\mathbf{f}$ es Lipschitz en $\mathbf{y}$ si existe $\mathcal{L}$ tal que

$$\|\mathbf{f}(x,\mathbf{Y}) - \mathbf{f}(x,\mathbf{y})\| \le \mathcal{L}\,\|\mathbf{Y} - \mathbf{y}\| \qquad \text{para todo } x \text{ del intervalo y todos } \mathbf{Y}, \mathbf{y}$$

Esta condición tiene una consecuencia importante que no se demuestra aquí: garantiza que el PVI tenga solución y que esa solución sea única (teorema de Picard-Lindelöf).

**Relación con el Jacobiano.** Si $\mathbf{f}$ es diferenciable respecto de $\mathbf{y}$ en una región convexa y su Jacobiano está acotado ahí, entonces $\mathbf{f}$ es Lipschitz en esa región con

$$\mathcal{L} = \sup \|\mathbf{J}_{\mathbf{f}}\|$$

donde la norma de la matriz es la inducida por la norma vectorial elegida. Lo contrario no es cierto: una función puede ser Lipschitz sin ser diferenciable. Por ejemplo, $g(x) = |x|$ es Lipschitz con $\mathcal{L} = 1$, aunque no tiene derivada en $x = 0$.

**Ejemplos del motor:**
- $\tanh(\omega/\varepsilon)$ es Lipschitz con $\mathcal{L} = 1/\varepsilon$, porque su derivada cumple $\frac{1}{\varepsilon}\,\text{sech}^2(\omega/\varepsilon) \le \frac{1}{\varepsilon}$.
- $\text{sign}(\omega)$ **no** es Lipschitz: ni siquiera es continua en $\omega = 0$. Dos velocidades $\omega = -\delta$ y $\omega = \delta$, tan cercanas como se quiera, tienen imágenes a distancia $2$.

### **Cota del error global del método de Euler**

Suponga que $\mathbf{f}$ es Lipschitz en $\mathbf{y}$ con constante $\mathcal{L}$, y que $\|\mathbf{Y}''(x)\| \le M$ en todo el intervalo, de modo que $\|\mathbf{T}_k\| \le \frac{h^2}{2}M$ (sección 1.4). Al tomar normas en la ecuación del error y usar la desigualdad triangular:

$$\|\mathbf{e}_{k+1}\| \le \|\mathbf{e}_k\| + h\,\|\mathbf{f}(x_k,\mathbf{Y}(x_k)) - \mathbf{f}(x_k,\mathbf{y}_k)\| + \|\mathbf{T}_k\| \le (1 + h\mathcal{L})\,\|\mathbf{e}_k\| + \frac{h^2}{2}M$$

Observe que aquí no se aproximó nada ni se derivó: la condición de Lipschitz reemplaza al Jacobiano. Al aplicar la desigualdad repetidamente, desde $k = 0$ hasta $k = n-1$:

$$\|\mathbf{e}_n\| \le (1+h\mathcal{L})^n\,\|\mathbf{e}_0\| + \frac{h^2 M}{2}\sum_{j=0}^{n-1}(1+h\mathcal{L})^j$$

La suma es geométrica:

$$\sum_{j=0}^{n-1}(1+h\mathcal{L})^j = \frac{(1+h\mathcal{L})^n - 1}{h\mathcal{L}}$$

Por último, como $1 + z \le e^{z}$ para todo $z$, se cumple $(1+h\mathcal{L})^n \le e^{nh\mathcal{L}} = e^{\mathcal{L}(x_n - x_0)}$, ya que $nh = x_n - x_0$. Al juntar todo:

$$\boxed{\|\mathbf{e}_n\| \le e^{\mathcal{L}(x_n - x_0)}\,\|\mathbf{e}_0\| + \frac{hM}{2\mathcal{L}}\left(e^{\mathcal{L}(x_n - x_0)} - 1\right)}$$

Esta cota dice dos cosas:
1. **Estabilidad:** un error inicial $\mathbf{e}_0$ (por ejemplo, de redondeo) se amplifica como mucho por el factor $e^{\mathcal{L}(x_n - x_0)}$, que no depende de $h$: queda acotado en cualquier intervalo finito.
2. **Convergencia de orden 1:** si $\mathbf{e}_0 = \mathbf{0}$, el error global es $O(h)$: al reducir $h$ a la mitad, la cota del error se reduce a la mitad. Este término viene de $\mathbf{T}_k$: el error local no se ignoró, sino que se fue acumulando.

### **Alcances y limitaciones**

- **Ventaja:** el resultado vale para sistemas no lineales en todo el intervalo, sin linealizar y sin necesitar derivadas.
- **Limitación 1: la cota es muy pesimista.** El factor $e^{\mathcal{L}(x_n - x_0)}$ crece muy rápido con $\mathcal{L}$. En el motor con la regularización $\tanh$, la constante de Lipschitz es al menos del orden de $\max\{R/L,\ \tau_c/(J_m\varepsilon)\}$, que puede ser de miles de $\text{s}^{-1}$; en un intervalo de un segundo, el factor sería astronómico. La cota garantiza que el método converge cuando $h \to 0$, pero no sirve para elegir $h$ en la práctica. Para eso se usa el criterio de estabilidad absoluta de la sección 1.4.
- **Limitación 2: requiere que $\mathbf{f}$ sea Lipschitz.** Con $\text{sign}(\omega)$, el teorema no se aplica cuando $\omega$ cruza cero. La regularización con $\tanh$ lo resuelve, a cambio de una constante $\mathcal{L}$ grande.
