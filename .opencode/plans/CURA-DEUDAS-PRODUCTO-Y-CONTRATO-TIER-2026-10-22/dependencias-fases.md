# Dependencias entre Fases — CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22

> Se genera en la etapa de Preparación y se actualiza al cierre de cada fase. La versión vigente incorpora la corrección de estrategia aprobada por el Operador: `spark` retirado, `D21`/`P6.5` fuera, `D16` y `D24` con decisión, FASE-H partida y E2E-PRE antes de la corrida.

## Diagrama de dependencias

```
FASE-A (N1/N7/R4: retiro de spark + guardián)
   │
   ├──► FASE-B (ítem A: render condicionado, 2 claims)
   │         │
   │         └──► FASE-C (ítem C: veredicto + conditional_reason)
   │
   ├──► FASE-D (R1: contrato GBP en v4audit y v4complete)
   │
   └──► FASE-E (R2: lector único + cinco tablas)
             │
             ├──► FASE-F (R3: umbrales por semántica + D25-bis/D27)
             │         │
             └─────────┴──► FASE-H1 (D16 /90 + D24 stub retirado)
                               │
                               └──► FASE-H2 (D18/D22/D23/D20)
                                         │
                                         ▼
                                  FASE-E2E-PRE (ensayo determinista, sin inferencia)
                                         │
                                         ▼
                                  FASE-E2E (v4complete Don Alfonso, ZIP real)
                                         │
                                         ▼
                                  FASE-VERIFY (AC1–AC8)
                                         │
                                         ▼
                                  FASE-RELEASE-4.82.0
```

**Orden de ejecución fijo**: A → B → C → D → E → F → H1 → H2 → E2E-PRE → E2E → VERIFY → RELEASE (una fase por sesión).

`FASE-H1` abre tras FASE-E y FASE-F (necesita el contrato y los valores estables). `FASE-H2` abre tras H1. `FASE-E2E-PRE` exige todas las fases de implementación ✅. `FASE-E2E` exige `E2E-PRE` ✅. `FASE-VERIFY` exige `E2E` ✅. `FASE-RELEASE` exige `VERIFY` ✅.

## Conflictos de archivos (superficies compartidas)

| Archivo/superficie | Fases que lo tocan | Gestión del conflicto |
|--------------------|--------------------|-----------------------|
| `main.py` (ruta `spark`, `_map_audit_to_spark_data`, `run_spark_mode`, `_run_spark_legacy`) | FASE-A | Única fase que retira la ruta; FASE-C solo toca el tribunal, no la CLI |
| `modules/analyzers/gap_analyzer.py` | FASE-A (lector latente), FASE-H2 (`revpar_targets` ya retirado por E) | A corrige el atributo; E retira la tabla; H2 solo documenta |
| `modules/commercial_documents/v4_proposal_generator.py` | FASE-B (render), FASE-F (`_load_scenario_config`/`recovery_factors`) | Orden B antes de F; F toca solo el dict de respaldo/default, no el render |
| `modules/commercial_documents/v4_diagnostic_generator.py` | FASE-B (condicional/precomputado), FASE-D (`_map_brecha_to_issue_type`), FASE-F (umbrales) | Orden B → D → F; D no cambia el render, B no cambia el mapa de brechas |
| `modules/commercial_documents/templates/propuesta_v6_template.md` y `diagnostico_v6_template.md` | FASE-B | Única fase que los toca |
| `modules/quality_gates/tribunal/judge.py` + `acta_writer.py` | FASE-C | Única fase que los toca; `P6.5` y `T1_CERTIFIABLE_CLAUSES` no se tocan |
| `modules/utils/dynamic_impact.py` + `modules/scrapers/gbp_auditor.py` | FASE-D (contrato), FASE-F (umbrales/constantes) | Orden D → F; F re-centraliza valores sin cambiar el contrato de claves |
| `modules/scrapers/gbp_leak_detector.py` | FASE-D | Única fase: sustitución/relevo; FASE-F re-mide las constantes que sobrevivan |
| `modules/utils/benchmarks.py`, `data/benchmarks/*`, `scripts/validate_benchmark_sync.py`, `scripts/run_all_validations.py` | FASE-E (lector + cableado), FASE-H2 (`Benchmarking.md`) | Orden E antes de H2; H2 solo documenta, no mueve valores |
| `modules/generators/report_builder.py`, `modules/scrapers/scraper_fallback.py` | FASE-E | Retirar/derivar el segundo lector y su fallback regional |
| `modules/financial_engine/opportunity_scorer.py`, `modules/auditors/v4_comprehensive.py`, `modules/commercial_documents/data_structures.py` | FASE-F | Barrido de umbrales por símbolo; no cambiar semántica de brechas |
| `config/regional_benchmarks.yaml`, `config/scenarios.yaml` | FASE-F | Fuente de umbrales y coherencia de `recovery_factors` |
| `modules/scrapers/booking_scraper.py` | FASE-H1 (stub retirado) | No tocar `modules/providers/autonomous_researcher.py` |
| `modules/scrapers/gbp_auditor.py` (score `/90`) | FASE-H1 | Solo la superficie de score; FASE-D ya fijó el contrato de claves |
| `data/benchmarks/Benchmarking.md` | FASE-H2 | Solo documentación/declaración de fuente |
| Tests (`tests/`) | Todas | Cada fase añade sus tests con nombres propios; los pares pre/post por fase (R2.3) evitan mezclar deltas |

## Restricciones de secuencia heredadas de los contextos de origen

- **Congelados DEC-2/DEC-3** (solo lectura): `CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md`, `CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md` y el `10-analisis` de `CURA-COSTURA-TRIBUNAL-2026-10-11`.
- **Portones levantados**: `CURA-COSTURA-TRIBUNAL-2026-10-11` cerró (4.81.0) y `CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15` cerró (4.81.1, publicada el 2026-10-22). Este plan es el único en vuelo.
- **Segunda vía del verificador de frescura**: el plan cita `CONTEXT-DEUDAS-PRODUCTO-VERIFICADAS-2026-10-21.md` (no publicado) desde documentos de plan. Si se cura la segunda vía, publicar ese contexto en el mismo ciclo.
- **Train de release**: 4.82.0 es el slot libre (4.81.1 publicada). `FASE-RELEASE-4.82.0` es la única fase que toca `VERSION.yaml`.
- **`P6.5`/`D21` y `D26` no se abren**. `D21` tiene dueño; `D26` carece de enunciado original.

## Estado de fases

| Fase | Estado | Fecha cierre | Notas |
|------|--------|--------------|-------|
| Preparación | ✅ | 2026-10-22 | Correcciones al contexto de deudas aplicadas; estrategia corregida y prompts regenerados |
| FASE-A | ✅ | 2026-10-22 | `spark` retirado (centinela exit 0, `D19` cerrada por retiro); `gap_analyzer` reparado con `get_superposition_factor()`; guardián por existencia con par rojo/verde; barrido `R4c` sin huérfanos vivos |
| FASE-B | ✅ | 2026-10-23 | Ítem A: 2 claims neutralizados por tier en propuesta y diagnóstico (AC1: revisor real + par rojo/verde con diente); gate de Wiring re-publicado (`--quick` 13/13); índice de lecciones re-publicado con autorización (`--check` de `EXIT=1` a `EXIT=0`, los 50 nodos de `lesson_relevance` vuelven verdes); errata de `REGISTRY` corregida a mano (11 nuevos / 7 modificados); H1–H5 y rojos R declarados y H6 curado en `10-analisis` §Seguimientos, con H7 (deuda de instrumento) dueño FASE-H2 |
| FASE-C | ✅ | 2026-10-23 | Ítem C: `APROBADO-CONDICIONAL` + `conditional_reason` (`ANALYTICS_CEILING`/`ONBOARDING_INCOMPLETE`/`UNCERTIFIABLE_CLAUSES`); `has_onboarding` viaja en `review_input_manifest.json`; 8→0 del literal viejo en la población declarada; `P6.5`/`T1` intactas; par rojo/verde M1/M2 en evidencia |
| FASE-D | ✅ | 2026-10-23 | `R1`: contrato GBP único en los dos caminos (`D28`/`N2`/`N3`, `DA-C3`); vocabulario = `_base_profile` (4 claves inglesas retiradas); `PERFIL_ABANDONADO` por actividad, `CERO_ACTIVIDAD_RECIENTE` etiqueta propia; schema tri-estado; mapa de `v4complete` sin schema→abandono; relevo de `gbp_leak_detector` (copia marcada, oráculo vivo) y par M1/M2/M3 (M1 reproduce el reproductor de `D28`: 6 brechas / 39.600.000 COP/mes) |
| FASE-E | ✅ | 2026-10-23 | Lector único: `regiones()` normaliza `v25_config.regiones` y deriva `revpar_cop` por región (el fósil 197.120 global quedó retirado); `ScraperFallback` delega y pierde su respaldo, `gap_analyzer.revpar_targets` retirada, `report_builder` con un solo lector, `FinancialFactors.get_all_regions()` deja de morir en `AttributeError`. Contrato de maestros en tres poblaciones: **cinco** bloques sin dato publicado (la primera medición dijo ocho y su propio test la refutó: barrió rutas, no claves) + **tres horques publicados no leídos** con divergencia medida. `[2/13]` compara valores y conserva parseo/versión, con rojo si `0 regiones comparadas`; M1 13 rojos / M2 1 rojo / M3 de dato; `--quick` 13/13 |
| FASE-F | ✅ | 2026-10-23 | Umbrales por semántica: cinco nombres publicados en `regional_benchmarks.yaml` con lector único (`modules/common/umbrales_fotos.py`) y 14 sitios vivos re-medidos (el contexto publicó 11); `D25-bis` con un solo valor vivo (`modules/common/scenario_config.py`, respaldo 0.20 → 0.35 = maestro); `D27` renombrado por semántica con 0 usos del nombre genérico; `H1` curado (propuesta y diagnóstico resuelven el tier con el mismo productor, `evidence_tier.py`). `--quick` 13/13; mutantes M1/M2 en rojo con árbol intacto por sha |
| FASE-H1 | ✅ | 2026-10-23 | `D16` `/90`: `SCORE_GBP_MAXIMO` en lector único `modules/common/rubrica_gbp.py`; la rúbrica queda con un solo productor (`_calculate_gbp_score`, llamado desde `_scrape_maps_profile` — el contexto de deudas la ubicaba en `check_google_profile`, corregido por AST); reporte, `audit_competitor_profile` (`geo_score_maximo`) y el log del analizador publican el denominador del cálculo; rama API muerta (`_places_api_lookup` + `use_api`) retirada con diente de literales de código; la estimación viaja con `score_maximo=100` y `comparable_con_rubrica_gbp=False`. `D24`: `scrape` publica `found=False`/`data={}`/`STUB_RETIRADO`, export marcado `LEGACY` en su sitio, `autonomous_researcher.BookingScraper` intacto (suite verde). +23 funciones (5.455 → 5.478); mutantes M1 `/100` → 2 rojos, M2 `found=True` → 4 rojos, M3 rúbrica duplicada → 2 rojos, árbol intacto por sha256; declarados con dueño `report_builder` (módulo DEPRECATED), `gbp_leak_detector` (copia FASE-D), la clave `geo_score` con tres escalas (Operador/E2E) y `gbp_geo_score_threshold` sin lector (H2). **Re-declaró el pin de población de FASE-F** (`test_umbrales_fotos_semantica.py`: `gbp_auditor` 5 → 3 sitios, total 14 → 12) porque contaba la rúbrica duplicada que `D16` unifica. Suite 5 failed/5.614 passed: 2 curados aquí, 3 atribuidos (2 preexistentes en `git archive HEAD`, 1 por orden de colección); `--quick` 13/13 |
| FASE-H2 | ⏳ pendiente | — | `D18`/`D22`/`D23`/`D20` |
| FASE-E2E-PRE | ⏳ pendiente | — | Ensayo determinista, sin inferencia |
| FASE-E2E | ⏳ pendiente | — | Corrida Don Alfonso (1/1) |
| FASE-VERIFY | ⏳ pendiente | — | Certificación AC1–AC8 |
| FASE-RELEASE-4.82.0 | ⏳ pendiente | — | Orden R2.10: write-back → índice → `git mv` → índice → refs → quick |
