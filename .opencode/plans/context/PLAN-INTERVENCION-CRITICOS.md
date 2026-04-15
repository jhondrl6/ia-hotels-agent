# PLAN DE INTERVENCIÓN — Bugs Críticos Post-FASE-RELEASE

**Fecha:** 2026-04-15
**Proyecto:** AMAZILIA-BUGFIX (v4.31.1)
**Origen:** Verificación cruzada FASE-RELEASE vs AUDIT-AMAZILIA-2026-04-14.md

---

## Diagnóstico Causal

Los fixes de código de FASE-DATASOURCE/BUGFIXES/CONTENT-FIXES **sí están aplicados**, pero el v4complete FASE-RELEASE generó outputs con problemas residuales por **3 causas raíz distintas**:

### CAUSA 1: Key mismatch en validated_data (D5, D4 parcial)
- **Orchestrator** (`v4_asset_orchestrator.py:626-627`) pone `rating` y `review_count` en `validated_data["hotel_data"]`
- **Handler review_widget** (`conditional_generator.py:415`) busca `validated_data.get("review_data", {})` — CLAVE INCORRECTA
- Resultado: handler recibe `{}` vacío → `_generate_review_widget({}, "Hotel")` → `not rating` = True → muestra estado honesto
- **Pero** el output muestra ★★★★★ → significa que `validated_data["review_data"]` SÍ existe pero con datos de una ruta anterior (template fallback o cache)

### CAUSA 2: WhatsApp sin número (D4)
- Handler (`conditional_generator.py:360`) busca `validated_data.get("whatsapp")` o `validated_data.get("whatsapp_number")`
- Orchestrator NO pasa campo "whatsapp" — solo `phone_web` y `phone_gbp` en `validated_data["phone_web"]`
- Resultado: `phone` = "" → `_generate_whatsapp_button("", "Hotel")` → HTML con `href="https://wa.me/?text=..."` (sin número)
- El fix D9 puso phone_web en audit_report pero NO se propaga a validated_data["whatsapp"]

### CAUSA 3: monthly_report con nombre "Hotel" (GAP-2)
- Generador (`monthly_report_generator.py:35`) lee `hotel_data.get("name")`
- Orchestrator pasa `hotel_data` desde `audit_result.schema.properties.get("name")`
- Si schema no tiene `name` (el sitio no tiene schema.org), el dict queda con `"name": None`
- Generador hace `hotel_data.get("name") or hotel_data.get("nombre", "Hotel")` → fallback a "Hotel"
- **El sitio amaziliahotel.com NO tiene schema.org** (audit lo confirmó: 0 bloques JSON-LD)
- El nombre real "Amaziliahotel" está en el title tag, no en schema

### CAUSA 4: Propuesta "No generado" (D7)
- `main.py:2375` verifica `Path(asset.path).exists()` para mostrar ✅/❌
- Pero la propuesta se genera ANTES de los assets (documentos principales primero)
- La propuesta usa datos del orchestrator que reporta `generated_assets` pero el check de `asset.path` usa rutas que pueden no existir si la generación falló silenciosamente
- Assets marcados ❌: voice_assistant_guide, whatsapp_button, monthly_report — los 3 pueden fallar por Causas 1-3

---

## Fases de Intervención

### FASE-FIX-A: Data Pipeline Mismatch (CRITICAL)
**Prioridad:** P1 — bloquea D5, D4, GAP-2
**Archivos:** `v4_asset_orchestrator.py`, `conditional_generator.py`

#### Fix A1: review_data key mismatch (D5)
- **Archivo:** `conditional_generator.py:415`
- **Cambio:** `validated_data.get("review_data", {})` → `validated_data.get("hotel_data", {})`
- **Verificación:** Los datos de rating/review_count están en hotel_data (orchestrator línea 626-627)
- **Impacto:** Review widget usará rating=0 → mostrará estado honesto "Aún no hay reseñas"

#### Fix A2: WhatsApp phone propagation (D4)
- **Archivo:** `v4_asset_orchestrator.py` en `_extract_validated_fields()`
- **Cambio:** Agregar `validated_data["whatsapp"] = validated_data.get("phone_web", "")` después de línea 649
- **Alternativa:** Cambiar handler en `conditional_generator.py:360` para buscar `phone_web` además de `whatsapp`
- **Verificación:** Si phone_web="+57 3104019049" → wa.me/573104019049

#### Fix A3: monthly_report hotel name (GAP-2)
- **Archivo:** `v4_asset_orchestrator.py` en `_extract_validated_fields()`
- **Cambio:** Usar `audit_result.schema.name` (del title tag) como fallback cuando schema.properties.name es None
- **O bien:** `monthly_report_generator.py` — buscar también en `hotel_data.get("title")` o `hotel_data.get("url")` para extraer nombre
- **Verificación:** Monthly report debe decir "Amaziliahotel" no "Hotel"

### FASE-FIX-B: Propuesta Asset Status (HIGH)
**Prioridad:** P2 — afecta credibilidad comercial
**Archivos:** `main.py`

#### Fix B1: Propuesta asset status check (D7)
- Investigar por qué `Path(asset.path).exists()` da False para assets que sí se generaron
- Posible causa: `asset.path` es None o la ruta no coincide con el output real
- Verificar: `asset_result.generated_assets` contiene los paths correctos

### FASE-FIX-C: WhatsApp number extraction (MEDIUM)
**Prioridad:** P3 — depende de Fix A2
**Archivos:** `conditional_generator.py`

#### Fix C1: Clean phone number for wa.me
- El número "+57 3104019049" debe limpiarse a "573104019049" para wa.me
- Actualmente: `wa.me/+57 3104019049` (INCORRECTO — el + y espacios rompen la URL)
- Necesario: `wa.me/573104019049` (solo dígitos)

---

## Orden de Ejecución

```
FASE-FIX-A (data pipeline) → fix A1, A2, A3
    ↓
FASE-FIX-B (propuesta) → fix B1
    ↓
FASE-FIX-C (whatsapp clean) → fix C1
    ↓
Tests de regresión
    ↓
Verificación offline (grep outputs)
    ↓
Post-documentación
```

## Criterios de Éxito

| Hallazgo | Criterio | Verificación |
|----------|----------|-------------|
| D5 | Review widget sin ★★★★★ si rating=0 | grep ★★★★★ en output más reciente = 0 |
| D4 | WhatsApp con wa.me/NÚMERO real | grep wa.me/57 en output más reciente |
| GAP-2 | Monthly report dice "Amaziliahotel" | grep "Hotel": Hotel = 0 matches |
| D7 | Propuesta sin ❌ para assets existentes | grep "No generado" = 0 |

## Conflictos de Archivos

| Archivo | Fases que lo tocan |
|---------|-------------------|
| conditional_generator.py | FIX-A (A1, A3), FIX-C |
| v4_asset_orchestrator.py | FIX-A (A2, A3) |
| main.py | FIX-B |

**Overlap: conditional_generator.py en FIX-A y FIX-C** — ejecutar secuencialmente.

---

*Plan creado: 2026-04-15 por análisis post-FASE-RELEASE*
