# Hallazgo: seo_elements={} en audit_report.json

**Fecha**: 2026-04-08
**Origen**: Investigacion post-FASE-A
**Estado**: Pendiente de fix

---

## Descripcion

`SEOElementsDetector` (creado en FASE-A) funciona correctamente y se ejecuta en el pipeline v4complete, PERO el resultado NO se serializa a `audit_report.json`. El campo vive en memoria pero desaparece al persistir.

## Brecha Exacta

- `modules/auditors/seo_elements_detector.py` (104 lineas) -- Detecta Open Graph, imagenes sin alt, redes sociales. Funciona.
- `modules/auditors/v4_comprehensive.py` linea 404 -- Se ejecuta: `seo_elements = self._run_seo_elements_audit(html_content, url)`
- `modules/auditors/v4_comprehensive.py` linea 500 -- Se pasa al resultado: `seo_elements=seo_elements`
- `modules/auditors/v4_comprehensive.py` `to_dict()` (~linea 188-290) -- **NO serializa `seo_elements`**

## Impacto

- Ejecucion en vivo: **NO hay problema** -- generadores consumen el atributo del objeto directamente via `hasattr()`
- JSON persistido: **SI hay problema** -- `execute` o procesos que carguen analisis previo desde `audit_report.json` ven `seo_elements` ausente/vacio

## Consumidores Confirmados

- `v4_diagnostic_generator.py` -- lee `seo_elements` del objeto
- `alt_text_guide_gen.py`, `og_tags_guide_gen.py`, `social_strategy_guide_gen.py` -- generadores de delivery

## Fix Requerido

Agregar en `V4AuditResult.to_dict()` en `modules/auditors/v4_comprehensive.py` despues de linea ~288 (antes del `return result`):

```python
if self.seo_elements:
    result["seo_elements"] = {
        "open_graph": self.seo_elements.open_graph,
        "imagenes_alt": self.seo_elements.imagenes_alt,
        "redes_activas": self.seo_elements.redes_activas,
        "confidence": self.seo_elements.confidence,
        "notes": self.seo_elements.notes,
        "open_graph_tags": self.seo_elements.open_graph_tags,
        "images_without_alt": self.seo_elements.images_without_alt,
        "social_links_found": self.seo_elements.social_links_found,
    }
```

Ademas agregar `"seo_elements_detection"` a `executed_validators` en la lista ~lineas 453-462.

## Esfuerzo Estimado

~12 lineas de cambio. Bajo riesgo -- solo agrega serializacion, no altera logica.
