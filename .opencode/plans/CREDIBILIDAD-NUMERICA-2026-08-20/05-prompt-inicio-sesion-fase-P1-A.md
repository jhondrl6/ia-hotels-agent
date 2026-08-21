# FASE-P1-A: Benchmark Maestro Único de ADR Regional (F2 + F4)

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-P1-A
**Objetivo**: Unificar las fuentes de benchmark ADR en UNA sola (incluyendo Bogotá), eliminar la
desincronización entre `config/regional_benchmarks.yaml` y `data/benchmarks/regional_adr_2026.json`,
y agregar mecanismo de sincronización.
**Dependencias**: FASE-P0-C ✅ (encoding corregido en writers)
**Duración estimada**: 1 sesión (≤60 iteraciones)
**Skill**: `phased_project_executor.md` (ejecución DIRECTA)

## Modo de Ejecución

**DIRECTO con el agente principal.** Decidir cuál archivo es master y cómo migrar consumidores
es una decisión arquitectónica cross-module (financial_engine, v4_comprehensive, docs comerciales).

## Contexto

CONTEXT §2 fallos **F2** y **F4**:
- **F2**: 3 valores de ADR para `eje_cafetero`: $285K (YAML) vs $420K (JSON runtime, gana) vs
  $200K (doc comercial). Cifra fundacional del pitch varía según la fuente consultada.
- **F4**: Bogotá cubierta en YAML ($350K) pero ausente en JSON runtime → degrada a default $300K.

Causa raíz: dos fuentes de benchmarks sin mecanismo de sincronización. P1 exige consistencia de
benchmarks antes del primer hook enviado (la fuga debe ser defendible).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P0-A | ✅ Completada |
| FASE-P0-B | ✅ Completada |
| FASE-P0-C | ✅ Completada |

### Base Técnica Disponible
- **TRES fuentes de benchmarks viven en el código (verificadas en revisión 2026-08-20) — el plan original asumía 2**:
  1. `config/regional_benchmarks.yaml` — ADR PLANO por región + pain_narratives + confidence + score thresholds. Consumidores: `modules/commercial_documents/v4_diagnostic_generator.py` (L80-110, carga la sección `regions.{region}` completa) y `modules/commercial_documents/v4_proposal_generator.py` (L71-103, confidence thresholds)
  2. `data/benchmarks/regional_adr_2026.json` — ADR por CATEGORÍA (boutique/standard) + occupancy. Gana en runtime
  3. `data/benchmarks/plan_maestro_data.json` — ADR + occupancy + scores geo/aeo/seo + packages + thresholds. Consumidores (9+): `modules/financial_engine/regional_adr_resolver.py` (la cascada REAL: regional_adr_2026.json → plan_maestro_data → default, con `REGION_ALIASES` "coffee_axis"→"eje_cafetero" L136-138), `v4_proposal_generator.py` (L2045-2048), `v4_diagnostic_generator.py` (L2105+, scores via scraper_fallback), `modules/scrapers/scraper_fallback.py` (L13), `modules/utils/dynamic_impact.py`, `modules/utils/benchmarks.py`, `modules/validation/plan_validator.py`, `modules/utils/financial_factors.py`
- **El rango del hook NO usa ninguna de las tres**: `two_phase_flow._get_regional_benchmarks` (L215-230) usa defaults hardcodeados porque `plan_maestro_data` nunca se pasa (OnboardingController L58-61) — se resuelve en FASE-P1-C (decisión D4)
- Tests: 3,233 + nuevos de P0 — línea base `evidence/BASELINE-TESTS-v4.71.0.txt` ("sin regresiones" = sin fallos NUEVOS)

## Tareas

### T0: Mapa completo de fuentes y consumidores (ANTES de decidir master)
**Objetivo**: confirmar con greps el inventario de la Base Técnica (arriba) y detectar cualquier
consumidor adicional NO listado. Grep sugerido: `regional_benchmarks|regional_adr_2026|plan_maestro_data` en `modules/` y `main.py`.
**Criterios de aceptación**:
- [ ] Inventario escrito: fuente → esquema (plano/categoría) → consumidores (archivo+línea) → concepto que consume (ADR/occupancy/scores/factores)
- [ ] Los 9+ consumidores de plan_maestro_data verificados y clasificados por concepto (solo los de ADR/occupancy entran en scope de unificación; scores/factores quedan documentados pero fuera de esta fase — no romper financial_factors)

### T1: Diseñar e implementar el benchmark maestro único
**Decisión a documentar** (10-analisis-post-implementacion.md, decisión D3 del maestro §7):
- ¿YAML o JSON como master? (JSON gana en runtime; YAML es más legible para edición manual)
- **¿ADR plano o por categoría?** (asimetría estructural NO contemplada en el plan original: YAML es plano, JSON es por categoría — el master hereda una de las dos y el otro archivo se adapta o deprecia)
- **¿Destino de plan_maestro_data.json?** (tercera fuente viva: ¿se convierte en derivado del master para ADR/occupancy conservando scores/paquetes, o se acota su rol con validación anti-divergencia?)

**Archivos afectados**:
- `config/regional_benchmarks.yaml` o `data/benchmarks/regional_adr_2026.json` (elegir master)
- `modules/financial_engine/regional_adr_resolver.py` (la cascada REAL del ADR — NO estaba listada en el plan original)
- Script de sincronización/validación (si aplica)

**Criterios de aceptación**:
- [ ] Un solo archivo master con TODAS las regiones (incluyendo Bogotá)
- [ ] Si existe segundo archivo, es generado/validado contra el master (no editado manualmente)
- [ ] Consumidores de ADR (regional_adr_resolver, financial_engine, v4_comprehensive, propuesta) leen del master
- [ ] Bogotá resuelve a su valor correcto (no a default $300K)
- [ ] plan_maestro_data.json: ADR/occupancy sincronizados con el master (o mecanismo anti-divergencia) SIN romper sus otros roles (scores, packages — usados por 6+ módulos)

### T2: Actualizar consumidores
**Archivos afectados**:
- `modules/financial_engine/` (resolución de ADR por región — vía regional_adr_resolver.py)
- `modules/auditors/v4_comprehensive.py` (fallback de región)
- `config/regional_benchmarks.yaml` o `data/benchmarks/regional_adr_2026.json` (según decisión)

**Criterios de aceptación**:
- [ ] Todos los consumidores de ADR leen del master (verificar contra el inventario T0)
- [ ] Sin regresiones en resolución de ADR para hoteles existentes

### T3: Tests de contrato anti-regresión
**Criterios de aceptación**:
- [ ] Test: Bogotá resuelve a su valor correcto
- [ ] Test: eje_cafetero resuelve a un único valor consistente (YAML == JSON == diagnóstico)
- [ ] Test: mecanismo de sincronización detecta divergencia si se edita manualmente el archivo no-master
- [ ] Suite `tests/financial_engine/` sin fallos NUEVOS vs línea base (10 fallos preexistentes en esa suite: test_calculator_v2 ×2 + test_pricing_resolution_wrapper ×8 — ver evidence/BASELINE-TESTS-v4.71.0.txt)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Benchmark maestro | `tests/financial_engine/test_benchmark_master.py` (nuevo) | Contratos F2/F4 pasan |
| Regresión financial_engine | `pytest tests/financial_engine/ -v` | Sin fallos NUEVOS vs línea base (preexistentes: test_calculator_v2 ×2, test_pricing_resolution_wrapper ×8) |

**Comando de validación**:
```powershell
.\venv\Scripts\python.exe -m pytest tests/financial_engine/ -v
.\venv\Scripts\python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-P1-A ✅.
2. `README.md` del plan: actualizar tabla de progreso.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E.
4. `10-analisis-post-implementacion.md`: fila de ejecución + mínimo 3 lecciones + **decisión D3 documentada** (cuál archivo es master + rationale).
5. **Registrar la fase**:
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-P1-A --desc "Benchmark maestro unico de ADR regional (F2+F4) con mapa de 3 fuentes y 9+ consumidores" --archivos-mod "config/regional_benchmarks.yaml,data/benchmarks/regional_adr_2026.json,modules/financial_engine/regional_adr_resolver.py" --tests "<N>" --check-manual-docs
```
6. Editar CHANGELOG.md y GUIA_TECNICA.md (template §6).

## Criterios de Completitud (CHECKLIST)

- [ ] Bogotá y eje_cafetero resuelven a valores únicos y consistentes
- [ ] Mecanismo de sincronización implementado (o migración total)
- [ ] Suite financial_engine sin fallos NUEVOS vs línea base (§6)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada

## Restricciones

- Máximo 60 iteraciones.
- NO modificar lógica de fallback de región (es FASE-P1-B).
- NO modificar comisión OTA (es FASE-P1-B).
- NO ejecutar v4complete.
