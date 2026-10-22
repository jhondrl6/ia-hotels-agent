# Documentación Post-Proyecto — CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

> **Acumulador canónico de métricas por fase** (lo consume FASE-RELEASE). Un conteo o resultado se registra **una vez** aquí (o en el informe/crudo que lo produce) y los demás documentos lo **referencian**; no se re-transcribe.

## Sección A: Módulos Nuevos

| Fase | Módulo | Función |
|------|--------|---------|
| FASE-A | — | Sin módulos nuevos: cierre documental, cero código |

## Sección B: Funcionalidades Nuevas

| Fase | Funcionalidad | Descripción |
|------|---------------|-------------|
| FASE-A | — | Sin funcionalidades nuevas: solo evidencia versionada y docs de cierre |

## Sección D: Métricas Acumulativas

| Fase | Tests nuevos | Delta R2.3 (pre → post) | `--quick` | Notas |
|------|--------------|-------------------------|-----------|-------|
| FASE-A | 0 (sin código) | — | 13/13 (venv canónico) | Crudos: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/` (verde en `03b-quick-venv-canonico.txt`; el 9/13 del `.venv-wsl` 3.11 queda en `03-quick.txt` como contaminación de intérprete) |
| FASE-B | 0 (medición) | — | (lo imprime la corrida) | Crudo: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/` |
| FASE-C | (según mecanismo) | (par pre/post en evidence) | (lo imprime la corrida) | Crudo: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-C/` |
| FASE-RELEASE-4.81.1 | 0 | — | (lo imprime la corrida) | Cifras de cobertura de la ronda medidas con el comando canónico |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Fase | Cambio |
|---------|------|--------|
| `dependencias-fases.md`, README del plan, `06-checklist-implementacion.md`, `09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md` §2 | FASE-A | Post-Ejecución 1-6 del cierre (2026-10-21) |
| `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/` | FASE-A | Acta del cierre + 12 crudos de verificación de la sesión |
| `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/15-…` a `26-…` | FASE-A | 12 crudos de la tanda persistidos en `77dea21` |
| `docs/contributing/REGISTRY.md`, `.agent/SYSTEM_STATUS.md` | FASE-A | Registro de fase (`log_phase_completion.py --tests 0`) |
| `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` | FASE-A | Par regenerado como derivado de la post-ejecución (lo exige el `[6/8]` del hook) |
