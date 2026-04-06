# GAP-IAO-01-05: GA4 para Tráfico Indirecto (OPCIONAL)

**ID**: GAP-IAO-01-05
**Objetivo**: Agregar métricas de GA4 como método #5 de medición IA
**Dependencias**: GAP-IAO-01-04 (assets) — O después de GAP-IAO-01-03 si no se hace 04
**Duración estimada**: 1-2 horas
**Nota**: **FASE OPCIONAL** — El pipeline funciona sin GA4. Esta fase solo agrega un método adicional.
**Skill**: Ninguna específica

---

## Contexto

### Cuándo hacer esta fase

**Hacer esta fase si**:
- El pipeline básico (fases 01-04) funciona correctamente
- Se necesita tráfico indirecto como métrica adicional
- El cliente tiene GA4 configurado

**NO hacer esta fase si**:
- El pipeline básico aún no funciona
- El cliente no tiene GA4
- Los recursos son limitados

### Los 5 métodos de la KB

| # | Método | Estado | Implementación |
|---|--------|--------|---------------|
| 1 | GSC (Knowledge Panels) | ❌ Postergado | Stub en futuro |
| 2 | IATester | ✅ Implementado en 01-02 | `IATester.test_hotel()` |
| 3 | SEMrush | ⚠️ Stub nomás | Sin implementar |
| 4 | BingProxy | ✅ Implementado en 01-02 | `BingProxyTester.test_visibility()` |
| 5 | GA4 (tráfico indirecto) | ❌ No existe | **Esta fase** |

### Si GA4 no está disponible

El pipeline funciona sin GA4:
- Score IA usa IATester + BingProxy
- Método #5 se marca como `"N/A"` en data_source
- La propuesta lo indica: "Tráfico indirecto: pendiente de medición GA4"

---

## Tareas

### Tarea 1: Crear stub de GoogleAnalyticsClient

**Archivo**: `modules/analytics/google_analytics_client.py` (NUEVO)

```python
"""
Google Analytics Client para medir tráfico indirecto.

MÉTODO #5 de KB [SECTION:IA_VISIBILITY_MEASUREMENT]:
Tráfico indirecto post-consulta IA (Google Analytics).
"""

class GoogleAnalyticsClient:
    """Client para GA4 Data API."""
    
    def __init__(self, property_id: str = None, credentials_path: str = None):
        self.property_id = property_id or os.getenv("GA4_PROPERTY_ID")
        self.credentials_path = credentials_path or os.getenv("GA4_CREDENTIALS_PATH")
        self._client = None
    
    def get_indirect_traffic(self, date_range: str = "last_30_days") -> dict:
        """
        Obtiene métricas de tráfico que sugiere consulta previa en IA.
        
        Args:
            date_range: "last_30_days" | "last_90_days"
        
        Returns:
            {
                "sessions_indirect": int,
                "sessions_direct": int,
                "sessions_referral": int,
                "top_sources": [{"source": str, "sessions": int}],
                "data_source": "GA4" | "N/A"
            }
        """
        if not self.property_id:
            return {
                "sessions_indirect": 0,
                "sessions_direct": 0,
                "sessions_referral": 0,
                "top_sources": [],
                "data_source": "N/A",
                "note": "GA4_PROPERTY_ID no configurado"
            }
        
        try:
            # Implementar conexión GA4
            # ...
            pass
        except Exception as e:
            return {
                "sessions_indirect": 0,
                "sessions_direct": 0,
                "sessions_referral": 0,
                "top_sources": [],
                "data_source": "N/A",
                "note": f"Error GA4: {str(e)}"
            }
    
    def is_available(self) -> bool:
        """Verifica si GA4 está configurado y disponible."""
        return bool(self.property_id)
```

**Criterios de aceptación**:
- [ ] `GoogleAnalyticsClient` creado
- [ ] `get_indirect_traffic()` retorna estructura esperada
- [ ] Si no está configurado → retorna `data_source: "N/A"`
- [ ] No rompe si GA4 no está disponible

### Tarea 2: Integrar GA4 en AEOKPIs

**Archivo**: `data_models/aeo_kpis.py`

**Agregar campo** para métricas GA4:

```python
@dataclass
class AEOKPIs:
    # ... campos existentes ...
    
    # === CAMPO NUEVO ===
    indirect_traffic: Optional["IndirectTrafficMetrics"] = None

@dataclass
class IndirectTrafficMetrics:
    """Métricas de tráfico indirecto de GA4."""
    sessions_indirect: int = 0
    sessions_direct: int = 0
    sessions_referral: int = 0
    data_source: str = "N/A"
```

**Modificar** `calculate_composite_score()`:

```python
def calculate_composite_score(self) -> float:
    scores = []
    
    if self.ai_visibility_score is not None:
        scores.append(self.ai_visibility_score * 0.35)  # Reducido de 0.40
    
    if self.share_of_voice is not None:
        scores.append(self.share_of_voice * 0.20)
    
    if self.citation_rate is not None:
        scores.append(self.citation_rate * 0.20)
    
    # GA4 como método #5
    if self.indirect_traffic is not None and self.indirect_traffic.data_source == "GA4":
        # Normalizar: 100 sesiones = 10 puntos, más = más puntos
        indirect_normalized = min(100, self.indirect_traffic.sessions_indirect / 10)
        scores.append(indirect_normalized * 0.25)  # 25% del score
    
    if not scores:
        return -1.0
    
    return round(sum(scores), 2)
```

### Tarea 3: Integrar en diagnóstico

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Agregar llamada a GA4** en `_calculate_iao_score()`:

```python
def _calculate_iao_score(self, audit_result: V4AuditResult, hotel_data: dict = None) -> str:
    # ... IATester + BingProxy existentes ...
    
    # AGREGAR: GA4 como método #5
    try:
        from modules.analytics.google_analytics_client import GoogleAnalyticsClient
        
        ga4 = GoogleAnalyticsClient()
        if ga4.is_available():
            ga4_metrics = ga4.get_indirect_traffic()
            
            # Agregar a AEOKPIs
            from data_models.aeo_kpis import AEOKPIs, IndirectTrafficMetrics
            
            kpis.indirect_traffic = IndirectTrafficMetrics(
                sessions_indirect=ga4_metrics.get("sessions_indirect", 0),
                sessions_direct=ga4_metrics.get("sessions_direct", 0),
                sessions_referral=ga4_metrics.get("sessions_referral", 0),
                data_source="GA4"
            )
    except Exception:
        pass  # GA4 es opcional, no rompe
    
    score = kpis.calculate_composite_score()
    return str(max(0, min(100, int(score)))) if score >= 0 else "0"
```

---

## Archivos a modificar/crear

| Archivo | Acción |
|---------|--------|
| `modules/analytics/google_analytics_client.py` | CREAR (nuevo) |
| `data_models/aeo_kpis.py` | MODIFICAR (agregar IndirectTrafficMetrics) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | MODIFICAR (llamar GA4) |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`06-checklist-implementacion.md`**: Marcar GAP-IAO-01-05 como completada o saltada

2. **Si se ejecuta**:
```bash
python scripts/log_phase_completion.py \
    --fase GAP-IAO-01-05 \
    --desc "GA4 integrado como método #5 de medición IA" \
    --archivos-nuevos "modules/analytics/google_analytics_client.py" \
    --archivos-mod "data_models/aeo_kpis.py,modules/commercial_documents/v4_diagnostic_generator.py" \
    --check-manual-docs
```

3. **Si se SKIP** (usar si GA4 no es necesario):
```bash
python scripts/log_phase_completion.py \
    --fase GAP-IAO-01-05 \
    --desc "GA4 omitido - pipeline funciona sin método #5" \
    --force-skip-docs \
    --skip-reason "opcional-post-mvp"
```

---

## Criterios de Completitud

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

**Si se ejecuta**:
- [ ] `GoogleAnalyticsClient` creado y funcional
- [ ] `get_indirect_traffic()` retorna estructura correcta
- [ ] GA4 opcional: no rompe si no está configurado
- [ ] `indirect_traffic` agregado a `AEOKPIs`
- [ ] Score IA incluye GA4 cuando disponible
- [ ] `log_phase_completion.py` ejecutado

**Si se salta**:
- [ ] `force-skip-docs` ejecutado con razón válida
- [ ] Pipeline funciona sin GA4

---

## Nota sobre GA4 y la KB

La KB `[SECTION:IA_VISIBILITY_MEASUREMENT]` dice:

> "Tráfico indirecto post-consulta IA (Google Analytics) — Mensual"

GA4 es útil pero **no bloqueante**. El score IA puede calcularse solo con IATester + BingProxy.

Si el cliente tiene GA4 configurado y se quiere agregar:
- Solicitar `GA4_PROPERTY_ID` y credentials
- Seguir las tareas de esta fase

Si el cliente no tiene GA4:
- Omitir esta fase
- El pipeline funciona con 4/5 métodos
