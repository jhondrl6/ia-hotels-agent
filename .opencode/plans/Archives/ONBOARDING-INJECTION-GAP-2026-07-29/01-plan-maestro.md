# Plan Maestro: ONBOARDING-INJECTION-GAP — Refactorizacion del Pipeline de Inyeccion Onboarding → v4complete

> **Origen**: CONTEXT-ONBOARDING-INJECTION-GAP-2026-07-28.md (validado contra codigo vivo)
> **Version objetivo**: v4.67.0
> **Version actual**: v4.66.0
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Sesiones estimadas**: 10 fases
> **Estimacion total**: ~10-12h
> **Auditoria**: Validado contra codigo vivo 2026-07-29. 8 fallos corregidos (C1-C8).

---

## Resumen Ejecutivo

El pipeline bimodal de iah-cli promete inyectar datos reales de onboarding (Tier A) en v4complete, pero **nunca lo hace** para hoteles cuyo nombre difiere de su dominio. Dos bugs CRITICOS (B1, B2) bloquean la inyeccion, y 6 hallazgos adicionales (N3-N5, §10a-§10c) amplifican la brecha.

**Causa raiz**: No existe un identificador canonico compartido entre `onboard` y `v4complete`. Cada comando resuelve la identidad del hotel con estrategias independientes:
- `onboard` usa `--hotel-name` → slug: `zi-one-luxury`
- `v4complete` deriva nombre de URL → slug: `zione`

El diseno de solucion integrada usa **la URL como clave canonica universal** — presente en ambos comandos, identica en ambos, sin ambiguedad.

---

## Bugs y Hallazgos

| ID | Severidad | Descripcion | FIX-PRIORITY | Fase |
|----|-----------|-------------|-------------|------|
| B1 | **CRITICA** | Slug mismatch onboard↔v4complete | 1 | FASE-0-A + FASE-0-B |
| B2 | **CRITICA** | Ventana frescura 24h hardcodeada | 1 | FASE-0-A |
| N3 | MEDIA | `hotel_url` aceptado pero ignorado en loader | 1 | FASE-0-A |
| N4 | BAJA | `output_dir` hardcodeado en lectura vs configurable en escritura | 1 | FASE-0-B |
| N5 | MEDIA | Sin identity resolver centralizado | 1 | FASE-0-A + FASE-0-B |
| §10a | MEDIA | `user_provided` invisible al tiering | 2 | FASE-1 |
| §10b | BAJA | `audit` deprecado sugerido por onboard | 2 | FASE-1 |
| §10c | MEDIA | `observations.json` no integrado en pipeline | 3 | FASE-2 |

---

## Fases del Plan

| Fase | Titulo | Complejidad | Tareas | Comando largo | R3 | Budget |
|------|--------|-------------|--------|---------------|-----|--------|
| **FASE-0-A** | Reescribir loader + normalize_url + frescura | **ALTA** ⚠️ | 3 | No | ✅ | ~60 ✅ |
| **FASE-0-B** | CAMBIO A+B + template url | MEDIA | 3 | No | ✅ | ~55 ✅ |
| **FASE-1** | Alineacion taxonomica + fix deprecacion | BAJA | 2 | No | ✅ | ~45 ✅ |
| **FASE-2** | Integracion observations.json | MEDIA | 3 | No | ✅ | ~55 ✅ |
| **FASE-3** | Tests de regresion | MEDIA | 3 | No | ✅ | ~58 ✅ |
| **FASE-RELEASE-A** | v4complete Zi One + verificacion 8 hallazgos | MEDIA | 2 | v4complete (1) | ✅ (2+1) | ~50 ✅ |
| **FASE-RELEASE-B** | Version bump v4.67.0 + CHANGELOG + docs | MEDIA | 3 | No | ✅ | ~50 ✅ |
| **FASE-RELEASE-C** | Analisis post-implementacion + cierre | MEDIA | 2 | No | ✅ | ~40 ✅ |

---

## Fase de Mayor Complejidad Tecnica: FASE-0-A

**FASE-0-A (Reescribir loader + normalize_url + frescura)** es la fase de mayor complejidad por:

1. **Reescritura de funcion core**: `_load_latest_onboarding_data()` (~50 lineas) se reemplaza completamente — matching por slug derivado → iteracion por glob + matching de URL normalizada
2. **Nueva funcion auxiliar**: `_normalize_url()` — normalizacion deterministica (protocolo, www, trailing slash, path, query)
3. **Cambio de algoritmo**: De lectura de 1 archivo por slug a iteracion sobre todos los YAMLs + matching por campo `hotel.url`
4. **Riesgo de regresion**: Si el matching falla, v4complete pierde TODA capacidad de cargar datos onboardeados para cualquier hotel

**Mitigaciones**:
- Diseno deterministico: la URL es inmutable entre comandos — no hay ambiguedad
- `_normalize_url()` es una funcion pura con 5 reglas fijas — testeable unitariamente
- Si el matching falla, el comportamiento es identico al actual (usa defaults regionales) — no rompe nada, solo no inyecta

---

## Orden de Ejecucion

```
FASE-0-A (Loader rewrite + normalize + frescura) ── nucleo del matching
  │
  └──▶ FASE-0-B (CAMBIO A+B + template url) ── requiere FASE-0-A (consume nueva firma)
         │
         ├──▶ FASE-1 (Taxonomia + deprecacion) ── independiente de FASE-0 (archivos distintos)
         │
         ├──▶ FASE-2 (observations.json) ── requiere FASE-0-A (modifica funcion reescrita)
         │
         └──▶ FASE-3 (Tests) ── requiere FASE-0-A + 0-B + 1 + 2
                │
                └──▶ FASE-RELEASE-A (v4complete + verificacion) ── requiere TODAS
                       │
                       └──▶ FASE-RELEASE-B (Version bump + docs) ── requiere RELEASE-A
                              │
                              └──▶ FASE-RELEASE-C (Analisis + cierre) ── requiere RELEASE-B
```

---

## Mapa de Cobertura de Hallazgos

| Hallazgo | Resuelto por | Mecanismo | Fase |
|----------|-------------|-----------|------|
| B1 (slug mismatch) | CAMBIO A + C | URL como clave canonica; matching deterministico | FASE-0-A + 0-B |
| B2 (24h freshness) | Fix 3 | Check hardcodeado eliminado; ONBOARDING_FRESHNESS_HOURS opt-in | FASE-0-A |
| N3 (hotel_url ignorado) | CAMBIO C | `hotel_url` se usa como clave primaria de matching | FASE-0-A |
| N4 (output_dir hardcodeado) | CAMBIO B | `output_dir` pasado como parametro desde el caller | FASE-0-B |
| N5 (sin identity resolver) | CAMBIO A + C | URL es el identificador canonico universal | FASE-0-A + 0-B |
| §10a (user_provided invisible) | Fix 4 | Agregar a `verified_sources` en tiering | FASE-1 |
| §10b (audit deprecado sugerido) | Fix 5 | Actualizar mensaje a `v4complete` | FASE-1 |
| §10c (observations.json no integrado) | Fix 6 | Fallback en `_load_latest_onboarding_data` | FASE-2 |

---

## Criterios de Exito (DoD)

| # | Criterio | Fase que lo cubre | Verificable en |
|---|----------|-------------------|----------------|
| S-1 | `_load_latest_onboarding_data()` usa glob + matching por URL normalizada | FASE-0-A | `main.py` |
| S-2 | `_normalize_url()` maneja: www, protocol, trailing slash, path, query | FASE-0-A | `main.py` |
| S-3 | Ventana de frescura eliminada; `ONBOARDING_FRESHNESS_HOURS` como opt-in | FASE-0-A | `main.py` |
| S-4 | `onboard` persiste `hotel.url` via `form._data['hotel']['url']` | FASE-0-B | `main.py` |
| S-5 | `create_onboarding_template()` tiene `'url': None` | FASE-0-B | `data_loader.py` |
| S-6 | `v4complete` pasa `output_dir` configurable al loader | FASE-0-B | `main.py` |
| S-7 | `user_provided` en `verified_sources` de `_determine_evidence_tier()` | FASE-1 | `scenario_calculator.py` |
| S-8 | Mensaje de onboard sugiere `v4complete`, no `audit` | FASE-1 | `main.py` |
| S-9 | `observations.json` tiene campo `website` en los 6 observations | FASE-2 | `observations.json` |
| S-10 | `_load_latest_onboarding_data()` tiene fallback a `observations.json` | FASE-2 | `main.py` |
| S-11 | `_observation_to_onboarding_format()` mapea campos correctamente | FASE-2 | `main.py` |
| S-12 | Tests para `_normalize_url()` con ≥10 casos | FASE-3 | `tests/` |
| S-13 | Tests para URL-based matching con YAMLs mock | FASE-3 | `tests/` |
| S-14 | v4complete Zi One: rooms=34, adr=290K, occupancy=0.784, tier=A | FASE-RELEASE-A | `financial_scenarios.json` + `01_DIAGNOSTICO_*.md` |
| S-15 | 8 hallazgos verificados post-implementacion | FASE-RELEASE-A | `08-analisis-post-implementacion.md` |
| S-16 | VERSION.yaml → 4.67.0, CHANGELOG completo | FASE-RELEASE-B | `VERSION.yaml`, `CHANGELOG.md` |

---

## Archivos del Plan

```
/.opencode/plans/Archives/ONBOARDING-INJECTION-GAP-2026-07-29/
├── 01-plan-maestro.md                   ← Este archivo
├── 02-prompt-fase-0-a.md                ← Loader rewrite + normalize + frescura
├── 03-prompt-fase-0-b.md                ← CAMBIO A+B + template url
├── 04-prompt-fase-1.md                  ← Taxonomia + deprecacion
├── 05-prompt-fase-2.md                  ← observations.json integration (con T0 website)
├── 06-prompt-fase-3.md                  ← Tests de regresion
├── 07-prompt-fase-release-a.md          ← v4complete + verificacion 8 hallazgos
├── 08-prompt-fase-release-b.md          ← Version bump + CHANGELOG + docs
├── 09-prompt-fase-release-c.md          ← Analisis post-implementacion + cierre
├── 10-checklist-implementacion.md       ← Master tracker (renombrado)
├── 11-analisis-post-implementacion.md   ← Template (completar post-ejecucion)
├── 12-documentacion-post-proyecto.md    ← Template (completar en RELEASE-C)
└── dependencias-fases.md                ← Dependency graph + file conflict matrix
```

---

## Lecciones DT4 Incorporadas

| Leccion DT4 | Accion en este plan |
|-------------|-------------------|
| #1: Path validation with `_get_pipeline_path()` | FASE-0-A usa `Path()` consistente para `output_dir` |
| #2: Plan vs live code drift audit | CAMBIO A usa `form._data['hotel']['url']` (verificado contra forms.py) |
| #3: Pre-v4complete verification | FASE-RELEASE-A incluye verificacion PRE-v4complete |
| #4: Commits por fase | Cada fase genera su propio commit |
| #6: Verify files with `ls -la` | Subagente instruido a usar `ls -la` no inferir de logs |

---

## Impacto Financiero del Gap (recordatorio)

Con datos reales de Zi One Luxury (34 hab, $290K ADR, 78.4% ocup, 40% canal directo) el pipeline actual produce cifras Tier B con 10 hab, $420K ADR, 51.2% ocup. La diferencia en fuga mensual es de **$3.4M COP adicionales** (1.9x) y el ROICR pasa de 0.7x a 1.3x.

---

*Plan maestro generado 2026-07-29 a partir de CONTEXT-ONBOARDING-INJECTION-GAP-2026-07-28.md v3.*
*Auditado contra codigo vivo 2026-07-29. 8 correcciones aplicadas (C1-C8).*
*Para reanudar: cargar este plan + `iah-cli-execution-conventions` + `iah-cli-phased-execution`.*
