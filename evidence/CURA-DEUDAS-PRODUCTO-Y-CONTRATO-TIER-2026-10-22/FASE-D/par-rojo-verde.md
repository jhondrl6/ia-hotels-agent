# Par rojo/verde — mutation check AC3 + N2 (FASE-D)

**Símbolo real del guard (R2.8)**: `get_detected_issues` (`modules/utils/dynamic_impact.py`) y su llamador `_detectar_fugas` (`modules/scrapers/gbp_auditor.py`); `_map_brecha_to_issue_type` (`modules/commercial_documents/v4_diagnostic_generator.py`); `tipo_map` (`modules/scrapers/gbp_auditor.py`). Runner versionado: `mutation_pair_runner.py` (muta, corre, revierte y verifica la reversión byte a byte).

| Paso | Mutación | Resultado | Crudo |
|------|----------|-----------|-------|
| 1 | Árbol real (sin mutación) | **VERDE** — 32 passed (dientes de frontera + relevo) | `01-verde-dientes.txt` |
| 2 | **M1**: contrato viejo restaurado en `get_detected_issues` (claves inglesas `claimed`/`photos`/`has_whatsapp`/`has_hours` + semántica de schema vieja) y default `schema_data={}` del llamador | **ROJO** — 11 failed, 7 passed sobre `tests/test_gbp_contrato_frontera.py`. El diente de frontera imprime el reproductor medido de `D28`: `fugas=['PERFIL_NO_RECLAMADO', 'FOTOS_INSUFICIENTES', 'SIN_WHATSAPP_VISIBLE', 'SIN_HORARIOS', 'PERFIL_ABANDONADO', 'SIN_FAQ_CONVERSACIONAL'], perdida=39600000 COP/mes` (= 6 brechas, 39.600.000 COP/mes, la cifra del reproductor del contexto de deudas) | `02-rojo-mutante-m1-claves-inglesas.txt` |
| 3 | Restauración de M1 | **VERDE** — 18 passed | `03-verde-tras-restaurar-m1.txt` |
| 4 | **M2**: `_map_brecha_to_issue_type` restaurado (`no_hotel_schema`/`low_citability` → `PERFIL_ABANDONADO`, `no_og_tags` → `FOTOS_INSUFICIENTES`) | **ROJO** — 3 failed sobre `TestPainSolutionMapperCaminoV4Complete` (`assert 'PERFIL_ABANDONADO' != 'PERFIL_ABANDONADO'`, `assert 'FOTOS_INSUFICIENTES' != 'FOTOS_INSUFICIENTES'`) | `04-rojo-mutante-m2-mapa-schema-a-abandono.txt` |
| 5 | Restauración de M2 | **VERDE** — 5 passed | `05-verde-tras-restaurar-m2.txt` |
| 6 | **M3**: colapso de `tipo_map` restaurado (`CERO_ACTIVIDAD_RECIENTE` → `PERFIL_ABANDONADO`, el defecto `N2`) | **ROJO** — 2 failed, 1 passed sobre `TestN2EtiquetasPropias`: `assert 'CERO_ACTIVIDAD_RECIENTE' in ['PERFIL_ABANDONADO', 'PERFIL_ABANDONADO']` y el dedupe aguas abajo undercounta a 1. El tercero (`test_los_textos_no_repite_la_misma_queja`) queda **VERDE bajo el mutante**: lee `motivo`, que `_get_motivo_for_issue` calcula sobre el `issue_type` original —antes del `tipo_map`—, así que no depende del símbolo mutado | `06-rojo-mutante-m3-tipo-map-colapsado.txt` (crudo: `2 failed, 1 passed`) |
| 7 | Restauración completa (mutantes revertidos) | **VERDE** — 3 passed | `07-verde-tras-restaurar-m3.txt` |

**Poblaciones**: el verde del paso 1 son los 32 tests nuevos de la fase (dos archivos); los rojos usan el archivo o la clase que lee el símbolo mutado (18 / 5 / 3 tests). No es un par like-for-like sobre la suite completa: los rojos prueban el diente sobre la superficie del guard mutado.

**Restauración verificada**: el runner revierte por escritura del original y compara bytes antes de cada verde; `git diff` post-corrida solo muestra los cambios propios de la fase (3 módulos + tests).

**Qué certifica cada rojo**:
- M1 (contrato viejo restaurado → rojo con el reproductor de `D28`): el diente de frontera no es verde por no-ejecución — con las claves inglesas de vuelta, la forma real de `_base_profile()` vuelve a producir las 6 brechas incondicionales y los 39.600.000 COP/mes inventados. Certifica AC3.
- M2 (mapa restaurado → rojo): «sin schema» vuelve a ser `PERFIL_ABANDONADO` y `no_og_tags` vuelve a reclamar fotos GBP; certifica el criterio del mapa en el camino de `v4complete`.
- M3 (colapso restaurado → rojo): las dos brechas de actividad vuelven al mismo `tipo` y el dedupe por `tipo` aguas abajo undercounta; certifica `N2` con **dos** dientes (los de `tipo` y dedupe). El texto diferenciado no lo certifica este mutante: su verde es fijo porque `motivo` se resuelve antes del mapa (queda declarado como límite de cobertura en `10-analisis` §Seguimientos).

**Lo que el par NO certifica** (`L-R.4`): no hay guard automático que impida re-introducir el contrato viejo fuera de esta suite (la mutación es manual y vive en el runner); `v4complete` no se ejercitó (fuera de alcance de FASE-D; AC3 se certifica con el diente de esta fase, como declara el prompt).
