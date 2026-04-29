# sync_versions.py: Propagación Parcial de Version

**Fecha**: 2026-04-29
**Descubierto en**: FASE-RELEASE-4.37.0 (E3)
**Severidad**: MEDIUM — causa versiones stale silenciosas en 3 archivos
**Estado**: NO CORREGIDO — workaround manual aplicado en RELEASE

---

## Problema

`scripts/sync_versions.py` reporta "All files in sync" (exitoso) pero NO propaga la version a 3 archivos:

| Archivo | Version tras sync | Version esperada |
|---------|-------------------|------------------|
| `docs/CONTRIBUTING.md` | v4.36.0 | v4.37.0 |
| `docs/GUIA_TECNICA.md` | v4.36.0 | v4.37.0 |
| `docs/contributing/REGISTRY.md` | v4.36.0 | v4.37.0 |

Los otros 5 archivos si se actualizan correctamente:
- `README.md` (OK)
- `AGENTS.md` x2 (OK)
- `.cursorrules` (OK)
- `docs/CONTRIBUTING.md` footer (OK) — nota: el header si cambia, el footer no

## Causa Probable

Los patrones de busqueda (regex) en `sync_versions.py` para los 3 archivos fallan al hacer match. Hipotesis principal:

- **Prefijo "v" inconsistente**: Algunos archivos usan `v4.37.0` (con "v"), otros `4.37.0` (sin "v"). Si el patron de busqueda hardcodea `v{version}` pero el archivo tiene `{version}` (sin "v"), no encuentra la linea y reporta "in sync" porque no hay nada que reemplazar — no porque ya este sincronizado.

Archivos afectados usan formato con "v":
- `CONTRIBUTING.md`: `v4.36.0`
- `GUIA_TECNICA.md`: `v4.36.0`
- `REGISTRY.md`: `v4.36.0`

Archivos que funcionan usan formato sin "v":
- `VERSION.yaml`: `4.37.0`
- `AGENTS.md`: `4.37.0`
- `README.md`: `4.37.0`

## Evidencia

```bash
# sync_versions.py output (enganoso):
# OK: docs/CONTRIBUTING.md (contributing_version_header) - in sync
# OK: docs/GUIA_TECNICA.md (guia_tecnica_header) - in sync
# OK: docs/contributing/REGISTRY.md (registry_last_update) - in sync
# Result: All files in sync

# Pero los archivos seguian en v4.36.0:
# grep "v4.36.0" docs/CONTRIBUTING.md → match
# grep "v4.37.0" docs/CONTRIBUTING.md → sin resultados
```

## Workaround Aplicado

Patch manual directo en los 3 archivos durante FASE-RELEASE:

```python
# CONTRIBUTING.md: "v4.36.0" → "v4.37.0"
# GUIA_TECNICA.md: "v4.36.0" → "v4.37.0" + fecha
# REGISTRY.md: "v4.36.0" → "v4.37.0"
```

## Recomendacion

1. **Investigar `sync_versions.py`**: Inspeccionar los patrones regex para `contributing_version_header`, `guia_tecnica_header`, y `registry_last_update`. Verificar si el patron incluye "v" como literal cuando el archivo lo tiene.

2. **Agregar validacion post-sync**: Despues de "actualizar", verificar que el archivo efectivamente contiene la nueva version (no solo que el regex no encontro nada). Ej:
   ```python
   # Despues del reemplazo:
   content = open(filepath).read()
   if new_version not in content:
       print(f"WARNING: {filepath} no contiene {new_version} tras sync")
   ```

3. **Test**: Agregar test unitario que cambie VERSION.yaml a una version de prueba, ejecute sync, y verifique los 8 archivos.

## Archivo Afectado

- `scripts/sync_versions.py` — patrones de busqueda y logica de reporte
