# FASE-2: Asset Confidence Enrichment (CONFIDENCE-LOW Co-Bloqueante)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (análisis iterativo + patch)
> **Complejidad**: 🟡 MEDIA

## Contexto previo

FASE-1 completó el fix del gate para que whatsapp_button sea reconocido como present_in_production. Tras FASE-1, proposal alignment debería estar en ~75% (6 aligned de 8 totales). **Sigue bajo threshold de 80%** porque:

- `faq_page`: confidence 0.5 (threshold 0.7)
- `optimization_guide`: confidence 0.5 (threshold 0.7)

Ambos están en el denominador del alignment pero NO cuentan como "satisfied". Necesitamos elevar al menos UNO a ≥0.7 para llegar a ≥87.5% → PASSED.

**Ground truth**: El gate report muestra 2 assets "low_quality" — fueron generados pero con información insuficiente del DOM scraping.

## Objetivo de esta fase

Elevar confidence de al menos UNO de {`faq_page`, `optimization_guide`} a ≥0.7 mediante enriquecimiento de datos DOM o ajuste de scoring, desbloqueando proposal alignment ≥80%.

**Meta preferida**: Elevar AMBOS si es viable en el budget de iteraciones.

### Tareas

- [ ] **T1 — Diagnosticar causa de low confidence**: Para cada asset afectado:
  1. Leer `modules/asset_generation/conditional_generator.py` — entender cómo se calcula confidence
  2. Verificar `asset_generation_report.json` de evidence para cada asset: qué `pain_ids_resolved`, qué datos se usaron, qué generó confidence=0.5
  3. Identificar qué datos DOM faltan (¿FAQ sections sin contenido? ¿Contacto/Local sin metadata?)
  Archivos a inspeccionar:
  - `modules/asset_generation/conditional_generator.py` (confidence calculation)
  - `modules/asset_generation/asset_catalog.py` L80-90 (faq_page config) y L182-192 (optimization_guide config)
  - `evidence/roicriii-fase-6/asset_generation_report.json` (estado actual)

- [ ] **T2 — Enriquecer DOM scraping O ajustar scoring**: Según diagnóstico en T1:
  - **Opción A (preferida)**: Extraer más metadatos del DOM scraping para FAQ/Contacto/Local sections → más datos = más confidence natural
  - **Opción B**: Ajustar scoring en conditional_generator.py para que datos ya-disponibles pesen más apropiadamente
  - **Opción C (fallback)**: Alinear `required_confidence` en asset_catalog.py con el threshold real del gate (0.7), si ambos están en 0.5 pero el gate exige 0.7, hay un gap de configuración
  
- [ ] **T3 — Tests**: 
  - Test unitario que verifique: con datos DOM enriquecidos (mock), confidence de faq_page o optimization_guide ≥ 0.7
  - Test de regresión: confidence de otros assets no debe bajar
  - Ejecutar `pytest tests/ -k "confidence OR asset_catalog OR conditional_gen"` → todos pasan

### Restricciones

- NO modificar site_presence_report ni publication_gates.py (eso fue FASE-1)
- NO ejecutar v4complete (eso es FASE-4)
- Priorizar enriquecimiento real sobre bypass de threshold
- Si required_confidence en catálogo es 0.5 pero gate exige 0.7 → documentar la discrepancia y decidir (subir catálogo o documentar excepción)

### Criterios de completitud

- [ ] Al menos UNO de {faq_page, optimization_guide} con confidence ≥ 0.7 en tests
- [ ] Causa raíz del low confidence identificada y documentada
- [ ] Tests nuevos pasan (≥1)
- [ ] No regresión en confidence de otros assets
- [ ] Cascade de docs actualizada (dependencias-fases.md, REGISTRY.md, 09-doc)
- [ ] `log_phase_completion.py` ejecutado con `--fase FASE-2`

### Próxima sesión

FASE-3: Proposal Semantic Cleanup — eliminar artifact "13% del dolor" de plantilla de propuesta. Esta fase SÍ usa delegate_task.
