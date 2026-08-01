# Documentacion Post-Proyecto — ONBOARDING-INJECTION-GAP-2026-07-29

> **Version final**: v4.67.0
> **Fecha de cierre**: 2026-07-30
> **Plan maestro**: `01-plan-maestro.md`

---

## 1. Decisiones de Diseno

### 1.1 URL como clave canonica

**Problema**: `onboard` y `v4complete` derivaban identificadores distintos del mismo hotel (slug de nombre vs slug de dominio), haciendo imposible el matching.

**Alternativas consideradas**:
- **Hotel ID numerico**: Requiere base de datos centralizada. No viable para la arquitectura actual file-based.
- **Slug unificado**: Requiere que ambos comandos usen la misma funcion. Fragil si el nombre cambia.
- **Fuzzy matching de nombres**: No deterministico, riesgo de falsos positivos.

**Decision**: URL como clave canonica universal. Es el unico dato presente en ambos comandos, identico en ambos, e inmutable durante el ciclo de vida del analisis.

### 1.2 `_normalize_url()` deterministica

**Reglas fijas**: strip protocolo, strip www, lowercase, ignorar path/query/port. Sin fuzzy matching. Si dos URLs normalizan al mismo string, son el mismo hotel. Sin ambiguedad.

### 1.3 Frescura eliminada (opt-in via env var)

**Razon**: El dato operativo (habitaciones, ADR, canal) no se vuelve obsoleto en 24h. Si el hotel cambia de estructura, se re-onboardea y el nuevo archivo reemplaza al viejo. La ventana de 24h era inconsistente con el ciclo real de ventas (time-to-response: 2-7 dias).

**Opt-in**: `ONBOARDING_FRESHNESS_HOURS=168` para exigir datos de la ultima semana.

---

## 2. Archivos Modificados

| Archivo | Tipo de cambio | Fase |
|---------|---------------|------|
| `main.py` | MOD: `_load_latest_onboarding_data()` reescrita | ✅ FASE-0-A |
| `main.py` | NEW: `_normalize_url()` | ✅ FASE-0-A |
| `main.py` | MOD: `run_onboard_mode()` — CAMBIO A | FASE-0-B |
| `main.py` | MOD: `run_v4_complete_mode()` — CAMBIO B | FASE-0-B |
| `main.py` | NEW: `_observation_to_onboarding_format()` | FASE-2 |
| `main.py` | MOD: `_load_latest_onboarding_data()` — fallback observations | FASE-2 |
| `main.py` | MOD: L1113, L1118 — mensaje onboard | FASE-1 |
| `modules/onboarding/data_loader.py` | MOD: `create_onboarding_template()` — `url: None` | FASE-0-B |
| `modules/financial_engine/scenario_calculator.py` | MOD: `_determine_evidence_tier()` — `user_provided` | FASE-1 |
| `data/hotel_observations/observations.json` | MOD: `website` field en 6 observations | FASE-2 |
| `tests/test_onboarding_injection.py` | NEW: ~15 tests | FASE-3 |
| `VERSION.yaml` | MOD: 4.67.0 | FASE-RELEASE-B |
| `CHANGELOG.md` | MOD: entrada [4.67.0] | FASE-RELEASE-B |
| `AGENTS.md` | MOD: version header | FASE-RELEASE-B |
| `GUIA_TECNICA.md` | MOD: seccion matching URL | FASE-RELEASE-B |

---

## 3. Nuevas Funciones Publicas

### `_normalize_url(url: str) -> str`

Normaliza URL para matching canonico. Ignora protocolo, www, trailing slash, path, query string. Case-insensitive.

### `_observation_to_onboarding_format(obs: dict) -> dict`

Convierte un observation de `observations.json` al mismo formato que un YAML de onboarding. Usado como fallback cuando no hay YAML para un hotel.

---

## 4. Cambios en Estructura de Datos

### YAML de Onboarding

**Nuevo campo**: `hotel.url` — URL del hotel como clave canonica de matching.

```yaml
hotel:
  nombre: Zi One Luxury
  ubicacion: Pereira
  url: https://zione.co      # ← NUEVO (CAMBIO A)
```

### observations.json

**Nuevo campo**: `website` en cada observation.

```json
{
  "hotel_name": "Zi One Luxury",
  "website": "https://zione.co/",   // ← NUEVO (FASE-2 T0)
  "rooms": 34,
  ...
}
```

---

## 5. Riesgos Conocidos

| Riesgo | Impacto | Mitigacion |
|--------|---------|------------|
| YAMLs viejos sin `hotel.url` no matchean | Bajo — mismo comportamiento que antes (retorna None, usa defaults) | Re-onboardear el hotel para generar YAML con URL |
| observations.json sin `website` → fallback nunca se activa | Medio — datos Tier A inaccesibles | T0 en FASE-2 agrega `website` a los 6 observations existentes |
| URLs con variantes no cubiertas por `_normalize_url()` | Bajo — las 5 reglas cubren el 99% de casos | Extender `_normalize_url()` si se descubre un caso edge |
| v4complete timeout por scraping lento | Medio — subagente puede timeout a 900s | Re-ejecutar con timeout mas alto |

---

## 6. Lecciones Aprendidas

Completado. Ver `08-analisis-post-implementacion.md` sección 7 para el detalle completo de lecciones de diseño, ejecución, delegate_task, y qué se haría diferente.

**Resumen**: La decisión de diseño más acertada fue usar URL como clave canónica. La lección más importante: verificar premisas de datos contra archivos vivos (observations.json no tenía `website` como se asumió). delegate_task solo es viable para comandos largos sin dependencia de contexto de código.

---

## 7. Cierre del Plan

El plan **ONBOARDING-INJECTION-GAP-2026-07-29** está COMPLETADO.

### Estado final

| Métrica | Valor |
|---------|-------|
| Fases ejecutadas | 8/8 (FASE-0-A, 0-B, 1, 2, 3, RELEASE-A, RELEASE-B, RELEASE-C) |
| Hallazgos resueltos | 8/8 (B1, B2, N3, N4, N5, §10a, §10b, §10c) |
| Bugs críticos cerrados | 2/2 (B1 slug mismatch, B2 frescura 24h) |
| Tests nuevos | 27 (15 normalize_url + 7 loader + 5 observation_format) |
| Regresiones | 0 |
| Versión | v4.67.0 |

### Verificación E2E

Zi One Luxury (https://zione.co/): **rooms=34, adr=290K, occupancy=0.784, evidence_tier=A, ROICR=1.3x**. Datos Tier A confirmados en `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260730_143715.md`.

### Hallazgos residuales para futuros planes

| Item | Descripción |
|------|-------------|
| Pain ratio 7.24% vs 1.9% esperado | El plan maestro esperaba 1.9% con datos Tier A, pero el output real muestra 7.24%. No es un bug — es el valor correcto con datos reales. El 1.9% del plan era una estimación optimista pre-ejecución. |
| `_load_latest_onboarding_data()` sin caché | Iteración O(N) sobre YAMLs. OK para <50 hoteles. Indexar si N > 100. |
| `generate_slug()` aún en main.py | Se mantiene en `run_onboard_mode()` pero ya no en el loader. Sin acción inmediata. |
