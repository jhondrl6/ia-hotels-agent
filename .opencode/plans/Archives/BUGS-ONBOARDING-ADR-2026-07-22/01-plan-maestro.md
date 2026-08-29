# Plan Maestro: BUGS-ONBOARDING-ADR-2026-07-22

> **Fecha**: 2026-07-22
> **Contexto origen**: `/.opencode/context/Historico/BUGS-ONBOARDING-ADR-TEMPLATE-2026-07-22.md`
> **Hotel de prueba**: Hotel Don Alfonso (https://www.donalfonsohotel.com/)
> **Datos reales**: `data/hotel_observations/observations.json` (entry: Hotel Don Alfonso)
> **Estado base**: 700 tests pasan, 55 fallan (preexistentes, no relacionados)
> **Convención**: 1 fase = 1 sesión. Sin excepciones.

---

## 1. Resumen Ejecutivo

Se ejecutó v4complete dos veces para Hotel Don Alfonso. La comparación reveló **3 bugs + 4 hallazgos sistémicos** que degradan la precisión financiera y la experiencia del documento. El plan aplica la **Opción C (robusta, recomendada)** del contexto: fix root cause + cascada + unificación de taxonomía + tests e2e + verificación con v4complete.

## 2. Hallazgos a Corregir

| ID | Hallazgo | Severidad | Fase |
|----|----------|-----------|------|
| BUG-1 | ADR de onboarding ignorado en payload del harness | CRÍTICA | FASE-1 |
| NEW-1 | Occupancy_rate sobrescrito por regional en handler | CRÍTICA | FASE-1 |
| F3 | `adr_source="handler"` placeholder muerto en JSON | MEDIA | FASE-1 |
| H1 | Consumidor paralelo divergente en proposal generator | ALTA | FASE-2 |
| H3 | Falsa confianza + falsa procedencia en ValidationSummary | ALTA | FASE-2 |
| H2 | 3 vocabularios incompatibles para "fuente del ADR" | ALTA | FASE-3 |
| BUG-2 | Template "Complete onboarding" siempre visible (7 CTAs) | ALTA | FASE-3 (Opción C: centralizar) |
| H4 | Sin tests e2e onboarding → harness → JSON | MEDIA | FASE-4 |
| BUG-3 | Escenario optimista negativo (diseño, no bug) | BAJA | No incluido |

## 3. Dependencias entre fases

```
FASE-1 (root cause) ──→ FASE-2 (cascade: proposal + validation)
                   ──→ FASE-3 (cascade: taxonomy + CTA)
FASE-2 + FASE-3    ──→ FASE-4 (e2e + v4complete + análisis)
FASE-4             ──→ FASE-5 (RELEASE)
```

FASE-2 y FASE-3 son independientes entre sí pero ambas dependen de FASE-1.

## 4. Complejidad técnica por fase

| Fase | Complejidad | Justificación |
|------|-------------|---------------|
| FASE-1 | MEDIA | 2 archivos, ~15 líneas. Cambios localizados en payload + handler. |
| **FASE-2** | **ALTA (mayor)** | **Toque arquitectónico: romper invariante value↔source en ValidationSummary + integrar ADR del onboarding en proposal generator (path paralelo con su propio resolver). 2 módulos, cascade de datos跨-capas.** |
| FASE-3 | ALTA | Unificar 3 vocabularios + centralizar 7 CTAs en función `_build_onboarding_cta` (Opción C). Mucha surface area pero cambios mecánicos + 1 función nueva. |
| FASE-4 | MEDIA | Tests + v4complete (5-10 min runtime). Verificación visual. |
| FASE-5 | BAJA | Mechanical: version bump, changelog, docs. |

## 5. delegate_task — Matriz de viabilidad

| Fase | ¿Viable? | Tipo | Razón |
|------|----------|------|-------|
| FASE-1 | ✅ SÍ | SUBAGENTE | Spec completa, 2 archivos, cambios precisos del contexto. |
| FASE-2 | ✅ SÍ | SUBAGENTE | Spec completa con código ANTES/DESPUÉS. Requiere razonamiento pero auto-contenido. |
| FASE-3 | ✅ SÍ | SUBAGENTE | Cambios mecánicos de strings + condicionales. Spec completa. |
| FASE-4 | ⚠️ PARCIAL | MIXTO | Tests → delegate_task. v4complete → terminal background + timeout 900s. |
| FASE-5 | ✅ SÍ | SUBAGENTE | Mechanical: version bump, changelog, pre-commit. |

## 6. Fase de mayor complejidad técnica: FASE-2

**FASE-2** es la fase de mayor complejidad técnica porque:

1. **Rompe un invariante arquitectónico** (H3): actualmente `confidence=VERIFIED` y `sources=["Onboarding"]` se derivan de `adr_from_onboarding_verified` (flag de existencia), pero `value` viene de `adr_cop` (que puede ser regional). El fix requiere rastrear la fuente REAL del valor a través del pipeline, no solo si el onboarding fue cargado.

2. **Integra un path paralelo divergente** (H1): `v4_proposal_generator.py:1859` instancia su propio `RegionalADRResolver` con `user_provided_adr=None`. El fix debe hacer que el proposal generator reciba el ADR del orquestador, lo que requiere cambiar la firma de `_get_adr_from_benchmarks` o inyectar el valor desde el caller en L760.

3. **Cross-module data flow**: el fix toca `main.py` (ValidationSummary construction, L2150-2187) + `v4_proposal_generator.py` (ADR resolution, L760 + L1859-1873). El subagent debe entender el flujo de datos entre orquestador → proposal generator.

**Mitigaciones**: prompt auto-contenido con snippets ANTES/DESPUÉS del contexto, verificación post-patch con grep de invariantes, y test de regresión incluido en la misma fase.

## 7. Definition of Done (DoD) global

- [ ] ADR=$330,000 COP en todas las superficies (diagnóstico, propuesta, JSON) post-fix
- [ ] Occupancy=0.4242 en JSON post-fix (no 0.512 regional)
- [ ] `adr_source != "handler"` en JSON post-fix
- [ ] `ValidationSummary.confidence` consistente con la fuente REAL del valor
- [ ] CTA "Complete el onboarding" NO aparece cuando hay onboarding cargado
- [ ] ADR consistente entre diagnóstico y propuesta (mismo valor)
- [ ] Tests e2e: YAML → harness → JSON → documento
- [ ] v4complete ejecutado para Hotel Don Alfonso con análisis post-implementación
- [ ] 700 tests preexistentes siguen pasando (no regressión)
- [ ] RELEASE: CHANGELOG + version sync + pre-commit

## 8. Datos de prueba esperados (Hotel Don Alfonso)

| Campo | Valor esperado post-fix | Valor actual (bug) |
|-------|------------------------|-------------------|
| adr_cop | 330,000 | 420,000 |
| occupancy_rate | 0.4242 | 0.512 |
| adr_source | "user_provided" o "onboarding" | "handler" |
| OTA commission | ~$4,851,000/mes | $6,174,000/mes |
| Realistic | ~$2,481,000/mes | $3,157,862/mes |
| Conservative | ~$5,503,000/mes | $7,004,068/mes |

## 9. Deuda técnica post-plan (Opción D no implementada)

El plan implementa Opción C (robusta) para BUG-1+NEW-1 y Opción C (centralizada) para BUG-2. La Opción D (refactor mayor) del contexto queda como deuda técnica explícita, registrada en `ROADMAP.md` §13 (item 13):

**Lo que Opción C cubre y D no es necesaria**:
- BUG-1, NEW-1, H1, H3, F3: fixeados puntuamente
- BUG-2: centralizado en `_build_onboarding_cta` (Opción C)
- H4: tests e2e cierran el pipeline

**Lo que Opción D habría cubierto y C deja como deuda**:
- **Consolidación total de vocabularios**: C hace que el discriminador matchee, pero los 3 vocabularios (ADRSource enum, ValidationSummary.sources, JSON adr_source) siguen existiendo como 3 cosas distintas. D los consolidaría en una sola taxonomía.
- **build_validated_field centralizado**: C fixea los 3 casos puntuales (adr_cop, occupancy, direct_channel). D extraería `build_validated_field(name, value, source)` para que todo nuevo campo validado tenga la invariante value↔source por construcción.
- **Contrato de tipos para payload del harness**: C agrega keys al payload dict. D migraría a un contrato de tipos (dataclass/TypedDict) que previene olvidar keys por construcción.

**Riesgo de la deuda**: un nuevo campo validado o un nuevo CTA puede cometer el exact mismo error que BUG-1/BUG-2. La mitigación son los tests e2e de FASE-4, pero la prevención por construcción solo viene con D.

**Registro**: ROADMAP.md §13 item 13 (agregado en esta sesión).

## 10. Estructura del plan

```
/.opencode/plans/Archives/BUGS-ONBOARDING-ADR-2026-07-22/
├── 01-plan-maestro.md                    # Este archivo
├── 02-prompt-fase-1.md                   # Root cause: ADR + occupancy propagation
├── 03-prompt-fase-2.md                   # Cascade: proposal + validation (MAYOR COMPLEJIDAD)
├── 04-prompt-fase-3.md                   # Taxonomy + CTA fix
├── 05-prompt-fase-4.md                   # E2E + v4complete + análisis
├── 06-prompt-fase-5-release.md           # RELEASE
├── 07-checklist-implementacion.md        # Tracking
└── 08-analisis-post-implementacion.md    # Retrospectiva
```
