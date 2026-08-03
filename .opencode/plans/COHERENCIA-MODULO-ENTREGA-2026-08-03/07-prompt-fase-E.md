# FASE-E: Verificación E2E — ÚNICA ejecución v4complete (Zi One Luxury, zione.co)

**ID**: COHERENCIA-FASE-E
**Objetivo**: Ejecutar UNA sola vez `v4complete` con datos reales de onboarding y verificar que los 21 hallazgos (D1-D12, N1-N9) fueron superados; capturar evidencia y alimentar el análisis post-implementación.
**Dependencias**: FASE-A ✅, FASE-B ✅, FASE-C-A ✅, FASE-C-B ✅, FASE-D ✅.
**Duración estimada**: 1 sesión (~42 iteraciones de 60; el comando corre 5-10 min en subagente/background).
**Skill**: `phased_project_executor` v2.13.0 §Protocolo-Subagente-para-v4complete + §Protocolo-Evidencia-Proactiva.

## Contexto

Todas las fases de implementación están completas. Esta fase es la ÚNICA ejecución de `v4complete` en todo el plan (decisión explícita del usuario). Hotel: **Zi One Luxury** (https://zione.co/, Pereira, Eje Cafetero) con onboarding real Tier A: 34 habitaciones, 800 reservas/mes, valor_reserva 290.000 COP, canal directo 40%.

Baseline de comparación (NO re-ejecutar): run 2026-08-01 17:05:39 — `output/v4_complete/` y checklist por hallazgo en contexto §6.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A / B / C-A / C-B / D | ✅ Completadas |
| FASE-E | ▶️ EN CURSO (esta sesión) |

## Modo de ejecución (delegate_task)

**DELEGADO para el comando largo.** Regla executor §Regla-de-Decisión-para-v4complete: spawn de subagente/background con timeout ≥ 900s y notificación al completar; el agente principal usa sus iteraciones en T0, verificación y evidencia. NUNCA ejecutar v4complete sin notify/background (warning del executor).

> ⚠️ Adaptación de entorno: el venv es Windows (`./venv/Scripts/python.exe`).
> El comando debe lanzarse desde el workspace Windows con ese intérprete, en
> modo background/notify, redirigiendo salida a log: 
> `./venv/Scripts/python.exe main.py v4complete ... > evidence/FASE-E/v4complete_run.log 2>&1`

## Tareas

### T0 — Pre-requisito onboarding (antes de lanzar)
- Agregar `url: https://zione.co` a la sección `hotel` de `output/clientes/zi-one-luxury_onboarding.yaml` (el matching de `_load_latest_onboarding_data` en main.py es por URL normalizada; sin este campo el YAML se salta y cae al fallback de `data/hotel_observations/observations.json`, que SÍ contiene a Zi One Luxury con los mismos datos 34/800/290000/40 — verificado 2026-08-03. Agregar url garantiza que se use el YAML canónico Tier A como fuente).
- Verificar que el resto del YAML permanece intacto (34 hab, 800 res/mes, 290000, 40%).
- Verificar `.env` con API keys (PageSpeed puede fallar — esperado, es parte del test D6).

### T1 — Ejecución v4complete (subagente/background, ~5-10 min)
Comando exacto:
```bash
./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --output output/v4_verify_4.70.0
```
Contexto del subagente (protocolo executor):
- URL: https://zione.co/ · Output esperado: diagnóstico, propuesta, assets, coherence ≥ 0.80.
- timeout=900, notify_on_complete=true, toolsets=["terminal"].

### T2 — Protocolo de Evidencia Proactiva (OBLIGATORIO, inmediatamente termina T1)
```bash
mkdir -p evidence/FASE-E
cp output/v4_verify_4.70.0/01_DIAGNOSTICO_*.md evidence/FASE-E/
cp output/v4_verify_4.70.0/02_PROPUESTA_*.md evidence/FASE-E/
cp -r output/v4_verify_4.70.0/zione/v4_audit/ evidence/FASE-E/v4_audit/
```
Esto es OBLIGATORIO antes de cualquier verificación (executor §Protocolo-Evidencia-Proactiva).

### T3 — Verificación de los 21 hallazgos contra baseline (checklist contexto §6)

| Hallazgo | Check sobre `output/v4_verify_4.70.0` | ✅/❌ |
|----------|----------------------------------------|-----|
| D1 | Doc dice "Open Graph Tags Incompletos (8 tags detectados)", no "Sin Meta Tags"; breakdown AEO coherente | |
| D2 | pain_ledger.json == brechas del doc (mismo N); conteo dinámico en template | |
| D3 | `opportunity_scores[].estimated_monthly_cop` == costos del doc | |
| D4 | Doc muestra escenarios reales (19.6M/7.19M/−6.8M con probs 70/20/10) o rango renombrado; CG-SCENARIO-ORDER en gate_report | |
| D5 | gate_report: covered > 0 o mensaje honesto; nunca "Coverage completo" con covered=0 | |
| D6 | Doc refleja "API key inválida"/estado real de performance (o texto de sitio nuevo SOLO si status OK) | |
| D7 | Sin "203 reseñas" | |
| D8 | Atribución GEO = "algoritmo propio de IA Hoteles Agent sobre datos de Google Places" | |
| D9 | Target fotos 40 | |
| D10 | Redes sin duplicados; TikTok/YouTube si aplican | |
| D11 | commercial_gates_report.json fresco (timestamp == run) | |
| D12 | financial_scenarios.json: occupancy "onboarding" | |
| N1 | Diagnóstico y propuesta con la MISMA recuperación proyectada 6m | |
| N2 | gate_report: hard_contradictions/doc_audit_consistency reporta o está limpio con fundamento | |
| N3 | diff doc 2026-08-01 vs doc FASE-E > 3 líneas | |
| N4 | ZIP contiene SOLO artefactos v4_audit del run actual | |
| N5-N8 | Sin "acima", sin "Por que importa", truncamiento por palabra, confianza bien atribuida | |
| N9 | execution_trace coherente con el texto del doc sobre PageSpeed | |

Además: coherence ≥ 0.8, gate_status global honesto, evidence_tier B+ (no revertir a A).

### T4 — Análisis post-implementación (llenar `10-analisis-post-implementacion.md`)
- Matriz de verificación de hallazgos (Expected vs Real vs Status) como en el plan DELIVERY-ZIP.
- **Lecciones aprendidas**: mínimo 3 lecciones con formato "qué pasó / por qué / qué lo previene", evaluando pertinencia para futuras releases (ver contexto §9 como ejemplo).
- Qué fixes fueron superados totalmente, parcialmente o requieren seguimiento (p. ej. gate N2 en modo WARNING pendiente de upgrade a BLOCKING).

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Regresión rápida pre-run | `./venv/Scripts/python.exe -m pytest tests/regression -q` | 26/26 |
| Validaciones | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | 4/4 |

## Post-Ejecución (OBLIGATORIO)

1. Marcar FASE-E ✅ en `dependencias-fases.md`, `09-checklist-implementacion.md`, `README.md`.
2. Completar `10-analisis-post-implementacion.md` (matriz + lecciones).
3. Actualizar `11-documentacion-post-proyecto.md` sección D (hallazgos cerrados 21/21, coherence final).
4. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-E \
    --desc "E2E v4complete Zi One Luxury: 21/21 hallazgos verificados" \
    --archivos-mod "output/clientes/zi-one-luxury_onboarding.yaml" \
    --tests "0" --coherence <score final> --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] Onboarding inyectado (YAML con url + log del run lo confirma)
- [ ] v4complete completó sin crash; coherence ≥ 0.8
- [ ] Evidencia copiada a `evidence/FASE-E/` ANTES de verificar
- [ ] Checklist 21 hallazgos completado (registrar fallos como seguimiento, no bloquear el registro)
- [ ] `10-analisis-post-implementacion.md` con matriz + ≥3 lecciones aprendidas
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- Máximo 60 iteraciones (R2). El comando largo corre en subagente/background, no consume iteraciones del principal.
- **UNA sola ejecución de v4complete.** Si el run falla por infraestructura (red/API), se permite UN retry; si falla por código, marcar ⏳ INCOMPLETA y retomar en sesión fresca (no improvisar fixes en esta sesión).
- NO modificar código fuente en esta fase salvo el YAML de onboarding (T0).
- Suite completa de tests NO se ejecuta aquí (timeout conocido); se delega a FASE-RELEASE por módulo si es necesario.
