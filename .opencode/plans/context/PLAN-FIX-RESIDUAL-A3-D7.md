# PLAN FIX RESIDUAL — A3 + D7 Post-Verificación E2E

**Fecha:** 2026-04-15  
**Origen:** Verificación v4complete post-PLAN-INTERVENCION-CRITICOS  
**Ejecución previa:** FASE-INTERVENCION (subagent) — 3/5 fixes verificados OK  

---

## Estado de Fixes Anteriores

| Fix | Criterio | Estado E2E |
|-----|----------|------------|
| A1 (review_data key) | Sin ★★★★★ fake | ✅ RESUELTO |
| A2 (whatsapp propagation) | wa.me/NUMERO limpio | ✅ RESUELTO |
| A3 (hotel name fallback) | Monthly report = "Amaziliahotel" | ❌ NO RESUELTO |
| B1 (asset path check) | Propuesta sin ❌ | ⚠️ PARCIAL |
| C1 (wa.me clean URL) | Solo dígitos en URL | ✅ RESUELTO |

---

## DIAGNÓSTICO A3: Monthly Report "Hotel" Genérico

### Causa Raíz (2 bugs independientes)

**Bug A3.1 — Fix dentro de bloque condicional que nunca ejecuta:**

```python
# v4_asset_orchestrator.py _extract_validated_fields()

if audit_result and audit_result.schema and audit_result.schema.properties:  # ← L18
    props = audit_result.schema.properties
    validated_data["hotel_data"] = { ... }      # ← hotel_data se crea AQUÍ
    
    # FIX-A3 está AQUÍ adentro:
    if not validated_data["hotel_data"].get("name") and audit_result.metadata:
        title_name = getattr(audit_result.metadata, 'title', None)
        if title_name:
            validated_data["hotel_data"]["name"] = title_name
```

**Problema:** `audit_result.schema.properties` es `{}` (dict vacío).  
En Python: `if {}:` → `False`.  
**Resultado:** Todo el bloque se salta. `hotel_data` NUNCA se crea.  
El fallback A3 nunca tiene oportunidad de ejecutarse.

**Bug A3.2 — Fuente de datos vacía (metadata.title = ""):**

```json
"metadata": {"title": "", "cms_detected": "wordpress", ...}
```

El título real "Amazilia | Hotel campestre en Pereira" está en el HTML `<title>`,  
pero `audit_result.metadata.title` es string vacío.  
Incluso si el fix estuviera fuera del bloque, `getattr(metadata, 'title', None)` → `""` (falsy) → no se asigna.

### Fuentes de nombre disponibles en audit_result

| Fuente | Valor | ¿Disponible sin schema? |
|--------|-------|------------------------|
| `audit_result.hotel_name` | "Amaziliahotel" | ✅ SÍ (campo required del dataclass) |
| `audit_result.gbp.name` | "Amazilia Hotel Campestre" | ✅ SÍ |
| `audit_result.metadata.title` | "" | ✅ SÍ (pero vacío en este caso) |
| `audit_result.schema.properties.name` | N/A (properties vacío) | ❌ NO |

### Data Flow Actual (roto)

```
audit_result → _extract_validated_fields()
  → schema.properties = {} (falsy)
  → SKIP: if schema.properties:
  → hotel_data NUNCA se crea
  → handler: validated_data.get("hotel_data", {}) → {}
  → generator: hotel_data.get("name") → None → fallback "Hotel"
```

### Data Flow Correcto (deseado)

```
audit_result → _extract_validated_fields()
  → hotel_data = {} (SIEMPRE crear)
  → if schema.properties: enriquecer con datos del schema
  → if not hotel_data.get("name"): fallback desde hotel_name o gbp.name
  → handler: validated_data.get("hotel_data", {}) → {name: "Amaziliahotel", ...}
  → generator: hotel_data.get("name") → "Amaziliahotel"
```

---

## DIAGNÓSTICO D7: Propuesta ❌ en Assets Existentes

### Causa Raíz

**El propuesta usa `asset_plan` (10 items), NO `asset_result.generated_assets` (12 items).**

Cadena causal:

1. `main.py L2049`: `asset_plan = pain_mapper.generate_asset_plan(detected_pains, ...)` → 10 assets
2. `main.py L2193`: `assets_for_quality = [{"asset_type": spec.asset_type, ...} for spec in asset_plan]` → 10 items
3. `main.py L2204`: `proposal_gen.generate(...)` recibe `asset_plan=asset_plan`
4. `v4_proposal_generator.py L679`: `_generate_asset_quality_table(assets_for_quality)` itera sobre `PROPOSAL_SERVICE_TO_ASSET`
5. Mapeo busca asset_type en `asset_lookup` (construido de `assets_for_quality`)
6. 3 servicios no encontrados → "❌ No generado"

### Assets que faltan en asset_plan pero SÍ se generan

| Asset | ¿En pain_map? | ¿En asset_plan? | ¿En ASSET_CATALOG promised_by="always"? | ¿Generado? |
|-------|---------------|-----------------|----------------------------------------|------------|
| voice_assistant_guide | ❌ NO | ❌ NO | ? pendiente verificar | ✅ SÍ |
| whatsapp_button | ✅ SÍ (pain: no_whatsapp_visible) | ❌ NO (pain no detectado: WhatsApp verificado) | ? pendiente verificar | ✅ SÍ |
| monthly_report | ❌ NO | ❌ NO | ? pendiente verificar | ✅ SÍ |

**Razón por la que se generan:** `v4_asset_orchestrator.py` L29-55 agrega assets de `ASSET_CATALOG` con `promised_by=["always"]` DESPUÉS de los pain-mapped. Pero `main.py` pasa `asset_plan` (solo pain-mapped) a la propuesta.

### Verificación pendiente

```python
# Verificar cuáles tienen promised_by="always" en ASSET_CATALOG
for asset_type in ['voice_assistant_guide', 'whatsapp_button', 'monthly_report']:
    entry = ASSET_CATALOG.get(asset_type)
    print(f"{asset_type}: promised_by={getattr(entry, 'promised_by', 'N/A')}")
```

---

## FIX A3: Reestructurar `_extract_validated_fields()`

### Archivo
`modules/asset_generation/v4_asset_orchestrator.py` — método `_extract_validated_fields()`

### Cambio 1: SIEMPRE crear hotel_data (mover fuera del if)

```python
# ANTES (L17-40):
if audit_result and audit_result.schema and audit_result.schema.properties:
    props = audit_result.schema.properties
    validated_data["hotel_data"] = { ... }
    # FIX-A3 aquí adentro...

# DESPUÉS:
validated_data["hotel_data"] = {}  # SIEMPRE crear

if audit_result and audit_result.schema and audit_result.schema.properties:
    props = audit_result.schema.properties
    validated_data["hotel_data"].update({
        "name": props.get("name"),
        "description": props.get("description"),
        # ... resto de campos
    })
```

### Cambio 2: Fallback name desde hotel_name (fuente correcta)

```python
# ANTES (L37-40):
if not validated_data["hotel_data"].get("name") and audit_result.metadata:
    title_name = getattr(audit_result.metadata, 'title', None)
    if title_name:
        validated_data["hotel_data"]["name"] = title_name

# DESPUÉS (orden de prioridad):
if not validated_data["hotel_data"].get("name"):
    # Fuente 1: hotel_name del audit (siempre disponible)
    if audit_result and getattr(audit_result, 'hotel_name', None):
        validated_data["hotel_data"]["name"] = audit_result.hotel_name
    # Fuente 2: GBP name  
    elif audit_result and audit_result.gbp:
        gbp_name = getattr(audit_result.gbp, 'name', None)
        if gbp_name:
            validated_data["hotel_data"]["name"] = gbp_name
    # Fuente 3: metadata title (último recurso)
    elif audit_result and audit_result.metadata:
        title_name = getattr(audit_result.metadata, 'title', None)
        if title_name:
            validated_data["hotel_data"]["name"] = title_name
```

### Cambio 3: Asegurar campos mínimos en hotel_data siempre

```python
# Después del if schema.properties block, ASEGURAR que hotel_data tenga campos mínimos:
if not validated_data["hotel_data"].get("url") and audit_result:
    validated_data["hotel_data"]["url"] = getattr(audit_result, 'url', '')
```

### Impacto esperado

- Si `schema.properties` tiene datos → se usan (comportamiento actual OK)
- Si `schema.properties` está vacío → hotel_data se crea vacío, luego se enriquece con `hotel_name`
- Monthly report recibe `{name: "Amaziliahotel"}` → muestra "Amaziliahotel" no "Hotel"
- Otros assets (llms_txt, geo_playbook, hotel_schema) también se benefician

### Riesgos y edge cases

| Escenario | Comportamiento | ¿Es OK? |
|-----------|---------------|----------|
| Schema vacío + hotel_name vacío | Fallback a "Hotel" (default del generator) | ✅ SÍ — es el último recurso |
| Schema vacío + hotel_name presente | Usa hotel_name | ✅ SÍ — fix principal |
| Schema con name | Usa schema.name (comportamiento actual) | ✅ SÍ — sin cambio |
| audit_result es None | hotel_data = {} → generators usan defaults | ✅ SÍ — backward compat |
| Mock tests con spec=Dataclass | getattr() maneja AttributeError | ✅ SÍ — fix anterior A1 usa getattr |

---

## FIX D7: Propuesta usa generated_assets, no asset_plan

### Archivo
`main.py` — sección de generación de propuesta (~L2190-2215)

### Cambio 1: Construir assets_for_quality desde asset_result.generated_assets

```python
# ANTES (L2191-2201):
_CONFIDENCE_TO_SCORE = {"verified": 0.8, "estimated": 0.6, "conflict": 0.3, "unknown": 0.0}
assets_for_quality = [
    {
        "asset_type": spec.asset_type,
        "confidence_score": _CONFIDENCE_TO_SCORE.get(
            spec.confidence_level.value if hasattr(spec.confidence_level, 'value') else str(spec.confidence_level).lower(),
            0.0
        ),
    }
    for spec in asset_plan
]

# DESPUÉS:
# Usar asset_result.generated_assets si está disponible (tiene TODOS los assets generados)
# Fallback a asset_plan si asset_result no está disponible
if asset_result and asset_result.generated_assets:
    assets_for_quality = [
        {
            "asset_type": a.asset_type,
            "confidence_score": a.confidence_score if hasattr(a, 'confidence_score') else 0.0,
        }
        for a in asset_result.generated_assets
    ]
else:
    # Fallback: usar asset_plan (comportamiento anterior)
    _CONFIDENCE_TO_SCORE = {"verified": 0.8, "estimated": 0.6, "conflict": 0.3, "unknown": 0.0}
    assets_for_quality = [
        {
            "asset_type": spec.asset_type,
            "confidence_score": _CONFIDENCE_TO_SCORE.get(
                spec.confidence_level.value if hasattr(spec.confidence_level, 'value') else str(spec.confidence_level).lower(),
                0.0
            ),
        }
        for spec in asset_plan
    ]
```

### Impacto esperado

- Propuesta muestra 12/12 assets (no 10/12)
- voice_assistant_guide, whatsapp_button, monthly_report aparecen con su confidence_score real
- Los que tienen confidence >= 0.7 → "✅ Completo"
- Los que tienen confidence < 0.7 → "⚠️ Requiere datos" o "🔧 En desarrollo"
- Gate 9 (proposal_asset_alignment) ya pasa — esto es solo visual

### Riesgos

| Escenario | Comportamiento | ¿Es OK? |
|-----------|---------------|---------|
| asset_result es None (error en generación) | Fallback a asset_plan | ✅ SÍ |
| asset_result.generated_assets vacío | Fallback a asset_plan | ✅ SÍ |
| Asset con confidence_score bajo | Muestra "🔧 En desarrollo" en vez de ❌ | ✅ SÍ — más informativo |
| Tests que mockean propuesta | Puede requerir mock de asset_result | ⚠️ Verificar tests |

---

## Secuencia de Ejecución

```
1. Verificar ASSET_CATALOG promised_by="always" (confirmar hipótesis D7)
   ↓
2. FIX A3: Reestructurar _extract_validated_fields() en orchestrator
   ↓
3. FIX D7: Cambiar assets_for_quality en main.py
   ↓
4. Tests de regresión:
   ./venv/Scripts/python.exe -m pytest tests/asset_generation/ tests/commercial_documents/ -v --tb=short
   ↓
5. Verificación offline (sin v4complete):
   - grep "hotel_data" orchestrator.py → verificar estructura
   - grep "assets_for_quality" main.py → verificar usa generated_assets
   - Test manual: importar MonthlyReportGenerator y generar con {name: "Amaziliahotel"}
   ↓
6. Documentación: log_phase_completion.py + Sección E checklist
```

## Verificación (sin v4complete)

No ejecutar v4complete en esta fase — es FIX, no RELEASE. Verificar con:

```bash
# 1. Syntax check
./venv/Scripts/python.exe -m py_compile modules/asset_generation/v4_asset_orchestrator.py
./venv/Scripts/python.exe -m py_compile main.py

# 2. Regression tests
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_conditional_generator.py -v --tb=short
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -v --tb=short

# 3. Unit test para A3: verificar hotel_data se crea sin schema
./venv/Scripts/python.exe -c "
from modules.asset_generation.v4_asset_orchestrator import V4AssetOrchestrator
# Mock test: schema.properties vacío + hotel_name presente
# Verificar que hotel_data['name'] == hotel_name
"

# 4. Unit test para D7: verificar propuesta incluye todos los generated_assets
./venv/Scripts/python.exe -c "
# Simular: asset_result con 12 generated_assets
# Verificar que assets_for_quality tiene 12 items, no 10
"
```

v4complete se ejecutará en FASE-RELEASE (siguiente ciclo).

---

*Plan creado: 2026-04-15 10:45 — Post-verificación E2E amaziliahotel.com*
