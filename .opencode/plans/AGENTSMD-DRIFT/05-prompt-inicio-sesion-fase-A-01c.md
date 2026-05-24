# 05-prompt-inicio-sesion-fase-A-01c

**Fase:** A-01c — v4complete Hotel Castilla Real
**Plan:** AGENTSMD-DRIFT
**Sesión:** Nueva (fresh)
**Iteraciones máx:** 60
**Depende de:** FASE-A-01b ✅
**Bloquea a:** FASE-RELEASE-4.49.0
**⚠️ CONTIENE COMANDO LARGO: v4complete (~5-10 min)**

## Objetivo

Ejecutar v4complete sobre Hotel Castilla Real para verificar que el pipeline funciona correctamente con AGENTS.md ya corregido y validate_agents_md.py integrado. Esta es la verificación E2E final antes del cierre documental.

## Contexto de Fases Anteriores

**FASE-A-01a ✅:** AGENTS.md corregido — 2,743 tests, 11 gates, módulos FASE-0 documentados.
**FASE-A-01b ✅:** validate_agents_md.py creado e integrado en CONTRIBUTING.md.

**Hotel:** Castilla Real
**URL:** https://www.hotelcastillareal.com/
**Referencia previa:** VERSION.yaml menciona "FASE-PF-3: E2E Hotel Castilla Real — coherence 0.8261, coverage PASS, tier_c_onboarding PASS" en v4.48.0. Esta ejecución debe mantener o mejorar ese baseline.

**Expectativas del pipeline actual:**
- Coherence ≥ 0.80
- Coverage gate: PASS
- tier_c_onboarding_required: PASS
- 7+ assets generados
- Diagnóstico + Propuesta completos

## Tareas

### T1: Ejecutar v4complete

Ejecutar v4complete usando subagente (siguiendo el protocolo de `phased_project_executor.md` §Protocolo-Subagente-v4complete):

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
```

**Plan de presupuesto de iteraciones:**
- Gastos fijos (leer plan, investigar): ~10 iteraciones
- v4complete: 1 tool call (terminal con timeout=600, notify_on_complete=True)
- Verificar output: ~10 iteraciones
- Evidencia + docs: ~15 iteraciones
- Total estimado: ~36 iteraciones → margen de 24

**Estrategia:** Ejecutar v4complete DIRECTAMENTE con `terminal(timeout=600, notify_on_complete=True)`. El presupuesto es holgado (36 < 60).

### T2: Verificar output

Una vez que v4complete termine, verificar:

1. **Archivos generados:**
   ```bash
   ls -la output/v4_complete/01_DIAGNOSTICO_*.md
   ls -la output/v4_complete/02_PROPUESTA_*.md
   ls -la output/v4_complete/hotel_castilla_real/v4_audit/*.json
   ```

2. **Coherence score:**
   ```bash
   cat output/v4_complete/hotel_castilla_real/v4_audit/coherence_validation.json | python -m json.tool | grep coherence_score
   ```
   Debe ser ≥ 0.80.

3. **Publication gates:**
   ```bash
   cat output/v4_complete/hotel_castilla_real/v4_audit/gate_report.json | python -m json.tool | grep -E '"status"|"passed"'
   ```

4. **Delivery quality report:**
   ```bash
   cat output/v4_complete/hotel_castilla_real/v4_audit/delivery_quality_report.json | python -m json.tool | grep -E '"overall"|"ready"'
   ```

5. **Pain ledger:**
   ```bash
   cat output/v4_complete/hotel_castilla_real/v4_audit/pain_ledger.json | python -m json.tool | grep -c '"pain_id"'
   ```
   Debe tener ≥ 7 pains registrados.

6. **Human checklist:**
   ```bash
   ls -la output/v4_complete/hotel_castilla_real/human_checklist_*.md
   ```
   Debe existir y tener ≤ 10 items.

### T3: Guardar evidencia + análisis + docs

**Protocolo de Evidencia Proactiva (OBLIGATORIO — ejecutar INMEDIATAMENTE después de verificar):**

```bash
mkdir -p evidence/FASE-A-01c
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-A-01c/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-A-01c/
cp output/v4_complete/hotel_castilla_real/v4_audit/*.json evidence/FASE-A-01c/
```

**Análisis de ejecución:**

Redactar un análisis breve que cubra:
- Coherence score obtenido vs baseline anterior (0.8261 en v4.48.0)
- Gates que pasaron y los que no
- Comparación con ejecución previa si hay datos
- Cualquier warning o advisory del delivery_quality_report
- Tiempo total de ejecución

**log_phase_completion.py:**

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A-01c \
    --desc "v4complete Hotel Castilla Real — E2E verification post AGENTS.md fix + validate_agents_md.py integration" \
    --archivos-mod "" \
    --tests "0" \
    --check-manual-docs
```

**Actualizar 09-documentacion-post-proyecto.md:**
- Sección D: `Coherence Hotel Castilla Real | X.XXXX | FASE-A-01c` (con el valor real)
- Sección D: `Publication Gates PASS rate | X/11 | FASE-A-01c`
- Sección E: `evidence/FASE-A-01c/ | Evidencia v4complete preservada | FASE-A-01c`

## Criterios de Completitud

- [ ] v4complete ejecutado sin errores fatales
- [ ] 01_DIAGNOSTICO_*.md generado (>5KB)
- [ ] 02_PROPUESTA_*.md generado (>5KB)
- [ ] Coherence score ≥ 0.80
- [ ] Coverage gate: PASS
- [ ] tier_c_onboarding_required gate: PASS
- [ ] Pain ledger: ≥7 pains con trazabilidad
- [ ] Human checklist: ≤10 items
- [ ] Evidencia copiada a evidence/FASE-A-01c/
- [ ] Análisis de ejecución redactado
- [ ] log_phase_completion.py ejecutado
- [ ] 09-documentacion-post-proyecto.md actualizado

## Restricciones

- Máximo 60 iteraciones
- **NO modificar AGENTS.md, ROADMAP.md, CONTRIBUTING.md, CHANGELOG.md, GUIA_TECNICA.md, VERSION.yaml**
- **NO modificar ningún archivo .py**
- Solo generar output + evidencia + docs de fase
- Si v4complete falla por timeout/API, guardar evidencia parcial y reportar
