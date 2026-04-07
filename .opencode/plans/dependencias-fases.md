# Dependencias de Fases — Plan Unificado v2 (2026-04-06)

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
FASE-C (Opportunity Scorer)
   │
   ▼
FASE-D (GSC Integration) ◄── usa provider_registry + canonical_metrics de A
```

## Tabla de Fases

| # | ID | Descripcion | Depende de | Prioridad | Origen |
|---|-----|-------------|-----------|-----------|--------|
| 1 | FASE-A | Canonical Metrics + Provider Registry + Permission Modes | Ninguna | MEDIA | Goose patterns |
| 2 | FASE-B | Document Quality Gate + Content Scrubber | Ninguna (A es nice-to-have) | **ALTA** | seomachine #1,#2 |
| 3 | FASE-C | Priorizacion Ponderada con Impacto Estimado | B (docs pasan QA) | ALTA | seomachine #3 |
| 4 | FASE-D | Google Search Console Integration | A (registry), C (scores) | MEDIA | seomachine #4 |
| 5 | FASE-E | Micro-Content Local Generator | B (QA del contenido) | BAJA | seomachine #5 |

## Orden de Ejecucion Recomendado

```
Sesion 1: FASE-A (infraestructura base para FASE-D)
Sesion 2: FASE-B (previene documentos con errores visibles al cliente)
Sesion 3: FASE-C (mejora argumento comercial del diagnostico)
Sesion 4: FASE-D (datos reales de GSC — transformador)
Sesion 5: FASE-E (add-on comercial — cuando haya demanda)
```

NOTA: FASE-A y FASE-B son independientes. Si la prioridad es limpieza inmediata de documentos,
FASE-B puede ir primero. Pero FASE-A es base para FASE-D.

## Conflictos Potenciales

| Archivo | Fases que lo tocan | Resolucion |
|---------|-------------------|------------|
| `main.py` | A (--mode), B (scrub injection) | Secciones distintas, sin conflicto |
| `composer.py` | C (scores), D (GSC data) | D va despues de C, sin conflicto |
| `config/provider_registry.yaml` | A (crea con gsc anticipado), D (verifica) | A incluye entrada gsc con status pending |
| `publication_gates.py` | B (agrega gate #6) | Solo B lo toca |

## Archivos Archivados

| Archivo | Contenido | Motivo |
|---------|-----------|--------|
| `archived/05-prompt-fase-A-review-response.md` | Review Response Rate scraping | Diferido — no existe en codigo |
| `archived/05-prompt-fase-B-review-response.md` | Propagation to Commercial Docs | Diferido — depende del anterior |
