# FASE-4: Sync Contract - Sincronización narrativa entre diagnóstico comercial y GEO

**ID**: FASE-4
**Objetivo**: Crear el módulo que garantiza que la narrativa del diagnóstico comercial y el diagnóstico GEO no se contradigan
**Dependencias**: FASE-3 (GEO Enrichment Layer implementado)
**Duracion estimada**: 1-2 horas
**Skill**: systematic-debugging

---

## Contexto del Problema

El sistema genera dos tipos de diagnóstico independientes:

```
Diagnóstico Comercial:
- Pérdida mensual: $6.9M COP
- Problema: Dependencia de OTAs
- Propuesta: Paquete acelerador SEO

Diagnóstico GEO:
- Score: 82 (GOOD)
- Problema: No requiere acción
```

**Pregunta**: ¿Cómo se relacionan ambos? ¿Se contradicen?

### Reglas de Sincronización

| Combinación | GEO Score | Pérdida Comercial | Resultado | Tag |
|-------------|-----------|------------------|-----------|-----|
| A1 | EXCELLENT (86-100) | Alta | No contradictorio | "Problema es comercial, no técnico" |
| A2 | EXCELLENT | Baja | No contradictorio | "Hotel en buen estado técnico" |
| B1 | GOOD (68-85) | Alta | No contradictorio | "Brecha técnica contribuye" |
| B2 | GOOD | Baja | No contradictorio | "Hotel en buen estado" |
| C1 | FOUNDATION (36-67) | Alta | No contradictorio | "Brecha técnica confirma pérdida" |
| C2 | FOUNDATION | Baja | Investigar | "Inconsistencia - investigar" |
| D1 | CRITICAL (0-35) | Alta | No contradictorio | "Crisis técnica confirma pérdida" |
| D2 | CRITICAL | Baja | Error | "Error - verificar datos" |

---

## Tareas

### Tarea 1: Crear SyncContractAnalyzer

**Objetivo**: Analizar la relación entre diagnóstico comercial y GEO

**Archivos afectados**:
- `modules/geo_enrichment/sync_contract.py` (NUEVO)

**Criterios de aceptacion**:
- [ ] Método `analyze(commercial_diagnosis, geo_assessment)` retorna SyncResult
- [ ] Clasificación correcta según tabla de combinaciones
- [ ] Tags claros para cada caso

```python
@dataclass
class SyncResult:
    is_consistent: bool
    combination_tag: str  # ej: "Problema es comercial, no técnico"
    recommendation: str   # Qué decir en la propuesta
    contradiction_report: dict | None  # Si hay inconsistencia
```

### Tarea 2: Integrar en GEO Enrichment Layer

**Objetivo**: El enrichment layer usa sync para determinar qué generar

**Criterios de aceptacion**:
- [ ] geo_enrichment_layer recibe también commercial_diagnosis
- [ ] SYNC se ejecuta antes de generar assets
- [ ] Tags se incluyen en el output

### Tarea 3: Documentar reglas de sincronización

**Objetivo**: Que el equipo entienda las reglas

**Criterios de aceptacion**:
- [ ] Docstring en sync_contract.py explica cada combinación
- [ ] README del módulo incluye tabla de combinaciones

---

## Tests Obligatorios

| Test | Criterio de Exito |
|------|-------------------|
| `test_sync_excellent_alta.py` | Tag: "Problema es comercial, no técnico" |
| `test_sync_critical_alta.py` | Tag: "Crisis técnica confirma pérdida" |
| `test_sync_inconsistency.py` | Detecta inconsistencia y reporta |

**Comando de validacion**:
```bash
python -m pytest tests/geo_enrichment/test_sync_contract.py -v
```

---

## Post-Ejecucion

1. Marcar FASE-4 como completada en README.md
2. Actualizar capabilities.md con SyncContractAnalyzer

---

## Criterios de Completitud

- [ ] SyncContractAnalyzer implementada
- [ ] 8 combinaciones documentadas y funcionando
- [ ] Tags claros para cada caso
- [ ] Tests pasan
