# Prompt de Inicio de Sesión: FASE-TRAZABILIDAD-VALIDATE

**Proyecto**: Corrección Trazabilidad "Calidad Garantizada" + Reconección Módulos→Diagnóstico
**Fase**: 3 de 3 — Validación con Única Prueba v4complete
**Sesión**: Nueva (1 fase por sesión)
**Dependencia**: FASE-TRAZABILIDAD-RAIZ completada (detección unificada + gates cableados + template reconectado + deprecaciones)

---

## ⚠️ REGLA DE ORO: UNA SOLA EJECUCIÓN

> **Optimización de costos API**: Esta fase ejecuta **UNA SOLA** vez el comando `v4complete`. No se permiten re-ejecuciones. Si algo falla, se documenta como hallazgo — NO se re-intenta.

---

## Contexto

### Estado al iniciar esta fase
- `_identify_brechas()` → delega en `detect_pains()` (DEP-03: fuente única)
- `detect_pains()` → ahora detecta `no_og_tags` (bidireccional)
- `SERVICE_CATALOG` → cubre todos los pain_ids de brechas
- `PublicationGatesOrchestrator` → cableado en main.py v4complete
- `financial_validity` gate → inspecciona `financial_sources` (BUG-02)
- `_calculate_web_score()` → wrapper de `calcular_score_seo()` (DEP-01)
- IAO → `ia_readiness.overall_score` como primario (DEP-02)
- Template V6 → incluye `${ia_metrics_table}` (RES-01) y `${positive_findings}` (RES-02)
- `_build_geo_problems_table()` → incluye fila geo_flow_result (RES-03)
- Bug escala crawler corregido: `> 0.5` (BUG-01)
- 16 tests pasando en `tests/quality_gates/`

### Hotel de prueba
- **Nombre en Google Maps**: "Amazilia Hotel Campestre"
- **Nombre para doc**: "Amazilia Hotel" (DOS palabras, con espacio)
- **NO usar**: "amaziliahotel" (una palabra) como nombre del hotel
- **Sitio web**: https://amaziliahotel.com/
- **Hotel ID interno**: amaziliahotel (slug de URL)

---

## Tareas Específicas

### T1: Ejecutar v4complete (ÚNICA VEZ)

```bash
./venv/Scripts/python.exe main.py v4complete \
    --url https://amaziliahotel.com \
    --nombre "Amazilia Hotel"
```

**Lo que debe ocurrir**:
1. FASE 1: Hook generation
2. FASE 2: Validación cruzada
3. FASE 3: Escenarios financieros
4. FASE 4: Coherence Gate (CoherenceValidator)
5. **FASE 4.5 (NUEVA): Publication Gates (9 gates)** ← cableado
6. Diagnóstico con coherence_score + gate_results + trazabilidad + **IA metrics visibles** + **positive findings**
7. Assets condicionales
8. Propuesta comercial

### T2: Verificar Outputs — EXISTENCIA

```bash
ls -la output/v4_complete/
cat output/v4_complete/gate_report.json | python3 -m json.tool | head -40
head -10 output/v4_complete/01_DIAGNOSTICO_*.md
```

### T3: Verificar COHERENCIA CRUZADA entre sistemas

```bash
# Extraer pain_ids del diagnóstico
grep -oP 'pain_id.*' output/v4_complete/01_DIAGNOSTICO_*.md | sort -u

# Extraer servicios del diagnóstico
grep -A 20 "Trazabilidad Brechas" output/v4_complete/01_DIAGNOSTICO_*.md

# Verificar gate 9
python3 -c "
import json
with open('output/v4_complete/gate_report.json') as f:
    gates = json.load(f)
gate9 = [g for g in gates if g['gate_name'] == 'proposal_asset_alignment']
if gate9:
    print(f'Gate 9 (alignment): {gate9[0][\"status\"]} — {gate9[0][\"message\"]}')
else:
    print('ERROR: Gate 9 no encontrado')
print(f'Total gates ejecutados: {len(gates)}')
"
```

### T4: Checklist de Verificación Completa (18 criterios)

| # | Verificación | Comando | Esperado |
|---|-------------|---------|----------|
| 1 | gate_report.json existe | `ls output/v4_complete/gate_report.json` | Archivo presente |
| 2 | 9 gates en reporte | `python3 -c "import json; print(len(json.load(open('output/v4_complete/gate_report.json'))))"` | 9 |
| 3 | Gate 9 (alignment) ejecutado | grep en gate_report | proposal_asset_alignment presente |
| 4 | financial_validity reporta sources | grep "financial_sources\|default\|hardcode" gate_report.json | WARNING/BLOCKED si Tier C |
| 5 | Sección "Validación de Calidad" en diagnóstico | `grep -c "Validación de Calidad" output/v4_complete/01_*.md` | ≥1 |
| 6 | Sección "Trazabilidad Brechas" en diagnóstico | `grep -c "Trazabilidad Brechas" output/v4_complete/01_*.md` | ≥1 |
| 7 | **★ Tabla "Métricas de Acceso para IA"** | `grep -c "Métricas de Acceso para IA\|Accesibilidad IA" output/v4_complete/01_*.md` | ≥1 |
| 8 | **★ Crawlers bloqueados mencionados** | `grep -c "bloqueados\|GPTBot\|crawler" output/v4_complete/01_*.md` | ≥1 |
| 9 | **★ geo_flow_result referenciado** | `grep -c "Salud Técnica GEO\|geo_flow" output/v4_complete/01_*.md` | ≥0 (opcional si geo_flow existe) |
| 10 | **★ Sección "Lo que ya funciona"** | `grep -c "Lo que ya funciona" output/v4_complete/01_*.md` | ≥1 |
| 11 | **★ WhatsApp mencionado en positivos** | `grep -c "WhatsApp verificado" output/v4_complete/01_*.md` | ≥1 |
| 12 | **★ GBP stats en positivos** | `grep -c "Google Business Profile activo\|reviews" output/v4_complete/01_*.md` | ≥1 |
| 13 | coherence_score en header | `head -10 output/v4_complete/01_*.md \| grep coherence_score` | Presente |
| 14 | Nombre "Amazilia Hotel" en doc | `grep "Amazilia Hotel" output/v4_complete/01_*.md` | Presente (NO "amaziliahotel") |
| 15 | Cada brecha mapea a un servicio | Inspección visual de trazabilidad | Sin brechas huérfanas |
| 16 | **★ SEO único (no dual)** | `grep "seo_score\|web_score" output/v4_complete/v4_complete_report.json` | Mismo valor en diagnóstico y score_global |
| 17 | **★ IAO = ia_readiness** | Comparar diagnóstico IAO vs audit_report.json ia_readiness.overall_score | Valores coinciden (±1) |
| 18 | Sin errores en ejecución | Revisar log completo | Sin tracebacks |

★ = Criterios nuevos (auditoría profundizada 2026-04-25)

### T5: Documentar Resultados

Crear `output/v4_complete/VALIDATION_RESULTS.md`:

```markdown
# Resultados de Validación - FASE-TRAZABILIDAD-VALIDATE

**Fecha**: [fecha]
**Hotel**: Amazilia Hotel
**URL**: https://amaziliahotel.com/

## Gates Ejecutados

| Gate | Estado | Valor |
|------|--------|-------|
| hard_contradictions | ... | ... |
| evidence_coverage | ... | ... |
| financial_validity | ... | ... |
| coherence | ... | ... |
| critical_recall | ... | ... |
| ethics | ... | ... |
| content_quality | ... | ... |
| asset_confidence | ... | ... |
| proposal_asset_alignment | ... | ... |

## Métricas IA (NUEVO)

| Métrica | Score | Detalle |
|---------|-------|---------|
| Accesibilidad IA | ... | ... crawlers bloqueados |
| Citabilidad | ... | ... bloques |
| IA-Readiness | ... | ... |
| Salud Técnica GEO | ... | ... |

## Hallazgos Positivos (NUEVO)

[Extraer del diagnóstico]

## Trazabilidad Brechas → Servicios

[Tabla extraída del diagnóstico]

## Verificación de Deprecaciones

- [ ] DEP-01: SEO usa CHECKLIST_SEO (no algoritmo custom)
- [ ] DEP-02: IAO = ia_readiness.overall_score (no CHECKLIST_IAO standalone)
- [ ] DEP-03: _identify_brechas() usa detect_pains() (no umbrales duplicados)

## Issues Detectados

[Ninguno o lista]
```

---

## Criterios de Completitud

- [ ] v4complete ejecutado UNA sola vez para Amazilia Hotel
- [ ] gate_report.json generado con 9 gates
- [ ] financial_validity gate reporta WARNING para Tier C (5/7 fuentes default/hardcode)
- [ ] Gate 9 proposal_asset_alignment ejecutado
- [ ] Diagnóstico incluye "Validación de Calidad" + "Trazabilidad Brechas"
- [ ] **NUEVO**: Diagnóstico incluye tabla "Métricas de Acceso para IA" con crawlers bloqueados
- [ ] **NUEVO**: Diagnóstico incluye sección "✅ Lo que ya funciona" con WhatsApp, HTTPS, GBP
- [ ] **NUEVO**: SEO unificado (mismo valor diagnóstico = score_global)
- [ ] **NUEVO**: IAO coincide con ia_readiness.overall_score (≈33 para Amazilia)
- [ ] **NUEVO**: Bug escala crawler corregido (> 0.5, ya no > 50)
- [ ] Cada brecha en el diagnóstico tiene correspondencia en servicios
- [ ] El nombre en el documento es "Amazilia Hotel" (NO "amaziliahotel")
- [ ] VALIDATION_RESULTS.md creado (incluye secciones nuevas)
- [ ] CHANGELOG.md actualizado (cierre)
- [ ] REGISTRY.md actualizado vía log_phase_completion.py

## Post-Ejecución

```bash
# 1. Registrar fase
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-TRAZABILIDAD-VALIDATE \
    --desc "Validacion unica v4complete Amazilia Hotel: 9 gates + trazabilidad + IA metrics visibles + positive findings + SEO/IAO unificados + crawler fix verificado + 18 criterios" \
    --archivos-nuevos "output/v4_complete/VALIDATION_RESULTS.md" \
    --archivos-mod "CHANGELOG.md" \
    --tests "0" \
    --coherence 0.89 \
    --check-manual-docs

# 2. Sincronizar versiones
./venv/Scripts/python.exe scripts/sync_versions.py

# 3. Validación final
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status
```

## Archivos Involucrados

| Archivo | Tipo | Cambio |
|---------|------|--------|
| `output/v4_complete/gate_report.json` | Generado | 9 gates con source info |
| `output/v4_complete/01_DIAGNOSTICO_*.md` | Generado | Con trazabilidad + IA metrics + positivos |
| `output/v4_complete/02_PROPUESTA_*.md` | Generado | Propuesta |
| `output/v4_complete/VALIDATION_RESULTS.md` | Nuevo (manual) | Resultados con secciones nuevas |
| `CHANGELOG.md` | Modificar | Cierre |
