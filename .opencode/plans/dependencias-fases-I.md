# Dependencias de Fases - FASE-I (Autonomous Researcher)

## Diagrama de Dependencias

```
FASE-I-01
├── Módulo: autonomous_researcher.py (existente)
├── Módulo: data_assessment.py (existente)
├── Módulo: conditional_generator.py (existente)
└── Docs: capabilities.md (existente)

No hay dependencias entre tareas - son paralelas.
```

## Tabla de Conflictos Potenciales

| Archivo | Fase(s) que lo modifican | Tipo de conflicto |
|---------|--------------------------|------------------|
| `modules/asset_generation/data_assessment.py` | FASE-I-01 (Tarea 1) | Añade método nuevo |
| `modules/asset_generation/conditional_generator.py` | FASE-I-01 (Tarea 2) | Añade lógica de enrichment |
| `docs/contributing/capabilities.md` | FASE-I-01 (Tarea 3) | Añade fila a tabla |

**Conflicto bajo**: Todos los cambios son adiciones (nuevos métodos, nuevas filas).

## Arquitetura de Integración

```
                    ┌──────────────────────────────┐
                    │  DataAssessment.assess()     │
                    │  hotel_data, gbp_data        │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │  DataClassification          │
                    │  ¿LOW? ¿MED? ¿HIGH?         │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┴───────────────┐
                    │                              │
              ¿LOW?│                              │¿MED/HIGH
                    ▼                              ▼
    ┌──────────────────────┐          ┌──────────────────────┐
    │ AutonomousResearcher()│          │ Continuar sin        │
    │ .research(hotel_name)          │ research             │
    └──────────┬───────────┘          └──────────────────────┘
               │
     sources_checked[]
     data_found{}
     confidence
               │
               ▼
    ┌──────────────────────┐
    │ ResearchOutput        │
    │ (persistido en JSON)  │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ Enrich hotel_data     │
    │ con data_found        │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ ConditionalGenerator  │
    │ continúa generación   │
    └──────────────────────┘
```

## Verificación de Desconexiones

| Capability | Estado Actual | Estado Esperado | Verificación |
|------------|---------------|-----------------|--------------|
| AutonomousResearcher | huérfana | conectada | capabilities.md + flujo |

---

## Notas

- FASE-I es independiente de otras fases
- No modifica lógica existente, solo añade nuevo método y conexión
- Los scrapers (GBP, Booking, TripAdvisor, Instagram) son stubs intencionales - no se modifican
