# FASE-RELEASE: v4.36.0 AmaziliaHotel Patch — Release Final

**ID**: FASE-RELEASE-AMAZILIAHOTEL
**Objetivo**: Cerrar release v4.36.0 "PATCH Forense AmaziliaHotel" — verificar CHANGELOG.md refleja todos los fixes y ejecutar validacion final
**Dependencias**: FASE-1-A ✅, FASE-1-B ✅, FASE-1-C ✅ (todas 2026-04-28)
**Duracion estimada**: 1 sesion (~10 min)
**Skill**: `phased_project_executor.md` v2.9.0

---

## Estado del Release

| Criterio | Estado |
|----------|--------|
| FASE-1-A (fixes) | ✅ Completada 2026-04-28 |
| FASE-1-B (T4 + v4complete) | ✅ Completada 2026-04-28 |
| FASE-1-C (docs cascade) | ✅ Completada 2026-04-28 |
| "Salud Tecnica GEO" en diagnostico | ✅ Confirmado FASE-1-B |
| 4/4 validaciones | ✅ Pasadas 2026-04-28 |
| REGISTRY.md actualizado | ✅ Entrada FASE-1-AMAZILIA-CORRECCION |
| CHANGELOG.md v4.36.0 | ⚠️ Verificar que refleje fixes A+B |

> [!NOTE]
> version_consistency_checker.py reportaba CHANGELOG=4.35.1 vs VERSION.yaml=4.36.0 — es bug del checker (leo primera linea [4.35.1] en lugar de buscar la version mas alta). CHANGELOG.md YA tiene entrada [4.36.0] linea 41. Verificar que el contenido refleje los fixes.

---

## Resumen de Cambios (FASE-1-AMAZILIA-CORRECCION)

Hallazgos VALIDATE-v2 corregidos:

| Finding | Descripcion | Archivo |
|---------|-------------|---------|
| M3 | can_use unificado (preflight_status != "BLOCKED") | asset_metadata.py L151-173 |
| H1 | local_content_page handler en orchestrator | v4_asset_orchestrator.py |
| N1 | Header dual removido, un solo header | v4_diagnostic_generator.py L1307 |
| M4 | Forward slashes en paths (no backslash) | conditional_generator.py |
| T4 | GEO timing async/await corregido | v4_diagnostic_generator.py |
| slug bug | output_name con {slug} literal | conditional_generator.py L621 |

---

## Tareas

### Tarea 1: Verificar CHANGELOG.md v4.36.0

Leer CHANGELOG.md desde linea 41 y verificar que la entrada [4.36.0] incluya:
- Los fixes de FASE-1-A (M3, H1, N1, M4, slug bug)
- El fix de T4 de FASE-1-B (GEO timing)

**Si esta incompleto**: Editar y agregar seccion con los hallazgos corregidos.
**Si esta completo**: Solo marcar como verificado.

### Tarea 2: run_all_validations.py --quick

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

**Criterio**: 4/4 validaciones pasadas.

---

## Scope R3 — Verificacion

Esta sesion tiene:
- [x] Verificar CHANGELOG.md (1 tarea)
- [x] run_all_validations (1 tarea)

**Total**: 2 tareas + 0 comandos largos = dentro del limite R3 ✅

---

## Cierre de Sesion (OBLIGATORIO)

Antes de cerrar, SIEMPRE:

1. **Verificar** `run_all_validations.py --quick` pasa 4/4
2. **Si CHANGELOG.md fue editado**: Commit con mensaje `[RELEASE] v4.36.0 - PATCH Forense AmaziliaHotel (VALIDATE-v2 fixes)`
3. **Guardar evidencia** en `evidence/fase-1-amazilia-correccion/04_FASE-RELEASE_EVIDENCE.md`

---

## Criterios para Release Cerrado

Cuando todas las tareas esten ✅:
- CHANGELOG.md entrada v4.36.0 refleja todos los hallazgos corregidos
- 4/4 validaciones pasadas
- Evidence guardada
- Opcional: git tag `v4.36.0`

---

## Como Iniciar la Nueva Sesion

```
Ejecutar FASE-RELEASE:
  archivo: C:\Users\Jhond\Github\iah-cli\.opencode\plans\06-prompt-inicio-sesion-FASE-RELEASE-amazilia.md
```

**Dependencias**: Todas las sub-fases de FASE-1-AMAZILIA-CORRECCION deben estar ✅.
