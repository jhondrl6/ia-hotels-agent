# FASE-TRAZABILIDAD-VALIDATE-v2: Verificacion Post-PATCH Forense

> **Sesion unica. Maximo 60 iteraciones.**
> **Trigger**: Validar que los 18 hallazgos + 4 issues T1-T4 fueron superados.

---

## Contexto

Version actual: **v4.36.0** (PATCH Forense AmaziliaHotel, 2026-04-26)

Cadena de fases completadas:
- FASE-TRAZABILIDAD-DOCS → v4.35.1
- FASE-TRAZABILIDAD-RAIZ → v4.35.1
- FASE-TRAZABILIDAD-VALIDATE → v4.35.1 (primera validacion, 4 issues T1-T4)
- FASE-TRAZABILIDAD-PATCH+SEO → v4.35.1 (fixes T1-T4)
- FASE-TRAZABILIDAD-REFINEMENT → v4.35.1
- PATCH Forense FASE-A/B/C/D → v4.36.0

**Objetivo**: Ejecutar UNA corrida v4complete para Amazilia Hotel y auditar que TODOS los hallazgos fueron superados.

---

## Tarea 1: Ejecutar v4complete

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --nombre "Amazilia Hotel"
```

**Capturar**: tiempo de ejecucion, exit code, coherence_score.

---

## Tarea 2: Auditar Diagnostic Markdown

Verificar en `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md` (el mas reciente):

### 2.1 Secciones Obligatorias
- [ ] `## ✅ Validación de Calidad` presente (T2 fix)
- [ ] `## 🔍 Trazabilidad: Brechas Identificadas` presente (T2 fix)
- [ ] `${brechas_section}` renderizado (no literal)
- [ ] `${manual_attention_table}` renderizado (no literal)
- [ ] `${positive_findings}` renderizado (D15 fix)
- [ ] `${ia_metrics_table}` renderizado con datos (D11 fix)

### 2.2 Metricas IA
- [ ] "Salud Técnica GEO" row presente en ia_metrics_table (T4 fix, D12)
- [ ] Crawlers bloqueados visibles (D13)
- [ ] Scores SEO/GEO/AEO/IAO presentes y numericos

### 2.3 Scores
- [ ] SEO Local score numerico (no N/A ni 0 si hay datos)
- [ ] Coherence score >= 0.8

### 2.4 Datos del Hotel
- [ ] Hotel name correcto (NO "amaziliahotel" sin espacio en titulo visible)
- [ ] Region: Eje Cafetero / Pereira / Risaralda
- [ ] Datos financieros con Tier C evidente (C1 fix)

---

## Tarea 3: Auditar JSON Report

Verificar en `output/v4_complete/v4_complete_report.json`:

- [ ] `seo_score` presente como entero (T3 fix)
- [ ] `coherence_score` >= 0.8
- [ ] `publication_ready` = true
- [ ] `gate_report` presente con resultados de 9 gates
- [ ] `financial_validity` gate muestra WARNING (no solo PASSED) si hay defaults (T1 fix)

---

## Tarea 4: Auditar Gate Report

Verificar en gate_report (JSON o en la salida del diagnostico):

- [ ] 9 gates ejecutados (6 blocking + 3 advisory)
- [ ] `financial_validity` tiene status WARNING cuando financial_sources contiene defaults
- [ ] `financial_validity` tiene `passed=True` (no bloquea publicacion)
- [ ] `financial_validity` details incluye `default_sources` list

---

## Tarea 5: Tabla Comparativa de Hallazgos

Generar tabla final:

| # | Hallazgo | Antes (v4.35.0) | Despues (v4.36.0) | Veredicto |
|---|----------|-----------------|-------------------|-----------|
| C1 | financial_validity defaults | Sin WARNING | WARNING + Tier C | ? |
| C2 | pains/brechas divergentes | Thresholds diferentes | Unificado detect_pains() | ? |
| C3 | SEO dual score | 2 algoritmos | Wrapper CHECKLIST_SEO | ? |
| C4 | IAO independiente | Standalone | Fallback ia_readiness | ? |
| D11 | Metricas IA eliminadas | Sin tabla | ia_metrics_table presente | ? |
| D12 | geo_flow invisible | Sin row | "Salud Técnica GEO" | ? |
| D13 | Crawlers no mencionados | Sin datos | En ia_metrics_table | ? |
| D14 | Dead code geo_problems | Dead code | ? | ? |
| D15 | Sin positivos | Sin seccion | positive_findings | ? |
| C5 | README "6 gates" | "6" | "9" | ? |
| C7 | Crawler scale bug | > 50 | > 0.5 | ? |
| T1 | financial_validity false positive | Solo PASSED | WARNING passed=True | ? |
| T2 | Secciones ausentes | Sin headers | Headers presentes | ? |
| T3 | seo_score JSON ausente | Sin campo | seo_score: int | ? |
| T4 | geo_flow timing | Sin row | Row presente | ? |

---

## Restricciones

1. **NO modificar codigo fuente.** Esta fase es SOLO validacion.
2. **NO ejecutar v4complete mas de UNA vez.** Si falla, reportar error y terminar.
3. Maximo 60 iteraciones del agente.
4. Documentar TODO hallazgo nuevo encontrado durante la validacion.

---

## Criterios de Completitud

- [ ] v4complete ejecutado exitosamente (exit code 0)
- [ ] Tareas 2-4 completadas con checklist
- [ ] Tabla comparativa (Tarea 5) generada
- [ ] Veredicto final: SUPERADO / PARCIAL / NO SUPERADO
- [ ] log_phase_completion.py ejecutado

---

## Post-Ejecucion (TIER 1 — Inmediato)

1. Marcar esta fase como completada en `06-checklist-implementacion.md`
2. Actualizar `dependencias-fases.md` con resultado
3. Actualizar `09-documentacion-post-proyecto.md` Section E
