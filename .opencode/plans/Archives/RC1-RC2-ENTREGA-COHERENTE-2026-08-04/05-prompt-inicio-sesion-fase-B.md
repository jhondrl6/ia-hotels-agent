# FASE-B — RC1: Parametrizar Tabla de Servicios de la Propuesta (⚠️ MAYOR COMPLEJIDAD)

**ID**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04 / FASE-B
**Objetivo**: Que la tabla de servicios de la propuesta cite el MISMO costo, rank y label de brecha que el diagnóstico del mismo run, consumiendo `opportunity_scores` del pipeline en lugar del mapa estático `BREACH_BY_ASSET`.
**Dependencias**: FASE-A ✅ (cuarentena de tests patológicos + lista segura)
**Duración estimada**: 2-3 horas
**Skill**: `.agents/workflows/phased_project_executor.md`
**Modo de ejecución**: Agente principal **DIRECTO — NO DELEGAR**. Esta fase incluye una decisión arquitectónica cross-module (el generador de propuesta pasa a consumir `opportunity_scores` keyed por `asset_type` vía `ASSET_TO_PAIN_ID`/`pain_solution_mapper`): un subagente carece del contexto completo para tomarla correctamente (§Regla código+tests, lección DT-3).

---

## Contexto

Hallazgos del contexto fuente (`CONTEXT-VALIDACION-COHERENCIA-PLAN-ENTREGA-2026-08-04.md`):

| Hallazgo | Problema |
|----------|----------|
| **N10 (ALTA)** | `BREACH_BY_ASSET` hardcodeado en `v4_proposal_generator.py` L1193-1206 muestra costos con factor 0.671× respecto al diagnóstico (fuente pre-D3, commit `3c3b9f8`) |
| **N17 (MEDIA)** | Mapeo servicio→brecha INVERTIDO: `BREACH_BY_ASSET["optimization_guide"]` apunta a "Sin Schema Hotel" cuando la brecha real de SEO Local es `low_seo_score` |
| **N18 (BAJA)** | Hardcode separado L1250: `"Brecha #5: WhatsApp no coincide"` (rank stale #5 vs rank vivo 1 = `whatsapp_conflict`) |
| **N19 (BAJA)** | Servicio fantasma "Schema Organization" (L61/L1199): `org_schema` no generado y sin brecha asociada |

**Fuente de verdad disponible**: el pipeline YA produce `opportunity_scores` en
`v4_complete_report.json` (8 entries, suma = escenario más probable). El generador de
propuesta simplemente no la consume (RC1).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada (verificar en dependencias-fases.md ANTES de empezar; si no ✅, ABORTAR) |

### Base Técnica Disponible
- Lista segura de tests del área propuesta (documentada por FASE-A)
- `ASSET_TO_PAIN_ID` ya existe en `v4_proposal_generator.py` L1185-1191
- `modules/commercial_documents/pain_solution_mapper.py`
- Evidencia del run 20260804_124443 en `output/v4_verify_4.70.0/v4_complete/`

---

## Tareas

### T1: Backup + Parametrización (R1.1 + R1.2)
**Objetivo**: Reemplazar la fuente estática por la fuente viva del run.

**Protocolo forense OBLIGATORIO (L4/L5)**:
```powershell
New-Item -ItemType Directory -Force temp/rc1_backup | Out-Null
Copy-Item modules/commercial_documents/v4_proposal_generator.py temp/rc1_backup/
git status --short
```

**Cambios**:
1. Construir un **mapa inverso** `ASSET_TO_BRECHA_ID: asset_type → brecha_id` invirtiendo
   `pain_solution_mapper.PAIN_SOLUTION_MAP[brecha_id]["assets"]` (cada asset_type apunta
   al brecha_id que lo activa). Luego reemplazar `BREACH_BY_ASSET` (L1193-1206) por una
   función que construya el mapa dinámicamente desde `opportunity_scores` del run actual:
   para cada entry, `brecha_id → (rank, estimated_monthly_cop, brecha_name)`, cruzado
   con el mapa inverso para obtener `asset_type → (rank, cost, label)`.

   **⚠️ Cobertura**: `ASSET_TO_PAIN_ID` (L1185-1191) solo cubre 6 de 8 services (falta
   `optimization_guide`, `open_graph`, `org_schema`). El mapa inverso desde
   `pain_solution_mapper` SÍ los cubre:
   - `optimization_guide ← low_seo_score` (también ← `low_content_length`: desempatar por presencia en opportunity_scores)
   - `open_graph ← no_og_tags`
   - `org_schema ← no_org_schema`
   - `whatsapp_button ← whatsapp_conflict` o `no_whatsapp_visible` (desempatar igual)
   - `llms_txt ← missing_llmstxt`
   - `faq_page ← no_faq_schema`
   - `hotel_schema ← no_hotel_schema`

2. El mapeo semántico N17 (`optimization_guide → low_seo_score`) se corrige
   AUTOMÁTICAMENTE con el reemplazo: el label vendrá de `brecha_name` del
   opportunity_score (ej: "SEO Local Bajo"), no del hardcode "Sin Schema Hotel".
   NO es un fix independiente — es consecuencia de T1.1.

3. Incluir el hardcode L1250 (`"Brecha #5: WhatsApp no coincide"`) en la parametrización:
   el texto "Brecha #5" debe reemplazarse por el rank vivo de `whatsapp_conflict` en
   opportunity_scores (rank 1 en el run Zione), label = `brecha_name` ("Conflicto de
   WhatsApp"), costo = `estimated_monthly_cop`.

4. Eliminar la fila fantasma `org_schema` (N19): renderizarla CONDICIONALMENTE solo si
   el asset fue generado en el run Y `no_org_schema` existe en `opportunity_scores`.
   Si `no_org_schema` no está en opportunity_scores → mostrar sin costo ("—").

5. Fallback explícito: si un `asset_type` no resuelve ningún `brecha_id` presente en
   `opportunity_scores`, NO inventar cifras — mostrar la brecha sin costo y registrar
   warning.

**Criterios de aceptación**:
- [ ] `grep -n "BREACH_BY_ASSET"` → eliminado o convertido a construcción dinámica.
- [ ] `grep -n "Brecha #5: WhatsApp"` → 0 hits (hardcode eliminado).
- [ ] El generador no contiene literales de costos de brechas (grep de cifras tipo `\d{3},\d{3}` en contexto de brechas).

### T2: Test aislado de consistencia (R1.3)
**Objetivo**: Gate de no-regresión permanente para RC1.

- Nuevo archivo de test (ej: `tests/commercial_documents/test_proposal_breach_consistency.py`)
  con fixture fijo: "costo/rank/label por servicio en tabla de propuesta == valores del
  `opportunity_scores` del fixture".
- Casos: mapeo correcto SEO Local→low_seo_score; WhatsApp rank 1; org_schema ausente
  cuando el asset no existe; fallback sin cifras inventadas.
- SOLO ejecutar este archivo + la lista segura de FASE-A. NUNCA suite completa.

**Criterios de aceptación**:
- [ ] Tests nuevos pasan (registrar conteo desde `git diff tests/` con patrón `^\+\s*def test_` — L8).
- [ ] Lista segura de FASE-A sigue pasando (0 regresiones).

### T3: Verificación E2E estática contra evidencia del run existente
**Objetivo**: Confirmar que con la data real del run 20260804_124443 la nueva lógica
produciría cifras correctas (sin re-ejecutar v4complete — eso es FASE-F).

- Script Python UTF-8 (L15): parsear `opportunity_scores` del
  `output/v4_verify_4.70.0/v4_complete/.../v4_complete_report.json` (8 entries con
  campos `brecha_id`, `rank`, `estimated_monthly_cop`, `brecha_name`), construir el
  mapa inverso `asset_type → brecha_id` desde `pain_solution_mapper`, y verificar que
  los 7 services de `PROPOSAL_SERVICE_TO_ASSET` resuelven costo/rank/label.
  Expected: 5 services con costo (whatsapp, hotel_schema, faq, optimization, open_graph)
  y 2 sin costo (org_schema, llms_txt — sus brechas no están en opportunity_scores).
- Si algún test del área no puede correr: evidencia mixta dinámica+estática (L7) —
  `git show HEAD:` + diff de la fase para el área no cubierta.

**Criterios de aceptación**:
- [ ] Los 5 services con brecha en opportunity_scores resuelven costo == `estimated_monthly_cop`.
- [ ] Los 2 services sin brecha muestran "—" sin cifras inventadas.
- [ ] Script de verificación guardado en `evidence/FASE-B/`.

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Test nuevo RC1 | `python -m pytest tests/commercial_documents/test_proposal_breach_consistency.py -v > temp/fase_b_test.txt 2>&1` | 100% PASS |
| Lista segura FASE-A | Lotes pequeños secuenciales redirigidos a archivo | 0 regresiones |
| Validaciones | `python scripts/run_all_validations.py --quick` | TOTAL PASS (conteo dinámico del script) |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. Actualizar `dependencias-fases.md` (FASE-B ✅) y `README.md` del plan.
2. `09-documentacion-post-proyecto.md`: Sección B (feature: tabla de servicios dinámica),
   Sección D (+N tests desde git diff), Sección E (archivos).
3. Evidencia en `evidence/FASE-B/` (script de verificación + salidas).
4. Registrar la fase:
```bash
python scripts/log_phase_completion.py --fase FASE-B --desc "RC1: tabla de servicios de propuesta parametrizada desde opportunity_scores (N10/N17/N18/N19)" --archivos-mod "modules/commercial_documents/v4_proposal_generator.py" --tests "N" --check-manual-docs
```
**SIN `--release`** (L3/L9).

---

## Criterios de Completitud (CHECKLIST)

- [ ] `BREACH_BY_ASSET` estático eliminado; hardcode L1250 eliminado; org_schema condicional
- [ ] Mapeo semántico corregido (optimization_guide→low_seo_score, whatsapp→whatsapp_conflict)
- [ ] Test de consistencia nuevo pasando; conteo registrado desde git diff (L8)
- [ ] Verificación contra evidencia real del run 124443: 8/8 brechas resuelven costo correcto
- [ ] `run_all_validations.py --quick` TOTAL PASS (conteo dinámico del script)
- [ ] `log_phase_completion.py` ejecutado SIN --release
- [ ] Backup en `temp/rc1_backup/` conservado hasta el cierre de FASE-F

## Restricciones

- Máximo 60 iteraciones (R2). Fase de mayor complejidad: si el presupuesto se agota,
  marcar ⏳ INCOMPLETA con checkpoint en `dependencias-fases.md` y cerrar sesión.
- NUNCA suite completa de `tests/commercial_documents`/`tests/financial_engine` (L1/L11).
- NO ejecutar `v4complete` en esta fase (reservado para FASE-F — UNA sola ejecución).
- NO tocar `commercial_gate.py` ni `delivery_packager.py` (pertenecen a FASE-C/D).
- Si el usuario interviene: `git diff --stat` + `git status --short` antes de continuar (L10).
