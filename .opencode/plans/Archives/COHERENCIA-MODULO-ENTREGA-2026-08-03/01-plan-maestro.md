# Plan Maestro: Coherencia Módulo ↔ Entrega (D1-D12 + N1-N9)

**ID del plan**: COHERENCIA-MODULO-ENTREGA-2026-08-03
**Contexto fuente**: `/.opencode/context/Historico/CONTEXT-DIAGNOSTICO-COHERENCIA-MODULO-ENTREGA-2026-08-02.md` (re-auditoría 2026-08-03: 12/12 hallazgos confirmados + 9 ampliaciones N1-N9)
**Workflow rector**: `.agents/workflows/phased_project_executor.md` v2.13.0
**Versión actual**: v4.69.0 → **Release objetivo: v4.70.0**
**Hotel de verificación E2E**: Zi One Luxury (https://zione.co/) — onboarding real en `output/clientes/zi-one-luxury_onboarding.yaml`
**Fecha de creación**: 2026-08-03

---

## 1. Objetivo

El pipeline publica `gate_status: PASSED` con `coherence_score 0.9168` mientras el documento entregado contradice su propia evidencia (D1: "Sin OG" con 8 tags detectados; D2: 9 vs 4 vs "7" brechas). El plan elimina las 6 clases de defecto estructural identificadas:

1. **Doble detección de pains** (D2) — generator con VS sintético + caché vs orquestador con inputs reales.
2. **Triple capa de dinero paralela** (D3, N1) — costos de brechas y recuperación proyectada con 2-3 implementaciones divergentes.
3. **Gates con semántica débil** (D5, N2) — validan INPUTS, no el artefacto que publican.
4. **Texto estático que miente** (D1, D6-D10, N3, N5-N8) — hardcodes que se propagan byte-idénticos entre runs.
5. **Labels de procedencia derivados de config, no de origen** (D12).
6. **Ausencia de freshness en evidencia** (D11, N4) — artefactos stale viajan al ZIP.

**Regla de oro**: una fuente de verdad por concepto — detección (1), costos (1), recuperación (1), labels de origen (1).

## 2. Alcance

### INCLUIDO
- Fixes D1-D12 y N1-N9 según contexto §5, respetando la prioridad P0→P2.
- Tests por hallazgo + verificación estática (greps §6 del contexto).
- UNA sola ejecución de `v4complete` en todo el plan: FASE-E (verificación E2E), con onboarding real de Zi One Luxury.
- Análisis post-implementación (fixes superados) + lecciones aprendidas (`08-analisis-post-implementacion.md`, se llena en FASE-E/RELEASE).

### EXCLUIDO (con razón)
- `modules/delivery/delivery_packager.py` arquitectura single-write (resuelta en v4.69.0, contexto DELIVERY-ZIP-PACKAGING-BROKEN). Solo se toca el criterio de selección de archivos v4_audit (N4).
- Fórmulas de pérdida de `scenario_calculator.py` (valores centrales verificados correctos).
- Fórmula geo_score de `google_places_client.py` (correcta; el problema es la atribución en el template, D8).
- Fix de tier B+ / evidence tier (ya aplicado, no revertir).
- Re-ejecución de baselines: se usa como baseline los outputs del run 2026-08-01 ya auditados (`output/v4_complete/` + `evidence/`).

## 3. Fases (1 fase = 1 sesión, regla R1)

| Fase | Hallazgos | Objetivo | Complejidad | Modo de ejecución (delegate_task) |
|------|-----------|----------|-------------|-----------------------------------|
| FASE-A | D1, D2 | Contenido veraz: `_pain_to_brecha` + detección única de brechas | Media | **DIRECTO** — fix puro de código+tests (regla código+tests) |
| FASE-B | D3, D4, N1 | Finanzas honestas: costo único, escenarios reales, fórmula única de recuperación 6m | **MÁXIMA** ⚠️ | **DIRECTO** — decisión arquitectónica cross-module, NO delegable (regla DT-3) |
| FASE-C-A | D5, N2 | Gates reales: coverage honesto + gate doc↔audit | Media-Alta | **DIRECTO** — rediseño de semántica de gates |
| FASE-C-B | D6, D7, D8 | Textos dinámicos: performance/reviews/atribución GEO | Baja-Media | **DELEGADO parcial** — 2 tracks paralelos (generator vs template) vía subagentes; principal coordina |
| FASE-D | D9, D10, D11, D12, N4, N3, N5-N8 | Freshness + procedencia + pulido de texto | Media | **DELEGADO parcial** — track N5-N8 (pulido mecánico) a subagente; D9-D12+N4 directo |
| FASE-E | E2E | **Única ejecución v4complete** Zi One Luxury + verificación 21 hallazgos + evidencia | Media | **DELEGADO** — v4complete vía subagente (protocolo §Protocolo-Subagente-para-v4complete) |
| FASE-RELEASE-4.70.0 | Docs | Version bump, CHANGELOG, GUIA_TECNICA, validaciones, flujo documental | Baja | **DELEGABLE** (tip Paso 7: solo YAML/MD + scripts, sin imports del proyecto) |

### Fase de mayor complejidad técnica: **FASE-B**

Razones:
1. Contiene **2 decisiones arquitectónicas cross-module** que el plan debe resolver antes de codificar: D3 (opción A vs B para la fuente única de costos) y N1 (curva de maduración vs pain_ratio×recovery como fórmula única de recuperación 6m).
2. Toca 3 subsistemas acoplados: `financial_engine` (opportunity_scorer, scenario_calculator, pillar_maturity_curve), `commercial_documents` (v4_diagnostic_generator) y el gate comercial CG-SCENARIO-ORDER que debe cablearse al pipeline.
3. Efecto cascada máximo: cambia los costos de brechas y la cifra de recuperación de TODOS los hoteles (riesgo §8 filas 1-2) → fixtures golden-file y tests de diagnóstico/propuesta requerirán actualización coordinada.
4. Semántica invertida de escenarios (conservative 19.6M = peor caso con prob 70%; optimistic −6.8M = ganancia): el fix incorrecto confunde al cliente final (riesgo §8 fila 5).

## 4. Mapa de conflictos de archivos

| Archivo | Fases que lo tocan | Separación |
|---------|-------------------|------------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | A, B, C-B, D | A: `_pain_to_brecha`/`_identify_brechas` (L2823-3028) · B: costos/escenarios (L1063-1240, L3217-3230) · C-B: L316/L1741 · D: L1854-1862/L2458/L2471 |
| `main.py` | A, D | A: L2638/L3290 (inputs reales a `_identify_brechas`) · D: L1878/L1937 (label occupancy) |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | A, C-B | A: conteo dinámico L66-67 · C-B: atribución GEO L140/L299 + N5 L57 (N5 puede caer en D) |
| `modules/quality_gates/publication_gates.py` | C-A | Único |
| `modules/financial_engine/*` | B | Único |
| `modules/commercial_documents/v4_proposal_generator.py` | B, D | B: reconciliación recuperación (3 cálculos: net_benefit L591-596, curva L786-925, diagnóstico) · D: L629 (commercial_gates_report — mover write FUERA del branch de error, escribir SIEMPRE) |
| `modules/delivery/delivery_packager.py` | D | Único (solo criterio de selección, NO arquitectura) |

Detalle completo y orden de ejecución → `dependencias-fases.md`.

## 5. Baseline y verificación E2E

- **Baseline auditado** (NO re-ejecutar): run 2026-08-01 17:05:39 — outputs en `output/v4_complete/` y `output/v4_complete/zione/v4_audit/`; checklist de comparación en contexto §6.
- **Ejecución E2E única** (FASE-E):
  ```bash
  ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --output output/v4_verify_4.70.0
  ```
  El onboarding se carga automáticamente por `hotel.url` (`main.py::_load_latest_onboarding_data`), con fallback a `data/hotel_observations/observations.json` (que YA contiene a Zi One Luxury con los mismos datos 34/800/290000/40 — verificado 2026-08-03). **Pre-requisito FASE-E T0**: agregar `url: https://zione.co` al YAML `output/clientes/zi-one-luxury_onboarding.yaml` (hoy el campo falta; el matching por YAML fallaría y se usaría el fallback de observations.json — datos equivalentes, pero el YAML canónico Tier A es la fuente preferida).
- **Verificación**: checklist D1-D12 + N1-N9 (contexto §6) + greps estáticos + Protocolo de Evidencia Proactiva (`evidence/FASE-E/`).

## 6. Métricas base

| Métrica | Valor inicial | Fuente |
|---------|---------------|--------|
| Tests totales | 3,185 funciones / 253 archivos | AGENTS.md §Estado Actual |
| Coherence run baseline | 0.9168 (frontmatter del doc `01_DIAGNOSTICO_..._20260801_170539.md:5`; el gate_report lo redondea a 0.92) | run 2026-08-01 |
| Hallazgos abiertos | 21 (D1-D12, N1-N9) | contexto re-auditoría |
| Versión | v4.69.0 | VERSION.yaml |

## 7. Registro por fase (anti-deuda, executor §2.5)

CADA fase de implementación ejecuta su propio `log_phase_completion.py` al cerrar (nunca acumular en RELEASE):

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-X --desc "..." \
    --archivos-mod "paths" --tests "N" --coherence 0.XX --check-manual-docs --release 4.70.0
```

(Sin `--status`; `--release` sin prefijo "v".)

## 8. Riesgos operativos conocidos

| Riesgo | Mitigación |
|--------|------------|
| Suite completa 3,185 tests da timeout | Ejecutar por módulo (lección 5 plan ZIP); suite completa solo en FASE-E/RELEASE |
| v4complete 5-10 min agota sesión | FASE-E: subagente/background + notify + evidencia ANTES de verificar |
| WSL safety guard bloquea rm/copy/heredocs | Usar write_file y rutas explícitas (skill wsl-safety-guard-bypass) |
| Unificar detección (D2) cambia costos de todos los hoteles | Documentado como corrección; baseline pre/post en evidencia |
| Gate doc↔audit (N2) falla runs existentes | WARNING primero, BLOCKING después (decisión en FASE-C-A) |
