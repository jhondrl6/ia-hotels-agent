# FASE-D: gate_report con verificacion de presencia en sitio

**ID**: FASE-D
**Objetivo**: Corregir el gate_report.json para que no marque como "missing" assets que ya existen en el sitio real del hotel, integrando la verificacion de SitePresenceChecker en el calculo de alignment.
**Dependencias**: Ninguna (independiente de FASE-A, B, C)
**Duracion estimada**: 1-1.5 horas
**Skill**: phased_project_executor v2.4.0

---

## Contexto

El gate_report.json de AmaziliaHotel reporta:
- `alignment_percentage=14.3%`
- 2 missing: whatsapp_button, open_graph

Pero whatsapp_button YA EXISTE en el sitio real del hotel (verificado por SitePresenceChecker con status EXISTS). El gate solo verifica si el pipeline genero un archivo, no si el asset ya existe en produccion. Esto:

1. **Infla el conteo de "missing"** con falsos positivos
2. **Baja el alignment_percentage** artificialmente
3. **Pierde credibilidad** ante el cliente: dice "falta WhatsApp" cuando el hotel lo tiene

El SitePresenceChecker YA tiene la logica de verificacion (check_site, PresenceStatus.EXISTS, should_generate). El gate_report simplemente no la consulta.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | Pendiente o Completada (independiente) |
| FASE-B | Pendiente o Completada (independiente) |
| FASE-C | Pendiente o Completada (independiente) |

### Base Tecnica Disponible
- Gate report: buscar donde se genera gate_report.json (v4_asset_orchestrator o quality gates)
- SitePresenceChecker: `modules/asset_generation/conditional_generator.py` o modulo dedicado
- PresenceStatus: EXISTS, NOT_EXISTS, REDUNDANT, VERIFICATION_FAILED
- Tests base: 2224 funciones

---

## Tareas

### Tarea 1: Localizar generacion de gate_report.json

**Objetivo**: Encontrar donde se calcula alignment_percentage y se genera la lista de "missing" assets.

**Archivos afectados**:
- Buscar en `modules/quality_gates/` o `modules/asset_generation/`
- Buscar "alignment_percentage" y "missing" en el codebase

**Pasos**:
1. Buscar donde se genera gate_report.json
2. Identificar la funcion que calcula alignment_percentage
3. Identificar donde se decide si un asset es "missing" vs "present"
4. Documentar el flujo actual

**Criterios de aceptacion**:
- [ ] Funcion de generacion de gate_report identificada
- [ ] Logica de "missing" entendida y documentada

### Tarea 2: Integrar SitePresenceChecker en evaluacion de assets

**Objetivo**: Antes de marcar un asset como "missing", verificar si ya existe en el sitio real via SitePresenceChecker.

**Archivos afectados**:
- Archivo de generacion de gate_report (identificado en Tarea 1)

**Pasos**:
1. En la evaluacion de cada asset, agregar pre-check:
   - Si SitePresenceChecker.check_site() retorna EXISTS → marcar como "present_in_production" (no "missing")
   - Si retorna NOT_EXISTS o VERIFICATION_FAILED → marcar como "missing" (comportamiento actual)
   - Si retorna REDUNDANT → marcar como "redundant" (ya entregado antes)
2. Agregar campo al gate_report: `presence_verified: true/false` por asset
3. Recalcular alignment_percentage excluyendo assets "present_in_production"

**Criterios de aceptacion**:
- [ ] Assets que existen en sitio real NO se marcan como "missing"
- [ ] gate_report incluye campo presence_verified por asset
- [ ] alignment_percentage excluye falsos positivos
- [ ] Para AmaziliaHotel: whatsapp_button aparece como "present_in_production", no "missing"

### Tarea 3: Agregar categoria "present_in_production" al reporte

**Objetivo**: El gate_report debe distinguir entre:
- `generated`: Asset generado por el pipeline
- `present_in_production`: Asset ya existe en sitio real (no necesita generacion)
- `missing`: Asset ni generado ni existente en sitio (requiere intervencion)
- `skipped`: Asset saltado por gate condicional

**Archivos afectados**:
- Archivo de generacion de gate_report
- Posible template de reporte

**Pasos**:
1. Definir enum o constantes para las categorias
2. Modificar la logica de clasificacion para usar las 4 categorias
3. Actualizar el output JSON con la nueva estructura

**Criterios de aceptacion**:
- [ ] gate_report distingue 4 categorias de assets
- [ ] Output JSON es backward compatible (campos anteriores siguen existiendo)
- [ ] La nueva categoria se refleja claramente en el reporte

### Tarea 4: Tests de regresion

**Archivos afectados**:
- `tests/quality_gates/test_publication_gates.py` (o donde esten los tests del gate)
- Nuevo: test para presence verification en gate_report

**Pasos**:
1. Ejecutar tests existentes de quality gates
2. Crear test: "asset con PresenceStatus.EXISTS no se marca como missing"
3. Crear test: "asset con PresenceStatus.NOT_EXISTS se marca como missing"
4. Crear test: "alignment_percentage calcula correctamente con presence_verified"
5. Crear test: "gate_report backward compatible"

**Criterios de aceptacion**:
- [ ] Todos los tests existentes pasan (0 regresiones)
- [ ] Al menos 4 tests nuevos
- [ ] `pytest tests/quality_gates/ -v` pasa 100%

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| test_publication_gates.py | tests/quality_gates/ | Pasa sin regresion |
| test_asset_confidence_gate.py | tests/quality_gates/ | Pasa sin regresion |
| test_gate_presence.py | tests/quality_gates/ (NUEVO) | Presence verification funciona |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/ -v --timeout=60
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-D como Completada con fecha
2. **`README.md` del plan**: Actualizar tabla de progreso
3. **`09-documentacion-post-proyecto.md`**: Seccion A (modulos), D (metricas), E (archivos)

---

## Criterios de Completitud (CHECKLIST)

- [ ] **gate_report no marca como missing assets que existen en sitio**
- [ ] **presence_verified por asset en output JSON**
- [ ] **alignment_percentage recalculado correctamente**
- [ ] **4 categorias de assets en gate_report**
- [ ] **Tests nuevos pasan**: 4+ tests nuevos
- [ ] **Tests existentes sin regresion**: `pytest tests/quality_gates/ -v` 100%
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: FASE-D marcada como completada
- [ ] **Post-ejecucion completada**: Todos los puntos anteriores realizados

---

## Restricciones

- NO modificar SitePresenceChecker (ya funciona correctamente)
- NO cambiar la logica de generacion condicional (ya SKIP correctamente)
- Solo modificar como el gate_report EVALUA lo que ya existe
- Mantener backward compatibility en el JSON de output
- Maximo 60 iteraciones del agente en esta fase

---

## Prompt de Ejecucion

```
Actua como desarrollador senior de iah-cli.

OBJETIVO: Corregir gate_report.json para que no marque como "missing" assets que ya existen en el sitio real del hotel, integrando SitePresenceChecker en la evaluacion de alignment.

CONTEXTO:
- gate_report.json marca whatsapp_button como "missing" con alignment=14.3%
- Pero whatsapp_button YA EXISTE en el sitio del hotel (SitePresenceChecker dice EXISTS)
- El gate solo verifica si el pipeline genero un archivo, no si ya existe en produccion
- SitePresenceChecker YA tiene la logica (check_site, PresenceStatus.EXISTS, should_generate)

TAREAS:
1. Localizar donde se genera gate_report.json y se calcula alignment_percentage
2. Integrar SitePresenceChecker: antes de marcar "missing", verificar presencia en sitio
3. Agregar categoria "present_in_production" al reporte
4. Tests de presence verification en gate_report

CRITERIOS:
- Assets con PresenceStatus.EXISTS NO se marcan como "missing"
- gate_report incluye presence_verified por asset
- alignment_percentage excluye falsos positivos
- 4 categorias: generated, present_in_production, missing, skipped
- 0 regresiones

VALIDACIONES:
- pytest tests/quality_gates/ -v --timeout=60
- run_all_validations.py --quick
```
