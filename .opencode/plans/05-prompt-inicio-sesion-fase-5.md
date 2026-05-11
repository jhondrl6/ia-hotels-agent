# FASE-5: Verificación E2E — v4complete para Termales Santa Rosa de Cabal

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.  
> **Tipo de ejecución**: DIRECTA con comando largo (v4complete)  
> **Límite de iteraciones**: Máximo 60. Budget estimado: ~26 fijos + ~10 trabajo + ~10 docs = ~46.
>
> **Presupuesto de iteraciones**:
> - Leer plan + verificar estado: ~3
> - Ejecutar v4complete: 1 tool call (timeout=600, notify_on_complete=True)
> - Guardar evidencia: ~2
> - Verificar output + análisis: ~10
> - Docs cascade: ~10
> - Total: ~26

## Contexto previo

FASE-1 a FASE-4 completadas. Los 8 hallazgos están corregidos en código:
- H6: Coherence post-generación implementado
- H1/H5/H8: Propuesta completa con 8 servicios + gate 80%
- H7: Monthly report fail-safe
- H3/H4: Financiero normalizado

## Objetivo de esta fase

Ejecutar `v4complete` para Termales Santa Rosa de Cabal y verificar que los fixes funcionan en producción. Generar análisis de ejecución comparando el estado anterior (auditoría 2026-05-09) vs el estado post-fix.

### Tareas

- [ ] **T1: Ejecutar v4complete para Termales**
  - Comando: `./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co`
  - Usar: `terminal(timeout=600, notify_on_complete=True)`
  - Esperar a que termine completamente
  - NOTA: La ejecución puede tardar 5-10 minutos (scraping + APIs + generación de documentos + assets)

- [ ] **T2: Guardar evidencia proactiva (INMEDIATAMENTE después de que termine v4complete)**
  - Antes de cualquier verificación o análisis:
  ```bash
  mkdir -p evidence/FASE-5-VERIFICACION
  cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-5-VERIFICACION/
  cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-5-VERIFICACION/
  cp output/v4_complete/termales_santa_rosa_de_cabal/v4_audit/*.json evidence/FASE-5-VERIFICACION/ 2>/dev/null || cp output/v4_complete/*/v4_audit/*.json evidence/FASE-5-VERIFICACION/
  cp output/v4_complete/termales_santa_rosa_de_cabal/v4_complete_report.json evidence/FASE-5-VERIFICACION/ 2>/dev/null || cp output/v4_complete/*/v4_complete_report.json evidence/FASE-5-VERIFICACION/
  ```
  - Esto es OBLIGATORIO sin importar cuántas iteraciones queden.

- [ ] **T3: Verificar fixes contra criterios de aceptación**
  Para cada hallazgo, verificar en los JSONs/md generados:

  **H6 — Coherence post-generación:**
  - `v4_complete_report.json` debe tener `coherence_score_pre` y `coherence_score_post`
  - `coherence_score_post` debe reflejar assets realmente generados (no catálogo estático)
  - Si hay assets missing, `coherence_score_post < coherence_score_pre`

  **H1/H5 — Propuesta completa:**
  - `02_PROPUESTA_*.md` debe mencionar 8 servicios (no solo 3)
  - Debe haber sección de assets técnicos (analytics, indirect_traffic)

  **H8 — Gate robusto:**
  - `gate_report.json` → `proposal_asset_alignment.alignment_percentage` debe evaluarse contra umbral 0.8
  - Si alignment < 0.8, estado debe ser `BLOCKED` (no `WARNING`)

  **H7 — Monthly report:**
  - `asset_generation_report.json` → `monthly_report` debe estar generado o tener mensaje de fallback claro
  - Si BLOCKED, propuesta debe contener disclaimer

  **H3/H4 — Financiero:**
  - Suma de brechas en propuesta debe cuadrar exactamente con valor central
  - Propuesta debe distinguir pain_ratio (41%) de recovery_factor (20%)

- [ ] **T4: Generar análisis de ejecución**
  - Crear archivo: `evidence/FASE-5-VERIFICACION/analisis_ejecucion.md`
  - Contenido:
    1. **Resumen**: Estado general (PASS/PARTIAL/FAIL) por hallazgo
    2. **Métricas comparativas** (antes vs después):
       - Coherence score pre vs post
       - Número de servicios visibles en propuesta (3 → 8)
       - Gate 9 estado (WARNING → BLOCKED si aplica)
       - Suma de brechas vs valor central (diferencia en COP)
    3. **Hallazgos residuales**: Si algo NO se corrigió, explicar por qué
    4. **Recomendaciones**: Si se necesita otra fase, describirla

### Restricciones

- **NO** modificar código fuente en esta fase (solo verificación)
- **NO** ejecutar más de 1 vez v4complete (el usuario pidió "única ejecución")
- **SI** v4complete falla por timeout de APIs o network, reportar el estado parcial y copiar lo que exista en output/
- Prioridad: guardar evidencia > análisis > documentación

### Criterios de completitud

- [ ] v4complete ejecutado (completado o timeout documentado)
- [ ] Evidencia copiada a `evidence/FASE-5-VERIFICACION/`
- [ ] Análisis de ejecución escrito en `evidence/FASE-5-VERIFICACION/analisis_ejecucion.md`
- [ ] Estado de cada hallazgo documentado (PASS / PARTIAL / FAIL con justificación)

### Próxima sesión

FASE-RELEASE: Documentación oficial, version bump 4.43.0 → 4.44.0, CHANGELOG, GUIA_TECNICA.
