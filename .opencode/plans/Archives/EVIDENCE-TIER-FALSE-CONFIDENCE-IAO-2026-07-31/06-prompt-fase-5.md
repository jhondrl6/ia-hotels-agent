# FASE-5: v4complete Zi One + Control Sin Onboarding + Post-Implementation Analysis

> **REGLA**: Una fase = una sesion. No ejecutar multiples fases aqui.
> **Tipo de ejecucion**: **MIXTO** — delegate_task para v4complete + DIRECTO para analisis
> **Complejidad**: MEDIA
> **Depende de**: FASE-4 completada (tests verdes)
> **Auditoria 2026-07-31**: Ampliada con T0 (control de regresion sin onboarding — NP8). Sin este control, no se verifica que el fix no rompe el caso default Tier C (leccion previa §6 "Regresion en hoteles sin onboarding" no verificada).

## Contexto previo

FASE-1 a FASE-4 completadas. Tests verdes. Codigo de produccion implementado:
- Evidence tier honesto (B+ sin GA4, A solo con GA4+GSC real)
- Consumers downstream limpios (hook_pdf_generator, publication_gates, v4_diagnostic_generator default)
- Propuesta sin mentiras de tier, has_onboarding sin fallback silencioso
- Gate `CG-EVIDENCE-TIER-CONSISTENCY` per-hotel bloquea delivery fraudulento
- MANIFEST enriquecido en `delivery_packager.py` con quality_metadata
- Tests unitarios + integracion + gate + actualizacion de tests pre-existentes pasando

**AHORA**: Verificar que todo funciona en casos reales (con y sin onboarding).

## Objetivo de esta fase

Ejecutar v4complete para dos hoteles de control:
1. **Zi One Luxury** (con onboarding, sin GA4) → debe generar Tier B+ (no A)
2. **Hotel de control sin onboarding** (hotel_test_001) → debe generar Tier C (sin regresion)

Verificar que los 20 hallazgos (12 originales + 8 nuevos NP1-NP8) fueron resueltos. Generar analisis post-implementacion con lecciones aprendidas.

### Estrategia MIXTO

| Componente | Ejecucion | Razon |
|-----------|-----------|-------|
| v4complete Zi One (T1) | **delegate_task** (timeout=900, toolsets=["terminal"]) | 5-10 min wall-clock, no bloquea iteracion |
| v4complete hotel_test_001 (T0) | **delegate_task** (timeout=900, toolsets=["terminal"]) | Mismo patron que Zi One, control de regresion |
| Copia de evidencia | **main agent** DIRECTO | Necesita contexto de paths |
| Verificacion 20 hallazgos | **main agent** DIRECTO | Requiere plan completo + contexto de fases |
| Analisis post-implementacion | **main agent** DIRECTO | Requiere comprension de todas las fases |

### Tareas

#### T0 (NUEVA — Control de regresion sin onboarding, NP8)

- [ ] **T0 — v4complete hotel_test_001 (control sin onboarding)**: Ejecutar v4complete para un hotel SIN datos de onboarding (`output/hotel_test_001/`) para verificar que el fix no introduce regresion:
  ```
  delegate_task(
    goal="Execute v4complete for hotel_test_001 (control hotel sin onboarding)",
    context="Working directory: /mnt/c/Users/Jhond/Github/iah-cli. Command: ./venv/Scripts/python.exe main.py v4complete --url https://example-hotel-sin-onboarding.com/ --force-new",
    timeout=900,
    toolsets=["terminal"]
  )
  ```
  **Expected**:
  - `evidence_tier = "C"` (NO "B+", NO "A") — porque no hay onboarding ni GA4
  - `disclaimer` = "Estimacion basada en datos limitados de su web..."
  - `precision_tier = "C"`
  - Gate `CG-EVIDENCE-TIER-CONSISTENCY` pasa (porque tier no es A)
  - **Si tier es "B+"**: HAY REGRESSION — el fix está asignando B+ a hoteles sin onboarding. Investigar.
  - **Si tier es "A"**: REGRESSION CRITICA — mismo bug del plan original.

- [ ] **T0.b — Verificar no-regresion en default Tier C**: Confirmar que el fix no rompió el caso default. Hotel sin onboarding + sin GA4 → Tier C. Documentar evidencia.

#### Tareas principales (T1-T4)

- [ ] **T1 — Ejecutar v4complete via delegate_task (Zi One Luxury)**:
  ```
  delegate_task(
    goal="Execute v4complete for Zi One Luxury (https://zione.co/)",
    context="Working directory: /mnt/c/Users/Jhond/Github/iah-cli. Command: ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --force-new",
    timeout=900,
    toolsets=["terminal"]
  )
  ```

- [ ] **T2 — Copiar evidencia**: Guardar outputs del v4complete Zi One en `evidence/FASE-5/` del plan. Guardar outputs del v4complete hotel_test_001 en `evidence/FASE-5/control-sin-onboarding/`.

- [ ] **T3 — Verificar matriz de 20 hallazgos**: Cross-check de cada hallazgo contra el nuevo output. **20 hallazgos** = 12 originales del plan + 8 nuevos NP1-NP8.

- [ ] **T4 — Generar analisis post-implementacion**: Completar `09-analisis-post-implementacion.md`.

### Restricciones

- **NO continuar a RELEASE si v4complete Zi One o v4complete control falla o timeout.**
- **NO asumir que el v4complete paso sin verificar el output.**
- **Usar delegate_task solo para los comandos largos.** El analisis lo hace el main agent.
- **La verificacion debe ser exhaustiva**: leer cada seccion del output y confirmar cada hallazgo.
- **T0 (control) y T1 (Zi One) son AMBOS necesarios.** Sin T0, no se verifica no-regresion.
- **T0 es critico**: si v4complete control genera Tier B+ o A, hay un bug grave en el fix que requiere rollback.

### Criterios de completitud

#### T0 (Control — NP8)

- [ ] v4complete hotel_test_001 ejecutado
- [ ] `evidence_tier` = "C" (NO "B+", NO "A")
- [ ] Gate `CG-EVIDENCE-TIER-CONSISTENCY` pasa (tier != A)
- [ ] `precision_tier` = "C"
- [ ] `disclaimer` coherente con Tier C
- [ ] NO hay regresion (Tier C default preservado)

#### T1-T4 (Zi One + Analisis)

- [ ] v4complete para Zi One Luxury ejecutado (o documentar timeout/error)
- [ ] Zi One: `financial_evidence_tier` en frontmatter es "B+" (NO "A")
- [ ] Zi One: El disclaimer NO dice "Google Analytics y Search Console verificados"
- [ ] Zi One: Las Fuentes de Datos muestran honestamente "GA4: No configurado"
- [ ] Zi One: La propuesta NO dice "benchmarks regionales" (usa datos de onboarding)
- [ ] Zi One: `has_onboarding` = True (Zi One tiene onboarding cargado)
- [ ] Zi One: `precision_tier` visible en el documento
- [ ] Zi One: MANIFEST.json incluye `quality_metadata` (en delivery_packager.py output)
- [ ] Zi One: `CG-EVIDENCE-TIER-CONSISTENCY` en el gate report (passed porque tier != A)
- [ ] Zi One: `tier_explanation.relationship` usa tier dinamico (no "B" hardcodeado)
- [ ] **NP1**: `hook_pdf_generator.py` produce PDFs sin WARN de tier invalido
- [ ] **NP2**: `publication_gates.py:399` muestra tier_message coherente con tier real (no "Tier C evidence" para B+)
- [ ] **NP4**: `v4_diagnostic_generator.py` default "C" cuando no hay financial_breakdown
- [ ] **NP5**: `v4_proposal_generator.py` usa param `has_onboarding` correctamente (no fallback silencioso)
- [ ] **NP6**: MANIFEST.json incluye `quality_metadata` (verificado en `output/v4_complete/deliveries/`)
- [ ] **NP7**: Gate `CG-EVIDENCE-TIER-CONSISTENCY` usa params per-hotel (verificable en logs)
- [ ] **20/20 hallazgos verificados** contra el nuevo output
- [ ] `09-analisis-post-implementacion.md` completado

### Matriz de verificacion (20 hallazgos)

#### Originales del plan (12)

| # | Hallazgo | Que verificar en el nuevo output | Expected |
|---|----------|----------------------------------|----------|
| 1 | Tier A falso sin GA4 | `financial_evidence_tier` en frontmatter | "B+" |
| 2 | Disclaimer "GA4 verificado" mintiendo | Disclaimer en doc | NO dice "GA4 verificado" |
| 3 | Contradiccion lineas 84 vs 215 vs 276 | Consistencia entre CTA, disclaimer, fuentes | Consistente |
| 4 | `_determine_evidence_tier` sin check GA4 | Tier en financial_scenarios.json | "B+" |
| 5 | `EvidenceTier.A.disclaimer` falso | N/A (tier no es A) | N/A |
| 6 | `has_onboarding` hardcodeado False | Propuesta dice "datos operativos verificados" | SI |
| 7 | Propuesta dice 3 tiers diferentes | Disclaimer en propuesta | Un solo tier |
| 8 | relationship text hardcodeado "B" | `tier_explanation.relationship` en JSON | Usa tier real |
| 9 | precision_tier no visible | Documento muestra precision_tier | Visible |
| 10 | Template legend sin B+ | Leyenda de tiers | Incluye B+ |
| 11 | Sin gate GA4/GSC | Gate report | CG-EVIDENCE-TIER-CONSISTENCY presente |
| 12 | MANIFEST sin metadata | MANIFEST.json | Incluye quality_metadata |

#### Nuevos NP1-NP8 (8)

| # | Hallazgo | Que verificar en el nuevo output | Expected |
|---|----------|----------------------------------|----------|
| 13 | **NP1**: hook_pdf_generator rechaza B+ | PDF output sin WARN de tier invalido | Pasa |
| 14 | **NP2**: publication_gates:399 logica rota | Logs de publication_gates | tier_message coherente |
| 15 | **NP3**: tests pre-existentes rompen | Suite de tests pasa | Todos pasan |
| 16 | **NP4**: default "A" en diagnostic generator | Caso sin financial_breakdown | Tier C, no A |
| 17 | **NP5**: fallback silencioso has_onboarding | Propuesta refleja onboarding real | Coherente |
| 18 | **NP6**: MANIFEST ubicacion incorrecta | MANIFEST.json enriquecido | quality_metadata presente |
| 19 | **NP7**: gate usa env vars globales | Gate recibe params per-hotel | Verificable en logs |
| 20 | **NP8**: control sin onboarding | v4complete hotel_test_001 | Tier C, no regresion |

### delegate_task prompt (embebido para T0 y T1)

```
GOAL: Execute v4complete for [Zi One Luxury OR hotel_test_001 control].

Working directory: /mnt/c/Users/Jhond/Github/iah-cli

Command to run:
./venv/Scripts/python.exe main.py v4complete --url [https://zione.co/ OR https://example-hotel-sin-onboarding.com/] --force-new

This will take 5-10 minutes. Wait for completion. The timeout is 900s.
After completion, report:
- Exit code
- Output paths generated (diagnostic, proposal, financial scenarios, gate reports, MANIFEST)
- Evidence tier from frontmatter
- Any gate failures
- evidence_tier in financial_scenarios.json
- disclaimer text from financial_breakdown

For Zi One: expected tier "B+" (not A).
For hotel_test_001: expected tier "C" (regression control).

If the command times out, report the last 50 lines of output and state clearly: "TIMEOUT - verification incomplete."
```

### Verificacion post-v4complete (main agent)

```bash
# Zi One (T1):
# 1. Verificar evidence_tier en el nuevo output
grep "financial_evidence_tier" output/v4_complete/01_DIAGNOSTICO_*.md | tail -1

# 2. Verificar que NO dice "GA4 verificado"
grep -c "Google Analytics.*Search Console.*verificad" output/v4_complete/01_DIAGNOSTICO_*.md
# Esperado: 0

# 3. Verificar que Fuentes de Datos es honesto
grep -A5 "Fuentes de Datos" output/v4_complete/01_DIAGNOSTICO_*.md | tail -10

# 4. Verificar precision_tier visible
grep "precision_tier\|Precision" output/v4_complete/01_DIAGNOSTICO_*.md

# 5. Verificar MANIFEST quality_metadata (CORREGIDO NP6)
grep "quality_metadata" output/v4_complete/deliveries/zione_*_MANIFEST.json

# 6. Verificar propuesta sin "benchmarks regionales" falso
grep "benchmarks regionales" output/v4_complete/02_PROPUESTA_*.md
# Esperado: 0 (Zi One tiene onboarding)

# 7. Verificar financial_scenarios.json
jq '.breakdown.evidence_tier, .breakdown.tier_explanation.relationship' output/v4_complete/zione/v4_audit/financial_scenarios_*.json

# Control (T0):
# 8. Verificar evidence_tier = "C" para hotel_test_001
jq '.breakdown.evidence_tier' output/hotel_test_001/v4_audit/financial_scenarios_*.json 2>/dev/null
# Esperado: "C"

# 9. Verificar NO hay regresion (tier != A y tier != B+ para hotel sin onboarding)
grep "financial_evidence_tier" output/hotel_test_001/01_DIAGNOSTICO_*.md 2>/dev/null
# Esperado: "C"
```

### Proxima sesion

**FASE-RELEASE**: Version bump v4.68.0 + CHANGELOG consolidado + docs cascade + pre-commit. Ejecutable via delegate_task (solo YAML/MD).
