# FASE-D: Correccion de 5 BUGS MEDIOS + Serializacion seo_elements

> **Skill**: `phased_project_executor`
> **Version Base**: 4.25.3
> **Tests Base**: 1782 funciones, 140 archivos, 52 regresion
> **Dependencias**: FASE-C (debe estar completada)
> **Archivos Principales**: `modules/commercial_documents/v4_diagnostic_generator.py`, `modules/auditors/v4_comprehensive.py`
> **Sesion**: 1 fase = 1 sesion

---

## CONTEXTO

FASE-C corrigio los 4 bugs criticos. Esta fase corrige 5 bugs medios (metodos duplicados, claves duplicadas, inconsistencia de confidence, pipes markdown, sufijo score) y agrega la serializacion faltante de `seo_elements` en `V4AuditResult.to_dict()`. Sin este fix, el JSON persistido pierde los datos SEO.

---

## BUGS A CORREGIR

### MED-1: Metodos duplicados con shadowing (~120 lineas dead code)

**Ubicacion**: Lineas 1630 vs 2035 (`_compute_opportunity_scores`), 1699 vs 2099 (`_inject_brecha_scores`)
**Sintoma**: Dos definiciones de cada metodo. La segunda silencia la primera. Tipos inconsistentes (atributos vs dicts).
**Codigo actual**: Primera definicion en lineas 1630-1749
```python
def _compute_opportunity_scores(self, ...):
    # ... ~60 lineas dead code
    pass

def _inject_brecha_scores(self, ...):
    # ... ~60 lineas dead code
    pass
```
**Fix**: Eliminar primera definicion completa (lineas 1630-1749). La segunda definicion es la que corre en produccion.

### MED-2: Claves duplicadas en dict de template data

**Ubicacion**: Lineas 517-520 vs 595-598
**Sintoma**: `geo_regional_avg`, `competitive_regional_avg`, `seo_regional_avg`, `aeo_regional_avg` definidas 2 veces con valores identicos. Python usa la ultima silenciosamente.
**Codigo actual** (lineas 517-520, primera ocurrencia):
```python
"geo_regional_avg": ...,
"competitive_regional_avg": ...,
"seo_regional_avg": ...,
"aeo_regional_avg": ...,
```
**Fix**: Eliminar primera ocurrencia (lineas 517-520). La segunda ocurrencia (595-598) permanece.

### MED-3: Inconsistencia mayusculas/minusculas en confidence

**Ubicacion**: Linea 822 vs 833/844/854/864/868
**Sintoma**: WhatsApp usa `confidence.value` (minusculas: "verified"), otros usan strings hardcodeados en mayusculas ("ESTIMATED", "VERIFIED"). Tabla de datos validados muestra estilos mezclados.
**Fix**: Estandarizar a mayusculas via helper. En la linea 822, cambiar:
```python
# Antes (si existe algo como):
confidence_value = confidence.value  # "verified" minusculas
# Despues:
confidence_value = confidence.value.upper() if hasattr(confidence, 'value') else str(confidence).upper()
```
Para las lineas 833/844/854/864/868 que ya usan mayusculas hardcodeadas, verificar consistencia.

### MED-4: Tabla Markdown con pipe duplicado

**Ubicacion**: Linea 298
**Sintoma**: Fila AEO empieza con `||` en vez de `|` -- rompe alineacion de tabla markdown.
**Codigo actual**:
```python
f"|| Infraestructura"
```
**Fix**:
```python
f"| Infraestructura"
```

### MED-5: Falta `/100` en aeo_score del template

**Ubicacion**: Linea 298
**Sintoma**: Demas scores muestran `42/100`, AEO muestra `42` sin sufijo. Inconsistencia visual.
**Codigo actual**:
```python
${aeo_score}
```
**Fix**:
```python
${aeo_score}/100
```

---

### SER-1: seo_elements NO se serializa a audit_report.json

**Ubicacion**: `modules/auditors/v4_comprehensive.py` metodo `to_dict()` (~linea 288)
**Sintoma**: `SEOElementsDetector` corre y asigna resultado a `V4AuditResult.seo_elements`, pero `to_dict()` NO lo incluye en el dict retornado. JSON persistido pierde datos OG, imagenes alt, redes sociales.
**Fix**: Agregar en `to_dict()` antes del `return result`:
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

---

## PLAN DE EJECUCION

### Paso 1: Verificacion pre-fix (5 min)

1. Confirmar que FASE-C fue completada (4 fixes aplicados)
2. Verificar lineas exactas de cada bug MED-1 a MED-5 en el archivo actual
3. Verificar que los metodos duplicados (MED-1) efectivamente son shadowing (ejecutar la segunda definicion)
4. Confirmar estructura de `SEOElementsResult` en `seo_elements_detector.py` para serializacion
5. Ejecutar test baseline: `python -m pytest tests/ -x --tb=short -q 2>&1 | tail -5`

### Paso 2: Aplicar fixes (15 min)

Aplicar en orden, de menor riesgo a mayor:

| Orden | Bug | Archivo | Cambio | Riesgo |
|-------|-----|---------|--------|--------|
| 1 | MED-4 | v4_diagnostic_generator.py:298 | Pipe `||` -> `|` | Bajo |
| 2 | MED-5 | v4_diagnostic_generator.py:298 | Agregar `/100` | Bajo |
| 3 | MED-2 | v4_diagnostic_generator.py:517-520 | Eliminar claves dup | Bajo |
| 4 | MED-3 | v4_diagnostic_generator.py:822 | `.upper()` en confidence | Bajo |
| 5 | SER-1 | v4_comprehensive.py:~288 | Agregar serializacion seo_elements | Bajo - solo agrega |
| 6 | MED-1 | v4_diagnostic_generator.py:1630-1749 | Eliminar metodos dup | Medio - mayor cambio |

### Paso 3: Validacion post-fix (10 min)

```bash
# Validacion rapida del ecosistema
python scripts/run_all_validations.py --quick

# Tests especificos del modulo afectado
python -m pytest tests/ -k "diagnostic" -x --tb=short -v

# Tests de regresion completos
python -m pytest tests/ -x --tb=short -q
```

### Paso 4: Verificacion manual de fixes (5 min)

1. **MED-1**: Confirmar que solo queda una definicion de cada metodo
2. **MED-2**: Confirmar que las claves regional_avg aparecen solo una vez
3. **MED-3**: Confirmar confidence siempre en mayusculas
4. **MED-4**: Confirmar tabla markdown con pipes correctos
5. **MED-5**: Confirmar AEO score muestra `/100`
6. **SER-1**: Confirmar que `audit_report.json` incluye campo `seo_elements` con datos

### Paso 5: Post-ejecucion (5 min)

1. Marcar checklist de completitud (ver abajo)
2. Actualizar `dependencias-fases.md` con estado FASE-D
3. Ejecutar: `python scripts/log_phase_completion.py --fase FASE-D`
4. Commit: `git add -A && git commit -m "fix(FASE-D): 5 medium bugs + seo_elements serialization in v4_comprehensive"`

---

## CRITERIOS DE COMPLETITUD

### Checklist de Verificacion

- [ ] **D1**: Metodos `_compute_opportunity_scores` y `_inject_brecha_scores` tienen una sola definicion cada uno
- [ ] **D2**: Claves `*_regional_avg` aparecen una sola vez en el dict de template data
- [ ] **D3**: Confidence usa mayusculas consistentemente (`.upper()`)
- [ ] **D4**: Tabla AEO no tiene pipe duplicado (`|` no `||`)
- [ ] **D5**: AEO score incluye `/100`
- [ ] **D6**: `V4AuditResult.to_dict()` serializa `seo_elements` completo
- [ ] **D7**: `executed_validators` incluye `"seo_elements_detection"`
- [ ] **D8**: `run_all_validations.py --quick` pasa sin errores
- [ ] **D9**: Todos los tests existentes pasan (sin regresion vs FASE-C)
- [ ] **D10**: `log_phase_completion.py --fase FASE-D` ejecutado exitosamente
- [ ] **D11**: Commit realizado con mensaje descriptivo

### Condiciones de Exito

| Criterio | Condicion |
|----------|-----------|
| Tests pasan | >= baseline post-FASE-C (sin regresion) |
| Validaciones | `--quick` sin errores |
| Bugs corregidos | 5/5 medios + 1/1 serializacion (D1-D7 verificados) |
| Sin nuevos fallos | 0 nuevos test failures |

### Condiciones de Rollback

Si algo falla:
```bash
git stash  # Revertir cambios
git stash drop  # Descartar cambios
# Revisar error y reintentar
```

---

## ARCHIVOS AFECTADOS

| Archivo | Tipo | Cambio |
|---------|------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | MODIFICAR | MED-1 a MED-5 (~25 lineas) |
| `modules/auditors/v4_comprehensive.py` | MODIFICAR | SER-1 serializacion (~12 lineas) |

## ARCHIVOS DE REFERENCIA (solo lectura)

| Archivo | Uso |
|---------|-----|
| `modules/auditors/seo_elements_detector.py` | Confirmar campos de `SEOElementsResult` |
| `modules/auditors/citability_scorer.py` | Referencia de estructura de resultado |
| `tests/` | Baseline y validacion post-fix |

---

## NOTAS

- MED-1 elimina ~120 lineas de dead code. Verificar que la segunda definicion cubre toda la funcionalidad.
- SER-1 es bajo riesgo porque solo agrega serializacion. No altera logica de auditoria.
- FASE-E (OG HTML reuse) y FASE-D pueden ejecutarse en cualquier orden segun `dependencias-fases.md`, pero el workflow exige 1 fase/sesion.
