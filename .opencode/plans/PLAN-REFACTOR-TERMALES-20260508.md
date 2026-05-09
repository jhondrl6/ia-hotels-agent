# Plan Maestro: Refactorizacion v4complete — Termales Santa Rosa de Cabal

> **URL objetivo**: http://www.termales.com.co/  
> **Analisis base**: `.opencode/context/ANALISIS_V4COMPLETE_TERMALES_20260508.md` (v2.0.0)  
> **Workflow guia**: `.agents/workflows/phased_project_executor.md` (v2.10.0)  
> **Regla de sesion**: 1 fase por sesion. Sin excepciones.  
> **Presupuesto iteraciones**: max 60 por fase.  

---

## Resumen Ejecutivo

El pipeline v4complete entrega documentos **no publicables** para Termales Santa Rosa de Cabal debido a 7 causas raiz validadas contra codigo vivo y sitio real. Este plan corrige los bugs criticos, mejora la deteccion de presencia (WhatsApp/Schema), enriquece los generadores con datos de contexto, y evalua cambios de policy en gates.

**Hallazgos criticos a corregir**:
- D1: Template engine `string.Template` incompatible con sintaxis Jinja2 `{{if}}...{{endif}}` en propuesta comercial
- D2: `coherence_validator` verifica catálogo estatico en vez de `generated_assets`
- D3: `monthly_report` es 100% tabla hardcodeada — nunca lee `asset_generation_report.json`
- D4: `SitePresenceChecker` falla silenciosamente (catch-all `except Exception`) → falsos negativos WhatsApp/Schema
- A5: `ContentScrubber` sin regla para detectar `[PENDING_*]` markers
- A6/A7: Generadores (FAQ, indirect_traffic) usan contenido generico sin datos del sitio
- B3: Gate `proposal_asset_alignment` es WARNING no bloqueante por diseno (evaluar cambio a BLOCKED)

---

## Estructura de Fases

| Fase | ID | Tipo | Contenido | Comando largo |
|------|-----|------|-----------|---------------|
| PRE | FASE-PRE | Preparacion | Saneamiento, validaciones base, estructura evidence | No |
| 1-A | FASE-1-A | Implementacion | FIX-1 Template engine + FIX-2 Coherence validator | No |
| 1-B | FASE-1-B | Implementacion | FIX-4 Scrubber [PENDING*] + FIX-3 monthly_report data-driven | No |
| 2-A | FASE-2-A | Implementacion | FIX-5 SitePresenceChecker + FIX-6 indirect_traffic + FIX-7 FAQ | No |
| 2-B | FASE-2-B | Verificacion E2E | **v4complete Termales** + verificar outputs vs metricas | **Si** |
| 2-PATCH | FASE-2-PATCH | Correccion | M1: financial_evidence_tier context, M4: PENDING_ONBOARDING in llms_txt, M5/M6: SitePresence WhatsApp/Schema, M7: placeholder phone | No |
| 3 | FASE-3 | Policy | FIX-9 proposal_asset_alignment policy + FIX-10 Onboarding gate Tier C | No |
| RELEASE | FASE-RELEASE-4.43.0 | Cierre | Version bump, CHANGELOG, GUIA_TECNICA, validaciones finales | No |

---

## Dependencias entre Fases

```
FASE-PRE
    |
    v
FASE-1-A ----> FASE-1-B
    |               |
    +---------------+
            |
            v
        FASE-2-A
            |
            v
        FASE-2-B  (v4complete unico del plan)
            |
            v
        FASE-3
            |
            v
    FASE-RELEASE-4.43.0
```

- FASE-1-A y FASE-1-B pueden ejecutarse en cualquier orden tras FASE-PRE, pero se recomienda secuencial.
- FASE-2-A **requiere** FASE-1-A y FASE-1-B completadas.
- FASE-2-B **requiere** FASE-2-A completada, porque el v4complete de verificacion E2E debe ejecutarse con todos los fixes criticos y de contenido ya aplicados.
- FASE-3 puede ejecutarse en paralelo logico con FASE-2-B, pero se recomienda despues para evaluar los gates con el nuevo pipeline.
- FASE-RELEASE requiere todas las anteriores.

---

## Archivos a Modificar (consolidado)

| Fix | Archivo | Lineas | Cambio |
|-----|---------|--------|--------|
| FIX-1 | `modules/commercial_documents/v4_proposal_generator.py` | ~1103-1106 | Reemplazar `string.Template` por pre-procesador de condicionales `{{if}}...{{endif}}` |
| FIX-1 | `modules/commercial_documents/templates/propuesta_v6_template.md` | ~85-90,111-113 | Validar compatibilidad con nuevo motor |
| FIX-2 | `modules/commercial_documents/coherence_validator.py` | ~518-538 | `_check_promised_assets_exist()` usa `generated_assets` del pipeline, no `is_asset_implemented()` |
| FIX-3 | `modules/asset_generation/monthly_report_generator.py` | ~170-182 | Tabla dinamica leyendo `asset_generation_report.json` |
| FIX-4 | `modules/postprocessors/content_scrubber.py` | ~76-104 | Rule 6: `_fix_pending_markers()` con regex `\[PENDING_[A-Z_]+\]` + `block_publication=True` |
| FIX-5 | `modules/quality_gates/publication_gates.py` | ~816-821 | Hardening `except`: log completo + retornar `unknown` en vez de `None` |
| FIX-5 | `modules/asset_generation/site_presence_checker.py` | (varias) | Investigar y corregir fallo en Termales |
| FIX-6 | `modules/asset_generation/indirect_traffic_generator.py` | (varias) | Leer `audit_report.json` antes de recomendar acciones |
| FIX-7 | `modules/asset_generation/faq_generator.py` | (varias) | Scraping previo del sitio para extraer servicios reales |
| FIX-9 | `modules/quality_gates/publication_gates.py` | ~863 | Evaluar `passed=False, status=BLOCKED` cuando `alignment < 0.5` |
| FIX-10 | `modules/quality_gates/publication_gates.py` | (nuevo) | Onboarding gate para Tier C |

---

## Metricas de Exito (Post-Refactor)

1. `_render_template` procesa `{{if}}...{{endif}}` → propuesta sin marcadores crudos visibles
2. `coherence_validator._check_promised_assets_exist()` refleja assets REALMENTE generados (score esperado: ~0.57 si 3 de 7 faltan, no 1.0)
3. `monthly_report` muestra tabla dinamica basada en `asset_generation_report.json` (solo `can_use=True` marcados como entregados)
4. `ContentScrubber` detecta y bloquea documentos con `[PENDING_*]` (`block_publication=True`)
5. `SitePresenceChecker` reporta `unknown` en vez de fallar silenciosamente; gate no asume "no existe"
6. `whatsapp_button` se marca como `present_in_production` cuando existe en el sitio real
7. Gate `proposal_asset_alignment` evaluado para cambio de WARNING→BLOCKED (decision documentada)
8. Assets reflejan datos reales del hotel, no templates universales
9. Sin placeholders genericos (`+57 300 000 0000`, `—`, `Por confirmar`) en documentos finales

---

## Ejecucion v4complete Unica

**Solo en FASE-2-B.** El comando:

```bash
./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/
```

**Proposito**: Determinar si la implementacion de FIX-1 a FIX-7 fue efectiva.  
**Criterios de aceptacion post-v4complete**:
- `02_PROPUESTA_COMERCIAL_*.md` NO contiene `{{if}}...{{endif}}` sin procesar
- `coherence_validation.json` refleja assets realmente generados
- `monthly_report` muestra estados reales (no todos "Entregado")
- `SitePresenceChecker` detecta WhatsApp y Schema correctamente
- `llms_txt` NO contiene `[PENDING_ONBOARDING]`
- Sin `[PENDING_*]` en ningun documento final

**Evidencia obligatoria** (Protocolo de Evidencia Proactiva, phased_project_executor.md §Protocolo-Evidencia-Proactiva):
```bash
mkdir -p evidence/fase-2-B
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-2-B/
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-2-B/
cp output/v4_complete/{hotel_id}/v4_audit/*.json evidence/fase-2-B/
```

---

## Resultado Verificacion FASE-2-B

**Veredicto**: PARCIAL — 2/7 metricas pasadas

| # | Metrica | Estado | Detalle |
|---|---------|--------|---------|
| M1 | Sin `{{if}}...{{endif}}` en propuesta | ❌ FALLO | L114-116: `{{if financial_evidence_tier == "A" or financial_evidence_tier == "B"}}` sin procesar |
| M2 | Coherence refleja assets reales | ✅ PASA | overall_score: 0.89 (umbral 0.8) |
| M3 | monthly_report dinamico | ✅ PASA | 0 ocurrencias de "Geo Playbook" hardcodeado |
| M4 | Sin [PENDING*] en documentos | ❌ FALLO | `ESTIMATED_llms_20260508_203338.txt` contiene `[PENDING_ONBOARDING: usp/description]` |
| M5 | WhatsApp detectado | ❌ FALLO | gate_report no tiene `whatsapp_button` — FIX-5 no funciono en produccion |
| M6 | Schema detectado | ❌ FALLO | gate_report no tiene `schema_hotel` — FIX-5 no funciono en produccion |
| M7 | Sin placeholders genericos | ❌ FALLO | Propuesta L228: `+57 300 000 0000` |

**Proximo paso recomendado**: Nueva fase PATCH (FASE-2-C o FASE-PATCH-TERMALES) para corregir:
1. M1: El `{{if}}` indica que `financial_evidence_tier` no existe en el contexto — resolver la variable ausente
2. M4: `[PENDING_ONBOARDING]` indica que LLMSTXTGenerator recibe datos incompletos (usp/description missing)
3. M5/M6: SitePresence hardening no esta detectando WhatsApp/Schema en Termales — investigar por qué
4. M7: Phone number sigue siendo placeholder generico — el ContentScrubber no lo detecta

---

## Notas para el Orquestador

- **R3 Scope**: FASE-2-B contiene 1 comando largo (v4complete) + verificacion = dentro del limite. FASE-2-A contiene 3 fixes = dentro del limite.
- **R2 Iteraciones**: FASE-2-B es la mas pesada. Si el presupuesto de iteraciones se agota durante la verificacion post-v4complete, guardar evidencia inmediatamente y dejar docs cascade para sesion de recuperacion.
- **Subagente**: FASE-2-B DEBE evaluar si usa subagente para v4complete. Regla de decision: si (investigacion previa + verificacion + docs) < 30 iteraciones restantes, ejecutar directo; si no, subagente.
- **Docs cascade**: Cada fase ejecuta `log_phase_completion.py` al finalizar. La acumulacion en `09-documentacion-post-proyecto.md` se hace por fase. FASE-RELEASE genera CHANGELOG y GUIA_TECNICA oficiales.

---

---

## Estado del Plan

**Estado**: ✅ COMPLETADO — 2026-05-08 21:15
**Version final**: 4.43.0 (TERMALES-REFACTOR)

---

*Plan disenado en sesion: 2026-05-08*  
*Orquestador: Hermes Agent*  
*Workflow base: phased_project_executor.md v2.10.0*
