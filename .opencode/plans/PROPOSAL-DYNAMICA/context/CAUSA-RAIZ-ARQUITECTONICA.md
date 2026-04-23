# Contexto: Causa Raíz Arquitectónica — Propuesta Estática vs Pains Dinámicos

**Fecha**: 2026-04-23  
**Proyecto**: iah-cli v4.34.0  
**Estado**: Documentado — Pendiente FASE futura

---

## Resumen

En iah-cli v4.34.0 se corrigió el síntoma inmediato: FAQ y Open Graph ahora aparecen en la propuesta comercial. Sin embargo, la causa raíz arquitectónica **no fue resuelta**: el generador de propuestas sigue creando servicios desde un diccionario estático, no desde los pains detectados dinámicamente.

---

## Anatomía del Problema

### Capa 1: Detección (pain_solution_mapper.py)

```
detect_pains() → ~20 pains dinámicos
  - no_schema_hotel
  - no_open_graph
  - no_faq_page
  - low_organic_visibility
  - no_analytics
  - etc.
```

Detecta qué problemas tiene el hotel. No tiene límite fijo.

### Capa 2: Promesa (PROPOSAL_SERVICE_TO_ASSET)

```python
PROPOSAL_SERVICE_TO_ASSET = {
    "Google Maps Optimizado": "geo_optimized",
    "SEO Local": "local_seo",
    "Botón de WhatsApp": "whatsapp_button",
    "Datos Estructurados": "org_schema",
    "Informe Mensual": "monthly_report",
    "Página de FAQ": "faq_page",           # agregado v4.34.0
    "Meta Tags Sociales (Open Graph)": "open_graph",  # agregado v4.34.0
}
```

Diccionario **estático** de 7 servicios. No reacciona a lo que detecta `pain_solution_mapper`.

### Capa 3: Presentación (propuesta_v6_template.md)

Tiene **dos tablas**:

1. **Tabla principal** (líneas ~44-50): texto markdown hardcodeado con filas fijas de servicios. Corregida de 5→7 filas en v4.34.0, pero sigue siendo **estática**.

2. **Tabla secundaria** (`${asset_quality_table}`): generada dinámicamente por `_generate_asset_quality_table()` en `v4_proposal_generator.py`, iterando sobre `PROPOSAL_SERVICE_TO_ASSET`.

### Problema Concreto

Si un hotel tiene 12 pains detectados, la propuesta mostrará máximo 7 servicios (el diccionario). Si el diccionario tiene un servicio que el hotel no necesita, igualmente se ofrece.

**Ejemplo**: Hotel sin brechas de SEO pero con brechas de IA. La propuesta ofreció SEO Local de todas formas porque está en el diccionario.

---

## Impacto

- **Desalineamiento persistente**: La propuesta no refleja la realidad del diagnóstico.
- **Sobre-promesa**: Se ofrecen servicios que el hotel no necesita.
- **Sub-promoesa**: Se omiten servicios que el hotel sí necesita pero no están en el diccionario.
- **Escalabilidad**: Cada nuevo asset requiere actualizar manualmente el diccionario y el template.

---

## Solución Arquitectónica (FASE Futura)

### Opción A: Generación Dinámica desde Pain Detection

Refactorizar `v4_proposal_generator.py` para que la propuesta se genere iterando sobre `pain_solution_mapper.detect_pains()` en vez de `PROPOSAL_SERVICE_TO_ASSET`:

```python
# En vez de:
for service_name, asset_id in PROPOSAL_SERVICE_TO_ASSET.items():
    # generar fila estática

# Debería ser:
for pain in pain_solution_mapper.detect_pains(audit_result):
    if pain.has_solution():
        asset_id = pain.solution_asset_id
        service_name = pain.solution_service_name
        # generar fila dinámica
```

**Pros**: La propuesta siempre refleja exactamente los problemas detectados.
**Cons**: Requiere refactor significativo. Pérdida de control editorial sobre qué servicios se ofrecen.

### Opción B: Híbrido (Mantener Diccionario + Validación Dinámica)

1. Mantener `PROPOSAL_SERVICE_TO_ASSET` como whitelist de servicios vendibles.
2. Validar que cada servicio en la propuesta corresponde a un pain detectado.
3. Si un servicio del diccionario no tiene pain correspondiente, marcarlo como "opcional" o no incluirlo.
4. Si un pain detectado no tiene servicio en el diccionario, generar warning.

**Pros**: Más conservador. Compatible con modelo comercial actual.
**Cons**: No resuelve sobre-promesa si el diccionario tiene servicios innecesarios.

### Opción C: Desacoplar Template de Diccionario (Elegida)

1. Crear `SERVICE_CATALOG` — catálogo independiente de todos los servicios vendibles con metadatos (service_name, asset_type, pain_id, description).
2. El generador consulta `pain_solution_mapper` para detectar pains, luego consulta `SERVICE_CATALOG` para mapear pains a servicios.
3. El template recibe la lista de servicios dinámicamente y renderiza la tabla automáticamente.
4. `PROPOSAL_SERVICE_TO_ASSET` se mantiene para backwards compatibility de gates de publicación (verificación post-generación).

**Pros**: Máxima flexibilidad. Agregar servicios futuros solo requiere actualizar `SERVICE_CATALOG`. Backwards compatible.
**Cons**: Requiere reescribir la lógica de presentación completamente.

---

## Dependencias para FASE Futura

- Requiere entender completamente `pain_solution_mapper.detect_pains()` y su relación con `PROPOSAL_SERVICE_TO_ASSET`.
- Requiere revisión del modelo comercial: ¿cuáles servicios son "core" (siempre se ofrecen) vs "add-on" (dinámicos)?
- Los gates de publicación (`proposal_asset_alignment`) necesitan actualizarse para reflejar el nuevo flujo.

---

## Referencias

- Plan original: `.opencode/plans/README.md`
- Código relevante:
  - `modules/commercial_documents/v4_proposal_generator.py`
  - `modules/commercial_documents/pain_solution_mapper.py`
  - `modules/asset_generation/proposal_asset_alignment.py`
  - `modules/commercial_documents/templates/propuesta_v6_template.md`
- Tests: `tests/asset_generation/test_proposal_alignment.py`
- Skills relacionadas: `iah-cli-plan-vs-reality-check`, `iah-cli-post-implementation-e2e-verification`

---

## Changelog

| Fecha | Cambio |
|-------|--------|
| 2026-04-23 | Documentado tras FASE-RELEASE-4.34.0. Causa raíz arquitectónica pendiente de resolución en FASE futura. |
| 2026-04-23 | AUDITORÍA PLAN: Duplicación de `_generate_asset_quality_table` (líneas 654 y 1084) identificada. Plan actualizado para eliminar en FASE-CAUSAL-REFACTOR. E2E v4complete movido exclusivamente a FASE-RELEASE (costos API). |
| 2026-04-23 | REVISIÓN PRE-EJECUCIÓN: Opcion C corregida para reflejar que PROPOSAL_SERVICE_TO_ASSET se mantiene (backwards compatibility). Agregado test_proposal_dynamic.py como criterio de VALIDATE. |
