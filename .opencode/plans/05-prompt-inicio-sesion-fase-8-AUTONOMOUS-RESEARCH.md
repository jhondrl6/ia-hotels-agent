# FASE 8: Autonomous Research Engine v2

**ID**: FASE-8-AUTONOMOUS-RESEARCH
**Objetivo**: Implementar investigación autónoma real con output verificable
**Dependencias**: FASE 5 completada
**Duración estimada**: 2-3 horas
**Skill**: autonomous-ai-agents, web-research

---

## Problema Actual

```
Informe dice: "Autonomous Researcher intentó investigar..."
Pero no hay evidencia. El módulo es no-op o su output se pierde.

El sistema no usa datos de Booking, TripAdvisor, Instagram.
```

---

## Solución: Research Engine con Evidence

```
Research Request
      │
      ▼
┌─────────────────────────────────────┐
│     AUTONOMOUS RESEARCHER ENGINE     │
├─────────────────────────────────────┤
│  1. GBP Lookup                      │
│  2. Booking.com Scrape              │
│  3. TripAdvisor Scrape              │
│  4. Instagram Lookup               │
│  5. Cross-Reference                 │
│  6. Confidence Scoring             │
└─────────────────────────────────────┘
      │
      ▼
Research Report (JSON)
      │
      ▼
Assets referencian el research
```

---

## Tareas

### T8A: Research Output Schema
**Archivo**: `modules/providers/autonomous_researcher.py` (modificar)

```python
@dataclass
class ResearchOutput:
    hotel_name: str
    sources_checked: List[str]
    data_found: Dict[str, Any]
    confidence: float
    citations: List[str]  # URLs
    gaps: List[str]       # Qué NO se encontró
```

### T8B: Implementar Source Scrapers
**Archivos**: `modules/scrapers/` (NUEVO)
- `booking_scraper.py` - Reviews, ratings, photos
- `tripadvisor_scraper.py` - Reviews, rankings
- `instagram_scraper.py` - Photos, engagement

### T8C: Integrar en Orchestration
**Flujo**:
```
Audit → Research → Assessment → Generation → Report
```

**Beneficio**: Assets usan datos de múltiples fuentes, no solo GBP.

### T8D: Research Confidence Scoring
```python
def calculate_research_confidence(sources: List[str], data: Dict) -> float:
    sources_checked: 4/4 → 1.0
    sources_checked: 2/4 → 0.5
    sources_checked: 1/4 → 0.25
```

---

## Tests Obligatorios

| Test | Criterio |
|------|----------|
| `test_research_output_schema` | Schema se serializa correctamente |
| `test_scraper_booking` | Datos de Booking se extraen |
| `test_research_confidence` | Score refleja fuentes encontradas |
| `test_research_integrated` | Research output disponible |

---

## Criterios de Completitud

- [ ] ResearchOutput schema implementado
- [ ] Scrapers para Booking, TripAdvisor, Instagram
- [ ] Research se integra en orchestration
- [ ] Research confidence scoring funciona
- [ ] Tests pasan
