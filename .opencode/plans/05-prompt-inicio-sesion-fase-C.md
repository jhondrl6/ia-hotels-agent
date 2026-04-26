# FASE-C: Reparar asset open_graph (template + activacion pain_id)

**ID**: FASE-C
**Objetivo**: Hacer que el asset open_graph funcione end-to-end: crear el template faltante y cablear el pain_id `no_og_tags` para que se active cuando audit_report detecta ausencia de OG tags.
**Dependencias**: Ninguna (independiente de FASE-A y FASE-B)
**Duracion estimada**: 1.5-2 horas
**Skill**: phased_project_executor v2.4.0

---

## Contexto

El Veredicto forense (Hallazgo 2b) confirmo que open_graph esta catalogado como IMPLEMENTED en asset_catalog.py pero:

1. El template `open_graph_template.html` NO EXISTE en disco
2. El pain_id `no_og_tags` NO se activa desde audit_report cuando `open_graph=false`
3. Resultado: el sistema NUNCA genera OG tags para hoteles que las necesitan

El asset_catalog lo tiene registrado con:
- `status=AssetStatus.IMPLEMENTED`
- `template=open_graph_template.html`
- `promised_by=["no_og_tags"]`

Pero ninguno de esos tres pilares funciona: el template no existe, el pain_id no se dispara, y por tanto nunca se genera.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | Pendiente o Completada (independiente) |
| FASE-B | Pendiente o Completada (independiente) |

### Base Tecnica Disponible
- Catalogo: `modules/asset_generation/asset_catalog.py` (entrada open_graph)
- Generator: `modules/asset_generation/conditional_generator.py`
- Pain mapper: `modules/pain_solution_mapper.py` (pain_id no_og_tags, lineas ~343-364)
- Audit report: genera campo open_graph (true/false) que deberia disparar el pain
- Templates existentes: ver `modules/asset_generation/templates/` para referencias de formato
- Tests base: 2224 funciones

---

## Tareas

### Tarea 1: Crear template open_graph_template.html

**Objetivo**: Crear el template HTML para OG tags que se inserta en el sitio del hotel.

**Archivos afectados**:
- `modules/asset_generation/templates/open_graph_template.html` (NUEVO)

**Pasos**:
1. Revisar templates existentes (faq_template.html, etc.) para mantener formato consistente
2. Crear template con OG tags estandar:
   - og:title, og:description, og:image, og:url, og:type, og:site_name
   - twitter:card, twitter:title, twitter:description, twitter:image
   - Placeholders variables: {{hotel_name}}, {{description}}, {{image_url}}, {{url}}, etc.
3. Verificar que el template sigue la convencion de nomenclatura del catalogo

**Criterios de aceptacion**:
- [ ] Archivo `open_graph_template.html` existe en `modules/asset_generation/templates/`
- [ ] Contiene placeholders para datos dinamicos del hotel
- [ ] Sigue convencion de formatos de templates existentes

### Tarea 2: Cablear pain_id no_og_tags desde audit_report

**Objetivo**: Cuando audit_report genera `open_graph=false`, el pain_id `no_og_tags` debe activarse en pain_solution_mapper.

**Archivos afectados**:
- `modules/pain_solution_mapper.py` (verificar y corregir activacion de no_og_tags)

**Pasos**:
1. Localizar donde audit_report genera el campo `open_graph` (true/false)
2. Verificar como pain_solution_mapper.py recibe ese campo
3. Si el mapeo no existe, crearlo: `open_graph=false` → activa pain_id `no_og_tags`
4. Verificar que el pain_id `no_og_tags` esta correctamente mapeado al asset `open_graph` en el catalogo
5. Agregar logs: "OG tags not detected → activating pain_id no_og_tags"

**Criterios de aceptacion**:
- [ ] `open_graph=false` en audit_report activa pain_id `no_og_tags`
- [ ] pain_id `no_og_tags` dispara generacion de asset open_graph
- [ ] Flujo end-to-end funciona: audit sin OG → pain → generacion → asset entregado
- [ ] Cuando `open_graph=true`, el pain NO se activa (no genera innecesariamente)

### Tarea 3: Verificar generacion end-to-end en conditional_generator

**Objetivo**: Confirmar que una vez el pain_id se activa, conditional_generator genera el asset correctamente usando el template.

**Archivos afectados**:
- `modules/asset_generation/conditional_generator.py` (verificar rama open_graph)

**Pasos**:
1. Localizar la rama de generacion para open_graph en conditional_generator
2. Verificar que lee el template `open_graph_template.html`
3. Verificar que llena los placeholders con datos del hotel (nombre, descripcion, imagen, URL)
4. Si no existe la rama, crearla siguiendo el patron de otros assets (faq, etc.)

**Criterios de aceptacion**:
- [ ] conditional_generator tiene rama funcional para open_graph
- [ ] Usa template y llena placeholders con datos reales del hotel
- [ ] Output es un HTML valido con OG tags completos

### Tarea 4: Tests de regresion y validacion

**Archivos afectados**:
- `tests/asset_generation/test_conditional_generator.py`
- `tests/asset_generation/test_asset_catalog.py` (si cambian entradas)
- Nuevo: `tests/asset_generation/test_open_graph_generation.py`

**Pasos**:
1. Ejecutar tests existentes: `pytest tests/asset_generation/ -v --timeout=60`
2. Crear test: "audit_report con open_graph=false activa pain_id no_og_tags"
3. Crear test: "pain_id no_og_tags genera asset open_graph con template"
4. Crear test: "audit_report con open_graph=true NO activa pain_id"
5. Crear test: "template open_graph genera HTML valido con placeholders reemplazados"

**Criterios de aceptacion**:
- [ ] Todos los tests existentes pasan (0 regresiones)
- [ ] Al menos 4 tests nuevos cubriendo el flujo end-to-end
- [ ] `pytest tests/asset_generation/ -v` pasa 100%

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| test_conditional_generator.py | tests/asset_generation/ | Pasa sin regresion |
| test_asset_catalog.py | tests/asset_generation/ | open_graph catalogado correcto |
| test_open_graph_generation.py | tests/asset_generation/ (NUEVO) | 4+ tests pasan |
| test_content_gates.py | tests/asset_generation/ | Pasa sin regresion |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe -m pytest tests/asset_generation/ -v --timeout=60
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-C como Completada con fecha
2. **`README.md` del plan**: Actualizar tabla de progreso
3. **`09-documentacion-post-proyecto.md`**: Seccion A (modulos), D (metricas), E (archivos)

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Template creado**: `open_graph_template.html` existe y es valido
- [ ] **Pain_id cableado**: `no_og_tags` se activa desde audit_report
- [ ] **Generacion end-to-end**: audit sin OG → pain → generacion → asset
- [ ] **Tests nuevos pasan**: 4+ tests nuevos ejecutan exitosamente
- [ ] **Tests existentes sin regresion**: `pytest tests/asset_generation/ -v` 100%
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: FASE-C marcada como completada
- [ ] **Post-ejecucion completada**: Todos los puntos anteriores realizados

---

## Restricciones

- NO modificar la estructura de audit_report (ya genera open_graph=true/false correctamente)
- NO cambiar otros pain_ids (solo cablear no_og_tags)
- Mantener backward compatibility: si el pain no se activa, el sistema funciona como antes
- Maximo 60 iteraciones del agente en esta fase

---

## Prompt de Ejecucion

```
Actua como desarrollador senior de iah-cli.

OBJETIVO: Reparar el asset open_graph para que funcione end-to-end: crear template faltante, cablear pain_id no_og_tags desde audit_report, y verificar generacion completa.

CONTEXTO:
- asset_catalog.py marca open_graph como IMPLEMENTED pero el template no existe
- pain_id no_og_tags esta definido en pain_solution_mapper.py pero no se activa desde audit_report
- Resultado: el sistema nunca genera OG tags para hoteles que las necesitan

TAREAS:
1. Crear open_graph_template.html con OG tags estandar y placeholders
2. Cablear pain_id no_og_tags: audit_report.open_graph=false → activa pain
3. Verificar que conditional_generator genera el asset usando el template
4. Agregar tests end-to-end (pain activation, generacion, no-activacion cuando no aplica)

CRITERIOS:
- Template existe y tiene placeholders {{hotel_name}}, {{description}}, {{image_url}}, {{url}}
- open_graph=false en audit → pain_id no_og_tags se activa
- open_graph=true en audit → pain NO se activa
- Genera HTML valido con OG tags completos
- 0 regresiones en tests existentes

VALIDACIONES:
- pytest tests/asset_generation/ -v --timeout=60
- run_all_validations.py --quick
```
