# FASE 11: Google Travel Integration + Onboard Enhancement

**Versión**: 1.0.0
**Fecha**: 2026-03-23
**Proyecto**: IA Hoteles CLI - NEVER_BLOCK
**Estado**: 🚧 EN PROGRESO

---

## 1. CONTEXTO Y MOTIVACIÓN

### Problemas Identificados en v4complete para Hotelvisperas

| # | Problema | Severidad | Causa Raíz |
|---|----------|-----------|------------|
| 1 | `Place not found in Google Places` | 🔴 CRITICAL | Google Places API ≠ Google Travel API |
| 2 | `optimization_guide` fallido | 🟡 MEDIUM | Datos estimados vs datos reales |
| 3 | Crawlers IA bloqueados | 🟡 MEDIUM | Robots.txt no existe |
| 4 | Metadata por defecto | 🟡 MEDIUM | CMS defaults detectados |

### Evidencia de Existencia del Hotel

El hotel SÍ existe en Google via Google Travel:
- URL: `https://www.google.com/travel/hotels/entity/ChcIqp2ZrdfnspElGgsvZy8xdGhobGtqYhAB`
- Título: `HOTEL VISPERAS | Hoteles de Google`
- Dirección: `Km. 4 vía Termales, vereda La Leona, Santa Rosa de Cabal, Risaralda, Colombia`
- Fuente: Google Travel/Hotels (agregador de hoteles)

### Diferencia Técnica

```
Google Places API      → Busca en Google Maps/Nearby Search
                        → API: places.googleapis.com/v1
                        → Retorna: place_id, reviews, photos, rating

Google Travel API      → Busca en Google Travel/Hotels
                        → URL: google.com/travel/hotels
                        → Retorna: hotel_info, prices, availability, photos
```

---

## 2. ARQUITECTURA PROPUESTA

### Flujo de Datos Mejorado

```
┌──────────────────────────────────────────────────────────────────────┐
│                      AUTONOMOUS RESEARCHER v2                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Hotelvisperas.com                                                   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │  GBPScraper │────▶│TravelScraper│────▶│  Benchmark   │           │
│  │  (Places)   │     │  (Travel)   │     │  Resolver   │           │
│  └─────────────┘     └─────────────┘     └─────────────┘           │
│        │                   │                   │                    │
│        ▼                   ▼                   ▼                    │
│   [Place found]      [Place found]        [Fallback]                 │
│        │                   │                   │                    │
│        └───────────────────┴───────────────────┘                    │
│                            │                                        │
│                            ▼                                        │
│                  ┌─────────────────┐                                │
│                  │ ResearchOutput  │                                │
│                  │ (JSON persist)  │                                │
│                  └─────────────────┘                                │
└──────────────────────────────────────────────────────────────────────┘
```

### Prioridad de Fuentes

1. **Google Places API** (primaria, si funciona)
2. **Google Travel Scraper** (secundaria, si Places falla)
3. **Benchmark Regional** (fallback, si ambas fallan)

---

## 3. SUB-FASES

### 3.1 FASE 11A: Google Travel Scraper

**Objetivo**: Crear scraper para Google Travel que capture datos de hoteles.

### 3.2 FASE 11B: Onboard Enhancement

**Objetivo**: Mejorar captura y persistencia de datos operativos.

### 3.3 FASE 11C: Asset Quality Boost

**Objetivo**: Verificar que con datos reales, todos los assets pasan validación.

---

## 4. IMPLEMENTACIÓN FASE 11A

### Tarea 1: Crear GoogleTravelScraper

**Archivo**: `modules/scrapers/google_travel_scraper.py`

```python
class GoogleTravelScraper:
    """Scraper para Google Travel/Hotels.
    
   区别于 Google Places API, Google Travel es un agregador
    de hoteles con informacion de precios, disponibilidad y opiniones.
    """
    
    def scrape_hotel(self, hotel_name: str, location: str = None) -> dict:
        """Scrapes hotel data from Google Travel.
        
        Args:
            hotel_name: Nombre del hotel
            location: Ubicacion opcional (ciudad, region)
            
        Returns:
            dict con: name, rating, reviews_count, address, phone, website
        """
        pass
```

### Tarea 2: Integrar en AutonomousResearcher

**Archivo**: `modules/providers/autonomous_researcher.py`

```python
class AutonomousResearcher:
    def _try_sources(self, hotel_name: str, location: str) -> ResearchOutput:
        # 1. Try GBPScraper (Places API)
        gbp_result = self._try_gbp_scrape(hotel_name)
        if gbp_result and gbp_result.place_found:
            return gbp_result
        
        # 2. Try GoogleTravelScraper (Travel)
        travel_result = self._try_travel_scrape(hotel_name)
        if travel_result and travel_result.place_found:
            return travel_result
        
        # 3. Fallback: Benchmark resolver
        return self._fallback_benchmark(hotel_name)
```

### Tarea 3: Tests Obligatorios

**Archivo**: `tests/scrapers/test_google_travel_scraper.py`

```python
def test_hotelvisperas_found_in_google_travel():
    """Hotel Visperas debe ser encontrado via Google Travel."""
    pass

def test_travel_data_integrates_with_researcher():
    """Datos de Travel deben fluir hacia ResearchOutput."""
    pass

def test_fallback_places_to_travel():
    """Cuando Places falla, Travel debe intentar."""
    pass

def test_fallback_travel_to_benchmark():
    """Cuando Travel falla, usar benchmark regional."""
    pass

def test_travel_response_structure():
    """Travel scraper debe retornar estructura correcta."""
    pass
```

---

## 5. TESTS OBLIGATORIOS (5 mínimo)

| # | Test | Propósito |
|---|------|-----------|
| 1 | `test_hotelvisperas_found_in_google_travel` | Hotel encontrado en Travel |
| 2 | `test_travel_data_integrates_with_researcher` | Integración con flujo principal |
| 3 | `test_fallback_places_to_travel` | Fallback funcional |
| 4 | `test_fallback_travel_to_benchmark` | Doble fallback funcional |
| 5 | `test_travel_response_structure` | Estructura de datos correcta |

---

## 6. CRITERIOS DE ACEPTACIÓN

### FASE 11A - Google Travel
```
✅ GoogleTravelScraper existe y es importable
✅ Hotel Visperas encontrado via Google Travel
✅ Datos de Travel aparecen en ResearchOutput
✅ autonomous_researcher usa Travel como fallback
✅ 5 tests nuevos pasando
```

### FASE 11B - Onboard
```
✅ Datos onboard persisten en data/onboarded_hotels.json
✅ v4complete carga datos onboard automaticamente
✅ No pide datos repetidos en segunda ejecucion
```

### FASE 11C - Asset Quality
```
✅ optimization_guide pasa validacion (0 content_issues)
✅ 7/7 assets generados exitosamente
✅ Coherence Score >= 0.85
```

---

## 7. ARCHIVOS A MODIFICAR

| Archivo | Modificación | Fase |
|---------|-------------|------|
| `modules/scrapers/google_travel_scraper.py` | NUEVO | 11A |
| `modules/providers/autonomous_researcher.py` | Agregar Travel fallback | 11A |
| `modules/scrapers/__init__.py` | Exportar GoogleTravelScraper | 11A |
| `tests/scrapers/test_google_travel_scraper.py` | NUEVO | 11A |
| `data/onboarded_hotels.json` | NUEVO (esquema) | 11B |
| `modules/onboarding/onboarding_controller.py` | Persistencia | 11B |
| `CHANGELOG.md` | Entrada FASE 11 | 11C |

---

## 8. DEPENDENCIAS

```
FASE 11A (Google Travel)
    │
    ├── Requiere: modules/scrapers/__init__.py
    ├── Requiere: modules/providers/autonomous_researcher.py
    └── Tests: tests/scrapers/test_google_travel_scraper.py

FASE 11B (Onboard Enhancement)
    │
    ├── Depende de: FASE 11A
    └── Requiere: data/onboarded_hotels.json schema

FASE 11C (Asset Quality)
    │
    ├── Depende de: FASE 11B
    └── Requiere: v4complete re-run con datos reales
```

---

## 9. VALIDACIONES POST-IMPLEMENTACIÓN

```bash
# Test de la integracion
python -m pytest tests/scrapers/test_google_travel_scraper.py -v

# Test de regresion del flujo completo
python main.py v4complete --url https://hotelvisperas.com/

# Verificar GBP encontrado
grep -i "place_found" output/v4_complete/audit_report.json

# Verificar assets generados
ls -la output/v4_complete/hotelvisperas/
```

---

## 10. NOTAS

- Google Travel scraping requiere manejo de User-Agent y delays
- Si Travel esta bloqueado, el fallback a benchmark es aceptable
- El objetivo NO es eliminar el fallback, sino MEJORAR la calidad de datos

---

**Siguiente Accion**: Ejecutar implementacion FASE 11A en sesion dedicada.