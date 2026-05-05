# SCORING-TRANSPARENCY — Plan de Fases v1.0.0

**Creado:** 2026-05-05
**Versión target:** v4.40.0 → v4.40.1
**Contexto validado:** `.opencode/context/scoring-transparency-context.md`
**Hotel de prueba:** Hotel Castilla Real (https://www.hotelcastillareal.com/)

---

## Objetivo

Transparentar el sistema de scoring de los 4 pilares (SEO, GEO, AEO, IAO) en el diagnóstico generado por `v4complete`. Actualmente solo GEO tiene breakdown y además filtra los factores FALSE, ocultando información al cliente.

---

## R3 Scope Evaluation

| Fase | Tareas | Comandos largos | ¿Pasa R3? |
|------|--------|-----------------|-----------|
| **SCORING-A** | 2 (investigar + implementar fix) | 1 (v4complete) | ✅ 2 tareas + 1 comando largo |
| **SCORING-B** | 3 (investigar template + agregar placeholders + agregar asignaciones) | 1 (v4complete) | ✅ 3 tareas + 1 comando largo |
| **SCORING-C** | 4 (log×3 fases + CHANGELOG + GUIA_TECNICA + validaciones) | 0 | ✅ 4 tareas + 0 comandos largos |

---

## Dependencia Diagram (ASCII)

```
┌──────────────────────────────────────────────────────────┐
│                 SCORING-TRANSPARENCY                      │
│                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌───────────┐ │
│  │ SCORING-A    │────▶│ SCORING-B    │────▶│ SCORING-C │ │
│  │ Fix filtrado │     │ 4 pilares    │     │ Docs      │ │
│  │              │     │ breakdown    │     │ cascade   │ │
│  └──────┬───────┘     └──────┬───────┘     └─────┬─────┘ │
│         │                    │                    │       │
│         ▼                    ▼                    ▼       │
│    v4_diagnostic        v4_diagnostic      CHANGELOG.md   │
│    _generator.py        _generator.py      REGISTRY.md    │
│    L276-285             L697-700           GUIA_TECNICA   │
│                          + template v6     validaciones   │
│                                                          │
│  Hotel test: hotelcastillareal (único para las 3 fases)  │
└──────────────────────────────────────────────────────────┘
```

**Regla de dependencia:** A → B → C. No hay conflictos de archivos entre A y B (tocan líneas distintas del mismo archivo, sin solapamiento).

---

## Iteration Budget Estimate

| Fase | Tipo | Budget estimado |
|------|------|----------------|
| SCORING-A | fix código + v4complete + verificar | ~35 iteraciones (15 fix + 1 v4complete bg + 15 verificar/docs) |
| SCORING-B | feature código + v4complete + verificar | ~35 iteraciones (15 feature + 1 v4complete bg + 15 verificar/docs) |
| SCORING-C | docs cascade (sin código) | ~25 iteraciones (5 logs + 10 docs + 10 validaciones) |

**Nota:** `v4complete` con `background=true` + `notify_on_complete=true` cuenta como 1 tool call, liberando el presupuesto de iteraciones del agente.

---

## Archivos Involucrados

| Archivo | Tipo de cambio | Fase |
|---------|---------------|------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | MOD (L276-285: fix filtrado) | SCORING-A |
| `modules/commercial_documents/v4_diagnostic_generator.py` | MOD (L697-700: 3 nuevas asignaciones) | SCORING-B |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | MOD (3 nuevos placeholders) | SCORING-B |
| `docs/CHANGELOG.md` | MOD (entrada v4.40.1) | SCORING-C |
| `docs/GUIA_TECNICA.md` | MOD (nota técnica) | SCORING-C |
| `docs/contributing/REGISTRY.md` | MOD (automático via log) | SCORING-C |

---

## Post-Ejecución: Comandos log_phase_completion.py

```bash
# SCORING-A
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-SCORING-A \
    --desc "Fix de filtrado en _build_scoring_breakdown() para mostrar todos los factores con marcador visual" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "0" \
    --check-manual-docs

# SCORING-B
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-SCORING-B \
    --desc "Extension del scoring breakdown a los 4 pilares (SEO, GEO, AEO, IAO)" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --tests "0" \
    --check-manual-docs

# SCORING-C
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-SCORING-C \
    --desc "Documentacion cascade: CHANGELOG v4.40.1, GUIA_TECNICA, REGISTRY, validaciones" \
    --archivos-mod "docs/CHANGELOG.md,docs/GUIA_TECNICA.md" \
    --check-manual-docs
```

---

## Hotel de Prueba (único)

| Campo | Valor |
|-------|-------|
| **Nombre** | Hotel Castilla Real |
| **URL** | https://www.hotelcastillareal.com/ |
| **Región** | eje_cafetero |
| **Uso** | Validación post-fix en SCORING-A y SCORING-B |

Comando de validación:
```bash
venv/Scripts/python.exe main.py v4complete \
    --url https://www.hotelcastillareal.com/ \
    --output output/test-scoring-transparency
```

---

## Criterios de Éxito Globales

1. Output del diagnóstico muestra TODOS los factores del checklist GEO (6/6), no solo los TRUE
2. Factores ausentes marcados visualmente (`~~tachado~~`)
3. Los 4 pilares (SEO, GEO, AEO, IAO) tienen breakdown visible
4. `scoring_methodology.md` y el output están alineados (ambos prometen y entregan 4 pilares)
5. `python scripts/run_all_validations.py --quick` pasa 4/4
6. Hotel Castilla Real: diagnóstico generado sin errores, todos los factores visibles

---

## Progreso

| Fase | Estado | Fecha | Sesión |
|------|--------|-------|--------|
| SCORING-A | ✅ Completada | 2026-05-05 | 20260505_1527 |
| SCORING-B | ✅ Completada | 2026-05-05 | 20260505_1545 |
| SCORING-C | ✅ Completada | 2026-05-05 | 20260505_1549 |
