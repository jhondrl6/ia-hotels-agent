# FASE-RELEASE-4.34.0: Release y Documentación Completa

**ID**: FASE-RELEASE-4.34.0  
**Objetivo**: Documentar, sincronizar versiones y hacer release de la corrección  
**Dependencias**: FASE-CAUSAL-TEST (verificación exitosa)  
**Duración estimada**: 1-2 horas  
**Skill**: Documentación (workflow §4.5)

---

## Contexto

### Corrección Aplicada
- `PROPOSAL_SERVICE_TO_ASSET` ahora tiene 7 entradas (5 + FAQ + OG)
- La propuesta ahora lista dinámicamente los servicios basados en pains detectados

### Verificación Previa Requerida
- [ ] FASE-CAUSAL-TEST completada exitosamente
- [ ] Propuesta con 7 servicios verificada
- [ ] Tests pasan

---

## Tareas: Flujo §4.5 Documentación Obligatoria

### Paso 4.5.1: Registrar Fases en REGISTRY.md

Ejecutar `log_phase_completion.py` para cada fase del plan:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Registrar FASE-CAUSAL-DIAG
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-CAUSAL-DIAG \
    --desc "Diagnosticar causa raíz desalineamiento diagnóstico-propuesta" \
    --archivos-nuevos "" \
    --archivos-mod "N/A (solo lectura)" \
    --tests "0" \
    --check-manual-docs

# Registrar FASE-CAUSAL-FIX
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-CAUSAL-FIX \
    --desc "Corregir PROPOSAL_SERVICE_TO_ASSET, ASSET_NAMES y ambas tablas de propuesta" \
    --archivos-nuevos "" \
    --archivos-mod "modules/asset_generation/proposal_asset_alignment.py,modules/commercial_documents/pain_solution_mapper.py,modules/commercial_documents/templates/propuesta_v6_template.md" \
    --tests "N" \
    --check-manual-docs

# Registrar FASE-CAUSAL-TEST
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-CAUSAL-TEST \
    --desc "Verificación E2E con Amaziliahotel" \
    --archivos-nuevos "" \
    --archivos-mod "N/A (verificación)" \
    --tests "N" \
    --check-manual-docs

# Registrar FASE-RELEASE-4.34.0
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.34.0 \
    --desc "Release 4.34.0: FAQ y Open Graph en propuesta comercial" \
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
## [4.34.0] - Título (Fecha)

### Objetivo
Corregir desalineamiento entre diagnóstico de brechas y propuesta comercial agregando FAQ y Open Graph como servicios.

### Cambios Implementados
- `modules/asset_generation/proposal_asset_alignment.py` - Agregadas 2 entradas a PROPOSAL_SERVICE_TO_ASSET (FAQ, Open Graph)
- `modules/commercial_documents/pain_solution_mapper.py` - Completados ASSET_NAMES faltantes (`open_graph`, `og_tags_guide`)
- `modules/commercial_documents/templates/propuesta_v6_template.md` - Actualizada tabla principal a 7 servicios

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/proposal_asset_alignment.py` | Agregado: FAQ y Open Graph |
| `modules/commercial_documents/pain_solution_mapper.py` | ASSET_NAMES completados |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Tabla principal: 5 → 7 filas |

### Tests
- Tests de proposal_alignment verificados
```

**Checklist CHANGELOG:**
- [ ] Entrada `[4.34.0]` existe
- [ ] Tiene sección `### Objetivo`
- [ ] Tiene sección `### Cambios Implementados`
- [ ] Tiene sección `### Archivos Modificados`
- [ ] Tiene sección `### Tests`
- [ ] No hay entradas duplicadas

---

### Paso 4.5.4: GUIA_TECNICA.md — Nota Técnica v4.34.0

**Ubicación**: `docs/GUIA_TECNICA.md`

**Agregar nota técnica** (sección "Notas de Cambios v4.34.0"):

```markdown
## Notas de Cambios v4.34.0

### Problema
|La propuesta comercial hardcodeaba 5 servicios, pero el diagnóstico detectaba 4 brechas. FAQ y Open Graph no aparecían en la propuesta aunque sus mapeos existían en pain_solution_mapper.

### Solución
|- Agregadas 2 entradas a `PROPOSAL_SERVICE_TO_ASSET` en `proposal_asset_alignment.py`:
|  - "Página de FAQ" → "faq_page"
|  - "Meta Tags Sociales" → "open_graph"
|- Hacer dinámica la generación de servicios en la plantilla

### Módulos Afectados
|- `modules/asset_generation/proposal_asset_alignment.py`
|- `modules/commercial_documents/templates/propuesta_v6_template.md`

### Backwards Compatibility
|✅ Compatible. Solo agrega servicios, no modifica lógica existente.

### Tests
|- Tests de proposal_alignment verificados con 7 servicios
```

---

### Paso 4.5.5: Prueba E2E v4complete — ÚNICA (Post-Implementación)

> ⚠️ **CRÍTICO — Minimización de Costos API**
> Esta prueba se ejecuta UNA SOLA VEZ al final de FASE-RELEASE.
> NO se ejecutó en ninguna fase previa (DIAG, FIX, TEST) para evitar costos duplicados.
> Si la prueba falla, se crea una FASE-PATCH corrective, NO se re-ejecuta aquí.

**URL de prueba**: `https://amaziliahotel.com/`

**Objetivo**: Validar que el fix de FAQ + Open Graph aparece correctamente en:
1. El diagnóstico generado (brechas FAQ y OG detectadas si aplican)
2. La propuesta comercial (7 servicios en tabla principal y secundaria)
3. Los assets generados (faq_page, open_graph si gates pasan)

**Ejecución**:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Crear directorio de evidencia para esta prueba
mkdir -p evidence/release-e2e-amazilia

# Ejecutar v4complete E2E — ÚNICA vez al final
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ 2>&1 | tee evidence/release-e2e-amazilia/ejecucion.log
```

**Timeout**: 300s

**Validaciones post-ejecución** (solo si la ejecución succeeded):

```bash
# 1. Verificar que la propuesta tiene 7 servicios (no 5)
./venv/Scripts/python.exe -c "
import json, glob, re

# Buscar propuesta generada
propuestas = sorted(glob.glob('output/v4_complete/*PROPUESTA*.md'))
if propuestas:
    contenido = open(propuestas[-1], encoding='utf-8').read()
    # Contar filas de tabla de servicios (formato | Servicio |)
    servicios = re.findall(r'^\|\s*([^|]+?)\s*\|', contenido, re.MULTILINE)
    print(f'Servicios encontrados en propuesta: {len(servicios)}')
    for s in servicios[:10]:
        print(f'  - {s.strip()}')
else:
    print('WARNING: No se encontró propuesta')
"

# 2. Verificar que FAQ y Open Graph están en la propuesta
./venv/Scripts/python.exe -c "
import glob
propuestas = sorted(glob.glob('output/v4_complete/*PROPUESTA*.md'))
if propuestas:
    contenido = open(propuestas[-1], encoding='utf-8').read()
    has_faq = 'faq' in contenido.lower() or 'FAQ' in contenido
    has_og = 'open graph' in contenido.lower() or 'meta tag' in contenido.lower()
    print(f'FAQ presente: {has_faq}')
    print(f'Open Graph presente: {has_og}')
"

# 3. Verificar que no hay errores críticos en el log
./venv/Scripts/python.exe -c "
import re
log = open('evidence/release-e2e-amazilia/ejecucion.log').read()
errors = re.findall(r'ERROR|FATAL|CRASH|Traceback', log, re.IGNORECASE)
if errors:
    print(f'ERRORES detectadas: {len(errors)}')
    for e in errors[:5]:
        print(f'  {e}')
else:
    print('Sin errores críticos en el log')
"

# 4. Verificar coherence score
./venv/Scripts/python.exe -c "
import re
log = open('evidence/release-e2e-amazilia/ejecucion.log').read()
coherence = re.search(r'coherence[:\s]+([0-9.]+)', log, re.IGNORECASE)
if coherence:
    score = float(coherence.group(1))
    print(f'Coherence Score: {score} (umbral: 0.8)')
    print(f'PASS' if score >= 0.8 else 'FAIL')
else:
    print('Coherence score no encontrado en log')
"
```

**Criterios de aceptación** (TODOS deben pasar):

| # | Criterio | Veredicto |
|---|----------|-----------|
| 1 | Ejecución completa sin crash fatal | ✅/❌ |
| 2 | Propuesta tiene 7 servicios (FAQ + OG incluidos) | ✅/❌ |
| 3 | Sin errores ERROR/FATAL/Traceback en log | ✅/❌ |
| 4 | Coherence score >= 0.8 | ✅/❌ |

**Si pasa**: Continuar con Paso 4.5.6 (Validación Final) y commit.

**Si falla**: NO re-ejecutar. Documentar en el checklist: "❌ E2E FALLÓ — Crear FASE-PATCH correctiva" y proceder con documentación indicando la falla para que la siguiente sesión la aborde.

**Archivos generados** (guardar para evidencia):

```
evidence/release-e2e-amazilia/
├── ejecucion.log                  # Log completo de la ejecución
├── output/v4_complete/*PROPUESTA*.md  # Copia de la propuesta generada
└── output/v4_complete/01_DIAGNOSTICO*.md  # Copia del diagnóstico
```

---

### Paso 4.5.6: Validación Final

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Ejecutar todas las validaciones
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Verificar estado del sistema
./venv/Scripts/python.exe scripts/doctor.py --status

# Verificar DOMAIN_PRIMER (si hubo cambios arquitectónicos)
./venv/Scripts/python.exe scripts/doctor.py --context
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
   grep "4.34.0" docs/contributing/REGISTRY.md
   ```

2. **Commit y tag**:
   ```bash
   git add -A
   git commit -m "FASE-RELEASE-4.34.0: FAQ y Open Graph en propuesta comercial"
   git tag -a v4.34.0 -m "Release 4.34.0"
   git push origin main --tags
   ```

3. **Verificar que sync_versions actualizó**:
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
- [ ] CHANGELOG.md con entrada [4.34.0] y formato correcto
- [ ] GUIA_TECNICA.md con nota técnica v4.34.0
- [ ] **E2E v4complete (ÚNICA) — `https://amaziliahotel.com/` ejecutada al final**
  - [ ] Criterio 1: Ejecución sin crash fatal
  - [ ] Criterio 2: Propuesta con 7 servicios (FAQ + OG)
  - [ ] Criterio 3: Sin errores ERROR/FATAL/Traceback en log
  - [ ] Criterio 4: Coherence score >= 0.8
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` sin errores críticos
- [ ] REGISTRY.md actualizado con las 4 fases
- [ ] Commit creado con mensaje "FASE-RELEASE-4.34.0"
- [ ] Tag `v4.34.0` creado

> ⚠️ **Si E2E falla**: No re-ejecutar. Marcar ❌, documentar en REGISTRY.md como "FASE-RELEASE-4.34.0 — E2E FALLÓ" y crear FASE-PATCH correctiva en siguiente sesión.

---

## Restricciones

- [ Seguir exactamente el flujo §4.5 ]
- [ NO omitir ningún paso ]
- [ Verificar cada checklist antes de continuar ]

---

## Prompt de Ejecución

```
Actúa como release manager. Tu objetivo es documentar y hacer release de la corrección.

CONTEXTO:
- FASE-CAUSAL-DIAG, FASE-CAUSAL-FIX, FASE-CAUSAL-TEST completadas
- Necesitas hacer el flujo de documentación §4.5 completo

TAREAS:
1. Ejecutar log_phase_completion.py para las 4 fases
2. Ejecutar sync_versions.py
3. Validar/crear entrada [4.34.0] en CHANGELOG.md
4. Agregar nota técnica en GUIA_TECNICA.md
5. **EJECUTAR PRUEBA E2E v4complete ÚNICA** (post-implementación, no en fases previas):
   - URL: https://amaziliahotel.com/
   - Objetivo: Verificar que FAQ y Open Graph aparecen en propuesta con 7 servicios
   - Costo: 1 ejecución API al final, no en fases previas
6. Ejecutar run_all_validations.py --quick
7. Ejecutar doctor.py --status
8. Commit y tag

CRITERIOS:
- Todas las fases registradas en REGISTRY.md
- 6 archivos sincronizados con VERSION.yaml
- CHANGELOG con formato correcto
- **E2E v4complete pasa (7 servicios, coherence >= 0.8)**
- Validaciones pasan 4/4
- Tag v4.34.0 creado y pushado
```
