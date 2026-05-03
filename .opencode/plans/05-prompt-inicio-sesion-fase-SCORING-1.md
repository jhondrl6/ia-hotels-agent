# 05-prompt-inicio-sesion-fase-SCORING-1.md

> **FASE:** FASE-SCORING-1
> **Objetivo:** Agregar funciones `_build_scoring_breakdown()` y `_build_excluded_factors_section()` en `v4_diagnostic_generator.py`
> **Contexto previo:** Ninguno (primera fase)

---

## TAREAS

### 1. Investigar código existente

- Lee `modules/commercial_documents/v4_diagnostic_generator.py` líneas 149-224 para entender las funciones `calcular_score_*()` y los diccionarios `CHECKLIST_*`.
- Lee la función `_prepare_template_data()` para ver cómo se preparaban los datos para el template (buscar en el archivo con `def _prepare_template_data`).

### 2. Implementar `_build_scoring_breakdown(pilar, elementos)`

En `v4_diagnostic_generator.py`, después de las funciones `calcular_score_*()`, agrega:

```python
def _build_scoring_breakdown(pilar: str, elementos: dict) -> str:
    """Retorna string con breakdown del score usando CHECKLIST_* del pilar.
    
    El score se calcula INTERNAMENTE desde el checklist (calcular_score_*())
    para garantizar que el breakdown sea matemáticamente consistente:
    cada item True contribuye su peso exacto al score mostrado.
    
    **IMPORTANTE — Divergencia GEO**: El score mostrado en la tabla principal
    (${geo_score}) viene de _calculate_geo_score() → GBP raw geo_score.
    El score en este breakdown viene de calcular_score_geo() → CHECKLIST_GEO.
    Pueden diferir porque son metodologías distintas. Ver FASE-SCORING-2
    para la nota explicativa en el template.
    
    Args:
        pilar: 'seo', 'geo', 'aeo', 'iao'
        elementos: dict con elementos del checklist (k: str, v: bool)
    
    Returns:
        String formateado con breakdown y score auto-calculado.
    """
    checklist_map = {
        'seo': CHECKLIST_SEO,
        'geo': CHECKLIST_GEO,
        'aeo': CHECKLIST_AEO,
        'iao': CHECKLIST_IAO,
    }
    score_fns = {
        'seo': calcular_score_seo,
        'geo': calcular_score_geo,
        'aeo': calcular_score_aeo,
        'iao': calcular_score_iao,
    }
    labels_map = {
        'seo': 'SEO Local',
        'geo': 'GEO',
        'aeo': 'AEO',
        'iao': 'IAO',
    }
    
    checklist = checklist_map.get(pilar, {})
    label = labels_map.get(pilar, pilar.upper())
    score_fn = score_fns.get(pilar)
    
    # Calcular score desde el checklist (fuente única de verdad para el breakdown)
    computed_score = score_fn(elementos) if score_fn else 0
    
    if not checklist:
        return f"**{label} {computed_score}/100**"
    
    # Construir breakdown solo con elementos que contribuyeron
    parts = []
    for k, peso in checklist.items():
        if elementos.get(k) is True:
            parts.append(f"{k}({peso}%)")
    
    if parts:
        return f"**{label} {computed_score}/100** = {' + '.join(parts)}"
    else:
        return f"**{label} {computed_score}/100**"
```

### 3. Implementar `_build_excluded_factors_section()`

Después de `_build_scoring_breakdown()`, agrega:

```python
def _build_excluded_factors_section() -> str:
    """Retorna sección 'Este score NO mide' con factores excluidos por pilar."""
    return """> **Este score NO mide:**
- **SEO Local:** contenido editorial, perfil de backlinks, domain authority externo
- **GEO:** tasa de respuesta a reseñas, tiempo de respuesta, calidad de las respuestas, engagement rate, antigüedad de reseñas nuevas
- **AEO:** volumen de tráfico, conversiones
- **IAO:** tráfico directo, revenue, NPS

> **Para el score GEO específicamente:** un hotel con 203 reseñas y respuesta <24h puede bajar su score por fotos faltantes o inconsistencia NAP — no por la calidad de su engagement con reseñas."""
```

### 4. Agregar template vars en `_prepare_template_data()`

Busca la función `_prepare_template_data()` y agrega las siguientes variables al dict `data` (después de la sección de regional averages, ~L618):

**Paso 4a: Extraer elementos GEO**
```python
# Extraer elementos GEO del audit_result para el breakdown
elementos_geo = self._extraer_elementos_geo(audit_result)
```

**Paso 4b: Agregar template vars**
```python
# Scoring transparency (FASE-SCORING-1)
'geo_score_breakdown': _build_scoring_breakdown('geo', elementos_geo),
'excluded_factors_section': _build_excluded_factors_section(),
'scoring_methodology_url': './scoring_methodology.md',
```

**IMPORTANTE**: `${geo_score_breakdown}` usa `calcular_score_geo(elementos_geo)` para calcular el score (checklist-based), NO `_calculate_geo_score()` (GBP raw). Esto garantiza consistencia matemática: el score mostrado en el breakdown coincide exactamente con la suma de los items True del checklist.

El score en la tabla principal (`${geo_score}`) puede diferir porque viene de GBP raw. El template (FASE-SCORING-2) incluirá una nota explicativa.

**Nota:** `_build_scoring_breakdown` funciona para los 4 pilares. Si se desea breakdown de SEO/AEO/IAO en el futuro, se repite el patrón con `_extraer_elementos_seo()`, `_extraer_elementos_aeo()`, `_extraer_elementos_iao()`.

### 5. Ejecutar tests existentes

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -v -x --tb=short 2>&1 | head -50
```

Si hay tests que fallan por los cambios, ajusta la implementación.

---

## CRITERIOS DE COMPLETITUD

- [x] `_build_scoring_breakdown()` existe con signature `(pilar, elementos)` y score auto-calculado (checklist-based)
- [x] `_build_excluded_factors_section()` existe y retorna la sección "Este score NO mide"
- [x] `_prepare_template_data()` incluye las nuevas variables de template
- [x] Tests pasan (0 regressions — 4 pre-existentes: test_identify_brechas_returns_all_detected, 3x TestIaoScoreWithLlmReport)

## ESTADO
✅ COMPLETADA — 2026-05-02

---

## RESTRICCIONES

- No modificar el template todavía (eso es FASE-SCORING-2)
- No ejecutar v4complete
- No crear scoring_methodology.md todavía
- Máximo 60 iteraciones

---

## EVIDENCIA A GUARDAR

Al terminar, reporta:
1. Líneas donde agregaste las funciones
2. Output de los tests
