# NR1 — Delta R2.7 (FASE-P2)

Regla R2.7: `suma_post − suma_pre == tests_nuevos`. Diferencia 0 = baseline contaminado.

## Método

- Comando canónico **idéntico** pre y post:
  `python -m pytest tests/ -q --tb=no -rf -p no:cacheprovider`
- **PRE** capturado a las **16:57** del 2026-09-14 (HEAD = `ae6dd61`, el cierre documental
  de P3-B), **antes de la primera edición** de `main.py`, `modules/` o `tests/`
  → `nr1_baseline_pre.txt`.
  No hizo falta `--ignore` de los tests propios: los dos archivos de test de esta fase
  (`test_p2_veredicto_enriquecido.py`, `test_p2_cuarentena_zip.py`) aún no existían
  cuando corrió el PRE (**L-T4B.5** satisfecha por construcción, igual que en P3-B).
  **Combinación de archivos declarada**: `tests/` completo, sin exclusión, con
  `-p no:cacheprovider`.
- **POST** capturado después de **todos** los cambios de código y de test, con el árbol
  ya restaurado por `nr7_mutation_checks.py` (el script afirma al terminar que
  `judge.py`, `outcome.py`, `acta_writer.py` y `delivery_packager.py` son idénticos al
  original) → `nr1_baseline_post.txt`.
- **Flaky conocido declarado (L-VUP-1)**: `test_function_default_flags`
  (`tests/financial_engine/test_pricing_resolution_wrapper.py`, orden-dependiente).
  Está en rojo en PRE y en POST, mismo conjunto, por tanto no afecta la resta.

> **Segundo POST, no el primero**: la primera corrida POST se tomó con `+27` y quedó
> invalidada por una edición posterior (el seguimiento de `10-analisis` que P2 cerró:
> la fuente del tier sale ahora del `first_floor_rule` del acta). Se añadió
> `test_el_acta_nombra_la_fuente_real_del_tier` y el POST se **repitió** con el árbol
> final. Si no se hubiera repetido, R2.7 se habría declarado con un árbol que ya no
> existe. El `nr7_mutation_checks.py` se re-ejecutó después de esa edición (8/8) porque
> sus mutaciones casan texto literal de los archivos.

## Sumas canónicas (failed + passed + skipped + xfailed)

| | failed | passed | skipped | xfailed | SUMA |
|--|--------|--------|---------|---------|------|
| PRE  | 2 | 4.116 | 31 | 4 | **4.153** |
| POST | 2 | 4.144 | 31 | 4 | **4.181** |
| Δ    | **0** | **+28** | 0 | 0 | **+28** |

## Resta R2.7

```
suma_post − suma_pre = 4181 − 4153 = 28
tests_nuevos         = 28   (19 + 9, ver desglose abajo)
28 == 28  →  OK (baseline NO contaminado)
```

A diferencia de P3-B, aquí `passed` sube **exactamente** +28: ningún test existente
migró de `failed` a `passed` (no había rojos propios que cerrar) y ningún test se
perdió ni se desplazó. `skipped` y `xfailed` sin cambio.

## Tests nuevos por AC (los 28)

- **AC-E0 / NR8 — los cuatro estados (7)**: `test_p2_veredicto_enriquecido.py` →
  `test_los_4_revisores_no_hallan_nada`, `test_artefacto_ausente`, `test_lector_fallido`,
  `test_los_revisores_no_corrieron`, `test_los_tres_estados_no_colapsan`,
  `test_la_seccion_de_revisores_nunca_se_omite`, `test_un_fallo_de_lectura_nunca_bloquea`.
- **AC-E1 — DTO poblado (1)**: `test_reviewer_reports_refleja_los_cuatro_revisores`.
- **AC-E2 — la objeción decide (4)**: `test_bloquear_de_un_revisor_bloquea_la_entrega`,
  `test_critical_verificado_por_un_revisor_bloquea`,
  `test_warning_de_revisor_no_degrada_bajo_el_primer_piso`,
  `test_el_orden_de_la_matriz_es_parte_del_contrato`.
- **AC-E3 — never-block (1)**: `test_revisor_que_revienta_no_rompe_la_corrida`.
- **AC-E4 — kill switch heredado (2)**: `test_el_knob_apagado_no_bloquea_pero_lo_declara`,
  `test_el_knob_forzado_a_on_ejercita_el_bloqueo`.
- **AC-E5 — consecuencia del bloqueo (3 + 5 del ZIP real)**: en el acta
  `test_veredicto_bloqueante_deja_acciones_correctivas_con_dueno`,
  `test_bloqueo_por_gate_sin_hallazgo_de_revisor_tambien_tiene_dueno`,
  `test_veredicto_no_bloqueante_no_inventa_acciones`; y en
  `test_p2_cuarentena_zip.py`, **contra ZIP real** (L-V.1):
  `test_write_deja_cuarentena_sin_publicar`,
  `test_suprimir_la_cuarentena_no_deja_ningun_zip`,
  `test_publicar_otorga_el_nombre_definitivo_y_validate_zip_pasa`,
  `test_borrado_que_falla_es_error_de_infraestructura`,
  `test_publicar_sin_cuarentena_no_inventa_un_zip`.
- **Cierre del círculo judge↔packager (2)**: `test_los_revisores_leen_el_paquete_en_cuarentena`
  (Bot 3 lee `IMPLEMENTATION_ORDER.md` desde el `.zip.tmp`) y
  `test_veredicto_bloqueante_del_tribunal_suprime_el_zip_real` /
  `test_veredicto_no_bloqueante_publica_el_zip_real` (el rename solo ocurre si el
  veredicto lo permite).
- **Seguimiento cerrado por P2 (1)**: `test_el_acta_nombra_la_fuente_real_del_tier`.

**28 funciones = 28 tests recolectados**: en esta fase no hay parametrización, así que
el conteo canónico por `def` y el de pytest coinciden.

## Tests existentes migrados (3, sin cambio de suma)

No son tests nuevos ni borrados; cambian de aserción porque el contrato fija un régimen
nuevo. Se listan porque un lector de `git diff` los verá y debe poder distinguir
"migración justificada" de "regresión maquillada":

1. `test_judge.py::test_verdict_tier_a_can_be_approved` — antes: `evaluate()` solo daba
   `APROBADO-PARA-ENTREGA`. Ahora la primera pasada con los 4 Bots en `NOT_RUN` da
   `APROBADO-CONDICIONAL…` **por contrato** (regla 2 de DA-P1.6: ausencia jamás es PASS)
   y el veredicto máximo se observa tras `enrich()` con informes legados.
2. `test_judge.py::test_p6_2_deferred_does_not_block_approval` — same regime shift; su
   garantía (P6.2 diferida no impide el veredicto máximo) sigue viva, en la 2ª pasada.
3. `test_acta_serialization.py::test_acta_md_references_source_artifacts` — asertaba
   `"MANIFEST.json" in md`, que desde AC-F2 era el **literal del writer**, no lo que el
   Juez leyó. Ahora aserta `financial_scenarios` (la fuente real) y que el valor sale de
   `first_floor_rule.source_artifact`.

## Fallos — POST

2 fallos, **ambos ajenos a esta fase** y **idénticos en el PRE**:

1. `tests/financial_engine/test_pricing_resolution_wrapper.py::...::test_function_default_flags` — flaky conocido (L-VUP-1)
2. `tests/test_diagnostic_geo_metrics.py::...::test_diagnostic_includes_geo_metrics` — ajeno conocido

**0 regresiones.** `test_faq_generator_output_is_jsonld`, que estaba rojo al concebir el
plan, ya venía verde desde el PRE de P3-B.

## Conteo canónico (el del `grep`, no el de pytest)

Medido al cerrar la fase con el método canónico del repo
(`grep -rE "^\s*def test_" tests --include=*.py`):

| | Al cerrar P3-B | Al cerrar P2 | Δ |
|--|----------------|--------------|---|
| Funciones `def test_` | 4.146 | **4.174** | **+28** |
| Archivos `test_*.py` | 298 | **300** | +2 |

Tests del directorio `tests/quality_gates/tribunal/`: **158 → 177** recolectados (+19).

Para RELEASE: **4.174 funciones / 4.181 recolectados / 300 archivos**. La brecha entre
ambas bases era **7 al cerrar P3-B** (4.146 vs 4.153) y sigue siendo **7** — P2 no la
creció ni la redujo (aquí funciones == recolectados, sin parametrizaciones nuevas). Su
origen exacto se reconcilia en RELEASE, no en esta fase.

## Duraciones

PRE 157.35 s (2:37), POST 133.89 s (2:13). El POST de P2 es el más corto de la serie del
plan (P3-B: 450–622 s) porque la máquina estaba ociosa; el método es idéntico.
