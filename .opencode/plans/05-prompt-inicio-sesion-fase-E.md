# FASE-E: OG Detection - Reutilizar HTML del schema audit en vez de segunda request

> **Skill**: `phased_project_executor`
> **Version Base**: 4.25.3
> **Tests Base**: 1782 funciones, 140 archivos, 52 regresion
> **Dependencias**: Ninguna (independiente de C y D por archivos)
> **Archivo Principal**: `modules/auditors/v4_comprehensive.py`
> **Sesion**: 1 fase = 1 sesion

---

## CONTEXTO

`SEOElementsDetector` (creado en FASE-A) funciona correctamente y 9 tests pasan. El wiring existe: `v4_comprehensive.py` L404 ejecuta el detector y L500 asigna el resultado al `V4AuditResult`.

**El problema**: El detector recibe HTML sin OG tags aunque el sitio los tiene. Esto ocurre porque `v4_comprehensive.py` hace una **segunda request HTTP** en step 2.8/2.9 (linea 391-393) que devuelve HTML diferente al del schema audit (step 2.1). Sitios SPA/JS-rendered pueden servir shells HTML sin metadatos en requests subsecuentes.

**Evidencia**: Para hotelvisperas.com, el sitio tiene OG tags verificados via curl, pero el log E2E muestra `Open Graph: False`. Citability tambien dio 0.0/100 con 0 bloques analizados, confirmando HTML transitorio.

**Impacto comercial**: +25pts AEO por hotel tipico al corregir este falso negativo.

---

## TAREA: Reutilizar HTML del schema audit (step 2.1)

### Cambio requerido

**Archivo**: `modules/auditors/v4_comprehensive.py`

**Flujo actual** (problematico):
```
Step 2.1: schema audit
  -> HttpClient().get(url) -> html_content_1  (con OG tags)

Step 2.8: citability
  -> HttpClient().get(url) -> html_for_citability  (HTML diferente!)

Step 2.9: SEO elements  
  -> usa html_for_citability.text  (sin OG tags!)
```

**Flujo corregido**:
```
Step 2.1: schema audit
  -> HttpClient().get(url) -> html_content_1  (con OG tags)
  -> Guardar html_content_1.text en variable accesible

Step 2.8: citability
  -> Reutilizar html_content_1.text  (evitar 2da request)

Step 2.9: SEO elements
  -> Reutilizar html_content_1.text  (mismo HTML con OG tags)
```

### Ubicacion del cambio

**v4_comprehensive.py lineas ~391-404**:

Codigo actual (aproximado):
```python
# Linea ~391-393: Segunda request (innecesaria)
html_for_citability = HttpClient().get(url)
html_content = html_for_citability.text

# Linea ~404: Detector usa html_content de la segunda request
seo_elements = self._run_seo_elements_audit(html_content, url)
```

Fix:
```python
# Reutilizar html_content del schema audit (step 2.1)
# NO hacer segunda request
seo_elements = self._run_seo_elements_audit(self.html_content, url)
# Donde self.html_content fue guardado en step 2.1
```

### Logging defensivo

Agregar logging cuando OG no se detecta, para facilitar diagnostico futuro:

```python
if seo_elements and not seo_elements.open_graph:
    import logging
    logger = logging.getLogger(__name__)
    # Guardar snippet del HTML para diagnostico
    html_snippet = html_content[:500] if html_content else "EMPTY"
    logger.warning(f"OG not detected. HTML snippet: {html_snippet}")
```

---

## PLAN DE EJECUCION

### Paso 1: Verificacion pre-fix (5 min)

1. Leer `v4_comprehensive.py` completo, identificar exactamente donde se hace cada request HTTP
2. Confirmar que `self.html_content` (o equivalente) ya existe del step 2.1
3. Verificar que citability scorer y SEO elements detector pueden compartir el mismo HTML
4. Confirmar firma de `_run_seo_elements_audit(html_content, url)`
5. Ejecutar test baseline: `python -m pytest tests/ -x --tb=short -q 2>&1 | tail -5`

### Paso 2: Aplicar fix (10 min)

1. Eliminar la segunda request HTTP en step 2.8/2.9
2. Reutilizar `html_content` del step 2.1 para citability y SEO elements
3. Agregar logging defensivo cuando OG no se detecta
4. Verificar que no hay otros consumidores del HTML de la segunda request

### Paso 3: Validacion post-fix (10 min)

```bash
# Validacion rapida del ecosistema
python scripts/run_all_validations.py --quick

# Tests especificos de SEO elements
python -m pytest tests/ -k "seo_elements" -x --tb=short -v

# Tests de regresion completos
python -m pytest tests/ -x --tb=short -q
```

### Paso 4: Verificacion manual E2E (5 min)

Si es posible ejecutar v4complete contra un hotel real:
```bash
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es --debug
grep "Open Graph" evidence/*/ejecucion.log
# Esperado: "Open Graph: True"
```

### Paso 5: Post-ejecucion (5 min)

1. Marcar checklist de completitud
2. Actualizar `dependencias-fases.md` con estado FASE-E
3. Ejecutar: `python scripts/log_phase_completion.py --fase FASE-E`
4. Commit: `git add -A && git commit -m "fix(FASE-E): reuse schema audit HTML for OG detection, eliminate redundant HTTP request"`

---

## CRITERIOS DE COMPLETITUD

### Checklist de Verificacion

- [ ] **E1**: Segunda request HTTP eliminada (o reutilizada) en step 2.8/2.9
- [ ] **E2**: SEO elements detector usa el mismo HTML del schema audit
- [ ] **E3**: Logging defensivo agregado para OG no detectado
- [ ] **E4**: `run_all_validations.py --quick` pasa sin errores
- [ ] **E5**: Tests existentes pasan (sin regresion)
- [ ] **E6**: `log_phase_completion.py --fase FASE-E` ejecutado exitosamente
- [ ] **E7**: Commit realizado con mensaje descriptivo

### Condiciones de Exito

| Criterio | Condicion |
|----------|-----------|
| Tests pasan | >= baseline (sin regresion) |
| Validaciones | `--quick` sin errores |
| HTTP requests | Reducidas en 1 (eliminada segunda request) |
| OG deteccion | Falso negativo eliminado (verificable con logging) |

### Condiciones de Rollback

Si algo falla:
```bash
git stash
git stash drop
# Revisar error y reintentar
```

---

## ARCHIVOS AFECTADOS

| Archivo | Tipo | Cambio |
|---------|------|--------|
| `modules/auditors/v4_comprehensive.py` | MODIFICAR | Eliminar 2da request, reutilizar HTML, agregar logging |

## ARCHIVOS DE REFERENCIA (solo lectura)

| Archivo | Uso |
|---------|-----|
| `modules/auditors/seo_elements_detector.py` | Confirmar que funciona con cualquier HTML |
| `modules/auditors/citability_scorer.py` | Confirmar que puede compartir HTML |
| `tests/` | Baseline y validacion post-fix |

---

## NOTAS

- Este fix es independiente de FASE-C y FASE-D (archivos diferentes) pero el workflow exige 1 fase/sesion.
- El beneficio principal es eliminar un falso negativo que subestima el AEO score en ~25pts.
- Sitios con HTML estatico (no SPA) no se benefician porque ambas requests devuelven lo mismo, pero tampoco se perjudican.
- Reducir requests HTTP tambien mejora velocidad de ejecucion.
