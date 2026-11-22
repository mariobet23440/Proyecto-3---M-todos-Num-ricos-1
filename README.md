# Motor DC — Gemelo digital y control PID

Proyecto 3 del curso **Métodos Numéricos 1**, Universidad del Valle de Guatemala.

Simulación numérica del modelo no lineal de un motor DC controlado por armadura (JGA25-370), incluida la fricción de Coulomb, y ensayo experimental de su respuesta al escalón:

$$
\begin{cases}
L\,\dfrac{di}{dt} = V - R\,i - K_e\,\omega \\[4pt]
J_m\,\dfrac{d\omega}{dt} = K_t\,i - b\,\omega - \tau_c\,\operatorname{sign}(\omega) - \tau_{carga} \\[4pt]
\dfrac{d\theta}{dt} = \omega
\end{cases}
$$

## Abrir el cuaderno

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mariobet23440/Proyecto-3---M-todos-Num-ricos-1/blob/main/Proyecto3MetodosNumericos.ipynb)

## Estructura del repositorio

```
.
├── Proyecto3MetodosNumericos.ipynb        # Cuaderno principal (teoría + código)
├── Animaciones/                           # GIF didácticos del cuaderno (generados con IA)
├── ParteExperimental/
│   ├── MotorDC_L298N/
│   │   └── MotorDC_L298N.ino              # Arduino Nano + L298N: captura rápida y PID
│   ├── protocolo_motor.py                 # Protocolo serie (contraparte del .ino)
│   ├── captura_respuesta.py               # Receptor: datos brutos de la captura rápida
│   ├── postprocesamiento.py               # Posición, velocidad y corriente
│   ├── modelo_motor.py                    # Modelo del motor (Euler y RK4) para el gemelo
│   ├── arduino_simulado.py                # Arduino simulado para probar sin hardware
│   ├── GemeloDigital/                     # Aplicación de escritorio (customtkinter)
│   │   ├── app.py                         # python app.py
│   │   ├── MANUAL.md                      # Manual de uso (cómo capturar datos)
│   │   ├── estilo.py, pixel.py, graficas.py
│   │   └── fuentes/                       # Fuentes pixeladas (ver LEEME.md)
│   ├── Esquematico_MotorDC.svg            # Esquemático del circuito anterior (driver MOSFET)
│   └── Simulaciones/                      # Simulaciones LTspice del driver del motor
│       ├── ReporteSimulaciones.md         # Reporte con las formas de onda
│       ├── correr_simulaciones.py         # Corre LTspice y genera las figuras
│       ├── *.cir, *.inc, modelos/         # Netlists y modelos SPICE
│       └── figuras/
├── UsoIA/
│   ├── BitacoraUsoIA.md                   # Registro del uso de herramientas de IA
│   ├── correcciones/                      # Revisión del desarrollo matemático
│   ├── redacciones/                       # Textos del cuaderno redactados con IA (con sus prompts)
│   └── ParteExperimental/                 # Prompts y documentación de la parte experimental
├── README.md
├── LICENSE                                # MIT
├── .gitattributes
└── .gitignore
```

> El cuaderno se queda en la raíz a propósito. El botón de Colab y la opción
> *Archivo → Guardar una copia en GitHub* usan esa ruta. Si se mueve, hay que
> actualizar el enlace de la primera celda y elegir la nueva ruta al guardar desde Colab.

## Autores

- Mario Alejandro Betancourt Franco (23440)
- *(agregar integrantes)*

Parte del trabajo se hizo con asistencia de IA; está registrado en [`UsoIA/BitacoraUsoIA.md`](UsoIA/BitacoraUsoIA.md).

## Licencia

MIT. Ver [LICENSE](LICENSE).
