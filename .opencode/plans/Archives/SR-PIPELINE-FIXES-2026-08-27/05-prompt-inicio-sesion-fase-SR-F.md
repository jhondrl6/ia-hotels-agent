# FASE-SR-F — Investigación de Varianza del Plan de Assets + PageSpeed (OPS)

**ID**: FASE-SR-F
**Objetivo**: Explicar (y corregir si es determinista) por qué el plan de assets varió entre corridas separadas por horas con la misma URL efectiva (7→5 brechas; `low_ia_readiness` y `ai_crawler_blocked` ausentes en C de forma determinista — H5), y verificar el estado de la API key de PageSpeed (H6.1, OPS — rec #6).
**Dependencias**: FASE-SR-E ✅ (mismo archivo `pain_solution_mapper.py` — SR-E PRIMERO).
**Complejidad**: Media · **Delegación**: ❌ DIRECTO (investigación forense con juicio sobre corridas reales; outcome condicional pre-decidido D-PF6)
**Duración estimada**: 45-60 min · **Presupuesto**: ~20 iteraciones trabajo + ~15 verificación/docs (R2: máx. 60)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones (checkpoint + evidencia si se agota). R3: 4 tareas + 0 comandos largos. **NO ejecutar v4complete/v4audit** (la investigación usa los ledgers en disco de las corridas A y C).
- Python: `./venv/Scripts/python.exe`.

## Contexto

**Lectura previa obligatoria**: CONTEXT-SALENTOREAL §6 (H5 con hipótesis revisada), §9 #5 y #6 + plan maestro §8 (D-PF6).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SR-A…SR-E | ✅ Completadas |

### Base Técnica Disponible (H5 verificado en disco)
- Comparación A (18:03, `output/v4_complete/`) vs C (18:30, `output/test_salentoreal_v4c/`): brechas 7→5, assets 7→5, `llms_txt` generado→present_in_production, coherencia 0.8438→0.8644, **escenarios financieros idénticos** (determinista).
- ⚠️ Hipótesis del contexto original ("desaparece si robots = 1.00") DESCARTADA: `ai_crawler_blocked` NO aparece en NINGUNO de los dos ledgers (grep = 0 en A y C). Hipótesis vigente: **`pain_solution_mapper` (o cache de audit/SitePresence) aplica un filtro distinto entre corridas que excluye `low_ia_readiness` y `ai_crawler_blocked` de forma determinista**, no por score de robots.
- Artefactos para comparar: `pain_ledger.json` / `pain_ledger_resolved.json` / `asset_generation_report` de ambas corridas (en disco, NO regenerar).
- PageSpeed: `[3/5] Status: ERROR — API key not valid` mientras la MISMA key funciona para Places. Hipótesis OPS: keys distintas por servicio en `config/settings.yaml` (o key de PageSpeed no configurada/rotada).

## Tareas

### T1: Investigación forense de la varianza (solo lectura)
**Archivos**: ledgers de corridas A y C (en disco), `modules/commercial_documents/pain_solution_mapper.py` (filtros sobre pain_ids), cache de audit/SitePresence (`data/cache/` si aplica).
**Criterios**:
- [ ] Confirmar con diff de ledgers: exactamente qué pain_ids faltan en C (`low_ia_readiness`, `ai_crawler_blocked`) y en qué etapa del pipeline se filtran
- [ ] Identificar la condición del filtro (cache TTL de SitePresence? filtro por presencia? umbral de scores? orden de ingesta?)
- [ ] Reproducir la exclusión de forma determinista (test o traza documentada)

### T2: Fix mínimo O seguimiento (D-PF6 — outcome pre-decidido)
**Criterios**:
- [ ] SI la causa es un filtro determinista erróneo → aplicar fix mínimo + test que lo fije (determinismo del plan de assets)
- [ ] SI requiere rediseño mayor (p. ej., cache TTL con semántica de vigencia) → NO expandir la fase: documentar hipótesis, evidencia y propuesta en Seguimientos de `10-analisis` y registrar en `06-checklist` como criterio satisfecho-vía-seguimiento
- [ ] En ambos casos, el informe de varianza queda escrito (AC8)

### T3: PageSpeed OPS (rec #6 — sin tocar secretos)
**Criterios**:
- [ ] Leer `config/settings.yaml` (y `.env.template`) para determinar si existe una key específica de PageSpeed distinta de `GOOGLE_API_KEY`
- [ ] Documentar el diagnóstico y la instrucción de rotación para el usuario en `10-analisis` §Seguimientos (NUNCA imprimir/escribir el valor de la key)
- [ ] Verificar que la ausencia de PageSpeed degrada evidencia sin bloquear (comportamiento observado) — documentar como diseño correcto

### T4: Docs + registro
**Criterios**:
- [ ] Informe de varianza completo en `10-analisis` (hipótesis, evidencia, veredicto)
- [ ] Seguimientos actualizados (varianza → resuelta o propuesta; PageSpeed → instrucción OPS al usuario)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| determinismo del filtro (si hubo fix) | tests de `pain_solution_mapper` | Mismo input → mismo plan de assets (con y sin cache) |
| (sin fix) no aplica | — | Informe + seguimiento documentados |

**Comandos** (solo si hubo fix; procesos aislados, salida a archivo):
```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents -k "mapper" -v > temp/fase_sr_f_tests.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. `dependencias-fases.md` §2 → ✅. 2. `README.md` → ✅. 3. `06-checklist` → SR-F. 4. `09-documentacion` → B/D/E + Notas. 5. `10-analisis` → Resumen + informe de varianza + D-PF6 outcome + seguimiento PageSpeed. 6. `evidence/FASE-SR-F/` → diffs de ledgers A vs C + informe. 7. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-SR-F --desc "Varianza del plan de assets investigada (7->5) + PageSpeed OPS; fix minimo o seguimiento documentado" --archivos-mod "modules/commercial_documents/pain_solution_mapper.py" --tests "<N reales>" --check-manual-docs
```
(Ajustar `--archivos-mod`/`--tests` si no hubo fix: usar `--force-skip-docs --skip-reason "investigacion-documental"` solo si el script lo exige.)
8. `./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer`

## Criterios de Completitud (CHECKLIST)

- [ ] Informe de varianza completo con veredicto (fix o seguimiento)
- [ ] Si hubo fix: tests pasan + regresiones 0
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Instrucción PageSpeed documentada sin exponer secretos
- [ ] Docs post-fase completos (1-8)
- [ ] Evidencia en `evidence/FASE-SR-F/`

## Restricciones

- Máx. 60 iteraciones; **NO ejecutar v4complete/v4audit/scraping** (solo artefactos en disco).
- NO tocar secretos/keys (`.env`, valores en settings.yaml) — solo lectura de estructura de config.
- NO expandir el fix de varianza más allá del alcance mínimo (D-PF6): rediseños van a Seguimientos.
- NO delegar a subagente; NO usar `--release` en log_phase_completion.
- AC10: capa financiera intacta.
