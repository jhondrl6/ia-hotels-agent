# FASE-5: Responsibility Contract - Relación explícita entre assets CORE y GEO

**ID**: FASE-5
**Objetivo**: Documentar y garantizar la relación correcta entre assets CORE y assets GEO para evitar confusión en implementación
**Dependencias**: FASE-4 (Sync Contract implementado)
**Duracion estimada**: 1-2 horas
**Skill**: systematic-debugging

---

## Contexto del Problema

El sistema genera múltiples versiones de schema y otros assets:

```
03_PARA_TU_WEBMASTER/
    hotel_schema.json              ← CORE (del pipeline original)
    hotel_schema_rich.json         ← GEO (del enrichment)
    faq_schema.json                ← CORE (del pipeline original)
    faq_schema_rich.json          ← GEO (del enrichment)
```

**Pregunta crítica**: ¿El webmaster debe implementar ambos? ¿Cuál reemplaza a cuál?

### Regla de Oro

> **NUNCA REEMPLAZAR, SIEMPRE ENRIQUECER**
>
> Los assets CORE son obligatorios.
> Los assets GEO son enrichment ADICIONAL.

---

## Arquitectura de Responsabilidades

### Asset Classification

| Tipo | Significado | Prioridad | Obligatorio |
|------|-------------|-----------|-------------|
| **CORE** | Generado por pipeline original | 1 (primero) | Sí |
| **GEO** | Generado por GEO enrichment | 2 (después) | Sí (si score < 68) |
| **ADVISORY** | Recomendación, no archivo | - | No |

### Dependency Graph

```
                    ┌─────────────────────┐
                    │   CORE ASSETS       │
                    │ (Pipeline original) │
                    └──────────┬──────────┘
                               │
               ┌───────────────┼───────────────┐
               │               │               │
               ▼               ▼               ▼
        ┌───────────┐   ┌───────────┐   ┌───────────┐
        │hotel_schema│   │faq_schema │   │boton_ws   │
        │   .json   │   │  .json    │   │  .html    │
        └───────────┘   └───────────┘   └───────────┘
               │               │               │
               │      ┌────────┴────────┐      │
               │      ▼                 ▼      │
               │  ┌───────────┐  ┌────────────┐ │
               │  │faq_schema │  │boton_ws    │ │
               │  │  _rich    │  │  _rich    │ │
               │  └───────────┘  └────────────┘ │
               │      GEO ENRICHMENT            │
               └─────────────────────────────────┘
```

---

## Tareas

### Tarea 1: Crear AssetResponsibilityContract

**Objetivo**: Documentar explícitamente qué asset implementar y en qué orden

**Archivos afectados**:
- `modules/geo_enrichment/asset_responsibility_contract.py` (NUEVO)

**Criterios de aceptacion**:
- [ ] Método `get_implementation_order(core_assets, geo_assets)` retorna lista ordenada
- [ ] Método `get_replacement_rule(asset_type)` indica si es enrichment o reemplazo
- [ ] Documentación clara para cada asset

```python
@dataclass
class AssetResponsibility:
    filename: str
    type: AssetType  # CORE | GEO | ADVISORY
    priority: int  # 1 = primero
    mandatory: bool
    replaces: str | None  # Si reemplaza otro asset
    enriched_by: str | None  # Si es enriquecido por otro
```

### Tarea 2: Crear template de entrega unificado

**Objetivo**: El delivery package incluye guía de qué implementar

**Criterios de aceptacion**:
- [ ] Template que indica orden de implementación
- [ ] Checkboxes para webmaster
- [ ] Notas de compatibilidad

### Tarea 3: Integrar en v4_asset_orchestrator

**Objetivo**: El orchestrator incluye el contract en el delivery

**Criterios de aceptacion**:
- [ ] asset_responsibility_contract se genera automáticamente
- [ ] Se incluye en el delivery package

---

## Tests Obligatorios

| Test | Criterio de Exito |
|------|-------------------|
| `test_responsibility_order.py` | CORE va antes que GEO |
| `test_no_replacement.py` | GEO nunca reemplaza CORE |
| `test_enrichment_chain.py` | chain correcto |

**Comando de validacion**:
```bash
python -m pytest tests/geo_enrichment/test_asset_responsibility.py -v
```

---

## Post-Ejecucion

1. Marcar FASE-5 como completada en README.md
2. Documentar en capabilities.md

---

## Criterios de Completitud

- [ ] AssetResponsibilityContract implementado
- [ ] Regla "NUNCA REEMPLAZAR" garantizada
- [ ] Template de entrega incluye orden
- [ ] Tests pasan
