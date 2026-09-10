# FASE-VERIFY: Certificación Formal de ACs contra Output E2E

**ID**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-VERIFY
**Objetivo**: Certificar formalmente que los AC1-AC16 del plan se cumplen contra el output E2E real generado en FASE-E2E. No modifica código. Produce evidencia de certificación y completa la matriz de verificación.
**Dependencias**: FASE-E2E ✅ (todas las fases de implementación completas)
**Complejidad técnica**: **MEDIA** — requiere juicio y contexto completo del plan; lectura de artefactos reales, greps, comparación JSON
**Modo de ejecución**: **DIRECTO** (agente principal). NO delegable: requiere juicio y contexto completo del plan (§4.6 del executor).
**Skill**: `phased_project_executor.md` v2.20.0 §4.6

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-T1 | ✅ |
| FASE-T2-A | ✅ |
| FASE-T2-B | ✅ |
| FASE-T4-A | ✅ |
| FASE-T4-B | ✅ |
| FASE-E2E | ✅ (output real disponible) |
| FASE-VERIFY | ← ESTA FASE |

### Rutas a output y baseline

- **Output post-fix**: `evidence/FASE-E2E/` (artefactos copiados por Protocolo de Evidencia Proactiva, INCLUYENDO `deliveries/` con MANIFEST/IMPLEMENTATION_ORDER/ASSETS)
- **Output vivo**: `output/v4_complete/hotelsalentoreal/v4_audit/`
- **Deliveries vivos**: `output/v4_complete/deliveries/hotelsalentoreal_*/` (más reciente por glob)
- **Baseline solo-lectura**: `output/FASE-D_salentoreal_post_guard/v4_complete/` (Tier B, 2026-08-31)
- **Corrida de referencia estabilización**: `evidence/FASE-I/`

---

## Metodología (§4.6 del executor — 7 pasos)

### Paso 1: Leer output post-fix y baseline

- Leer `evidence/FASE-E2E/acta_revision.json` — veredicto, cláusulas, evidence_tier
- Leer `evidence/FASE-E2E/revision_diagnostico.json` — findings de Bot 1
- Leer `evidence/FASE-E2E/revision_assets.json` — coverage de Bot 3
- Leer `evidence/FASE-E2E/revision_alineacion.json` — service_matrix de Bot 2
- Leer `evidence/FASE-E2E/revision_honestidad.json` — findings de Bot 4
- Leer baseline FASE-D para comparación (si los artefactos existen)

### Paso 2: Verificar cada AC contra output real

| AC | Método de verificación | Qué buscar |
|----|----------------------|------------|
| AC1 | Lectura directa JSON | `acta_revision.json` → clave `verdict` existe y es string válido |
| AC2 | Lectura directa JSON | `verdict` == `APROBADO-CONDICIONAL-PENDING-ONBOARDING` + `evidence_tier` ∈ {B,C} |
| AC3 | Lectura directa MD | `acta_revision.md` contiene secciones P6.1, P6.2, P6.3, P6.4, P6.5, P6.6 |
| AC4 | Grep en `main.py` | Buscar `tribunal` o `TribunalJudge` — debe aparecer UNA sola vez como llamada; verificar que no hay cuarta ruta de bloqueo |
| AC5 | Lectura directa JSON | `revision_diagnostico.json` → clave `findings` es lista no vacía |
| AC6 | Lectura directa JSON | Buscar finding con `finding_type == "VACUOUS_RECALL"` (si aplica en esta corrida) |
| AC7 | Lectura directa JSON | `revision_assets.json` → clave `coverage_by_service` es lista |
| AC8 | Lectura directa JSON | Buscar finding con `finding_type == "EMPTY_DELIVERY_TEMPLATE"` (vacío = 0 B o plantilla sin contenido por-hotel) |
| AC9 | Lectura directa JSON | `revision_alineacion.json` → clave `service_matrix` es lista |
| AC10 | Verificar en tests | Test `test_promise_without_matrix_detected` pasa (ya verificado en T4-A; aquí se confirma que el régimen se sostiene en la corrida real) |
| AC11 | Lectura directa JSON | `revision_honestidad.json` → clave `findings` es lista |
| AC12 | Lectura directa JSON | Buscar finding con `cg_reference == "CG-WHATSAPP-LEAD"` |
| AC13 | Lectura directa JSON | `acta_revision.json` → `clauses_evaluated` == 6 |
| AC14 | `ls` del directorio | Los 4 archivos `revision_*.json` existen en `v4_audit/` |
| AC15 | Lectura de sonda/test | S-E2: salida de `generate_proposal=False` sin `NameError` (test verde) |
| AC16 | Lectura de test | S9: test de contrato de `INVALID_MAPPINGS` verde |

### Paso 3: Comparar antes/después (delta)

| Zona | Baseline FASE-D | Output E2E | Delta |
|------|----------------|------------|-------|
| Artefactos de tribunal en `v4_audit/` | 0 | 6 | +6 (acta + 4 revisiones + acta.md) |
| Veredicto de entrega | (no existía) | `APROBADO-CONDICIONAL-PENDING-ONBOARDING` | nuevo |
| Coherence canónico | 0.88 | (leer de `asset_generation_report.json`) | delta |
| `is_coherent` | false | (leer) | esperado: true (post-estabilización) |
| `no_breach` servicios | 0 (post-estabilización) | (leer de `proposal_asset_matrix.json`) | esperado: 0 |

### Paso 4: Greps residuales

Strings que NO deberían aparecer en el output del tribunal:

| Patrón | Dónde | Esperado |
|--------|-------|----------|
| `"verdict": "APROBADO-PARA-ENTREGA"` | `acta_revision.json` (si tier B) | 0 matches |
| `import.*publication_gates` | `modules/quality_gates/tribunal/*.py` | 0 matches (NR4) |
| `two_phase_flow` | `main.py` (zona tribunal) | 0 matches |
| `"score": 1.0` hardcodeado sin condición | `tribunal/*.py` | 0 matches |

### Paso 5: Completar matriz de verificación

Llenar la tabla en `10-analisis-post-implementacion.md` §Matriz de Verificación:
- Columna "Real": valor leído del artefacto
- Columna "Status": ✅ / ⚠️ / ❌

**Regla R2.4**: un AC cuyo valor no es legible en el artefacto se marca ⚠️, NUNCA ✅.

### Paso 6: Registrar lecciones aprendidas

Mínimo 3 lecciones de la verificación. Formato: qué pasó / por qué / qué lo previene + pertinencia (INCLUIR/EXCLUIR).

### Paso 7: Registro + validación

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-VERIFY \
    --desc "Certificación AC1-AC16 contra output E2E real del tribunal" \
    --check-manual-docs

./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: marcar FASE-VERIFY ✅
2. **`README.md` del plan**: actualizar progreso
3. **`10-analisis-post-implementacion.md`**: Matriz de verificación COMPLETA + lecciones + métricas
4. **`06-checklist-implementacion.md`**: marcar items VERIFY
5. **`evidence/FASE-VERIFY/`**: capturas de los greps, delta documentado

---

## Criterios de Completitud (CHECKLIST)

- [ ] AC1-AC16 verificados contra output REAL (no solo tests)
- [ ] Matriz de verificación completa (16 filas con Real + Status)
- [ ] Delta antes/después documentado
- [ ] Greps residuales: 0 matches en los 4 patrones
- [ ] Mínimo 3 lecciones aprendidas registradas
- [ ] `log_phase_completion.py` ejecutado (SIN `--release`)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] NO modificó código fuente (verificar con `git diff --stat`)

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **Presupuesto**: 40 iteraciones, corte en commit de código (R2.1)
- **NO modifica código fuente** — si un AC falla, se documenta en "Seguimientos abiertos"
- **NO ejecuta v4complete** — la ejecución E2E ya ocurrió en FASE-E2E
- **NO modificar ROADMAP.md**
- **NO usar números de línea** (R2.2)
- **NO delegar** — requiere juicio y contexto completo del plan
- **FASE-RELEASE requiere FASE-VERIFY ✅** antes de ejecutarse
