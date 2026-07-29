# FASE-2: Integración observations.json como Fuente de Fallback

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (❌ NO VIABLE subagente — modifica función reescrita en FASE-0, requiere contexto acumulado)
> **Complejidad**: MEDIA
> **Plan**: `ONBOARDING-INJECTION-GAP-2026-07-29/01-plan-maestro.md`

## Contexto previo

**FASE-0**: `_load_latest_onboarding_data()` ahora busca por URL normalizada en vez de slug, usando `_normalize_url()` y aceptando `output_dir` parametrizado. `onboard` persiste `hotel.url` en el YAML.

**FASE-1**: `"user_provided"` es reconocido como fuente verificada en tiering. Mensaje de onboard sugiere `v4complete`.

**Pendiente §10c**: `data/hotel_observations/observations.json` contiene 6 hoteles con datos Tier A verificados (confidence 0.95), incluyendo Zi One Luxury (rooms=34, ADR=$290K, occupancy=78.4%). Actualmente NUNCA es consultado por v4complete. El único puente es el YAML de onboarding. Si el YAML no existe (hotel nunca pasó por `onboard`), los datos del warehouse son inaccesibles para el pipeline.

## Objetivo de esta fase

Agregar un fallback en `_load_latest_onboarding_data()`: si ningún YAML matchea por URL, buscar en `observations.json` por `website` normalizado y convertir el observation a formato onboarding.

### Tareas

- [ ] **T0 — PRECONDICION**: Agregar campo `website` a los 6 observations en `observations.json`
- [ ] **T1 — Fix 6**: Agregar fallback a `observations.json` en `_load_latest_onboarding_data()`
- [ ] **T2**: Crear helper `_observation_to_onboarding_format()` que convierta un observation al mismo dict que retornaría un YAML

### Detalle T0 — Agregar `website` a observations.json

**Archivo**: `data/hotel_observations/observations.json`

**Verificacion de codigo vivo (2026-07-29)**: Los 6 observations NO tienen el campo `website`. Sin este campo, el matching por URL normalizada en FASE-2 no puede funcionar.

Agregar `"website"` a cada observation. Mapeo:

| Hotel | website |
|-------|---------|
| Hotel Luxor | `"https://hotelluxor.com/"` |
| Hotel Don Alfonso | `"https://hoteldonalfonso.com/"` |
| Luma Plaza Hotel | `"https://lumaplazahotel.com/"` |
| GHL Hotel Abadia Plaza | `"https://ghlhotelabadiaplaza.com/"` |
| Hotel Castilla Real | `"https://hotelcastillareal.com/"` |
| Zi One Luxury | `"https://zione.co/"` |

**IMPORTANTE**: Los websites deben ser los REALES de cada hotel. Si no se conocen con certeza, verificar contra los datos de contacto en `Hoteles.txt` o `Datos.md`.

### Detalle T1 — Fix 6

**Archivo**: `main.py:_load_latest_onboarding_data()` (reescrita en FASE-0)

Después del loop de glob que busca YAMLs y antes del `return None` final, agregar:

```python
    # Fallback: buscar en observations.json (warehouse de datos verificados)
    obs_path = Path("data/hotel_observations/observations.json")
    if obs_path.exists():
        try:
            import json
            obs_data = json.loads(obs_path.read_text(encoding='utf-8'))
            for obs in obs_data.get('observations', []):
                obs_website = obs.get('website', '')
                if obs_website and _normalize_url(obs_website) == normalized_url:
                    return _observation_to_onboarding_format(obs)
        except Exception:
            pass  # Fallback silencioso — si falla, seguimos sin datos
    
    return None
```

### Detalle T2 — Helper

**Archivo**: `main.py` (función auxiliar, cerca de `_normalize_url()`)

```python
def _observation_to_onboarding_format(obs: dict) -> dict:
    """Convierte un observation de observations.json al formato de onboarding YAML.
    
    El formato retornado debe ser compatible con lo que espera run_v4_complete_mode()
    en main.py:1745-1788: datos_operativos.habitaciones, .reservas_mes, .valor_reserva_cop,
    .canal_directo_pct, y metadatos.fecha_captura, .campos_confirmados.
    """
    from datetime import datetime, timezone
    
    return {
        'hotel': {
            'nombre': obs.get('hotel_name', ''),
            'url': obs.get('website', ''),
            'ubicacion': obs.get('region', ''),
        },
        'datos_operativos': {
            'habitaciones': obs.get('rooms', 10),
            'reservas_mes': obs.get('monthly_reservations', 0),
            'valor_reserva_cop': obs.get('avg_reservation_cop', 0),
            'canal_directo_pct': obs.get('direct_channel_percentage', 20.0),
        },
        'metadatos': {
            'fuente': 'observations_tier_a',
            'fecha_captura': obs.get('collected_at', datetime.now(timezone.utc).isoformat()),
            'confidence': obs.get('confidence', 0.0),
            'epistemic_status': obs.get('epistemic_status', 'verified'),
            'campos_confirmados': ['habitaciones', 'reservas_mes', 'valor_reserva_cop', 'canal_directo_pct'],
            'source_note': f"Datos de observations.json (Tier A, confidence {obs.get('confidence', 'N/A')})",
        },
    }
```

### Verificación de mapeo de campos

**observations.json → onboarding format**:

| Campo observations.json | → | Campo onboarding dict |
|---|---|---|
| `hotel_name` | → | `hotel.nombre` |
| `website` | → | `hotel.url` |
| `region` | → | `hotel.ubicacion` |
| `rooms` | → | `datos_operativos.habitaciones` |
| `monthly_reservations` | → | `datos_operativos.reservas_mes` |
| `avg_reservation_cop` | → | `datos_operativos.valor_reserva_cop` |
| `direct_channel_percentage` | → | `datos_operativos.canal_directo_pct` |
| `collected_at` | → | `metadatos.fecha_captura` |
| `confidence` | → | `metadatos.confidence` |
| `epistemic_status` | → | `metadatos.epistemic_status` |

**IMPORTANTE**: El campo `website` DEBE existir en los observations de `observations.json` para que el matching funcione. Verificar que los 6 hoteles existentes tengan el campo `website`. Si no lo tienen, este fallback no podrá matchear — se necesita un paso adicional de enriquecimiento. Revisar el observation de Zi One Luxury (línea 114) para confirmar.

**Si `website` no existe en observations.json**: Agregar `"website": "https://zione.co/"` al observation de Zi One Luxury como parte de esta fase. Para los demás hoteles, documentar como deuda técnica.

### Restricciones

- ❌ NO modificar la lógica principal de matching por YAML — el fallback solo se ejecuta si ningún YAML matchea
- ✅ El fallback es silencioso — si falla, simplemente retorna None (mismo comportamiento que antes)
- ✅ `_observation_to_onboarding_format()` debe ser una función separada (testeable unitariamente)
- ✅ El path `data/hotel_observations/observations.json` es hardcodeado (el warehouse tiene ubicación fija)

### Criterios de completitud

- [ ] **T0**: Los 6 observations en `observations.json` tienen campo `website` con URL real
- [ ] `_load_latest_onboarding_data()` tiene fallback a `observations.json` después del loop de YAML
- [ ] `_observation_to_onboarding_format()` existe y mapea todos los campos de la tabla
- [ ] El diccionario retornado tiene la misma estructura que un YAML de onboarding
- [ ] Si `observations.json` no existe o un observation no tiene `website`, el fallback no crashea

### Verificación manual

```bash
# Verificar que los websites existen en observations.json
python3 -c "import json; d=json.load(open('data/hotel_observations/observations.json')); [print(o.get('hotel_name','?'), '→', o.get('website','SIN WEBSITE')) for o in d['observations']]"

# Verificar que el fallback existe
grep -A 10 "observations.json" main.py

# Verificar el helper
grep -A 20 "def _observation_to_onboarding_format" main.py
```

### Próxima sesión

**FASE-3**: Tests de regresión para `_normalize_url()`, URL-based matching, observations.json fallback, y frescura configurable. MEDIA complejidad. ⚠️ PARCIAL delegate_task.

Carga: `05-prompt-fase-3.md`
