# Dependencias de Fases — Plan Unificado v3 (2026-04-07)

## Nota Historica

Las fases A/B en CHANGELOG.md corresponden al CICLO AEO (Correccion Conceptual + Voice-Ready),
ya completadas en versiones anteriores. NO confundir con las fases de este plan.

Los prompts previos para "Review Response Rate scraping" (fases A/B originales de este plan)
NUNCA se implementaron. Se archivaron en `archived/`. El feature se difiere — el GBP activity_score
ya funciona sin el y las mejoras de seomachine tienen mayor ROI.

## Diagrama de Dependencias

```
FASE-A (Canonical Metrics + Registry + Modes)
   │
   ├────────────────────────────────────┐
   ▼                                    ▼
FASE-B (Quality Gate + Scrubber)     FASE-E (Micro-Content Local)
   │                                 (dep debil: B para QA del contenido)
   ▼
FASE-CORRECCION/HOTFIX-1 (Path + Region + Scrubber)
   │
   ▼
FASE-CORRECCION/HOTFIX-2 (OpportunityScorer + COP COP template)
   │
   ▼
FASE-CORRECCION/HOTFIX-3 (E2E validacion + LocalContent conexion)
   │
   ▼
FASE-C (Opportunity Scorer)
   │
   ▼
FASE-D (GSC Integration) ◄── usa provider_registry + canonical_metrics de A
```

## Tabla de Fases

| # | ID | Descripcion | Depende de | Prioridad | Origen |
|---|-----|-------------|-----------|-----------|--------|
| 1 | FASE-A | Canonical Metrics + Provider Registry + Permission Modes | Ninguna | MEDIA | Goose patterns | ✅ COMPLETADO |
| 2 | FASE-B | Document Quality Gate + Content Scrubber | Ninguna (A es nice-to-have) | **ALTA** | seomachine #1,#2 | ✅ COMPLETADO |
| 3 | FASE-C | Priorizacion Ponderada con Impacto Estimado | B (docs pasan QA) | ALTA | seomachine #3 | ✅ COMPLETADO |
| 4 | FASE-D | Google Search Console Integration | A (registry), C (scores) | MEDIA | seomachine #4 | ✅ COMPLETADO |
| 5 | FASE-E | Micro-Content Local Generator | B (QA del contenido) | BAJA | seomachine #5 | ✅ COMPLETADO |

## FASE-CORRECCION: Bug Fixes (E2E Crash Recovery) — 2026-04-07 ✅ COMPLETADO

Sesion de correccion de 3 bugs criticos y 2 desconexiones descubiertos en ejecucion E2E v4complete
con hotelvisperas.com. No es una FASE nominal del plan, sino hotfix sobre bugs encontrados
durante la ejecucion de v4complete. Se subdivide en 3 sub-fases secuenciales.

**Estado: COMPLETADO 2026-04-06** — Todos los bugs fueron resueltos y validados con
`v4complete --url https://www.hotelvisperas.com/es`.

### FASE-HOTFIX-1 (CRITICA): Path Fix + Region Fix + Desbloquear Scrubber/Gates ✅ COMPLETADO
| Bug | Descripcion | Archivo | Lineas |
|-----|-------------|---------|--------|
| BUG-1 (CRITICO) | `diagnostic_path` es `str` pero se usa `.exists()` como `Path`. Crash: AttributeError | main.py | 2120, 2141, 2266, 2272 |
| BUG-2 | FASE 3.6 (Content Scrubber) nunca se ejecuta como consecuencia de BUG-1 | main.py | ~2105-2184 |
| BUG-3 (CRITICO) | Region "default" se propaga a documentos del cliente | main.py | 1511, 2742-2755 |

- **Impacto**: Desbloquea FASE 3.6, 4.5, 4.6, 7, 10. Documentos cliente profesional sin placeholders.

### FASE-HOTFIX-2 (ALTA): OpportunityScorer en template + COP COP raiz ✅ COMPLETADO
| Desconexion | Sintoma | Causa |
|-------------|---------|-------|
| OpportunityScorer no se refleja | Brechas muestran % estatico, no scores ponderados | _inject_brecha_scores() no reemplaza placeholders del template |
| COP COP raiz en templates | "COP COP" x6 en diagnostico incluso si scrubber funciona | Templates generan duplicacion de moneda de entrada |

- **Fix**: Verificar mapeo de variables en templates y corregir inyeccion. Verificar que templates no generen "COP COP".
- **Archivos**: v4_diagnostic_generator.py, templates/

### FASE-HOTFIX-3 (ALTA): Re-ejecucion v4complete + Validacion + LocalContent conexion ✅ COMPLETADO
- Re-ejecutar v4complete con hotelvisperas.com
- Verificar 0 ocurrencias de "COP COP" y "en default" en output
- Verificar que FASE 3.6, 4.5, 4.6, 7, 10 ejecutan sin errores
- Opportunity scores visibles en brechas del diagnostico
- Conectar LocalContentGenerator al flujo (PainSolutionMapper -> local_content_page)
- **Archivos**: main.py, pain_solution_mapper.py, asset_catalog.py

### Validacion Final (despues de HOTFIX-3)

✅ **VALIDADO 2026-04-06** — Todos los checks pasaron en ejecucion real con hotelvisperas.com

```bash
venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es
```

Verificado en output:
- 0 ocurrencias de "COP COP" ✅
- 0 ocurrencias de "en default" / "de default" ✅
- FASE 3.6 ejecuta sin errores ✅ (13 fixes aplicados)
- FASE 4.5 Publication Gates pasa ✅ (READFOR_PUBLICATION)
- FASE 4.6 Consistency Checker ejecuta ✅
- FASE 7 Delivery Packaging ejecuta ✅
- FASE 10 Health Dashboard ejecuta ✅
- Opportunity scores visibles en brechas del diagnostico ✅ (45%/42%/40%/27%)

## Orden de Ejecucion Recomendado

```
Sesion 1: FASE-A (infraestructura base para FASE-D)
Sesion 2: FASE-B (previene documentos con errores visibles al cliente)
Sesion 3: FASE-CORRECCION (bugs E2E: Path, region, scrubber) ✅ COMPLETADO
Sesion 4: FASE-C (mejora argumento comercial del diagnostico)
Sesion 5: FASE-D (datos reales de GSC — transformador)
Sesion 6: FASE-E (add-on comercial — cuando haya demanda)
```

NOTA: FASE-A y FASE-B son independientes. Si la prioridad es limpieza inmediata de documentos,
FASE-B puede ir primero. Pero FASE-A es base para FASE-D.
FASE-CORRECCION debe ir ANTES de FASE-C porque sin el scrubber funcionando, los documentos
de FASE-C tendran bugs de contenido visibles al cliente.

## Conflictos Potenciales

| Archivo | Fases que lo tocan | Resolucion |
|---------|-------------------|------------|
| `main.py` | A (--mode), B (scrub injection), HOTFIX-1 (Path fix) | Secciones distintas, sin conflicto |
| `main.py` | HOTFIX-1 (Path fix + region), HOTFIX-3 (LocalContent) | Secciones distintas, sin conflicto |
| `v4_diagnostic_generator.py` | HOTFIX-1 (region fallback), HOTFIX-2 (scores, COP COP) | HOTFIX-2 va despues de HOTFIX-1 |
| `templates/` | HOTFIX-2 (COP COP en templates) | Solo HOTFIX-2 |
| `v4_diagnostic_generator.py` | C (scores), D (GSC data) | D va despues de C, sin conflicto |
| `config/provider_registry.yaml` | A (crea con gsc anticipado), D (verifica) | A incluye entrada gsc con status pending |
| `publication_gates.py` | B (agrega gate #6) | Solo B lo toca |

## Archivos Archivados

| Archivo | Contenido | Motivo |
|---------|-----------|--------|
| `archived/05-prompt-fase-A-review-response.md` | Review Response Rate scraping | Diferido -- no existe en codigo |
| `archived/05-prompt-fase-B-review-response.md` | Propagation to Commercial Docs | Diferido -- depende del anterior |
| `archived/dependencias-fases-HOTFIX.md` | HOTFIX v4.25.0 (3 sub-fases) | Fusionado en este documento (v3) |
