# FASE-1-C-AMAZILIA-CORRECCION: Docs Cascade

**ID**: FASE-1-C-AMAZILIA-CORRECCION
**Sub-fase de**: FASE-1-AMAZILIA-CORRECCION (plan padre)
**Objetivo**: Ejecutar la cascada completa de documentacion post-fase
**Dependencias**: FASE-1-B completada (T4 fix + v4complete verificado)
**Duracion estimada**: 1 sesion (~20 min)
**Skill**: `phased_project_executor.md` v2.9.0

---

## Estado del Plan Padre

| Sub-fase | Estado |
|----------|--------|
| FASE-1-A (fixes) | ✅ Completada |
| FASE-1-B (T4 + v4complete) | ⏳ Debe estar ✅ antes de iniciar |
| **FASE-1-C (esta)** | ⏳ Pendiente |

> [!CAUTION]
> **NO iniciar FASE-1-C hasta que FASE-1-B muestre ✅ en todos sus criterios.**
> Si FASE-1-B aun esta incompleta, la docs cascade se ejecutara sobre un
> output que no representa el estado final de la fase.

---

## Pre-requisitos Verificados

Antes de iniciar, confirmar:

- [ ] FASE-1-B muestra `✅ Completada` en el plan padre
- [ ] `geo_flow_result.json` aparece en ia_metrics_table del diagnostico final
- [ ] Output v4complete existe en `output/v4_complete/`
- [ ] Evidence de FASE-1-B en `evidence/fase-1-amazilia-correccion/`

---

## Tareas

### Tarea 1: log_phase_completion.py

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-1-AMAZILIA-CORRECCION \
    --desc "Correccion hallazgos VALIDATE-v2 + T4 fix + v4complete Amazilia Hotel" \
    --archivos-mod "modules/asset_generation/conditional_generator.py,modules/asset_generation/asset_metadata.py,modules/orchestration/v4_diagnostic_generator.py,modules/orchestration/v4_asset_orchestrator.py,main.py" \
    --check-manual-docs
```

**Verificar**: No debe haber `[GAP]` en DOCUMENTATION AUDIT.

### Tarea 2: sync_versions.py

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/sync_versions.py
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

**Verificar**: Todos los 6 archivos sincronizados con VERSION.yaml.

### Tarea 3: Actualizar 06-checklist-implementacion.md

- Marcar FASE-1-AMAZILIA-CORRECCION como ✅
- Actualizar fecha de finalizacion
- Listar hallazgos corregidos: M3, H1, N1, M4, T4, slug bug

### Tarea 4: Actualizar 09-documentacion-post-proyecto.md

- **Seccion D (Metricas)**: coherence 0.88, 13/13 assets, 5 hallazgos corregidos
- **Seccion E (Archivos afiliados)**: todos los archivos modificados listados

### Tarea 5: Actualizar dependencias-fases.md

- Marcar FASE-1-AMAZILIA-CORRECCION como completada
- Incluir resumen de hallazgos corregidos y archivos modificados

### Tarea 6: run_all_validations.py

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

**Criterio**: 4/4 checks pasan.

---

## Scope R3 — Verificacion

Esta sesion tiene:
- [x] log_phase_completion (1 tarea)
- [x] sync_versions (1 tarea)
- [x] Actualizar 06 y 09 docs (1 tarea)
- [x] Actualizar dependencias-fases (1 tarea)
- [x] run_all_validations (1 tarea)

**Total**: 5 tareas + 0 comandos largos = dentro del limite R3 ✅

---

## Archivos a Modificar en Docs Cascade

| Archivo | Cambio |
|---------|--------|
| `docs/contributing/REGISTRY.md` | Nueva entrada FASE-1-AMAZILIA-CORRECCION |
| `06-checklist-implementacion.md` | Marcar FASE-1 como ✅ |
| `09-documentacion-post-proyecto.md` | Secciones D y E actualizadas |
| `dependencias-fases.md` | Marcar FASE-1 como completada |
| `CHANGELOG.md` | Nueva entrada si hay version bump |
| `docs/GUIA_TECNICA.md` | Nota tecnica de los fixes (T4, slug) |

---

## Cierre de Sesion (OBLIGATORIO — sin excepciones)

Antes de cerrar, SIEMPRE:

1. **Verificar** `run_all_validations.py --quick` pasa 4/4
2. **Actualizar plan padre** `05-prompt-inicio-sesion-fase-1-amazilia-correccion.md`:
   - Marcar FASE-1-C como ✅
   - Si todas las sub-fases (A, B, C) estan ✅ → la fase completa esta completada
3. **Guardar evidencia final** en `evidence/fase-1-amazilia-correccion/`

---

## Como Iniciar la Nueva Sesion

```
Ejecutar FASE-1-C-AMAZILIA-CORRECCION:
  archivo: C:\Users\Jhond\Github\iah-cli\.opencode\plans\05-prompt-inicio-sesion-fase-1-C-amazilia-correccion.md
```

**Dependencias**:
- FASE-1-B debe estar completada (✅) — confirmar en el plan padre
- Evidence de FASE-1-B en `evidence/fase-1-amazilia-correccion/`

**Checkpoint si se retom a**: leer el plan padre para confirmar estado de FASE-1-B antes de continuar.
