# FASE-RELEASE-B: Version Bump v4.67.0 + CHANGELOG + Docs Cascade

> **REGLA**: Una fase = una sesion. No ejecutar multiples fases aqui.
> **Tipo de ejecucion**: DIRECTA (modifica VERSION.yaml, CHANGELOG.md, AGENTS.md, GUIA_TECNICA.md)
> **Complejidad**: MEDIA
> **R3**: 3 tareas, 0 comandos largos ✅ dentro del limite
> **Plan**: `ONBOARDING-INJECTION-GAP-2026-07-29/01-plan-maestro.md`
> **PRECONDICION**: FASE-RELEASE-A completada (v4complete exitoso, 8 hallazgos verificados)

## Contexto previo

**FASE-RELEASE-A**: v4complete Zi One Luxury ejecutado y verificado. rooms=34, adr=290K, tier=A confirmados en output.

Falta formalizar la release: bump de version, CHANGELOG, y propagacion a docs del proyecto.

## Objetivo de esta fase

Version bump a v4.67.0 con CHANGELOG completo y propagacion a AGENTS.md y GUIA_TECNICA.md.

### Tareas

- [ ] **T1**: Version bump: VERSION.yaml → 4.67.0
- [ ] **T2**: CHANGELOG.md: entrada [4.67.0] con todos los cambios
- [ ] **T3**: AGENTS.md + GUIA_TECNICA.md actualizados

---

### T1 — VERSION.yaml

**Archivo**: `VERSION.yaml`

```yaml
version: "4.67.0"
codename: "Onboarding Injection Fix — URL-based canonical matching + observations.json fallback"
release_date: "2026-07-29"
```

### T2 — CHANGELOG.md

Agregar antes de la entrada [4.66.0]:

```markdown
## [4.67.0] — 2026-07-29

### Cambios Implementados
- **Onboarding Injection Pipeline**: Matching canonico por URL normalizada en `_load_latest_onboarding_data()`. Eliminada dependencia de slug derivado de nombre.
- **`_normalize_url()`**: Nueva funcion auxiliar para matching deterministico de URLs (ignora protocolo, www, trailing slash, path, query).
- **CAMBIO A**: `run_onboard_mode()` ahora persiste `hotel.url` en el YAML via `form._data['hotel']['url']`.
- **CAMBIO B**: `run_v4_complete_mode()` ahora pasa `output_dir` configurable (`args.output`) al loader.
- **CAMBIO C**: `_load_latest_onboarding_data()` reescrita: iteracion por glob, matching por URL normalizada, parametro `output_dir`.
- **Fix 3**: Ventana de frescura hardcodeada eliminada. `ONBOARDING_FRESHNESS_HOURS` env var como opt-in.
- **Fix 4**: `"user_provided"` agregado a `verified_sources` en `_determine_evidence_tier()`.
- **Fix 5**: Mensaje de `onboard` actualizado: sugiere `v4complete` en vez de `audit` (deprecado).
- **Fix 6**: `_load_latest_onboarding_data()` ahora tiene fallback a `observations.json` via `_observation_to_onboarding_format()`.

### Archivos Modificados
- `main.py`: `_load_latest_onboarding_data()` reescrita, `_normalize_url()`, `_observation_to_onboarding_format()`, `run_onboard_mode()` CAMBIO A, `run_v4_complete_mode()` CAMBIO B
- `modules/onboarding/data_loader.py`: `create_onboarding_template()` — agregado `'url': None`
- `modules/financial_engine/scenario_calculator.py`: `_determine_evidence_tier()` — `user_provided` en verified_sources
- `data/hotel_observations/observations.json`: Agregado `website` a 6 observaciones

### Tests
- `tests/test_onboarding_injection.py`: ~15 tests nuevos (`_normalize_url`, `_load_latest_onboarding_data`, `_observation_to_onboarding_format`)

### Bugs Resueltos
- B1: Slug mismatch onboard↔v4complete (CRITICO)
- B2: Ventana frescura 24h (CRITICO)
- N3: hotel_url ignorado en loader
- N4: output_dir hardcodeado en lectura
- N5: Sin identity resolver centralizado
- §10a: user_provided invisible al tiering
- §10b: audit deprecado sugerido por onboard
- §10c: observations.json no integrado
```

### T3 — AGENTS.md + GUIA_TECNICA.md

**AGENTS.md**:
- Actualizar header de version: `<!-- agents_version: 4.67.0 -->`
- Agregar one-liner: "v4.67.0 — Onboarding injection: URL-based canonical matching + observations.json fallback"

**GUIA_TECNICA.md**:
- Agregar seccion sobre el nuevo mecanismo de matching por URL:
  - `_normalize_url()` como funcion pura de normalizacion
  - `_load_latest_onboarding_data()` con iteracion por glob + matching URL
  - Fallback a `observations.json` cuando no hay YAML

### Restricciones

- ❌ NO ejecutar v4complete — ya se hizo en FASE-RELEASE-A
- ✅ Verificar consistencia CHANGELOG vs VERSION despues de escribir
- ✅ Si existe `scripts/sync_versions.py`, ejecutarlo para propagar version a otros docs

### Criterios de completitud

- [ ] VERSION.yaml → 4.67.0 con release_date 2026-07-29
- [ ] CHANGELOG.md → entrada [4.67.0] completa
- [ ] AGENTS.md header actualizado a 4.67.0
- [ ] GUIA_TECNICA.md menciona el nuevo mecanismo de matching
- [ ] `grep "4.67.0" VERSION.yaml CHANGELOG.md AGENTS.md` → 3 matches
- [ ] Pre-commit hooks limpios (si aplica)

### Proxima sesion

**FASE-RELEASE-C**: Analisis post-implementacion + documentacion post-proyecto + cierre del plan. 2 tareas. MEDIA complejidad.

Carga: `08-prompt-fase-release-c.md`
