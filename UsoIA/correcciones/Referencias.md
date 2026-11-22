# Referencias

Referencia bibliográfica del **modelo del motor DC** que el cuaderno cita en la Introducción (celdas 7 y 8). Sirve para completar esa cita, que es la corrección C-15 de [`Correcciones_DesarrolloMatematico_2026-11-21.md`](Correcciones_DesarrolloMatematico_2026-11-21.md).

> **Fe de erratas (22/11/2026).** Una versión anterior de este archivo decía que esta bibliografía *respaldaba las correcciones propuestas*. **Eso era incorrecto.** Las correcciones C-01 a C-14 tratan de métodos numéricos (el método de Euler para sistemas, el Jacobiano, la estabilidad numérica y la notación matemática), y el libro de Nise no cubre esos temas. Tampoco respalda C-03 ni C-16, aunque la versión anterior lo afirmaba. Ver la Entrada 4 de [`BitacoraUsoIA.md`](../BitacoraUsoIA.md).

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

### Dónde está lo que cita el cuaderno

Páginas según la numeración impresa del libro. En el PDF, la página del archivo es la página impresa + 20.

| Lo que cita el cuaderno | Ubicación en el libro |
|-------------------------|-----------------------|
| Celda 7: modelo del motor DC controlado por armadura ("capítulo 4 no recuerdo donde estaba") | Cap. 2, §2.8 *Electromechanical System Transfer Functions*, pp. 77–83. **No está en el capítulo 4**, que es *Time Response* |
| Celda 8: "el modelo lineal presentado en Nise" | Cap. 2, §2.8, pp. 77–83 |

### Diferencias de notación entre Nise y el cuaderno

Solo como guía de lectura del libro.

| Cantidad | Nise (§2.8) | Cuaderno |
|----------|-------------|----------|
| Corriente de armadura | $i_a$ | $i$ |
| Voltaje aplicado | $e_a$ | $V$ |
| Resistencia / inductancia de armadura | $R_a$, $L_a$ | $R$, $L$ |
| Constante de fuerza contraelectromotriz | $K_b$ | $K_e$ |
| Constante de torque | $K_t$ | $K_t$ |
| Inercia equivalente | $J_m$ | $J$ |
| Amortiguamiento viscoso | $D_m$ | $b$ |
| Posición / velocidad angular | $\theta_m$, $\dot\theta_m$ | $\theta$, $\omega$ |

### Cita sugerida para el cuaderno

Para reemplazar los textos pendientes de las celdas 7 y 8 (ver C-15):

> Para más información, véase N. S. Nise, *Control Systems Engineering*, 7.ª ed., Wiley, 2015, cap. 2, §2.8, pp. 77–83.

> A diferencia del modelo lineal presentado en Nise [1, §2.8], …

> ⚠️ Estas citas son **propuestas**. Las aplica el equipo después de aprobarlas.
