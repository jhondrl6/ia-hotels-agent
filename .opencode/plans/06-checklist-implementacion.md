# Checklist Maestro de Implementación

**Proyecto**: Corrección Trazabilidad "Calidad Garantizada" + Reconección Módulos→Diagnóstico
**Inicio**: 2026-04-24
**Actualizado**: 2026-04-25 (v5 — FASE-07 absorbida en FASE-06, 4 fases total, 1 sola ejecución v4complete)
**Total fases**: 4 (DOCS → RAIZ → VALIDATE → PATCH+SEO)
**Contextos**: `.opencode/context/auditoria_calidad_garantizada_20260424.md` + auditoría profundizada sesión 2026-04-25
**Baseline evaluación**: `.opencode/context/fase-trazabilidad-patch-eval.md`
**Decisiones**: `00-decisiones-deprecacion.md`

---

## Estados de Fases

| Fase | Estado | Sesión | Completada |
|------|--------|--------|------------|
|| FASE-TRAZABILIDAD-DOCS | ✅ Completada | 2026-04-25 | ✅ 2026-04-25 |
|| FASE-TRAZABILIDAD-RAIZ | ✅ Completada | 2026-04-25 | ✅ 2026-04-25 (commits 81a0391, e7157e2) |
|| FASE-TRAZABILIDAD-VALIDATE | ✅ Completada | 2026-04-25 | ✅ Baseline en `fase-trazabilidad-patch-eval.md` |
|| FASE-TRAZABILIDAD-PATCH+SEO (06) | ⬜ Pendiente | Nueva sesión requerida | ❌ (5 issues, 1 sola ejecución v4complete) |
|| ~~FASE-SEO-SCORE (07)~~ | ~~ABSORBIDA~~ | — | Absorbida como T3 de FASE-06 |

---

## FASE-TRAZABILIDAD-DOCS: Correcciones Documentales

- [x] README.md L306: "6" → "9 Publication Gates (6 blocking + 3 advisory)"
- [x] README.md: Agregar descripción gates 7-9
- [x] v4_complete.md L95: Remover `v4_coherence_validator`
- [x] publication_gates.py L5-13: Docstring "5 critical" → "9 gates"
- [x] AGENTS.md: Sincronizar coherence score
- [x] log_phase_completion.py ejecutado
- [x] sync_versions.py ejecutado
- [x] CHANGELOG.md actualizado
- [x] GUIA_TECNICA.md con nota técnica
- [x] run_all_validations.py --quick (4/4)
- [x] doctor.py --status sin errores
- [ ] Commit

---

## FASE-TRAZABILIDAD-RAIZ: Unificación + Cableado + Reconección + Deprecaciones

### T0: Unificación de detectores (DEP-03)
- [x] `_identify_brechas()` refactorizada para delegar en `detect_pains()`
- [x] Umbrales duplicados ELIMINADOS (L2027 geo<60, L2061 mobile<70, L2116 citability<30)
- [x] Umbrales ahora vienen de `detect_pains()`: geo<70, mobile<50, citability<50
- [x] Nuevos pain_ids en brechas: `no_org_schema`, `no_analytics_configured`, `ai_crawler_blocked`, `low_ia_readiness`
- [x] Traducción Pain→Brecha con narrativa comercial para cada nuevo pain_id
- [x] `detect_pains()` ahora detecta `no_og_tags` (bidireccional)
- [x] Todo pain_id de brechas existe en `PAIN_SOLUTION_MAP`
- [x] Todo pain_id de brechas tiene `ServiceEntry` en `SERVICE_CATALOG`

### T1-T2: Cableado Publication Gates
- [x] Leer métodos `_*_gate()` en publication_gates.py (9 gates)
- [x] Construir assessment dict en main.py con TODAS las keys requeridas
- [x] Insertar `PublicationGatesOrchestrator.run_all()` en main.py v4complete
- [x] Generar `gate_report.json` en output_dir
- [x] Mostrar resumen de gates en consola

### T1.1: Fix financial_validity gate (CRÍTICA #1 + BUG-02)
- [ ] ~~Modificar `_financial_validity_gate()` para pasar `sources` a NoDefaultsValidator~~ **NO implementado** — grep confirma CERO cambios en publication_gates.py
- [ ] ~~Agregar `financial_sources` al assessment dict en main.py~~ **NO implementado**
- [ ] ~~WARNING si mayoría (>50%) default/hardcode~~ **NO implementado** — GateStatus.WARNING no existe en el archivo
- [ ] ~~BLOCKED si TODOS son default~~ **NO implementado**
- [ ] ~~2 nuevos tests para financial source validation~~ **NO implementado**
- [ ] **SCOPE transferido a FASE-06 PATCH T1-BUG02** — ver `06-fase-trazabilidad-patch-issues.md`

### T3-T4: Trazabilidad en diagnóstico
- [x] Agregar `gate_results` param a `generate()`
- [x] Template: `${GATE_VALIDATION_SECTION}` con tabla de 9 gates
- [x] Template: trazabilidad brechas→servicios (pain_id → ServiceEntry → asset)
- [x] Pasar `gate_results` desde main.py

### T4.1: Unificar SEO (DEP-01)
- [x] `_calculate_web_score()` ahora es wrapper de `calcular_score_seo()`
- [x] Algoritmo custom antiguo (L1375-1393) ELIMINADO
- [x] SEO mostrado al cliente = SEO usado en score_global (sin dualidad)

### T4.2: Unificar IAO (DEP-02)
- [x] IAO usa `ia_readiness.overall_score` como fuente primaria
- [x] CHECKLIST_IAO es solo fallback (cuando ia_readiness no disponible)
- [x] `_calculate_iao_score_from_audit()` refactorizada

### T7: Restaurar IA metrics en V6 (D11, D13, RES-01)
- [x] `${ia_metrics_table}` insertado en template V6
- [x] `_build_geo_problems_table()` renombrado/expandido
- [x] Incluye fila geo_flow_result "Salud Técnica GEO" (RES-03)
- [x] 14 crawlers bloqueados AHORA visibles para el cliente

### T8: Fix bug escala crawler (MENOR #7 → BUG-01)
- [x] Línea 1927: `> 50` → `> 0.5`
- [x] 15pts IAO restaurados en fallback CHECKLIST_IAO

### T9: Hallazgos positivos (D15, RES-02)
- [x] `_build_positive_findings()` implementada
- [x] `${positive_findings}` en `_prepare_template_data()`
- [x] `${positive_findings}` insertado en template V6
- [x] Muestra: HTTPS, WhatsApp, GBP stats, redes sociales

### T10: geo_flow_result complementario (D12, RES-03)
- [x] Cubierto por T7 (fila en ia_metrics_table)
- [x] Nota en `${regional_transparency}` si geo_flow < 40

### T5: Tests (16 total)
- [x] 1-12: Tests PublicationGatesOrchestrator (originales)
- [x] 13: `test_identify_brechas_uses_detect_pains`
- [x] 14: `test_crawler_scale_fix`
- [x] 15: `test_positive_findings_generated`
- [x] 16: `test_ia_metrics_table_in_output`
- [x] Todos los tests pasan

### T11: Limpieza código muerto (D14)
- [x] Variables no usadas por V6 etiquetadas como `# DEPRECATED`
- [x] `_calculate_web_score()` wrapper tiene docstring de deprecación
- [x] `_extraer_elementos_iao()` etiquetado como `# FALLBACK only`

### T6: Documentación
- [x] CHANGELOG.md actualizado (formato CONTRIBUTING.md)
- [x] DEP-01, DEP-02, DEP-03 documentados
- [x] BUG-01, BUG-02 documentados
- [x] RES-01, RES-02, RES-03 documentados
- [x] log_phase_completion.py ejecutado
- [x] Commit (81a0391 + e7157e2)

---

## FASE-TRAZABILIDAD-VALIDATE: Única Prueba v4complete

Baseline documentado en `.opencode/context/fase-trazabilidad-patch-eval.md` (4 issues abiertos identificados).

- [x] v4complete ejecutado UNA vez: `--url https://amaziliahotel.com --nombre "Amazilia Hotel"`
- [x] gate_report.json existe con 9 gates
- [x] financial_validity gate reporta sources (WARNING esperado para Tier C)
- [x] Gate 9 (proposal_asset_alignment) ejecutado
- [x] **Issue abierto**: Diagnóstico incluye "Validación de Calidad" (9 gates) — nombre diferente
- [x] **Issue abierto**: Diagnóstico incluye "Trazabilidad Brechas → Servicios" — nombre diferente
- [x] **Issue abierto**: Tabla "Métricas de Acceso para IA" visible — parcialmente
- [x] **Issue abierto**: Tabla IA muestra crawlers bloqueados (14 para Amazilia)
- [x] **Issue abierto**: geo_flow_result "Salud Técnica GEO" referenciado
- [x] **Issue abierto**: Sección "✅ Lo que ya funciona" visible
- [x] Cada brecha mapea a un servicio (sin huérfanas)
- [x] Número de brechas ≈ número de pains (alineados)
- [x] SEO score único (sin dualidad, mismo valor en score_global)
- [x] IAO score = ia_readiness.overall_score (coincide con audit_report.json)
- [x] Crawler access score > 0.5 (BUG-01 corregido)
- [x] Nombre en doc: "Amazilia Hotel" (NO "amaziliahotel")
- [x] Publication Readiness: READY_FOR_PUBLICATION
- [x] Blocking issues: 0

**4 issues abiertos** → pasan a FASE-06 PATCH

---

## FASE-TRAZABILIDAD-PATCH+SEO (06): Corrección Unificada — 1 sola ejecución v4complete

**Dependencia**: FASE-TRAZABILIDAD-VALIDATE completada
**Baseline**: `.opencode/context/fase-trazabilidad-patch-eval.md`
**Optimización**: FASE-07 SEO-SCORE absorbida como T3. Antes: 2 ejecuciones v4complete. Después: 1 sola.

### T1: BUG-02 — financial_validity gate FALSE POSITIVE
- [ ] Modificar `_financial_validity_gate()` — implementar path WARNING + financial_sources (scope completo)
- [ ] WARNING con `passed=True` cuando `financial_sources` tiene defaults
- [ ] details.default_sources con campos affected
- [ ] Test unitario: `Status: WARNING, Passed: True, Message: contiene "Tier C"`
- [ ] Test integración: gate_report.json muestra status WARNING

### T2: Secciones faltantes en diagnóstico
- [ ] Modificar `_build_brechas_section()` (L1771) para anteponer `## 🔍 Trazabilidad: Brechas Identificadas`
- [ ] Agregar `## ✅ Validación de Calidad` al template V6 — SIEMPRE viable (`_build_manual_attention_table()` nunca vacío)
- [ ] Verificar ambos encabezados en diagnóstico generado

### T3: seo_score ausente del JSON (D2 — absorbido de FASE-07)
- [ ] Localizar dict `report` en main.py (~L2792)
- [ ] Agregar `'seo_score': int(template_data.get('seo_score', 0))` al report JSON
- [ ] Test unitario: `_calculate_web_score()` retorna string numérico, `int()` para JSON
- [ ] Integration: `grep -i "seo_score" output/v4_complete/v4_complete_report.json` → no vacío

### T4: geo_flow_result — Timing
- [ ] Ya genera datos reales (confirmado en baseline)
- [ ] Verificar timing post-assets (se genera después del diagnóstico)
- [ ] Aceptable que "Salud Técnica GEO" solo aparezca tras segunda ejecución

### T5: D1 — check_publication_readiness ignora WARNING
- [ ] **DIFERIDO**: Decisión de negocio requerida
- [ ] Opciones: WARNING → REQUIRES_REVIEW o mantener READY_FOR_PUBLICATION
- [ ] Sesión dedicada para esta decisión

### Verificación FASE-06 (ÚNICA ejecución v4complete)
- [ ] `./venv/Scripts/python.exe -c "from modules.quality_gates.publication_gates import..."` (unit test T1)
- [ ] `grep "Trazabilidad" output/v4_complete/01_DIAGNOSTICO_*.md`
- [ ] `grep "Validación de Calidad" output/v4_complete/01_DIAGNOSTICO_*.md`
- [ ] `grep -i "seo_score" output/v4_complete/v4_complete_report.json`
- [ ] `ls output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json`
- [ ] `./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --nombre "Amazilia Hotel"` (1 sola)
- [ ] `run_all_validations.py --quick` pasa
- [ ] `doctor.py --status` sin errores
- [ ] log_phase_completion.py ejecutado
- [ ] Commit

---

## Cobertura de Desconexiones (ACTUALIZADA)

| # | Desconexión | Severidad | Cubierta | Fase |
|---|-------------|-----------|----------|------|
| C1 | financial_validity gate default | CRÍTICA | ✅ SI | RAIZ T1.1 |
| C2 | pains vs brechas divergentes | CRÍTICA | ✅ SI | RAIZ T0 |
| C3 | Dos cálculos SEO (10 vs 25) | CRÍTICA | ✅ SI | RAIZ T4.1 (DEP-01) |
| C4 | IAO vs ia_readiness | CRÍTICA | ✅ SI | RAIZ T4.2 (DEP-02) |
| C5 | README 6→9 gates | MENOR | ✅ SI | DOCS |
| C6 | Workflow ghost command | MENOR | ✅ SI | DOCS |
| C7 | Bug escala crawler | MENOR→INCLUIDO | ✅ SI | RAIZ T8 (BUG-01) |
| C8 | geo_score dual (62 vs 23) | MENOR→INCLUIDO | ✅ SI | RAIZ T7/T10 (RES-03) |
| C9 | Múltiples coherence | MENOR | ◐ Parcial | RAIZ T1-T2 |
| C10 | Benchmarks sin trace | MENOR | ⬜ Diferida | Post-VALIDATE |
| D11 | IA metrics V6 eliminadas | NUEVA CRÍTICA | ✅ SI | RAIZ T7 (RES-01) |
| D12 | geo_flow invisible al cliente | NUEVA ALTA | ✅ SI | RAIZ T7/T10 (RES-03) |
| D13 | Crawlers bloqueados no mencionados | NUEVA ALTA | ✅ SI | RAIZ T7 (RES-01) |
| D14 | Código muerto _build_geo_problems | NUEVA MEDIA | ✅ SI | RAIZ T11 |
| D15 | Sin hallazgos positivos | NUEVA MEDIA | ✅ SI | RAIZ T9 (RES-02) |
| D16 | Contexto regional hardcoded | NUEVA BAJA | — | Aceptado (narrativa) |
| D17 | Competidores stub | NUEVA BAJA | ⬜ Diferida | Post-VALIDATE |
| D18 | Financial sources matiz | NUEVA BAJA | — | Documentado |
| T1 | financial_validity FALSE POSITIVE | ALTA | ⬜ PATCH+SEO-06 | PATCH T1 (scope ampliado: implementación completa) |
| T2 | Secciones diagnóstico faltantes | MEDIA | ⬜ PATCH+SEO-06 | PATCH T2 |
| T3 | seo_score ausente del JSON (D2) | MEDIA | ⬜ PATCH+SEO-06 | PATCH T3 (absorbido de FASE-07) |
| D1 | WARNING ignora readiness | MEDIA | ⬜ DIFERIDO | Sesión dedicada |

**COBERTURA**: 4/4 CRÍTICAs originales + 1 NUEVA CRÍTICA + 2 NUEVAS ALTAS cubiertas.
19/21 hallazgos cubiertos en el plan. 3 diferidos (no bloquean).

---

## Dependencias

```
FASE-TRAZABILIDAD-DOCS ──┐
                          ├──→ FASE-TRAZABILIDAD-VALIDATE
FASE-TRAZABILIDAD-RAIZ ──┘  (requiere AMBAS completadas)
                                    │
                                    └──→ FASE-06 PATCH+SEO (5 issues, 1 v4complete)
```

---

## Deprecaciones Resueltas en Este Proyecto

| DEP # | Función/Módulo deprecado | Reemplazo |
|-------|-------------------------|-----------|
| DEP-01 | `_calculate_web_score()` custom | `calcular_score_seo()` via CHECKLIST_SEO |
| DEP-02 | CHECKLIST_IAO standalone | `ia_readiness.overall_score` |
| DEP-03 | Umbrales duplicados en `_identify_brechas()` | `detect_pains()` como fuente única |
