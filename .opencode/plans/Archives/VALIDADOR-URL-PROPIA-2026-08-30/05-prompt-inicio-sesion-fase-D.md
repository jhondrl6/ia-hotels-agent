# FASE-D — E2E: única corrida v4complete Hotel Salento Real (no-regresión tradicional)

**ID**: VALIDADOR-URL-PROPIA / FASE-D
**Objetivo**: Demostrar que el guard NO afecta la ejecución tradicional de `v4complete` sobre un sitio propio: UNA única corrida E2E sobre Hotel Salento Real (`https://www.hotelsalentoreal.com/`), con evidencia proactiva y comparación contra el baseline `output/salentoreal_final_v4c_h2/` (FASE-SR-H2: smoke 7/7, coherence 0.88).
**Dependencias**: FASE-A ✅, FASE-B ✅ (FASE-C ✅ recomendada)
**Duración estimada**: 1.5-2 horas (~41-50 iteraciones; el comando tarda 5-10 min de pared)
**Skill**: `phased_project_executor.md` v2.17.0

## Modo de ejecución (regla del executor)

**MIXTO**: el comando largo `v4complete` se delega a subagente (timeout 900, `notify_on_complete`, "ejecutar y reportar, no interpretar"); el agente principal prepara el run y verifica/compara la evidencia (patrón validado L30 RC1-RC2: delegación + evidencia-first ahorra presupuesto).

> **NUNCA ejecutar v4complete sin notify_on_complete o subagente** — si el parent se agota antes, la verificación no ocurre y la fase queda incompleta.

## Contexto

El guard es ortogonal al flujo tradicional (AC3/AC8): sitios propios pasan sin cambio. La prueba definitiva es el E2E real, porque "tests unitarios que mockean el camino completo no detectan sitios de integración omitidos; solo el E2E lo hace" (L29). Baseline de referencia: `output/salentoreal_final_v4c_h2/` + `evidence/FASE-SR-H2/smoke_result_h2.json` (smoke 7/7, coherence 0.88, READY_FOR_PUBLICATION).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A / FASE-B | ✅ Completadas |
| FASE-C | ✅ Completada (probes P1-P11 en `evidence/FASE-VUP-C/`) |
| FASE-D | ⏳ En progreso (esta sesión) |

### Lecciones capitalizadas aplicables
| Lección | Aplicación concreta |
|---------|---------------------|
| L13 REINTERPRETADA (auditoría F5): el baseline H2 corrió CON DEFAULTS — verificado en `output/salentoreal_final_v4c_h2/v4_complete/v4_complete_report.json` ("uses default/legacy values — Tier B evidence", `direct_channel_percentage: "default"`), y no existe YAML de onboarding de Salento Real en el repo (verificado 2026-08-30: `output/clientes/` solo tiene zi-one-luxury) | La equivalencia AC8 exige correr EN LAS MISMAS condiciones que el baseline: SIN poblar `clientes/`, con defaults. NO fabricar datos de onboarding (cambiaría tier de evidencia/pricing/gates y rompería la comparación). El run DEBE mostrar "Using defaults" igual que H2 |
| L-SR1: ramas no ejercitadas acumulan defectos latentes | ANTES del run: grep de símbolos no definidos en las ramas nuevas del guard (p. ej. `logger` no existe en main.py — usar `print(f"[INFO] ...")`) |
| Protocolo de Evidencia Proactiva (§executor) | INMEDIATAMENTE terminado el run, copiar artefactos críticos a `evidence/FASE-VUP-D/` ANTES de cualquier análisis |
| L-PF12: reproducibilidad del plan de assets como criterio de cierre | Comparar plan pains→assets contra baseline H2 (determinismo) |
| L30: evidencia incluye report JSON y ZIP, no solo docs | Copiar también `v4_complete_report.json` y el ZIP de delivery |

## Tareas

### T1: Preparación del run (parent, directo)
**Acciones**:
- Verificar `git status` limpio (A y B commiteados).
- Crear `output/FASE-D_salentoreal_post_guard/` **SIN `clientes/`** (auditoría F5: el baseline H2 usó defaults; se espera "Using defaults" en el log — es la condición de equivalencia, no un fallo). Confirmar que no existe YAML de Salento Real (ya verificado en la auditoría; re-confirmar con `ls output/clientes/`).
- Grep de símbolos sospechosos en las ramas nuevas (T2 de A/B): `logger.`, imports faltantes → fix mínimo `print(f"[INFO]...")` si aparece (es fix de preparación, no de feature).
- Verificar que el baseline existe: `output/salentoreal_final_v4c_h2/v4_complete/v4_complete_report.json` y `evidence/FASE-SR-H2/smoke_result_h2.json`. Si no existe, registrarlo: la comparación usará solo criterios absolutos.

**Criterios**: [ ] Directorio creado SIN clientes/, [ ] grep limpio o fixes mínimos aplicados.

### T2: Ejecución delegada del comando largo (subagente)
**Prompt de delegación (exacto)**:
```
Ejecutar en la raíz del repo y reportar:
./venv/Scripts/python.exe main.py v4complete --url "https://www.hotelsalentoreal.com/" --output output/FASE-D_salentoreal_post_guard
timeout=900. Ejecutar y reportar exit code + últimas 50 líneas de salida. NO interpretar, NO corregir, NO reintentar sin instrucción.
```
**Criterios**: [ ] Exit code 0 o estado del pipeline claramente reportado.

### T3: Evidencia + verificación de no-regresión (parent, directo)
**Acciones**:
1. **Protocolo de Evidencia Proactiva (PRIMERO)** — rutas explícitas según la estructura real verificada en H2 (`v4_complete/` anidado; el glob `**` NO funciona en Git Bash sin globstar — auditoría F9):
```bash
mkdir -p evidence/FASE-VUP-D
D=output/FASE-D_salentoreal_post_guard/v4_complete
cp "$D"/01_DIAGNOSTICO_*.md "$D"/02_PROPUESTA_*.md "$D"/v4_complete_report.json evidence/FASE-VUP-D/
cp "$D"/hotelsalentoreal/v4_audit/*.json evidence/FASE-VUP-D/ 2>/dev/null
cp "$D"/deliveries/*.zip "$D"/deliveries/*.pdf evidence/FASE-VUP-D/ 2>/dev/null
```
2. Verificar con Python UTF-8 (parseo JSON, no regex de consola):
   - `target_id` == `hotelsalentoreal.com` (identidad correcta).
   - coherence ≥ 0.8 y estado de publicación (baseline H2: 0.88 READY_FOR_PUBLICATION).
   - Gates: mismo perfil que baseline (13 gates; blocking sin regresión).
   - Plan de assets: pains→assets equivalentes al baseline H2 (determinismo L-PF12).
   - El log muestra "Using defaults" (equivalencia con H2 — auditoría F5) y NO muestra al guard interfiriendo (0 rechazos durante el run).
3. Tabla antes/después (baseline H2 vs este run) en `evidence/FASE-VUP-D/comparacion.md`.

**Criterios de aceptación**:
- [ ] Run completado y evidencia copiada ANTES del análisis.
- [ ] coherence ≥ 0.8; gates sin regresión blocking vs baseline.
- [ ] target_id correcto; plan de assets equivalente.
- [ ] Si el run falla: clasificar infraestructura vs código (L14); solo infraestructura habilita retry; código → ⏳ INCOMPLETA.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md` → FASE-D ✅ con fecha.
2. `README.md` del plan + `06-checklist-implementacion.md`.
3. `09-documentacion-post-proyecto.md` → sección D (coherence, gates, duración del run).
4. `10-analisis-post-implementacion.md` → fila Resumen de Ejecución (delegate_task: sí, comando largo), Métricas, mínimo 3 lecciones (incluir: evaluación del protocolo evidencia-first, estado del onboarding L13, diff vs baseline).
5. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-D --desc "E2E v4complete Hotel Salento Real post-guard: no-regresion tradicional verificada vs baseline H2" \
    --coherence 0.XX --check-manual-docs
```
6. Commit (evidencia incluida).

## Criterios de Completitud (CHECKLIST)

- [ ] Corrida única E2E ejecutada (no repetir salvo fallo de infraestructura)
- [ ] Evidencia proactiva en `evidence/FASE-VUP-D/` (docs + JSON + ZIP)
- [ ] AC3/AC8 verificados contra baseline o criterios absolutos
- [ ] Post-ejecución completa

## Restricciones

- **Máximo 60 iteraciones** (R2); el comando cuenta 1 tool call pero consume pared — planificar presupuesto ANTES de lanzarlo.
- **UNA sola corrida** — es la única ejecución v4complete del plan (FASE-VERIFY NO ejecuta v4complete).
- NO modificar código del pipeline durante la verificación; si un check falla, documentar en Seguimientos y planificar recuperación.
- NO usar `--release` en `log_phase_completion.py`.
