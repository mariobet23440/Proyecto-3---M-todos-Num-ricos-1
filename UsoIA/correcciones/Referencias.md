# Referencias

Bibliografía que respalda las correcciones propuestas en [`Correcciones_DesarrolloMatematico_2026-11-21.md`](Correcciones_DesarrolloMatematico_2026-11-21.md).

> El PDF del libro **no se sube al repositorio** porque está protegido por derechos de autor. Aquí solo se citan la referencia y las páginas.

---

## [1] Nise — *Control Systems Engineering*

**Formato IEEE:**

> N. S. Nise, *Control Systems Engineering*, 7th ed. Hoboken, NJ, USA: John Wiley & Sons, 2015.

**Formato APA (7.ª ed.):**

> Nise, N. S. (2015). *Control systems engineering* (7th ed.). John Wiley & Sons.

| Dato | Valor |
|------|-------|
| Autor | Norman S. Nise (California State Polytechnic University, Pomona) |
| Edición | Séptima (7.ª) |
| Editorial | John Wiley & Sons, Inc., Hoboken, NJ |
| Año | 2015 |
| ISBN (impreso) | 978-1-118-17051-9 |
| ISBN (PDF) | 978-1-118-80082-9 |

Los datos de edición, año e ISBN se tomaron de la página legal del PDF que tiene el equipo.

### Secciones relevantes para el proyecto

Páginas según la numeración impresa del libro. En el PDF, la página del archivo es la página impresa + 20; por ejemplo, la p. 77 es la página 97 del PDF.

| Sección | Páginas | Qué contiene | Para qué sirve en el proyecto |
|---------|---------|--------------|-------------------------------|
| Cap. 2, §2.8 *Electromechanical System Transfer Functions* | 77–83 | Modelo del **servomotor DC controlado por armadura**: fuerza contraelectromotriz $v_b = K_b\,\dot\theta_m$ (Ec. 2.144), ecuación de malla de la armadura (Ec. 2.146), torque $T_m = K_t\,i_a$ (Ec. 2.147), carga mecánica $J_m$, $D_m$ (Fig. 2.36) y función de transferencia del motor | Es la referencia del modelo de la Introducción (celdas 7 y 8). Corrige "capítulo 4" → **capítulo 2, §2.8** |
| Cap. 2, §2.8, p. 79 | 79 | El libro afirma que, en un sistema de unidades consistente, $K_t$ y $K_b$ tienen el mismo valor | Respalda la observación física de C-16 ($K_e = K_t$ en SI) |
| Cap. 2, nota al pie 8 | 65 | Aclara que la fricción en todo el libro es **viscosa**, no de Coulomb, salvo que se indique otra cosa | Respalda que el modelo de Nise es **lineal** y que la fricción de Coulomb del proyecto es una extensión (celda 8, C-08) |
| Cap. 2, §2.10 *Nonlinearities* | 86–87 | Definición de sistema lineal (superposición y homogeneidad) y ejemplos de no linealidades físicas, como la **zona muerta** de un motor por fricción (Fig. 2.46) | Sustenta que el término $\tau_c\operatorname{sign}(\omega)$ es una no linealidad (celda 8, C-08) |
| Cap. 2, §2.11 *Linearization* | 87 en adelante | Linealización alrededor de un punto de equilibrio con series de Taylor (Ec. 2.181–2.183) | Sustenta la discusión de la celda 8 sobre linealizar el sistema, y por qué no se puede hacer en $\omega = 0$, donde $\operatorname{sign}$ no es diferenciable (C-08) |

### Diferencias de notación entre Nise y el cuaderno

| Cantidad | Nise (§2.8) | Cuaderno | Comentario |
|----------|-------------|----------|------------|
| Corriente de armadura | $i_a$ | $i$ | — |
| Voltaje aplicado | $e_a$ | $V$ | — |
| Resistencia / inductancia de armadura | $R_a$, $L_a$ | $R$, $L$ | — |
| Constante de fuerza contraelectromotriz | $K_b$ | $K_e$ | Misma cantidad, distinto nombre |
| Constante de torque | $K_t$ | $K_t$ | — |
| Inercia equivalente | $J_m$ | $J$ | Nise usa $J_m$; eso respalda la propuesta C-03 de no usar $J$ solo |
| Amortiguamiento viscoso | $D_m$ | $b$ | — |
| Posición / velocidad angular | $\theta_m$, $\dot\theta_m$ | $\theta$, $\omega$ | — |
| Fricción de Coulomb | (no se incluye) | $\tau_c\operatorname{sign}(\omega)$ | Extensión no lineal del proyecto |

### Cita sugerida para el cuaderno

Para reemplazar los textos pendientes de las celdas 7 y 8:

> Para más información, véase N. S. Nise, *Control Systems Engineering*, 7.ª ed., Wiley, 2015, cap. 2, §2.8, pp. 77–83.

> A diferencia del modelo lineal presentado en Nise [1, §2.8], que considera solo fricción viscosa [1, p. 65, nota 8], …

> ⚠️ Estas citas son **propuestas** (ver C-15). Las aplica el equipo después de aprobarlas.
