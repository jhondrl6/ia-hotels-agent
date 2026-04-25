# FASE-C: Fix Propuesta Comercial — Template V6 + Lenguaje de Entregables

**ID**: FASE-C
**Objetivo**: Crear template V6 funcional, eliminar mensajes de error en tabla de entregables, corregir ortografia y timeline de implementacion.
**Dependencias**: FASE-A completada (catalogos alineados), FASE-B completada (financiero estable)
**Duracion estimada**: 2.5 - 3 horas
**Skill**: test-driven-development, constrained-content-generation

---

## Contexto

La propuesta comercial es el entregable que ve el cliente. Actualmente usa un template embebido con errores de ortografia, secciones vacias y mensajes tecnicos como "No generado". Esta fase transforma la experiencia del cliente sin cambiar la logica financiera ya corregida en FASE-B.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | Completada |
| FASE-B | Completada |

### Base Tecnica Disponible
- Archivos existentes: `modules/commercial_documents/v4_proposal_generator.py`, `modules/commercial_documents/templates/diagnostico_v4_template.md`
- Variables de template: ver lista completa en `context_validado.md` seccion "Variables de Template Disponibles"
- Tests: `tests/commercial_documents/test_proposal_confidence_disclosure.py`, `tests/commercial_documents/test_proposal_dynamic.py`

---

## Tareas

### Tarea 1: Crear propuesta_v6_template.md
**Objetivo**: Tener un template externo completo en lugar del embebido.

**Archivos afectados**:
- `modules/commercial_documents/templates/propuesta_v6_template.md` (NUEVO)
- `modules/commercial_documents/v4_proposal_generator.py` (ajustar carga de template)

**Criterios de aceptacion**:
- [ ] Template incluye TODAS las variables de `_prepare_template_data()`
- [ ] Seccion "Esto es lo que hacemos por usted" usa `${dynamic_services_table}` con fallback a 7 servicios estandar cuando no hay pains detectados
- [ ] Seccion "Tabla de entregables" usa `${asset_quality_table}`
- [ ] Correccion de ortografia: "hoteles" (no "hotels"), "brille" (no "brillen"), "proveer" (no "prover"), "Absorbido" (no "Absorption"), "proteccion" (no "protecion")
- [ ] `_load_template()` encuentra y carga V6 correctamente

### Tarea 2: Fallback de servicios dinamicos cuando no hay pains
**Objetivo**: Resolver BUG-1 (seccion vacia cuando detected_pain_ids es None).

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (`_generate_dynamic_services_table()`)

**Criterios de aceptacion**:
- [ ] Si `detected_pain_ids` es None/empty, `_generate_dynamic_services_table()` retorna tabla con los 7 servicios de SERVICE_CATALOG (no string vacio)
- [ ] Si hay pains detectados, retorna solo servicios relevantes (comportamiento actual preservado)
- [ ] Test que verifica fallback: tabla no vacia cuando pain_ids=None

### Tarea 3: Cambiar lenguaje de tabla de entregables
**Objetivo**: Resolver BUG-4 y D-7 (6 de 7 items bloqueados).

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (`_confidence_to_nivel_significado()`)

**Criterios de aceptacion**:
- [ ] "No generado" -> "Incluido en su kit (preparacion posterior a firma)"
- [ ] "Requiere datos" -> "En preparacion (datos pendientes)"
- [ ] "Pendiente" -> "Incluido en su kit"
- [ ] "En desarrollo" -> "En optimizacion"
- [ ] NUNCA mostrar "No generado" ni "Requiere datos" al cliente final
- [ ] Nivel tecnico real se conserva internamente (logs), pero la propuesta muestra lenguaje positivo

### Tarea 4: Corregir timeline de implementacion
**Objetivo**: Resolver D-4 (quick wins = 30 dias vs promesa 7 dias).

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (`_build_7_day_plan()`, `_build_30_day_plan()`, etc.)

**Criterios de aceptacion**:
- [ ] Dia 1-7: Solo quick wins que NO requieran datos externos (FAQ, schema basico, WhatsApp si ya tiene numero)
- [ ] Dia 8-30: Implementacion de assets que requieren datos (Maps, SEO, Open Graph con fotos reales)
- [ ] Dia 31-60: Optimizacion avanzada y configuracion de analytics
- [ ] Dia 61-90: Reporte y ajustes
- [ ] Si un asset requiere dato que no se tiene (ej: fotos para OG), el plan dice "Pendiente de recibir fotos del cliente"

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| TestAssetQualityTable | `tests/commercial_documents/test_proposal_confidence_disclosure.py` | 5/5 PASS (lenguaje actualizado) |
| TestProposalDynamicFiltering | `tests/commercial_documents/test_proposal_dynamic.py` | 14/14 PASS |
| Tests delivery | `tests/delivery/test_delivery_packager.py` | Sin regresiones |

**Comando de validacion**:
```bash
venv/Scripts/python.exe -m pytest tests/commercial_documents/ tests/delivery/ -v --tb=short
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

1. **`.opencode/plans/06-checklist-implementacion.md`** -> Marcar FASE-C completada
2. **`09-documentacion-post-proyecto.md`** -> Seccion A: template V6 nuevo; Seccion D: lenguaje de entregables corregido
3. **REGISTRY.md**:
```bash
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-C --desc "Template V6 + fallback servicios dinamicos + lenguaje entregables + timeline realista" --archivos-nuevos "modules/commercial_documents/templates/propuesta_v6_template.md" --archivos-mod "modules/commercial_documents/v4_proposal_generator.py" --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] Template V6 existe y es cargado por _load_template()
- [ ] Tests commercial_documents y delivery: 0 regresiones
- [ ] Validaciones del proyecto: 4/4
- [ ] 06-checklist-implementacion.md actualizado
- [ ] REGISTRY.md actualizado
- [ ] Post-ejecucion completada

---

## Restricciones

- NO ejecutar v4complete en esta fase (optimizacion costos API)
- NO modificar calculos financieros (FASE-B ya los corrigio)
- El template V6 debe ser renderable con safe_substitute (variables opcionales no deben romper)
