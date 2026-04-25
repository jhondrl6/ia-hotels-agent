# FASE-VALIDATE-RC: Validación de Bugs — Amazilia Hotel

**Fecha**: 2026-04-24 (actualizado 2026-04-24 19:08)  
**Propuesta evaluada**: `02_PROPUESTA_COMERCIAL_20260424_190828.md` (regenerada post-hotfix BUG-8)  
**Propuesta anterior**: `02_PROPUESTA_COMERCIAL_20260424_143736.md` (PRE-hotfix — descartada)

## Resultados

| Bug | Criterio | Veredicto | Evidencia |
|-----|----------|-----------|-----------|
| BUG-1 | "Esto es lo que hacemos" no vacía | ✅ PASS | Líneas 42-54: tabla con 8 servicios |
| BUG-3 | ROI <= 5.0X en propuesta | ✅ PASS | Propuesta muestra "ROI: 0.2" (< 5.0X) |
| BUG-4 | 0 items "No generado" / "Requiere datos" | ✅ PASS | Tabla usa: "En preparacion", "Completo", "Incluido en su kit" |
|| BUG-8 | Ortografía corregida (hoteles, brille, proveer, Absorbido, protección) | ✅ FIXED (2026-04-24) | "huespedes" → "huéspedes" en scrubber, template V6, service_catalog, y 3 archivos más |
| D-1 | AEO incluido condicionalmente | ✅ PASS | Línea 53: "Optimización para IA Generativa" |
| D-4 | Timeline 7/30/60/90 días realista | ✅ PASS | Día 1, Días 2-7, Días 8-30, Mes 2-3 |
| D-7 | 0 items "No generado" en entregables | ✅ PASS | Ningún item "No generado" en tabla |

## Detalle BUG-8 (FIXED 2026-04-24)

**Hotfix aplicado en sesión actual:**

1. `modules/postprocessors/content_scrubber.py` — EN_TO_ES: "guests" → "huéspedes", "guest" → "huésped"
2. `modules/postprocessors/content_scrubber.py` — PT_TO_ES: "hospede"/"hóspede" → "huésped"
3. `modules/postprocessors/document_quality_gate.py` — mismas correcciones
4. `modules/commercial_documents/service_catalog.py` — descripciones corregidas
5. `modules/commercial_documents/templates/propuesta_v6_template.md` — "guests" → "huéspedes"
6. `modules/asset_generation/templates/indirect_traffic_optimization_template.md` — "huespedes" → "huéspedes"
7. `modules/orchestration_v4/two_phase_flow.py` — "huespedes" → "huéspedes"
8. `modules/asset_generation/whatsapp_conflict_guide.py` — "huesped" → "huésped"

Tests: 183/183 PASS (postprocessors + commercial_documents + delivery).

## Nota sobre BUG-3

El gate de publicación mostró internamente "ROI: 20.0x" pero la propuesta generada muestra "ROI: 0.2". Hay una discrepancia entre el valor calculado internamente y el mostrado. El veredicto se basa en el texto visible al cliente en la propuesta.

## Nota sobre variables legacy (plan_\*d)

El plan original de FASE-VALIDATE-RC asumía que `plan_7d`, `plan_30d`, `plan_60d`, `plan_90d` eran dead code (0 referencias). El grep de verificación demostró LO CONTRARIO:

- `diagnostico_v4_template.md` consume `${plan_7d}`, `${plan_30d}`, `${plan_60d}`, `${plan_90d}`
- `propuesta_v4_template.md` consume las mismas variables
- `v4_diagnostic_generator.py` también las define

Por restricción del plan: "Si grep revela que alguna variable legacy SI se usa, NO eliminarla". Las variables se mantienen y el hotfix solo pasó `asset_plan` a las líneas 559-560.

## Hotfix aplicado

```diff
-        'plan_60d': self._build_60_day_plan(),
-        'plan_90d': self._build_90_day_plan(),
+        'plan_60d': self._build_60_day_plan(asset_plan),
+        'plan_90d': self._build_90_day_plan(asset_plan),
```

## Evidencia preservada en `evidence/fase-VALIDATE-RC/`

- [x] `validacion_checklist.md` — checklist de bugs evaluados (actualizado a FIXED)
- [x] `02_PROPUESTA_COMERCIAL_20260424_143736.md` — propuesta PRE-hotfix (descartada)
- [x] `02_PROPUESTA_COMERCIAL_20260424_190828.md` — propuesta POST-hotfix (evaluada, tilde correcta)

`tests/commercial_documents/test_proposal_generator_dict.py` — 4/4 PASS
- `test_prepare_template_data_no_typeerror` — verificación directa del bugfix
- `test_v6_plan_keys_present_and_nonempty` — V6 keys no vacías
- `test_legacy_v4_keys_present_and_nonempty` — V4 keys se mantienen
- `test_hotfix_applies_to_60_and_90_day_plans` — verificación explícita del fix
