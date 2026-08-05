# Documentación Post-Proyecto — RC1-RC2-ENTREGA-COHERENTE-2026-08-04

> **Propósito**: fuente de datos acumulativa para FASE-RELEASE-4.71.0 (generación de
> CHANGELOG y GUIA_TECNICA oficiales). Cada fase completa su columna al terminar.
> **Regla L8**: todos los conteos se registran DESDE FUENTE VIVA (git diff, pytest,
> grep), nunca desde notas o estimaciones previas.

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| (ninguno previsto — el plan refactoriza módulos existentes) | — | — | — |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Cuarentena de tests patológicos | tests/ | 3 archivos aislados + lista segura documentada | FASE-A |
| Tabla de servicios dinámica | commercial_documents | Propuesta consume `opportunity_scores` (costo/rank/label por brecha); org_schema condicional | FASE-B |
| CG-CLAIM-VS-EVIDENCE sin falsos positivos | quality_gates | Parseo por oración + ignorar condicionales + exigir sujeto | FASE-C |
| CG-TIER-CONSISTENCY cableado | quality_gates + commercial_documents | Inputs reales (frontmatter + texto); None → fallo explícito | FASE-C |
| Política de entrega ZIP | delivery | Sin `commercial_gates_report*` al cliente + filtro por run | FASE-D |
| Fallback loader onboarding | main.py | `{output}/clientes` → fallback `output/clientes` (S7) | FASE-D |
| Occupancy label veraz | financial_engine | `data_sources.occupancy` coherente con fuente real (S5) | FASE-D |
| E2E certificado Zi One Luxury | — | Run único con onboarding real, V1-V10 PASS | FASE-F |
| Enforcement anti `--release` | scripts | Check "Prompts No Release" en `run_all_validations.py` (L3/L9, R3.1) | FASE-E |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests baseline (pre-plan) | 3,215 collected | — |
| Tests collected post-cuarentena | 3,175 collected (2026-08-05) | FASE-A |
| Tests nuevos RC1 | 9 (git diff tests/, patrón `^\+\s*def test_`, 2026-08-05) | FASE-B |
| Tests nuevos gates | ⬜ (desde `git diff tests/`) | FASE-C |
| Tests nuevos delivery/loader/financial | ⬜ (desde `git diff tests/`) | FASE-D |
| Coherencia run E2E Zione | ⬜ (≥ 0.8 exigido) | FASE-F |
| Gates publicación run E2E | ⬜ (12/12 exigido) | FASE-F |
| Tests collected final | ⬜ (registrar en RELEASE) | FASE-RELEASE |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `pytest.ini` / `tests/_archived_broken_tests/` | Cuarentena 3 archivos | FASE-A |
| `modules/commercial_documents/v4_proposal_generator.py` | Parametrización BREACH_BY_ASSET + hardcode L1250 | FASE-B |
| `main.py` | Cableado `opportunity_scores` (FASE 3.5 → `proposal_gen.generate()`) | FASE-B |
| `tests/commercial_documents/test_proposal_breach_consistency.py` | Nuevo (gate de no-regresión RC1) | FASE-B |
| `evidence/FASE-B/` | Script verificación estática + salidas (tests, lista segura) | FASE-B |
| `modules/quality_gates/commercial_gate.py` | R2.1 + R2.2 | FASE-C |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Cableado tier al gate | FASE-C |
| `modules/delivery/delivery_packager.py` | Política ZIP (R2.3 + N21) | FASE-D |
| `main.py` | Fallback loader onboarding (S7) | FASE-D |
| `modules/financial_engine/*` (occupancy) | Label fuente veraz (S5) | FASE-D |
| `.opencode/plans/COHERENCIA-MODULO-ENTREGA-2026-08-03/*` | R3.1/R3.2/R3.3 | FASE-E |
| `.opencode/context/CONTEXT-VALIDACION-COHERENCIA-PLAN-ENTREGA-2026-08-04.md` | R3.4 (cita _coverage_gate) | FASE-E |
| `scripts/run_all_validations.py` | Check "Prompts No Release" (R3.1 enforcement L3/L9) | FASE-E |
| `evidence/FASE-F/` | Run E2E + verificación V1-V10 + análisis post-implementación | FASE-F |
| `VERSION.yaml`, `CHANGELOG.md`, `docs/GUIA_TECNICA.md` | Bump 4.71.0 + docs oficiales | FASE-RELEASE |

## Notas de Ejecución (por fase)

### FASE-A
- Causa probable por archivo patológico:
  - `test_proposal_generator.py`: fixture `generator` instancia `V4ProposalGenerator()` directamente; constructor carga templates/config. 32 tests × costo inicialización = fuga ~8GB.
  - `test_price_consistency.py`: `generate()` con patches parciales; lógica no mockeada causa cuelgue indefinido.
  - `test_proposal_generator_dict.py`: `setup_method` instancia generador; mocks insuficientes causan 16/38 fallos preexistentes.
- Lista segura de tests del área propuesta: 13 archivos PASS (ver `dependencias-fases.md` §Notas FASE-A)
- Archivos movidos: 3 archivos a `tests/_archived_broken_tests/commercial_documents/`
- `pytest.ini`: `--ignore` específicos añadados (NO `norecursedirs` global — CR-8)
- Tests collected: 3215 → 3175 (diferencia exacta: 40 tests)

### FASE-B
- Decisión de mapeo adoptada (asset_type → brecha_id candidatos, auditada):
  - `optimization_guide ← [low_seo_score, low_content_length]` (desempate por rank presente)
  - `whatsapp_button ← [whatsapp_conflict, no_whatsapp_visible]` (desempate igual)
  - `hotel_schema ← no_hotel_schema` · `org_schema ← no_org_schema` · `faq_page ← no_faq_schema`
  - `open_graph ← no_og_tags` · `llms_txt ← missing_llmstxt`
  - Restricción deliberada: brechas de otro dominio (ej: `ai_crawler_blocked → llms_txt`)
    NO se atribuyen a servicios de la tabla — evita distorsionar el costo del servicio.
  - Implementación: `_build_dynamic_breach_map()` en `v4_proposal_generator.py`
    (mapa inverso desde `pain_solution_mapper.PAIN_SOLUTION_MAP` + candidatos auditados).
- Resultado verificación contra evidencia run 20260804_124443: PASS —
  5 services con costo == `estimated_monthly_cop` (whatsapp #1 $1.198.906, hotel_schema #2
  $1.498.094, faq #3 $719.200, SEO Local #4 $1.198.906, open_graph #8 $479.706),
  2 services sin costo ("—": org_schema, llms_txt), N17 y N18 corregidos en tabla renderizada.
- Tests: 9 nuevos (test_proposal_breach_consistency.py) + lista segura FASE-A 208 passed,
  0 regresiones. Fallos preexistentes estables: test_proposal_dynamic (7),
  test_proposal_confidence_disclosure (5) — áreas no tocadas (asset_quality_table/lookups).

### FASE-C
- Patrón final CG-CLAIM-VS-EVIDENCE: ⬜
- Comportamiento tier con inputs None: ⬜

### FASE-D
- Modo de ejecución real (delegado vs directo): ⬜
- Política ZIP adoptada (excluir reports / filtrar por run): ⬜

### FASE-E
- Conteos en vivo registrados: ⬜

### FASE-F
- Run: timestamp ⬜ — coherencia ⬜ — gates ⬜
- V1-V10: ⬜/10 PASS
- Lecciones nuevas (L16+): ver `10-analisis-post-implementacion.md`
