* ---------------------------------------------------------------------------
* Ensayo de escalon: el pin del Arduino da un pulso de 0.1 ms a 1.1 ms.
* ---------------------------------------------------------------------------
.tran 0 2.5m 0 0.5u
.meas tran Id_antes FIND I(Lm) AT=90u
.meas tran Id_pulso FIND I(Lm) AT=1m
.meas tran Vgs_pulso FIND V(g) AT=1m
.meas tran Vds_pulso FIND V(dr) AT=1m
.meas tran P_Q1_pulso AVG V(dr)*Id(M1) FROM=0.9m TO=1m
.meas tran Id_final FIND I(Lm) AT=2.4m
.meas tran Vgs_final FIND V(g) AT=2.4m
.meas tran ID1_pico MAX I(D1) FROM=0 TO=2.5m
