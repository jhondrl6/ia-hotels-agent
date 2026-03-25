# Documentacion: Reglas y Checklist

> Este documento detalla las reglas de documentacion segun CONTRIBUTING.md §5 y §8.

---

## 5. Checklist de Documentacion Obligatoria (Nuevo Modulo)

Cuando agregues un nuevo modulo Python o realices una migracion tecnica:

1. **Crear codigo** en el modulo correspondiente (`modules/`)
2. **Crear tests** en `tests/` con cobertura minima 80%
3. **Actualizar documentacion** segun checklist abajo
4. **Ejecutar validaciones pre-commit** (ver `validation.md`)

### Documentos a Actualizar

| Documento | Cuando actualizar | Contenido |
|-----------|-------------------|-----------|
| `CHANGELOG.md` | **Siempre** | Entrada con archivos nuevos/modificados |
| `GUIA_TECNICA.md` | Si afecta arquitectura, stack o flujos | Seccion en "Notas de Cambios" |
| `INDICE_DOCUMENTACION.md` | Si el modulo es publico/utilizado | Fila en tabla de modulos |
| `ROADMAP.md` | Si es hito relevante para monetizacion | Fila en tabla de hitos |
| `VERSION.yaml` | Si es release completo | Incrementar version |

### Checklist de Capability Contract (ver `capabilities.md` §13)

| Item | Descripcion |
|------|-------------|
| Capacidad definida | Nueva capability en matriz-capacidades.md |
| Punto de invocacion | Identificado en flujo principal |
| Output serializable | Verificado en to_dict/export/report |
| No es huerfana | Se ejecuta, no solo existe en codigo |

### Formato de Entrada en CHANGELOG

```markdown
## v{VERSION} - {Titulo} (Fecha)

### Objetivo
{Descripcion breve del cambio}

### Cambios Implementados
- `ruta/archivo.py` - Descripcion del cambio

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| `ruta/nuevo.py` | Descripcion |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `ruta/existente.py` | Descripcion del cambio |

### Tests
- X tests en `test_xxx.py`
```

---

## 8. Clasificacion de Archivos de Documentacion

### Sistema de Sincronizacion (Config-Driven)

A partir de v4.5.6, el sistema de sincronizacion es **config-driven**:
- **Configuracion**: `scripts/sync_config.yaml` - declara qué sincronizar dónde
- **Script**: `scripts/sync_versions.py` - ejecuta las reglas del config
- **Extensible**: agregar sync = agregar 4 líneas al YAML

**Flujo:**
1. Editar `VERSION.yaml` con nueva versión
2. Ejecutar `python scripts/sync_versions.py`
3. El script sincroniza automáticamente según `sync_config.yaml`

**Comandos:**
```bash
python scripts/sync_versions.py          # Sync all files
python scripts/sync_versions.py --check   # Check if sync needed
python scripts/sync_versions.py --list    # List all sync rules
python scripts/sync_versions.py --validate # Validate config
```

### Archivos Sincronizados Automaticamente

| Archivo | Qué sincroniza |
|---------|---------------|
| `README.md` | Version, fecha, status banner, codename |
| `AGENTS.md` | Version, codename, fecha, status table |
| `.cursorrules` | Version, fecha |
| `INDICE_DOCUMENTACION.md` | Version, fecha |

### Archivos que se Actualizan Manualmente

| Archivo | Cuando actualizar |
|---------|------------------|
| `CHANGELOG.md` | Nueva release (registro historico de cambios) |
| `GUIA_TECNICA.md` | Cambios arquitectonicos o tecnicos |
| `ROADMAP.md` | Cambios en estrategia de monetizacion |
| `CONTRIBUTING.md` | Nuevos procedimientos de mantenimiento |
| `.agents/workflows/README.md` | Agregar o eliminar skills |
| `docs/PRECIOS_PAQUETES.md` | Cambios en precios o paquetes |

### Casos en que NO se Utiliza CONTRIBUTING

| Situacion | Accion correcta |
|-----------|-----------------|
| Agregar entrada al CHANGELOG | Editar manualmente, NO usar procedimientos de Contributing |
| Actualizar ROADMAP estrategico | Editar manualmente |
| Agregar nueva seccion a GUIA_TECNICA | Editar manualmente |
| Cambiar precios en PRECIOS_PAQUETES.md | Editar manualmente |
| Agregar nuevo template en templates/ | Editar manualmente |
| Actualizar archivos de benchmarks | Editar manualmente |

---

## 9. Guia de Uso Rapido

### Antes de Cualquier Cambio

Consulta esta tabla para determinar el procedimiento correcto:

| Si quieres... | Entonces... |
|--------------|-------------|
| Cambiar version del proyecto | Editar VERSION.yaml -> ejecutar `python scripts/sync_versions.py` |
| Agregar una nueva skill | Seguir procedimiento en `procedures.md` §2 |
| Eliminar una skill | Seguir procedimiento en `procedures.md` §3 |
| Modificar Decision Engine | Seguir procedimiento en `procedures.md` §4 |
| Agregar nuevo modulo | Seguir procedimiento en `procedures.md` §5 |
| Hacer commit | Ejecutar checklist en `validation.md` §6 |
| Actualizar CHANGELOG | Editar manualmente (NO usar procedimientos de Contributing) |
| Actualizar ROADMAP | Editar manualmente |
| Actualizar GUIA_TECNICA | Editar manualmente |

### Flujo de Trabajo Tipico

```
1. Determinar el tipo de cambio -> consultar tabla arriba
2. Si requiere procedimiento -> seguir los pasos de la seccion correspondiente
3. Si es manual -> editar directamente el archivo
4. Antes de commit -> ejecutar checklist en validation.md
5. Verificar con git diff
```

### Resumen de Scripts

| Script | Cuando ejecutarlo |
|--------|-------------------|
| `run_all_validations.py --quick` | Antes de cada commit (recomendado) |
| `run_all_validations.py` | Validacion completa antes de release |
| `pre-commit run --all-files` | Antes de cada commit (si no esta instalado) |
| `sync_versions.py` | Despues de editar VERSION.yaml |
| `generate_domain_primer.py` | Despues de modificar financial_engine/ |
| `generate_system_status.py` | Despues de agregar/eliminar skill |
| `validate.py --plan` | Despues de modificar Plan Maestro |
| `validate.py --security` | Antes de push (verificar secrets) |
| `validate_structure.py` | Validar estructura del proyecto |
| `config_checker.py` | Verificar configuracion |
| `extract_psi_metrics.py` | Extraer metricas PageSpeed |
| `.agents/workflows/v4_regression_guardian.py --quick` | Despues de cambios en modulos v4 |
