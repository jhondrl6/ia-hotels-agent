# FASE 9: AI/ML Enhancement - Intelligent Disclaimer Generator v2

**ID**: FASE-9-AI-DISCLAIMER
**Objetivo**: Evolucionar disclaimer generator con contexto LLM y improvement steps
**Dependencias**: FASE 8 completada
**Duración estimada**: 2-3 horas
**Skill**: llm-integration, prompt-engineering

---

## Problema Actual

```
Disclaimer actual:
"Este asset fue generado con datos estimados..."

El disclaimer NO dice:
- Qué datos específica faltan
- Qué benchmark se usó
- Cómo mejorar el asset
```

---

## Solución: Contextual AI Disclaimers

```
Tipo: hotel_schema, Confidence: 0.3
Datos faltantes: GBP reviews, photos, ratings
Benchmark usado: Pereira boutique avg

↓

Disclaimer INTELIGENTE:
"""
⚠️ ASSET CON BAJA CONFIANZA (0.3/1.0)

Este schema fue generado usando benchmark regional porque:
• Google Business Profile no tiene datos (0 reviews, 0 fotos)
• Sistema usó promedio de hotels boutique en Pereira como referencia

PARA MEJORAR ESTE ASSET:
1. Completar perfil de Google Business Profile
2. Agregar al menos 10 fotos de alta calidad
3. Solicitar 5+ reseñas a clientes reales

CONFIDENCE ESPERADO DESPUÉS: 0.8+
"""
```

---

## Tareas

### T9A: DisclaimerGeneratorV2
**Archivo**: `modules/providers/disclaimer_generator.py` (modificar)

```python
class IntelligentDisclaimerGenerator:
    def generate(
        asset_type: str,
        confidence: float,
        missing_data: List[str],
        benchmark_used: str,
        improvement_steps: List[str]
    ) -> str:
        """Genera disclaimer contextual con recomendaciones"""
```

### T9B: Integrar con asset_metadata
**Metadato mejorado**:
```json
{
  "disclaimer": "...",
  "missing_data": ["gbp_reviews", "photos"],
  "benchmark_used": "pereira_boutique_avg",
  "improvement_steps": [
    "Agregar 10+ fotos a GBP",
    "Solicitar 5+ reseñas"
  ],
  "confidence_after_fix": 0.85
}
```

### T9C: Improvement Score
```python
def calculate_improvement_score(asset: dict) -> float:
    """
    current: 0.3, after: 0.85 → improvement_score: 0.55
    """
```

---

## Tests Obligatorios

| Test | Criterio |
|------|----------|
| `test_intelligent_disclaimer_content` | Disclaimer menciona datos específicos |
| `test_disclaimer_includes_steps` | Incluye improvement steps |
| `test_improvement_score` | Score se calcula correctamente |

---

## Criterios de Completitud

- [ ] DisclaimerGeneratorV2 implementado
- [ ] Disclaimers incluyen missing_data y improvement_steps
- [ ] improvement_score calculado por asset
- [ ] Tests pasan
