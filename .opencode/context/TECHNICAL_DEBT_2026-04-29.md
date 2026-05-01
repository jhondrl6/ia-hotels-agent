# Contexto: Deuda Técnica — 29 Abril 2026 (Validación Forense v2)

**Fuentes:**
- `docs/technical_debt/sync_versions_partial_propagation.md` (SYNC-BUG)
- `docs/technical_debt/hardcodes_audit_2026-04-29.md` (HARDCODE-AUDIT)
- Validación forense directa contra código vivo (2026-04-29, sesión v2)

**Estado al 2026-04-29:** Los dos hallazgos fueron DOCUMENTADOS durante FASE-RELEASE-4.37.0 pero NO CORREGIDOS. Quedan como deuda técnica para proyecto futuro.

**Validación forense v2:** Revisión exhaustiva contra código real. Catálogo original de 19 hardcodes: **2 eliminados correctamente** (H-21 por nombre, H-26 corregido — SÍ existe), **2 reclasificados** (H-22 reducido, H-18 expandido). Deep-dive descubrió **12 hardcodes adicionales NO documentados** (N-01 a N-12).

---

## Matriz de Verificación Forense (v2)

| Claim | Veredicto v1 | Veredicto v2 | Corrección |
|-------|-------------|-------------|------------|
| CR-1: Doble escape YAML `\\\\*\\\\*` en sync_config.yaml L101-103 | CORRECTO | ✅ CORRECTO | — |
| CR-2: Ausencia validación post-reemplazo en sync_versions.py L131-133 | CORRECTO | ✅ CORRECTO | — |
| CR-3: Inconsistencia "v" en template GUIA_TECNICA | CORRECTO | ✅ CORRECTO | — |
| H-21 eliminado (shift_ota no existe) | ELIMINADO | ⚠️ PARCIAL | Nombre "shift_ota" no existe, PERO los valores 0.05/0.10/0.20 SÍ existen como `minimal_improvement`/`moderate_shift`/`optimistic_shift`. Reclassificar, no eliminar. |
| H-26 eliminado (plan stubs no existen) | ELIMINADO | ❌ INCORRECTO | `plan_7d`/`plan_30d`/`plan_60d`/`plan_90d` SÍ existen en v4_diagnostic_generator.py L414-417. Debe REVERTIRSE la eliminación. |
| H-22 reducido a 1 valor | CORRECTO | ✅ CORRECTO | Solo `_get_ia_boost_percentage()` retornando 0.05 |
| H-18 expandido a 2 hardcodes | CORRECTO | ✅ CORRECTO | TIER_CONFIG min_price=1,200,000 vs floor=800,000 en archivos distintos |
| 14 hardcodes confirmados (de 19) | PARCIAL | ❌ REVISADO | Reconteo: 19 originales - 1 eliminado (H-21) + 1 revertido (H-26) = **19 confirmados**. El conteo "14" subestimó. |
| Fuentes documentales existen | CORRECTO | ✅ CORRECTO | Ambos archivos en `docs/technical_debt/` |

---

## HALLAZGO 1: sync_versions.py — Propagación Parcial de Versión

**Archivo:** `scripts/sync_versions.py` + `scripts/sync_config.yaml`
**Severidad:** HIGH (fue MEDIUM, elevada tras descubrir causa raíz real)
**Estado:** WORKAROUND MANUAL APLICADO — bug sigue presente en el script

### Problema

`sync_versions.py --check` reporta "All files in sync" pero la regla `guia_tecnica_header` NUNCA actualiza `GUIA_TECNICA.md`.

### Causas Raíz (3, no 1 como documentado originalmente)

#### CR-1-H1: Doble escape en YAML para GUIA_TECNICA patterns

El documento original no identificó el bug real. El problema NO es inconsistencia de "v" — es **doble escape** en `sync_config.yaml`.

**sync_config.yaml líneas 101-103 (ROTO):**
```yaml
- pattern: '\\\\*\\\\*Última actualización:\\\\*\\\\*\\\\s*\\\\d+\\\\s+\\\\w+\\\\s+\\\\d{4}'
  template: '**Última actualización:** {date_text}'
- pattern: '\\\\*\\\\*Versión:\\\\*\\\\*\\\\s*[\\\\d]+\\\\.[\\\\d]+\\\\.[\\\\d]+[^\\\\(\\\\n]*'
  template: '**Versión:** {version} ({codename})'
```

Los patterns usan `\\\\\\\\*\\\\\\\\*` (doble escape). YAML parsea esto como `\\\\*\\\\*` (literal backslash-star), NO como `\\*\\*` (regex escaped star). El regex resultante **nunca** hace match con `**Versión:**` en el archivo real.

**Comparación con CONTRIBUTING (que SÍ funciona):**
```yaml
# Línea 82 — escape simple → FUNCIONA
- pattern: '>\\\\s*\\\\*\\\\*Version Actual:\\\\*\\\\*\\\\s*v?[\\\\d]+\\\\.[\\\\d]+\\\\.[\\\\d]+\\\\s*\\\\([^)]*\\\\)'
```

**Por qué el script dice "in sync":**
`sync_versions.py` línea 131-133: si `_apply_replacements` retorna `changed=False` (porque `re.sub` no encontró match), el script asume "in sync". Un pattern roto que nunca matchea = siempre "in sync" falso positivo.

**Alcance del doble escape:** Solo afecta a las 2 reglas de `guia_tecnica_header` (L101, L103). Las otras 6 reglas usan escape simple correcto.

#### CR-2-H1: Ausencia de validación post-reemplazo

`sync_versions.py` líneas 131-133:
```python
if not changed:
    self.results[rule_id] = "SYNC"
    print(f"OK: {rule['file']} ({rule_id}) - in sync")
    return True
```

No verifica que el valor interpolado exista en el contenido. Debería confirmar que `v{version}` aparece tras el reemplazo.

#### CR-3-H1: Inconsistencia "v" en template de GUIA_TECNICA

- Template dice: `'**Versión:** {version} ({codename})'` → inserta `4.37.0` SIN "v"
- Archivo real tiene: `**Versión:** v4.37.0` CON "v"
- Pattern busca: `[\\\\d]+\\\\.[\\\\d]+\\\\.[\\\\d]+` SIN `v?`

Incluso si se corrige el doble escape, el template no inserta "v" pero el archivo la tiene. Hay que decidir: agregar "v" al template o quitarla del archivo.

### Estado Actual de los 3 Archivos (post-workaround)

```
docs/CONTRIBUTING.md:4:    > **Version actual:** v4.37.0  → SYNC FUNCIONA para este archivo
docs/GUIA_TECNICA.md:3:    **Versión:** v4.37.0           → MANUAL, sync NO funciona
docs/contributing/REGISTRY.md:3-4: 2026-04-29 / v4.37.0  → SYNC FUNCIONA para registry_last_update
```

**v4.36.0 residual (NO stale, es histórico):**
- `GUIA_TECNICA.md` L25: `### v4.36.0 - 2026-04-26` (título de sección changelog)
- `REGISTRY.md` L4269: mención en descripción de fase completada

### Fix Requerido H1

1. **Corregir doble escape**: `\\\\\\\\*\\\\\\\\*` → `\\\\*\\\\*` en las 2 reglas de `guia_tecnica_header` (sync_config.yaml L101-103)
2. **Consistencia "v"**: Cambiar template de GUIA_TECNICA a `'**Versión:** v{version} ({codename})'` y agregar `v?` al pattern
3. **Agregar validación post-sync** en `sync_versions.py`: verificar que el valor interpolado existe en contenido tras `re.sub`
4. **Test de integración**: cambiar VERSION.yaml a dummy, ejecutar sync, verificar los N archivos

---

## HALLAZGO 2: Hardcodes Audit — Catálogo Completo Revisado

**Archivos afectados:**
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `modules/financial_engine/pricing_calculator.py`
- `modules/financial_engine/loss_projector.py`
- `modules/financial_engine/scenario_calculator.py`
- `modules/utils/financial_factors.py`

**Severidad global:** HIGH
**Estado:** NO CORREGIDOS — catálogo ampliado y re-validado

### Correcciones al Catálogo Original (v1 → v2)

#### H-21: REVERTIR ELIMINACIÓN — Reclassificar como "alias diferente"

El claim original decía `shift_ota` en `scenario_calculator.py` L178,243,286.

- **Verificación por nombre**: "shift_ota" NO existe. Búsqueda retorna 0 resultados. ✅ Eliminación justificada por nombre.
- **Verificación por valor**: Los valores 0.05, 0.10, 0.20 SÍ existen en esas líneas EXACTAS con nombres diferentes:
  - L178: `minimal_improvement = 0.05` → `potential_shift = ota_bookings * minimal_improvement` (L193)
  - L243: `moderate_shift = 0.10` → `potential_shift = ota_bookings * moderate_shift` (L244)
  - L286: `optimistic_shift = 0.20` → `potential_shift = ota_bookings * optimistic_shift` (L300)
- **Veredicto v2**: NO eliminar. Son hardcodes REALES que afectan el cálculo financiero. Reclasificar a Grupo B con nota sobre el nombre real.

#### H-26: REVERTIR ELIMINACIÓN — Los plan stubs SÍ existen

El claim original decía "No hay plan stubs en el diagnostic generator".

- **Verificación**: `v4_diagnostic_generator.py` L414-417:
  ```python
  plan_7d = "Revisar y optimizar Google Business Profile"
  plan_30d = "Implementar quick wins identificados y comenzar plan de contenido"
  plan_60d = "Desarrollar presencia en asistentes de IA y monitorear resultados"
  plan_90d = "Consolidar estrategia de IA y evaluar retorno de inversión"
  ```
- **Contexto**: Estos stubs van al DIAGNÓSTICO (01_DIAGNOSTICO). El PROPUESTA (02_PROPUESTA_COMERCIAL) tiene planes dinámicos en `_build_7_day_plan()` etc. (L1211-1365).
- **Severidad real**: LOW-MEDIUM (no son facticialmente incorrectos, pero son genéricos y no reflejan hallazgos del audit).
- **Veredicto v2**: REVERTIR eliminación. Reclasificar a Grupo C (comercial).

### Reconteo Final

| Categoría | Cantidad |
|-----------|----------|
| Hardcodes originales en auditoría | 19 |
| Eliminados correctamente (H-21 por nombre) | -1 |
| Revertidos (H-26 sí existe) | +0 (ya estaba contado) |
| Reclasificados (H-22 reducido, H-18 expandido) | neto 0 |
| **Total hardcodes catálogo original** | **19** |
| Hardcodes nuevos descubiertos (N-01 a N-12) | +12 |
| **Total hardcodes proyecto** | **31** |

### Catálogo Completo — Hardcodes Originales (19 confirmados)

#### Grupo A: Fallbacks Peligrosos (datos falsos al cliente) — 🔴 CRÍTICO

| ID | Elemento | Archivo | Línea Real | Valor Real | Peligro |
|----|----------|---------|------------|------------|---------|
| H-11 | `benchmark_score` SIEMPRE 58 | `v4_proposal_generator.py` | L1040 | `58` | No es fallback: es valor FIJO. Cliente siempre ve "promedio regional 58" sin importar la región real |
| H-12 | `score_tecnico` fallback | `v4_proposal_generator.py` | L573, L986 | `50` | 2 ubicaciones. Si módulo falla, cliente ve 50/100 sin disclaimer |
| H-13 | `coherence_score` fallback | `v4_proposal_generator.py` | L569 | `'70'` (string) | String, no int. Si falla, cliente ve coherencia "70%" inventada |
| H-27 | `voice_readiness` fallback | `v4_diagnostic_generator.py` | L613-614, L616-617 | `'0'` + `'unknown'` | 2 ramas (exception + proxy None). Cero falso sin explicación |

**Todos los fallbacks del Grupo A producen DATOS FALSOS si el módulo falla silenciosamente. El cliente ve un número inventado sin saber que es fallback.**

#### Grupo B: Parámetros Financieros Operativos — 🟡 HIGH

| ID | Elemento | Archivo | Línea Real | Valor Real |
|----|----------|---------|------------|------------|
| H-14a | `recovery_factor` conservador | `v4_proposal_generator.py` | L524 | `0.15` |
| H-14b | `recovery_factor` realista | `v4_proposal_generator.py` | L486 | `0.20` |
| H-14c | `recovery_factor` optimista | `v4_proposal_generator.py` | L528 | `0.25` |
| H-17 | Scenario weights | `v4_proposal_generator.py` | L1101 | `0.70 / 0.20 / 0.10` |
| H-19 | `TIER_CONFIG` completo | `pricing_calculator.py` | L47-69 | 3 tiers con percentages, min/max |
| H-20 | `degradation_rate` | `loss_projector.py` | L65 | `0.02` (2%/mes) |
| H-21 | OTA shift per scenario (RECLASIFICADO) | `scenario_calculator.py` | L178, L243, L286 | `0.05` / `0.10` / `0.20` |
| H-22 | `ia_boost` | `scenario_calculator.py` | L471 | `0.05` (único valor, TODO: GA4) |
| H-18a | `TIER_CONFIG` min_price BOUTIQUE | `pricing_calculator.py` | L52 | `1,200,000` |
| H-18b | Pricing floor fallback | `v4_proposal_generator.py` | L1104 | `800,000` (difiere de H-18a) |

**H-21 Detalle (v2):** Originalmente eliminado porque la variable no se llama `shift_ota`. En realidad SÍ existe como `minimal_improvement`/`moderate_shift`/`optimistic_shift`. Los valores son idénticos al claim original. TODO comments en `_get_shift_percentage()` y `_get_ia_boost_percentage()` confirman intención de reemplazar con datos GA4.

**H-18b Detalle:** `TIER_CONFIG` define `min_price: 1_200_000` para BOUTIQUE, pero `_estimate_monthly_investment()` usa `800000` como floor. Son DOS hardcodes distintos para "precio mínimo" en DOS archivos. Inconsistencia comercial.

**H-22 Detalle:** `_get_ia_boost_percentage()` tiene TODO: `# TODO: Reemplazar con dato de GA4 cuando esté disponible`. Documentado como deuda conocida por el propio desarrollador.

#### Grupo C: Términos Comerciales — 🔵 MEDIUM

| ID | Elemento | Archivo | Línea Real | Valor Real |
|----|----------|---------|------------|------------|
| H-15 | ROI cap | `v4_proposal_generator.py` | L934 | `5.0`X máximo |
| H-16 | `break_even` default | `v4_proposal_generator.py` | L941 | `6` meses |
| H-23 | Discounts template | `propuesta_v6_template.md` | L170-172 | `10%` trimestral, `18%` semestral |
| H-24 | Cuotas sin interés | `propuesta_v6_template.md` | L168 | `3` cuotas |
| H-26 | Plan stubs genéricos (REVERTIDO) | `v4_diagnostic_generator.py` | L414-417 | Strings fijos 7d/30d/60d/90d |

**H-26 Detalle (v2):** Originalmente eliminado alegando que no existen. SÍ existen: `plan_7d`, `plan_30d`, `plan_60d`, `plan_90d` como strings hardcoded. Van al diagnóstico (no al propuesta). Son genéricos pero no facticialmente incorrectos. Severidad real: LOW-MEDIUM.

#### Grupo D: Duplicación de Garantías — 🟡 MEDIUM

| ID | Elemento | Archivo 1 | Archivo 2 | Detalle |
|----|----------|-----------|-----------|---------|
| H-25 | Garantías comerciales | `v4_proposal_generator.py` L964-979 | `propuesta_v6_template.md` L142-153 | "90 días", "10%", "15 días" hardcodeados en AMBOS lugares |

**H-25 Detalle:** Las garantías existen en el método Python `_build_guarantees_section()` Y en el template MD. Editar uno sin el otro produce inconsistencia. El documento original solo citaba el método Python.

---

## HALLAZGO 3: Hardcodes NO Documentados (Nuevos, N-01 a N-12)

Descubiertos durante deep-dive forense. NO estaban en el catálogo original de 19.

### Grupo E: Fallbacks de Datos (Descubiertos) — 🟡 HIGH

| ID | Elemento | Archivo | Línea | Valor | Impacto |
|----|----------|---------|-------|-------|---------|
| N-01 | `pain_ratio` default | `v4_proposal_generator.py` | L204 | `0.20` | Afecta TODOS los cálculos de ROI/proyección cuando no hay pricing_result |
| N-04 | Descuento pago único | `v4_proposal_generator.py` | L602 | `0.9` (10% dto) | Visible al cliente en opciones de pago |
| N-04b | Descuento trimestral | `v4_proposal_generator.py` | L605 | `0.95` (5% dto) | Visible al cliente en opciones de pago |

### Grupo F: Umbrales de Scoring (Descubiertos) — 🔵 MEDIUM

| ID | Elemento | Archivo | Línea | Valor | Impacto |
|----|----------|---------|-------|-------|---------|
| N-02 | Confidence thresholds | `v4_proposal_generator.py` | L890-900 | `0.85`/`0.70`/`0.40` | Determina etiquetas de calidad de assets |
| N-03 | Coherence score multipliers | `v4_diagnostic_generator.py` | L847-853 | `100`/`70`/`30`/`0` | Cálculo de coherencia: VERIFIED=100, ESTIMATED=70, etc. |
| N-06 | GBP geo_score threshold | `v4_diagnostic_generator.py` | L1992 | `70` | Determina pass/fail para pilar GEO |
| N-07 | Mobile score threshold | `v4_diagnostic_generator.py` | L1709 | `50` | Determina "Adecuado" vs "Bajo" |
| N-08 | Citability thresholds | `v4_diagnostic_generator.py` | L1681-1685 | `50`/`30` | Afecta scoring cualitativo IAO |
| N-09 | IAO label thresholds | `v4_diagnostic_generator.py` | L1717-1719 | `60`/`35` | Determina etiqueta "Alta"/"Media"/"Baja" |
| N-10 | Score status multipliers | `v4_diagnostic_generator.py` | L1741-1743 | `1.1`/`0.9` | Determina "Superior"/"Promedio" vs benchmark |

### Grupo G: Narrativas de Impacto (Descubiertas) — 🔴 CRÍTICO

| ID | Elemento | Archivo | Líneas | Cantidad | Impacto |
|----|----------|---------|--------|----------|---------|
| N-05 | Pain narrative impact percentages | `v4_diagnostic_generator.py` | L2208-2279 | 14 valores | **Impulsan las "4 Razones" (brechas) con impacto monetario mostrado al cliente** |

**N-05 Detalle (CRÍTICO):** 14 valores hardcoded que determinan el porcentaje de impacto de cada brecha en el diagnóstico:
- `no_whatsapp_visible`: impacto=0.20
- `no_hotel_schema`: impacto=0.25
- `low_gbp_score`: impacto=0.30
- `poor_performance`: impacto=0.15
- `no_faq_schema`: impacto=0.12
- `no_og_tags`: impacto=0.08
- `low_citability`: impacto=0.10
- `ai_crawler_blocked`: impacto=0.15
- `no_org_schema`: impacto=0.08
- (+ 5 más)

Estos valores son **completamente invisibles** para auditorías de código que solo buscan "hardcoded numbers" — están en un diccionario de narrativas, no en cálculos financieros directos. Son los que más afectan la percepción del cliente porque determinan QUÉ TAN GRAVE se ve cada problema.

### Grupo H: Factores Financieros (Descubiertos) — 🟡 HIGH

| ID | Elemento | Archivo | Línea | Valor | Impacto |
|----|----------|---------|-------|-------|---------|
| N-11 | `SUPERPOSITION_FACTOR` | `modules/utils/financial_factors.py` | L50 | `0.7` | Factor de corrección para evitar doble conteo |
| N-11b | `DEFAULTS` dict completo | `modules/utils/financial_factors.py` | ~L20-48 | 12 valores | `factor_captura_aila=0.70`, `comision_ota_min/base/max=0.18/0.20/0.22`, `penalizacion_invisibilidad_ia=0.05`, `revpar_cop=197120`, etc. |
| N-12 | GATE ratio constants | `pricing_calculator.py` | L72-74 | `0.03`/`0.06`/`0.045` | `GATE_MIN_RATIO`, `GATE_MAX_RATIO`, `GATE_IDEAL_RATIO` — adicionales a TIER_CONFIG |

---

## HALLAZGO 4: Deuda Técnica No-Code (TODOs, Stubs y Módulos Huérfanos)

**⚠️ REVISADO 2026-04-29 (sesión 16:45):** Severidad original sobrestimada. Verificación forense de imports y uso real revela que Profound/Semrush son huérfanos funcionales — el pipeline principal NO los usa. Sus funciones están cubiertas por alternativas reales (GSC, GA4, PageSpeed).

### TODO Comments (12 encontrados, ninguno en H-catalog)

| Módulo | Línea | TODO | Severidad |
|--------|-------|------|-----------|
| ~~`analytics/profound_client.py`~~ | ~~L108, L139, L167~~ | ~~"Implementar llamada real a API de Profound"~~ | ~~🔴 HIGH (API stub)~~ → 🟢 LOW (huérfano, ver abajo) |
| ~~`analytics/semrush_client.py`~~ | ~~L69, L96, L120~~ | ~~"Implementar llamada real a API de Semrush"~~ | ~~🔴 HIGH (API stub)~~ → 🟢 LOW (huérfano, ver abajo) |
| `asset_generation/data_assessment.py` | L361 | "Re-evaluar clasificación con datos encontrados" | 🟡 MEDIUM |
| `auditors/v4_comprehensive.py` | L1152-1153 | `lat=0.0, lng=0.0` — "Get from geocoding" | 🟡 MEDIUM (coordenadas hardcoded a 0.0) |
| `financial_engine/scenario_calculator.py` | L465, L470 | "Reemplazar con dato de GA4 cuando esté disponible" | 🟡 MEDIUM |
| `scrapers/scraper_fallback.py` | L562 | "Implementar cuando se requiera integración LLM" | 🔵 LOW |

### Corrección de Severidad: APIs Stub — Verificación de Uso Real

**Investigación forense (2026-04-29 17:00):**

| Módulo | Líneas | Importado por | Usado en pipeline v4complete? | Alternativa real |
|--------|--------|--------------|-------------------------------|-------------------|
| `profound_client.py` | 168 | SOLO `aeo_metrics_gen.py` (huérfano) | ❌ NO — `_check_analytics_status()` NO lo verifica; `_build_transparency_section()` NO lo muestra | Ninguna para AI Visibility |
| `semrush_client.py` | 121 | SOLO `aeo_metrics_gen.py` (huérfano) | ❌ NO — ídem | **GoogleSearchConsoleClient** (298 líneas, IMPLEMENTADO, API GRATIS) para tráfico orgánico |
| `data_aggregator.py` | 320 | NADIE (completamente huérfano) | ❌ NO — cero imports externos | N/A |
| `aeo_metrics_gen.py` | 238 | NADIE (completamente huérfano) | ❌ NO — `generate_aeo_metrics()` nunca se llama | N/A |

**Conclusión:** El TECHNICAL_DEBT original clasificó 6 "API stubs" como HIGH severity. La realidad:
- **3 funciones de Semrush** (tráfico orgánico, keywords, SEO) → YA CUBIERTAS por `GoogleSearchConsoleClient` (298 líneas, API gratuita de Google) + `PageSpeedClient` + scraping real
- **3 funciones de Profound** (AI visibility, share of voice, citation rate) → genuinamente no tienen alternativa, PERO no alimentan ningún score del diagnóstico. Solo afectan la sección de transparencia
- **2 módulos completos huérfanos**: `data_aggregator.py` (320 líneas, 0 imports) y `aeo_metrics_gen.py` (238 líneas, 0 callers)
- **`_check_analytics_status()`** dice verificar Profound/Semrush pero el código real solo verifica GA4 y GSC
- **`AnalyticsStatus.is_any_missing()`** siempre retorna True porque `profound_available=False` y `semrush_available=False` son defaults nunca modificados
- **`_build_transparency_section()`** solo lista GA4, GSC, Audit Web y Places — no menciona Profound/Semrush

### Severidad Revisada

| Elemento | Severidad Original | Severidad Corregida | Justificación |
|----------|-------------------|---------------------|---------------|
| ProfoundClient stub | 🔴 HIGH | 🟢 LOW | Huérfano funcional. No alimenta scores. El sistema es honesto: muestra "No disponible". Deprecar. |
| SemrushClient stub | 🔴 HIGH | 🟢 LOW | Huérfano funcional. GSC + GA4 + PageSpeed cubren sus funciones. Deprecar. |
| data_aggregator.py | No catalogado | 🟢 LOW | 320 líneas, 0 imports externos. Código muerto. Deprecar/eliminar. |
| aeo_metrics_gen.py | No catalogado | 🟢 LOW | 238 líneas, 0 callers. Código muerto. Deprecar/eliminar. |
| AnalyticsStatus.is_any_missing() bug | No catalogado | 🟡 MEDIUM | Siempre True por stubs no inicializados. Corregir para solo verificar fuentes reales (GA4, GSC). |

### Nuevo Hallazgo: H6 — Módulos Huérfanos en analytics/

**Severidad:** 🟡 MEDIUM (confusión operativa, no impacto en output)
**Archivos:** `modules/analytics/profound_client.py`, `semrush_client.py`, `data_aggregator.py`; `modules/delivery/generators/aeo_metrics_gen.py`
**Impacto:** 4 archivos (847 líneas combinadas) que parecen activos pero nunca se ejecutan. Causan confusión en auditorías (como este mismo TECHNICAL_DEBT). El `__init__.py` de analytics re-exporta clases que no se usan. `AnalyticsStatus` tiene campos para profound/semrush que siempre están en False.
**Fix:** Deprecar con warning + docstring, limpiar `__init__.py`, corregir `AnalyticsStatus.is_any_missing()`.

---

## HALLAZGO 5: Disconnect Config/Code

### settings.yaml no es leído por los generadores

`config/settings.yaml` existe con datos de pricing (package prices en L132-189), PERO ni `v4_proposal_generator.py` ni `v4_diagnostic_generator.py` importan de este archivo. Los generadores usan valores hardcodeados propios.

**Implicación:** Incluso si un usuario edita `settings.yaml` para ajustar precios, los documentos generados NO reflejarán el cambio.

### Archivos de config faltantes

| Config esperado | Contenido propuesto | Archivos que lo necesitarían |
|-----------------|---------------------|------------------------------|
| `config/pricing.yaml` | TIER_CONFIG, GATE ratios, min/max prices | pricing_calculator.py, v4_proposal_generator.py |
| `config/scenarios.yaml` | recovery_factors, weights, degradation, ia_boost, shift percentages | scenario_calculator.py, v4_proposal_generator.py |
| `config/fallbacks.yaml` | benchmark_score, score_tecnico, coherence, voice_readiness | v4_proposal_generator.py, v4_diagnostic_generator.py |
| `config/regional_benchmarks.yaml` | Pain narrative impacts, scoring thresholds | v4_diagnostic_generator.py |

---

## Causas Raíz Consolidadas (7)

### CR-1: Doble escape YAML en sync_config.yaml
- **Archivo:** `scripts/sync_config.yaml` líneas 101-103
- **Impacto:** 2 reglas de GUIA_TECNICA jamás se sincronizan
- **Fix:** Cambiar `\\\\\\\\*\\\\\\\\*` a `\\\\*\\\\*` en ambos patterns

### CR-2: Ausencia de validación post-reemplazo en SyncEngine
- **Archivo:** `scripts/sync_versions.py` líneas 131-133
- **Impacto:** Pattern roto = "in sync" falso positivo sin detección
- **Fix:** Verificar que el valor interpolado existe en contenido post-reemplazo

### CR-3: Fallbacks silenciosos producen datos falsos
- **Archivos:** `v4_proposal_generator.py` (L569, 573, 986, 1040), `v4_diagnostic_generator.py` (L613-614, L616-617)
- **Impacto:** Cliente ve scores inventados sin disclaimer visible
- **Fix:** (a) Agregar flag "estimated" visible en template, (b) Mover defaults a config, (c) Considerar mostrar "N/A" si no hay dato real

### CR-4: Parámetros financieros hardcodeados sin fuente configurable
- **Archivos:** `pricing_calculator.py`, `v4_proposal_generator.py`, `loss_projector.py`, `scenario_calculator.py`, `financial_factors.py`
- **Impacto:** Cambios comerciales requieren editar código Python
- **Fix:** Extraer a YAML config con schema validado + carga con fallback

### CR-5: Duplicación garantías (código + template)
- **Archivos:** `v4_proposal_generator.py` L964-979 Y `propuesta_v6_template.md` L142-153
- **Impacto:** Inconsistencia si se edita uno y no el otro
- **Fix:** Eliminar método `_build_guarantees_section()`, mantener solo template con variables

### CR-6: (NUEVO) Disconnect config/code — settings.yaml ignorado
- **Archivos:** `config/settings.yaml` existe pero no es importado por generadores
- **Impacto:** Ediciones de config no se reflejan en documentos generados
- **Fix:** Unificar: que TODOS los parámetros de negocio se lean de config YAML

### CR-7: (NUEVO) Narrativas de impacto hardcodeadas sin parametrizar
- **Archivos:** `v4_diagnostic_generator.py` L2208-2279 (14 valores)
- **Impacto:** Porcentajes de impacto de brechas no ajustables por región/tipo de hotel
- **Fix:** Migrar a `config/regional_benchmarks.yaml` con schema validado

---

## Plan de Implementación Corregido

### Proyecto: `FEATURE-CONFIG-EXTRACTION`

**Objetivo:** Corregir bug de sync + migrar 31 hardcodes a archivos YAML con schema validado.

**Fases reordenadas por prioridad real:**

| Fase | Alcance | Archivos | Hardcodes | Prioridad |
|------|---------|----------|-----------|-----------|
| FASE-CONFIG-1 | sync_versions fix (CR-1 + CR-2) | `sync_config.yaml`, `sync_versions.py` | — | 🔴 ALTA (bug activo) |
| FASE-CONFIG-2 | Fallbacks peligrosos (CR-3) | `v4_proposal_generator.py`, `v4_diagnostic_generator.py` | H-11, H-12, H-13, H-27 | 🔴 ALTA (datos falsos) |
| FASE-CONFIG-3 | Extracción pricing + escenarios (CR-4) | `pricing_calculator.py`, `v4_proposal_generator.py`, `loss_projector.py`, `scenario_calculator.py`, `financial_factors.py`, 3 YAML nuevos | H-14, H-17, H-18, H-19, H-20, H-21, H-22, N-01, N-11, N-12 | 🟡 MEDIA |
| FASE-CONFIG-4 | Template parametrizado (CR-5 + comerciales) | `propuesta_v6_template.md`, `v4_proposal_generator.py`, `v4_diagnostic_generator.py` | H-15, H-16, H-23, H-24, H-25, H-26, N-04 | 🟡 MEDIA |
| FASE-CONFIG-5 | Umbrales y narrativas (CR-7) | `v4_diagnostic_generator.py`, YAML nuevo | N-02, N-03, N-05, N-06, N-07, N-08, N-09, N-10 | 🟡 MEDIA |
| FASE-CONFIG-6 | Config reconnect + Deprecación módulos huérfanos (CR-6 + H6) | `config/settings.yaml`, generadores, `modules/analytics/__init__.py`, `data_models/analytics_status.py`, 4 módulos a deprecar | — | 🟡 MEDIA |
| FASE-CONFIG-7 | Tests + regresión | `tests/` | — | 🟡 MEDIA |
| FASE-CONFIG-8 | Documentación + RELEASE | `CHANGELOG.md`, `GUIA_TECNICA.md` | — | 🔵 BAJA |

**Pre-requisitos por fase:**

**FASE-CONFIG-1:**
- Test que cambie VERSION.yaml a dummy (ej: `99.99.99`), ejecute sync, verifique los N archivos
- Corregir doble escape en sync_config.yaml
- Agregar `v` al template de GUIA_TECNICA
- Agregar validación post-sync en sync_versions.py

**FASE-CONFIG-2:**
- Schema YAML para fallbacks con tipos validados
- Flag `estimated` visible en template cuando se usa fallback
- Decisionar: ¿mostrar "N/A" o score estimado con disclaimer?

**FASE-CONFIG-3:**
- `config/pricing.yaml` con TIER_CONFIG + GATE ratios
- `config/scenarios.yaml` con recovery_factors, weights, degradation, ia_boost, shift percentages, OTA commission
- `config/financial_defaults.yaml` con DEFAULTS de financial_factors.py
- Carga con fallback: si YAML no existe, usar defaults documentados
- Resolver inconsistencia H-18b (800K vs 1.2M como floor)

**FASE-CONFIG-4:**
- Eliminar `_build_guarantees_section()` (método duplicado)
- Parametrizar términos comerciales como variables inyectadas
- `config/commercial.yaml` con garantías, descuentos, cuotas, ROI cap, break_even
- Reemplazar plan stubs (H-26) con generación dinámica o al menos variables configurables

**FASE-CONFIG-5:**
- `config/regional_benchmarks.yaml` con pain narrative impacts, scoring thresholds, confidence levels
- Parametrizar los 14 valores de N-05 (pain narratives)
- Parametrizar umbrales N-02, N-03, N-06 a N-10

**FASE-CONFIG-6:**
- Auditar `config/settings.yaml` vs código (identificar parámetros duplicados con nuevos YAML)
- Deprecar módulos huérfanos: `profound_client.py`, `semrush_client.py`, `data_aggregator.py`, `aeo_metrics_gen.py`
- Agregar `@deprecated` warnings + docstrings + limpiar `modules/analytics/__init__.py`
- Corregir `AnalyticsStatus.is_any_missing()` → solo verificar GA4 y GSC (no stubs)
- Eliminar duplicación entre settings.yaml y YAML nuevos
- Unificar imports en generadores

**FASE-CONFIG-7:**
- Tests que verifiquen cada valor se lee de config, no de hardcode
- Tests que simulen config faltante (fallback a defaults)
- `doctor.py` debe verificar integridad de config files

**FASE-CONFIG-8:**
- CHANGELOG con formato CONTRIBUTING.md
- GUIA_TECNICA con nota técnica por fase
- run_all_validations.py --quick (4/4 checks)

**Riesgos:**
- Romper backwards compatibility (mitigar con fallback a defaults)
- Defaults incorrectos si YAML tiene errores (mitigar con schema validation)
- Migración parcial (mitigar con FASE-CONFIG-7 obligatoria)
- Inconsistencia H-18b requiere decisión comercial antes del fix
- N-05 (14 pain narratives) es el de mayor impacto en percepción del cliente
- Deprecación de módulos huérfanos: verificar que `__init__.py` cleanup no rompa imports legacy
- `AnalyticsStatus.is_any_missing()` actualmente siempre retorna True — corregir podría cambiar el comportamiento de `_build_transparency_section()`

---

## metadata.yaml del Contexto (Actualizado v2)

```yaml
version: 2.0.0
creado: 2026-04-29
validado: 2026-04-29
revision: v2 (exhaustive forensic re-validation)
fuentes:
  - docs/technical_debt/sync_versions_partial_propagation.md
  - docs/technical_debt/hardcodes_audit_2026-04-29.md
  - scripts/sync_versions.py
  - scripts/sync_config.yaml
  - modules/financial_engine/pricing_calculator.py
  - modules/financial_engine/scenario_calculator.py
  - modules/financial_engine/loss_projector.py
  - modules/commercial_documents/v4_proposal_generator.py
  - modules/commercial_documents/v4_diagnostic_generator.py
  - modules/commercial_documents/templates/propuesta_v6_template.md
  - modules/utils/financial_factors.py
correcciones_v2:
  - H-21: REVERTIDA eliminación — valores existen con nombre diferente (minimal_improvement/moderate_shift/optimistic_shift)
  - H-26: REVERTIDA eliminación — plan stubs SÍ existen en v4_diagnostic_generator.py L414-417
  - Conteo original "14 confirmados" INCORRECTO — son 19 del catálogo original
hallazgos_originales: 2
hallazgos_validados: 2 (causas raíz corregidas)
hallazgos_nuevos: 1 (H6 - módulos huérfanos)
hardcodes_catalogo_original: 19
hardcodes_eliminados_correctamente: 0 (H-21 reclasificado, H-26 revertido)
hardcodes_nuevos_descubiertos: 12 (N-01 a N-12)
hardcodes_total_proyecto: 31
causas_raiz: 7 (CR-1 a CR-7)
todos_encontrados: 12
api_stubs_reclasificados: 6 → severidad corregida (eran HIGH, son LOW — cubiertos por GSC/GA4/PageSpeed)
modulos_huerfanos: 4 (profound_client, semrush_client, data_aggregator, aeo_metrics_gen)
config_disconnect: settings.yaml no leído por generadores
estado: DOCUMENTADOS, CORREGIDOS (severidad stubs), AMPLIADOS (H6)
proximo_paso: FASE-CONFIG-1 (sync fix) en nueva sesión
revision_2026-04-29_1700: severidad H4 corregida + H6 añadido (módulos huérfanos)
```
