# Plan Maestro: BUGFIX-LUXOR-2026-07-06 v4.60.1

## Origen

Contexto: `/.opencode/context/Historico/bugs_no_onboarding_luxor_2026-07-06.md`
Auditoría con doctrina validate-against-live-code — cada bug verificado contra código vivo del repo.
Ejecución origen: `main.py v4complete --url http://www.luxorhotel.com.co/` (motor v4.60.0)
Versión base: v4.60.0
Versión objetivo: v4.60.1
Fecha de creación: 2026-07-06

---

## Resumen Ejecutivo

Corrección de 5 bugs detectados en la ejecución v4complete de Luxorhotel, no relacionados con onboarding. Los bugs se agrupan por complejidad y riesgo: BUG-1 y BUG-2 son quick wins de bajo riesgo, BUG-4 (openrouter) es un fix de resiliencia, BUG-5 es higiene de pipeline, y BUG-6 (SPA rendering) es el de mayor complejidad técnica. BUG-4 parte gemini queda fuera del plan (configuración de credenciales — acción manual del usuario).

---

## Findings y Soluciones

| ID | Bug | Severidad | Solución | Archivo(s) | ¿En plan? |
|----|-----|-----------|----------|------------|-----------|
| BUG-1 | lat:0.0, lng:0.0 en `_audit_competitors` | P1 Alta | Usar `gbp_result.lat/lng` + validación de rango | `modules/auditors/v4_comprehensive.py` | SÍ |
| BUG-2 | `calc_result` UnboundLocalError en FASE-K | P3 Baja | Remover línea o referenciar variable válida del scope | `main.py` | SÍ |
| BUG-4a | openrouter 404 — modelo hardcoded | P2 Media | Externalizar modelo al `provider_registry.yaml` | `modules/auditors/llm_mention_checker.py` + `config/provider_registry.yaml` | SÍ |
| BUG-4b | gemini 403 — API key ausente | P2 Media | Configurar `GEMINI_API_KEY` en `.env` | N/A (acción usuario) | NO |
| BUG-5 | Content Scrubber bypass en FASE 3.6 | P3 Baja | Eliminar/reordenar bloque FASE 3.6 (dead code) | `main.py` | SÍ |
| BUG-6 | OG no detectado — sitio es SPA | P2 Media | Integrar Playwright como fallback para SPAs | `modules/auditors/v4_comprehensive.py` + `modules/auditors/seo_elements_detector.py` | SÍ |

---

## Matriz de Dependencias

```
FASE-1 (BUG-2 + BUG-1: quick wins)  ──────────┐
                                               │
FASE-2 (BUG-4a: openrouter)  ─────────────────┤  (independiente de FASE-1)
                                               │
FASE-3 (BUG-5: scrubber)  ────────────────────┤  (independiente de FASE-1 y FASE-2)
                                               │
FASE-4 (BUG-6: SPA rendering)  ───────────────┤  (independiente de FASE-1/2/3)
                                               │
FASE-5 (v4complete E2E + verificación)  ───────┤  (DEPENDIENTE de FASE-1 a FASE-4)
                                               │
FASE-RELEASE v4.60.1  ─────────────────────────┘  (DEPENDIENTE de FASE-5)
```

**Conflictos de archivos:**
- `main.py`: FASE-1 (BUG-2, ~L1942) y FASE-3 (BUG-5, ~L2372-2473) — secciones NO superpuestas
  - Resolución: FASE-1 edita L1942, FASE-3 edita L2372-2473. Sin conflicto.
- `modules/auditors/v4_comprehensive.py`: FASE-1 (BUG-1, L1159-1160) y FASE-4 (BUG-6, L505)
  - Resolución: FASE-1 edita `_audit_competitors`, FASE-4 edita `_run_seo_elements_audit`/`_run_full_audit`. Sin conflicto.

---

## Estructura de Fases

| Fase | Bugs | Tareas | delegate_task | Complejidad | Sesión |
|------|------|--------|---------------|-------------|--------|
| **FASE-1** | BUG-2 + BUG-1 | 4: fix BUG-2 + fix BUG-1 + tests + run tests | No (código puro, directo) | ⭐ Baja | Nueva |
| **FASE-2** | BUG-4a | 3: investigar catálogo OpenRouter + externalizar modelo + test mock | No (código puro + web_search) | ⭐⭐ Media | Nueva |
| **FASE-3** | BUG-5 | 3: investigar FASE 3.6 + eliminar/reordenar bloque + test E2E | No (código puro) | ⭐⭐ Media | Nueva |
| **FASE-4** | BUG-6 | 4: verificar Playwright + integrar fallback SPA + test + fallback graceful | No (código puro) | ⭐⭐⭐ Alta | Nueva |
| **FASE-5** | Verificación | 2: v4complete E2E + análisis post-fix | ✅ Sí (v4complete como subagente) | ⭐⭐ Media | Nueva |
| **FASE-RELEASE** | — | Docs cascade, version bump, sync | No | ⭐ Baja | Nueva |

**Total: 5 fases + 1 release = 6 sesiones**

---

## Fase de Mayor Complejidad Técnica

### ⭐⭐⭐ FASE-4: BUG-6 — SPA Rendering con Playwright

**Razones:**
1. **Nueva dependencia de runtime**: Playwright está instalado pero no se usa para renderizar SPAs antes del SEO audit
2. **Manejo de timeouts**: Integrar renderizado con timeout + fallback graceful si Playwright falla
3. **Detección de SPA**: Heurística para detectar app shell vacío (HTML con `<script>` pero sin og tags Y pocos meta tags)
4. **Riesgo de regresión**: Añade dependencia de runtime que puede fallar en CI/entornos sin browser instalado
5. **Múltiples archivos**: Posiblemente toca `v4_comprehensive.py`, `seo_elements_detector.py`, y/o `http_client.py`

**Por qué NO usar delegate_task:**
- Código puro en módulos de auditores + tests
- Overhead de spawn > beneficio para tareas secuenciales
- Budget directo: ~30-40 iters (investigación + fix + test + verificación)

---

## Fases con delegate_task

### FASE-5: v4complete como subagente
- Subagente ejecuta `v4complete` para Luxorhotel (5-10 min wall clock)
- Agente principal verifica output, análisis post-implementación, docs cascade
- **Protocolo de evidencia proactiva obligatorio**

---

## Bugs Fuera de Planificación

### BUG-4b: gemini 403 (configuración de credenciales)

- **Acción del usuario:** crear `GEMINI_API_KEY` en Google AI Studio (https://aistudio.google.com/apikey) y añadirla a `.env`
- No es fix de código, es setup de infraestructura. El código ya lee `GEMINI_API_KEY` correctamente (`llm_mention_checker.py:100`)
- **Prueba manual post-config:** ejecutar `python main.py v4complete --url http://www.luxorhotel.com.co/` y verificar que el log NO muestre `LLM query failed for gemini: 403`

---

## Métricas de Éxito (Post-Fix)

1. ✅ BUG-1: `_audit_competitors` usa `gbp_result.lat/lng` en lugar de `0.0`
2. ✅ BUG-2: No aparece `UnboundLocalError` para `calc_result` en log de FASE-K
3. ✅ BUG-4a: `llm_mention_checker.py` lee modelo del `provider_registry.yaml` (no hardcoded)
4. ✅ BUG-5: No aparece `[SKIP] Diagnostic document not available for scrubbing` en log
5. ✅ BUG-6: OG tags detectados para sitios SPA (cuando existen en HTML renderizado)
6. ✅ v4complete E2E: coherence score ≥ 0.80, sin nuevas regresiones
7. ✅ Todos los tests existentes pasan sin cambios
8. ✅ Nuevos tests de regresión pasan

---

## Archivos Involucrados

| Archivo | Fases | Cambios |
|---------|-------|---------|
| `main.py` | 1, 3 | Fix `calc_result` (L1942); eliminar/reordenar FASE 3.6 (L2372-2473) |
| `modules/auditors/v4_comprehensive.py` | 1, 4 | Fix lat/lng en `_audit_competitors` (L1159-1160); integrar Playwright fallback para SPA |
| `modules/auditors/llm_mention_checker.py` | 2 | Externalizar modelo hardcoded (L239) al registry |
| `config/provider_registry.yaml` | 2 | Verificar/actualizar `default_model` con modelo vigente |
| `modules/auditors/seo_elements_detector.py` | 4 | Posible modificación de `detect()` para aceptar HTML renderizado |
| `tests/test_google_places_client.py` | 1 | Test de regresión BUG-1 |
| `tests/test_financial_breakdown.py` | 1 | Test de regresión BUG-2 |
| `tests/auditors/test_seo_elements_detector.py` | 4 | Test SPA rendering con Playwright mock |
| `VERSION.yaml` | RELEASE | Bump a 4.60.1 |

---

## Reglas de Ejecución

- **R1**: 1 fase por sesión
- **R2**: Max 60 iteraciones por fase
- **R3**: Max 4 tareas o 3+1 comando largo por fase
- Cada fase ejecuta `log_phase_completion.py` al completar
- FASE-RELEASE NO registra fases anteriores (solo sync)
- Protocolo de evidencia proactiva obligatorio post-v4complete (FASE-5)
- **Verificación anti-deuda (§2.5 del workflow)**: Cada fase de implementación ejecuta `log_phase_completion.py` al terminar. FASE-RELEASE solo hace sync.
