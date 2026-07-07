# ROICRIIIF — Resultados de Investigación: Root Cause de 2 Issues

**Fecha**: 2026-05-28
**Sesión**: Investigación (read-only, sin modificar código)
**Fuente**: INVESTIGACION_CONTEXTO.md

---

## ISSUE #1: `whatsapp_button` → MISSING — ROOT CAUSE CONFIRMADA

### Root Cause

**`assessment_builder._to_dict()` usa `dataclasses.asdict()` que convierte el objeto `SitePresenceReport` a un dict plano. `verify_proposal_asset_alignment()` no puede extraer el `presence_lookup` de un dict porque usa `hasattr(obj, 'results')`.**

### Cadena completa del bug

```
1. main.py (~L2693): checker.check_site(url)
   → SitePresenceReport OBJETO: .results = {whatsapp_button: PresenceCheckResult(EXISTS)}

2. main.py (~L2770): builder.with_site_presence(report)
   → self._payload.site_presence_report = SitePresenceReport (objeto)

3. assessment_builder._to_dict() L260-263:
   return asdict(self._payload)
   → Convierte SitePresenceReport a DICT
   → {'site_url': '...', 'results': {'whatsapp_button': {'status': {'_value_': 'exists'}, ...}}}

4. publication_gates.py (~L887):
   site_presence_report = assessment.get("site_presence_report")
   → Obtiene el DICT (no el objeto)

5. proposal_asset_alignment.py L206-211:
   if isinstance(site_presence_report, dict) and site_presence_report.get('presence_status') == 'unknown':
       # False: SitePresenceReport NO tiene campo 'presence_status' a nivel raíz
   elif hasattr(site_presence_report, 'results'):
       # False: los dict no tienen atributo .results
   → presence_lookup = {} (vacío)

6. L234: presence_result = presence_lookup.get('whatsapp_button')
   → None (porque presence_lookup está vacío)
   → whatsapp_button va a → missing ❌
```

### Verificación empírica

```python
# SitePresenceChecker detecta correctamente:
r = SitePresenceChecker().check_site('https://www.hotelcastillareal.com/', asset_types=['whatsapp_button'])
r.results['whatsapp_button'].status.value  # → 'exists' ✅

# Pero tras asdict():
d = asdict(r)
hasattr(d, 'results')  # → False ❌
'results' in d          # → True (es una key del dict)
```

### Archivos involucrados

| Archivo | Línea(s) | Rol |
|---------|----------|-----|
| `modules/assessment_builder.py` | 260-263 | `_to_dict()` → `asdict()` serializa el objeto |
| `modules/asset_generation/proposal_asset_alignment.py` | 206-211 | `presence_lookup` solo funciona con objeto, no con dict |
| `modules/asset_generation/site_presence_checker.py` | 96-103 | `SitePresenceReport` dataclass con `.results` |

### Opciones de fix

| Opción | Descripción | Archivos | Pros | Contras |
|--------|-------------|----------|------|---------|
| **A** | Agregar handling de dict en `verify_proposal_asset_alignment` L209: `elif isinstance(site_presence_report, dict) and 'results' in site_presence_report` | 1 archivo (proposal_asset_alignment.py) | Mínimo cambio, backward-compatible | No resuelve la pérdida de tipos (PresenceCheckResult → dict anidado) |
| **B** | Evitar que `_to_dict()` convierta SitePresenceReport: excluirlo de `asdict()` o guardarlo aparte | 1-2 archivos (assessment_builder.py) | Preserva tipos originales | Requiere cambios en cómo publication_gates extrae el campo |
| **C (recomendada)** | Ambas: (1) Agregar dict handling en proposal_asset_alignment.py, (2) También agregar protección en assessment_builder para no perder tipos | 2 archivos | Robusta, cubre ambos lados | Más código a mantener |

**Recomendación**: **Opción A como fix inmediato**. Es 3 líneas de cambio en `proposal_asset_alignment.py` L209, cambia `elif hasattr(site_presence_report, 'results'):` por:

```python
elif hasattr(site_presence_report, 'results'):
    # objeto SitePresenceReport
    ...
elif isinstance(site_presence_report, dict) and 'results' in site_presence_report:
    # dict post-asdict() — navegar clave 'results' como dict
    for asset_type, result_dict in site_presence_report['results'].items():
        # Reconstruir PresenceCheckResult si es necesario, o extraer status directamente
        ...
```

La Opción B puede hacerse en una segunda iteración para preservar tipos.

---

## ISSUE #2: `faq_page` y `optimization_guide` confidence 0.5

### Root Cause

**Los campos requeridos (`faqs` / `metadata`) no están presentes en `validated_data` al momento del preflight check. Como `block_on_failure=False`, el checker genera WARNING + fallback. `_calculate_confidence_score()` asigna 0.5 a checks WARNING con `priority=REQUIRED`, resultando en confidence final = 0.5.**

### Evidencia de regresión

Comparación de archives para Hotel Castilla Real:

| Asset | v4_complete_report.json (temprano) | v4_complete_report1.json (post-FASE-2) | v4_complete_report3.json |
|-------|-------------------------------------|----------------------------------------|--------------------------|
| **faq_page** | **0.85** ✅ PASSED | **0.5** ❌ WARNING | **0.5** ❌ WARNING |
| optimization_guide | 0.5 ❌ WARNING | 0.5 ❌ WARNING | 0.5 ❌ WARNING |
| indirect_traffic_optimization | 0.8 ⚠️ WARNING | 0.8 ⚠️ WARNING | 0.8 ⚠️ WARNING |

**faq_page cayó de 0.85 (PASSED) a 0.5 (WARNING)** entre el primer run y los subsiguientes. Coincide temporalmente con el commit 335d534 (FASE-2: "trata listas como ESTIMATED en preflight_checks.py confidence scoring").

### Cadena del scoring

```
1. preflight_checks.py check_asset() L140-248:
   required_field = ASSET_CATALOG[asset_type].required_field
   faq_page → "faqs"
   optimization_guide → "metadata"
   
2. Si required_field NOT IN validated_data:
   - block_on_failure=False → WARNING + fallback
   - check.fallback_action = fallback ("generate_with_actual_count" / "generate_basic_guide")
   
3. conditional_generator._calculate_confidence_score() L1621-1652:
   WARNING + priority=REQUIRED → +0.5
   WARNING + priority=RECOMMENDED + fallback_action → +0.8
   
   Para faq_page: priority="REQUIRED" (default) → 0.5
   Para optimization_guide: priority="REQUIRED" (default) → 0.5
   
   Con 1 solo check: 0.5/1 = 0.5
```

### Por qué faq_page tenía 0.85 antes

En el run original (v4_complete_report.json), el campo `faqs` probablemente SÍ existía en `validated_data` (datos de scraping real del sitio). La regresión sugiere que:

1. El FASE-2 fix (335d534) cambió cómo se clasifica la confianza de datos tipo lista → posiblemente degradó de VERIFIED/1.0 a ESTIMATED/0.7, pero 0.7 >= 0.5 (required_confidence de faq_page) debería seguir siendo PASSED.

2. **Hipótesis alternativa**: El pipeline de datos dejó de pasar `faqs` a `validated_data` en runs posteriores (posiblemente por un cambio en cómo el orchestrator construye los datos). Si `"faqs"` no está en `validated_data`, el check va directo a WARNING con fallback, resultando en 0.5.

### Archivos involucrados

| Archivo | Línea(s) | Rol |
|---------|----------|-----|
| `modules/asset_generation/asset_catalog.py` | 80-89, 182-192 | Define required_field="faqs" y "metadata", required_confidence=0.5 |
| `modules/asset_generation/preflight_checks.py` | 140-248 | `check_asset()` → WARNING si falta el required_field |
| `modules/asset_generation/preflight_checks.py` | 279-282 | FASE-2 fix: listas → ESTIMATED (0.7) |
| `modules/asset_generation/conditional_generator.py` | 1621-1652 | `_calculate_confidence_score()` → 0.5 para WARNING+REQUIRED |
| `modules/asset_generation/conditional_generator.py` | 640-648 | `_apply_naming_strategy()` → prefijo ESTIMATED_ para WARNING |
| `modules/delivery/generators/faq_gen.py` | 87-155 | FAQGenerator.generate_list() — scraping real del sitio |
| `modules/asset_generation/optimization_guide_generator.py` | 23-279 | OptimizationGuideGenerator.generate() — usa metadata |

### Opciones de fix

| Opción | Descripción | Archivos | Pros | Contras |
|--------|-------------|----------|------|---------|
| **A** | Asegurar que `faqs` y `metadata` lleguen a `validated_data` en el orchestrator | 1 archivo (orchestrator) | Resuelve raíz: datos reales → PASSED → confidence > 0.5 | Requiere investigar dónde se pierden los datos en la pipeline |
| **B** | Bajar `priority` de faq_page/optimization_guide a `RECOMMENDED` en asset_catalog.py | 1 archivo (asset_catalog.py) | 0.5 → 0.8 cuando hay fallback | No resuelve el problema de fondo (datos faltantes), solo maquilla el score |
| **C** | Subir `fallback_action` para que FASE-0H-G8 asigne 0.8 en vez de 0.5 | 1 archivo (conditional_generator.py) | Mismo efecto que B pero sin tocar el catálogo | Igual que B: maquillaje |
| **D** | Investigar + fix A + optionally B/C como safety net | 2-3 archivos | Solución completa | Más investigación requerida (ver abajo) |

### Investigación adicional necesaria (fuera del scope actual)

Para la Opción D, se necesita:

1. **Tracear dónde se construye `validated_data`** para faq_page y optimization_guide en el flujo de v4complete
   - `grep -rn "validated_data\[.faqs.\]\|validated_data\[.metadata.\]" modules/ main.py`
   
2. **Verificar si el scraping de FAQs funciona**: FAQGenerator._extract_services_from_site() hace requests.get — ¿se ejecuta en v4complete? ¿El resultado se inyecta en validated_data?

3. **Comparar el run original vs actual**: ¿Qué cambió en la pipeline de datos entre v4_complete_report.json (faq_page=0.85) y v4_complete_report1.json (faq_page=0.5)?

### Nota sobre optimization_guide vs indirect_traffic_optimization

Son assets distintos:
- `optimization_guide`: required_field="metadata", confidence 0.5 SIEMPRE (en los 3 archives)
- `indirect_traffic_optimization`: required_field="organic_traffic", confidence 0.8 (RECOMMENDED, recibe 0.8 por FASE-0H-G8)

`indirect_traffic_optimization` tiene `priority="RECOMMENDED"` (L309), lo que le da 0.8 en `_calculate_confidence_score`. `optimization_guide` NO tiene priority explícito (default REQUIRED), por eso se queda en 0.5.

---

## Resumen Ejecutivo

| Issue | Root Cause | Severidad | Fix Recomendado | Esfuerzo |
|-------|-----------|-----------|-----------------|----------|
| #1 whatsapp_button MISSING | `asdict()` rompe `hasattr(dict, 'results')` | **Alta** — bloquea el gate proposal_asset_alignment | Opción A: agregar dict handling (3 líneas) | Bajo |
| #2 faq_page 0.5 | `faqs` ausente en validated_data → WARNING → 0.5 | **Media** — degrada alignment a 62.5% | Investigar pérdida de datos en pipeline + Opción A | Medio |
| #2 optimization_guide 0.5 | `metadata` ausente en validated_data → WARNING → 0.5 | **Media** — mismo impacto | Cambiar priority a RECOMMENDED o investigar datos | Bajo/Medio |

### Orden de ataque recomendado

1. **Primero**: Fix Issue #1 (Opción A) — es rápido y desbloquea el gate
2. **Segundo**: Fix Issue #2 optimization_guide — agregar `priority="RECOMMENDED"` en asset_catalog.py L182 (igual que indirect_traffic_optimization), sube de 0.5 a 0.8
3. **Tercero**: Investigar pérdida de datos `faqs` para faq_page — resolvería la regresión de 0.85→0.5

---

*Investigación completada 2026-05-28. No se modificó código.*
