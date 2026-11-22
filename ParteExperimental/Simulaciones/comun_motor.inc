* ---------------------------------------------------------------------------
* Parte comun: bus de 12 V, motor y diodo de rueda libre.
* El motor se aproxima como R-L con el rotor detenido (sin fuerza
* contraelectromotriz), que es el caso de mayor corriente.
*   Rmotor = 6 ohm  -> 12 V / 6 ohm = 2 A. El autor indico que la corriente del
*                      motor se mantiene por debajo de 2 A: es el peor caso.
*   Lmotor = 2 mH   -> VALOR SUPUESTO. Reemplazar por el que se identifique en
*                      el ensayo de escalon.
* El ACS712 (1.2 mOhm) se desprecia.
* ---------------------------------------------------------------------------
.param Rmotor=6 Lmotor=2m
V12 vbus 0 12
Rm vbus m1 {Rmotor}
Lm m1 dr {Lmotor}
D1 dr vbus 1N540X
.include modelos/transistores_ltspice.lib
.include modelos/1N540X.lib
.options plotwinsize=0
