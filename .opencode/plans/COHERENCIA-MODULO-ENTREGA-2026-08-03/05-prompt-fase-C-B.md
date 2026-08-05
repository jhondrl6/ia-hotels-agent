# FASE-C-B: Textos Dinámicos — D6 (performance) + D7 (reviews) + D8 (atribución GEO)

**ID**: COHERENCIA-FASE-C-B
**Objetivo**: Eliminar 3 textos estáticos que mienten: la explicación de Core Web Vitals (D6), el ejemplo "203 reseñas" (D7) y la atribución falsa "algoritmo de Google" (D8).
**Dependencias**: FASE-A ✅ (estructura del doc estable). Puede correr después de C-A (archivos disjuntos).
**Duración estimada**: 1 sesión (~35 iteraciones de 60).
**Skill**: `phased_project_executor` v2.13.0.

## Contexto

- **D6 (ALTA)**: el doc dice "Sin Datos de Campo — el sitio puede ser nuevo o tener tráfico bajo" cuando la causa real es `performance.status=ERROR` ("API key not valid"). Texto hardcodeado en v4_diagnostic_generator.py:1741 que no lee el estado real (reforzado por N9: execution_trace.skipped=["pagespeed_api"]).
- **D7 (MEDIA)**: "un hotel con 203 reseñas" (generator:316) vs 966 reviews reales del audit en el mismo doc.
- **D8 (MEDIA)**: GEO 78 atribuido a "algoritmo de Google"; es fórmula local de iah-cli (google_places_client.py:177-193: rating/5×30 + reviews/100×2 + fotos×0.5 + 10 + 10, /90×100). La fórmula es correcta; el problema es la ATRIBUCIÓN en el template.

Fuente completa: contexto §5 FASE-3 (D6/D7/D8).

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-C-A | ✅ Completada |
| FASE-C-B | ▶️ EN CURSO (esta sesión) |

## Modo de ejecución (delegate_task)

**DELEGADO PARCIAL — 2 tracks independientes vía subagentes** (regla executor branch trabajo paralelo). Los tracks NO comparten archivos y NO requieren imports del venv para editar/tests unitarios simples; el agente principal coordina, integra tests y hace docs.

> ⚠️ Regla WSL-venv: si algún track necesita EJECUTAR tests con imports del
> proyecto (bs4/selenium), ese track lo ejecuta el agente principal con
> `./venv/Scripts/python.exe`, NO el subagente.

### Track 1 (subagente) — D6 + D7 en `v4_diagnostic_generator.py`
Contexto para el subagente:
- D6: en L1741, leer `audit_result.performance.status/.message`:
  - `status == "ERROR"` → "API de PageSpeed no disponible (verificar clave)" (severidad naranja/rojo).
  - `status OK` sin field data → "El sitio puede ser nuevo o tener tráfico bajo" (amarillo).
- D7: en L316, parametrizar con `audit_result.gbp.reviews` o eliminar el ejemplo numérico.
- Tests unitarios en `tests/commercial_documents/`.

### Track 2 (subagente) — D8 en el template
Contexto para el subagente:
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — la atribución GEO está en las líneas **L112 y L228** del template (las "doc:140 / doc:299" del contexto son líneas del DOCUMENTO generado; el template usa variables `geo_score_breakdown` en otras posiciones). Buscar `grep -n "algoritmo propio de Google"` en el template → 2 hits esperados (L112 nota divergencia + L228 divergencia GEO).
  "algoritmo propio de Google Business Profile" → "algoritmo propio de IA Hoteles Agent sobre datos de Google Places (rating, reseñas, fotos, horario, web)".
- NO tocar la fórmula de `google_places_client.py` (correcta, contexto §4.2).
- Test de render: el doc generado contiene la atribución correcta.

### Coordinación (agente principal)
- Integrar resultados de ambos tracks, resolver conflictos.
- Ejecutar suites y validaciones.
- Verificación estática:
```bash
grep -rn "203 reseñas" modules/                              # → 0 hits
grep -rn "algoritmo propio de Google" modules/               # → 0 hits
grep -rn "El sitio puede ser nuevo o tener tráfico bajo" modules/  # → solo rama status OK
```

## Criterios de aceptación

- [ ] D6: con `performance.status=ERROR` el doc refleja "API de PageSpeed no disponible"; el texto de sitio nuevo solo aparece con status OK sin field data.
- [ ] D7: cero apariciones de "203 reseñas"; el número de reseñas proviene del audit.
- [ ] D8: atribución GEO correcta en template y doc renderizado.

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Suites afectadas | `./venv/Scripts/python.exe -m pytest tests/commercial_documents -q` | 0 regresiones |
| Validaciones | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | 4/4 |

## Post-Ejecución (OBLIGATORIO)

1. Marcar FASE-C-B ✅ en `dependencias-fases.md`, `09-checklist-implementacion.md`, `README.md`.
2. Actualizar `11-documentacion-post-proyecto.md` (B, D, E).
3. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-C-B \
    --desc "D6 performance dinámico + D7 reviews parametrizadas + D8 atribución GEO" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --tests "<N nuevos>" --check-manual-docs
```
> ⚠️ NO usar `--release` en fases intermedias (L3/L9) — solo en FASE-RELEASE.

## Criterios de Completitud (CHECKLIST)

- [ ] D6, D7, D8 cerrados según criterios
- [ ] Greps estáticos en 0 hits
- [ ] Tests pasan + 0 regresiones
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- Máximo 60 iteraciones (R2), contando coordinación de subagentes.
- NO ejecutar v4complete (única ejecución: FASE-E).
- NO tocar `publication_gates.py` ni fórmulas financieras.
- NO tocar `google_places_client.py` (fórmula geo_score correcta).
- Si un subagente falla o se atasca (síntomas §Síntomas-de-Agotamiento), re-spawn una sola vez con timeout mayor; si persiste, ejecutar el track directamente.
