---
description: Protocolo de auto-mantenimiento para la arquitectura de skills.
---

# Skill: Maintenance Autopilot (Auto-Gestión)

> [!NOTE]
> **Trigger**: "Audita el sistema de skills", "verifica consistencia", "mantenimiento rutinario".

## Pre-requisitos (Contexto)
- [ ] Catálogo de skills (`.agents/workflows/`).
- [ ] Documentación técnica (`GUIA_TECNICA.md`).

## Fronteras (Scope)
- **Hará**: Chequeo de enlaces rotos entre Markdowns, Validación de Triggers duplicados, Sincronización de CHANGELOG.md.
- **NO Hará**: No modifica lógica de negocio en archivos `.py`.

## Pasos de Ejecución

### 1. Auditoría de Skills (Scan)
Escanear `.agents/workflows/` buscando Markdowns sin Trigger o con YAML mal formado.

*Validación*: Reporte de skills inconsistentes generado.

### 2. Sincronización de Documentos
Alinear la `v3.3.3` en todos los archivos de documentación maestros.

*Validación*: `CHANGELOG.md` y `README.md` reflejan el estado actual.

### 3. Poda de Archivos Temporales (Pruning)
Eliminar logs antiguos y archivos de caché obsoletos en `data/cache/`.

*Validación*: Directorio de trabajo limpio y ligero.

## Criterios de Éxito
- [ ] Repositorio 100% coherente.
- [ ] Sin triggers huérfanos.
- [ ] Documentación al día con el código.

## Plan de Recuperación (Fallback)
- Si un archivo crítico se borra, usar el historial de Git para restaurar.
- Si hay inconsistencia masiva, proponer al usuario una sesión de refactor dirigida.
