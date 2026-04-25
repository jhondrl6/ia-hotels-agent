# FASE-D: AEO + Contenido Dinamico + Competidores

**ID**: FASE-D
**Objetivo**: Cerrar el gap de AEO (0/100) agregando entregable de citabilidad IA, agregar seccion de competencia identificada, y hacer planes de implementacion dinamicos basados en asset_plan.
**Dependencias**: FASE-A, FASE-B, FASE-C completadas
**Duracion estimada**: 2 - 2.5 horas
**Skill**: test-driven-development, systematic-debugging

---

## Contexto

Esta fase cierra gaps estrategicos que debilitan la propuesta: AEO ignorado, competencia sin nombre, y planes hardcoded. Es la ultima fase de codigo antes de la validacion con API.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | Completada |
| FASE-B | Completada |
| FASE-C | Completada |

### Base Tecnica Disponible
- Archivos existentes: `modules/commercial_documents/v4_proposal_generator.py`, `modules/auditors/citability_scorer.py`
- Datos de diagnostico: `citability_score`, `ao_score` (AEO)
- Asset plan: lista de assets con prioridades P1/P2/P3

---

## Tareas

### Tarea 1: Agregar entregable AEO si aoe_score < 20
**Objetivo**: Resolver D-1 (AEO 0/100 sin plan).

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (`_prepare_template_data()`)
- `modules/commercial_documents/service_catalog.py` (opcional: nuevo pain_id para AEO)

**Criterios de aceptacion**:
- [ ] Si `ao_score` (o `citability_score`) < 20, agregar servicio "Optimizacion para IA Generativa" a la tabla dinamica
- [ ] Descripcion: "Aparece cuando clientes preguntan a ChatGPT/Gemini 'donde hospedarme en [region]'"
- [ ] El servicio aparece en `_generate_dynamic_services_table()` cuando el pain correspondiente esta detectado
- [ ] NO romper el conteo de 7 servicios base (AEO es servicio adicional condicional)

### Tarea 2: Hacer planes 7/30/60/90 dias dinamicos
**Objetivo**: Resolver BUG-6 (planes hardcoded).

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (`_build_7_day_plan()`, `_build_30_day_plan()`, etc.)

**Criterios de aceptacion**:
- [ ] `_build_7_day_plan()` recibe `asset_plan` y genera timeline basado en assets P1 (prioridad alta)
- [ ] `_build_30_day_plan()` incluye assets P1 y P2
- [ ] `_build_60_day_plan()` incluye assets P3 y optimizacion
- [ ] `_build_90_day_plan()` incluye reporte y ajustes
- [ ] Si un asset no tiene datos suficientes, el plan dice "Pendiente: [dato faltante]"
- [ ] Fallback: si asset_plan es None, usar texto generico (backward compat)

### Tarea 3: Agregar seccion de competidores identificados
**Objetivo**: Resolver D-8 (sin competidores nombrados).

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (`_prepare_template_data()`)
- Template V6 (nueva variable `${competitors_section}`)

**Criterios de aceptacion**:
- [ ] Si GBP data contiene competidores cercanos, generar tabla con nombre, distancia, y brecha principal
- [ ] Si no hay competidores identificados, omitir la seccion (no mostrar vacia)
- [ ] La seccion va despues de "Esto es lo que hacemos por usted"

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| Tests commercial_documents | `tests/commercial_documents/` | 0 regresiones |
| Tests delivery | `tests/delivery/` | 0 regresiones |

**Comando de validacion**:
```bash
venv/Scripts/python.exe -m pytest tests/commercial_documents/ tests/delivery/ -v --tb=short
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

1. **`.opencode/plans/06-checklist-implementacion.md`** -> Marcar FASE-D completada
2. **`09-documentacion-post-proyecto.md`** -> Seccion A: planes dinamicos; Seccion D: AEO incluido
3. **REGISTRY.md**:
```bash
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-D --desc "AEO entregable condicional + planes dinamicos 7/30/60/90 + seccion competidores" --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/service_catalog.py" --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] Tests: 0 regresiones en commercial_documents y delivery
- [ ] Validaciones: 4/4
- [ ] 06-checklist-implementacion.md actualizado
- [ ] REGISTRY.md actualizado
- [ ] Post-ejecucion completada

---

## Restricciones

- NO ejecutar v4complete en esta fase (optimizacion costos API)
- NO modificar logica financiera (FASE-B)
- NO modificar template V6 salvo agregar variable `${competitors_section}`
