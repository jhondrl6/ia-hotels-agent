"""Denominadores del score GBP: un nombre por escala, un solo sitio de definición.

`D16` publicó la rúbrica de `GBPAuditor` como `/100` cuando su techo es 90 (20+15+15+15+10+10+5):
un sesgo sistemático de 10 puntos. Los tres vocabularios que se leían como uno solo quedan
separados por nombre:

- `SCORE_GBP_MAXIMO` — techo de la rúbrica del perfil (productor único: `_calculate_gbp_score`).
- `ESTIMACION_GBP_MAXIMO` — techo de la heurística de competidor (`reviews/10 x rating x 2`), que
  puede llegar a 100 y NO es comparable con la rúbrica: por eso viaja con `score_source`.
- `geo_score` del cliente de Google Places se normaliza a 100 dentro del propio cliente, así que
  su `/100` es correcto y no se define aquí.

Quien renderiza un denominador importa esta constante; ningún texto comercial fija el número.
"""

SCORE_GBP_MAXIMO = 90
ESTIMACION_GBP_MAXIMO = 100
