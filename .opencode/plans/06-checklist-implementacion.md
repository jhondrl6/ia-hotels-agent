# Checklist Maestro de Implementación

**Proyecto**: Corrección Trazabilidad "Calidad Garantizada" + Reconección Módulos→Diagnóstico
**Inicio**: 2026-04-24
**Actualizado**: 2026-04-25 (auditoría profundizada: 18 hallazgos)
**Total fases**: 3
**Contextos**: `.opencode/context/auditoria_calidad_garantizada_20260424.md` + auditoría profundizada sesión 2026-04-25
**Decisiones**: `00-decisiones-deprecacion.md`

---

## Estados de Fases

| Fase | Estado | Sesión | Completada |
|------|--------|--------|------------|
| FASE-TRAZABILIDAD-DOCS | ⬜ Pendiente | Nueva sesión requerida | ❌ |
| FASE-TRAZABILIDAD-RAIZ | ⬜ Pendiente | Nueva sesión requerida | ❌ |
| FASE-TRAZABILIDAD-VALIDATE | ⬜ Pendiente | Nueva sesión requerida | ❌ |

---

## FASE-TRAZABILIDAD-DOCS: Correcciones Documentales

- [ ] README.md L306: "6" → "9 Publication Gates (6 blocking + 3 advisory)"
- [ ] README.md: Agregar descripción gates 7-9
- [ ] v4_complete.md L95: Remover `v4_coherence_validator`
- [ ] publication_gates.py L5-13: Docstring "5 critical" → "9 gates"
- [ ] AGENTS.md: Sincronizar coherence score
- [ ] log_phase_completion.py ejecutado
- [ ] Commit

---

## FASE-TRAZABILIDAD-RAIZ: Unificación + Cableado + Reconección + Deprecaciones

### T0: Unificación de detectores (DEP-03)
- [ ] `_identify_brechas()` refactorizada para delegar en `detect_pains()`
- [ ] Umbrales duplicados ELIMINADOS (L2027 geo<60, L2061 mobile<70, L2116 citability<30)
- [ ] Umbrales ahora vienen de `detect_pains()`: geo<70, mobile<50, citability<50
- [ ] Nuevos pain_ids en brechas: `no_org_schema`, `no_analytics_configured`, `ai_crawler_blocked`, `low_ia_readiness`
- [ ] Traducción Pain→Brecha con narrativa comercial para cada nuevo pain_id
- [ ] `detect_pains()` ahora detecta `no_og_tags` (bidireccional)
- [ ] Todo pain_id de brechas existe en `PAIN_SOLUTION_MAP`
- [ ] Todo pain_id de brechas tiene `ServiceEntry` en `SERVICE_CATALOG`

### T1-T2: Cableado Publication Gates
- [ ] Leer métodos `_*_gate()` en publication_gates.py (9 gates)
- [ ] Construir assessment dict en main.py con TODAS las keys requeridas
- [ ] Insertar `PublicationGatesOrchestrator.run_all()` en main.py v4complete
- [ ] Generar `gate_report.json` en output_dir
- [ ] Mostrar resumen de gates en consola

### T1.1: Fix financial_validity gate (CRÍTICA #1 + BUG-02)
- [ ] Modificar `_financial_validity_gate()` para pasar `sources` a NoDefaultsValidator
- [ ] Agregar `financial_sources` al assessment dict en main.py
- [ ] WARNING si mayoría (>50%) default/hardcode
- [ ] BLOCKED si TODOS son default
- [ ] 2 nuevos tests para financial source validation

### T3-T4: Trazabilidad en diagnóstico
- [ ] Agregar `gate_results` param a `generate()`
- [ ] Template: `${GATE_VALIDATION_SECTION}` con tabla de 9 gates
- [ ] Template: trazabilidad brechas→servicios (pain_id → ServiceEntry → asset)
- [ ] Pasar `gate_results` desde main.py

### T4.1: Unificar SEO (DEP-01)
- [ ] `_calculate_web_score()` ahora es wrapper de `calcular_score_seo()`
- [ ] Algoritmo custom antiguo (L1375-1393) ELIMINADO
- [ ] SEO mostrado al cliente = SEO usado en score_global (sin dualidad)

### T4.2: Unificar IAO (DEP-02)
- [ ] IAO usa `ia_readiness.overall_score` como fuente primaria
- [ ] CHECKLIST_IAO es solo fallback (cuando ia_readiness no disponible)
- [ ] `_calculate_iao_score_from_audit()` refactorizada

### T7: Restaurar IA metrics en V6 (D11, D13, RES-01)
- [ ] `${ia_metrics_table}` insertado en template V6
- [ ] `_build_geo_problems_table()` renombrado/expandido
- [ ] Incluye fila geo_flow_result "Salud Técnica GEO" (RES-03)
- [ ] 14 crawlers bloqueados AHORA visibles para el cliente

### T8: Fix bug escala crawler (MENOR #7 → BUG-01)
- [ ] Línea 1927: `> 50` → `> 0.5`
- [ ] 15pts IAO restaurados en fallback CHECKLIST_IAO

### T9: Hallazgos positivos (D15, RES-02)
- [ ] `_build_positive_findings()` implementada
- [ ] `${positive_findings}` en `_prepare_template_data()`
- [ ] `${positive_findings}` insertado en template V6
- [ ] Muestra: HTTPS, WhatsApp, GBP stats, redes sociales

### T10: geo_flow_result complementario (D12, RES-03)
- [ ] Cubierto por T7 (fila en ia_metrics_table)
- [ ] Nota en `${regional_transparency}` si geo_flow < 40

### T5: Tests (16 total)
- [ ] 1-12: Tests PublicationGatesOrchestrator (originales)
- [ ] 13: `test_identify_brechas_uses_detect_pains`
- [ ] 14: `test_crawler_scale_fix`
- [ ] 15: `test_positive_findings_generated`
- [ ] 16: `test_ia_metrics_table_in_output`
- [ ] Todos los tests pasan

### T11: Limpieza código muerto (D14)
- [ ] Variables no usadas por V6 etiquetadas como `# DEPRECATED`
- [ ] `_calculate_web_score()` wrapper tiene docstring de deprecación
- [ ] `_extraer_elementos_iao()` etiquetado como `# FALLBACK only`

### T6: Documentación
- [ ] CHANGELOG.md actualizado (formato CONTRIBUTING.md)
- [ ] DEP-01, DEP-02, DEP-03 documentados
- [ ] BUG-01, BUG-02 documentados
- [ ] RES-01, RES-02, RES-03 documentados
- [ ] log_phase_completion.py ejecutado
- [ ] Commit

---

## FASE-TRAZABILIDAD-VALIDATE: Única Prueba v4complete

- [ ] v4complete ejecutado UNA vez: `--url https://amaziliahotel.com --nombre "Amazilia Hotel"`
- [ ] gate_report.json existe con 9 gates
- [ ] financial_validity gate reporta sources (WARNING esperado para Tier C)
- [ ] Gate 9 (proposal_asset_alignment) ejecutado
- [ ] Diagnóstico incluye "Validación de Calidad" (9 gates)
- [ ] Diagnóstico incluye "Trazabilidad Brechas → Servicios"
- [ ] **NUEVO**: Diagnóstico incluye tabla "Métricas de Acceso para IA"
- [ ] **NUEVO**: Tabla IA muestra crawlers bloqueados (14 para Amazilia)
- [ ] **NUEVO**: Tabla IA muestra geo_flow_result "Salud Técnica GEO"
- [ ] **NUEVO**: Diagnóstico incluye sección "✅ Lo que ya funciona"
- [ ] **NUEVO**: Sección positiva menciona WhatsApp, HTTPS, GBP stats
- [ ] Cada brecha mapea a un servicio (sin huérfanas)
- [ ] Número de brechas ≈ número de pains (alineados)
- [ ] SEO score único (sin dualidad, mismo valor en score_global)
- [ ] IAO score = ia_readiness.overall_score (coincide con audit_report.json)
- [ ] Crawler access score > 0.5 (BUG-01 corregido, ya no siempre False)
- [ ] Nombre en doc: "Amazilia Hotel" (NO "amaziliahotel")
- [ ] VALIDATION_RESULTS.md creado
- [ ] CHANGELOG.md actualizado (cierre)
- [ ] log_phase_completion.py ejecutado
- [ ] sync_versions.py ejecutado
- [ ] run_all_validations.py --quick pasa
- [ ] doctor.py --status sin errores
- [ ] Commit final

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

**COBERTURA**: 4/4 CRÍTICAs originales + 1 NUEVA CRÍTICA + 2 NUEVAS ALTAS cubiertas.
15/18 hallazgos cubiertos en el plan. 3 diferidos (no bloquean).

---

## Dependencias

```
FASE-TRAZABILIDAD-DOCS ──┐
                          ├──→ FASE-TRAZABILIDAD-VALIDATE
FASE-TRAZABILIDAD-RAIZ ──┘  (requiere AMBAS completadas)
```

---

## Deprecaciones Resueltas en Este Proyecto

| DEP # | Función/Módulo deprecado | Reemplazo |
|-------|-------------------------|-----------|
| DEP-01 | `_calculate_web_score()` custom | `calcular_score_seo()` via CHECKLIST_SEO |
| DEP-02 | CHECKLIST_IAO standalone | `ia_readiness.overall_score` |
| DEP-03 | Umbrales duplicados en `_identify_brechas()` | `detect_pains()` como fuente única |
