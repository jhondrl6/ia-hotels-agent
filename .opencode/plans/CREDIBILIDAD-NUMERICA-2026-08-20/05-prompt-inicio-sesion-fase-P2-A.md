# FASE-P2-A: Coherence acepta "Verificado en Producción" (F14) + Occupancy Label Residual (F8)

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-P2-A
**Objetivo**: Alinear el coherence validator con el gate para que ambos acepten el estado
"verificado en producción" sobre `promised_assets_exist` (F14), y verificar/corregir cualquier
etiqueta residual de provenance de occupancy (F8, valor ya corregido en FASE-F recovery v4.71.0).
**Dependencias**: FASE-P1-D ✅ (estado "verificado en producción" ya implementado — decisión D8)
**Duración estimada**: 1 sesión (≤60 iteraciones)
**Skill**: `phased_project_executor.md` (ejecución DIRECTA)

## Modo de Ejecución

**DIRECTO con el agente principal.** Los cambios son acotados pero requieren leer el coherence
validator completo para no romper los demás `promised_assets_exist` (lección §1.3: archivo completo
antes de declarar bug).

## Contexto

CONTEXT fallos **F14** y **F8**:
- **F14** (🟡 ALTA): tres componentes discrepan sobre `whatsapp_button`: coherence post-generación
  = FAILED ("Assets no implementados", busca archivo físico), gate_report `proposal_asset_alignment`
  = PASSED ("verified in production"), pain_ledger = DETECTED HIGH. Causa raíz: `promised_assets_exist`
  del coherence validator no contempla el estado "existe en producción sin archivo" que el gate sí
  contempla. Señal de calidad contradictoria dentro del mismo kit (PASSED y FAILED sobre el mismo asset).
- **F8** (residual, 🟡 ALTA): el valor del occupancy (0.7843) ya fue corregido y su etiqueta de
  inyección Tier A fue arreglada en la FASE-F recovery de RC1-RC2 (commit `main.py` rutas
  `_occupancy_source`, verificado en corrida s5b: etiqueta `"onboarding"`). Lo que queda: VERIFICAR
  que no haya rutas residuales que etiqueten mal, y asegurar que el fix aplica para la corrida E2E.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P0-A/B/C | ✅ Completadas |
| FASE-P1-A/B/C | ✅ Completadas |
| FASE-P1-D | ✅ Completada (verificar en 06-checklist — requisito de entrada) |

### Base Técnica Disponible
- `modules/commercial_documents/coherence_validator.py` (`promised_assets_exist`)
- Estado "verificado en producción" implementado en FASE-P1-D (decisión D8 en 10-analisis)
- `tests/financial_engine/test_fase_f_recovery_s5b.py` (tests del fix previo de occupancy)
- Gate `proposal_asset_alignment` (ya contempla el estado)

## Tareas

### T1: Fix F14 — `promised_assets_exist` acepta "verificado en producción"
**Archivos afectados**:
- `modules/commercial_documents/coherence_validator.py`
**Criterios de aceptación**:
- [ ] Si el asset está verificado en producción (según el estado de FASE-P1-D), `promised_assets_exist`
      NO falla aunque no exista archivo físico generado
- [ ] Coherence y gate_report producen la MISMA señal sobre el mismo asset (ambos PASSED o ambos FAILED)
- [ ] Los assets prometidos sin archivo y sin verificación en producción siguen fallando (no se debilita el gate)

### T2: Verificación F8 — provenance de occupancy sin rutas residuales
**Archivos afectados** (solo si se encuentra ruta residual):
- `main.py` y/o `modules/financial_engine/harness_handlers.py`
**Criterios de aceptación**:
- [ ] Auditoría de TODOS los sitios de construcción de `data_sources.occupancy` (grep por
      `occupancy_source`/`_occ_source`) — inventario escrito
- [ ] Toda inyección Tier A etiqueta `onboarding`; benchmark regional etiqueta la región exacta
      (no solo "regional" genérico — refinación §6.4 del CONTEXT)
- [ ] Si no hay rutas residuales, documentar la verificación (sin cambios de código)

### T3: Tests de contrato anti-regresión
**Criterios de aceptación**:
- [ ] Test F14: asset verificado en producción → coherence PASSED (coincidente con gate)
- [ ] Test F14: asset prometido sin archivo ni verificación → coherence FAILED (gate no debilitado)
- [ ] Test F8 (si aplica): etiqueta de occupancy correcta por ruta de inyección
- [ ] Suites `tests/commercial_documents/` y `tests/financial_engine/` sin fallos NUEVOS vs línea base (§6: 12 preexistentes en commercial_documents + 10 en financial_engine)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Coherence producción | `tests/commercial_documents/test_promised_assets_production.py` (nuevo) | Contratos F14 pasan |
| Regresión coherence | `pytest tests/commercial_documents/ -v` | 0 fallos NUEVOS vs línea base (12 preexistentes §6) |

**Comando de validación**:
```powershell
.\venv\Scripts\python.exe -m pytest tests/commercial_documents/ tests/financial_engine/ -v
.\venv\Scripts\python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-P2-A ✅.
2. `README.md` del plan: actualizar tabla de progreso.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E.
4. `10-analisis-post-implementacion.md`: fila de ejecución + mínimo 3 lecciones.
5. **Registrar la fase**:
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-P2-A --desc "Coherence acepta verificado en produccion (F14) + verificacion occupancy label (F8)" --archivos-mod "modules/commercial_documents/coherence_validator.py" --tests "<N>" --check-manual-docs
```
6. Editar CHANGELOG.md y GUIA_TECNICA.md (template §6).

## Criterios de Completitud (CHECKLIST)

- [ ] Coherence y gate de acuerdo sobre assets verificados en producción (F14 verificado por test)
- [ ] Provenance de occupancy auditado (F8 verificado, con o sin cambios de código)
- [ ] Suites commercial_documents + financial_engine sin fallos NUEVOS vs línea base (§6)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada

## Restricciones

- Máximo 60 iteraciones.
- NO re-abrir el fix de site_verification (ya cerrado en P1-D).
- NO debilitar `promised_assets_exist` más allá del estado "verificado en producción".
- NO ejecutar v4complete.
