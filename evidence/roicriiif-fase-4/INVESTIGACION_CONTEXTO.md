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
- **v4complete ejecutado**: evidence/roicriiif-fase-4/ —结果是 NOT_READY
- **Gates**: 10/11 passed, 1 BLOCKED (proposal_asset_alignment)
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

### Hipótesis de investigación

1. **faq_page**: El generador `faq_gen` usó datos genéricos (region eje_cafetero) en vez de extraer FAQs del sitio real. El prefijo `ESTIMATED` indica que no hubo extracción real.
   - Verificar: ¿Se ejecutó SitePresenceChecker para detectar servicios/FAQs reales del hotel?
   - Verificar: ¿Hay datos de GBP (Google Business Profile) que contengan FAQs?

2. **optimization_guide**: El generador `indirect_traffic_optimization` también usó datos genéricos.
   - Verificar: ¿El enrich/enrichment phase se ejecutó?
   - Verificar: ¿Hay datos reales de SEO del sitio (meta tags, contenido)?

3. **Confianza 0.5 = "ESTIMATED"**: El prefijo ESTIMATED indica que el asset se generó con suposiciones, no con datos extraídos. Necesario investigar qué activa el modo "ESTIMATED" vs "REAL".

### Código relevante

**preflight_checks.py** (FASE-2 fix, commit 335d534): trata listas como ESTIMATED en confidence scoring

**faq_gen** y **indirect_traffic_optimization_gen**: Generadores que producen contenido genérico cuando no hay datos reales del hotel.

---

## INVESTIGACIÓN REQUERIDA (Nueva Sesión)

### Tarea A: Issue #1 — `whatsapp_button` missing

**Hipótesis**: `verify_proposal_asset_alignment` requiere un objeto `SitePresenceReport` con atributo `.results`, pero `assessment_builder._to_dict()` le pasa un dict donde `.results` es una clave, no un atributo.

**Pasos de investigación**:
1. Leer `proposal_asset_alignment.py` L202-211 completo — verificar si hay lógica para manejar dict `results`
2. Leer `assessment_builder._to_dict()` — confirmar que convierte SitePresenceReport a dict
3. Diseñar fix: o bien (a) no convertir SitePresenceReport a dict, o (b) agregar handling de dict en `verify_proposal_asset_alignment`
4. Testear el fix con test unitario que simule el flujo completo: checker → builder → gate → verify

**Archivos a inspeccionar**:
- `modules/asset_generation/proposal_asset_alignment.py` (L157-240 especialmente)
- `modules/assessment_builder.py` (L260-263)
- `modules/asset_generation/site_presence_checker.py` (L96-104, SitePresenceReport dataclass)

### Tarea B: Issue #2 — Confidence 0.5

**Hipótesis**: Los generadores de faq_page y optimization_guide no reciben datos reales del sitio y operan en modo "ESTIMATED" con suposiciones.

**Pasos de investigación**:
1. Leer los archivos generados (ESTIMATED_faqs_*.json y ESTIMATED_guia_*.md) para ver contenido
2. Investigar qué activa el prefijo ESTIMATED vs contenido real en los generadores
3. Verificar si en runs anteriores de este hotel (archives/) hubo confidence ≥ 0.7
4. Investigar si el enrich phase se ejecutó y qué datos proporcionó

**Archivos a inspeccionar**:
- `evidence/roicriiif-fase-4/v4_complete/hotelcastillareal/faq_page/ESTIMATED_faqs_*.json`
- `evidence/roicriiif-fase-4/v4_complete/hotelcastillareal/optimization_guide/ESTIMATED_guia_*.md`
- `modules/asset_generation/faq_gen.py` (o nombre similar)
- `modules/asset_generation/indirect_traffic_optimization_gen.py` (o nombre similar)
- `archives/outputs/castilla real/v4_complete_report*.json` (buscar runs previos con confidence real)

---

## EVIDENCE DISPONIBLE

### Run FASE-4
```
evidence/roicriiif-fase-4/
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