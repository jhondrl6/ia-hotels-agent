# FASE-E: v4complete Hotel Castilla Real + Análisis Post-Implementación

**ID**: FASE-E (FASE-5 en numeración nueva)
**Objetivo**: Ejecutar v4complete para Hotel Castilla Real con todos los fixes aplicados + generar análisis post-implementación verificando los 5 niveles.
**Dependencias**: TODAS las fases anteriores (FASE-1 a FASE-4 completadas). **FASE-0 completada (Opción E)** — decisión comercial en `09-documentacion-post-proyecto.md` §F.
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution`
**Comando largo**: 1 (v4complete)

---

## Contexto

Las FASE-1 a FASE-4 corrigieron 10 problemas del ROI_AUDIT.md. Esta fase ejecuta el pipeline completo para verificar que:

1. Los 10 fixes se reflejan correctamente en el output
2. Los 5 niveles de calidad son superados
3. El veredicto comercial final es claro y accionable

El análisis debe seguir el patrón de `fase-f-commercial-viability-pattern.md`:
- Distinguir entre "niveles técnicos superados" y "viabilidad comercial"
- Clasificar el veredicto como ✅ ENVIABLE, ⚠️ ENVIABLE CON DEUDAS COMERCIALES, o ❌ NO ENVIABLE
- Si hay deudas comerciales (ROI negativo), documentarlas explícitamente

### Métricas base (pre-fixes)

| Métrica | Valor |
|---------|-------|
| Coherence Score | 0.83 |
| Publication Gates | 10/11 |
| Blocking Issues | 0 |
| ROI 6m | -$5.367.168 COP / 0.3X |
| Veredicto | ⚠️ ENVIABLE CON DEUDAS COMERCIALES |

---

## Tareas

### Tarea 1: Ejecutar v4complete para Hotel Castilla Real

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && \
cmd.exe /c "venv\Scripts\python.exe main.py v4complete --url https://www.hotelcastillareal.com/"
```

**Duración esperada**: 5-15 minutos (depende de la velocidad de las APIs)

**Criterios de aceptación**:
- [ ] v4complete termina sin errores fatales
- [ ] Se generan: `01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md`, `02_PROPUESTA_COMERCIAL_*.md`, `financial_scenarios_*.json`
- [ ] Publication gates report disponible

### Tarea 2: Análisis post-implementación por niveles

Verificar cada nivel contra el output generado:

#### Nivel 1 — Bloqueantes de output (FASE-1)
- [ ] Sin "⚠️ Alertas Comerciales" en `02_PROPUESTA_COMERCIAL_*.md`
- [ ] Sin placeholder `[Espacio para casos de éxito...]`
- [ ] Nota de pain_ratio NO dice "porción del dolor abordable con IAO"
- [ ] Nota de pain_ratio dice "relación entre inversión y pérdida mensual"

#### Nivel 2 — Jerga y entregables (FASE-2)
- [ ] Sin "AEO" sin explicación en lenguaje de negocio
- [ ] Sin "UTMs" sin descripción funcional
- [ ] Sin "P1/P2/P3" — reemplazados por "Fase 1/2/3"
- [ ] Tabla de entregables: headers "Momento de entrega" + "Qué incluye"
- [ ] Sin "% confianza" en tabla de entregables

#### Nivel 3 — Trazabilidad (FASE-C)
- [ ] `financial_scenarios.json` muestra `adr_source` correcto
- [ ] Frontmatter `version` NO es "4.0.0" (debe ser ≥ v4.53.0)
- [ ] Cadena de fallback ADR funcionando

#### Nivel 4 — Pulido (FASE-D)
- [ ] Sin tabla de APIs (OpenRouter, Gemini, Perplexity)
- [ ] Párrafo de transparencia presente
- [ ] `tier_explanation` en JSON
- [ ] Nota pain_ratio 20% vs 41% en diagnóstico

#### Nivel 5 — Transparencia
- [ ] Coherence score (comparar con baseline 0.83)
- [ ] Publication gates (comparar con baseline 10/11)
- [ ] Sin nuevas regresiones

### Tarea 3: Redactar informe de análisis

**Archivo**: `evidence/ROI-REFACTOR/analisis_post_implementacion.md`

**Estructura**:
```markdown
# Análisis Post-Implementación — ROI-REFACTOR
## Hotel: Castilla Real
## Fecha: [fecha]

### Resumen Ejecutivo
[Tabla con niveles 1-5 + veredicto]

### Nivel 1 — Bloqueantes
[Evidencia de cada fix]

### Nivel 2 — Jerga y Entregables
[Evidencia de cada fix]

### Nivel 3 — Trazabilidad
[Evidencia de cada fix]

### Nivel 4 — Pulido
[Evidencia de cada fix]

### Nivel 5 — Transparencia
[Coherence + gates + regresiones]

### Veredicto Comercial
[✅ ENVIABLE / ⚠️ ENVIABLE CON DEUDAS COMERCIALES / ❌ NO ENVIABLE]

### Deudas Comerciales (si aplica)
- ROI negativo: [monto y %. Si sigue negativo, documentar como deuda conocida]
- Otras deudas

### Comparativa Pre/Post
| Métrica | Pre-ROI-REFACTOR | Post-ROI-REFACTOR |
|---------|-----------------|-------------------|
| Alertas visibles | Sí | No |
| Placeholder testimonios | Sí | No |
| Nota pain_ratio | Engañosa | Corregida |
| Jerga técnica | Presente | Traducida |
| Entregables | % confianza | Momento de entrega |
| ADR fuente | Benchmark | Web scraping (si aplica) |
| Versión | 4.0.0 | [versión real] |
| APIs visibles | Sí | No |
| Tiers documentados | No | Sí |
```

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| v4complete | `cmd.exe /c "venv\Scripts\python.exe main.py v4complete --url https://www.hotelcastillareal.com/"` | Sin errores fatales |
| Validación rápida | `python3 scripts/run_all_validations.py --quick` | 3/5+ checks pass |
| Verificar output | `grep -c "⚠️ Alertas Comerciales" output/Castilla\ Real/v4_complete/02_PROPUESTA_COMERCIAL_*.md` | 0 coincidencias |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-5 como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items E1-E3 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar sección completa de FASE-5 con resultados
4. Ejecutar:
```bash
cmd.exe /c "venv\Scripts\python.exe scripts\log_phase_completion.py \
    --fase FASE-5 \
    --desc \"ROI-REFACTOR: v4complete Hotel Castilla Real + análisis post-implementación 5 niveles\" \
    --archivos-mod \"evidence/ROI-REFACTOR/analisis_post_implementacion.md\" \
    --tests 0 \
    --check-manual-docs"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete ejecutado sin errores fatales
- [ ] Output files generados (diagnóstico, propuesta, financial_scenarios.json)
- [ ] Nivel 1 verificado (sin alertas, sin placeholder, nota corregida)
- [ ] Nivel 2 verificado (sin jerga, entregables reformateados)
- [ ] Nivel 3 verificado (ADR fuente, versión dinámica)
- [ ] Nivel 4 verificado (APIs ocultas, tiers documentados, nota pain_ratio)
- [ ] Nivel 5 verificado (coherence, gates, sin regresiones)
- [ ] `analisis_post_implementacion.md` generado con veredicto
- [ ] Comparativa pre/post documentada
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO implementar nuevos fixes durante esta fase (solo verificar)
- Si algo falla, documentarlo en el análisis — NO corregir en esta fase
- Si el ROI sigue negativo, NO es un fallo — es una deuda comercial documentada
- El veredicto esperado es ⚠️ ENVIABLE CON DEUDAS COMERCIALES (ROI negativo)
- Máximo 60 iteraciones de agente
