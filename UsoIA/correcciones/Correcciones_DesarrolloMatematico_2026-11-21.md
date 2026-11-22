# Propuesta de correcciones — Desarrollo matemático

**Proyecto 3 — Métodos Numéricos 1 · Motor DC: gemelo digital y control PID**

| Campo | Detalle |
|-------|---------|
| **Documento revisado** | `Proyecto3MetodosNumericos.ipynb` |
| **Versión revisada** | commit `7b05bf5` ("Deducción de Estabilidad del Método de Euler") |
| **Secciones revisadas** | Introducción (celdas 5–8), Parte 1: secciones 1.1 a 1.4 (celdas 10–12) |
| **Fecha de la propuesta** | 21/11/2026 |
| **Elaborado con** | Claude Code (Claude Opus 5.5, Anthropic), a pedido de Mario Betancourt. Ver [`BitacoraUsoIA.md`](../BitacoraUsoIA.md) |
| **Referencias** | [`Referencias.md`](Referencias.md) |
| **Última actualización** | 22/11/2026: C-15 verificada con el libro de Nise y notas agregadas en C-03 y C-16 |

---

> [!WARNING]
> **Aviso importante.** Este documento lo generó una herramienta de inteligencia artificial y contiene **solo propuestas**.
> Ninguna corrección se ha aplicado al cuaderno. **Cada corrección debe ser revisada y aprobada por los
> miembros del equipo** antes de incorporarse al trabajo. La IA puede equivocarse: verifiquen cada argumento
> con la bibliografía del curso y con su propio criterio. La responsabilidad sobre el contenido final del
> proyecto es del equipo.

---

## Datos del revisor

Cada integrante que revise este documento llena una fila.

| Nombre del revisor | Carné | Fecha de revisión | Correcciones revisadas | Firma / iniciales |
|---|---|---|---|---|
| Mario Alejandro Betancourt Franco | 23440 | 22/11/2026 a las 00:10 AM | Conceptuales (C-01 a C-04) | MBF |


---

## Cómo usar este documento

1. Lean cada corrección: **texto original**, **corrección propuesta** y **justificación**.
2. Marquen una decisión con una `x` en el recuadro (`[x]`): **Aprobada**, **Aprobada con cambios** o **Rechazada**.
3. Si la modifican o la rechazan, expliquen por qué en el campo *Comentario del revisor*.
4. Al final, anoten observaciones generales en la sección [Observaciones del revisor](#observaciones-del-revisor).
5. Apliquen al cuaderno **solo** las correcciones aprobadas.

**Gravedad:**
- 🔴 **Error conceptual**: el resultado o el razonamiento es incorrecto.
- 🟠 **Imprecisión**: el resultado sirve, pero falta una hipótesis o la justificación no es válida tal como está escrita.
- 🟡 **Forma**: notación, terminología, LaTeX u ortografía.

---

## Índice de correcciones

| ID | Sección / celda | Gravedad | Tema |
|----|-----------------|----------|------|
| [C-01](#c-01) | 1.2 · celda 11 | 🔴 | $\mathbf{y}' = J\mathbf{y}$ confunde el Jacobiano con el campo vectorial |
| [C-02](#c-02) | 1.2 · celda 11 | 🔴 | $(1+hJ)\mathbf{y}_k$ solo vale para sistemas lineales |
| [C-03](#c-03) | Modelo, 1.2, 1.4 | 🔴 | El símbolo $J$ se usa para la inercia y para el Jacobiano |
| [C-04](#c-04) | 1.4 · celda 12 | 🔴 | Índice incorrecto en la ecuación del error |
| [C-05](#c-05) | 1.4 · celda 12 | 🟠 | La diferencia de $\mathbf f$ es una aproximación, no una igualdad |
| [C-06](#c-06) | 1.4 · celda 12 | 🟠 | Justificación para descartar el error de truncamiento |
| [C-07](#c-07) | 1.4 · celda 12 | 🟠 | Resto de Taylor para funciones vectoriales |
| [C-08](#c-08) | Modelo, celda 8 | 🟠 | $\operatorname{sign}(\omega)$ no es diferenciable en $\omega=0$ |
| [C-09](#c-09) | 1.2, 1.4 | 🟡 | $1$ en lugar de la matriz identidad $I$ |
| [C-10](#c-10) | 1.1, 1.2, 1.3 | 🟡 | "Variable independiente" donde va "dependiente" |
| [C-11](#c-11) | 1.1 · celda 10 | 🟡 | Punto de evaluación de $f$ y notación de $y_k$ |
| [C-12](#c-12) | 1.1–1.4 | 🟡 | Uso mezclado de $x$ y $t$ |
| [C-13](#c-13) | 1.3 · celda 11 | 🟡 | Notación de conjunto y número de EDOs equivalentes |
| [C-14](#c-14) | celdas 7, 11 | 🟡 | LaTeX que no compila o se ve mal |
| [C-15](#c-15) | celdas 7, 8 | 🟡 | Referencia a Nise incompleta |
| [C-16](#c-16) | varias | 🟡 | Ortografía y redacción |

---

## 🔴 Errores conceptuales

<a id="c-01"></a>
### C-01 · $\mathbf{y}' = J\mathbf{y}$ confunde el Jacobiano con el campo vectorial

**Ubicación:** Sección 1.2, celda 11.

**Texto original:**
> "se deduce que el Jacobiano de $\textbf{y}$ […] es: $J\textbf{y} = \left[\frac{dy_1}{dt}, \dots, \frac{dy_N}{dt}\right]^T$ […] Resulta obvio que: $\textbf{y}' = J\textbf{y}$"
>
> "¡Para sistemas de EDOs de primer orden el operador de la pendiente $f(x,y)$ se reemplaza por el Jacobiano!"
>
> "Por definición, el Jacobiano en este caso es un vector con los operadores $f_1$, $f_2$, …, $f_N$."

**Corrección propuesta:**

Reemplazar el argumento del Jacobiano por la definición del **campo vectorial** $\mathbf f$:

$$
\mathbf{y} = \begin{pmatrix} y_1 \\ \vdots \\ y_N \end{pmatrix},\qquad
\mathbf{f}(t,\mathbf{y}) = \begin{pmatrix} f_1(t,\mathbf{y}) \\ \vdots \\ f_N(t,\mathbf{y}) \end{pmatrix}
\quad\Longrightarrow\quad
\mathbf{y}' = \mathbf{f}(t,\mathbf{y})
$$

La conclusión queda: *"Para sistemas de EDOs de primer orden, la función de pendiente escalar $f(t,y)$ se reemplaza por el campo vectorial $\mathbf{f}(t,\mathbf{y})$"*, y el método de Euler en forma vectorial es:

$$\mathbf{y}_{k+1} = \mathbf{y}_k + h\,\mathbf{f}(t_k,\mathbf{y}_k)$$

El Jacobiano se presenta después, como la herramienta para el análisis de estabilidad:

$$
J_{\mathbf f}(t,\mathbf y) = \frac{\partial \mathbf f}{\partial \mathbf y} =
\begin{pmatrix}
\frac{\partial f_1}{\partial y_1} & \cdots & \frac{\partial f_1}{\partial y_N} \\
\vdots & \ddots & \vdots \\
\frac{\partial f_N}{\partial y_1} & \cdots & \frac{\partial f_N}{\partial y_N}
\end{pmatrix}\in\mathbb{R}^{N\times N}
$$

**Justificación:**
- Si $\mathbf{y}:\mathbb{R}\to\mathbb{R}^N$ es función de $t$, su Jacobiano respecto de $t$ es una matriz $N\times 1$ **igual a** $\mathbf{y}'$. Es la misma cosa, no un operador que multiplique a $\mathbf{y}$. Por eso la expresión $J\mathbf{y}$, leída como producto matriz–vector, no tiene sentido.
- El vector $(f_1,\dots,f_N)$ es el campo vectorial $\mathbf f$, no un Jacobiano. Un Jacobiano contiene **derivadas parciales**.
- El Jacobiano que de verdad importa es $\partial\mathbf f/\partial\mathbf y$ (matriz $N\times N$). Es el que se usa, correctamente, en la sección 1.4 (ver C-05).

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Es correcto. Yo confundí el campo vectorial por el Jacobiano. Esto podría deberse a que consulté a la IA de Google sobre la resolución de sistemas de ecuaciones diferenciales y el criterio de estabilidad numérica del método de Euler, y la IA presentó únicamente resultados para sistemas lineales y autónomos (no como el sistema del motor). En ese caso, la igualdad se cumple. Este caso es común en la presentación de la estabilidad numérica del método de Euler. Sin embargo, después de intentar sacar el Jacobiano para el sistema del motor, se encontró que era imposible meter los términos constantes dentro de la matriz jacobiana. Por lo tanto, este contraejemplo justifica la decisión de aplicar la corrección. 

En pocas palabras. Si intentamos sacar el jacobiano del sistema, donde aparecen términos constantes que se suman y restan, ¿dónde caben en el jacobiano? ¡En ninguna parte! y por lo tanto, mi intuición inicial estaba equivocada y no tenía pies ni cabeza. 

PROMPT UTILIZADO PARA ARREGLAR: Por favor reemplazar todas las apariciones del Jacobiano en las deducciones del método por el campo vectorial f, excepto en la sección de análisis de estabilidad.

&nbsp;

---

<a id="c-02"></a>
### C-02 · $\mathbf{y}_{k+1}=(1+hJ)\mathbf{y}_k$ solo vale para sistemas lineales

**Ubicación:** Sección 1.2, celda 11.

**Texto original:**
> "$\textbf{y}_{k+1} =\textbf{y}_{k} + h J\textbf{y}_{k}$ — Al reunir todos los operadores en un solo paréntesis: $\textbf{y}_{k+1} =(1 + h J) \textbf{y}_{k}$ — Esta forma de expresar la fórmula iterativa del método de Euler es extremadamente importante."

**Corrección propuesta:**

Presentar esta forma como un **caso particular**:

> *Caso particular: sistema lineal.* Si el sistema es lineal y autónomo, $\mathbf{y}' = A\mathbf{y}$ con $A\in\mathbb{R}^{N\times N}$ constante, entonces $\mathbf f(t,\mathbf y) = A\mathbf y$, su Jacobiano es exactamente $A$, y el método de Euler queda
> $$\mathbf{y}_{k+1} = \mathbf{y}_k + hA\mathbf{y}_k = (I + hA)\,\mathbf{y}_k.$$
> Este sistema es el **problema modelo** para estudiar estabilidad. Para un sistema no lineal no se puede factorizar $\mathbf y_k$, pero el mismo factor $(I + hJ_{\mathbf f})$ aparece en la ecuación del **error** (sección 1.4).

**Justificación:**
Factorizar $\mathbf y_k$ requiere que $\mathbf f$ sea lineal en $\mathbf y$. El modelo del motor no lo es:
- tiene términos constantes ($V/L$ y $-\tau_{carga}/J_m$), así que como mucho es afín: $\mathbf y' = A\mathbf y + \mathbf b$;
- tiene el término $-\tau_c\operatorname{sign}(\omega)$, que no es lineal.

La forma $(I+hA)\mathbf y_k$ sí es importante, pero para el **error**, no para la solución.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Claude tenía razón: yo cometí un error al investigar al utilizar la IA de Google como referencia. Es posible que haya considerado únicamente ejemplos de sistemas de EDOs lineales. El sistema de ecuaciones diferenciales del motor es no lineal por los términos constantes que se agregan. Se tomó la decisión de no presentar el caso particular: no aporta nada al estudio al que está orientado este proyecto. Junto con la corrección C-01 podemos proceder. (Revisor: Mario Betancourt).


&nbsp;

---

<a id="c-03"></a>
### C-03 · El símbolo $J$ se usa para la inercia y para el Jacobiano

**Ubicación:** Modelo del motor (celdas 6–7), sección 1.2 (celda 11) y sección 1.4 (celda 12).

**Texto original:**
> Celda 6: "$J\frac{d\omega}{dt} = K_t i - b\omega - \dots$" · Celda 7: "$J$ - Inercia del eje del motor"
>
> Celdas 11 y 12: "$\textbf{y}_{k+1} =(1 + h J) \textbf{y}_{k}$", "$\textbf{e}_{k+1} \approx (1 + hJ)\textbf{e}_{k}$"

**Corrección propuesta:**
- Inercia del eje: $J \to J_m$ en el modelo, en la lista de símbolos y en todo el texto posterior.
- Jacobiano: $J \to \mathbf{J}_{\mathbf f}$ (o $J_{\mathbf f}$). En el caso lineal de C-02, usar $A$.

**Justificación:**
Al calcular el Jacobiano del motor aparece la inercia dentro de él. La segunda fila es $\left(\frac{K_t}{J},\ -\frac{b}{J},\ 0\right)$, así que se escribiría "$J$ contiene $1/J$". Con notaciones distintas se evita la ambigüedad.

**Respaldo bibliográfico:** Nise también llama $J_m$ a la inercia equivalente en la armadura [Nise 2015, §2.8, p. 79, Fig. 2.36]. Ver [`Referencias.md`](Referencias.md).

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Decisión que a mi parecer es puramente estética. Apruebo sin pensármela mucho. Arreglar con IA.

&nbsp;

---

<a id="c-04"></a>
### C-04 · Índice incorrecto en la ecuación del error

**Ubicación:** Sección 1.4, celda 12, segunda ecuación.

**Texto original:**
$$\textbf{e}_{k+1} = \textbf{Y}(x_{k+1}) - \textbf{y}_{k+1} = [\textbf{Y}(x_k)-\textbf{y}_{k+1}] + h[\textbf{f}(x_k, \textbf{Y}(x_k)) - \textbf{f}(x_k, \textbf{y}_k)] + \frac{h^2}{2}\textbf{Y}''(\epsilon)$$

**Corrección propuesta:**
$$\mathbf{e}_{k+1} = \mathbf{Y}(t_{k+1}) - \mathbf{y}_{k+1} = [\mathbf{Y}(t_k)-\mathbf{y}_{k}] + h[\mathbf{f}(t_k, \mathbf{Y}(t_k)) - \mathbf{f}(t_k, \mathbf{y}_k)] + \mathbf{T}_k$$

($\mathbf T_k$ es el término de truncamiento; ver C-07.)

**Justificación:**
Al restar la fórmula de Euler $\mathbf{y}_{k+1} = \mathbf{y}_k + h\mathbf{f}(t_k,\mathbf{y}_k)$ de la expansión de Taylor
$\mathbf{Y}(t_{k+1}) = \mathbf{Y}(t_k) + h\mathbf{f}(t_k,\mathbf{Y}(t_k)) + \mathbf T_k$,
término a término queda $\mathbf{Y}(t_k) - \mathbf{y}_k = \mathbf e_k$. La línea siguiente del cuaderno ya usa $\mathbf e_k$, así que el resultado final no cambia; solo hay que corregir la línea intermedia.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Pequeño typo que cometí. Arreglar con IA.

&nbsp;

---

## 🟠 Imprecisiones

<a id="c-05"></a>
### C-05 · La diferencia de $\mathbf f$ es una aproximación, no una igualdad

**Ubicación:** Sección 1.4, celda 12.

**Texto original:**
> "Observe que $[\textbf{f}(x_k, \textbf{Y}(x_k)) - \textbf{f}(x_k, \textbf{y}_k)] = J[\textbf{Y}(x_k)-\textbf{y}_k]$."

**Corrección propuesta:**
> Por el teorema del valor medio (forma integral), si $\mathbf f$ es diferenciable respecto de $\mathbf y$:
> $$\mathbf{f}(t_k,\mathbf{Y}(t_k)) - \mathbf{f}(t_k,\mathbf{y}_k) = \left[\int_0^1 J_{\mathbf f}\big(t_k,\ \mathbf{y}_k + s\,\mathbf{e}_k\big)\,ds\right]\mathbf{e}_k \approx J_{\mathbf f}(t_k,\mathbf{y}_k)\,\mathbf{e}_k,$$
> donde $J_k := J_{\mathbf f}(t_k,\mathbf y_k)$ es el Jacobiano de $\mathbf f$ respecto de $\mathbf y$ evaluado en el paso $k$. La aproximación es exacta si $\mathbf f$ es lineal en $\mathbf y$; en general el error es $O(\|\mathbf e_k\|^2)$.
>
> Por lo tanto $\mathbf e_{k+1} \approx (I + hJ_k)\,\mathbf e_k$ y, a lo largo de $n$ pasos,
> $$\mathbf e_n \approx (I+hJ_{n-1})\cdots(I+hJ_1)(I+hJ_0)\,\mathbf e_0.$$

**Justificación:**
- La igualdad exacta solo vale si $\mathbf f$ es lineal en $\mathbf y$.
- Hay que decir **qué** Jacobiano es ($\partial\mathbf f/\partial\mathbf y$, no el "Jacobiano de $\mathbf y$" de la sección 1.2) y **dónde** se evalúa.
- En un sistema no lineal, $J$ cambia en cada paso. Por eso el error acumulado es un producto de matrices distintas, no una potencia $(I+hJ)^n$.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Es correcto. Respaldada por la corrección C-01 (Mario Betancourt)

&nbsp;

---

<a id="c-06"></a>
### C-06 · Justificación para descartar el error de truncamiento

**Ubicación:** Sección 1.4, celda 12.

**Texto original:**
> "Si escogemos un $h$ suficientemente pequeño, el error asociado al residuo $\textbf{Y}''(\epsilon)$ debería ser despreciable comparado a los demás términos de la ecuación. Por lo tanto, de ahora en adelante, lo descartamos […]"

**Corrección propuesta:**
> La recurrencia del error tiene dos partes:
> $$\mathbf{e}_{k+1} = \underbrace{(I+hJ_k)\,\mathbf{e}_k}_{\text{propagación del error}} + \underbrace{\mathbf{T}_k}_{\text{error local nuevo},\ O(h^2)}$$
> El análisis de **estabilidad** estudia la primera parte: cómo se amplifica o se atenúa un error que ya existe. Por eso se analiza la recurrencia homogénea $\mathbf{e}_{k+1} = (I + hJ_k)\mathbf{e}_k$. El término $\mathbf T_k$ no se descarta por ser pequeño: es el error que se inyecta en cada paso, y lo que pide la estabilidad es que el método no lo amplifique.
>
> **Criterio de estabilidad.** Si $J$ es (aproximadamente) constante y diagonalizable con valores propios $\lambda_1,\dots,\lambda_N$, el método de Euler es estable si
> $$\rho(I+hJ) = \max_i |1 + h\lambda_i| \le 1.$$
> Para $\lambda_i$ reales y negativos, esto da $h \le \dfrac{2}{|\lambda_i|}$ para todo $i$, es decir, $h \le \dfrac{2}{\max_i|\lambda_i|}$.

**Justificación:**
- El error global de Euler es $\|\mathbf e_k\| = O(h)$, así que $hJ\mathbf e_k = O(h^2)$, **del mismo orden** que $\mathbf T_k = O(h^2)$. Un $h$ pequeño no hace al residuo despreciable frente a los otros términos.
- La justificación correcta es conceptual: estabilidad (no amplificar errores) más consistencia ($\mathbf T_k/h \to 0$) implican convergencia (teorema de equivalencia de Lax / Dahlquist).
- Con el criterio $|1+h\lambda_i|\le 1$ la sección termina en un resultado utilizable. Ahora termina diciendo que el factor "es en realidad un operador", sin conclusión.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Todavía no hacer la diagonalización del Jacobiano. Eso se revisará por mi persona. Claude tiene un punto. No es necesario justificar la decisión de desaparecer el término proporcional al cuadrado de h, dado que el análisis de estabilidad se concentra únicamente en la amplificación del error ya existente, el cual produce la divergencia a gran escala. Entendí que T_k es ese erorr en cuestión.

&nbsp;

---

<a id="c-07"></a>
### C-07 · Resto de Taylor para funciones vectoriales

**Ubicación:** Sección 1.4, celda 12, primera ecuación.

**Texto original:**
$$\textbf{Y}(x_{k+1}) = \textbf{Y}(x_k) + h\textbf{f}(x_k, \textbf{Y}(x_k)) + \frac{h^2}{2}\textbf{Y}''(\epsilon)$$

**Corrección propuesta:**
$$\mathbf{Y}(t_{k+1}) = \mathbf{Y}(t_k) + h\,\mathbf{f}(t_k, \mathbf{Y}(t_k)) + \mathbf{T}_k,
\qquad (\mathbf T_k)_i = \frac{h^2}{2}\,Y_i''(\epsilon_i),\quad \epsilon_i\in(t_k,t_{k+1})$$

o, en forma de cota,

$$\|\mathbf T_k\| \le \frac{h^2}{2}\max_{t\in[t_k,t_{k+1}]}\|\mathbf Y''(t)\|.$$

**Justificación:**
El teorema de Taylor con resto de Lagrange vale para funciones escalares. En una función vectorial, cada componente tiene su propio punto intermedio $\epsilon_i$; en general no existe un único $\epsilon$ que sirva para todas a la vez. Además, el cuaderno no dice en qué intervalo está $\epsilon$, y hay que agregarlo.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Interesante observación. No lo había considerado. Aporta mucho a la consistencia del desarrollo matemático.

&nbsp;

---

<a id="c-08"></a>
### C-08 · $\operatorname{sign}(\omega)$ no es diferenciable en $\omega=0$

**Ubicación:** Modelo del motor (celda 6), comentario sobre linealización (celda 8) y análisis con el Jacobiano (celda 12).

**Texto original:**
> Celda 8: "Aunque es posible linealizar el sistema y analizarlo a través de Transformadas de Laplace […]"

**Corrección propuesta.** Agregar una observación, en la celda 8 o al final de la 1.4:

> **Observación sobre la fricción de Coulomb.** $\frac{\partial}{\partial\omega}\operatorname{sign}(\omega) = 0$ para $\omega\neq 0$ y no existe en $\omega=0$. Por lo tanto:
> 1. Para $\omega\neq 0$, el término $\tau_c\operatorname{sign}(\omega)$ es la constante $\pm\tau_c$, y el modelo es **afín por tramos**. La única no linealidad es el **salto en $\omega=0$**, y ahí el sistema **no se puede linealizar**.
> 2. El análisis de estabilidad con $J_{\mathbf f}$ vale por tramos ($\omega>0$ y $\omega<0$).
> 3. Para $\omega \neq 0$, con estado $\mathbf y=[i,\ \omega,\ \theta]^T$, el Jacobiano del motor es
> $$J_{\mathbf f} = \begin{pmatrix} -\dfrac{R}{L} & -\dfrac{K_e}{L} & 0 \\[6pt] \dfrac{K_t}{J_m} & -\dfrac{b}{J_m} & 0 \\[6pt] 0 & 1 & 0 \end{pmatrix}.$$
>    Un valor propio es $\lambda=0$, que viene de $\theta$: con él, $|1+h\cdot 0|=1$ y el error en $\theta$ ni crece ni decae. Los otros dos son los valores propios del bloque $2\times 2$ superior. Como la constante de tiempo eléctrica $L/R$ suele ser mucho menor que la mecánica $J_m/b$, el sistema tiende a ser **rígido** (*stiff*), y el valor propio rápido (cercano a $-R/L$) es el que limita el paso $h$.
> 4. Cuando el motor debería quedarse detenido ($\omega=0$ con $|K_t i - \tau_{carga}| < \tau_c$), Euler hace que $\omega$ oscile alrededor de cero (*chattering*) con amplitud del orden de $h\tau_c/J_m$. Una alternativa habitual es regularizar con $\operatorname{sign}(\omega)\approx\tanh(\omega/\varepsilon)$.

**Justificación:**
El análisis de la 1.4 supone que $\mathbf f$ es diferenciable, y eso no se cumple en $\omega=0$. La observación delimita cuándo vale el análisis, deja listo el Jacobiano del motor para la parte numérica y anticipa un comportamiento que va a aparecer en las simulaciones.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Mmmmm alrededor de un punto de operación, sí se puede. Sin embargo, tiene un punto. Esto anticipa un comportamiento y no considera el más general de los casos, que es el focus de este proyecto.

&nbsp;

---

## 🟡 Forma: notación, terminología, LaTeX y redacción

<a id="c-09"></a>
### C-09 · $1$ en lugar de la matriz identidad $I$

**Ubicación:** Sección 1.2 (celda 11) y sección 1.4 (celda 12, dos veces).

| Original | Propuesta |
|----------|-----------|
| $(1 + hJ)\mathbf{y}_k$ | $(I + hA)\mathbf{y}_k$ (caso lineal, ver C-02) |
| $(1 + hJ)\mathbf{e}_k$ | $(I + hJ_k)\mathbf{e}_k$ |
| "factor de amplificación $(1+hJ)$" | "matriz de amplificación $(I+hJ_k)$" |

**Justificación:** $J$ es una matriz $N\times N$, así que no se le puede sumar el escalar $1$. Lo correcto es la identidad $I_N$.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Decisión puramente estética. Aprobada.

&nbsp;

---

<a id="c-10"></a>
### C-10 · "Variable independiente" donde va "dependiente"

**Ubicación y cambios:**

| Sección | Texto original | Propuesta |
|---------|----------------|-----------|
| 1.1 | "son los valores de la variable **independiente** evaluados en los límites…" | "son los valores de la variable **dependiente**…" |
| 1.2 | "aproxime la derivada de cada variable **independiente** en el sistema" | "…de cada variable **dependiente**…" |
| 1.2 | "y por cada variable **independiente**:" | "y por cada variable **dependiente**:" |
| 1.3 | "una derivada de orden superior de una variable **independiente**" | "…de una variable **dependiente**" |
| 1.3 | "la variable $y_i$ […] tiene una derivada de orden $j$-esimo" | (sin cambio de término; ver C-13) |

**Justificación:** $y$ (o $y_i$) es la variable **dependiente**, la incógnita que depende de $t$; $t$ (o $x$) es la independiente. La frase de la 1.2 "dependientes de la misma variable independiente $t$" está bien y no se cambia.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Decisión puramente estética, aprobada sin más comentarios.

&nbsp;

---

<a id="c-11"></a>
### C-11 · Punto de evaluación de $f$ y notación de $y_k$

**Ubicación:** Sección 1.1, celda 10.

| Original | Propuesta |
|----------|-----------|
| "para aproximar la derivada en el rango $x \in [x_k, x_{k+1}]$" | "para aproximar la derivada **en $t_k$** usando el intervalo $[t_k, t_{k+1}]$" |
| "Donde $y_{k+1} = y(x_{k+1})$ y $y_{k} = y(x_{k})$ son los valores…" | "Donde $y_k \approx y(t_k)$ denota la **aproximación numérica** de la solución en $t_k$" |
| $\frac{y_{k+1} - y_k}{h}\approx f(x,y)$ | $\frac{y_{k+1} - y_k}{h}\approx f(t_k,y_k)$ |

**Justificación:**
- Evaluar $f$ en el extremo **izquierdo** $(t_k, y_k)$ es lo que hace que el método sea **explícito**. Evaluarla en $(t_{k+1},y_{k+1})$ da Euler implícito. Hay que dejarlo escrito.
- Si $y_k$ se define como el valor exacto $y(t_k)$, la fórmula de Euler parece exacta. La sección 1.4 sí distingue $\mathbf Y$ (exacta) de $\mathbf y$ (aproximada); conviene adoptar esa convención desde la 1.1.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Corrección sobre terminología del método de Euler. Decisiones de redacción que hacen más claro entender cuál es la solución exacta y cuál es la solución numérica.

&nbsp;

---

<a id="c-12"></a>
### C-12 · Uso mezclado de $x$ y $t$

**Ubicación:** 1.1 usa $x$; 1.2 empieza con $x$, pasa a $t$ ("dependientes de la misma variable independiente $t$", "$\frac{dy_1}{dt}$") y vuelve a $x_k$; 1.4 usa $x_k$; el modelo del motor usa $t$.

**Corrección propuesta:** Usar $t$ en todo el documento: $t_k = t_0 + kh$, $\mathbf f(t,\mathbf y)$, $\mathbf Y(t_k)$.

**Justificación:** Consistencia con el modelo físico, donde la variable independiente es el tiempo, y menos confusión al leer.

**Decisión:** [ ] Aprobada [ ] Aprobada con cambios [X] Rechazada
**Comentario del revisor:** Pendiente de revisión. El uso de variables x e y es únicamente para fines demostrativos. Es lo común en la literatura del tema y por lo tanto, cambiar todas las demostraciones generales a una variable t puede resultar incómodo para ciertos lectores. Rechazada.

&nbsp;

---

<a id="c-13"></a>
### C-13 · Notación de conjunto y número de EDOs equivalentes

**Ubicación:** Sección 1.3, celda 11.

| Original | Propuesta |
|----------|-----------|
| "$i\in \mathbb{N} \mid 1 \leq i \leq N$ (revisar notación de conjunto)" | "$i \in \{1, 2, \dots, N\}$" |
| "orden $j$-esimo" | "orden $j$-ésimo" |
| "estas EDOs se descomponen en **al menos** tantas EDOs de primer orden como el orden de su derivada más alta" | "una EDO de orden $n$ se convierte en **exactamente** $n$ EDOs de primer orden, usando $u_1 = y,\ u_2 = y',\ \dots,\ u_n = y^{(n-1)}$" |

**Sugerencia opcional:** agregar al final de la 1.3 que el modelo del motor ya está en forma de primer orden con estado $\mathbf y = [i,\ \omega,\ \theta]^T$. La ecuación $\theta' = \omega$ es justamente la reducción de orden de $J_m\theta'' = \dots$.

**Nota:** el ejemplo $y''=y'-1 \Rightarrow u_1'=u_2,\ u_2'=u_2-1$ está **correcto**.

**Justificación:** La barra $\mid$ solo tiene sentido dentro de llaves, como en $\{i\in\mathbb N \mid 1\le i\le N\}$. Y la reducción de orden da un número **exacto** de ecuaciones, no una cota inferior.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Hasta yo mismo tenía dudas al respecto y puse el prompt escondido para que Claude lo corrija. Totalmente aprobado

&nbsp;

---

<a id="c-14"></a>
### C-14 · LaTeX que no compila o se ve mal

| Celda | Problema | Propuesta |
|-------|----------|-----------|
| 7 | `$\tau_{carga}$ - Torque de carga [$N*m]`: falta el `$` de cierre | `[$\text{N}\cdot\text{m}$]` |
| 7 | Unidades con `*`: `$kg * m^2$`, `$(N*m)/A$`, `$(N*m)/(rad/s)$` | `$\text{kg}\cdot\text{m}^2$`, `$\text{N}\cdot\text{m}/\text{A}$`, `$\text{N}\cdot\text{m}\cdot\text{s}/\text{rad}$` |
| 11 | En el `cases` del sistema falta `\\` después de `\vdots`, así que $\vdots$ y la ecuación de $y_N'$ quedan en la misma línea | `\vdots \\` |
| 11 | `\begin{align}` dentro de `$$…$$` da error en algunos renderizadores; además faltan los `&` | `$$\begin{aligned} (y_1)_{k+1} &= \dots \\ \end{aligned}$$` |
| 6, 11 | `\textbf{y}` para vectores | Opcional: `\mathbf{y}`, que es la forma estándar en modo matemático |

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Arreglen esa cosa, corrección estética.

&nbsp;

---

<a id="c-15"></a>
### C-15 · Referencia a Nise incompleta

**Ubicación:** Celdas 7 y 8.

**Texto original:**
> "Para más información, vease Nise (AGREGAR REFERENCIA POR FAVOR, capítulo 4 no recuerdo donde estaba)"
>
> "A diferencia del modelo lineal presentado en Nise (no sé, no sé, no sé) […]"

**Corrección propuesta:**

Celda 7:
> "Para más información, véase N. S. Nise, *Control Systems Engineering*, 7.ª ed., Wiley, 2015, cap. 2, §2.8, pp. 77–83."

Celda 8:
> "A diferencia del modelo lineal presentado en Nise [1, §2.8], que considera solo fricción viscosa [1, p. 65, nota 8], …"

Además, agregar al cuaderno una sección **Referencias** con la entrada completa:
> [1] N. S. Nise, *Control Systems Engineering*, 7th ed. Hoboken, NJ, USA: John Wiley & Sons, 2015.

**Justificación:** ✅ **Verificada el 22/11/2026** con el PDF de la 7.ª edición que tiene el equipo:
- El modelo del servomotor DC controlado por armadura está en el **capítulo 2, §2.8 "Electromechanical System Transfer Functions", pp. 77–83**, no en el capítulo 4. El capítulo 4 es *Time Response*.
- La nota al pie 8 (p. 65) aclara que la fricción en todo el libro es viscosa, no de Coulomb. Eso confirma que el modelo de Nise es lineal, como dice la celda 8.
- Las secciones §2.10 *Nonlinearities* (pp. 86–87) y §2.11 *Linearization* (p. 87 en adelante) sustentan la discusión de la celda 8 sobre la no linealidad y la linealización.

El detalle completo, con ISBN, formatos IEEE y APA y la tabla de equivalencias de notación, está en [`Referencias.md`](Referencias.md).

**Decisión:** [ ] Aprobada [ ] Aprobada con cambios [X] Rechazada
**Comentario del revisor:** Ya corregida con nuevo commit. Yo puse el capítulo 4 porque fue como recorde donde vi el análisis de sistemas electromecánicos. Cabe aclarar que este análisis asume que el sistema es puramente lineal, cosa que no es cierta en este sistema. La referencia de Nise se utiliza únicamente para comparar el modelo con un modelo lineal ya estudiado con anterioridad, pero no puede ser utilizado como base para el proyecto. En caso contrario, se asume que el sistema es lineal cuando no lo es necesariamente.

&nbsp;

---

<a id="c-16"></a>
### C-16 · Ortografía y redacción

| Celda | Original | Propuesta |
|-------|----------|-----------|
| 7 | "vease" | "véase" |
| 7 | "Henries, H" | "henrios, H" (forma en español; "henries" es la inglesa) |
| 11 | "si recuerda que la derivar una función vectorial" | "si recuerda que derivar una función vectorial" |
| 11 | "orden $j$-esimo" | "orden $j$-ésimo" (también en C-13) |
| 8 | "este es un curso de métodos numéricos y no un curso de cómo aproximar cosas" | Opcional: "el objetivo no es simplificar el modelo, sino resolverlo numéricamente tal cual". La frase original suena contradictoria, porque los métodos numéricos también aproximan |
| 4 | "Elemento de lista" (texto de plantilla en el historial) | Eliminar o reemplazar por una entrada real |
| 3 | "Pongan sus nombres y (carnets)" | Completar con los integrantes |

**Observación física opcional:** en unidades SI, $K_e$ (V·s/rad) y $K_t$ (N·m/A) son numéricamente iguales para un motor ideal. Sirve para verificar los parámetros del JGA25-370. Nise afirma lo mismo para $K_t$ y $K_b$ en un sistema de unidades consistente [Nise 2015, §2.8, p. 79]; él llama $K_b$ a lo que el cuaderno llama $K_e$.

**Decisión:** [X] Aprobada [ ] Aprobada con cambios [ ] Rechazada
**Comentario del revisor:** Arreglar.

&nbsp;

---

## Lo que está correcto

Para que quede registro, estas partes no necesitan cambios de fondo:
- La deducción de Euler explícito para una EDO (1.1), salvo la notación de C-11.
- Las fórmulas de Euler componente a componente (1.2).
- El ejemplo de reducción de orden $y''=y'-1$ (1.3).
- La estructura de la deducción de estabilidad (1.4): Taylor → resta → recurrencia del error → matriz de amplificación. La recurrencia final $\mathbf e_{k+1}\approx(I+hJ)\mathbf e_k$ es correcta como aproximación linealizada, con las salvedades de C-05 y C-06.

---

## Resumen de decisiones

Para llenar al terminar la revisión.

| ID | Aprobada | Con cambios | Rechazada | Aplicada al cuaderno (commit) |
|----|:--------:|:-----------:|:---------:|-------------------------------|
| C-01 | | | | |
| C-02 | | | | |
| C-03 | | | | |
| C-04 | | | | |
| C-05 | | | | |
| C-06 | | | | |
| C-07 | | | | |
| C-08 | | | | |
| C-09 | | | | |
| C-10 | | | | |
| C-11 | | | | |
| C-12 | | | | |
| C-13 | | | | |
| C-14 | | | | |
| C-15 | | | | |
| C-16 | | | | |

Le voy a pedir a Claude que la llene por mí con las observaciones que puse antes.

---

## Observaciones del revisor

Espacio para que cada revisor anote observaciones generales, desacuerdos con la propuesta, errores que la IA no detectó o cambios adicionales.

**Revisor:** Mario Alejandro Betancourt Franco **Fecha:** 22/11/2026

**Observaciones:** Correcciones importantes sobre el uso de Jacobianos en el análisis del método de Euler para sistemas de ecuaciones diferenciales ordinarias. Correcciones sobre typos pequeños, redacción, entre otras cosas. Los cambios sobre el desarrollo matemático fueron revisados y autorizados por mi persona. Yo traté de dar mi interpretación sobre las propuestas antes de ejecutarlas. Le pediré a Claude que haga los cambios. Entendí que cambiará el Jacobiano de la sección 1.2 por el campo vectorial, y dejará el jacobiano donde estaba en el análisis de estabilidad, corrigiendo también ahi una igualdad por una aproximacióm. 

&nbsp;

&nbsp;

&nbsp;

---

**Revisor:** ______________________________ **Fecha:** ______________

**Observaciones:**

&nbsp;

&nbsp;

&nbsp;

---

**Revisor:** ______________________________ **Fecha:** ______________

**Observaciones:**

&nbsp;

&nbsp;

&nbsp;

---

**Aprobación final del equipo** (cuando todas las correcciones tengan una decisión):

Quiero quitar esta parte, no necesito la aprobación de otros para hacer estos cambios. Estos quedan documentados y hay flexibilidad para que ellos revisen y hagan más cambios.
