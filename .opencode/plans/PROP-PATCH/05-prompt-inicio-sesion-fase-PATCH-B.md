---
description: FASE-PATCH-B — Alineacion de assets y disclaimers (SOL-2 + SOL-3 + SOL-5)
version: 1.0.0
plan: PROP-PATCH
---

# FASE-PATCH-B: Alineacion de Assets y Disclaimers

**ID**: PATCH-B  
**Objetivo**: Investigar assets faltantes, alinear propuesta con realidad, mejorar disclaimers Tier C, y documentar gate vs generator mismatch  
**Dependencias**: Ninguna (independiente de PATCH-A)  
**Duracion estimada**: 2 horas  
**Skill**: phased_project_executor v2.10.0  
**Iteraciones max**: 60  

---

## Contexto

La validacion post-ejecucion de Termales detecto que 3 servicios prometidos en la propuesta no tienen assets generados: SEO Local (optimization_guide), Boton de WhatsApp (whatsapp_button), y Meta Tags Sociales (open_graph). Estos assets SI existen en `asset_catalog.py` como IMPLEMENTED, pero la generacion condicional los salto porque los pain_ids que los activan no fueron detectados.

Ademas, todos los assets generados para Termales son ESTIMATED (confianza 0.5) porque el pipeline usa Tier C (benchmarks regionales) sin onboarding real.

Finalmente, el gate `proposal_asset_alignment` usa un mapeo estatico de 6 servicios, mientras que el generador de propuestas filtra dinamicamente segun pain_ids.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| PROP-A — G | ✅ Completadas |
| PATCH-A | ⏳/✅ (verificar en dependencias-fases.md) |
| PATCH-B | 🔵 En Progreso |
| PATCH-C | ⏳ Pendiente |
| PATCH-RELEASE | ⏳ Pendiente |

### Base Tecnica Disponible

- Archivos existentes:
  - `modules/asset_generation/asset_catalog.py`
  - `modules/asset_generation/proposal_asset_alignment.py`
  - `modules/commercial_documents/proposal_generator.py`
  - `modules/quality_gates/proposal_asset_alignment_gate.py`
- Diagnostico YAML de Termales disponible en `output/v4_complete/termales/`

---

## Tareas

### T1: SOL-2 — Investigar pain_ids para Termales

**Objetivo**: Determinar por que los pain_ids de optimization_guide, whatsapp_button y open_graph no se activaron.

**Archivos afectados**:
- Diagnostico YAML de Termales (`output/v4_complete/01_DIAGNOSTICO_*.md`)
- `modules/asset_generation/asset_catalog.py`

**Pasos**:
1. Leer el diagnostico YAML de Termales y extraer la lista de `pain_ids` detectados.
2. En `asset_catalog.py`, verificar los `promised_by` de:
   - `optimization_guide` (L176): `metadata_defaults`, `poor_performance`, `low_citability`, `low_content_length`
   - `whatsapp_button` (L54): `no_whatsapp_visible`, `whatsapp_conflict`
   - `open_graph` (L325): `no_og_tags`
3. Comparar: estan estos pain_ids en el diagnostico de Termales?
4. Si NO estan: la generacion condicional funciona correctamente; el problema es que la propuesta los promete igual.
5. Si SI estan: la generacion condicional tiene un bug de filtrado para Tier C.

**Criterios de aceptacion**:
- [ ] Lista de pain_ids detectados documentada
- [ ] Causa raiz identificada (propuesta promete de mas vs bug de filtrado)

---

### T2: SOL-2 — Alinear propuesta con realidad

**Objetivo**: Modificar la logica para que la propuesta solo liste servicios cuyos assets se generaran realmente.

**Archivos afectados**:
- `modules/commercial_documents/proposal_generator.py` (o archivo que genere la tabla de servicios)
- `modules/asset_generation/proposal_asset_alignment.py` (mapeo estatico)

**Decision arquitectonica** (ya tomada en plan):
- Si los pain_ids NO estan: filtrar la tabla de servicios en la propuesta para no incluir servicios sin assets.
- Si los pain_ids SI estan pero filtrado los descarta: corregir la logica de filtrado condicional.

**Pasos**:
1. Localizar donde se construye la tabla de servicios en la propuesta.
2. Implementar filtrado: solo incluir servicio si su asset correspondiente sera generado (o ya existe en catalogo con condiciones cumplidas).
3. Verificar que servicios restantes tienen assets generados.

**Criterios de aceptacion**:
- [ ] Propuesta no lista "SEO Local" si optimization_guide no se genera
- [ ] Propuesta no lista "Boton de WhatsApp" si whatsapp_button no se genera
- [ ] Propuesta no lista "Meta Tags Sociales" si open_graph no se genera
- [ ] Servicios que SI se generan siguen apareciendo

---

### T3: SOL-3 — Mejorar disclaimers Tier C

**Objetivo**: Agregar notas explicitas en la propuesta para que el cliente entienda que los assets son estimaciones basadas en benchmarks regionales.

**Archivos afectados**:
- `modules/commercial_documents/proposal_generator.py` (o template de propuesta)

**Pasos**:
1. Localizar el banner Tier C existente (lineas ~100-103 del template).
2. Agregar parrafo adicional debajo del banner:
   > "Nota: Los entregables listados se generan a partir de benchmarks regionales (Tier C) y datos publicos del sitio web. Para activos con datos operativos reales del hotel, se recomienda completar el proceso de onboarding."
3. Verificar que el texto aparece en la propuesta generada.

**Criterios de aceptacion**:
- [ ] Disclaimer visible en propuesta Tier C
- [ ] No afecta propuestas Tier A/B (condicional por `financial_evidence_tier`)

---

### T4: SOL-5 — Documentar gate vs generator mismatch

**Objetivo**: Dejar documentado que el gate valida un contrato estatico mientras el generador produce contenido dinamico.

**Archivos afectados**:
- `modules/quality_gates/proposal_asset_alignment_gate.py`
- `modules/commercial_documents/proposal_generator.py`

**Pasos**:
1. En `proposal_asset_alignment_gate.py`, agregar docstring en la funcion principal del gate:
   ```python
   """
   Valida alineacion entre servicios prometidos y assets generados.

   NOTA: Este gate valida un contrato estatico (PROPOSAL_SERVICE_TO_ASSET).
   El generador de propuestas filtra dinamicamente servicios segun pain_ids.
   Por tanto, un alignment_percentage < 100% puede ser esperado cuando
   el generador excluye servicios cuyos pain_ids no estan presentes.
   """
   ```
2. En `proposal_generator.py`, agregar comentario donde se filtran servicios:
   ```python
   # Los servicios se filtran dinamicamente por pain_ids detectados.
   # El gate estatico (proposal_asset_alignment_gate) valida el contrato completo;
   # ver FASE-PATCH-B para contexto.
   ```

**Criterios de aceptacion**:
- [ ] Docstring presente en gate
- [ ] Comentario presente en generador
- [ ] Sin cambios funcionales (solo documentacion)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| Tests de propuesta | `tests/` (buscar `proposal` o `alignment`) | Pasan sin regresiones |
| Validaciones | `scripts/run_all_validations.py --quick` | 4/4 checks pass |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**
   - Marcar PATCH-B como ✅ Completada

2. **`06-checklist-implementacion.md`**
   - Marcar tareas de PATCH-B como completadas

3. **`09-documentacion-post-proyecto.md`**
   - **Seccion B**: Confirmar archivos modificados
   - **Seccion C**: Documentar backwards compatibility (filtro de servicios)
   - **Seccion D**: Actualizar metricas (missing assets)

4. **`log_phase_completion.py`**:
   ```bash
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase PATCH-B \
       --desc "Alineacion de assets y disclaimers: SOL-2 (filtrar servicios por pain_ids) + SOL-3 (disclaimers Tier C) + SOL-5 (documentar mismatch)" \
       --archivos-mod "modules/commercial_documents/proposal_generator.py,modules/asset_generation/proposal_asset_alignment.py,modules/quality_gates/proposal_asset_alignment_gate.py" \
       --check-manual-docs
   ```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: Sin regresiones
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: Estado PATCH-B marcado
- [ ] **Documentacion afiliada**: GUIA_TECNICA.md actualizado (via log_phase_completion)
- [ ] **Post-ejecucion completada**: Todos los puntos realizados

---

## Restricciones

- **Maximo 60 iteraciones**
- **NO modificar** `main.py` ni `coherence_validator.py` (reservado para PATCH-A)
- **NO ejecutar v4complete** en esta fase (reservado para PATCH-C)
- **NO modificar ROADMAP.md**
- El filtrado de servicios debe ser backwards compatible: si no hay pain_ids, comportamiento previo
