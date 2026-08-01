# FASE-3: Tests de Regresión para el Pipeline de Inyección Onboarding

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (⚠️ PARCIAL delegate_task — subagente puede escribir tests pero no ejecutarlos por WSL venv; se requiere agente principal para ejecución y depuración)
> **Complejidad**: MEDIA
> **Plan**: `ONBOARDING-INJECTION-GAP-2026-07-29/01-plan-maestro.md`

## Contexto previo

**FASE-0**: Matching canónico por URL + `_normalize_url()` + frescura configurable.
**FASE-1**: `"user_provided"` en verified_sources + mensaje onboard actualizado.
**FASE-2**: Fallback a `observations.json` + `_observation_to_onboarding_format()`.

Todas las modificaciones de código están completas. Falta cobertura de tests.

## Objetivo de esta fase

Crear tests de regresión para las 4 modificaciones principales implementadas en FASE-0, FASE-1 y FASE-2. Verificar que los tests pasan contra el venv Windows del proyecto.

### Tareas

- [ ] **T1**: Tests para `_normalize_url()` — ≥10 casos cubriendo todas las reglas de normalización
- [ ] **T2**: Tests para `_load_latest_onboarding_data()` — URL-based matching con YAMLs mock
- [ ] **T3**: Tests para `_observation_to_onboarding_format()` — mapeo correcto de campos

### Detalle T1 — Tests para `_normalize_url()`

**Archivo nuevo**: `tests/test_onboarding_injection.py` (o integrar en test existente si hay uno para onboarding)

Casos de prueba (≥10):

| # | Input | Esperado | Regla |
|---|-------|----------|-------|
| 1 | `https://zione.co/` | `zione.co` | Caso base |
| 2 | `https://www.zione.co/` | `zione.co` | www removido |
| 3 | `http://zione.co` | `zione.co` | Sin trailing slash |
| 4 | `https://www.hotel.com/es/` | `hotel.com` | Path ignorado |
| 5 | `https://hotel.co?lang=es` | `hotel.co` | Query string ignorado |
| 6 | `https://ZIONE.CO/` | `zione.co` | Case insensitive |
| 7 | `https://www.sub.domain.co/` | `sub.domain.co` | Subdominio preservado |
| 8 | `http://simple-hotel.co` | `simple-hotel.co` | HTTP sin www |
| 9 | `https://hotel.com:8080/` | `hotel.com` | Puerto (si urlparse lo maneja) |
| 10 | `zione.co` | `zione.co` | Sin protocolo |
| 11 | `https://www.hotel.com.co/path?q=1#frag` | `hotel.com.co` | Full URL compleja |

```python
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import _normalize_url

@pytest.mark.parametrize("input_url,expected", [
    ("https://zione.co/", "zione.co"),
    ("https://www.zione.co/", "zione.co"),
    ("http://zione.co", "zione.co"),
    ("https://www.hotel.com/es/", "hotel.com"),
    ("https://hotel.co?lang=es", "hotel.co"),
    ("https://ZIONE.CO/", "zione.co"),
    ("https://www.sub.domain.co/", "sub.domain.co"),
    ("http://simple-hotel.co", "simple-hotel.co"),
    ("zione.co", "zione.co"),
    ("https://www.hotel.com.co/path?q=1#frag", "hotel.com.co"),
])
def test_normalize_url(input_url, expected):
    assert _normalize_url(input_url) == expected
```

### Detalle T2 — Tests para `_load_latest_onboarding_data()`

Crear YAMLs temporales con diferentes URLs y verificar que el matching por URL normalizada funciona:

```python
class TestLoadLatestOnboardingData:
    """Tests para _load_latest_onboarding_data con matching por URL."""
    
    def test_match_by_url_normalized(self, tmp_path):
        """Un YAML con hotel.url debe matchear por URL normalizada."""
        # Crear YAML temporal con hotel.url
        yaml_content = """
hotel:
  nombre: Test Hotel
  url: https://www.testhotel.com/
datos_operativos:
  habitaciones: 20
metadatos:
  fecha_captura: '2026-07-29T10:00:00+00:00'
  fuente: test
"""
        yaml_file = tmp_path / "test-hotel_onboarding.yaml"
        yaml_file.write_text(yaml_content)
        
        result = _load_latest_onboarding_data(
            hotel_url="https://testhotel.com/",
            hotel_name="Test Hotel",
            output_dir=tmp_path,
        )
        assert result is not None
        assert result['datos_operativos']['habitaciones'] == 20
    
    def test_no_match_different_url(self, tmp_path):
        """URLs diferentes no deben matchear."""
        yaml_content = """
hotel:
  nombre: Hotel A
  url: https://hotel-a.com/
datos_operativos:
  habitaciones: 15
metadatos:
  fecha_captura: '2026-07-29T10:00:00+00:00'
"""
        (tmp_path / "hotel-a_onboarding.yaml").write_text(yaml_content)
        
        result = _load_latest_onboarding_data(
            hotel_url="https://hotel-b.com/",  # URL diferente
            hotel_name="Hotel B",
            output_dir=tmp_path,
        )
        assert result is None
    
    def test_no_url_field_returns_none(self, tmp_path):
        """YAML sin hotel.url no matchea (sin fallback)."""
        # Crear YAML sin hotel.url (como los viejos pre-CAMBIO A)
        yaml_content = """
hotel:
  nombre: Old Hotel
datos_operativos:
  habitaciones: 10
metadatos:
  fecha_captura: '2026-07-29T10:00:00+00:00'
"""
        (tmp_path / "old-hotel_onboarding.yaml").write_text(yaml_content)
        
        # Sin observations.json, debería retornar None
        result = _load_latest_onboarding_data(
            hotel_url="https://oldhotel.com/",
            hotel_name="Old Hotel",
            output_dir=tmp_path,
        )
        # Sin fallback a observations.json, sin hotel.url → None
        assert result is None
    
    def test_output_dir_default(self, tmp_path, monkeypatch):
        """Si no se pasa output_dir, usa Path('output/clientes')."""
        # Este test verifica el comportamiento default
        pass  # Implementar con monkeypatch si es necesario
```

### Detalle T3 — Tests para `_observation_to_onboarding_format()`

```python
class TestObservationToOnboardingFormat:
    """Tests para _observation_to_onboarding_format."""
    
    def test_maps_all_fields(self):
        """Todos los campos del observation se mapean correctamente."""
        from main import _observation_to_onboarding_format
        
        obs = {
            "hotel_name": "Zi One Luxury",
            "website": "https://zione.co/",
            "region": "eje_cafetero",
            "rooms": 34,
            "monthly_reservations": 800,
            "avg_reservation_cop": 290000,
            "direct_channel_percentage": 40.0,
            "collected_at": "2026-07-22",
            "confidence": 0.95,
            "epistemic_status": "verified",
        }
        
        result = _observation_to_onboarding_format(obs)
        
        assert result['hotel']['nombre'] == "Zi One Luxury"
        assert result['hotel']['url'] == "https://zione.co/"
        assert result['hotel']['ubicacion'] == "eje_cafetero"
        assert result['datos_operativos']['habitaciones'] == 34
        assert result['datos_operativos']['reservas_mes'] == 800
        assert result['datos_operativos']['valor_reserva_cop'] == 290000
        assert result['datos_operativos']['canal_directo_pct'] == 40.0
        assert result['metadatos']['confidence'] == 0.95
        assert result['metadatos']['epistemic_status'] == "verified"
        assert 'campos_confirmados' in result['metadatos']
    
    def test_missing_fields_default(self):
        """Campos faltantes usan defaults seguros."""
        from main import _observation_to_onboarding_format
        
        obs = {"hotel_name": "Minimal Hotel"}
        result = _observation_to_onboarding_format(obs)
        
        assert result['datos_operativos']['habitaciones'] == 10  # default
        assert result['datos_operativos']['reservas_mes'] == 0
        assert result['datos_operativos']['valor_reserva_cop'] == 0
```

### Restricciones

- ❌ NO ejecutar v4complete — solo tests unitarios
- ✅ Los tests deben correr con `python -m pytest tests/test_onboarding_injection.py -v`
- ✅ Usar `tmp_path` de pytest para fixtures temporales — no crear archivos en disco real
- ✅ Si `_normalize_url` o `_observation_to_onboarding_format` no son importables desde `main.py` (por dependencias transitivas), extraerlas a un módulo separado o usar `subprocess` para testear

### Criterios de completitud

- [ ] ≥10 tests para `_normalize_url()` — todos PASS
- [ ] ≥3 tests para `_load_latest_onboarding_data()` con matching por URL
- [ ] ≥2 tests para `_observation_to_onboarding_format()`
- [ ] Todos los tests pasan: `python -m pytest tests/test_onboarding_injection.py -v`
- [ ] Tests existentes no rompen: `python -m pytest --collect-only -q | tail -1`

### Verificación

```bash
# Ejecutar solo los tests nuevos
python -m pytest tests/test_onboarding_injection.py -v

# Verificar que no hay regresión
python -m pytest --collect-only -q | tail -1
```

### delegate_task Prompt (si se usa subagente para ESCRITURA de tests)

```
GOAL: Create regression tests for iah-cli onboarding injection pipeline in a new file tests/test_onboarding_injection.py.

CONTEXT: Three functions were added/modified in main.py:
1. _normalize_url(url) - normalizes URLs for canonical matching (strip protocol, www, trailing slash, path, query, lowercase)
2. _load_latest_onboarding_data(hotel_url, hotel_name, output_dir=None) - rewritten to match by URL instead of slug
3. _observation_to_onboarding_format(obs) - converts observations.json entry to onboarding dict format

Create pytest tests covering:
- _normalize_url: 10+ parametrized cases (www, protocol, path, query, case, subdomain, port)
- _load_latest_onboarding_data: match by URL, no match different URL, no hotel.url field, default output_dir
- _observation_to_onboarding_format: all fields mapped, missing fields use defaults

Use tmp_path for temporary YAML files. Do NOT run the tests (WSL can't import project modules).
Write the file to tests/test_onboarding_injection.py and report the path.
```

### Próxima sesión

**FASE-RELEASE**: v4complete Zi One Luxury + version bump v4.67.0 + CHANGELOG + análisis post-implementación con matriz de verificación de 8 hallazgos. MEDIA complejidad. ⚠️ MIXTO (v4complete→subagente, análisis→directo).

Carga: `06-prompt-fase-release.md`
