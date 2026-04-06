# GAP-IAO-01: Medición Real de Visibilidad en IA (ChatGPT/Perplexity)

**ID**: GAP-IAO-01
**Tipo**: Gap de Medición
**Objetivo**: Conectar ProfoundClient con v4_diagnostic_generator para medición REAL de IA visibility
**Dependencias**: Ninguna (módulo ProfoundClient ya existe)
**Duración estimada**: 2-3 horas

---

## Problema Identificado

### Contexto

En los informes de diagnóstico y propuesta comercial aparece:

```
| **Optimización ChatGPT** | 70/100 | 10/100 | ✅ Superior |
| **Visibilidad en ChatGPT** (IAO) | | | Que cuando alguien pregunte a la IA, su hotel sea recomendado |
```

### El Gap

| Lo que PROMITE (marketing) | Lo que REALMENTE mide (código) |
|---------------------------|-------------------------------|
| "Visibilidad en ChatGPT" | Schema + FAQ + GBP (senales técnicas) |
| "Optimización ChatGPT" | ¿Tiene Schema.org? |
| "Cuando pregunte a la IA, sea recomendado" | ¿Cuántas reseñas tiene? |

### Módulos Involucrados

| Módulo | Estado |
|--------|--------|
| `modules/analytics/profound_client.py` | ✅ Existe, tiene `get_share_of_voice()` |
| `modules/delivery/generators/aeo_metrics_gen.py` | ✅ Usa ProfoundClient |
| `modules/commercial_documents/v4_diagnostic_generator.py` | ❌ NO usa ProfoundClient |

### Cálculo Actual (Proxy)

```python
# v4_diagnostic_generator.py - _calculate_iao_score()
IAO Score = Schema (40pts) + FAQ (30pts) + GBP (30pts)
```

**Esto mide: qué tan preparado está TÉCNICAMENTE para AI.**
**NO mide: si REALMENTE aparece en las respuestas de ChatGPT.**

---

## Solución Proporcionada

### Arquitectura Propuesta

```
                    ┌─────────────────────────┐
                    │   v4_diagnostic_generator │
                    │   _calculate_iao_score()  │
                    └───────────┬─────────────┘
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
    ┌─────────────────────┐          ┌─────────────────────┐
    │   CÁLCULO PROXY     │          │   PROFOUND CLIENT   │
    │   (Fallback si API  │          │   (Share of Voice   │
    │    no disponible)   │          │    Real)            │
    └─────────────────────┘          └─────────────────────┘
               │                                 │
               └────────────────┬────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │   IAO Score REAL        │
                    │   (0-100)               │
                    └─────────────────────────┘
```

### Implementación

#### Paso 1: Modificar `_calculate_iao_score()`

```python
def _calculate_iao_score(self, audit_result: V4AuditResult) -> str:
    """Calculate IAO (AI Advanced) score.
    
    Si ProfoundClient retorna datos reales, usa esos.
    Si no, fallback al cálculo proxy actual.
    """
    # Intentar obtener Share of Voice real
    try:
        from modules.analytics.profound_client import ProfoundClient
        profound = ProfoundClient()
        sov_data = profound.get_share_of_voice(
            domain=audit_result.hotel_data.get('url', ''),
            competitors=[]
        )
        if sov_data.get('data_source') == 'profound_api':
            return str(sov_data.get('ai_visibility_score', 0))
    except Exception:
        pass
    
    # Fallback: cálculo proxy actual
    return self._calculate_iao_score_proxy(audit_result)
```

#### Paso 2: Agregar Benchmark Real

El benchmark regional de 10/100 en el diagnóstico también es inventado.
Debería usar datos reales de Profound o marcar como "N/A" si no hay API.

---

## Tareas

### Tarea 1: Investigar API de Profound

- [ ] Verificar documentación de ProfoundClient
- [ ] Confirmar formato de respuesta de `get_share_of_voice()`
- [ ] Determinar qué campos usar para el score IAO

### Tarea 2: Modificar `_calculate_iao_score()`

- [ ] Agregar try/except para ProfoundClient
- [ ] Si API disponible: retornar score real
- [ ] Si no disponible: fallback al cálculo proxy actual
- [ ] Loggear cuando se usa fallback

### Tarea 3: Actualizar Templates

- [ ] Agregar nota cuando el score es "real" vs "estimado"
- [ ] Si benchmark es inventado, marcar como "N/A"

### Tarea 4: Tests

- [ ] Test con ProfoundClient mock (API disponible)
- [ ] Test con ProfoundClient fallback (API no disponible)
- [ ] Test que fallback no rompe nada

---

## Criterios de Éxito

- [ ] `v4_diagnostic_generator.py` usa `ProfoundClient.get_share_of_voice()`
- [ ] Si API retorna datos reales, el score IAO refleja Share of Voice real
- [ ] Si API no disponible, usa fallback proxy sin romper
- [ ] Logs indican claramente si se usó API real o fallback
- [ ] Plantilla de diagnóstico indica cuando el score es "real" vs "estimado"

---

## Archivos a Modificar

| Archivo | Acción |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Modificar `_calculate_iao_score()` |

---

## Notas

- El módulo `aeo_metrics_gen.py` YA usa ProfoundClient correctamente
- La desconexión es solo en `v4_diagnostic_generator.py`
- No requiere nuevo módulo, solo integración
