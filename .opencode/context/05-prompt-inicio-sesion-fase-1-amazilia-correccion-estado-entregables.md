# Plan: FASE-1-AMAZILIA-CORRECCION-ESTADO-ENTREGABLES

## Contexto del Problema

El bloque "Estado de los Entregables" (línea 61 de `02_PROPUESTA_COMERCIAL_*.md`) muestra información incorrecta para algunos servicios:

- **Botón de WhatsApp**: se muestra como "⏳ Incluido en su kit" cuando YA EXISTE en producción (whatsapp_status: verified en audit_report.json)
- **Datos Estructurados**: se muestra como "✅ Completo" cuando el site NO tiene schema validado (hotel_schema_valid: false, confidence: unknown)
- **Página de FAQ**: se muestra como "✅ Completo" cuando el site NO tiene FAQ schema (faq_schema_valid: false)

### Causa Raíz

**3 desconexiones encadenadas:**

1. **SitePresenceChecker no alimenta al generador**: El SitePresenceChecker SÍ se invoca DENTRO del gate de publicación (`_proposal_asset_alignment_gate`, publication_gates.py L791-803), y detecta correctamente la presencia de WhatsApp. Sin embargo, esto ocurre DESPUÉS de que la propuesta ya fue generada — main.py NUNCA pasa `site_presence_report` al V4ProposalGenerator. El resultado del gate (present_in_production) nunca se retroalimenta al generador.

2. **Semántica incorrecta**: `_confidence_to_nivel_significado` (v4_proposal_generator.py L794) usa threshold 0.85 para "✅ Completo", mezclando "archivo bien generado" con "verificado en producción"

3. **gate_report se genera DESPUÉS de la propuesta**: La propuesta no tiene acceso al output del gate para saber present_in_production

### Archivos ya modificados parcialmente

El parche anterior en esta sesión tocó `v4_proposal_generator.py` pero NO fue completado:
- `_confidence_to_nivel_significado` fue mejorado con parámetros `present_in_production` y `presence_verified`
- `generate()` recibió el parámetro `site_presence_report`
- `_prepare_template_data()` recibió el parámetro `site_presence_report`
- PERO la cadena de llamadas no se cerró completamente

---

## Tareas Pendientes de Implementar (Opción B completa)

### Tarea 1: Cerrar la cadena de llamadas en v4_proposal_generator.py

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Subtarea 1A**: Completar el call chain de `generate()` → `_prepare_template_data()` → `_generate_asset_quality_table()` → `_confidence_to_nivel_significado()`

Ya existe en el archivo (parcialmente modificado):
- `generate()` tiene parámetro `site_presence_report: Optional[Any] = None` ✅
- `_prepare_template_data()` tiene parámetro `site_presence_report` ✅
- `_confidence_to_nivel_significado()` tiene parámetros `present_in_production` y `presence_verified` ✅

**Falta**:
- `generate()` L212 llama `_prepare_template_data()` sin pasar `site_presence_report` → agregar `site_presence_report=site_presence_report` (NOTA: `generate()` está en L154, la llamada a `_prepare_template_data()` está en L212)
- `_prepare_template_data()` L614 llama `_generate_asset_quality_table()` sin pasar `site_presence_report` → construir `presence_lookup` y pasarlo
- `_generate_asset_quality_table()` construir `presence_lookup` desde `SitePresenceReport` y pasarlo a `_confidence_to_nivel_significado()`

**Hallazgo adicional**: `_prepare_template_data()` (L459) acepta el parámetro `site_presence_report` en su firma pero NUNCA lo usa en el cuerpo del método — es un "half-done patch" donde se añadió la firma sin implementar el wiring.

**Subtarea 1B**: Modificar `_generate_asset_quality_table()` para construir `presence_lookup`

```python
# Construir presence_lookup desde site_presence_report
presence_lookup = {}
if site_presence_report and hasattr(site_presence_report, 'results'):
    for asset_type, result in site_presence_report.results.items():
        presence_lookup[asset_type] = {
            'present_in_production': result.status.value == "exists",
            'presence_verified': True,
        }
```

### Tarea 2: Modificar main.py para pasar site_presence_report al generador

**Archivo**: `main.py`

**Ubicación**: ~L2475-2488 (FASE 3.5: Generación de Propuesta Comercial)

**Cambio**: Antes de llamar `proposal_gen.generate()`, invocar SitePresenceChecker para los 7 asset_types de PROPOSAL_SERVICE_TO_ASSET, y pasar el resultado al generador.

```python
# Después de L2484 (antes de proposal_gen.generate)
from modules.asset_generation.site_presence_checker import SitePresenceChecker
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET

# Solo verificar assets que están en generated_assets (no todos)
generated_types = {a.asset_type for a in asset_result.generated_assets} if asset_result else set()
asset_types_to_check = [at for at in PROPOSAL_SERVICE_TO_ASSET.values() if at in generated_types]

site_presence_report = None
if asset_types_to_check:
    checker = SitePresenceChecker()
    site_presence_report = checker.check_site(args.url, asset_types=asset_types_to_check)

# Modificar la llamada:
proposal_path = proposal_gen.generate(
    ...
    site_presence_report=site_presence_report,  # AGREGAR ESTE PARÁMETRO
)
```

### Tarea 3: Actualizar tests

**Archivo**: `tests/asset_generation/test_proposal_alignment.py`

- Test L43: `"Boton de WhatsApp"` → `"Botón de WhatsApp"` (tilde faltante en 'ó'). **BUG real**: la clave en `PROPOSAL_SERVICE_TO_ASSET` (proposal_asset_alignment.py L23) es `"Botón de WhatsApp"` CON tilde. El test L43 usa `"Boton de WhatsApp"` SIN tilde → **KeyError en runtime**. Esto es un bug independiente del fix de presencia.
- Agregar test para `_confidence_to_nivel_significado` con `present_in_production=True` → "✅ Verificado en sitio"
- Agregar test para `_confidence_to_nivel_significado` con confidence 0.85 y sin presencia → "✅ Completo"

### Tarea 4: Regenerar la propuesta para Amaziliahotel

**Archivos de evidencia**:
- `evidence/fase-1-amazilia-correccion/`
- **Evidencia de sitio real**: WhatsApp confirmado en https://amaziliahotel.com/ (plugin Joinchat v5.2.1, +57 310 401 9049)

**Verificación esperada**:
- Botón de WhatsApp: "✅ Verificado en sitio" / "Ya existe en su web - nosotros lo entregamos"
- Datos Estructurados: "⚠️ Listo para implementar" / "Requiere confirmacion post-firma" (confidence 0.85, sin presencia verificada)
- Página de FAQ: "⚠️ Listo para implementar" / "Requiere confirmacion post-firma" (confidence 0.85, sin presencia verificada)

---

## Archivos Involved

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | Completar call chain con site_presence_report |
| `main.py` | Invocar SitePresenceChecker antes de generar propuesta, pasar site_presence_report |
| `tests/asset_generation/test_proposal_alignment.py` | Fix tilde + nuevos tests |
| `output/v4_complete/02_PROPUESTA_COMERCIAL_20260428_101550.md` | Regenerar tras fix |

---

## Datos de Referencia para Validación

- **gate_report.json**: aligned: 2 (Datos Estructurados 0.85, FAQ 0.85), low_quality: 4, present_in_production: 1 (WhatsApp)
- **audit_report.json**: whatsapp_status: verified, hotel_schema_valid: false, faq_schema_valid: false
- **v4_complete_report.json**: coherence_score: 0.893, 13 assets generados

### Verificación en Sitio Real (2026-04-28)

Confirmado mediante browser_navigate a https://amaziliahotel.com/:

- **Botón de WhatsApp**: ✅ CONFIRMADO — floating button verde (plugin "Joinchat" v5.2.1, Creame WhatsApp Me) en esquina inferior derecha
- **Número**: +57 310 401 9049 (coincide con audit_report.json phone_web)
- **Estado**: botón visible, badge con "1", mensaje de bienvenida "Bienvenido al Hotel Amazilia ¿En qué te podemos ayudar?"
- **Conclusión**: El WhatsApp está 100% operativo en producción. La propuesta que muestra "⏳ Incluido en su kit" es objetivamente incorrecta.

### Hallazgos Adicionales (no documentados en el análisis original)

- **N1 - Half-done patch**: `_prepare_template_data()` (L459) acepta `site_presence_report` pero NUNCA lo usa. El parámetro existe solo en la firma.
- **N2 - Gate funcional pero aislado**: `_proposal_asset_alignment_gate` (L791-803) SÍ invoca SitePresenceChecker correctamente y detecta WhatsApp. El bug es que esta info nunca llega al generador de propuestas.
- **N3 - KeyError en test**: `test_proposal_alignment.py` L43 accede `PROPOSAL_SERVICE_TO_ASSET["Boton de WhatsApp"]` (sin tilde). La clave real es `"Botón de WhatsApp"` (con tilde). El test está roto independientemente del fix de presencia.
- **N4 - Propuesta tiene problemas adicionales**: La propuesta actual tiene 8 blockers de "COP COP" (moneda duplicada en L97, L102, L165-169, L192) y "0% de confianza" (L186) detectados por content_quality gate. Estos son independientes del problema de presencia.

---

## Flujo Deseado (antes → después)

```
ANTES:
  generate(assets_generated=[13 items])
    → _generate_asset_quality_table()
      → confidence 0.85 → "✅ Completo" ← SIN contexto de presencia real

DESPUÉS:
  generate(assets_generated=[13 items], site_presence_report=SitePresenceReport)
    → _generate_asset_quality_table(presence_lookup)
      → WhatsApp: presence exists → "✅ Verificado en sitio"
      → hotel_schema: confidence 0.85, no presence → "⚠️ Listo para implementar"
      → faq_page: confidence 0.85, no presence → "⚠️ Listo para implementar"
```
