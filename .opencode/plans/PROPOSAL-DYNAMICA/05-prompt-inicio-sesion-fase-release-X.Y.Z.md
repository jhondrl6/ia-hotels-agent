# FASE-RELEASE-X.Y.Z: Release y Documentación

**ID**: FASE-RELEASE-X.Y.Z  
**Objetivo**: Documentar, sincronizar versiones y hacer release de la corrección arquitectónica  
**Dependencias**: FASE-CAUSAL-VALIDATE (verificación exitosa)  
**Duración estimada**: 1-2 horas  
**Skill**: Documentación (workflow §4.5)

---

## Contexto

### Corrección Aplicada
- `SERVICE_CATALOG` creado: mapeo dinámico pain→servicio
- `_generate_asset_quality_table` refactorizado para usar pains detectados
- Tabla principal del template ahora dinámica (no hardcodeada)

### Versión
> **NOTA**: La versión X.Y.Z se determina después de FASE-CAUSAL-VALIDATE. Usar `v4.35.0` o la siguiente versión disponible.

### Verificación Previa Requerida
- [ ] FASE-CAUSAL-VALIDATE completada exitosamente
- [ ] Tests pasan
- [ ] Propuesta dinámica verificada

---

## Tareas: Flujo §4.5 Documentación Obligatoria

### Paso 4.5.1: Registrar Fases en REGISTRY.md

Ejecutar `log_phase_completion.py` para cada fase del plan:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Registrar FASE-CAUSAL-DIAG
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-CAUSAL-DIAG \
    --desc "Diagnosticar mapeo pain→servicio y documentar gap analysis" \
    --archivos-nuevos "" \
    --archivos-mod "N/A (solo lectura)" \
    --tests "0" \
    --check-manual-docs

# Registrar FASE-CAUSAL-REFACTOR
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-CAUSAL-REFACTOR \
    --desc "Refactorizar generador: SERVICE_CATALOG + propuesta dinámica desde pains" \
    --archivos-nuevos "modules/commercial_documents/service_catalog.py" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md" \
    --tests "N" \
    --check-manual-docs

# Registrar FASE-CAUSAL-VALIDATE
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-CAUSAL-VALIDATE \
    --desc "Verificación unitaria: propuesta dinámica refleja pains detectados (sin E2E v4complete)" \
    --archivos-nuevos "tests/commercial_documents/test_proposal_dynamic.py" \
    --archivos-mod "N/A (verificación)" \
    --tests "N" \
    --check-manual-docs

# Registrar FASE-RELEASE-X.Y.Z
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-X.Y.Z \
    --desc "Release X.Y.Z: Propuesta dinámica desde pain detection" \
    --archivos-mod "VERSION.yaml,CHANGELOG.md,GUIA_TECNICA.md,docs/contributing/REGISTRY.md,AGENTS.md,README.md" \
    --check-manual-docs
```

---

### Paso 4.5.2: Sincronizar Versiones

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

./venv/Scripts/python.exe scripts/sync_versions.py

# Verificar sincronización
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

---

### Paso 4.5.3: Validar CHANGELOG.md

**Ubicación**: `CHANGELOG.md` (raíz del proyecto)

**Formato requerido** (según CONTRIBUTING.md §78-85):

```markdown
## [X.Y.Z] - Título (Fecha)

### Objetivo
Propuesta comercial ahora se genera dinámicamente desde los pains detectados, en vez de un diccionario estático de 7 servicios.

### Cambios Implementados
- `modules/commercial_documents/service_catalog.py` - NUEVO: SERVICE_CATALOG con mapeo pain→servicio
- `modules/commercial_documents/v4_proposal_generator.py` - Refactorizado _generate_asset_quality_table para usar pains detectados
- `modules/commercial_documents/templates/propuesta_v6_template.md` - Tabla principal ahora dinámica

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `v4_proposal_generator.py` | Propuesta dinámica desde pain detection |
| `propuesta_v6_template.md` | Tabla principal dinámica |

### Tests
- Tests de proposal_alignment verificados (backwards compatible)
```

**Checklist CHANGELOG:**
- [ ] Entrada `[X.Y.Z]` existe
- [ ] Tiene sección `### Objetivo`
- [ ] Tiene sección `### Cambios Implementados`
- [ ] Tiene sección `### Archivos Modificados`
- [ ] Tiene sección `### Tests`
- [ ] No hay entradas duplicadas

---

### Paso 4.5.4: GUIA_TECNICA.md — Nota Técnica X.Y.Z

**Ubicación**: `docs/GUIA_TECNICA.md`

**Agregar nota técnica** (sección "Notas de Cambios vX.Y.Z"):

```markdown
## Notas de Cambios vX.Y.Z

### Problema
La propuesta comercial generaba servicios desde un diccionario estático (PROPOSAL_SERVICE_TO_ASSET con 7 entradas fijas), independientemente de los pains detectados dinámicamente. Esto causaba desalineamiento: servicios ofrecidos que el hotel no necesitaba, y pains detectados sin servicio correspondiente.

### Solución
- Creado SERVICE_CATALOG: catálogo de servicios vendibles con mapeo a pain_id
- Refactorizado _generate_asset_quality_table() para iterar sobre detected_pains
- Tabla principal del template ahora dinámica (placeholder ${dynamic_services_table})

### Módulos Afectados
- `modules/commercial_documents/service_catalog.py` (NUEVO)
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`

### Backwards Compatibility
✅ Compatible. PROPOSAL_SERVICE_TO_ASSET se mantiene para backwards compatibility de gates de publicación.

### Tests
- Tests de proposal_alignment verificados con 13/13 PASS
```

---

### Paso 4.5.5: Prueba E2E (ÚNICA - Post-Implementación)

> ⚠️ **CRÍTICO — Minimización de Costos API**
> Esta prueba se ejecuta UNA SOLA VEZ al final de FASE-RELEASE.
> NO se ejecutó en fases previas (DIAG, REFACTOR, VALIDATE) para evitar costos duplicados.
> Si la prueba falla, se crea una FASE-PATCH correctiva, NO se re-ejecuta aquí.

**URL de prueba**: `https://amaziliahotel.com/`

**Objetivo**: Validar que la propuesta ahora muestra servicios basados en los pains detectados.

**Ejecución**:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Crear directorio de evidencia
mkdir -p evidence/release-e2e

# Ejecutar v4complete E2E — ÚNICA vez
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ 2>&1 | tee evidence/release-e2e/ejecucion.log
```

**Validaciones post-ejecución**:

```bash
# 1. Verificar que la propuesta tiene servicios dinámicos
./venv/Scripts/python.exe -c "
import json, glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')

propuestas = sorted(glob.glob('output/v4_complete/*PROPUESTA*.md'))
if propuestas:
    contenido = open(propuestas[-1], encoding='utf-8').read()
    servicios = re.findall(r'^\|\s*([^|]+?)\s*\|', contenido, re.MULTILINE)
    servicios = [s.strip() for s in servicios if s.strip() and '---' not in s and 'Entregable' not in s]
    print(f'Servicios en propuesta: {len(servicios)}')
    for s in servicios:
        print(f'  - {s}')
"

# 2. Verificar coherence score
./venv/Scripts/python.exe -c "
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
log = open('evidence/release-e2e/ejecucion.log', encoding='utf-8', errors='replace').read()
coherence = re.search(r'coherence[:\s]+([0-9.]+)', log, re.IGNORECASE)
if coherence:
    score = float(coherence.group(1))
    print(f'Coherence Score: {score} (umbral: 0.8) - {\"PASS\" if score >= 0.8 else \"FAIL\"}')
"

# 3. Verificar sin errores críticos
./venv/Scripts/python.exe -c "
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
log = open('evidence/release-e2e/ejecucion.log', encoding='utf-8', errors='replace').read()
errors = re.findall(r'ERROR|FATAL|CRASH|Traceback', log, re.IGNORECASE)
# Filtrar warnings de API que activaron fallback
real_errors = [e for e in errors if 'LLM query failed' not in e]
print(f'Errores criticos: {len(real_errors)}')
if real_errors:
    for e in real_errors[:5]:
        print(f'  {e}')
else:
    print('Sin errores criticos')
"
```

**Criterios de aceptación** (TODOS deben pasar):

| # | Criterio | Veredicto |
|---|----------|-----------|
| 1 | Ejecución completa sin crash fatal | ✅/❌ |
| 2 | Propuesta tiene servicios dinámicos (basado en pains) | ✅/❌ |
| 3 | Sin errores ERROR/FATAL/Traceback críticos | ✅/❌ |
| 4 | Coherence score >= 0.8 | ✅/❌ |

**Si pasa**: Continuar con Paso 4.5.6 (Validación Final) y commit.

**Si falla**: NO re-ejecutar. Documentar en el checklist: "❌ E2E FALLÓ — Crear FASE-PATCH correctiva" y proceder con documentación indicando la falla.

---

### Paso 4.5.6: Validación Final

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Ejecutar todas las validaciones
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Verificar estado del sistema
./venv/Scripts/python.exe scripts/doctor.py --status
```

**Checklist Final:**
- [ ] `run_all_validations.py --quick` pasa (4/4)
- [ ] `doctor.py --status` ejecutado sin errores críticos
- [ ] `version_consistency_checker.py` pasa
- [ ] CHANGELOG.md con formato correcto
- [ ] GUIA_TECNICA.md con nota técnica

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase:

1. **Verificar REGISTRY.md**:
   ```bash
   grep "FASE-CAUSAL" docs/contributing/REGISTRY.md
   grep "X.Y.Z" docs/contributing/REGISTRY.md
   ```

2. **Determinar versión** (si no fue determinada antes):
   - Revisar `VERSION.yaml` y elegir la siguiente versión

3. **Commit y tag**:
   ```bash
   git add -A
   git commit -m "FASE-RELEASE-X.Y.Z: Propuesta dinámica desde pain detection"
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   git push origin main --tags
   ```

4. **Verificar que sync_versions actualizó**:
   - `AGENTS.md`
   - `README.md`
   - `.cursorrules`
   - `CONTRIBUTING.md`
   - `GUIA_TECNICA.md`
   - `REGISTRY.md`

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] `log_phase_completion.py` ejecutado para las 4 fases
- [ ] `sync_versions.py` ejecutado sin errores
- [ ] `version_consistency_checker.py` pasa
- [ ] CHANGELOG.md con entrada [X.Y.Z] y formato correcto
- [ ] GUIA_TECNICA.md con nota técnica vX.Y.Z
- [ ] **E2E v4complete (ÚNICA) — ejecutada al final**
  - [ ] Criterio 1: Ejecución sin crash fatal
  - [ ] Criterio 2: Propuesta con servicios dinámicos
  - [ ] Criterio 3: Sin errores ERROR/FATAL/Traceback críticos
  - [ ] Criterio 4: Coherence score >= 0.8
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` sin errores críticos
- [ ] REGISTRY.md actualizado con las 4 fases
- [ ] Commit creado con mensaje "FASE-RELEASE-X.Y.Z"
- [ ] Tag `vX.Y.Z` creado

> ⚠️ **Si E2E falla**: No re-ejecutar. Marcar ❌, documentar en REGISTRY.md como "FASE-RELEASE-X.Y.Z — E2E FALLÓ" y crear FASE-PATCH correctiva en siguiente sesión.

---

## Restricciones

- [ Seguir exactamente el flujo §4.5 ]
- [ NO omitir ningún paso ]
- [ Verificar cada checklist antes de continuar ]
- [ NO re-ejecutar E2E si falla — crear FASE-PATCH ]

---

## Prompt de Ejecución

```
Actúa como release manager. Tu objetivo es documentar y hacer release de la corrección arquitectónica.

CONTEXTO:
- FASE-CAUSAL-DIAG, FASE-CAUSAL-REFACTOR, FASE-CAUSAL-VALIDATE completadas
- Necesitas hacer el flujo de documentación §4.5 completo
- Versión a usar: X.Y.Z (determinada según la siguiente disponible)

TAREAS:
1. Ejecutar log_phase_completion.py para las 4 fases
2. Ejecutar sync_versions.py
3. Validar/crear entrada [X.Y.Z] en CHANGELOG.md
4. Agregar nota técnica en GUIA_TECNICA.md
5. **EJECUTAR PRUEBA E2E v4complete ÚNICA** (este es el ÚNICO lugar donde se ejecuta):
   - URL: https://amaziliahotel.com/
   - Objetivo: Verificar que la propuesta tiene servicios dinámicos basados en pains
   - NOTA: NO se ejecutó en DIAG/REFACTOR/VALIDATE — solo aquí para minimizar costos API
6. Ejecutar run_all_validations.py --quick
7. Ejecutar doctor.py --status
8. Commit y tag vX.Y.Z

CRITERIOS:
- Todas las fases registradas en REGISTRY.md
- 6 archivos sincronizados con VERSION.yaml
- CHANGELOG con formato correcto
- **E2E v4complete pasa (servicios dinámicos, coherence >= 0.8)**
- Validaciones pasan 4/4
- Tag vX.Y.Z creado y pushado
```
