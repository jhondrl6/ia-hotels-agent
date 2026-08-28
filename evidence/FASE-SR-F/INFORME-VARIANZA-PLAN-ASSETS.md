# FASE-SR-F — Informe de Varianza del Plan de Assets (H5) + PageSpeed OPS (H6.1)

> **Fase**: FASE-SR-F del plan SR-PIPELINE-FIXES-2026-08-27 · **Fecha**: 2026-08-28
> **Decisión pre-registrada D-PF6**: fix mínimo + test si la causa es determinista errónea; seguimiento documentado si requiere rediseño mayor.
> **Veredicto**: **FIX** — causa determinista y errónea, upstream en las sondas URL (NO en el mapper). Fix mínimo aplicado en 3 sondas + 15 tests.

---

## 1. Fenómeno investigado

El plan de assets varió entre dos corridas de `v4complete` sobre la misma URL efectiva, separadas por ~30 minutos (2026-08-27):

| Corrida | Hora | URL pasada al CLI | Pains | Assets |
|---------|------|-------------------|-------|--------|
| A | 18:03 | `https://www.hotelsalentoreal.com/` (limpia) | 7 | 7 |
| C | 18:30 | `https://www.hotelsalentoreal.com/?utm_source=google&utm_medium=organic&utm_campaign=GoogleMyBusiness&partner=5792` | 5 | 5 |

Pains **solo en A** (ausentes en C): `ai_crawler_blocked` (confidence 0.5, MEDIUM) y `low_ia_readiness` (confidence 0.34674, HIGH).
Assets **solo en A**: `llms_txt` + `local_content_page` (derivados del pain `low_ia_readiness`).

**Fuentes de datos (solo lectura, sin re-ejecutar el pipeline)**:
- Ledgers: `output/v4_complete/hotelsalentoreal/v4_audit/pain_ledger*.json` (A) vs `output/test_salentoreal_v4c/v4_complete/hotelsalentoreal/v4_audit/pain_ledger*.json` (C)
- Audits: `audit_report_20260827_180335.json` (A) vs `audit_report_20260827_183048.json` (C)
- Diff completo: `evidence/FASE-SR-F/fase_sr_f_ledger_diff.txt` (script solo-lectura `temp/fase_sr_f_diff_ledgers.py`)

## 2. Hipótesis vigente vs hallazgo

**Hipótesis del prompt/CONTEXT §6 (revisada)**: "pain_solution_mapper (o cache de audit/SitePresence) aplica un filtro distinto entre corridas"; grep = 0 de `ai_crawler_blocked` en ambos ledgers.

**Hallazgo (falso la hipótesis)**:
- `ai_crawler_blocked` **SÍ estaba** en el ledger de A (conf 0.5, status DETECTED).
- `pain_solution_mapper` es **determinista**: umbrales fijos — `ai_crawler_blocked` si `ai_crawlers.overall_score < 0.7` (conf = score); `low_ia_readiness` si `ia_readiness.overall_score < 50` (conf = score/100). Misma entrada → mismo plan (verificado con test `test_mapper_is_deterministic_same_input_same_plan`).

## 3. Causa raíz real (cadena causal sellada)

La varianza se originaba en la **capa de medición**, no en la de decisión:

1. La corrida C pasó la URL **con query UTM**.
2. `AICrawlerAuditor` construía la sonda como `f"{url}/robots.txt"` → pedía `…/?utm=…/robots.txt` (malformada) → el servidor respondió **200 con la homepage** → el parser la interpretó como robots.txt "sin bloqueos" → `overall_score = 1.0`, `robots_exists = True`. **Evidencia decisiva**: un 404 real habría dado score 0.5 y `robots_exists=False`; la corrida A midió **0.5 con 14 bloqueados**.
3. La sonda `/llms.txt` en `v4_comprehensive._calculate_ia_readiness` (`f"{url}/llms.txt"`) sufrió lo mismo → homepage 200 contó como llms.txt presente → `llms_txt = 100` falso.
4. IA-Readiness: A = **34.674** (crawler_access 50, llms_txt 0) vs C = **56.896** (crawler_access 100, llms_txt 100). Delta = **22.222 exacto**, reproducible con los pesos del `IAReadinessCalculator`: `(50·0.22 + 100·0.09) / 0.90` (redistribución sin GA4 sobre 0.90).
5. El mapper, determinista, con esos scores: `1.0 ≥ 0.7` y `56.9 ≥ 50` → **ninguno de los 2 pains** → 5 pains → 5 assets. Con la medición de A: `0.5 < 0.7` y `34.7 < 50` → ambos pains → 7 assets.

**Conclusión**: exclusión **determinista por forma de la URL** (medición corrupta), no por tiempo, caché ni filtro errático.

## 4. Fix mínimo aplicado (D-PF6: FIX)

Anclaje de toda sonda URL derivada al **origen del sitio** (`urlparse` → `scheme://netloc`), patrón de referencia `seo_accelerator_pro._check_robots_and_sitemap`:

| Archivo | Cambio |
|---------|--------|
| `modules/auditors/ai_crawler_auditor.py` | Sonda robots.txt anclada al origen (import `urljoin`→`urlparse`) |
| `modules/auditors/v4_comprehensive.py` | Sonda `/llms.txt` en `_calculate_ia_readiness` anclada al origen |
| `modules/asset_generation/site_presence_checker.py` | `_check_direct_resource` anclada al origen |

**Desviación documentada**: el prompt anticipaba tocar `pain_solution_mapper.py` (matriz de conflictos); la investigación lo absolvió — el fix NO lo tocó.

## 5. Verificación

- **Tests nuevos**: `tests/auditors/test_fase_sr_f_probe_url_canonicalization.py` — 15 tests en 4 clases (sondas sin query; UTM ya no simula robots permisivo; homepage 200 ≠ llms.txt; delta 22.222 reproducible; A<50≤C; plan de pains 5-vs-7 con conf exactas). **15/15 PASSED** (`fase_sr_f_tests.txt`).
- **Regresión**: 58 tests aislados, **0 fallos** — 31 auditors + 22 site_presence (×3 archivos) + 5 mapper.
- **Greps residuos (L2)**: 0 construcciones `f"{url}/robots.txt"` ni equivalentes residuales en sondas activas.

## 6. PageSpeed OPS (H6.1, rec #6) — verificación de config (sin tocar secretos)

- **Fallback chain** (`pagespeed_client.py`): `PAGESPEED_API_KEY → GOOGLE_PAGESPEED_API_KEY → GOOGLE_API_KEY`.
- **Estado del .env** (solo existencia de nombres, valores NO inspeccionados): `GOOGLE_PAGESPEED_API_KEY` presente, `GOOGLE_MAPS_API_KEY` presente; `PAGESPEED_API_KEY` y `GOOGLE_API_KEY` ausentes → PageSpeed resuelve la **segunda** variable.
- **Síntoma en corrida C**: "API key not valid" desde PageSpeed mientras Places funcionaba (keys distintas) → la key de `GOOGLE_PAGESPEED_API_KEY` es inválida o no tiene la **PageSpeed Insights API habilitada**.
- **Diseño correcto**: degradación sin bloqueo (`skipped_validators`; corrida C completó 12/13 gates).
- **ACCIÓN DEL USUARIO (OPS)**: en Google Cloud Console — habilitar "PageSpeed Insights API" para la key existente **o** crear una key nueva y asignarla a `PAGESPEED_API_KEY` (variable canónica declarada en `.env.template`). No se tocaron secretos en esta fase.

## 7. Reproducibilidad del análisis

```powershell
# Diff de ledgers (solo lectura)
./venv/Scripts/python.exe temp/fase_sr_f_diff_ledgers.py > temp/fase_sr_f_ledger_diff.txt 2>&1

# Tests nuevos + regresión (procesos aislados, salida a archivo)
./venv/Scripts/python.exe -m pytest tests/auditors/test_fase_sr_f_probe_url_canonicalization.py -v > temp/fase_sr_f_tests.txt 2>&1
```
