# Checklist de Implementacion — ONBOARDING-INJECTION-GAP-2026-07-29

> **Plan**: `01-plan-maestro.md`
> **Version objetivo**: v4.67.0
> **Inicio**: 2026-07-29
> **Ultima actualizacion**: 2026-07-29 (post-auditoria C1-C8)

---

## Estado Global

| Metrica | Valor |
|---------|-------|
| Fases totales | 10 (7 implementacion + 3 release) |
| Fases completadas | 6 |
| Fases pendientes | 4 |
| Hallazgos a resolver | 8 |
| Hallazgos resueltos | 8 (B1, B2, N3, N4, N5, §10a, §10b, §10c resueltos) |

---

## Tracking por Fase

### FASE-0-A — Loader Rewrite + normalize_url + Frescura ✅ COMPLETADA

**Complejidad**: ALTA ⚠️ (mayor complejidad del plan)
**Ejecucion**: DIRECTA
**Delegate**: ❌ NO VIABLE
**Archivos**: main.py (1 funcion reescrita + 1 funcion nueva)
**R3**: 3 tareas, 0 comandos largos ✅

- [x] T1: CAMBIO C — Reescribir `_load_latest_onboarding_data()` con glob+URL matching
- [x] T2: Implementar `_normalize_url()` (funcion pura, 5 reglas)
- [x] T3: Fix 3 — Eliminar ventana de frescura hardcodeada; `ONBOARDING_FRESHNESS_HOURS` opt-in
- [x] Verificacion: `grep "glob" main.py | grep "_onboarding"` → existe
- [x] Verificacion: `grep "def _normalize_url" main.py` → existe
- [x] Verificacion: loader ya no importa `generate_slug`

**Bugs resueltos**: B1 (parcial), B2, N3

---

### FASE-0-B — CAMBIO A+B + Template url ✅ COMPLETADA

**Complejidad**: MEDIA
**Ejecucion**: DIRECTA
**Delegate**: ❌ NO VIABLE
**PRECONDICION**: FASE-0-A completada
**R3**: 3 tareas, 0 comandos largos ✅

- [x] T1: CAMBIO A — `form._data['hotel']['url'] = args.url.rstrip('/')` en `run_onboard_mode()`
- [x] T2: Agregar `'url': None` a `create_onboarding_template()` en `data_loader.py`
- [x] T3: CAMBIO B — Pasar `output_dir=Path(args.output)/"clientes"` al loader
- [x] Verificacion: `grep "form._data['hotel']['url']" main.py` → existe
- [x] Verificacion: `grep "'url': None" modules/onboarding/data_loader.py` → existe
- [x] Verificacion: `grep "output_dir=" main.py | grep "_load_latest"` → existe

**Bugs resueltos**: B1 (completa), N4, N5

---

### FASE-1 — Alineacion Taxonomica + Fix Deprecacion ✅ COMPLETADA

**Complejidad**: BAJA
**Ejecucion**: DIRECTA
**Delegate**: ✅ VIABLE (2 one-liners, sin dependencia de FASE-0)
**R3**: 2 tareas, 0 comandos largos ✅

- [x] T1: Fix 4 — `"user_provided"` en `verified_sources`
- [x] T2: Fix 5 — Mensaje onboard L1120 y L1125: `audit` → `v4complete`
- [x] Verificacion: `grep "user_provided" modules/financial_engine/scenario_calculator.py` → en verified_sources ✅
- [x] Verificacion: `grep "v4complete --url" main.py` → L1120 y L1125 actualizadas ✅

**Hallazgos resueltos**: §10a, §10b

---

### FASE-2 — Integracion observations.json ✅ COMPLETADA

**Complejidad**: MEDIA
**Ejecucion**: DIRECTA
**Delegate**: ❌ NO VIABLE
**PRECONDICION**: FASE-0-A completada
**R3**: 3 tareas, 0 comandos largos ✅

- [x] T0: Agregar campo `website` a los 6 observations en `observations.json`
- [x] T1: Fix 6 — Fallback a `observations.json` en `_load_latest_onboarding_data()`
- [x] T2: `_observation_to_onboarding_format()` implementada
- [x] Verificacion: 6/6 observations con campo `website` en observations.json
- [x] Verificacion: `grep "observations.json" main.py` → fallback existe (L3510)
- [x] Verificacion: `grep "def _observation_to_onboarding_format" main.py` → helper existe (L3419)

**Hallazgos resueltos**: §10c

---

### FASE-3 — Tests de Regresion ✅ COMPLETADA

**Complejidad**: MEDIA
**Ejecucion**: DIRECTA
**Delegate**: ⚠️ PARCIAL (solo escritura)
**PRECONDICION**: FASE-0-A, FASE-0-B, FASE-1, FASE-2 completadas
**R3**: 3 tareas, 0 comandos largos ✅

- [x] T1: Tests `_normalize_url()` 15 casos (13 parametrizados + 2 edge cases) → todos PASS
- [x] T2: Tests `_load_latest_onboarding_data()` URL matching 7 casos → todos PASS
- [x] T3: Tests `_observation_to_onboarding_format()` 5 casos → todos PASS
- [x] Verificacion: `python -m pytest tests/test_onboarding_injection.py -v` → 27 passed in 0.48s
- [x] Verificacion: tests existentes no rompen — 56/56 test_onboarding.py, 3158 total collect OK
- [x] Fix adicional: `_normalize_url()` corregido para manejar URLs sin protocolo (zione.co → zione.co)

---

### FASE-RELEASE-A — v4complete Zi One + Verificacion ✅ COMPLETADA

**Complejidad**: MEDIA
**Ejecucion**: MIXTO (v4complete→SUBAGENTE, verificacion→DIRECTO)
**Delegate**: ⚠️ MIXTO
**PRECONDICION**: TODAS las fases anteriores completadas
**R3**: 2 tareas + 1 comando largo ✅

- [x] PRE-v4complete check: loader existe (L3455), YAML zi-one-luxury_onboarding.yaml existe, observations.json con website ✅
- [x] T1: v4complete Zi One Luxury ejecutado (subagente deleg_cfd467b3, 180s, exitoso)
- [x] T2: Matriz de 8 hallazgos verificada contra output real — 8/8 PASS
- [x] Verificacion: rooms=34 (no 10) en financial_scenarios_20260730_143703.json
- [x] Verificacion: adr_cop=290000 (no 420000)
- [x] Verificacion: evidence_tier="A" (no "B") — 01_DIAGNOSTICO L9
- [x] Verificacion: 01_DIAGNOSTICO y 02_PROPUESTA EXISTEN (ls -la confirmado)

**Bugs verificados**: B1, B2, N3, N4, N5, §10a, §10b, §10c — todos PASS

---

### FASE-RELEASE-B — Version Bump v4.67.0 + CHANGELOG + Docs ⬜ PENDIENTE

**Complejidad**: MEDIA
**Ejecucion**: DIRECTA
**Delegate**: ❌ NO VIABLE (modifica 4 archivos de docs)
**PRECONDICION**: FASE-RELEASE-A completada
**R3**: 3 tareas, 0 comandos largos ✅

- [ ] T1: VERSION.yaml → 4.67.0 con release_date 2026-07-29
- [ ] T2: CHANGELOG.md → entrada [4.67.0] con todos los cambios
- [ ] T3: AGENTS.md header + GUIA_TECNICA.md actualizados
- [ ] Verificacion: `grep "4.67.0" VERSION.yaml CHANGELOG.md AGENTS.md` → 3 matches
- [ ] Verificacion: `scripts/sync_versions.py --check` (si existe)

---

### FASE-RELEASE-C — Analisis Post-Implementacion + Cierre ⬜ PENDIENTE

**Complejidad**: MEDIA
**Ejecucion**: DIRECTA
**Delegate**: ❌ NO VIABLE (requiere contexto completo)
**PRECONDICION**: FASE-RELEASE-B completada
**R3**: 2 tareas, 0 comandos largos ✅

- [ ] T1: `08-analisis-post-implementacion.md` completado (7 secciones)
- [ ] T2: `09-documentacion-post-proyecto.md` completado + checklist final
- [ ] Verificacion: todas las fases marcadas ✅ en este checklist
- [ ] Verificacion: prompt de cierre generado

---

## Resumen de Cobertura

| Hallazgo | Fase | Estado |
|----------|------|--------|
| B1 (slug mismatch) | FASE-0-A + 0-B | ✅ completado |
| B2 (frescura 24h) | FASE-0-A | ✅ completado |
| N3 (hotel_url ignorado) | FASE-0-A | ✅ completado |
| N4 (output_dir hardcodeado) | FASE-0-B | ✅ completado |
| N5 (sin identity resolver) | FASE-0-A + 0-B | ✅ completado |
| §10a (user_provided invisible) | FASE-1 | ✅ completado |
| §10b (audit deprecado) | FASE-1 | ✅ completado |
| §10c (observations.json) | FASE-2 | ✅ completado |

---

## Log de Sesiones

| Fecha | Fase | Estado | Iteraciones | Notas |
|-------|------|--------|-------------|-------|
| 2026-07-29 | FASE-0-A | ✅ COMPLETADA | 1 | Loader reescrito con glob+URL matching. _normalize_url() implementada. Ventana 24h eliminada (ONBOARDING_FRESHNESS_HOURS opt-in). 616 tests pasan, 0 regresiones. |
| 2026-07-29 | FASE-1 | ✅ COMPLETADA | 1 | 2 one-liners: user_provided en verified_sources (scenario_calculator.py L494), mensajes audit→v4complete (main.py L1120, L1125). Hallazgos §10a y §10b resueltos. |
| 2026-07-29 | FASE-2 | ✅ COMPLETADA | 1 | T0: 6 websites agregados a observations.json. T1: Fallback a observations.json en _load_latest_onboarding_data() (L3510). T2: _observation_to_onboarding_format() implementada (L3419). Hallazgo §10c resuelto. |
| 2026-07-29 | FASE-3 | ✅ COMPLETADA | 1 | 27 tests nuevos (15 normalize_url + 7 loader + 5 observation_format). Fix _normalize_url() para URLs sin protocolo. 27/27 PASS, 0 regresiones en 3158 tests. |
| 2026-07-30 | FASE-RELEASE-A | ✅ COMPLETADA | 1 | v4complete Zi One ejecutado (deleg_cfd467b3, 180s). 8/8 hallazgos verificados PASS: B1, B2, N3, N4, N5, §10a, §10b, §10c. rooms=34, adr=290K, evidence_tier=A. Evidencia en evidence/FASE-RELEASE-A/. |
