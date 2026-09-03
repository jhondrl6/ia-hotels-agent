# FASE-SR-D — Canonicalización de `target_id` (URL Canónica como Identidad de Memoria)

**ID**: FASE-SR-D
**Objetivo**: Que la identidad de memoria (`target_id`) se derive de la URL **canónica** (vía el helper EXISTENTE `_normalize_url()`, main.py:3542) y no de la URL raw, eliminando la fragmentación de memoria por parámetros UTM/campaña (H2/N3, L-SR2, L16: el gap está en el caller). INCLUYE `generate_hotel_id` de `modules/orchestration_v4/onboarding_controller.py:339-350` (añadido en revisión causa-raíz 2026-08-28): sanitiza la URL cruda con `replace('?','_')` etc. → produce el hotel_id contaminado del log "Phase 1 iniciada".
**Dependencias**: FASE-SR-C ✅ (evitar conflicto sobre `main.py`).
**Complejidad**: Media · **Delegación**: ❌ DIRECTO (código+tests con venv)
**Duración estimada**: 45-60 min · **Presupuesto**: ~20 iteraciones trabajo + ~15 verificación/docs (R2: máx. 60)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones (checkpoint + evidencia si se agota). R3: 4 tareas + 0 comandos largos.
- Python: `./venv/Scripts/python.exe`.

## Contexto

**Lectura previa obligatoria**: CONTEXT-SALENTOREAL §3 (H2), §1.3 (tabla UTM), §9.5.2 N3, §8.2 L-SR2 + plan maestro §8 (guarda del nombre del helper).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SR-A…SR-C | ✅ Completadas |

### Base Técnica Disponible (verificado 2 veces contra código vivo)
- `main.py:3542` — `def _normalize_url(url: str) -> str`: ignora protocolo, www, path y **query string**. ES EL HELPER CORRECTO.
- ⚠️ `_normalize_url_for_matching` NO EXISTE en el repo (grep = 0 en main.py y modules/) — cualquier referencia a él es un error del contexto original ya corregido. NO buscarlo, NO crearlo.
- Call sites que graban `target_id=args.url` crudo: `main.py` L3248/3394/3460 (vía `memory.append_log` / `save_analysis_reference`); `find_latest_v4_analysis` en `agent_harness/memory.py:665` busca por ese ID.
- Evidencia: corrida A (URL limpia) y corrida C (URL con UTM) = mismo hotel, **2 identidades distintas** → `find_latest_analysis`/`_find_recent_v4_analysis` no reutilizan → re-ejecución de audit con costo de API (GBP re-consultado, PageSpeed caído).
- `main.py:742` (`target_id = args.url or ...`) — otros comandos (onboard/execute/validate-guarantee) también construyen IDs desde URL cruda.
- ⚠️ **GAP añadido en revisión 2026-08-28**: `modules/orchestration_v4/onboarding_controller.py:339-350` — `generate_hotel_id()` sanitiza la URL **cruda** (`replace` de `?`, `&`, `=` por `_`) → `hotel_hotelsalentoreal.com__utm_source_...`. Este es el origen del hotel_id contaminado del log Phase 1; NO se corrige solo con `main.py`. Debe normalizar la URL (quitar query string) antes de construir el id.
- Detección de región: `_detect_region_from_url` hace substring sobre la URL — verificar que sigue funcionando con la URL normalizada (el dominio `hotelsalentoreal.com` conserva 'salento'; el path se pierde — confirmar que ninguna detección dependa del path).

## Tareas

### T1: Investigar TODOS los call sites de target_id
**Archivos**: `main.py` (L742, L890, L3248, L3394, L3460), `modules/orchestration_v4/onboarding_controller.py` (`generate_hotel_id`, L339-350), `agent_harness/memory.py` (solo lectura: `find_latest_v4_analysis`, `append_log`, vigencia < 20 días).
**Criterios**:
- [ ] Inventario completo de call sites que construyen target_id/hotel_id desde URL (v4complete + onboard + execute + validate-guarantee + `generate_hotel_id`)
- [ ] Confirmar semántica exacta de `_normalize_url()` (tests/lectura) y de `_detect_region_from_url` con URL normalizada

### T2: Implementar canonicalización (D-PF4)
**Criterios**:
- [ ] La URL se pasa por `_normalize_url()` como **primer paso** de `run_v4_complete_mode` (y de onboard/execute/validate-guarantee)
- [ ] `target_id` se construye desde la URL **normalizada**; la URL **original** solo se usa para scraping/audit
- [ ] `generate_hotel_id` (onboarding_controller) normaliza la URL antes de sanitizar (sin query string → ids estables con/sin UTM)
- [ ] El log de Phase 1 muestra el target_id canónico (`hotel_hotelsalentoreal.com` — sin UTM)
- [ ] Sin cambios en `agent_harness/memory.py` (la reutilización funciona sola cuando los IDs coinciden)

### T3: Tests anti-fragmentación
**Criterios**:
- [ ] Test: `https://www.hotelsalentoreal.com/` ≡ misma URL con UTM completo (corrida B/C) ≡ con `?partner=5792` ≡ mismo `target_id` (incl. `generate_hotel_id`)
- [ ] Test: variaciones protocolo/www producen el mismo target_id
- [ ] Test: `_detect_region_from_url` con URL normalizada sigue retornando `eje_cafetero` para Salento Real
- [ ] Smoke L-SR1: la rama modificada se ejecuta al menos una vez en test (o test estático cubre el símbolo)

### T4: Greps + docs
**Criterios**:
- [ ] Grep: 0 call sites restantes que graben `target_id=args.url` (crudo) en comandos con `--url`
- [ ] Grep: 0 `replace(` sobre URL cruda dentro de `generate_hotel_id` sin normalización previa
- [ ] Grep: `grep "_normalize_url_for_matching"` = 0 en todo el repo (el nombre erróneo no debe reaparecer)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| anti-fragmentación | `tests/test_target_id_canonicalization.py` (nuevo) o existente de harness | UTM ≡ limpia ≡ mismo id |
| región | ídem | eje_cafetero detectado con URL normalizada |

**Comandos** (procesos aislados, salida a archivo):
```bash
./venv/Scripts/python.exe -m pytest tests/test_target_id_canonicalization.py -v > temp/fase_sr_d_tests.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. `dependencias-fases.md` §2 → ✅. 2. `README.md` → ✅. 3. `06-checklist` → SR-D. 4. `09-documentacion` → B/D/E + Notas. 5. `10-analisis` → Resumen + L-PF (si aplica) + D-PF4 confirmada. 6. `evidence/FASE-SR-D/` → diff + tests. 7. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-SR-D --desc "Canonicalizacion de target_id via _normalize_url() en caller (v4complete + onboard + execute + validate-guarantee) + generate_hotel_id de onboarding_controller" --archivos-mod "main.py,modules/orchestration_v4/onboarding_controller.py" --tests "<N reales>" --check-manual-docs
```
8. `./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer`

## Criterios de Completitud (CHECKLIST)

- [ ] Tests anti-fragmentación pasan; regresiones = 0 (suites de harness tocadas)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Greps de residuos = 0 (incl. nombre erróneo del helper)
- [ ] Docs post-fase completos (1-8)
- [ ] Evidencia en `evidence/FASE-SR-D/`

## Restricciones

- Máx. 60 iteraciones; NO ejecutar v4complete/v4audit.
- NO modificar `agent_harness/memory.py` (solo lectura — el fix vive en el caller, L16).
- NO modificar la lógica de scraping/audit (usa la URL original).
- NO crear un normalizador nuevo ni el símbolo `_normalize_url_for_matching`.
- NO delegar a subagente; NO usar `--release` en log_phase_completion.
- AC10 (financiera intacta): no tocar nada de financial_engine.
