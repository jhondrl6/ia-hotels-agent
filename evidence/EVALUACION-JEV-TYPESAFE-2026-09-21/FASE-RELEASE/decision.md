# Decision del piloto JEV - EVALUACION-JEV-TYPESAFE-2026-09-21

- Emisor: scripts/evaluate_jev_pilot.py decide, sobre el informe de scripts/evaluate_jev_pilot.py report
- Fecha: 2026-10-05
- `run_status`: **INCOMPLETO**
- `decision`: **null**
- Estado: propuesto por el runner, **pendiente de revision del operador** (AC5).

## Criterios congelados, aplicados sin releerse

| Criterio | Umbral | Medido | Estado |
|---|---|---|---|
| cobertura_min | 0.95 | capa_fria=0.5; jev=0.5; deepseek=0.5 | NO CUMPLE |
| suficiencia_minima | 0.5 | 0.5 (2/4) | CUMPLE |
| margen_vs_deepseek | 0.25 | 0.0 | NO-EVALUABLE |
| latencia_max | 30000 | jev=395.794; deepseek=1392.648 | CUMPLE |

## Los cuatro literales

- **COSTE-NO-PAGADO**: BLOQUEADO - `usd` null en el protocolo congelado, fuera de gobernanza por decision del operador: no hay decision de coste sin coste en gobernanza
- **MUESTRA-INSUFICIENTE**: EXCLUIDA por la regla congelada; ponible por el operador - suficiencia_minima se cumple (0.5 >= 0.5) en el denominador congelado, pero el denominador efectivo de la comparacion es 1 par(es) con eleccion utilizable en los dos brazos
- **ACTIVAR**: EXCLUIDA por medicion - cobertura_min 0.95 contra 0.5 medido en el brazo sujeto
- **RECHAZAR**: NO EMITIDA - gobernaria el margen extremo_a_extremo, que es NO-EVALUABLE, y la pata Jev tuvo un fallo operativo

## Por que `decision = null`

- hubo un fallo operativo en la pata de inferencia: un fallo operativo nunca es RECHAZAR (AC5)
- criterios pre-registrados NO-EVALUABLE: margen_vs_deepseek; ACTIVAR y RECHAZAR requieren magnitud medida, asi que el emisor no elige y deja las bases para el operador

## Cocientes por brazo (denominadores separados)

| Brazo | recuperacion | precision_entre_propuestas | recall_importante_candidatos | extremo_a_extremo |
|---|---|---|---|---|
| capa_fria | 0.5 (1/2) | NO-EVALUABLE | 1.0 (1/1) | 0.5 (1/2) |
| jev | 0.5 (1/2) | 1.0 (1/1) | 1.0 (1/1) | 0.5 (1/2) |
| deepseek | 0.5 (1/2) | 1.0 (1/1) | 1.0 (1/1) | 0.5 (1/2) |

## Separacion de decisiones (AC7)

- `jev_recommendation`: NO EMITIDA: el emisor no elige sin los criterios evaluables
- `d6_eligibility`: NO ELEGIBLE
- `transfer_status`: PENDIENTE - la deuda del hermano solo se mueve con instruccion literal del operador que nombre archivos y alcance, tras re-leer su estado; no existe un flag que la simule
