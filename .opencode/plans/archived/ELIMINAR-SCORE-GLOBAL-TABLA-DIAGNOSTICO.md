# Contexto: Eliminar fila "Visibilidad Digital (Global)" de tabla de diagnóstico

**Fecha:** 2026-04-12
**Estado:** Análisis de causa raíz completo. Listo para planificación de implementación.
**Alcance:** Eliminar la fila redundante `score_global` del template de diagnóstico cliente. Mantener cálculo interno para propuesta/paquete.
**Impacto:** Bajo — 1 template, 1 línea en generador, 0 tests afectados (tests unitarios miden `calcular_score_global()` que se mantiene).

---

## 1. PROBLEMA IDENTIFICADO

La línea 56 del diagnóstico generado muestra una fila **"Visibilidad Digital (Global)"** que:

1. **Es redundante:** Es un promedio aritmético de las 4 filas anteriores (SEO, GEO, AEO, IAO) con peso idéntico 25% c/u. No aporta información nueva.
2. **Sin benchmark regional:** Muestra `- | -` en las columnas "Promedio Regional" y "Estado", mientras las otras 4 filas tienen benchmarks y estados (❌/✅). Dato sin contexto = dato inútil.
3. **Diluye el marco de 4 Pilares:** Todo el producto se construyó sobre 4 pilares diferenciados. Una 5ª fila confunde al cliente sobre dónde están sus brechas específicas.

### Evidencia del output actual (20260412_174210)

```
|| **SEO Local** (Para que te ENCUENTREN) | 10/100 | 59/100 | ❌ Bajo |
|| **Google Maps** (Para que te UBICQUEN) | 0/100 | 85/100 | ❌ Bajo |
|| **AEO** (Para que te CITEN) | 0/100 | 40/100 | ❌ Bajo |
|| **IAO** (Para que te RECOMIENDEN) | 17/100 | 15/100 | ✅ Superior |
|| **Visibilidad Digital** (Global) | 15/100 | - | - |    ← REDUNDANTE
```

### Cálculo en código

```python
# modules/commercial_documents/v4_diagnostic_generator.py:168-170
def calcular_score_global(seo, geo, aeo, iao):
    """Visibilidad Digital = promedio ponderado 4 pilares (0-100)."""
    return int((seo * 0.25) + (geo * 0.25) + (aeo * 0.25) + (iao * 0.25))
```

---

## 2. MAPEO DE ARCHIVOS AFECTADOS

### Archivos a modificar

| Archivo | Línea | Cambio | Prioridad |
|---------|-------|--------|-----------|
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | 56 | **Eliminar** la fila `\| **Visibilidad Digital** (Global) \| ${score_global}/100 \| - \| - \|` | ALTA |
| `modules/commercial_documents/v4_diagnostic_generator.py` | 626 | **Eliminar** `'score_global_status': ...` (dead code — nunca se usa en template) | MEDIA |

### Archivos que se MANTIENEN sin cambios

| Archivo | Línea | Razón para mantener |
|---------|-------|---------------------|
| `v4_diagnostic_generator.py:168-170` | `calcular_score_global()` | Función usada internamente por `sugerir_paquete()` |
| `v4_diagnostic_generator.py:625` | `'score_global': ...` | Campo necesario para `v4_proposal_generator.py:543-544` (alias `score_tecnico`) |
| `v4_diagnostic_generator.py:1578-1588` | `_calculate_score_global_from_audit()` | Método que alimenta el campo `score_global` en template data |
| `data_structures.py:316` | `score_global: Optional[int]` | Campo en dataclass, usado por proposal generator |
| `v4_proposal_generator.py:543-544` | `'score_tecnico': diagnostic_summary.score_global` | **USO FUNCIONAL CRÍTICO** — determina paquete básico/avanzado/premium |
| `tests/commercial_documents/test_iao_score.py:58-78` | Tests de `calcular_score_global()` | Tests unitarios de la función que se mantiene |

### Dead code adicional (eliminar junto con línea 626)

| Variable | Línea | Motivo dead code |
|----------|-------|------------------|
| `score_global_status` | 626 | Calculada pero **nunca referenciada** en ningún template ni en código posterior |

---

## 3. DETALLE DE CAMBIOS

### Cambio 1: Template — eliminar fila

**Archivo:** `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Antes (líneas 50-57):**
```markdown
|||| Indicador | Su Negocio | Promedio Regional | Estado ||
||||-----------|------------|------------------|--------||
| **SEO Local** (Para que te ENCUENTREN) | ${seo_score}/100 | ${seo_regional_avg}/100 | ${seo_status} |
| **Google Maps** (Para que te UBICQUEN) | ${geo_score}/100 | ${geo_regional_avg}/100 | ${geo_status} |
| **AEO** (Para que te CITEN) | ${aeo_score}/100 | ${aeo_regional_avg}/100 | ${aeo_status} |
| **IAO** (Para que te RECOMIENDEN) | ${iao_score}/100 | ${iao_regional_avg}/100 | ${iao_status} |
| **Visibilidad Digital** (Global) | ${score_global}/100 | - | - |
```

**Después (eliminar línea 56):**
```markdown
|||| Indicador | Su Negocio | Promedio Regional | Estado ||
||||-----------|------------|------------------|--------||
| **SEO Local** (Para que te ENCUENTREN) | ${seo_score}/100 | ${seo_regional_avg}/100 | ${seo_status} |
| **Google Maps** (Para que te UBICQUEN) | ${geo_score}/100 | ${geo_regional_avg}/100 | ${geo_status} |
| **AEO** (Para que te CITEN) | ${aeo_score}/100 | ${aeo_regional_avg}/100 | ${aeo_status} |
| **IAO** (Para que te RECOMIENDEN) | ${iao_score}/100 | ${iao_regional_avg}/100 | ${iao_status} |
```

### Cambio 2: Generador — eliminar dead code + fix docstring

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py`

**Eliminar línea 626:**
```python
'score_global_status': self._get_score_status(sg_sc, 50),
```

**La línea 625 (`'score_global': ...`) se MANTIENE porque `v4_proposal_generator.py` la necesita.**

**Corrección incidental — docstring copy-paste error en funcion ADYACENTE:**
El error NO esta en `calcular_score_global()` (líneas 168-170) sino en `calcular_cumplimiento()` (línea 173-175):

```python
# EN calcular_cumplimiento() — linea 175 (error copy-paste):
"""DEPRECATED: Usar calcular_score_global(calcular_score_seo(...), ...) en su lugar."""

# El docstring de calcular_cumplimiento() se refiere a sí misma diciendo
# "usa calcular_score_global" — pero calcula_cumplimiento NO fue reemplazada
# por calcular_score_global. Ambas existen con propósitos distintos.
```

**Razón:** Este docstring legacy genera confusión durante auditoria de codigo. No forma parte del scope de eliminacion de `score_global_status` pero se puede corregir en el mismo PR por proximidad.

---

## 4. VERIFICACIÓN POST-IMPLEMENTACIÓN

### Tests a ejecutar
```bash
# Tests unitarios de scoring (deben pasar sin cambios)
python -m pytest tests/commercial_documents/test_iao_score.py -v

# Tests de generación de diagnóstico
python -m pytest tests/commercial_documents/ -v -k "diagnostic"

# Smoke test: generar diagnóstico y verificar que la tabla tiene 4 filas (no 5)
python main.py v4complete --url <url_test>
```

### Checklist de verificación
- [ ] Tabla de diagnóstico tiene exactamente 4 filas de pilar (SEO, GEO, AEO, IAO)
- [ ] No aparece "Visibilidad Digital (Global)" en output generado
- [ ] `score_global` sigue disponible internamente para `sugerir_paquete()`
- [ ] Propuesta recomienda paquete correcto basado en score interno
- [ ] Tests unitarios de `calcular_score_global()` pasan (0 regresión)
- [ ] `score_global_status` eliminada de generador (no quedan referencias huérfanas)

---

## 5. CONTEXTO ARQUITECTÓNICO

### Por qué `score_global` sobrevive como cálculo interno

El `score_global` tiene un **único uso funcional legítimo**: determinar el paquete recomendado.

```python
# v4_proposal_generator.py:543-544
'score_tecnico': diagnostic_summary.score_global if diagnostic_summary.score_global is not None else (...)
```

`score_tecnico` alimenta `sugerir_paquete()` que clasifica en:
- `basico` (<40)
- `avanzado` (40-69)
- `premium` (>=70)

Esto es lógico: el score global **justifica la recomendación** en la propuesta, no es un dato aislado sin contexto en el diagnóstico.

### Relación con refactor 4 Pilares (AEO-IAO-PROGRESSION-REFACTOR.md)

El contexto existente `AEO-IAO-PROGRESSION-REFACTOR.md` define la arquitectura correcta de 4 pilares como progresión con dependencias:

```
SEO (base) → AEO (construye sobre SEO) → IAO (construye sobre AEO)
    └── GEO (pilar lateral, complementario)
```

Eliminar la fila Global **refuerza** esta arquitectura: el cliente ve 4 pilares independientes con sus propios scores y benchmarks, no un promedio que los aplana.

---

## 6. RIESGOS

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Cliente pregunta "¿cuál es mi score total?" | Media | Bajo | Responder con el paquete recomendado que ya lo explica comercialmente |
| Tests de integración buscan la fila Global | Baja | Medio | Grep en tests/ para confirmar (ya verificado: 0 referencias en templates) |
| `score_global` se usa en flujo no documentado | Baja | Alto | Ya mapeado: solo 2 usos (template + proposal). Proposal se mantiene. |
