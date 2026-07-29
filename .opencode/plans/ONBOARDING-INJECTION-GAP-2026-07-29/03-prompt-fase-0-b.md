# FASE-0-B: CAMBIO A (persistir hotel.url) + CAMBIO B (pasar output_dir) + Template url

> **REGLA**: Una fase = una sesion. No ejecutar multiples fases aqui.
> **Tipo de ejecucion**: DIRECTA (no delegable — modifica 3 archivos cross-module)
> **Complejidad**: MEDIA
> **Plan**: `ONBOARDING-INJECTION-GAP-2026-07-29/01-plan-maestro.md`
> **⚠️ PRECONDICION**: FASE-0-A DEBE estar completada. Esta fase consume la nueva firma de `_load_latest_onboarding_data()`.

## Contexto previo

**FASE-0-A completada**: `_load_latest_onboarding_data()` ahora acepta `output_dir`, busca por URL normalizada via `_normalize_url()`, y tiene frescura configurable via `ONBOARDING_FRESHNESS_HOURS`.

Ahora hay que conectar los extremos: que `onboard` persista `hotel.url` en el YAML (para que el loader pueda matchear), que `v4complete` pase `output_dir` configurable, y que la plantilla de onboarding tenga el campo `url`.

## Objetivo de esta fase

Cerrar el circuito productor-consumidor: `onboard` produce `hotel.url` → `v4complete` pasa `output_dir` al loader → loader matchea.

### Tareas

- [ ] **T1 — CAMBIO A**: `run_onboard_mode()` persiste `hotel.url` en el YAML
- [ ] **T2**: Agregar `'url': None` a `create_onboarding_template()` en `data_loader.py`
- [ ] **T3 — CAMBIO B**: `run_v4_complete_mode()` pasa `output_dir` configurable al loader

### Detalle T1 — CAMBIO A (main.py ~1072)

**Archivo**: `main.py:1067-1077` (dentro de `run_onboard_mode`)

**CODIGO ACTUAL**:
```python
    hotel_slug = generate_slug(hotel_nombre) if hotel_nombre else "hotel"
    if args.output_format == "yaml":
        output_path = output_dir / f"{hotel_slug}_onboarding.yaml"
        form.save_yaml(output_path)
```

**CAMBIAR A**:
```python
    hotel_slug = generate_slug(hotel_nombre) if hotel_nombre else "hotel"
    
    # CAMBIO A: Persistir hotel.url como clave canonica para matching futuro
    # IMPORTANTE: OnboardingForm usa self._data dict, NO atributos de objeto.
    # save_yaml() escribe self._data via yaml.dump().
    if args.url:
        form._data['hotel']['url'] = args.url.rstrip('/')
    
    if args.output_format == "yaml":
        output_path = output_dir / f"{hotel_slug}_onboarding.yaml"
        form.save_yaml(output_path)
```

**POR QUE ESTO Y NO `form.hotel_url = ...`**: `OnboardingForm` (forms.py L74-87) inicializa `self._data = create_onboarding_template()`. `save_yaml()` (L251-277) escribe `yaml.dump(self._data)`. `form.hotel_url = ...` crearia un atributo Python en el objeto que NUNCA se serializa. La unica forma de que `hotel.url` aparezca en el YAML es inyectarlo en `self._data['hotel']['url']`.

### Detalle T2 — Agregar `'url': None` al template

**Archivo**: `modules/onboarding/data_loader.py:99-122`

**CODIGO ACTUAL** (L106-110):
```python
    return {
        "hotel": {
            "nombre": None,
            "ubicacion": None,
        },
```

**CAMBIAR A**:
```python
    return {
        "hotel": {
            "nombre": None,
            "ubicacion": None,
            "url": None,  # CAMBIO A: clave canonica para matching futuro
        },
```

**Justificacion**: `create_onboarding_template()` es la fuente de verdad de la estructura del YAML. Si el campo `url` no existe en el template, el `_data` del form no tiene la key `hotel.url` hasta que se inyecta manualmente (T1). Agregarlo aqui hace que la estructura sea explicita y documentada.

### Detalle T3 — CAMBIO B (main.py ~1739)

**Archivo**: `main.py:1739` (dentro de `run_v4_complete_mode`)

**CODIGO ACTUAL**:
```python
    onboarding_data = _load_latest_onboarding_data(args.url, hotel_name)
```

**CAMBIAR A**:
```python
    clientes_dir = Path(args.output) / "clientes"
    onboarding_data = _load_latest_onboarding_data(
        hotel_url=args.url,
        hotel_name=hotel_name,
        output_dir=clientes_dir,
    )
```

Esto requiere importar `Path` si no esta ya importado en el scope de la funcion (verificar — probablemente ya se importa en L1599: `from pathlib import Path`).

### Restricciones

- ❌ NO modificar `save_yaml()` — escribe `self._data` y eso es correcto
- ❌ NO modificar `run_onboard_mode()` mas alla de T1
- ✅ Verificar que `run_v4_complete_mode` tiene `Path` importado (L1599: `from pathlib import Path` — SI esta)
- ✅ Si `args.url` es None en T1, no se inyecta nada — seguridad
- ✅ El orden T1 → T2 → T3 es el recomendado (template → productor → consumidor), pero T2 y T1 pueden invertirse

### Criterios de completitud

- [ ] `onboard --url https://zione.co/` escribe `hotel.url: https://zione.co` en el YAML
- [ ] `create_onboarding_template()` tiene `'url': None` en el dict `hotel`
- [ ] `run_v4_complete_mode()` pasa `output_dir=Path(args.output)/"clientes"` al loader
- [ ] `grep "form._data\['hotel'\]\['url'\]" main.py` → existe (CAMBIOS A)
- [ ] `grep "'url': None" modules/onboarding/data_loader.py` → existe en create_onboarding_template
- [ ] `grep "output_dir=" main.py | grep "_load_latest_onboarding_data"` → existe (CAMBIO B)

### Verificacion manual

```bash
# 1. Verificar CAMBIO A (inyeccion en _data)
grep -A2 "form._data\['hotel'\]\['url'\]" main.py

# 2. Verificar template
grep -A3 "def create_onboarding_template" modules/onboarding/data_loader.py | grep url

# 3. Verificar CAMBIO B (caller pasa output_dir)
grep -B2 -A4 "_load_latest_onboarding_data" main.py | grep output_dir
```

### Proxima sesion

**FASE-1**: Alineacion taxonomica (`user_provided` en `EvidenceTier`) + fix mensaje deprecado (`audit` → `v4complete`). 2 one-liners en `scenario_calculator.py` y `main.py`. BAJA complejidad. ✅ VIABLE delegate_task.

Carga: `04-prompt-fase-1.md`
