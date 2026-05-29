# ROICRIIIF — Contexto de Investigación: 2 Issues Persistentes

**Fecha**: 2026-05-28  
**Sesión origen**: FASE-4 (delegate task, fallido)  
**Objetivo**: Investigar y resolver los 2 issues que bloquean publication readiness

---

## ANTECEDENTES

### Contexto general
- **Proyecto**: iah-cli (v4.57.0)
- **Hotel**: Hotel Castilla Real (https://www.hotelcastillareal.com/)
- **Región**: eje_cafetero
- **v4complete ejecutado**: output\v4_complete\02_PROPUESTA_COMERCIAL_20260528_181937.md
 **Gates**: 10/11 passed, 1 BLOCKED (proposal_asset_alignment)
- **Coherence**: 0.8262 ✅ (≥ 0.80)
- **Alignment**: 62.5% ❌ (< 80%)

### Issues originales (FASE-1 a FASE-3 apply fixes, FASE-4 verifica)

| Fix | Issue | Expected Result | Resultado FASE-4 |
|-----|-------|-----------------|------------------|
| FASE-1 | Gate no reconoce whatsapp existente | whatsapp_button → present_in_production | ❌ sigue como MISSING |
| FASE-2 | Confidence bajo (faq_page/optimization_guide) | Al menos uno ≥ 0.7 | ❌ Ambos 0.5 |
| FASE-3 | "13% del dolor" artifact en propuesta | Texto eliminado/corregido | ✅ CORREGIDO |

### Intentos previos
- **FASE-1B** (commit 9c8977f): bridge skipped_assets → site_presence_report en publication_gates
- **FASE-2** (commit 335d534): trata listas como ESTIMATED en preflight_checks.py confidence scoring
- **FASE-3**: scrubber para eliminar "13% del dolor" — ✅ funcionando

---

## ISSUE #1: `whatsapp_button` marcado como MISSING pese a existir en producción

### Síntoma
- `gate_report` muestra: `"missing": [{"service": "Botón de WhatsApp", "asset": "whatsapp_button", ...}]`
- `present_in_production: []` (vacío)
- `SitePresenceChecker` confirma EXISTS cuando se prueba aisladamente

### Root cause ENCONTRADA (confirmada con tests reproducibles)

**El problema**: `SitePresenceReport` se convierte a `dict` via `asdict()` en `assessment_builder._to_dict()`, y `verify_proposal_asset_alignment` no puede extraer `presence_lookup` del dict.

### Cadena de llamadas probada:

```python
# TEST AISLADO (funciona correctamente):
checker = SitePresenceChecker()
report = checker.check_site('https://www.hotelcastillareal.com/', asset_types=['whatsapp_button'])
# report.results['whatsapp_button'].status = PresenceStatus.EXISTS ✅

# verify_proposal_asset_alignment con objeto SitePresenceReport:
result = verify_proposal_asset_alignment(proposal_services=ALL_PROMISED_SERVICES,
    generated_assets=[], site_presence_report=report)
# present_in_production: ['Botón de WhatsApp'] ✅

# PERO cuando assessment_builder convierte a dict (asdict):
report_dict = asdict(report)  # {'site_url':..., 'results': {whatsapp_button: {...dict...}}}
# hasattr(dict, 'results') = False ❌
# presence_lookup queda {} → whatsapp_button va a missing ❌
```

### Código relevante

**assessment_builder.py** (L260-263):
```python
def _to_dict(self) -> Dict[str, Any]:
    from dataclasses import asdict
    return asdict(self._payload)
    # ↑ Esto convierte SitePresenceReport (objeto) a dict
    # donde 'results' es un dict interno, no accesible via .results
```

**publication_gates.py** (L206-211):
```python
presence_lookup: Dict[str, Any] = {}
presence_unknown = False
if site_presence_report is not None:
    if isinstance(site_presence_report, dict) and site_presence_report.get('presence_status') == 'unknown':
        presence_unknown = True
    elif hasattr(site_presence_report, 'results'):  # ← FALSE para dict
        for asset_type, result in site_presence_report.results.items():
            presence_lookup[asset_type] = result
    # ↑ Si site_presence_report es dict, presence_lookup queda {}
```

**proposal_asset_alignment.py** (L233-234):
```python
presence_result = presence_lookup.get(expected_asset_type)
# → None cuando presence_lookup={} (porque era dict, no objeto)
```

### Flujo real en v4complete

```
main.py L2693-2700:
  site_presence_report = checker.check_site(args.url)
  → SitePresenceReport object con .results = {whatsapp_button: PresenceCheckResult}

main.py L2770:
  builder.with_site_presence(site_presence_report)
  → self._payload.site_presence_report = site_presence_report (objeto)

builder.build() → _to_dict():
  return asdict(self._payload)
  → SitePresenceReport se convierte a dict
  → 'results' ahora es {'whatsapp_button': {...dict...}}, no .results

publication_gates.py L887:
  site_presence_report = assessment.get("site_presence_report")
  → obtiene el DICT (no el objeto)

publication_gates.py L915:
  verify_proposal_asset_alignment(site_presence_report=site_presence_report)
  → recibe dict, hasattr(dict, 'results') = False
  → presence_lookup = {}
  → whatsapp_button → missing
```

### Test de verificación rápida

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Test 1: SitePresenceChecker aisladamente (debe retornar EXISTS)
python -c "
from modules.asset_generation.site_presence_checker import SitePresenceChecker
r = SitePresenceChecker().check_site('https://www.hotelcastillareal.com/', asset_types=['whatsapp_button'])
print(r.results['whatsapp_button'].status.value)
# Esperado: 'exists'
"

# Test 2: Convierte a dict y verifica hasattr
python -c "
from modules.asset_generation.site_presence_checker import SitePresenceChecker
from dataclasses import asdict
r = SitePresenceChecker().check_site('https://www.hotelcastillareal.com/', asset_types=['whatsapp_button'])
d = asdict(r)
print('hasattr(dict, results):', hasattr(d, 'results'))
# Esperado: False
"
```

---

## ISSUE #2: `faq_page` y `optimization_guide` confidence 0.5 (necesario ≥ 0.7)

### Síntoma
- Ambos assets con prefijo `ESTIMATED_` y confidence 0.5
- Gate `asset_confidence` reporta WARNING (2 assets below threshold)
- alignment: 62.5% (< 80%)

### Datos del run FASE-4

```json
"assets_generated": [
  {"asset_type": "optimization_guide", "filename": "ESTIMATED_guia_optimizacion_20260528_181927.md", "preflight_status": "WARNING", "confidence_score": 0.5},
  {"asset_type": "faq_page", "filename": "ESTIMATED_faqs_20260528_181927.json", "preflight_status": "WARNING", "confidence_score": 0.5}
]
```

### Archivo de evidencia
- `evidence/roicriiif-fase-4/v4_complete/hotelcastillareal/faq_page/ESTIMATED_faqs_20260528_181927.json`
- `evidence/roicriiif-fase-4/v4_complete/hotelcastillareal/optimization_guide/ESTIMATED_guia_optimizacion_20260528_181927.md`

### ⚠️ CORRECCIONES vs documento original (28-May-2026)

**ERROR 1**: El documento decía "faq_gen usó datos genéricos".
**REALIDAD**: `faq_page` NO se genera con `FAQGenerator` (modules/delivery/generators/faq_gen.py).
Se genera con `conditional_generator._generate_faq_page()` (L710) que recibe `faqs` de
`validated_data.get("faqs", [])`. Si la lista está vacía, genera FAQs default internamente (L723-724).
El `FAQGenerator` tiene scraping con `site_url` pero NO se invoca para faq_page.

**ERROR 2**: El documento decía "indirect_traffic_optimization_gen".
**REALIDAD**: El asset es `optimization_guide` (NO `indirect_traffic_optimization`).
Son assets DIFERENTES en ASSET_CATALOG:
- `optimization_guide`: required_field="metadata", confidence=0.5, priority=REQUIRED
- `indirect_traffic_optimization`: required_field="organic_traffic", confidence=0.4, priority=RECOMMENDED
La propuesta mapea "SEO Local" → `optimization_guide`.

**ERROR 3**: El documento decía "confidence 0.5 = ESTIMATED, modo genérico".
**REALIDAD**: La causa raíz es un MISMATCH DE THRESHOLDS + fórmula de scoring:

### Root Cause VERIFICADA (28-May-2026)

**Cadena completa**:
```
asset_catalog.py:
  faq_page.required_confidence = 0.5, priority = REQUIRED, block_on_failure = False
  optimization_guide.required_confidence = 0.5, priority = REQUIRED, block_on_failure = False

preflight_checks.py:
  required_field (faqs/metadata) tiene baja calidad → WARNING + fallback_action
  → can_proceed = True (block_on_failure=False)

conditional_generator._calculate_confidence_score() (L1621-1652):
  WARNING check con priority=REQUIRED → score = 0.5 (no importa que tenga fallback)
  WARNING check con priority=RECOMMENDED + fallback → score = 0.8

→ faq_page y optimization_guide obtienen confidence_score = 0.5

publication_gates._asset_confidence_gate():
  threshold = 0.7
  0.5 < 0.7 → WARNING
```

**La contradicción fundamental**: el asset_catalog acepta generar con confidence 0.5
(required_confidence=0.5) pero el gate penaliza con threshold 0.7. El sistema aprueba
la generación y luego rechaza el resultado.

**Diferencia con `indirect_traffic_optimization`**: ese asset tiene priority=RECOMMENDED,
así que un WARNING+fallback da 0.8 (≥ 0.7) y PASSE el gate. Es un buen contraejemplo.

### Código relevante

**conditional_generator.py L1621-1652**: `_calculate_confidence_score` — WARNING con REQUIRED=0.5, RECOMMENDED+fallback=0.8

**asset_catalog.py**:
- L80-90: faq_page — required_confidence=0.5, priority=REQUIRED (default)
- L182-191: optimization_guide — required_confidence=0.5, priority=REQUIRED (default)
- L300-310: indirect_traffic_optimization — required_confidence=0.4, priority=RECOMMENDED

**publication_gates.py L698-778**: `_asset_confidence_gate` — threshold hardcoded 0.7

**preflight_checks.py L279-282**: FASE-2 fix — listas con items → ESTIMATED (0.7), vacías → UNKNOWN (0.0)

---

## INVESTIGACIÓN COMPLETADA (28-May-2026)

### Issue #1 — CONFIRMADO ✅

**Root cause**: `asdict()` en `assessment_builder._to_dict()` convierte `SitePresenceReport`
(objeto dataclass con `.results`) a dict plano. `proposal_asset_alignment.py` L209 hace
`hasattr(site_presence_report, 'results')` que es `False` para dict → `presence_lookup = {}`
→ whatsapp_button va a `missing`.

**Fix recomendado**: En `proposal_asset_alignment.py` L207-211, agregar manejo de dict:
```python
if site_presence_report is not None:
    if isinstance(site_presence_report, dict) and site_presence_report.get('presence_status') == 'unknown':
        presence_unknown = True
    elif hasattr(site_presence_report, 'results'):
        for asset_type, result in site_presence_report.results.items():
            presence_lookup[asset_type] = result
    elif isinstance(site_presence_report, dict) and 'results' in site_presence_report:
        # FIX: asdict() convierte SitePresenceReport a dict
        presence_lookup = site_presence_report['results']
```

**Alternativa**: En `assessment_builder.py`, NO incluir `site_presence_report` en `asdict()`.

### Issue #2 — CONFIRMADO con correcciones ✅

**Root cause real**: Mismatch entre required_confidence (0.5) y gate threshold (0.7),
agravado por la fórmula de `_calculate_confidence_score` que penaliza REQUIRED+fallback
con 0.5 en vez de distinguir fallback controlado de fallback genérico.

**Fixes recomendados** (en orden de preferencia):

**Opción A** (mejor): Cambiar priority de REQUIRED → RECOMMENDED para faq_page y
optimization_guide en ASSET_CATALOG. Con RECOMMENDED+fallback, confidence = 0.8 ≥ 0.7.
Justificación: ambos tienen block_on_failure=False y fallback definido, lo cual es
la definición misma de RECOMMENDED.

**Opción B**: Subir required_confidence de 0.5 a 0.7 en ASSET_CATALOG para forzar
que el preflight exija datos de mayor calidad antes de generar. Si los datos no llegan,
el asset no se genera (BLOCKED en vez de WARNING).

**Opción C**: Modificar `_calculate_confidence_score` para que WARNING+fallback
(no importa priority) dé ≥ 0.7. Esto es más amplio pero puede mascarar problemas
reales de calidad de datos.

---

## EVIDENCE DISPONIBLE

### Run FASE-4
```
output\v4_complete
├── v4_complete/
│   ├── v4_complete_report.json                    ← Coherence 0.8262, assets_generated
│   ├── 01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md
│   ├── 02_PROPUESTA_COMERCIAL_*.md                ← Sin "13%", ✅
│   └── hotelcastillareal/
│       └── v4_audit/
│           └── gate_report_*.json                 ← BLOCKED: whatsapp missing
│       └── faq_page/ESTIMATED_faqs_*.json         ← confidence 0.5
│       └── optimization_guide/ESTIMATED_guia_*.md ← confidence 0.5
│       └── whatsapp_conflict_guide/guia_*.md      ← whatsapp CONFLICT
│       └── (otros assets)
│       └── deliveries/
│           └── hotelcastillareal_20260528.zip
```

### Runs anteriores (archives)
```
archives/outputs/castilla real/
├── v4_complete_report.json     ← whatsapp_button en present_in_production ✅
├── v4_complete_report1.json    ← whatsapp_button en present_in_production ✅
├── v4_complete_report2.json    ← whatsapp_button en present_in_production ✅
├── v4_complete_report3.json     ← whatsapp missing ❌ (comparar con FASE-4)
├── v4_complete_report4.json     ← whatsapp missing ❌
├── v4_complete_report5.json     ← whatsapp missing ❌
├── v4_complete_report6.json     ← whatsapp missing ❌
└── v4_complete_report7.json     ← whatsapp missing ❌
```

---

## COMANDOS DE VERIFICACIÓN RÁPIDA

```bash
# Verificar que SitePresenceChecker detecta whatsapp correctamente
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -c "
from modules.asset_generation.site_presence_checker import SitePresenceChecker
r = SitePresenceChecker().check_site('https://www.hotelcastillareal.com/', asset_types=['whatsapp_button'])
print('whatsapp_button status:', r.results['whatsapp_button'].status.value)
"

# Comparar gate_report de run exitoso vs fallido
cd /mnt/c/Users/Jhond/Github/iah-cli
cat archives/outputs/castilla\ real/v4_complete_report.json | python -c "import json,sys; d=json.load(sys.stdin); gates=[g for g in d['phases']['phase_4_publication_gates']['gate_results'] if g['gate_name']=='proposal_asset_alignment']; print(json.dumps(gates[0]['details']['present_in_production'], indent=2) if gates else 'NO GATE')"
cat evidence/roicriiif-fase-4/v4_complete/hotelcastillareal/v4_audit/gate_report_*.json | python -c "import json,sys; d=json.load(sys.stdin); gates=[g for g in d['gate_results'] if g['gate_name']=='proposal_asset_alignment']; print(json.dumps(gates[0]['details']['present_in_production'], indent=2) if gates else 'NO GATE')"
```

---

## RESTRICCIONES DE LA INVESTIGACIÓN

- **NO modificar código** — solo investigar y documentar findings
- **NO ejecutar v4complete** — solo análisis de evidence y código
- **El "13%" artifact** ya está resuelto (no investigar)
- **Sesión nueva** — el contexto se transporta completo, no hay acceso a la sesión anterior

---

## PRÓXIMA SESIÓN (FASE-5 o dedicated fix session)

Una vez la investigación esté completa, se necesitan:
1. Root cause confirmada para ambos issues
2. Opciones de fix (con pros/cons)
3. Recomendación de cuál fix aplicar primero
4. Test que demuestre que el fix resuelve sin regresión