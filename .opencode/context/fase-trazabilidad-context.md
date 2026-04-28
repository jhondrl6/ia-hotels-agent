# Contexto: FASE-TRAZABILIDAD — Hallazgos y Errores Amazilia Hotel

> Generado: 2026-04-27 | Baseline: sesiones 2026-04-25 | Version: v4.36.0

## Sitio de Prueba
- **Hotel**: Amazilia Hotel
- **URL**: https://amaziliahotel.com/
- **hotel_id**: amaziliahotel
- **Region**: Eje Cafetero, Pereira, Risaralda, Colombia

## Cadena de Fases Ejecutadas

| Fase | Version | Estado | Descripcion |
|------|---------|--------|-------------|
| FASE-TRAZABILIDAD-DOCS | v4.35.1 | ✅ Completada | Correcciones documentales (README, AGENTS, gates docstring) |
| FASE-TRAZABILIDAD-RAIZ | v4.35.1 | ✅ Completada | Unificacion pain/brecha, 9 gates, deprecaciones DEP-01-03 |
| FASE-TRAZABILIDAD-VALIDATE | v4.35.1 | ✅ Completada | Ejecucion v4complete Amazilia, identificacion 4 issues T1-T4 |
| FASE-TRAZABILIDAD-PATCH+SEO | v4.35.1 | ✅ Completada | Fixes T1-T4 implementados |
| FASE-TRAZABILIDAD-REFINEMENT | v4.35.1 | ✅ Completada | D1-D4 corrections + GEO source |
| PATCH Forense (FASE-A/B/C/D) | v4.36.0 | ✅ Completada | Schema dual, OTA label, open_graph, gate_report |

## Los 18 Hallazgos Originales

### Criticos (4 originales + 1 nuevo)

| ID | Hallazgos | Estado | Fix |
|----|-----------|--------|-----|
| C1 | `financial_validity` gate usaba defaults sin reportar fuentes | ✅ Fix T1 | WARNING + financial_sources + DEFAULT_SOURCES |
| C2 | `pains` y `brechas` con thresholds divergentes | ✅ Fix RAIZ | Delegacion total a `detect_pains()` |
| C3 | Dos calculos SEO diferentes (display vs score_global) | ✅ Fix DEP-01 | `_calculate_web_score()` wrapper de CHECKLIST_SEO |
| C4 | IAO score independiente de `ia_readiness.overall_score` | ✅ Fix DEP-02 | Demoted a fallback only |
| D11 | Tabla metricas IA eliminada de template V6 — 14 crawlers bloqueados invisibles | ✅ Fix RAIZ | Tabla ia_metrics_table restaurada |

### Altas (2 nuevas)

| ID | Hallazgos | Estado | Fix |
|----|-----------|--------|-----|
| D12 | `geo_flow_result` invisible para cliente | ✅ Fix T4 | "Salud Técnica GEO" row en ia_metrics_table |
| D13 | Crawlers bloqueados no mencionados en output | ✅ Fix RAIZ | ia_metrics_table incluye blocked_crawlers |

### Medias (2 nuevas)

| ID | Hallazgos | Estado | Fix |
|----|-----------|--------|-----|
| D14 | Dead code en `_build_geo_problems_table()` | ⚠️ Pendiente | Requiere revision de codigo |
| D15 | No hay seccion de hallazgos positivos (HTTPS, WhatsApp, GBP) | ✅ Fix v4.36.0 | `${positive_findings}` en template |

### Menores

| ID | Hallazgos | Estado | Fix |
|----|-----------|--------|-----|
| C5 | README decia "6 gates" en vez de "9" | ✅ Fix DOCS | Corregido a "9 Publication Gates" |
| C7 | Bug escala crawler: `> 50` deberia ser `> 0.5` (15 puntos IAO perdidos) | ✅ Fix RAIZ | Corregido en L1927 |

### Bugs Corregidos

| Bug | Descripcion | Fix |
|-----|-------------|-----|
| BUG-01 | Escala acceso crawler: `> 50` siempre False | `> 0.5` |
| BUG-02 | `financial_validity` no pasaba `sources` a NoDefaultsValidator | WARNING + sources dict |
| DEP-01 | `_calculate_web_score()` divergia de `calcular_score_seo()` | Wrapper CHECKLIST_SEO |
| DEP-02 | CHECKLIST_IAO standalone en vez de usar `ia_readiness.overall_score` | Fallback only |
| DEP-03 | `_identify_brechas()` logica duplicada con thresholds diferentes | Delega a `detect_pains()` |

### Issues Post-VALIDATE (T1-T4)

| Issue | Descripcion | Estado | Fix |
|-------|-------------|--------|-----|
| T1 (BUG-02) | `financial_validity` gate falso positivo — WARNING con Tier C | ✅ v4.36.0 | `publication_gates.py` L358-370 |
| T2 | Secciones "Validación de Calidad" y "Trazabilidad Brechas" ausentes | ✅ v4.36.0 | Template L110, L121 |
| T3 | `seo_score` ausente de `v4_complete_report.json` | ✅ v4.36.0 | `main.py` L2855-2856 |
| T4 | `geo_flow_result` timing — "Salud Técnica GEO" no aparecia | ✅ v4.36.0 | `_build_geo_problems_table()` L1300 |

## Defecciones Pendientes (3 de 18)

| ID | Descripcion | Razon de deferral |
|----|-------------|-------------------|
| C10 | Benchmarks sin trace de fuente | Requiere diseno de trazabilidad para benchmarks regionales |
| D16 | Contexto regional hardcoded | Requiere diseno de dynamic regional context |
| D17 | Competidores stub (sin datos reales) | Requiere API de competidores |

## Decisiones Diferidas

| Decision | Descripcion | Estado |
|----------|-------------|--------|
| D1 | WARNING gates deberian cambiar readiness a REQUIRES_REVIEW? | Diferida a sesion dedicada |

## Comando de Verificacion

```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --nombre "Amazilia Hotel"
```
