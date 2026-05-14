# Comparativo de Complejidad Tecnica — FASE-0-DELIVERY-QUALITY

> **Fecha:** 2026-05-13  
> **Plan:** `.opencode/plans/FASE-0-DELIVERY-QUALITY/`  
> **Repo:** iah-cli v4.45.0 — TERMALES-GATE-HARDENING  
> **Metodologia:** Evaluacion dimensional 1-5 por fase (8 fases x 7 dimensiones)  
> **Ultima actualizacion:** 2026-05-13 — Post FASE-0A completada

---

## Tabla Resumen

Escala: 1 (baja) a 5 (critica) por dimension.

| Fase | Nombre | Estado | Alg | Arch | Mod | Regr | Intg | Dep | Cost | **Total** |
|------|--------|:------:|:---:|:----:|:---:|:----:|:----:|:---:|:----:|:---------:|
| 0A | Baseline Real | ✅ | 1 | 1 | 2 | 1 | 1 | 1 | 1 | **7** |
| 0B | Pain Ledger | ⏳ | 2 | 3 | 3 | 3 | 3 | 2 | 1 | **17** |
| 0C | Coverage Gate | ⏳ | 3 | 2 | 3 | 4 | 3 | 3 | 1 | **19** |
| 0D | Proposal-Asset Matrix | ⏳ | 3 | 4 | 4 | 4 | 4 | 4 | 1 | **24** |
| **0E** | **Delivery Quality Report** | ⏳ | **4** | **4** | **5** | **5** | **5** | **5** | **1** | **29** |
|| 0F | Human Checklist | ⏳ | 1 | 2 | 2 | 2 | 2 | 3 | 1 | **13** |
|| 0G | E2E Controlado | ⏳ | 1 | 1 | 1 | 2 | 3 | 5 | 5 | **18** |
|| **0H** | **G8 Root-Cause Hardening** | ⏳ | **3** | **3** | **3** | **3** | **3** | **3** | **1** | **19** |
|| RELEASE | Docs Cascade | ⏳ | 1 | 2 | 1 | 2 | 2 | 5 | 1 | **14** |

**Maximo teorico:** 35 puntos por fase.

---

## Dimensiones Evaluadas

| Codigo | Dimension | Que mide |
|--------|-----------|----------|
| Alg | Complejidad algoritmica/logica | Numero de reglas condicionales, set operations, decision trees |
| Arch | Archivos a tocar | Cantidad y criticidad de archivos nuevos + modificados |
| Mod | Modulos existentes a entender | Cuantos modulos del repo debe comprender el implementador |
| Regr | Riesgo de regresion en produccion | Probabilidad de que un error rompa entregas actuales |
| Intg | Complejidad de integracion en data flow existente | Cuanto debe encajar en pipelines ya establecidos |
| Dep | Dependencias de otras fases / acoplamiento | Cuantas fases anteriores debe tener completas para funcionar |
| Cost | Costo de API/computo ($) | Gasto en llamadas externas durante la sesion |

---

## Analisis Detallado por Fase

### FASE-0A: Baseline Real (Total: 7) — ✅ COMPLETADA 2026-05-13
- **Tipo:** Investigacion pura. Sin codigo.
- **Archivos:** 0 codigo. Solo lectura de outputs JSON existentes.
- **Riesgo:** Nulo. No toca produccion.
- **Complejidad:** Baja. Requiere entender estructura de output existente y construir tabla.

**Resultados reales obtenidos:**
- 13 JSONs en `v4_audit/` documentados con top-keys
- 14 subdirectorios de assets (12 generados + geo_enriched + v4_audit)
- 1 ZIP verificado fisicamente (121 KB, `hotelcastillareal_20260512.zip`)
- 6 MDs diagnostico/propuesta (3 ejecuciones)
- Matriz de trazabilidad: 14 filas (12 assets + 1 skipped + 1 sin pain)
- 10 pain_ids unicos en assets vs 7 brechas numeradas en diagnostico
- `delivery_ready_percentage`: 25% (3/12 assets con confianza >= 0.8)
- GAP-H1 a GAP-H6 verificados con comandos `find` + `grep` + lectura de JSONs
- Baseline documentado en `.opencode/context/FASE-0-BASELINE-DELIVERY-QUALITY.md` (15 KB)
- **Veredicto:** FASE 0 requiere IMPLEMENTACION + ENDURECIMIENTO (3 artifacts nuevos, 2 endurecimientos, 1 correccion semantica)

### FASE-0B: Pain Ledger (Total: 17)
- **Tipo:** Codigo + tests. Facade sobre estructura existente.
- **Archivos:** Crea 1 modulo nuevo (`pain_ledger.py`). Modifica `v4_asset_orchestrator.py` (986 lineas).
- **Riesgo:** Medio. Orchestrator es central; la modificacion es insercion post-deteccion.
- **Complejidad:** Media. Requiere entender `PainSolutionMapper`, `Pain` dataclass, y donde inyectar `save()` en el flujo de asset generation.

### FASE-0C: Coverage Gate (Total: 19)
- **Tipo:** Codigo + tests. Gate de validacion de cobertura.
- **Archivos:** Modifica `publication_gates.py` (1278 lineas).
- **Riesgo:** Medio-Alto. Gates bloquean publicacion. Un error puede dejar hoteles sin entrega o permitir entregas inconsistentes.
- **Complejidad:** Media-Alta. Logica de set operations (`brechas_detectadas` vs `justificadas`) integrada en pipeline de gates existente.

### FASE-0D: Proposal-Asset Matrix (Total: 24)
- **Tipo:** Codigo + tests. Matriz dinamica de trazabilidad.
- **Archivos:** Modifica `proposal_asset_alignment.py` + `v4_proposal_generator.py` (1943 lineas).
- **Riesgo:** Alto. Proposal generator genera documentos comerciales visibles al cliente. Error aqui afecta propuesta de venta directamente.
- **Complejidad:** Alta. Debe entender:
  - `PROPOSAL_SERVICE_TO_ASSET` (estatico)
  - `_generate_dynamic_services_table` (dinamico)
  - `AssetDiagnosticLink`
  - `PainLedger`
  - Mantener backward compat con template V6

### FASE-0E: Delivery Quality Report (Total: 29) — MAYOR COMPLEJIDAD
- **Tipo:** Codigo + tests. QA bloqueante pre-ZIP.
- **Archivos:** Crea 1 modulo nuevo. Modifica `main.py` (**3318 lineas**).
- **Riesgo:** **CRITICO.** `main.py` es el punto de entrada del CLI. Un error puede romper TODO el pipeline `v4complete` para cualquier hotel.
- **Complejidad:** **MAXIMA.** Debe:
  - Leer multiples artifacts del `v4_audit/` (coherence, coverage, matrix, gates)
  - Coordinar resultados de gates de fases anteriores (0C, 0D, specificity)
  - Tomar decision de bloqueo que afecta el flujo comercial
  - Abortar ZIP si FAIL con mensaje de motivo
  - Ser el unico artifact que determina si el paquete es entregable (G0)
  - Requiere mocks de publicacion/ZIP para tests unitarios
  - Integracion en `main.py` implica entender el flujo completo de `v4complete`

### FASE-0F: Human Checklist (Total: 13)
- **Tipo:** Codigo + tests. Derivacion simple de reporte a markdown.
- **Archivos:** Crea 1 modulo nuevo. Modifica `main.py`.
- **Riesgo:** Bajo. Es un generador de texto; no afecta flujo de negocio.
- **Complejidad:** Baja. Derivacion directa de `DeliveryQualityReport` a lista markdown.

### FASE-0G: E2E Controlado (Total: 18)
- **Tipo:** Ejecucion + verificacion.
- **Archivos:** 0 codigo. Solo lectura/verificacion.
- **Riesgo:** Costo API ($$). No hay riesgo de regresion en codigo.
- **Complejidad:** Media. Requiere validar 4 gates (G0/G6/G7/G8) contra output real.

### FASE-RELEASE: Docs Cascade (Total: 14)
- **Tipo:** Documentacion pura.
- **Archivos:** 0 codigo productivo.
- **Riesgo:** Bajo. Solo docs.
- **Complejidad:** Media-Alta administrativamente (7 registros, version bump, sync).

---

## Ranking Definitivo (mayor a menor complejidad)

| Rank | Fase | Total | Clave de riesgo |
|------|------|:-----:|-----------------|
| 1 | **0E — Delivery Quality Report** | **29** | Toca main.py (3318 lineas), coordina gates anteriores, aborta ZIP, bloquea G0 |
| 2 | 0D — Proposal-Asset Matrix | 24 | Toca proposal generator (1943 lineas), documento comercial visible al cliente |
|| 3 | 0C — Coverage Gate | 19 | Pipeline de gates (1278 lineas), bloquea publicacion |
|| 4 | **0H — G8 Root-Cause Hardening** | **19** | **Refactor scoring + derivación de datos + contrato REQUIRED/RECOMMENDED** |
|| 5 | 0G — E2E Controlado | 18 | Costo API, depende de 0A-0F completas |
|| 6 | 0B — Pain Ledger | 17 | Orchestrator central (986 lineas) |
|| 7 | RELEASE — Docs Cascade | 14 | 7 registros + version sync |
|| 8 | 0F — Human Checklist | 13 | Derivacion simple, depende de 0E |
|| 9 | 0A — Baseline Real | 7 | Investigacion pura, 0 codigo |

---

## Recomendaciones de Mitigacion

### Para FASE-0E (mayor riesgo)

| Estrategia | Accion |
|------------|--------|
| Backup | Hacer backup de `main.py` antes de modificar |
| Split condicional | Si se acerca a 40 iteraciones, dividir en 0E-A (modulo + tests) y 0E-B (integracion en main.py) |
| Tests con mocks | Usar mocks de `create_delivery_package()` para testear aborto sin ejecutar ZIP real |
| Fixture local | Validar con output de hotelcastillareal copiado a fixture, sin v4complete |
| Regresion focalizada | Ejecutar `pytest tests/ -k "publication or gate"` antes y despues |

### Para FASE-0D (segundo mayor riesgo)

| Estrategia | Accion |
|------------|--------|
| Template V6 audit | Verificar que template hardcoded no se rompe al inyectar matriz dinamica |
| Dual table | `v4_proposal_generator.py` tiene 2 tablas: dinamica + hardcoded. Actualizar ambas |
| Aux lookups | Verificar `ASSET_NAMES` y display mappings completos |

### Para FASE-0G (costo)

| Estrategia | Accion |
|------------|--------|
| Preflight barato | `run_all_validations.py --quick` antes de gastar API |
| Evidencia proactiva | Copiar artifacts a `evidence/FASE-0G-E2E/` inmediatamente despues de v4complete |
| Hotel fijo | Usar hotelcastillareal (ya auditado) para comparacion antes/despues |

---

## Notas

- Este comparativo fue generado a partir del analisis de los prompts de fase en `.opencode/plans/FASE-0-DELIVERY-QUALITY/` y del estado real del codigo en `modules/`, `tests/`, `main.py`.
- **Lineas de codigo verificadas (post FASE-0A):** `v4_asset_orchestrator.py` (986), `conditional_generator.py` (358), `asset_diagnostic_linker.py` (284), `proposal_asset_alignment.py` (400), `asset_metadata.py` (732), `publication_gates.py` (1278), `v4_proposal_generator.py` (1943), `coherence_validator.py` (589), `main.py` (3318).
- **GAPs confirmados en baseline (FASE-0A):** 
  - H1: `delivery_quality_report.json` inexistente (ni en disco ni en codigo)
  - H2: `pain_ledger` nominalmente inexistente (pero infraestructura `pain_id` extensa en `asset_generation/`)
  - H3: Mapeo brecha→pain_id implicito (no explicito en diagnostico/propuesta)
  - H4: Contrato estatico `PROPOSAL_SERVICE_TO_ASSET` convive con generacion dinamica parcial
  - H5: `can_use=True` con 9/12 assets WARNING — `delivery_ready_percentage` 25%
  - H6: ZIP existe fisicamente (121 KB) — verificado en disco
- **Hallazgo critico adicional:** `monthly_report` tiene `pain_ids_resolved: []` (sin vinculacion a brecha).
