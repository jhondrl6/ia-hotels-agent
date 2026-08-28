# Análisis Post-Implementación — SR-PIPELINE-FIXES-2026-08-27

> **Estado**: Preparación completada (2026-08-27) — 13 archivos del plan creados; 0 fases ejecutadas.
> **Plan**: SR-PIPELINE-FIXES-2026-08-27 (v4.72.2 → v4.73.0 "Alineación de Pipeline")
> **Causa raíz tratada**: capas desincronizadas que contabilizan distinto el mismo hecho (promesa/matriz/gate) + gates que detectan sin ciclar + identidad de memoria no canónica + preflight que castiga la evidencia del problema.
> **Regla**: este archivo se crea DESDE LA CONCEPCIÓN del plan (executor v2.15.0+) y se actualiza al cierre de CADA fase.

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-SR-A (helper unresolved) | Sesión 1 | ⏳ | — | NO (directo) | |
| FASE-SR-B (unificación) ⚠️ | Sesión 2 | ⏳ | — | NO (DT-3) | |
| FASE-SR-C (self-healing) | Sesión 3 | ⏳ | — | NO (directo) | |
| FASE-SR-D (target_id) | Sesión 4 | ⏳ | — | NO (directo) | |
| FASE-SR-E (preflight) | Sesión 5 | ⏳ | — | NO (directo) | |
| FASE-SR-F (varianza+OPS) | Sesión 6 | ⏳ | — | NO (directo) | |
| FASE-SR-G (display) | Sesión 7 | ⏳ | — | NO (directo) | |
| FASE-SR-H (E2E Salento Real) | Sesión 8 | ⏳ | — | SÍ (v4complete) | |
| FASE-SR-VERIFY (ACs) | Sesión 9 | ⏳ | — | NO (§4.6) | |
| FASE-RELEASE-4.73.0 | Sesión 10 | ⏳ | — | opcional | |

---

## Matriz de Verificación de Hallazgos (llenar en FASE-SR-VERIFY; fuentes: `evidence/FASE-SR-H/baseline/` vs `output/salentoreal_final_v4c/`)

### Baseline de referencia (corrida C, 2026-08-27 18:30): NOT_READY — 12/13 PASSED, alignment 43% (3/7), coherence 0.8644, unresolved gate=4 vs delivery=1, hotel_schema DETECTED, target_id con UTM, claim falso publicado, tier 'B' vs 'D'.

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| AC1 | Gate proposal_asset_alignment NO bloquea por NO_BREACH ("sin costo") | coverage_ratio ≥ 0.80; gate PASSED en corrida final | ⏳ | ⏳ |
| AC2 | Promesa derivada del pain_ledger + present_in_production | Propuesta no promete servicios sin pain ni presencia; estados coherentes propuesta↔matriz↔gate | ⏳ | ⏳ |
| AC3 | Unresolved idéntico en gate_report y delivery_quality_report | Mismo número `unresolved` en ambos reportes del MISMO run (fin del 4-vs-1) | ⏳ | ⏳ |
| AC4 | Claims vs evidencia ciclan | 0 claims "no aparece" contradiendo GBP publicados (o BLOCKED real) | ⏳ | ⏳ |
| AC5 | target_id canónico | target_id sin query string en log de corrida final; unit tests UTM≡limpia | ⏳ | ⏳ |
| AC6 | hotel_schema generado | Asset generado vía fallback; no_hotel_schema = ASSET_GENERATED | ⏳ | ⏳ |
| AC7 | Paradoja de coherencia resuelta | coherence_validation sin "Assets no implementados: hotel_schema"; score ≥ 0.8 | ⏳ | ⏳ |
| AC8 | Varianza explicada | Informe con hipótesis verificada del 7→5 (o fix con test) | ⏳ | ⏳ |
| AC9 | Display sincronizado | 0 WARNING CG-TIER-CONSISTENCY; jerga reducida vs baseline | ⏳ | ⏳ |
| AC10 | 0 regresión financiera | Escenarios idénticos al baseline: $6.57M / $4.04M / $1.26M COP | ⏳ | ⏳ |
| AC11 | readiness READY_FOR_PUBLICATION | `readiness = READY_FOR_PUBLICATION` en v4_complete_report | ⏳ | ⏳ |
| AC12 | Entregables publicables | Sin BLOCKED_BY_GATES.md; 01/02 presentes; ZIP no abortado | ⏳ | ⏳ |
| AC13 | Guardián estático L-SR1 | Test AST pasa; `grep "logger\." main.py` = 0 | ⏳ | ⏳ |

---

## Lecciones Aprendidas

### Lecciones capitalizadas de planes anteriores (REFACTOR-COHERENCIA-NARRATIVA-2026-08-22 + CONTEXT Salento Real)

| Lección | ID original | Aplicación en este plan |
|---------|-------------|--------------------------|
| Ramas no ejercitadas acumulan defectos latentes; smoke E2E con `--output` alternativo + grep de símbolos sospechosos + test estático | L-SR1 | Guardián AST permanente (SR-A); corrida final con `--output` alternativo (SR-H) |
| La identidad de memoria debe derivarse de la URL canónica | L-SR2 | SR-D completo (canonicalización en caller) |
| Promesa, matriz y gate comparten UNA fuente de verdad del estado de un servicio | L-SR3 | SR-B completo (taxonomía única) |
| La confianza de un asset no se degrada por la evidencia del problema que resuelve | L-SR4 | SR-E completo (confianza desde fuentes para construir el asset) |
| Un gate BLOCKING que solo loggea no previene: debe ciclar o escalar | L-SR5 | SR-C completo (self-healing con escalado a BLOCKED real) |
| Fosilización narrativa/decisoria: la capa que no consume la fuente de verdad produce hallazgos recurrentes | L-NC10 | SR-B (promesa consume pain_ledger, no catálogo estático) |
| Verificación E2E > unit tests; variaciones de parámetros detonan ramas ocultas | L-NC11 | SR-H con `--output` alternativo; VERIFY certifica contra output real |
| Diff antes/después como evidencia formal obligatoria | L-NC12 | SR-VERIFY: diff corrida C vs corrida final en todas las zonas afectadas |
| Tras parametrizar, verificar strings de display contra la fuente | L30 | SR-G (tier display contra fuente financiera) |
| Citar fuente de verdad, no hardcodear | L27 | SR-B/SR-G (promesas y tier derivados de fuente) |
| El gap está en el caller: verificar si el helper ya existe | L16 | SR-D usa `_normalize_url()` existente (main.py:3542); SR-A reutiliza rutas de conteo existentes |
| Grep de residuos post-fix | L2 | Cierre de cada fase (0 matches) |
| Tests de contrato contra fuente dinámica, no valores fijos | L3 | SR-B: tests propuesta↔matriz↔gate contra pain_ledger real |
| Para contratos transversales, AST en vez de regex | L7 | SR-A: guardián AST para main.py |
| Símbolo no definido en rama no ejercitada (clase de bug H1/L-NC8/L-NC9) | L-NC8/9 | Guardián AST + smoke de ramas nuevas en cada fase |
| Ejecución segura de suites pytest (memoria 2026-08-03) | — | Archivos específicos, procesos aislados, salida a archivo, sin suite completa |
| log_phase_completion SIN --release en fases intermedias (memoria cierre de fase) | — | Todos los prompts de fase; solo RELEASE usa marker |

### Lecciones nuevas de este plan (L-PF1+ — registrar al cierre de cada fase; mínimo 3 totales)

> Formato: **qué pasó / por qué / qué lo previene** + pertinencia (INCLUIR/EXCLUIR de memoria).

| ID | Lección | Fase |
|----|---------|------|
| L-PF1 | (llenar al cerrar SR-A) | SR-A |
| L-PF2 | (llenar al cerrar SR-B) | SR-B |
| L-PF3 | (llenar al cerrar SR-C) | SR-C |
| L-PF4 | (llenar al cerrar VERIFY) | VERIFY |

---

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Bloqueo estructural proposal_asset_alignment (3ª manifestación) | 🔴 → SR-B | FASE-SR-B |
| Self-healing CG-CLAIM-VS-EVIDENCE | 🔴 → SR-C | FASE-SR-C |
| target_id con query string / fragmentación memoria | 🔴 → SR-D | FASE-SR-D |
| Preflight hotel_schema paradoja + fallback ignorado (N4) | 🔴 → SR-E | FASE-SR-E |
| Varianza plan de assets entre corridas (7→5) | 💡 → SR-F | FASE-SR-F |
| G9 divergente 4-vs-1 (N1) | 🔴 → SR-A | FASE-SR-A |
| CG-TIER-CONSISTENCY + CG-TECH-JARGON | 🔴 → SR-G | FASE-SR-G |
| PageSpeed API key inválida | 💡 OPS → SR-F | Verificación de config en SR-F; ROTACIÓN DE LA KEY = decisión del usuario (no se tocan secretos en el plan) |
| Gate de coherencia usa score agregado e ignora `is_coherent: false` del mismo archivo (CONTEXT §5) | 💡 FUERA DE ALCANCE | Evaluar en plan futuro; no bloquea este plan |
| Fix H1 logger (main.py) | ✅ RESUELTO (d8e509d) | Guardián estático en SR-A cierra la clase |

---

## Métricas de Ejecución (llenar al cierre)

| Métrica | Baseline (corrida C) | Post-fix (corrida final) | Delta |
|---------|----------------------|--------------------------|-------|
| Tests totales | 3,379 | (llenar) | |
| Coherence E2E Salento Real | 0.8644 | (llenar) | |
| Gates de publicación | 12 PASSED + 1 BLOCKED (alignment 43%) | (llenar) | |
| Alineación propuesta-assets | 43% (3/7) | (llenar) | |
| `no_hotel_schema` en pain_ledger | DETECTED | (llenar) | |
| unresolved (gate vs delivery) | 4 vs 1 | (llenar) | |
| Escenarios financieros | $6.57M / $4.04M / $1.26M | (llenar — deben ser idénticos) | 0 |
| readiness | NOT_READY | (llenar) | |

---

## Decisiones Arquitectónicas (pre-registradas en preparación; confirmar implementación en cada fase)

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|-------------------------|------|
| D-PF1 | UNA fuente de verdad del estado de servicio = pain_ledger + present_in_production (SitePresence); reutilizar el concepto `actionable` existente en `proposal_asset_alignment.py:783-789`; NO_BREACH fuera del denominador del gate Y de la tabla de compromiso de la propuesta | Nunca dos criterios en paralelo (L-NC10); el catálogo estático del tier ya demostró fosilización (L-SR3) | (a) Solo que el gate respete NO_BREACH sin tocar la propuesta — dejaría promesas vacías en el texto; (b) crear taxonomía nueva paralela — viola L-NC10 | SR-B |
| D-PF2 | Self-healing CG-CLAIM-VS-EVIDENCE: máx. 1 regeneración con el `suggestion` del gate como restricción; si persiste → BLOCKED real (documentos retenidos, ZIP abortado) | Detectar sin ciclar deja pasar la erosión de credibilidad (L-SR5); el loop infinito es un anti-patrón de gates | (a) Regeneración ilimitada — riesgo de bucle; (b) solo WARNING — mantiene el statu quo | SR-C |
| D-PF3 | Para brechas de ausencia ("no existe X"), la confianza del asset se calcula desde las fuentes disponibles para construir X (GBP/web); el preflight respeta `fallback` + `block_on_failure=False` del catálogo (contrato del catálogo gana — nunca ambos criterios, N4) | Separa "confianza en datos de entrada" de "confianza en implementación del asset" (L-SR4); el catálogo YA declara capacidad de fallback | (a) Eliminar el fallback del catálogo — dejaría el pain #1 estructuralmente irresoluble; (b) bajar el umbral 0.8 — enmascara el problema semántico | SR-E |
| D-PF4 | Canonicalizar la URL al inicio de cada comando con `--url` usando el helper EXISTENTE `_normalize_url()` (L16: el gap está en el caller); URL original solo para scraping | Reutilización sobre código nuevo; el helper ya ignora protocolo/www/path/query | (a) Crear normalizador nuevo; (b) normalizar solo en memory.py — dejaría los call sites inconsistentes | SR-D |
| D-PF5 | Guardián estático L-SR1 como test AST extensible (lista de símbolos prohibidos, inicia con `logger`) sobre main.py | Prevención permanente de la clase "símbolo no definido en rama no ejercitada" (H1, L-NC8/9) | (a) Solo grep manual — no es verificable en CI/validaciones | SR-A |
| D-PF6 | SR-F con outcome condicional pre-decidido: si la causa de la varianza es un filtro determinista erróneo → fix mínimo + test; si requiere rediseño mayor → seguimiento documentado (sin agrandar la fase) | Respeta R3; la investigación no puede inflarse en una fase de fixes | Dejar el outcome abierto — decisión incompleta viola el principio decision-complete | SR-F |

---

## Checklist de Cierre (FASE-RELEASE — llenar al cierre)

- [ ] Todas las fases ✅ en `06-checklist-implementacion.md` (SR-A a SR-H + VERIFY)
- [ ] Matriz de Verificación completa: 13/13 ACs con Real/Status
- [ ] Lecciones nuevas registradas (mínimo 3, formato qué pasó/por qué/qué lo previene)
- [ ] Métricas de Ejecución post-fix completadas
- [ ] VERSION.yaml == "4.73.0" + sync 6 archivos + Version Sync Gate OK
- [ ] CHANGELOG `[4.73.0]` + GUIA_TECNICA "Notas de Cambios v4.73.0"
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] README/AGENTS audit: test count verificado contra `pytest --collect-only`
- [ ] Seguimientos abiertos: ninguno o con plan asignado
- [ ] Commit de release ejecutado
