# Nota sobre sync_versions.py — PROPUESTA-COMERCIAL (2026-05-26)

## Problema

El script `scripts/sync_versions.py` no acepta los argumentos `--bump` ni `--release-name` que aparecían en el plan FASE-RELEASE.

```
$ ./venv/Scripts/python.exe scripts/sync_versions.py --bump minor --release-name "PROPUESTA-COMERCIAL"
sync_versions.py: error: unrecognized arguments: --bump minor --release-name PROPUESTA-COMERCIAL
```

## Solución aplicada

1. **Edit manual de `VERSION.yaml`** — actualizar `version`, `codename`, `release_date` directamente
2. **Ejecutar `sync_versions.py` sin argumentos** — el script detecta config-driven y propaga a todos los archivos

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
# Editar manualmente VERSION.yaml
./venv/Scripts/python.exe scripts/sync_versions.py
```

## Archivos sincronizados por sync_versions.py

- `AGENTS.md` (agents_version_comment + agents_header_banner)
- `README.md` (readme_version_header)
- `docs/CONTRIBUTING.md` (contributing_version_header)
- `docs/GUIA_TECNICA.md` (guia_tecnica_header)
- `docs/contributing/REGISTRY.md` (registry_last_update)

## Lecciones

- `sync_versions.py` es **config-driven** — sync rules defined in `sync_config.yaml`, no CLI flags
- El plan original copiaba argumentos de otros contextos de fase release que no aplican a este script
- Para próximos releases: editar `VERSION.yaml` manualmente → ejecutar `sync_versions.py`