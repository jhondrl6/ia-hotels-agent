# FASE-P1-D: Verdad del Sitio Vivo — Sedes WhatsApp (F12) + Propagación site_verification (F13)

> ⚠️ **FASE DE MAYOR COMPLEJIDAD TÉCNICA DEL PLAN** — Leer la sección "Gestión de Complejidad" antes de iniciar.

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-P1-D
**Objetivo**: Restaurar "el estado de verdad del sitio vivo" como fuente única: (1) el cross-validator
debe distinguir sedes en negocios multi-ubicación (F12), y (2) la verificación de sitio vivo ya
existente (`site_verification_applied`) debe propagarse al pain_ledger y al diagnóstico (F13).
**Dependencias**: FASE-P1-C ✅ (o FASE-P1-A ✅ — es independiente de la cadena de benchmarks; puede ejecutarse en paralelo con P1-B/C si el presupuesto del proyecto lo permite, pero el checklist la secuencia después por simplicidad)
**Duración estimada**: 1 sesión (≤60 iteraciones) — fase densa, presupuestar con disciplina
**Skill**: `phased_project_executor.md` (ejecución DIRECTA obligatoria — decisión arquitectónica cross-module)

## Modo de Ejecución

**DIRECTO con el agente principal. NO delegable.** Esta fase es la decisión arquitectónica
cross-module más compleja del plan: un concepto nuevo ("estado de verdad del sitio vivo") con 3+
consumidores que hoy discrepan (asset layer, gate, pain_ledger/diagnóstico). Un subagente carece
del contexto completo (regla del executor, lección DT-3 FASE-2).

## Contexto

CONTEXT §7.1 fallos **F12** y **F13** (clase "verdad del sitio vivo no propagada"), verificados
contra el sitio vivo https://zione.co/ (2 sedes: Pereira y Cartagena):

- **F12** (🔴 CRÍTICA): el diagnóstico alerta "Su Google Business muestra 311 6079036, pero su
  sitio web indica +573103724544" — pero el número alertado pertenece a la sede **Cartagena**.
  El número web de Pereira (+57 311 607 9036) es idéntico al del GBP. El cross-validator compara
  GBP contra el primer `wa.me`/tel del DOM sin mapear número→sede. **Infla la fuga $1.198.906/mes
  con una BRECHA 1 inexistente, refutable por el cliente en 2 minutos mirando su propio footer.**
- **F13** (🔴 CRÍTICA): `pain_ledger.json` reporta `no_whatsapp_visible` DETECTED HIGH (conf 0.3)
  cuando el botón existe en 3 ubicaciones del sitio (widget Elementor `e-fab-whatsapp`, footer,
  enlaces wa.me). La verificación de sitio vivo existe (`site_verification_applied: true`) y la
  consumen el asset layer (skip de generación) y el gate ("verified in production"), pero NO el
  pain_ledger ni el diagnóstico. **El fix no es un scanner nuevo: es propagar una verificación
  que ya existe** (lección §7.4 del CONTEXT).

**Causa raíz común** (extiende el patrón dominante): el sitio tiene una verdad y tres capas la
interpretan distinto.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P0-A/B/C | ✅ Completadas |
| FASE-P1-A/B/C | ✅ Completadas (o en curso — esta fase es independiente de ellas) |

### Base Técnica Disponible
- `modules/data_validation/cross_validator.py` (`validate_whatsapp`, definición L123)
- **3 callers productivos de `validate_whatsapp`** (un cambio de firma los afecta — decidir en T1
  si el parámetro nuevo es opcional/backwards-compatible o si hay que editarlos):
  `main.py` L1735, `modules/auditors/v4_comprehensive.py` L1557,
  `modules/orchestration_v4/two_phase_flow.py` L371
- `modules/asset_generation/pain_ledger.py` (trazabilidad pain_id → fuente → severidad)
- `modules/asset_generation/` (asset layer que ya consume `site_verification` para skip)
- `modules/quality_gates/` (gate `proposal_asset_alignment` que ya consume "verified in production")
- `modules/commercial_documents/v4_diagnostic_generator.py` (diagnóstico)
- Scanner web que produce los números `wa.me`/tel del DOM (identificar en T1)

## Presupuesto de Iteraciones (CRÍTICO en esta fase)

```
Presupuesto: 60 iteraciones
- Leer plan + verificar estado previo: ~3
- T1 investigación (scanner + cross_validator + pain_ledger + gate): ~15
- T2 fix F12 (sedes): ~10
- T3 fix F13 (propagación): ~10
- Tests: ~8
- log_phase_completion + docs cascade: ~10
Total estimado: ~56 → MARGEN MÍNIMO
```

**Si en la iteración ~40 no se ha terminado T3**: aplicar "Gestión de Complejidad" abajo.

## Gestión de Complejidad (contingencia por fase más compleja del plan)

```
SI la fase supera el presupuesto o la complejidad:
  1. Marcar FASE-P1-D como ⏳ INCOMPLETA en 06-checklist + dependencias-fases.md
  2. PRIORIZAR siempre F12 sobre F13 (F12 es la brecha refutable por el cliente
     en su propio footer — más dañina comercialmente)
  3. Dividir en:
     - FASE-P1-D-A (nueva sesión): solo F12 (mapeo número→sede en cross_validator)
     - FASE-P1-D-B (nueva sesión): solo F13 (propagación site_verification)
  4. Actualizar dependencias-fases.md con la nueva secuencia
  5. Guardar evidencia parcial en evidence/FASE-P1-D/
```

## Tareas

### T1: Investigación — mapear el flujo completo de verdad del sitio (ANTES de modificar)
**Objetivo**: leer completos y mapear: (a) quién scanea `wa.me`/tel del DOM y con qué metadata
(debe existir algún campo de contexto/ubicación en el DOM — footer de Zione tiene labels
"Pereira Contact"/"Cartagena Contact"); (b) `cross_validator.validate_whatsapp()` (L123) y sus
3 callers (main.py L1735, v4_comprehensive.py L1557, two_phase_flow.py L371) — decidir si el
cambio multi-sede es backwards-compatible o requiere editar los 3; (c) dónde se produce
`site_verification_applied` y quiénes la consumen (asset layer + gate); (d) cómo el pain_ledger
genera `no_whatsapp_visible`.
**Criterios de aceptación**:
- [ ] Diagrama escrito del flujo actual (quién produce/qué consume) en las notas de la fase
- [ ] Identificado el punto exacto donde la metadata de sede existe pero se descarta

### T2: Fix F12 — comparación WhatsApp con mapeo número→sede
**Archivos afectados**:
- `modules/data_validation/cross_validator.py` (`validate_whatsapp`, L123)
- Los 3 callers SI el cambio de firma no es backwards-compatible: `main.py` (L1735),
  `modules/auditors/v4_comprehensive.py` (L1557), `modules/orchestration_v4/two_phase_flow.py` (L371)
- Scanner del DOM (solo si necesita exponer metadata de sede/label del número)
**Criterios de aceptación**:
- [ ] La validación compara el número GBP contra el número web de la MISMA sede
- [ ] Números de otras sedes no generan conflicto (se registran como "sede alterna", no como brecha)
- [ ] Si no hay metadata de sede confiable, el conflicto degrada a WARNING (no HIGH) con disclaimer
- [ ] Caso Zione reproduce: GBP Pereira vs web Pereira → SIN conflicto

### T3: Fix F13 — propagar site_verification al pain_ledger y diagnóstico
**Archivos afectados**:
- `modules/asset_generation/pain_ledger.py` (consumo de site_verification)
- `modules/commercial_documents/v4_diagnostic_generator.py` (o el compositor del diagnóstico)
- Opcional: reconocimiento del widget Elementor `e-fab-whatsapp` en el scanner (si es barato;
  si no, documentar como seguimiento)
**Criterios de aceptación**:
- [ ] Si `site_verification` confirma el asset en producción, la entrada del pain_ledger pasa de
      DETECTED a VERIFIED_IN_SITE (o estado equivalente) — NO sigue HIGH
- [ ] El diagnóstico no reporta la brecha como abierta cuando está verificada en producción
- [ ] El coverage gate sigue cuadrando (cubiertas + justificadas == detectadas)

### T4: Tests de contrato (caso Zione como fixture)
**Criterios de aceptación**:
- [ ] Test F12: fixture multi-sede (GBP sede A, web sedes A+B) → sin falso positivo
- [ ] Test F13: site_verification=true → pain_ledger no DETECTED HIGH
- [ ] Suites `tests/data_validation/` y `tests/asset_generation/` sin fallos NUEVOS vs línea base (§6)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Sedes WhatsApp | `tests/data_validation/test_whatsapp_multisede.py` (nuevo) | Contratos F12 pasan |
| Propagación site_verification | `tests/asset_generation/test_site_verification_propagation.py` (nuevo) | Contratos F13 pasan |

**Comando de validación**:
```powershell
.\venv\Scripts\python.exe -m pytest tests/data_validation/ tests/asset_generation/ -v
.\venv\Scripts\python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-P1-D ✅ (o ⏳ INCOMPLETA con checkpoint).
2. `README.md` del plan: actualizar tabla de progreso.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E.
4. `10-analisis-post-implementacion.md`: fila de ejecución + mínimo 3 lecciones + **decisión D8 documentada** (estado "verificado en producción" como primera clase — será consumida por FASE-P2-A/F14).
5. **Registrar la fase**:
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-P1-D --desc "Verdad del sitio vivo: sedes WhatsApp (F12) + propagacion site_verification (F13)" --archivos-mod "modules/data_validation/cross_validator.py,modules/asset_generation/pain_ledger.py,modules/commercial_documents/v4_diagnostic_generator.py,<callers de validate_whatsapp editados segun T1: main.py y/o v4_comprehensive.py y/o two_phase_flow.py>" --tests "<N>" --check-manual-docs
```
6. Editar CHANGELOG.md y GUIA_TECNICA.md (template §6).
7. Guardar fixtures y evidencia en `evidence/FASE-P1-D/`.

## Criterios de Completitud (CHECKLIST)

- [ ] Fixture multi-sede no produce falso positivo de conflicto (F12 verificado por test)
- [ ] site_verification propagada: pain_ledger + diagnóstico coherentes con asset layer y gate (F13)
- [ ] Suites data_validation + asset_generation sin fallos NUEVOS vs línea base (§6)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada

## Restricciones

- Máximo 60 iteraciones — presupuestar según sección "Presupuesto".
- NO resolver F14 (`promised_assets_exist` del coherence validator) — es FASE-P2-A; esta fase solo DEJA LISTO el estado "verificado en producción" para que P2-A lo consuma.
- NO modificar benchmarks, pricing, ni rango del hook.
- NO ejecutar v4complete.
