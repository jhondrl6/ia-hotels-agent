---
description: FASE-CONFIDENCE-DISCLOSURE — Transparencia de calidad de assets al cliente
version: 1.0.0
---

# FASE-CONFIDENCE-DISCLOSURE: Transparencia de Calidad en Propuesta

**ID**: FASE-CONFIDENCE-DISCLOSURE
**Objetivo**: Que la propuesta comercial informe al cliente sobre la calidad/confianza de cada asset entregado
**Dependencias**: FASE-ASSETS-VALIDACION (necesita mapeo propuesta→asset funcional)
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Problema (R9 del AUDIT)

```
R9: Disclaimer de confianza en propuesta — IMPACTO BAJO (reevaluado: IMPACTO ALTO)

La propuesta NO menciona que los 10 assets tienen WARNING + confidence 0.50.
El cliente recibe assets marcados como "listos para usar" pero con calidad incierta.
```

**Dimensión real del problema**: Si un cliente implementa un asset con confidence 0.5 y no funciona, pierde confianza en TODO el servicio. Un disclaimer honesto protege la relación comercial.

### Ejemplo concreto

El `hotel_schema` entregado dice `name: "Hotel"` (placeholder). Si el cliente lo instala:
- Google lo rechaza por datos incompletos
- El cliente culpa al servicio
- No renueva, no refiere

**Mejor**: Decir "Datos estructurados — Nivel básico (requiere completar con datos del hotel)" que entregar un schema vacío como si fuera completo.

---

## Tareas

### Tarea 1: Agregar sección de calidad de assets en propuesta

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md`

**Nueva sección** (después de la tabla de servicios, antes de la inversión):

```markdown
### 📋 Estado de los Entregables

Cada entregable incluye un nivel de preparación:

| Entregable | Nivel | Qué significa |
|------------|-------|---------------|
| Google Maps Optimizado | ✅ Completo | Listo para implementar |
| Visibilidad en ChatGPT | ✅ Completo | Guía con pasos específicos |
| Busqueda por Voz | ✅ Completo | Checklist por plataforma |
| SEO Local | ✅ Completo | Guía con auditoría incluida |
| Boton de WhatsApp | ⚠️ Requiere datos | Necesitamos su número de WhatsApp |
| Datos Estructurados | ⚠️ Requiere datos | Necesitamos datos del hotel |
| Informe Mensual | ✅ Plantilla | Plantilla lista, métricas requieren GA4 |
```

Los niveles se calculan automáticamente desde `confidence_score` del asset correspondiente:
- confidence >= 0.7 → "✅ Completo"
- 0.4 <= confidence < 0.7 → "⚠️ Requiere datos"
- confidence < 0.4 → "🔧 En desarrollo"

---

### Tarea 2: Generar tabla dinámica desde confidence scores

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Cambios**:

1. Recibir `assets_generated` (lista del report) como parámetro adicional
2. Mapear cada servicio de la propuesta a su asset (usar `PROPOSAL_SERVICE_TO_ASSET` de FASE-ASSETS-VALIDACION)
3. Lookup confidence_score de cada asset
4. Generar la tabla de estado dinámicamente

**Código conceptual**:
```python
def _generate_asset_quality_table(self, assets_generated: List[Dict]) -> str:
    """Genera tabla de calidad de assets para la propuesta."""
    rows = []
    for service, asset_type in PROPOSAL_SERVICE_TO_ASSET.items():
        asset = next((a for a in assets_generated if a["asset_type"] == asset_type), None)
        if asset:
            confidence = asset.get("confidence_score", 0)
            if confidence >= 0.7:
                nivel = "✅ Completo"
            elif confidence >= 0.4:
                nivel = "⚠️ Requiere datos"
            else:
                nivel = "🔧 En desarrollo"
        else:
            nivel = "❌ No generado"
        rows.append(f"| {service} | {nivel} |")
    return "\n".join(rows)
```

---

### Tarea 3: Tests

**Archivo**: `tests/commercial_documents/test_proposal_confidence_disclosure.py`

**Casos**:
1. `test_proposal_includes_quality_table` — la propuesta generada incluye la tabla de calidad
2. `test_quality_table_reflects_real_confidence` — si hotel_schema tiene confidence 0.5, muestra "⚠️ Requiere datos"
3. `test_missing_asset_shows_not_generated` — si un asset falta, muestra "❌ No generado"

---

## Restricciones

- NO modificar cálculos financieros
- La sección de calidad NO debe asustar al cliente — ser honesto pero orientado a solución
- Mantener tono de la propuesta (español latino, directo, comercial)
- Backward compatible: si no hay assets_generated, generar tabla con "Pendiente" en todos

---

## Tests Obligatorios

| Test | Archivo | Criterio |
|------|---------|----------|
| `test_proposal_includes_quality_table` | `tests/commercial_documents/test_proposal_confidence_disclosure.py` | PASA |
| `test_quality_table_reflects_real_confidence` | `tests/commercial_documents/test_proposal_confidence_disclosure.py` | PASA |
| `test_missing_asset_shows_not_generated` | `tests/commercial_documents/test_proposal_confidence_disclosure.py` | PASA |

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tabla de calidad en propuesta**: Template actualizado con sección de estado
- [ ] **Generación dinámica**: Tabla se genera desde confidence scores reales
- [ ] **Tests pasan**: Los 3 tests ejecutan exitosamente
- [ ] **`dependencias-fases.md` actualizado**: FASE-CONFIDENCE-DISCLOSURE ✅

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-CONFIDENCE-DISCLOSURE como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar tareas como completadas
3. **`09-documentacion-post-proyecto.md`**:
   - Sección B: `propuesta_v6_template.md` modificado, `v4_proposal_generator.py` modificado
   - Sección D: "Confidence disclosure: NO → SI"
