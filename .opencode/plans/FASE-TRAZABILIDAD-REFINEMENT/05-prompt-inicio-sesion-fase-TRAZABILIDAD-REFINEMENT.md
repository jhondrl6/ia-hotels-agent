# FASE-TRAZABILIDAD-REFINEMENT — Prompt de Inicio de Sesion

> **Para Hermes:** Usar `iah-cli-plan-vs-reality-check` ANTES de implementar. Verificar cada cambio contra codigo vivo.

**Contexto**: Fase unica que corrige 4 hallazgos pendientes + situacion GEO Score dual, documentados en `.opencode/context/fase-trazabilidad-context.md`.

**Fuente de verdad**: `_calculate_geo_score()` (GBP data de Google) es la fuente GEO autoritativa. `geo_flow` (AI crawler readiness) es complementario, NO duplicado.

**E2E**: Una UNICA ejecucion v4complete al final — "Amazilia Hotel" (https://amaziliahotel.com/).

---

## Tareas

Las tareas son atomicas. Cada una modifica un solo aspecto. Ejecutar en orden.

---

### T0: Pre-flight — Verificar entorno y cargar skills

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar venv
ls venv/Scripts/python.exe && echo "OK venv" || echo "MISSING venv"

# Verificar que geo_flow_result.json existe para Amazilia
ls output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json 2>/dev/null && echo "OK geo_flow" || echo "MISSING geo_flow"

# Verificar estructura JSON
venv/Scripts/python.exe -c "
import json
with open('output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json') as f:
    d = json.load(f)
print('geo_assessment.total_score:', d.get('geo_assessment',{}).get('total_score','MISSING'))
print('geo_score (top-level):', d.get('geo_score','MISSING'))
"
```

**Skills a cargar**: `iah-cli-plan-vs-reality-check`

---

### T1: Corregir lectura de Salud Tecnica GEO (D3)

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`
**Lineas**: 1258-1261

**Problema**: El codigo lee `geo_flow_data.get('geo_score', 0)` pero el JSON real tiene `geo_assessment.total_score: 23`. La metrica siempre muestra 0/100.

**Cambio**:

```python
# ANTES (L1258-1261):
flow_score = geo_flow_data.get('geo_score', 0)
flow_status = geo_flow_data.get('status', 'unknown')

# DESPUES:
geo_assessment = geo_flow_data.get('geo_assessment', {})
flow_score = geo_assessment.get('total_score', 0)
flow_status = geo_assessment.get('band', 'unknown')
```

**Nota**: `geo_assessment.band` es string (ej: `"critical"`), NO dict. El `case` al nivel raiz tambien es `"critical"` pero `band` dentro de `geo_assessment` es la fuente correcta para status.

**Verificacion**: 
```bash
venv/Scripts/python.exe -c "
import json
with open('output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json') as f:
    d = json.load(f)
ga = d.get('geo_assessment', {})
print('Expected score:', ga.get('total_score'))  # Debe ser 23
print('Expected status:', ga.get('band'))          # Debe ser 'critical'
"
```

---

### T2: Agregar WARNING al summary de readiness (D1)

**Archivo**: `modules/quality_gates/publication_gates.py`
**Lineas**: 1008-1014 (dentro de `check_publication_readiness()`)

**Problema**: WARNING con `passed=True` no aparece en el readiness report. El cliente no ve que hay datos estimados.

**Cambio**: Agregar lista de warnings al summary dict:

```python
# DESPUES de L1014 (despues de "summary = {"):
summary = {
    "total_gates": len(results),
    "passed": passed_count,
    "failed": len(results) - passed_count,
    "blocked": sum(1 for r in results if r.status == GateStatus.BLOCKED),
    "warnings": [  # NUEVO: visibilidad de WARNING
        {
            "gate": r.gate_name,
            "message": r.message
        }
        for r in results if r.status == GateStatus.WARNING
    ],
    "timestamp": datetime.now().isoformat()
}
```

**Verificacion**: El readiness report (`gate_report.json`) ahora incluye `summary.warnings` con los gates que tienen WARNING.

```bash
# Despues del cambio, verificar que el key existe
grep -n '"warnings"' modules/quality_gates/publication_gates.py
```

---

### T3: Visibilidad Tier C en encabezado financiero (D2)

**Archivos**: 
- `modules/commercial_documents/v4_diagnostic_generator.py` (`_build_financial_placeholders()`, L718-786)
- `modules/commercial_documents/templates/diagnostico_v6_template.md` (L68-76)

**Problema**: Cuando `evidence_tier == "C"`, el encabezado dice "Comision OTA Actual (verificable)" y muestra el monto sin indicar que es estimado. El `tier` ya se computa en `_build_financial_placeholders()` (L736-747: "A" si GA4, "C" si no). La variable `${evidence_tier}` ya existe en el footer (L100 del template).

**IMPORTANTE**: `_build_financial_title_label()` (L703-716) retorna un `str` que alimenta `${financial_title_label}`. NO modificar su firma — solo agregar variables NUEVAS al diccionario de retorno de `_build_financial_placeholders()` (L765-786).

**Cambio A — Codigo Python** (`v4_diagnostic_generator.py`):

Agregar DESPUES de L763 (`estimate_footnote = ...`):

```python
        # FASE-TRAZABILIDAD-REFINEMENT: Tier C visibility in header
        financial_tier_suffix = " *(estimado — Tier C)*" if tier == "C" else ""
        financial_tier_banner = (
            "> ⚠️ **Nivel de evidencia: Tier C** — Estas cifras se basan en benchmark regional\n"
            "> + datos limitados de la web. Para precision, ejecute onboarding con datos reales.\n"
        ) if tier == "C" else ""
```

Agregar al diccionario de retorno (L765-786), por ejemplo despues de `'estimate_footnote': estimate_footnote,` (L783):

```python
            # FASE-TRAZABILIDAD-REFINEMENT: Tier C header visibility
            'financial_tier_suffix': financial_tier_suffix,
            'financial_tier_banner': financial_tier_banner,
```

**Cambio B — Template** (`diagnostico_v6_template.md`):

Agregar `${financial_tier_banner}` entre L68 y L70:

```markdown
## 💰 Impacto Financiero

${financial_tier_banner}
### ${financial_title_label}
```

Cambiar L72 de:
```markdown
**${ota_commission_formatted} COP/mes${estimate_asterisk}**
```
a:
```markdown
**${ota_commission_formatted} COP/mes${estimate_asterisk}${financial_tier_suffix}**
```

**Verificacion**: En el diagnostico generado, cuando Tier C:
- El titulo muestra el label adecuado
- El monto tiene sufijo "(estimado — Tier C)"
- Hay un banner amarillo sobre la tabla financiera

---

### T4: Nota de asset_confidence en diagnostico (D4)

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`
**Ubicacion**: En `_build_manual_attention_table()` o en la seccion de Validacion de Calidad

**Problema**: El diagnostico muestra coherence_score = 0.89 pero 8/10 assets tienen confianza < 0.7. No hay indicacion de que los assets son de baja calidad.

**Cambio**: Agregar variable `asset_confidence_note` al template_data, que se inyecta en la seccion de Validacion de Calidad (template L82-84):

```python
# En el metodo generate(), alrededor de L462 donde se construye template_data.
# Agregar despues de construir ia_metrics_table:

# Leer asset_generation_report.json si existe
asset_confidence_note = ""
if output_dir:
    hotel_slug = audit_result.hotel_name.lower().replace(" ", "_").replace("-", "_")
    asset_report_path = Path(output_dir) / hotel_slug / "v4_audit" / "asset_generation_report.json"
    if asset_report_path.exists():
        import json as _json
        with open(asset_report_path, 'r', encoding='utf-8') as f:
            asset_report = _json.load(f)
        low_assets = [
            a for a in asset_report.get('generated_assets', [])
            if a.get('confidence_score', 1.0) < 0.7
        ]
        if low_assets:
            asset_confidence_note = (
                f"> ⚠️ **{len(low_assets)} assets generados con confianza baja (< 0.7)** — "
                f"Incluidos con disclaimer en el paquete de entrega. "
                f"Ejecute onboarding con datos reales para mejorar la precision.\n"
            )
```

Y en el template (`diagnostico_v6_template.md` L82-84):

```markdown
## ✅ Validacion de Calidad

${asset_confidence_note}

${manual_attention_table}
```

**Verificacion**: Cuando hay assets con confianza < 0.7, el diagnostico muestra la nota.

---

### T5: Ejecutar v4complete para Amazilia Hotel

**UNICA ejecucion**. Comando:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

**Verificar en la salida**:
- [ ] Pilar GEO no muestra "0/100" (si el hotel tiene GBP, debe mostrar score real)
- [ ] Salud Tecnica GEO muestra score > 0 (debe ser ~23 de geo_flow_result)
- [ ] gate_report.json incluye `summary.warnings`
- [ ] Si Tier C: encabezado financiero muestra etiqueta de estimacion
- [ ] Si assets con baja confianza: nota de transparencia visible
- [ ] v4complete termina con exit code 0

---

## Criterios de Aceptacion

1. `_calculate_geo_score()` permanece como fuente GEO autoritativa (GBP data)
2. `geo_flow` NO se depreca — sirve para AI crawler readiness (proposito distinto)
3. Salud Tecnica GEO muestra score > 0 cuando geo_flow_result.json tiene datos
4. Warnings de gates aparecen en el summary de readiness
5. Tier C es visible en el encabezado financiero (titulo + banner)
6. asset_confidence bajo genera nota de transparencia en Validacion de Calidad
7. v4complete Amazilia Hotel termina sin errores
8. No hay cambios en la API publica de ningun modulo

---

## Post-Ejecucion

```bash
# Registrar la fase
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-TRAZABILIDAD-REFINEMENT \
    --desc "Correccion hallazgos D1-D4 + decision GEO (GBP prevalece, geo_flow = AI crawler)" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/quality_gates/publication_gates.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --tests "0" \
    --check-manual-docs

# Commit
git add -A
git commit -m "fix: FASE-TRAZABILIDAD-REFINEMENT — D1-D4 fixes + GEO source decision"
```
