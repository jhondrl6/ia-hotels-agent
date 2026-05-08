---
description: FASE-SOL2-B Asset Alignment & Gate Unification
version: 1.0.0
skill: phased_project_executor
---

> [!IMPORTANT]
> **NOTA POST-EJECUCION (2026-05-07)**
> Esta fase fue completada exitosamente. `PROPOSAL_SERVICE_TO_ASSET` ya tiene 7 entradas
> incluyendo `"Optimizacion para IA Generativa": "llms_txt"`. La unificacion de baseline
> entre coherence_validator y proposal_asset_alignment_gate ya fue implementada.
> Si estas leyendo este prompt en una sesion futura, NO re-ejecutar la unificacion.
> Verificar directamente que PROPOSAL_SERVICE_TO_ASSET tenga 7 entradas y continuar.

# FASE-SOL2-B: Asset Alignment & Gate Unification

**ID**: FASE-SOL2-B  
**Objetivo**: Eliminar la discrepancia entre coherence_validator y proposal_asset_alignment_gate, e incluir el 7mo servicio (AEO/llms_txt) en la validación.  
**Dependencias**: FASE-SOL2-A completada (limpieza de ghost refs).  
**Duración estimada**: 2-3 horas  
**Skill**: phased_project_executor, diagnostic-score-refactoring  

## Contexto

El sistema tiene DOS validadores que responden preguntas distintas con resultados inconsistentes:

| Validador | Pregunta | Resultado Termales |
|-----------|----------|-------------------|
| coherence_validator._check_promised_assets_exist() | ¿Los assets generados están en ASSET_CATALOG? | 6/6 OK, score=1.0 |
| proposal_asset_alignment_gate | ¿Los servicios prometidos tienen assets generados + presencia en sitio? | 2/6 aligned, 3 missing |

Además, GAP-C identifica que el 7mo servicio ("Optimización para IA Generativa" -> llms_txt) escapa al gate porque `PROPOSAL_SERVICE_TO_ASSET` solo tiene 6 entradas.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SOL2-A | ✅ Completada (asume dependencia) |
| PROP-PATCH | ✅ Completada |

### Base Técnica Disponible
- `modules/commercial_documents/coherence_validator.py` (líneas 494-526)
- `modules/quality_gates/publication_gates.py` (líneas 755-865)
- `modules/asset_generation/proposal_asset_alignment.py` (PROPOSAL_SERVICE_TO_ASSET líneas 20-27)
- `modules/commercial_documents/v4_proposal_generator.py` (líneas 839-908)
- `modules/asset_generation/asset_catalog.py` (is_asset_implemented, ASSET_CATALOG)

## Tareas

### Tarea 1: Incluir 7mo servicio en PROPOSAL_SERVICE_TO_ASSET
**Objetivo**: Cerrar GAP-C.

**Archivos afectados**:
- `modules/asset_generation/proposal_asset_alignment.py`
- `modules/quality_gates/publication_gates.py` (si ALL_PROMISED_SERVICES depende del dict)

**Criterios de aceptación**:
- [ ] `"Optimización para IA Generativa": "llms_txt"` agregado a PROPOSAL_SERVICE_TO_ASSET
- [ ] Verificar que ALL_PROMISED_SERVICES (usado por el gate) incluye la nueva entrada
- [ ] El gate ahora verifica llms_txt cuando score_aeo < 20
- [ ] Documentar en docstring que el dict ahora tiene 7 servicios base + condicionales

### Tarea 2: Unificar baseline de validación
**Objetivo**: Que coherence_validator y el gate usen la misma fuente de verdad para "qué se prometió".

**Análisis previo obligatorio**:
- [ ] Leer `_check_promised_assets_exist()` (coherence_validator.py:494-526)
- [ ] Leer `verify_proposal_asset_alignment()` (publication_gates.py:755-865)
- [ ] Identificar: ¿coherence_validator usa ASSET_CATALOG? ¿El gate usa PROPOSAL_SERVICE_TO_ASSET?
- [ ] Decisión de diseño:
  - **Opción C1**: coherence_validator también consulta PROPOSAL_SERVICE_TO_ASSET
  - **Opción C2**: El gate consulta ASSET_CATALOG en vez del dict estático
  - **Opción C3**: Crear un contrato único (service_manifest) que ambos consuman

**Criterios de aceptación**:
- [ ] Decisión documentada en comentario en ambos módulos
- [ ] Implementación de la opción elegida
- [ ] coherence_validator y gate ahora reportan consistencia para el mismo hotel

### Tarea 3: Documentar promised_by=["always"] en monthly_report
**Objetivo**: Cerrar GAP-F.

**Archivos afectados**:
- `modules/asset_generation/asset_catalog.py` (línea ~322)
- `modules/quality_gates/publication_gates.py` (docstring del asset_confidence gate)

**Criterios de aceptación**:
- [ ] Docstring en asset_catalog explica por qué monthly_report tiene promised_by=["always"]
- [ ] Docstring explica la causalidad: always → genera siempre → confidence 0.5 → low_quality_count
- [ ] Si se decide cambiar el comportamiento (ej: quitar "always"), documentar impacto

### Tarea 4: Validación
**Comando**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
pytest tests/quality_gates/test_publication_gates.py -v
pytest tests/commercial_documents/test_coherence_validator.py -v
```

**Criterios de aceptación**:
- [ ] 4/4 checks pasan
- [ ] Tests de publication_gates pasan
- [ ] Tests de coherence_validator pasan

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| test_proposal_asset_alignment | tests/asset_generation/test_proposal_asset_alignment.py | 7 servicios mapeados |
| test_coherence_validator_consistency | tests/commercial_documents/test_coherence_validator.py | Score coherente con gate |
| test_publication_gates_7th | tests/quality_gates/test_publication_gates.py | Gate detecta llms_txt missing |

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-SOL2-B ✅， fecha {timestamp}
2. **`06-checklist-implementacion.md`**: Estado ✅, iteraciones usadas
3. **`09-documentacion-post-proyecto.md`**:
   - Sección A: módulos nuevos (service_manifest si aplica)
   - Sección D: métricas de discrepancia resueltas
   - Sección E: archivos modificados listados
4. **Evidencia**: `git diff > evidence/SOL2-B/diff.patch`

## Criterios de Completitud (CHECKLIST)

- [ ] 7mo servicio (AEO/llms_txt) incluido en validación del gate
- [ ] coherence_validator y gate reportan alineación consistente
- [ ] promised_by=["always"] documentado con causalidad
- [ ] Tests nuevos pasan + existentes sin regresión
- [ ] run_all_validations.py --quick 4/4
- [ ] Documentación afiliada actualizada
- [ ] Máximo 60 iteraciones

## Restricciones

- **NO ejecutar v4complete** en esta fase
- **NO modificar v4_proposal_generator.py** salvo si es necesario para consistencia
- **NO eliminar PROPOSAL_SERVICE_TO_ASSET** sin reemplazo (rompería el gate)
- Si se crea service_manifest, mantenerlo simple (dict estático compartido, no base de datos)
- Máximo 60 iteraciones

## Prompt de Ejecución

```
Actúa como arquitecto de calidad de software.

OBJETIVO: Unificar la validación de asset alignment y cerrar GAP-C/GAP-F.

CONTEXTO:
- coherence_validator dice 6/6 OK, gate dice 2/6 aligned para el mismo hotel
- PROPOSAL_SERVICE_TO_ASSET tiene 6 entradas, faltando el 7mo (AEO/llms_txt)
- monthly_report tiene promised_by=["always"] que causa low_quality_count

TAREAS:
1. Agregar llms_txt a PROPOSAL_SERVICE_TO_ASSET y verificar gate
2. Analizar cómo unificar baseline entre coherence_validator y gate
3. Implementar unión elegida (C1, C2 o C3)
4. Documentar causalidad de promised_by=["always"]
5. Validar tests y run_all_validations.py

CRITERIOS:
- Ambos validadores consistentes para Termales
- 7 servicios cubiertos
- Documentación clara de diseño

VALIDACIONES:
- run_all_validations.py --quick 4/4
- Tests de ambos validadores pasan
```
