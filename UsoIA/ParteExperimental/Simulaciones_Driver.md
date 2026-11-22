# Driver del motor: análisis y simulaciones LTspice

> [!NOTE]
> **Simulaciones retiradas el 22/11/2026.** El autor cambió el driver MOSFET por un L298N y pidió
> quitar las simulaciones (Entrada 13 de la bitácora). La carpeta `ParteExperimental/Simulaciones/`
> se borró del repositorio; sigue en el historial de git (commit `7ed3b88` y anteriores). Este documento
> se conserva como registro del uso de IA; sus enlaces a esa carpeta ya no funcionan.

| Campo | Detalle |
|-------|---------|
| **Fecha** | 22/11/2026 |
| **Autores** | Mario Alejandro Betancourt Franco (23440) · Claude Opus 5.5 (Anthropic), asistente de IA |
| **Resultado técnico** | [`ParteExperimental/Simulaciones/ReporteSimulaciones.md`](../../ParteExperimental/Simulaciones/ReporteSimulaciones.md) |
| **Bitácora** | [`BitacoraUsoIA.md`](../BitacoraUsoIA.md), Entrada 7 |

> [!WARNING]
> **Aviso sobre el uso de IA.** El análisis, las simulaciones, el modelo SPICE del diodo 1N540X y el
> script los generó una herramienta de IA a pedido del autor. Dependen de valores supuestos, como la
> inductancia del motor y el t<sub>rr</sub> del diodo, y no se han comparado con mediciones reales.
> La decisión de diseño la tomó el autor.

---

## Prompts originales

Se copian textualmente, en el orden en que se enviaron el 22/11/2026. Se omiten los mensajes que solo pedían pausar o reanudar el trabajo.

**1. Pin con PWM y etapa de 12 V:**
```text
Tengo una pequeña corrección sobre el esquemático. Me gustaría utilizar un pin del Arduino nano que tenga funcionalidad PWM para la entrada del driver del motor. 

También quisiera que recomienda un circuito de acondicionamiento de señal (quizás otra etapa de un switch con un transistor de gama más baja) para conertir la señal lógica de 0-5V del Arduino Nano en una señal de 0-12 V necesarios para saturar el MOSFET. Considera utilizar un BJT NPN como el 2N3904. Argumentame si este diseño es adecuado o no.

Si el diseño es adecuado, procede con las correcciones sobre el esquemático
```

**2. Simulaciones en GitHub:**
```text
Ya que tienes LTSpice. Quisiera que agregues tus simulaciones al Github. Si no existen modelos para los transistores que hacen falta, busca transistores similares o crea modelos SPICE con hojas de datos de los dispositivos.
```

**3. Driver disponible:**
```text
Tengo un driver de mosfet
Driver de mosfet IR2153PBF
```

**4. Respuesta de otra IA:** el autor pegó una respuesta del asistente de IA de Google sobre el uso del IRFZ44N con 5 V en la compuerta. No se reproduce aquí porque es texto de otra herramienta. En resumen: el IRFZ44N funciona con 5 V para cargas de menos de 1–2 A, no es de nivel lógico, y para corrientes mayores o PWM recomienda un IRLZ44N o un transistor auxiliar (2N2222) que lleve la compuerta a 12 V.

**5.**
```text
Lo que propones es un circuito push-pull?
```

**6.** Se adjuntó el PDF *"IE3036 - Esquemático Circuito Push Pull"*, un amplificador push-pull lineal (TL081, 2N3904/2N3906 y TIP120/TIP125) de un proyecto anterior del curso Sistemas de Control 1:
```text
Sabes de hecho hice un proyecto exactamente así en sistemas de control y usamos este esqeumático para un motor TT. El uso de un op amp ayudó a que los transistores produjeran una salida lineal. No tendría que hacer control PWM y perfectamente podría replicarlo. Ya lo tengo en una proto jajaja
```

**7.**
```text
Mmmmmmmmmmmm pero recorde que el arduino no tiene DAC y el ESP32 tiene malos ADCs
```

**8.**
```text
Y que tal un controlador PWM. Creo que son más comunes en la práctica
```

**9.**
```text
Como que mi compuerta está mal manejada
```

**10.**
```text
La corriente se mantiene en un rango debajo de 2 A
```

**11.**
```text
Procede entonces. Dale bro
```

**12.**
```text
Por favor genera un reporte con las formas de onda que obtuviste en LTSpice
```

## Resumen de la discusión y de la decisión

| Opción evaluada | Conclusión |
|-----------------|------------|
| Un NPN (2N3904) como inversor para llevar la compuerta a 12 V | **No adecuada:** invierte la señal y enciende el motor cuando el pin está en 0 V o flotando (reset, carga del programa) |
| NPN 2N3904 + PNP 2N3906 (no inversor) | Funciona y es segura, pero apaga 30 veces más lento que la conexión directa. No es un push-pull: solo tiene un lado activo |
| IR2153PBF | **No adecuado:** es un driver de medio puente auto-oscilante, con ciclo de trabajo fijo de ~50 % y sin entrada lógica. No puede mantener el MOSFET encendido ni seguir un PWM (verificado en su hoja de datos) |
| Push-pull lineal con op amp (proyecto de IE3036) | Viable, pero necesita DAC o PWM filtrado, disipador y ganancia; además, "apagar" pasa a ser frenar con 0 V, no desconectar |
| Puente H PWM en módulo (TB6612FNG, DRV8871, …) | Opción habitual en la práctica; queda como alternativa para el PID |
| **5 V directo a la compuerta (diseño original del autor)** | **Elegido.** Con menos de 2 A conduce bien en el ensayo de escalón. El driver pasa a D9 para tener PWM |

## Modelos SPICE

- **2N3904, 2N3906, IRFZ44N y MBRS340:** copiados de la librería estándar de LTspice (`modelos/transistores_ltspice.lib`), con su fabricante indicado.
- **1N540X:** LTspice no lo trae, así que la IA lo **creó** con la hoja de datos de Vishay (documento 88516), como pidió el autor:
  - la curva típica de directa (puntos leídos de la gráfica);
  - la capacitancia de unión (tabla y gráfica);
  - la corriente inversa.

  Se verificó en LTspice contra esos datos (figura 5 del reporte). El t<sub>rr</sub> no está especificado en la hoja, así que se **supuso** T<sub>T</sub> = 3 µs.

## Correcciones de la IA durante esta parte

- **"Mal manejada" (en el chat).** La IA dijo que la compuerta del circuito original estaba "mal manejada". Fue una exageración: el diseño (180 Ω y 10 kΩ) es correcto y seguro. Su única limitación es el margen de V<sub>GS</sub>, que con menos de 2 A no es un problema.
- **Pérdidas con PWM (en el chat).** La IA estimó "unas décimas de watt" a 20 kHz sin simular. La simulación dio entre 0,9 y 1,8 W, así que con PWM a 20 kHz se necesita disipador.
- **Error en una medición.** Una primera versión calculaba la potencia del MOSFET con la corriente del motor, que durante el apagado circula por el diodo. Dio 5,9 W, un valor falso. Se corrigió antes de publicar los resultados.
- **Netlist de capacitancia.** El primer netlist daba un resultado sin sentido porque la fuente y el parámetro se llamaban igual. Se rehízo sin `.step`.
