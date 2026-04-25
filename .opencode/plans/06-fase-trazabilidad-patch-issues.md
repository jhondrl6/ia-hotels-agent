# Plan: FASE-TRAZABILIDAD-PATCH+SEO — Corrección Unificada de Issues Post-Validate

**Proyecto**: iah-cli v4.35.1 (Trazabilidad Publication Gates)
**Fase**: PATCH — Corrección de 5 issues (4 de VALIDATE + D2 seo_score) en UNA sesión
**Sesión**: Una fase por sesión (regla rígida)
**Fecha**: 2026-04-25 (v2 — fusionado con FASE-07 SEO-SCORE para optimizar costo API)
**Archivo**: `.opencode/plans/06-fase-trazabilidad-patch-issues.md`
**Dependencia**: FASE-TRAZABILIDAD-VALIDATE completada
**Decisiones requeridas**: D1 (WARNING en readiness) → diferida a sesión separada. D2 → absorbido en esta fase. D3 resuelta: geo_flow sí genera datos reales.
**Optimización API**: Todos los fixes de código se aplican primero, luego UNA sola ejecución v4complete al final verifica los 5 issues simultáneamente.

---

## Contexto: Estado Actual

Después de ejecutar FASE-TRAZABILIDAD-VALIDATE con Amazilia Hotel, se detectaron 5 issues
que requieren corrección. Originalmente separados en 2 fases (06 PATCH + 07 SEO), se fusionan
en 1 sola fase con 1 sola ejecución v4complete para optimizar costo de API.

### Issue 1: BUG-02 — financial_validity gate FALSE POSITIVE
**Archivo**: `modules/quality_gates/publication_gates.py` (líneas 318-389)
**Síntoma**: El gate 3 (financial_validity) reporta PASSED con mensaje
"All financial data validated - no default values detected" PERO
`gate_report.json` tiene un `financial_sources` al final con:
```json
"financial_sources": {
  "adr_cop": "legacy_hardcode",
  "occupancy_rate": "default",
  "direct_channel_percentage": "default"
}
```
El gate usa `NoDefaultsValidator` que valida si `can_calculate=True` (datos permiten
hacer el cálculo aunque sean defaults). **No detecta que las fuentes son default.**

**Fix propuesto**: Modificar `_financial_validity_gate` para que ALSO inspeccione
`assessment.get('financial_sources', {})` y si algún campo tiene source
`in ('default', 'legacy_hardcode', 'legacy_fixed')`, el gate debe retornar
WARNING (advisory) en lugar de PASSED, incluyendo los campos affected en details.

---

### Issue 2: Secciones faltantes en diagnóstico — Nombres incorrectos
**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`
**Síntoma**: El criterio de checklist buscaba "Validación de Calidad" y
"Trazabilidad Brechas" con ese nombre exacto. El diagnóstico actual tiene:
- "Brechas detectadas" (no "Trazabilidad Brechas")
- "Problemas que requieren atención manual" (no "Validación de Calidad")

Ambas secciones EXISTEN con contenido pero con nombres diferentes.

**Fix propuesto**: O bien (A) renombrar las secciones en el template para que
coincidan con los nombres esperados por el checklist, o (B) actualizar el
criterio de checklist para que use los nombres reales. **Opción B preferida**
(los nombres actuales son más descriptivos y el contenido es correcto).
Esto requiere cambiar SOLO el criterio de verificación en el plan, NO el código.

**Hipótesis adicional**: Podría existir una sección "Validación de Calidad" en el
template V6 que no se esté renderizando porque `_build_manual_attention_table()`
retorna string vacío cuando no hay items. Verificar.

---

### Issue 3: seo_score ausente del JSON (D2 — absorbido de FASE-07)
**Archivo**: `main.py` (~L2792-2875)
**Síntoma**: El v4_complete_report.json NO tiene campo `seo_score` ni `web_score`.
El diagnóstico markdown SÍ muestra "SEO Local: 25/100" (template funciona).
`_calculate_web_score()` (L1444) retorna `str(score)` pero no se persiste al JSON.

**Fix propuesto**: En main.py, al construir el dict `report`, agregar:
```python
'seo_score': int(template_data.get('seo_score', 0)),
```
Alternativa si template_data no disponible:
```python
seo_score_str = diagnostic_gen._calculate_web_score(audit_result)
report['seo_score'] = int(seo_score_str) if seo_score_str else 0
```

---

### Issue 4: geo_flow_result no generado
**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`
(línea 1251-1260, método `_build_geo_problems_table`)
**Síntoma**: El geo_flow_result.json nunca se genera. El pipeline de GEO
bridge (`geo_enriched_bridge.py`) existe y hace enrichment de assets,
pero NO genera el archivo `geo_flow_result.json` que
`_build_geo_problems_table()` intenta leer.

**Hipótesis**: El archivo `geo_flow_result.json` se genera en una fase
anterior del pipeline (geo_enrichment) pero nunca se ejecuta en v4complete.
Revisar main.py para ver si existe una fase que escriba geo_flow_result.json.

**Fix propuesto**: Investigar si el geo_flow_result.json debe generarse dentro
del flujo v4complete. Si sí, agregar su generación en la FASE 2 (auditoría).
Si no, cambiar `_build_geo_problems_table()` para que no falle cuando el
archivo no exista (ya tiene `if geo_flow_path.exists()` pero el score sería 0).

---

## Tareas Específicas

### T1: Corregir BUG-02 (financial_validity gate false positive)

**ALERTA — SCOPE AMPLIADO** (validación cruzada 2026-04-25):

El checklist de FASE-RAIZ marca T1.1 como completado (`[x]`), pero `grep` confirma **CERO**
ocurrencias de `financial_sources`, `GateStatus.WARNING`, `DEFAULT_SOURCES` o `Tier C` en
`publication_gates.py`. El gate sigue siendo **puramente binario PASSED/BLOCKED**.

Esto significa que T1-BUG02 **NO es un "check secundario"** sobre algo ya hecho.
Es la **implementación COMPLETA** del path WARNING + financial_sources que T1.1 de FASE-RAIZ
debio haber hecho pero no se reflejó en el código (posible sesión que fallo antes del commit).

**HIPÓTESIS DE CAUSA (confirmada)**:
`check_publication_readiness()` en publication_gates.py L979-982:
```python
results = run_publication_gates(assessment)
blocking_gates = [r for r in results if not r.passed]
ready = len(blocking_gates) == 0
```
El readiness usa `r.passed` (bool), que es `True` para WARNING (porque `passed=True`
en el gate). Esto significa que si BUG-02 retorna WARNING con `passed=True`,
el readiness NO cambia — sigue siendo READY_FOR_PUBLICATION. **El fix de WARNING
no tiene efecto en readiness pero SÍ mejora el mensaje del gate.**

**Fix Aprobado**: Modificar `_financial_validity_gate` para retornar WARNING
con `passed=True` cuando haya defaults, incluyendo los campos affected en details.
El readiness no se afecta porque `passed=True`. Este es un fix seguro.

**Paso 1**: Leer `_extract_financial_data()` para confirmar estructura del assessment.

**Paso 2**: Leer `NoDefaultsValidator` para confirmar que `can_calculate=True`
no equivale a "fuentes no-default".

**Paso 3**: Modificar `_financial_validity_gate` para agregar check secundario:
```python
# Check de fuentes: si hay defaults, es WARNING aunque can_calculate=True
financial_sources = assessment.get("financial_sources", {})
DEFAULT_SOURCES = {"default", "legacy_hardcode", "legacy_fixed"}
has_defaults = any(
    financial_sources.get(f) in DEFAULT_SOURCES
    for f in ("adr_cop", "occupancy_rate", "direct_channel_percentage")
)
if has_defaults and passed:
    return PublicationGateResult(
        gate_name="financial_validity",
        passed=True,  # No bloquea, solo advierte
        status=GateStatus.WARNING,
        message="Financial data uses default/legacy values — Tier C evidence",
        value=True,
        suggestion="Run onboarding with real data to improve evidence tier",
        details={
            "default_sources": {k: v for k, v in financial_sources.items()
                             if v in DEFAULT_SOURCES}
        }
    )
```

**NOTA**: Este es el código que T1.1 de FASE-RAIZ debió implementar. Si en la sesión
de FASE-RAIZ se implementó pero no se commiteó, buscar en stash/reflog antes de reescribir.

**Archivo a modificar**:
`modules/quality_gates/publication_gates.py`

**Verificación unitaria**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -c "
from modules.quality_gates.publication_gates import PublicationGatesOrchestrator
assessment = {
    'financial_sources': {
        'adr_cop': 'legacy_hardcode',
        'occupancy_rate': 'default',
        'direct_channel_percentage': 'default'
    },
    'financial_data': {'occupancy_rate': 0.5, 'direct_channel_percentage': 0.2, 'adr_cop': 300000}
}
orch = PublicationGatesOrchestrator()
result = orch._financial_validity_gate(assessment)
print(f'Status: {result.status.value}, Passed: {result.passed}')
print(f'Message: {result.message}')
"
# Esperado: status=WARNING, passed=True, message contiene 'Tier C'
```

---

### T2: Secciones faltantes — DIAGNÓSTICO y ACCIÓN

**ACLARACIÓN** (validación cruzada 2026-04-25):

`_build_manual_attention_table()` **SIEMPRE** retorna contenido (nunca vacío).
Retorna al menos una fila con "No se detectaron problemas que requieran atención manual".
**La sección "Validación de Calidad" es viable SIEMPRE**, no condicional.

**ANÁLISIS (basado en template diagnostico_v6_template.md)**:

El template NO contiene las secciones "Validación de Calidad" ni "Trazabilidad Brechas".
Las secciones equivalentes que SÍ existen son:

| Buscado | Existe | Nombre real en template/salida |
|---------|--------|------------------------------|
| "Validación de Calidad" | NO | No existe sección con ese nombre |
| "Trazabilidad Brechas" | NO | No existe sección con ese nombre |

La sección de brechas se inyecta como `${brechas_section}` (línea 84 del template)
sin nombre de sección visible en el markdown generado. El diagnóstico actual tiene:
"Brechas detectadas que afectan su presencia digital y reservas directas:" como
encabezado de párrafo, no como sección con nombre.

NOTA: Template V6 L125 YA tiene `## 📋 RESUMEN DE BRECHAS → OPORTUNIDADES`
con `${brechas_resumen_section}`. El nuevo encabezado `## 🔍 Trazabilidad` debe
ir en L82 antes/durante `${brechas_section}`, NO reemplazar L125.

**ACCIÓN REQUERIDA**:

**Paso 1**: Modificar `_build_brechas_section()` (L1771) para anteponer
encabezado `## 🔍 Trazabilidad: Brechas Identificadas` al contenido existente.
El método retorna `### [BRECHA N] nombre` por cada brecha — agregar el H2 antes.

**Paso 2**: Agregar sección `## ✅ Validación de Calidad` al template V6
(usar `${manual_attention_table}` o equivalente) — SIEMPRE visible porque
`_build_manual_attention_table()` siempre retorna contenido.

**Paso 3**: Verificar que ambos encabezados aparecen en el markdown generado.

---

### T3: seo_score ausente del JSON (D2 — absorbido de FASE-07)

**PRECISIÓN** (validación cruzada 2026-04-25):

El dict `report` se construye en main.py ~L2792-2875. NO incluye `seo_score`.
`_calculate_web_score()` (L1444) retorna `str(score)` pero no se persiste al JSON.
El diagnóstico markdown SÍ muestra "SEO Local: 25/100" (template funciona).

**Paso 1**: Localizar en main.py dónde se asigna el dict `report` (buscar `report = {` cerca L2792).

**Paso 2**: Agregar campo `seo_score` al dict. Opción recomendada (scope mínimo):
```python
'seo_score': int(template_data.get('seo_score', 0)),
```

Alternativa si template_data no disponible al momento de construir report:
```python
seo_score_str = diagnostic_gen._calculate_web_score(audit_result)
report['seo_score'] = int(seo_score_str) if seo_score_str else 0
```

**Verificación unitaria**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -c "
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
gen = V4DiagnosticGenerator()
# Test que retorna string numérico
print(type('25'))  # _calculate_web_score retorna str
print(int('25'))   # para JSON necesitamos int
"
```

---

## Tarea Separada: Modificar check_publication_readiness para incluir WARNING

Si el usuario quiere que los WARNING aparezcan en el readiness report
(para que sean visibles en el diagnóstico final), se necesita:

```python
# publication_gates.py L979-982, cambiar:
blocking_gates = [r for r in results if not r.passed]
# Por:
blocking_gates = [
    r for r in results
    if not r.passed or r.status == GateStatus.WARNING
]
ready = len([r for r in results if not r.passed]) == 0
status = "READY_FOR_PUBLICATION" if ready else "REQUIRES_REVIEW"
```

**Esta es una decisión de negocio**: ¿Los WARNING deben mostrarse como
"REQUIRES_REVIEW" o seguir siendo "READY_FOR_PUBLICATION"? Documentar
la decisión.

**Estado**: D1 — diferida a sesión dedicada.

---

## Archivos a Modificar

| Archivo | Cambio | Tarea |
|---------|--------|-------|
| `modules/quality_gates/publication_gates.py` | Fix BUG-02: implementar path WARNING + financial_sources | T1 |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Agregar encabezado "## 🔍 Trazabilidad" en `_build_brechas_section()` | T2 |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Agregar `## ✅ Validación de Calidad` + `${manual_attention_table}` | T2 |
| `main.py` | Agregar `seo_score` al dict `report` (~L2792) | T3 |

---

## Tests / Verificación

**Tests unitarios (sin costo API)**:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# T1: Test del gate financial_validity
./venv/Scripts/python.exe -c "
from modules.quality_gates.publication_gates import PublicationGatesOrchestrator
assessment = {
    'financial_sources': {
        'adr_cop': 'legacy_hardcode',
        'occupancy_rate': 'default',
        'direct_channel_percentage': 'default'
    },
    'financial_data': {'occupancy_rate': 0.5, 'direct_channel_percentage': 0.2, 'adr_cop': 300000}
}
orch = PublicationGatesOrchestrator()
result = orch._financial_validity_gate(assessment)
print(f'Status: {result.status.value}, Passed: {result.passed}')
print(f'Message: {result.message}')
print(f'Details: {result.details}')
"
# Esperado: status=WARNING, passed=True, message contiene 'Tier C'
```

**ÚNICA ejecución v4complete** (verifica los 5 issues simultáneamente):
```bash
./venv/Scripts/python.exe main.py v4complete \
    --url https://amaziliahotel.com/ \
    --nombre "Amazilia Hotel"
```

**Verificación post-v4complete**:
```bash
# T1: financial_validity WARNING
grep -A5 '"gate_name": "financial_validity"' output/v4_complete/gate_report.json

# T2: Encabezados en diagnóstico
grep -E "## .*[Tt]razabilidad|## .*Validación de Calidad" output/v4_complete/01_DIAGNOSTICO_*.md

# T3: seo_score en JSON
grep -i "seo_score" output/v4_complete/v4_complete_report.json

# T4: geo_flow_result existe
ls output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json
```

---

## Riesgos y Tradeoffs

1. **T1 BUG-02**: WARNING con `passed=True` NO cambia readiness — solo mejora el mensaje.
   Si se quiere que afecte readiness, requiere modificar `check_publication_readiness()`.
   Ver sección "Tarea Separada" más arriba.

2. **T2 (secciones)**: `_build_manual_attention_table()` SIEMPRE retorna contenido
   (confirmado). Agregar sección "Validación de Calidad" es seguro siempre.

3. **T3 (seo_score)**: `_calculate_web_score()` retorna `str`. Usar `int()` para JSON.
   No afecta el template markdown (ya funciona).

4. **T4 (geo_flow_result)**: El archivo SÍ se genera correctamente por
   v4_asset_orchestrator. El problema es timing (se genera después del
   diagnóstico). Aceptable que "Salud Técnica GEO" aparezca en segunda ejecución.

5. **D1 (WARNING en readiness)**: Diferida a sesión dedicada.

---

## Criterios de Completitud

- [ ] T1: financial_validity gate reporta WARNING (passed=True) para Tier C
- [ ] T1: gate_report.json tiene details.default_sources con campos affected
- [ ] T2: Diagnóstico tiene encabezado "## 🔍 Trazabilidad: Brechas Identificadas"
- [ ] T2: Diagnóstico tiene sección "## ✅ Validación de Calidad"
- [ ] T3: v4_complete_report.json incluye `seo_score` numérico
- [ ] T4: geo_flow_result disponible en timing correcto (verificar post-assets)
- [ ] 1 sola ejecución v4complete verifica los 5 issues
- [ ] run_all_validations.py --quick pasa
- [ ] log_phase_completion.py ejecutado
- [ ] Commit
