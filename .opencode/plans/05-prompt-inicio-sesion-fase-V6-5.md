---
description: FASE V6-5 - E2E Certification con v4complete para Hotel Vísperas
version: 1.0.0
fase: V6-5
---

# FASE V6-5: E2E Certification v4complete → V6

## Contexto

Ejecución end-to-end del flujo completo para certificar que:
1. Los templates V6 se usan correctamente
2. Los datos reales del audit llenan los placeholders
3. Los assets son coherentes con la propuesta V6
4. El coherence score cumple el threshold

**Dependencia:** FASE V6-1, V6-2, V6-3, V6-4 (todas completadas)

## Tarea Única: Ejecución E2E

### Comando a ejecutar:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
mkdir -p evidence/fase-v6-e2e
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es --debug 2>&1 | tee evidence/fase-v6-e2e/ejecucion.log
```

### Verificaciones Post-Ejecución

#### 1. Verificar documentos generados en formato V6

Buscar en output:
```bash
ls -la output/v6/  # o el directorio de output que se generó
```

Verificar que:
- `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` tiene frontmatter YAML y estructura V6
- `02_PROPUESTA_COMERCIAL.md` tiene pricing real, no placeholders

#### 2. Verificar coherence score

Buscar en logs:
```
Coherence Score: X.XX
```

Debe ser ≥ 0.80

#### 3. Verificar assets generados

Buscar en delivery:
```
Assets planificados: N
Assets generados: N
```

#### 4. Verificar que no hay errores de texto mixed-language

```
grep -i "使用" evidence/fase-v6-e2e/ejecucion.log
```
Debe retornar vacío.

#### 5. Verificar documentos en output

```bash
find output/ -name "01_DIAGNOSTICO*" -o -name "02_PROPUESTA*" | head -10
```

## Criterios de Completitud

- [ ] Ejecución completa sin errores fatales
- [ ] Coherence score ≥ 0.80
- [ ] Documentos generados en formato V6
- [ ] Datos reales (no placeholders) en los documentos
- [ ] Assets coherentes con lo prometido
- [ ] No hay texto mixed-language
- [ ] Tests de regresión pasan

## Post-Ejecución

### Paso 1: Marcar checklist como completado

### Paso 2: Ejecutar log_phase_completion.py

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase V6-5 \
    --desc "E2E Certification V6 - Documentos comerciales en formato V6 con datos reales para Hotel Vísperas" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/pain_solution_mapper.py,modules/asset_generation/asset_diagnostic_linker.py" \
    --tests "regression" \
    --coherence 0.84 \
    --check-manual-docs
```

### Paso 3: Actualizar CHANGELOG.md

Agregar entrada para v4.10.0 (nueva versión) con los cambios de este proyecto V6.

### Paso 4: Ejecutar validation scripts

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/run_all_validations.py --quick
```

## Archivos de Evidencia

Guardar en `evidence/fase-v6-e2e/`:
- `ejecucion.log` - log completo de la ejecución
- Documentos generados (copiar del output/)
- Screenshots de coherence score

## Nota sobre Versión

Esta fase probablemente incrementa la versión a 4.10.0 dado que es un cambio significativo en el formato de documentos comerciales.

**Release:** FASE-RELEASE-4.10.0
