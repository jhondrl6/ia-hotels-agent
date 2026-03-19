# 🏗️ Patrones de Código — IA Hoteles Agent

> [!NOTE]
> **Propósito**: Patrones canónicos para mantener consistencia al modificar código.
> **Cuándo consultar**: Antes de agregar nuevas reglas, conectores o tests.

---

## Índice de Patrones

| Patrón | Uso | Estado |
|--------|-----|--------|
| [Nueva Regla en Decision Engine](#nueva-regla-en-decision-engine) | Agregar regla al motor de decisión | ✅ Documentado |
| [Nuevo Conector de Deploy](#nuevo-conector-de-deploy) | Agregar CMS/plataforma al deployer | ✅ Documentado |
| [Test de Integración](#test-de-integración) | Escribir tests E2E | ✅ Documentado |
| [Sincronización Documental Post-Release](doc_sync_post_release.md) | Actualizar docs tras nuevo release | ✅ Documentado |

---

## Patrones Documentados

### Nueva Regla en Decision Engine

**Ubicación**: `modules/decision_engine.py`

**Estructura**:
```python
def _evaluar_regla_N(self, datos: dict) -> Optional[str]:
    """
    Regla N: [Descripción breve]
    
    Condición: [Cuándo aplica]
    Resultado: [Paquete que retorna]
    """
    # Extraer datos necesarios
    metrica = datos.get('metrica_clave', 0)
    
    # Evaluar condición
    if metrica > UMBRAL:
        return "paquete_recomendado"
    
    return None  # No aplica, continuar al siguiente
```

**Checklist**:
- [ ] Definir número de regla en orden correcto
- [ ] Documentar en `Plan_maestro_v2_5.md` si afecta lógica de negocio
- [ ] Agregar test en `tests/test_decision_engine.py`
- [ ] Actualizar `DOMAIN_PRIMER.md` si es regla nueva

---

### Nuevo Conector de Deploy

**Ubicación**: `modules/deployer/connectors/`

**Estructura**:
```python
# modules/deployer/connectors/{plataforma}_connector.py

from .base_connector import BaseConnector

class PlataformaConnector(BaseConnector):
    """Connector for [Plataforma] CMS."""
    
    def validate_connection(self) -> bool:
        """Verify credentials and connectivity."""
        # Implementation
        pass
    
    def create_post(self, content: dict) -> dict:
        """Create new content."""
        # Implementation
        pass
    
    def inject_code(self, code: str, location: str) -> bool:
        """Inject code snippet (if supported)."""
        # Implementation
        pass
```

**Checklist**:
- [ ] Heredar de `BaseConnector`
- [ ] Implementar métodos obligatorios
- [ ] Agregar a `deployer/manager.py` en detección de CMS
- [ ] Crear tests en `tests/test_deploy_{plataforma}.py`

---

### Test de Integración

**Ubicación**: `tests/` o `scripts/`

**Estructura**:
```python
# tests/test_{feature}_integration.py

import pytest
from modules.{modulo} import {Clase}

class TestFeatureIntegration:
    """Integration tests for [Feature]."""
    
    @pytest.fixture
    def setup_data(self):
        """Prepare test data."""
        return {"key": "value"}
    
    def test_scenario_happy_path(self, setup_data):
        """Test normal execution flow."""
        result = Clase().metodo(setup_data)
        assert result["status"] == "success"
    
    def test_scenario_edge_case(self, setup_data):
        """Test edge case: [descripción]."""
        setup_data["key"] = "edge_value"
        result = Clase().metodo(setup_data)
        assert result["handled"] is True
```

**Checklist**:
- [ ] Usar fixtures para datos de prueba
- [ ] Cubrir happy path y edge cases
- [ ] Nombrar tests descriptivamente
- [ ] Ejecutar con `pytest tests/ -v` antes de commit

---

## Agregar Nuevo Patrón

Cuando el agente identifique un patrón repetitivo:

1. Proponer al usuario: "He identificado un patrón para [X], ¿lo documento?"
2. Crear sección siguiendo esta estructura:
   - Nombre descriptivo
   - Ubicación en código
   - Estructura con ejemplo
   - Checklist de implementación

---

## Referencias

- [PROTOCOLO_AUTOMANTENIMIENTO.md](./workflows/PROTOCOLO_AUTOMANTENIMIENTO.md) — Roles y responsabilidades
- [GUIA_TECNICA.md](../docs/GUIA_TECNICA.md) — Arquitectura del proyecto
