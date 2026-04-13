---
description: FASE-ASSETS-VALIDACION — Alinear propuesta comercial con assets generados
version: 1.0.0
---

# FASE-ASSETS-VALIDACION: Propuesta → Assets — Cero Desconexiones

**ID**: FASE-ASSETS-VALIDACION
**Objetivo**: Que CADA servicio prometido en la propuesta comercial tenga un asset generado y efectivo
**Dependencias**: FASE-GEO-BRIDGE (bridge debe estar activo para enriquecer assets)
**Duración estimada**: 3-4 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Problema raíz (D4 del AUDIT — CORREGIDO con evidencia real)

La auditoría original decía D4 "IMPACTO MEDIO". La realidad es PEOR:

```
PROMESA EN PROPUESTA            ASSET ESPERADO                  GENERADO?
──────────────────────────────────────────────────────────────────────────
"Google Maps Optimizado"        geo_playbook                    SI  ✅
"Visibilidad en ChatGPT"        indirect_traffic_optimization   SI  ✅
"Busqueda por Voz (AEO)"        voice_assistant_guide           NO  ❌
"SEO Local"                     optimization_guide              SI  ✅
"Boton de WhatsApp"             whatsapp_button                 NO  ❌
"Datos Estructurados"           hotel_schema                    SI  ⚠️ placeholder
"Informe Mensual"               (no existe)                     NO  ❌
```

**3 de 7 servicios prometidos NO generan asset. El cliente paga por algo que NO recibe.**

### Raíz arquitectural

La propuesta template (`propuesta_v6_template.md`) hardcodea los 7 servicios con `✅`.
Pero la generación de assets es **pain-driven**: solo genera assets si `pain detection` detecta un problema específico.

```python
# v4_asset_orchestrator.py línea 220-224
pains = self.pain_mapper.detect_pains(...)
solutions = self.pain_mapper.map_to_solutions(pains)
asset_specs = self._solutions_to_asset_specs(solutions, pains)
```

Si el audit NO detecta `whatsapp_conflict` o `voice_readiness_low` como pain → el asset no se genera.
Pero la propuesta SIEMPRE promete esos servicios. **Desconexión garantizada.**

### Evidencia de amaziliahotel.com

```json
// v4_complete_report.json → assets_generated (10 assets)
[
  "hotel_schema",        // confidence 0.5 WARNING
  "geo_playbook",        // confidence 0.5 WARNING
  "review_plan",         // confidence 0.5 WARNING
  "optimization_guide",  // confidence 0.5 WARNING
  "llms_txt",            // confidence 0.5 WARNING
  "faq_page",            // confidence 0.5 WARNING
  "review_widget",       // confidence 0.5 WARNING
  "analytics_setup_guide",    // confidence 0.5 WARNING
  "indirect_traffic_optimization", // confidence 0.5 WARNING
  "org_schema"           // confidence 0.5 WARNING
]
```

FALTAN: `voice_assistant_guide`, `whatsapp_button`, `monthly_report` (no existe en catálogo).

---

## Tareas

### Tarea 1: Crear asset `monthly_report` en catálogo

**Problema**: La propuesta promete "Informe Mensual" pero NO existe asset ni generador.

**Ubicación**: `modules/asset_generation/asset_catalog.py`

**Nuevo entry**:
```python
"monthly_report": AssetCatalogEntry(
    asset_type="monthly_report",
    template="monthly_report_template.md",
    output_name="{prefix}informe_mensual{suffix}.md",
    required_field="hotel_data",
    required_confidence=0.3,
    fallback="generate_basic_monthly_report",
    block_on_failure=False,
    status=AssetStatus.IMPLEMENTED,
    promised_by=["always"]  # SIEMPRE generar — la propuesta SIEMPRE lo promete
),
```

**Generador**: Crear `modules/asset_generation/monthly_report_generator.py`

**Contenido mínimo del informe mensual**:
- Nombre del hotel + período
- KPIs a monitorear: tráfico web, GBP views, reservas directas, WhatsApp clicks
- Checklist de acciones mensuales
- Sección de "Próximos pasos" basada en los assets entregados
- Disclaimer: métricas requieren configuración de GA4/GSC

**No requiere datos reales** — es una plantilla de seguimiento que el cliente puede usar con sus datos.

---

### Tarea 2: Fix `voice_assistant_guide` — asegurar generación condicional

**Problema**: El asset existe en catálogo como IMPLEMENTED pero NO se genera porque ningún pain lo dispara.

**Archivos**:
- `modules/asset_generation/asset_catalog.py` — agregar `promised_by`
- `modules/asset_generation/conditional_generator.py` — verificar lógica de generación

**Cambios**:

1. En `asset_catalog.py`, actualizar entry de `voice_assistant_guide`:
```python
"voice_assistant_guide": AssetCatalogEntry(
    ...
    promised_by=["low_voice_readiness", "always_aeo"],  # NUEVO: siempre para AEO
),
```

2. Verificar que `_generate_voice_assistant_guide()` produce contenido válido (ya existe, línea 1434 de conditional_generator.py).

3. En el orchestrator o pain_mapper, asegurar que si la propuesta promete AEO, se genere `voice_assistant_guide` aunque no se detecte un pain específico.

---

### Tarea 3: Fix `whatsapp_button` — asegurar generación

**Problema**: `whatsapp_button` está en `_fast_assets` y `_standard_assets` (líneas 57-59 de conditional_generator.py) pero NO aparece en los 10 assets generados.

**Investigar**:
1. Leer `modules/asset_generation/preflight_checks.py` — ¿qué gate lo está bloqueando?
2. Verificar si `whatsapp` data está presente en `validated_data` para amaziliahotel.com
3. Si preflight lo bloquea, ajustar: generar botón básico siempre (el fallback ya existe: `generate_basic_whatsapp`)

**Archivos**:
- `modules/asset_generation/preflight_checks.py`
- `modules/asset_generation/conditional_generator.py` (líneas 354-360)

---

### Tarea 4: Crear mapeo propuesta → asset verificable

**Objetivo**: Código que verifique automáticamente que cada `✅` de la propuesta tiene un asset correspondiente.

**Ubicación**: `modules/asset_generation/proposal_asset_alignment.py` (nuevo)

**API**:
```python
def verify_proposal_asset_alignment(
    proposal_services: List[str],  # Servicios marcados con ✅ en propuesta
    generated_assets: List[Dict],   # assets_generated del report
    asset_catalog: Dict             # ASSET_CATALOG
) -> AlignmentReport:
    """
    Verifica que cada servicio prometido tenga un asset generado.
    
    Returns:
        AlignmentReport con:
        - aligned: servicios con asset presente
        - missing: servicios sin asset (DEBE ser 0 para publication)
        - low_quality: servicios con asset pero confidence < 0.7
    """
```

**Mapeo hardcodeado (fuente de verdad)**:
```python
PROPOSAL_SERVICE_TO_ASSET = {
    "Google Maps Optimizado": "geo_playbook",
    "Visibilidad en ChatGPT": "indirect_traffic_optimization",
    "Busqueda por Voz": "voice_assistant_guide",
    "SEO Local": "optimization_guide",
    "Boton de WhatsApp": "whatsapp_button",
    "Datos Estructurados": "hotel_schema",
    "Informe Mensual": "monthly_report",
}
```

---

### Tarea 5: Integrar verificación en publication gates

**Objetivo**: Si algún servicio prometido NO tiene asset, publication gates debe reflejarlo.

**Archivo**: `modules/quality_gates/publication_gates.py`

Agregar gate #9: `proposal_asset_alignment_gate`:
- Verifica que los 7 servicios de la propuesta tengan assets generados
- Si falta alguno → WARNING (no bloquear, pero alertar)
- Integrar como gate 9 en `run_publication_gates()`

---

## Restricciones

- NO modificar la cadena financiera
- NO alterar los 4 pilares del diagnóstico
- Los assets nuevos deben funcionar sin datos de onboarding (usar plantillas genéricas)
- Mantener backward compat: si no hay datos de voice/whatsapp, generar versión básica
- Tests existentes deben seguir pasando

---

## Tests Obligatorios

| Test | Archivo | Criterio |
|------|---------|----------|
| `test_monthly_report_generates` | `tests/asset_generation/test_monthly_report.py` | Genera contenido válido |
| `test_voice_assistant_guide_generates` | `tests/asset_generation/test_voice_guide_generation.py` | Se genera aunque no haya pain |
| `test_whatsapp_button_generates_basic` | `tests/asset_generation/test_whatsapp_button.py` | Genera botón básico sin datos |
| `test_proposal_alignment_check` | `tests/asset_generation/test_proposal_alignment.py` | Detecta assets faltantes |
| `test_alignment_gate` | `tests/quality_gates/test_proposal_alignment_gate.py` | Gate 9 funciona |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_monthly_report.py tests/asset_generation/test_voice_guide_generation.py tests/asset_generation/test_whatsapp_button.py tests/asset_generation/test_proposal_alignment.py tests/quality_gates/test_proposal_alignment_gate.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Criterios de Completitud (CHECKLIST)

- [x] **7/7 servicios tienen asset**: monthly_report creado, voice_assistant_guide y whatsapp_button generados
- [x] **Mapeo propuesta→asset existe**: `proposal_asset_alignment.py` funcional
- [x] **Gate 9 integrado**: `proposal_asset_alignment_gate` en publication_gates
- [x] **Tests pasan**: Los 5 tests nuevos ejecutan exitosamente
- [x] **Validaciones**: `run_all_validations.py --quick` pasa
- [x] **`dependencias-fases.md` actualizado**: FASE-ASSETS-VALIDACION ✅

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-ASSETS-VALIDACION como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar tareas como completadas
3. **`09-documentacion-post-proyecto.md`**:
   - Sección A: `monthly_report_generator.py`, `proposal_asset_alignment.py`
   - Sección D: "Servicios con asset: 3/7 → 7/7"
