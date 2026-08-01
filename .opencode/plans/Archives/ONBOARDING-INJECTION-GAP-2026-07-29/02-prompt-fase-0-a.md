# FASE-0-A: Reescribir `_load_latest_onboarding_data()` + `_normalize_url()` + Eliminar Ventana de Frescura

> **REGLA**: Una fase = una sesion. No ejecutar multiples fases aqui.
> **Tipo de ejecucion**: DIRECTA (no delegable — requiere comprension del flujo bimodal completo)
> **Complejidad**: ALTA ⚠️
> **Plan**: `ONBOARDING-INJECTION-GAP-2026-07-29/01-plan-maestro.md`
> **⚠️ PRECONDICION**: Esta fase DEBE ejecutarse antes que FASE-0-B (el caller necesita la nueva firma)

## Contexto previo

El pipeline bimodal de iah-cli tiene dos comandos que deben interoperar:
1. `onboard --url https://zione.co/ --hotel-name "Zi One Luxury"` → guarda `output/clientes/zi-one-luxury_onboarding.yaml`
2. `v4complete --url https://zione.co/` → busca `output/clientes/zione_onboarding.yaml` (deriva "Zione" del dominio)

**Nunca hay match** porque cada comando deriva el slug de inputs distintos. La causa raiz: no hay identificador canonico compartido.

Esta fase implementa el NUCLEO del nuevo mecanismo: la funcion de matching por URL normalizada. Sin esto, los cambios en FASE-0-B (CAMBIOS A y B) no tienen sentido.

## Objetivo de esta fase

Reescribir `_load_latest_onboarding_data()` para matchear por URL normalizada en vez de slug, agregar `_normalize_url()`, y eliminar la ventana de frescura bloqueante.

### Tareas

- [ ] **T1 — CAMBIO C**: Reescribir `_load_latest_onboarding_data()` con matching por URL normalizada
- [ ] **T2**: Implementar `_normalize_url()` como funcion auxiliar pura
- [ ] **T3 — Fix 3**: Eliminar ventana de frescura de 24h (o hacerla configurable via `ONBOARDING_FRESHNESS_HOURS`)

### Detalle T1 — CAMBIO C (main.py ~3396-3445)

**Archivo**: `main.py:3396-3452`

Reemplazar la funcion completa `_load_latest_onboarding_data()` con la nueva version que busca por URL normalizada.

**Nueva firma**:
```python
def _load_latest_onboarding_data(
    hotel_url: str,
    hotel_name: str,
    output_dir: Path | None = None,
) -> Dict[str, Any] | None:
```

**Nuevo algoritmo**:
1. `output_dir = output_dir or Path("output/clientes")` — respeta el parametro, fallback al default
2. Si el directorio no existe → None
3. `normalized_url = _normalize_url(hotel_url)`
4. Iterar sobre `output_dir.glob("*_onboarding.yaml")`:
   - Cargar YAML
   - Si no tiene `metadatos` → skip
   - Obtener `yaml_url = data.get('hotel', {}).get('url', '')`
   - Si `yaml_url` no esta vacio y `_normalize_url(yaml_url) == normalized_url` → MATCH
   - Validar frescura (T3) y retornar data
5. Si ningun archivo matchea → None

**Implementacion**:
```python
def _load_latest_onboarding_data(
    hotel_url: str,
    hotel_name: str,
    output_dir: Path | None = None,
) -> Dict[str, Any] | None:
    """Carga datos de onboarding mas recientes del hotel por URL normalizada.

    Busca en todos los archivos YAML del directorio de clientes y matchea
    por URL normalizada en vez de slug derivado de nombre.

    Args:
        hotel_url: URL del hotel (ej. https://zione.co/)
        hotel_name: Nombre del hotel (solo para logging, no se usa para matching)
        output_dir: Directorio donde buscar YAMLs. Default: output/clientes/

    Returns:
        Diccionario con datos de onboarding o None si no existe
    """
    import yaml

    clientes_dir = output_dir or Path("output/clientes")
    if not clientes_dir.exists():
        return None

    normalized_url = _normalize_url(hotel_url)

    for yaml_file in clientes_dir.glob("*_onboarding.yaml"):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception:
            continue

        if not data or 'metadatos' not in data:
            continue

        yaml_url = data.get('hotel', {}).get('url', '')
        if not yaml_url:
            continue

        if _normalize_url(yaml_url) != normalized_url:
            continue

        # Frescura: verificacion via env var (Fix 3 — ver T3)
        # Si ONBOARDING_FRESHNESS_HOURS no esta seteada, no hay limite
        freshness_hours = os.getenv("ONBOARDING_FRESHNESS_HOURS")
        if freshness_hours:
            from datetime import datetime, timezone, timedelta
            fecha_str = data.get('metadatos', {}).get('fecha_captura')
            if fecha_str:
                fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                if fecha.tzinfo is None:
                    fecha = fecha.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - fecha > timedelta(hours=int(freshness_hours)):
                    continue  # Data demasiado vieja, seguir buscando

        return data

    return None
```

**IMPORTANTE**: La funcion YA NO importa `generate_slug` ni `datetime` incondicionalmente. Solo importa `yaml` al inicio. `datetime` se importa bajo demanda (solo si hay env var de frescura).

**Deteccion de archivos viejos (pre-CAMBIO A)**: Si un YAML no tiene `hotel.url` (porque fue generado con la version actual del codigo), el loader lo ignora y sigue al siguiente archivo. Esto es intencional — sin URL en el YAML, no hay como matchear. El comportamiento resultante (retornar None) es identico al comportamiento actual.

### Detalle T2 — `_normalize_url()`

**Archivo**: `main.py` (funcion nueva, justo antes de `_load_latest_onboarding_data`)

```python
def _normalize_url(url: str) -> str:
    """Normaliza URL para matching canonico.

    Reduce https://www.zione.co/ → zione.co
    Ignora: protocolo, www, trailing slash, path, query string.
    """
    from urllib.parse import urlparse
    p = urlparse(url.rstrip('/'))
    return p.netloc.replace('www.', '').lower()
```

**Casos de prueba mental**:
- `https://zione.co/` → `zione.co`
- `https://www.zione.co/` → `zione.co`
- `http://zione.co` → `zione.co`
- `https://www.hotel.com/es/` → `hotel.com`
- `https://hotel.co?lang=es` → `hotel.co`
- `https://ZIONE.CO/` → `zione.co`
- `https://www.sub.domain.co/` → `sub.domain.co`
- `zione.co` → `zione.co`

### Detalle T3 — Fix 3 (Eliminar ventana de frescura)

**Opcion implementada (hibrida)**:
1. **Eliminar** el bloque de frescura hardcodeado (lineas 3427-3439 del codigo actual)
2. **Agregar** soporte opcional via `ONBOARDING_FRESHNESS_HOURS` env var (ya incluido en T1)
3. Por defecto (sin env var): sin limite de frescura. El dato operativo no caduca.

El campo `fecha_captura` se mantiene en el YAML y en el diccionario retornado para trazabilidad.

### Restricciones

- ❌ NO modificar `generate_slug()` — se mantiene para otros usos (solo se deja de usar en el loader)
- ❌ NO tocar `_extract_hotel_name_from_url()` — sigue siendo necesaria para derivar nombre cuando no hay `--nombre`
- ✅ La funcion DEBE seguir retornando `Dict[str, Any] | None` — misma interfaz
- ✅ El nuevo parametro `output_dir` tiene default `None` — compatible hacia atras
- ✅ Si ningun YAML tiene `hotel.url` (datos viejos pre-CAMBIO A), el loader retorna `None` — mismo comportamiento que antes
- ✅ La iteracion por glob es O(N) en numero de archivos YAML (tipicamente <50). Aceptable.

### Criterios de completitud

- [ ] `_load_latest_onboarding_data()` busca por `_normalize_url()` en vez de `generate_slug()`
- [ ] La firma acepta `output_dir: Path | None = None`
- [ ] `_normalize_url("https://www.zione.co/")` → `"zione.co"`
- [ ] `_normalize_url("http://hotel.com/es?lang=es")` → `"hotel.com"`
- [ ] `_normalize_url("https://ZIONE.CO/")` → `"zione.co"` (case-insensitive)
- [ ] Ventana de frescura hardcodeada eliminada; `ONBOARDING_FRESHNESS_HOURS` soportado como opcional
- [ ] El import `from modules.onboarding.data_loader import generate_slug` ya no esta en la funcion
- [ ] La funcion itera sobre `glob("*_onboarding.yaml")` en vez de construir path por slug

### Verificacion manual post-implementacion

```bash
# 1. Verificar que _normalize_url existe y es correcta
grep -A 8 "def _normalize_url" main.py

# 2. Verificar que el loader ya no usa generate_slug
grep "generate_slug" main.py | grep -v "run_onboard_mode"

# 3. Verificar que la firma acepta output_dir
grep "def _load_latest_onboarding_data" main.py

# 4. Verificar glob iteration
grep "glob" main.py | grep "_onboarding"
```

### Proxima sesion

**FASE-0-B**: CAMBIO A (persistir `hotel.url` en YAML) + CAMBIO B (pasar `output_dir` desde el caller) + agregar `'url': None` al template de onboarding. 3 tareas, complejidad MEDIA.

Carga: `03-prompt-fase-0-b.md`
