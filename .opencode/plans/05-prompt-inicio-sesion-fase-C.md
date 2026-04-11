# FASE-C: Pesos Normalizados + Integración DynamicImpactCalculator

**ID**: FASE-C
**Objetivo**: Reemplazar los pesos hardcoded de brechas (suma hasta 150%) por un sistema normalizado (suma siempre = 100%). Integrar `DynamicImpactCalculator` como fuente de pesos dinámicos cuando hay datos disponibles.
**Dependencias**: FASE-A (Scenario.monthly_loss_central)
**Duración estimada**: 2-2.5 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

Las brechas en `v4_diagnostic_generator.py` (líneas 1770-1910) tienen pesos hardcoded:
- 10 brechas con pesos arbitrarios (8%-30%)
- Suma máxima posible: 150% (inconsistencia matemática)
- Caso Amazilia: 4 brechas sumaron 55%, dejando 45% sin explicar ($1.4M)
- Ningún peso se deriva de datos reales

El módulo `DynamicImpactCalculator` (modules/utils/dynamic_impact.py, 306 líneas) YA TIENE la lógica para impacto dinámico basado en datos reales, pero NO está conectado al generador de diagnóstico.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada — Scenario.monthly_loss_central existe |
| FASE-B | ⬜ Pendiente (puede ejecutarse en paralelo con C) |

### Base Técnica Disponible
- `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 1547-1910)
  - `_identify_brechas()` — detecta brechas y asigna pesos hardcoded
  - `_get_brecha_costo()` — usa `monthly_loss_max * proportion`
  - `_get_brecha_recuperacion()` — usa `monthly_loss_max * proportion`
- `modules/utils/dynamic_impact.py` (306 líneas)
  - `DynamicImpactCalculator` — calculate_impacts(region, detected_issues, hotel_data)
  - `ImpactResult` — issue_type, factor, monthly_loss_cop, description, confidence_source
  - Factores por issue type: PERFIL_NO_RECLAMADO=1.0, FOTOS_INSUFICIENTES=0.35, etc.
  - Usa BenchmarkLoader y ConfidenceTracker
- Tests: tests existentes del generador de diagnóstico

---

## Tareas

### Tarea 1: Función de normalización de pesos

**Objetivo**: Crear una función centralizada que normalice cualquier conjunto de pesos a 100%.

**Archivo afectado**: `modules/commercial_documents/v4_diagnostic_generator.py` (agregar método privado)

**Implementación**:
```python
def _normalize_weights(self, brechas: List[Dict]) -> List[Dict]:
    """
    Normaliza pesos de brechas para que sumen exactamente 100%.
    
    Regla: peso_bruto / suma(pesos_brutos) * 100
    Cada brecha recibe peso proporcional a su impacto relativo.
    La suma siempre será 100%, sin porción "sin explicar".
    """
    if not brechas:
        return brechas
    
    total = sum(b.get('impacto', 0) for b in brechas)
    if total == 0:
        # Distribución equitativa como fallback
        equal_weight = 100.0 / len(brechas)
        for b in brechas:
            b['impacto'] = round(equal_weight, 2)
            b['impacto_raw'] = 0
            b['normalizado'] = True
        return brechas
    
    for b in brechas:
        raw = b.get('impacto', 0)
        b['impacto_raw'] = raw  # preservar peso original para auditoría
        b['impacto'] = round(raw / total * 100, 2)
        b['normalizado'] = True
    
    return brechas
```

**Criterios de aceptación**:
- [ ] La suma de pesos normalizados siempre es 100% (±0.01 por redondeo)
- [ ] El peso original se preserva en `impacto_raw`
- [ ] Cada brecha tiene flag `normalizado=True`
- [ ] Lista vacía retorna lista vacía sin errores

### Tarea 2: Integrar DynamicImpactCalculator como fuente alternativa de pesos

**Objetivo**: Si hay hotel_data disponible, usar DynamicImpactCalculator para pesos. Si no, usar _identify_brechas() hardcoded pero normalizado.

**Archivo afectado**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Cambios en el flujo**:
```python
def _get_brecha_pesos(self, audit_result, hotel_data=None, region=None):
    """
    Obtiene pesos de brechas con escalera de fuentes:
    1. DynamicImpactCalculator (si hay hotel_data + region)
    2. _identify_brechas() hardcoded normalizado (fallback)
    """
    brechas = self._identify_brechas(audit_result)
    
    # Intentar pesos dinámicos si hay datos
    if hotel_data and region:
        try:
            from modules.utils.dynamic_impact import DynamicImpactCalculator
            calc = DynamicImpactCalculator()
            detected_issues = [b.get('tipo', '') for b in brechas]
            impact_report = calc.calculate_impacts(region, detected_issues, hotel_data)
            
            # Mapear factores de DynamicImpactCalculator a pesos de brechas
            impact_map = {r.issue_type: r.factor for r in impact_report.impacts}
            for b in brechas:
                issue_type = self._map_brecha_to_issue_type(b.get('tipo', ''))
                if issue_type in impact_map:
                    b['impacto'] = impact_map[issue_type] * 100  # factor → porcentaje
                    b['peso_source'] = 'dynamic_impact'
        except Exception:
            pass  # Fallback a pesos hardcoded
    
    # Siempre normalizar
    brechas = self._normalize_weights(brechas)
    return brechas

def _map_brecha_to_issue_type(self, brecha_tipo: str) -> str:
    """Mapea tipo de brecha del diagnóstico a issue_type del DynamicImpactCalculator."""
    mapping = {
        'schema_hotel': 'SCHEMA_FALTANTE',
        'sin_whatsapp': 'SIN_WHATSAPP',
        'web_lenta': 'RENDIMIENTO_WEB',
        'falta_reviews': 'REVIEWS_INSUFICIENTES',
        'metadata_defaults': 'METADATA_DEFAULTS',
        'faq_schema': 'FAQ_SCHEMA',
        'open_graph': 'OPEN_GRAPH',
        'visibilidad_gbp': 'PERFIL_NO_RECLAMADO',
        'contenido_no_citable': 'CONTENIDO_NO_CITABLE',
        'conflictos_datos': 'CONFLICTOS_DATOS',
    }
    return mapping.get(brecha_tipo, '')
```

**Criterios de aceptación**:
- [ ] Escalera: DynamicImpact > hardcoded normalizado
- [ ] Si DynamicImpact falla, fallback a hardcoded normalizado (sin crash)
- [ ] Cada brecha tiene `peso_source` ('dynamic_impact' o None)

### Tarea 3: Actualizar `_get_brecha_costo` y `_get_brecha_recuperacion`

**Objetivo**: Consumir valor central + pesos normalizados en vez de `monthly_loss_max * proportion`.

**Archivo afectado**: `modules/commercial_documents/v4_diagnostic_generator.py` líneas 1547-1590

**Cambios**:
```python
def _get_brecha_costo(self, audit_result, financial_scenarios, index):
    brechas = self._get_brecha_pesos(audit_result)  # ya normalizados
    if index < len(brechas):
        main = financial_scenarios.get_main_scenario()
        # Valor central si existe, sino max (legacy fallback)
        base_value = getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max
        proportion = brechas[index].get('impacto', 0) / 100.0  # peso normalizado a proporción
        costo = base_value * proportion
        return format_cop(costo)
    return format_cop(0)

def _get_brecha_recuperacion(self, audit_result, financial_scenarios, index):
    # Mismo patrón que _get_brecha_costo
    brechas = self._get_brecha_pesos(audit_result)
    if index < len(brechas):
        main = financial_scenarios.get_main_scenario()
        base_value = getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max
        proportion = brechas[index].get('impacto', 0) / 100.0
        recuperacion = base_value * proportion
        return format_cop(recuperacion)
    return format_cop(0)
```

**Criterios de aceptación**:
- [ ] Usa `monthly_loss_central` si existe, `monthly_loss_max` como fallback
- [ ] Peso normalizado se divide entre 100 para convertir a proporción
- [ ] Caso Amazilia: 4 brechas suman 100% (no 55%)

### Tarea 4: Tests de normalización y pesos

**Archivo afectado**: Crear/actualizar tests del generador

**Tests requeridos**:
```python
# 1. Normalización suma 100%
def test_normalize_weights_sums_100():
    brechas = [
        {'tipo': 'schema', 'impacto': 25},
        {'tipo': 'faq', 'impacto': 12},
        {'tipo': 'metadata', 'impacto': 10},
        {'tipo': 'open_graph', 'impacto': 8},
    ]
    result = generator._normalize_weights(brechas)
    total = sum(b['impacto'] for b in result)
    assert abs(total - 100.0) < 0.1  # ±0.1%

# 2. Peso original preservado
def test_raw_weight_preserved():
    brechas = [{'tipo': 'schema', 'impacto': 25}]
    result = generator._normalize_weights(brechas)
    assert result[0]['impacto_raw'] == 25
    assert result[0]['impacto'] == 100.0  # Una sola brecha = 100%
    assert result[0]['normalizado'] == True

# 3. Fallback a equitativo si todos son 0
def test_equal_weight_fallback():
    brechas = [{'tipo': 'a', 'impacto': 0}, {'tipo': 'b', 'impacto': 0}]
    result = generator._normalize_weights(brechas)
    assert result[0]['impacto'] == 50.0
    assert result[1]['impacto'] == 50.0

# 4. Caso Amazilia: 4 brechas = 100%
def test_amazilia_four_brechas_100():
    brechas = [
        {'tipo': 'schema_hotel', 'impacto': 25},
        {'tipo': 'faq_schema', 'impacto': 12},
        {'tipo': 'metadata', 'impacto': 10},
        {'tipo': 'open_graph', 'impacto': 8},
    ]
    result = generator._normalize_weights(brechas)
    total = sum(b['impacto'] for b in result)
    assert abs(total - 100.0) < 0.1
    # Schema debería tener el mayor peso proporcional
    assert result[0]['impacto'] > result[1]['impacto']
```

**Criterios de aceptación**:
- [ ] 4 tests nuevos pasan
- [ ] Tests existentes del generador no se rompen

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| test_normalize_weights_sums_100 | tests del generador | Suma = 100% ±0.1 |
| test_raw_weight_preserved | tests del generador | impacto_raw preservado |
| test_equal_weight_fallback | tests del generador | Distribución equitativa |
| test_amazilia_four_brechas_100 | tests del generador | 4 brechas = 100% |
| Suite completa | `tests/` | 0 failures |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -20
```

---

## Restricciones

- NO modificar ScenarioCalculator — eso es FASE-B
- NO modificar main.py — eso es FASE-G
- NO modificar el template V6 — eso es FASE-F
- `_identify_brechas()` existente se mantiene (solo se agregan wrapper y normalización encima)
- DynamicImpactCalculator integration es best-effort: si falla, fallback limpio

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-C como ✅ Completada
2. **`06-checklist-implementacion.md`** — Marcar FASE-C
3. **`09-documentacion-post-proyecto.md`** — Sección A: normalize_weights, Sección D: métricas
4. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-C \
    --desc "Pesos normalizados (suma=100%) + integración DynamicImpactCalculator" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "4"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `_normalize_weights()` funciona correctamente (suma siempre ~100%)
- [ ] Pesos originales preservados para auditoría
- [ ] DynamicImpactCalculator integrado como fuente alternativa
- [ ] `_get_brecha_costo` y `_get_brecha_recuperacion` usan valor central + pesos normalizados
- [ ] 4 tests nuevos pasan
- [ ] Suite completa pasa
- [ ] `log_phase_completion.py` ejecutado
