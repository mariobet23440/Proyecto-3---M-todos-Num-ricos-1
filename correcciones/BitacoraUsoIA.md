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
  - El detalle está en [`Correcciones_DesarrolloMatematico_2026-11-21.md`](Correcciones_DesarrolloMatematico_2026-11-21.md) (ver Entrada 2).
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
- **Documento de correcciones.** Creó [`correcciones/Correcciones_DesarrolloMatematico_2026-11-21.md`](Correcciones_DesarrolloMatematico_2026-11-21.md), con:
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
