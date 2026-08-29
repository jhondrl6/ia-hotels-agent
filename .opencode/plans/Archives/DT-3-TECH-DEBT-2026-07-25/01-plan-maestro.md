# Plan Maestro: DT-3 — Technical Debt Post-DT-2

> **Origen**: CONTEXT-DT-3-TECH-DEBT-POST-DT2.md (auditado contra código vivo 2026-07-25)
> **Versión objetivo**: v4.64.0
> **Versión actual**: v4.63.2 (tag v4.63.2, commit dd576a2)
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Sesiones estimadas**: 5 fases + RELEASE = 6 sesiones
> **Estimación total**: ~8-10h

---

## Resumen Ejecutivo

Post-DT-2, el delivery pipeline de iah-cli tiene 4 bugs reales (1 CRÍTICO, 2 MEDIOS, 1 deuda técnica documentada) que bloquean la generación de entregables para hoteles como Zi One Luxury. La causa raíz sistémica es una migración parcial de rutas flat → per-hotel (BUG-1): 3 archivos JSON se leen de ruta incorrecta, causando que ProposalAssetMatrix reciba un pain_ledger vacío → 8/8 NO_BREACH → G9 FAIL → delivery bloqueado.

Este plan ejecuta 5 fases de implementación + RELEASE, priorizando el fix de causa raíz antes que la deuda técnica de unificación (P-04).

---

## Bugs y Deuda Técnica

| ID | Severidad | Descripción | Archivos | Líneas |
|----|-----------|-------------|----------|--------|
| BUG-1 | **CRÍTICO** | Half-fix sistémico: 3 JSONs con ruta flat inexistente | main.py | L2571, L2572, L2650 |
| BUG-2 | MEDIO | G9 dual-list: aparece en blocking_gates Y warning_gates | delivery_quality_report.py | L251-258 |
| BUG-3 | MEDIO | G9 evalúa asset_path, no status (NO_BREACH vs MISSING_ASSET) | delivery_quality_report.py | L201-204 |
| BUG-4 | MEDIO | Divergencia semántica ProposalAssetMatrix vs AlignmentReport (P-04) | proposal_asset_alignment.py | L60, L439 |
| ~~BUG-5~~ | ~~REFUTADO~~ | ~~PAIN_SOLUTION_MAP incompleto~~ | ~~pain_solution_mapper.py~~ | — |

---

## Fases del Plan

| Fase | Título | Complejidad | delegate_task | Tareas | Comando largo | R3 |
|------|--------|-------------|---------------|--------|---------------|-----|
| **FASE-0** | Fix sistémico rutas flat → per-hotel (BUG-1) | MEDIA | ✅ VIABLE | 4 | No | ✅ |
| **FASE-1** | Fix G9 dual-list + status-based eval (BUG-2, BUG-3) | BAJA | ✅ VIABLE | 3 | No | ✅ |
| **FASE-2** | Unificar ProposalAssetMatrix + AlignmentReport (BUG-4/P-04) | **ALTA** ⚠️ | ❌ NO VIABLE | 4 | No | ✅ |
| **FASE-3** | v4complete Zi One + verificación post-fix | MEDIA | ⚠️ MIXTO | 3 | v4complete (1) | ✅ |
| **FASE-RELEASE** | Documentación, version bump, release tagging | BAJA | ✅ VIABLE | 4 | No | ✅ |

---

## Fase de Mayor Complejidad Técnica: FASE-2

**FASE-2 (Unificar ProposalAssetMatrix + AlignmentReport)** es la fase de mayor complejidad por:

1. **Decisión arquitectónica no trivial**: Fusionar dos taxonomías semánticas ortogonales (analytics pain-driven × delivery asset-existence) en un solo contrato canónico
2. **Multi-module**: Afecta proposal_asset_alignment.py + delivery_quality_report.py + main.py
3. **Riesgo de regresión**: 42 tests existentes deben seguir pasando; G9 es un gate blocking
4. **Consumidores múltiples**: G9, publication_gates.py, v4_proposal_generator.py, tests/test_proposal_alignment.py
5. **No delegable**: Requiere el agente principal para la decisión arquitectónica (el contexto lo explicita en §7.6)

**Mitigaciones**:
- FASE-0 y FASE-1 deben estar completadas (datos reales para validar el contrato unificado)
- Tests existentes como red de seguridad (42/42 PASS)
- v4complete en FASE-3 como verificación E2E

---

## delegate_task Viability Matrix

| Fase | ¿Viable? | Razón | Riesgo |
|------|----------|-------|--------|
| FASE-0 | ✅ **VIABLE** | Code-editing puro (3 líneas + helper). No ejecuta imports del proyecto | WSL venv no requerido |
| FASE-1 | ✅ **VIABLE** | Fixes pequeños (~10 líneas) en un solo archivo. Sin imports | WSL venv no requerido |
| FASE-2 | ❌ **NO VIABLE** | Decisión arquitectónica requiere agente principal (§7.6 del contexto). Multi-module, cross-taxonomy merge | Subagente no tiene contexto de las dos taxonomías |
| FASE-3 | ⚠️ **MIXTO** | v4complete → delegate_task (comando largo). Análisis → DIRECTO (requiere contexto completo del plan) | Timeout 900s; ver patrón MIXTO en skill |
| FASE-RELEASE | ✅ **VIABLE** | Solo YAML/MD editing + scripts de validación. Sin imports del proyecto | Skill confirma viabilidad (worked example: BUGS-ONBOARDING-ADR FASE-5, 4m4s) |

---

## Criterios de Éxito (DoD)

| # | Criterio | Fase que lo cubre | Verificable en |
|---|----------|-------------------|----------------|
| S-1 | 3 rutas flat → per-hotel corregidas | FASE-0 | main.py L2571, L2572, L2650 |
| S-2 | Helper _get_pipeline_path() creado y usado | FASE-0 | main.py |
| S-3 | pain_ledger se carga con 9 entries para Zi One | FASE-0 | v4complete output |
| S-4 | G1 coherence sync funcional post-fix | FASE-0 | v4complete output |
| S-5 | G9 no aparece en warning_gates si está en blocking_gates | FASE-1 | delivery_quality_report.json |
| S-6 | G9 evalúa status (NO_BREACH=skip, MISSING_ASSET=fail, LINKED=pass) | FASE-1 | delivery_quality_report.py L201-204 |
| S-7 | ProposalAssetMatrix + AlignmentReport → contrato canónico unificado | FASE-2 | proposal_asset_alignment.py |
| S-8 | G9 consume el contrato unificado | FASE-2 | delivery_quality_report.py |
| S-9 | 42 tests existentes siguen pasando | FASE-2 | pytest |
| S-10 | Tests nuevos cubren contrato unificado + edge cases G9 | FASE-2 | test_delivery_contract.py |
| S-11 | ZIP generado para Zi One con assets reales | FASE-3 | output/v4_complete/ |
| S-12 | P-01, P-02, P-06 verificados en ZIP real | FASE-3 | MANIFEST.json + README.md en ZIP |
| S-13 | v4complete post-fix: G9 PASS o WARNING legítimo (no falso positivo) | FASE-3 | delivery_quality_report.json |
| S-14 | VERSION.yaml → 4.64.0, CHANGELOG actualizado, tag creado | FASE-RELEASE | git tag, VERSION.yaml |

---

## Restricciones Globales

1. **Una fase = una sesión**: No ejecutar múltiples fases en la misma sesión
2. **FASE-0 antes que FASE-2**: Unificar sobre datos incorrectos = contrato canónico incorrecto (§12 del contexto)
3. **Safety guard WSL**: No usar `rm -rf` directamente (skill `wsl-safety-guard-bypass`)
4. **pytest**: `./venv/Scripts/python.exe -m pytest` (Windows venv)
5. **v4complete**: `./venv/Scripts/python.exe main.py v4complete --url https://zione.co/`
6. **Pre-commit**: `version_consistency_checker.py` (BLOCKING) + `sync_versions.py --check` (advisory)
7. **NO modificar**: PAIN_SOLUTION_MAP (BUG-5 refutado), pipeline de producción, SitePresenceChecker, CoherenceValidator

---

## Archivos del Plan

```
/.opencode/plans/Archives/DT-3-TECH-DEBT-2026-07-25/
├── 01-plan-maestro.md                 ← ESTE ARCHIVO
├── 02-prompt-fase-0.md                ← Fix sistémico BUG-1
├── 03-prompt-fase-1.md                ← Fix G9 BUG-2 + BUG-3
├── 04-prompt-fase-2.md                ← Unificación P-04 (MAYOR COMPLEJIDAD)
├── 05-prompt-fase-3.md                ← v4complete Zi One + verificación
├── 06-prompt-fase-release.md          ← RELEASE v4.64.0
├── 07-checklist-implementacion.md     ← Tracker maestro
├── 08-analisis-post-implementacion.md ← Template (completar post-ejecución)
└── dependencias-fases.md              ← Grafo de dependencias + conflictos
```

---

## Orden de Ejecución

```
FASE-0 (BUG-1)
  └── Fix rutas flat → per-hotel
      └── FASE-1 (BUG-2 + BUG-3)
          └── Fix G9 dual-list + status-based eval
              └── FASE-2 (BUG-4 / P-04)
                  └── Unificar ProposalAssetMatrix + AlignmentReport
                      └── FASE-3 (v4complete + verificación)
                          └── Ejecutar v4complete Zi One + análisis post-fix
                              └── FASE-RELEASE
                                  └── Docs cascade, version bump v4.64.0, tag
```

---

## Anti-Patrones del Plan

1. **NO crear un tercer sistema**: El contrato unificado reemplaza (no coexiste con) ProposalAssetMatrix y AlignmentReport
2. **NO eliminar G9**: G9 es valioso como gate. El problema es la taxonomía que usa
3. **NO tocar el pipeline de producción**: SitePresenceChecker, CoherenceValidator, scenario_calculator.py fuera de alcance
4. **NO cambiar semántica de NO_BREACH para hoteles existentes**
5. **NO romper backward compatibility**: create_readme() legacy mode, delivery_quality_report.json, proposal_asset_matrix.json
6. **NO usar delegate_task para decisiones arquitectónicas** (FASE-2)
7. **NO ejecutar FASE-2 sin antes completar FASE-0 y FASE-1**

---

## Post-Implementación

Al completar todas las fases, el archivo `08-analisis-post-implementacion.md` debe contener:

- Tabla resumen de ejecución (fase, sesión, iteraciones, estado, delegate_task usado)
- Análisis de FASE-2 (mayor complejidad): ¿por qué fue la más compleja? ¿mitigaciones efectivas?
- Verificación de los 14 criterios DoD (S-1 a S-14)
- Lecciones aprendidas
- Deuda técnica remanente (si aplica)
