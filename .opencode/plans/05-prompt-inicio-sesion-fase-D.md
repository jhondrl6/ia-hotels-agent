# FASE-D: Medición AEO Real — KPIs e Integración Analytics

**ID**: FASE-D  
**Objetivo**: Implementar framework de medición para AEO real (voice search KPIs)  
**Dependencias**: FASE-C completada  
**Duración estimada**: 2 horas  
**Skill**: `plan` + `data-science`

---

## Contexto

### Qué se implementó en FASE-C

- Google Assistant checklist
- Apple Business Connect guide  
- Alexa Skill blueprint
- voice_assistant_guide asset

### Qué falta (KB AEO_agent_ready.md)

| Métrica | Descripción | Estado |
|---------|-------------|--------|
| AI Visibility Score | % menciones en respuestas IA | ⚠️ Requiere API external |
| Share of Voice (SoV) | Cuota vs competidores | ⚠️ Requiere API external |
| Tasa de Citación | Frecuencia IA incluye enlace | ⚠️ Requiere API external |
| Voice Search Impressions | Llamadas de asistente al hotel | ⚠️ No medible sin plataforma |

---

## Tareas

### Tarea D.1: Diseñar KPI Framework para AEO

**Objetivo**: Crear estructura de datos para métricas de AEO.

**Referencia KB**: Sección [KPIS] líneas 296-316

**KPIs a incluir**:
- AI Visibility Score (0-100)
- Voice Readiness Index (composite)
- Share of Voice vs competitors
- Tasa de Citación

**Archivo a crear**: `data_models/aeo_kpis.py`

**Criterios de aceptación**:
- [ ] Data class AEOKPIs con campos relevantes
- [ ] Método para calcular composite score
- [ ] Serialización a dict/JSON

### Tarea D.2: Mock Integrations para Profound/Semrush APIs

**Objetivo**: Crear stubs para integración futura con APIs de analytics.

**Referencia KB**: Sección [VENDORS] líneas 320-328

**Stubs a crear**:
- `modules/analytics/profound_client.py` (stub)
- `modules/analytics/semrush_client.py` (stub)

**Criterios de aceptación**:
- [ ] Clases con métodos placeholders
- [ ] Docstrings indicando qué API harían
- [ ] Configuración para API keys (env vars)

### Tarea D.3: Dashboard Template para AEO Metrics

**Objetivo**: Crear template de reporte con métricas de AEO.

**Referencia**: revenue_dashboard.py existente

**Archivo a crear**: `modules/delivery/generators/aeo_metrics_report.md`

**Criterios de aceptación**:
- [ ] Template con secciones para cada KPI
- [ ] Incluye gráficos sugeridos (ASCII/text)
- [ ] Placeholder para datos de APIs reales

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_aeo_kpis_model` | `tests/` | Data class funciona |
| `test_aeo_kpis_serialization` | `tests/` | Serialización funciona |
| Regression suite | `tests/` | Todos pasan |

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-D como ✅ Completada
2. **Actualizar documentation** con nuevos módulos

---

## Criterios de Completitud (CHECKLIST)

- [ ] **KPI Framework** definido en data_models
- [ ] **Mock clients** para Profound/Semrush
- [ ] **Dashboard template** con métricas AEO
- [ ] **Tests pasan**
- [ ] **Documentación actualizada**

---

## Restricciones

- NO implementar APIs reales (requieren cuentas y presupuesto)
- Mock mode debe ser claro para usuarios
- FASE-D es foundation, no measurement real

---

## Prompt de Ejecución

```
Actúa como data scientist y architect.

OBJETIVO: Crear framework de medición para AEO real.

CONTEXTO:
- FASE-C completada: integrations checklists
- KB: AEO_agent_ready.md secciones [KPIS], [VENDORS]
- Base: data_models/ existente

TAREAS:
1. Diseñar KPI framework (AI Visibility, SoV, Citación)
2. Crear mock clients para Profound/Semrush
3. Generar dashboard template con métricas

CRITERIOS:
- Data class con serialización
- Stubs con docstrings claros
- Template con métricas actionable
- Tests pasan
```
