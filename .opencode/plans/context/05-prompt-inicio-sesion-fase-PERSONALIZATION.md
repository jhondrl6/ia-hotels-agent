# FASE-PERSONALIZATION — Personalización de Generators con Audit Data

**ID**: FASE-PERSONALIZATION
**Objetivo**: Modificar generators para recibir y usar audit_report como contexto
**Dependencias**: FASE-DATASOURCE ✅ (completada 2026-04-14)
**Duración estimada**: 2-3 horas
**Skill**: systematic-debugging
**Paralela con**: FASE-BUGFIXES (NO compartir archivos — ver Restricciones)

---

## Contexto

Causa raíz D2: los generators producen assets genéricos porque NO reciben datos del audit.

Síntomas:
- hotel_schema tiene name="Hotel" en vez de "Amaziliahotel"
- llms_txt dice "hotel ubicado en Colombia" sin URL real
- geo_playbook usa región genérica

Solución: Los generators reciben `validated_data` dict (que ya contiene `hotel_data` con name, url, region, phone, lat, lng) y lo usan para personalizar.

## Estado Post-FASE-DATASOURCE

FASE-DATASOURCE ya agregó:
- `validated_data["hotel_data"]` con name, description, telephone, url, address, image, price_range, latitude, longitude
- `validated_data["phone_web"]`, `validated_data["phone_gbp"]`
- `validated_data["gbp_rating"]`, `validated_data["gbp_review_count"]`

Estos datos YA están disponibles en `validated_data` — solo falta que los generators LOS USEN.

---

## ⚠️ RESTRICCIONES CRÍTICAS (paralelización)

**NO modificar estos archivos** (pertenece a FASE-BUGFIXES que corre en paralelo):
- `modules/asset_generation/whatsapp_button_generator.py`
- `modules/asset_generation/review_widget_generator.py`
- `modules/asset_generation/org_schema_generator.py`
- `main.py` (sección propuesta ~líneas 2063-2098)

**Archivos SÍ permitidos para esta fase:**
- `modules/asset_generation/v4_asset_orchestrator.py`
- `modules/asset_generation/conditional_generator.py`
- `modules/asset_generation/hotel_schema_generator.py` (si existe como archivo separado)
- `modules/asset_generation/llmstxt_generator.py`
- `modules/asset_generation/geo_playbook_generator.py`
- `modules/asset_generation/monthly_report_generator.py`
- `modules/asset_generation/optimization_guide_generator.py`
- Cualquier otro generator EXCEPTO los 3 excluidos arriba

---

## Tarea 1: Diagnosticar Flujo de Datos Actual

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Ver qué datos ya están en validated_data
grep -n "validated_data\[" modules/asset_generation/v4_asset_orchestrator.py | head -20

# Ver cómo conditional_generator pasa datos a generators
grep -n "hotel_data\|validated_data\|generate" modules/asset_generation/conditional_generator.py | head -30

# Listar generators
ls modules/asset_generation/*_generator.py
```

Documentar: ¿qué generators YA reciben `validated_data` o `hotel_data`? ¿cuáles no?

## Tarea 2: Propagar audit_data a Generators (NO excluidos)

Para CADA generator (excepto whatsapp/review/org_schema):

### Patrón de inyección

Los generators son llamados desde `conditional_generator.py` en `_generate_content()`. El `validated_data` dict YA está disponible ahí. El cambio es asegurar que cada handler pase los datos relevantes:

```python
# En conditional_generator.py, cada handler tipo:
elif asset_type == "llms_txt":
    hotel_data = validated_data.get("hotel_data", {})
    data = getattr(hotel_data, 'value', hotel_data) if not isinstance(hotel_data, dict) else hotel_data
    content = self._generate_llms_txt(data)  # data ya tiene name, url, region, etc.
```

Y en cada generator method, usar los datos:

```python
def _generate_llms_txt(self, hotel_data: Dict) -> str:
    name = hotel_data.get("name", "Hotel")
    url = hotel_data.get("url", "")
    region = hotel_data.get("region", "")
    # ... usar datos reales en vez de placeholders
```

### Generators a modificar (verificar cuáles existen):
1. `_generate_hotel_schema()` — YA usa hotel_data (verificar que lat/lng fluyan)
2. `_generate_llms_txt()` o llmstxt_generator.py
3. `_generate_geo_playbook()` o geo_playbook_generator.py
4. `_generate_monthly_report()` o monthly_report_generator.py
5. `_generate_optimization_guide()` o optimization_guide_generator.py

## Tarea 3: Tests

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/ -v --tb=short -q
```

Crear test mínimo si no existe:
```python
# tests/asset_generation/test_personalization.py
def test_hotel_schema_uses_real_name():
    """hotel_schema debe usar nombre del audit, no 'Hotel' genérico"""
    generator = ConditionalGenerator()
    validated_data = {"hotel_data": {"name": "Amazilia Hotel", "url": "https://amaziliahotel.com/"}}
    result = generator.generate("hotel_schema", validated_data, ...)
    assert "Amazilia" in result.content
```

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md` → FASE-PERSONALIZATION ✅
2. `06-checklist-implementacion.md` → tareas [x]
3. `09-documentacion-post-proyecto.md` → Sección A/D
4. `log_phase_completion.py --fase FASE-PERSONALIZATION`
5. `./venv/Scripts/python.exe scripts/doctor.py --status`

## Criterios de Completitud

- [ ] Generators (no excluidos) usan hotel_data.name en vez de "Hotel"
- [ ] Generators usan hotel_data.url en vez de ""
- [ ] Generators usan hotel_data.region/lat/lng
- [ ] No modifica whatsapp/review/org_schema generators
- [ ] Tests pasan
- [ ] Documentación actualizada
