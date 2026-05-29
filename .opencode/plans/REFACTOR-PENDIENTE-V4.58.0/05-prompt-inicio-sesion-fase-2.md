# FASE-2: MIN-02 (ADR Evidenciado) — ⭐ MÁS COMPLEJA

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA — **NO DELEGAR**. Esta fase requiere razonamiento iterativo
> sobre triple capa (YAML + Python pipeline + Template). Delegar aumenta riesgo de
> integración incorrecta entre capas.

## Contexto previo

- **FASE-0** ✅: Verificación completada.
- **FASE-1A** ✅: IMP-03 (CAPEX) + F7 (gate) implementados.
- **FASE-1B** ✅: F5 (ADR checklist) corregido con lectura en cascada.
- El helper `_get_adr_from_benchmarks()` ya existe en `v4_proposal_generator.py`.
- Tests pasando.

## Objetivo de esta fase

Implementar **MIN-02: ADR evidenciado en la propuesta comercial**. El hotelero necesita
ver el ADR (Average Daily Rate) como dato de referencia regional en la propuesta,
no como campo vacío. Esto requiere cambios en 3 capas:

1. **Config**: Añadir ADR en `regional_benchmarks.yaml` para todas las regiones
2. **Pipeline**: Inyectar ADR en el data dict que alimenta el template
3. **Template**: Añadir placeholders para renderizar ADR en el output

---

### Tareas

- [ ] **T1: Añadir ADR en `config/regional_benchmarks.yaml`**

  **Valores de referencia (COP, 2026):**
  ```yaml
  eje_cafetero:
    adr: 285000
    occupancy_rate: 0.55
    # ... otros campos existentes

  caribe:
    adr: 320000
    occupancy_rate: 0.62
    # ...

  andina:
    adr: 310000
    occupancy_rate: 0.58
    # ...

  pacifico:
    adr: 265000
    occupancy_rate: 0.50
    # ...

  amazonia_orinoquia:
    adr: 245000
    occupancy_rate: 0.48
    # ...

  bogota:
    adr: 350000
    occupancy_rate: 0.65
    # ...
  ```

  **Pasos:**
  1. Leer el YAML completo para entender la estructura actual:
     ```bash
     cat config/regional_benchmarks.yaml
     ```
  2. Añadir `adr` key a cada región (preservar valores existentes)
  3. Verificar sintaxis YAML:
     ```bash
     ./venv/Scripts/python.exe -c "import yaml; yaml.safe_load(open('config/regional_benchmarks.yaml'))"
     ```

  **Regla:** Los nombres de región deben coincidir EXACTAMENTE con los del tuple
  `validated_regions` (lowercase + underscores). Si el YAML usa "Eje Cafetero"
  como key, normalizar a "eje_cafetero".

- [ ] **T2: Inyectar `adr_display` en el data dict del proposal generator**

  **Archivo:** `modules/commercial_documents/v4_proposal_generator.py`

  Buscar dónde se construye el data dict (dictionary literal grande con todas las
  variables del template). Añadir:

  ```python
  # Pre-computar ANTES del data dict (ver pitfall: dict-literal-insertion)
  _adr_value = self._get_adr_from_benchmarks(region)
  _adr_display = f"${_adr_value:,.0f} COP" if _adr_value else "No disponible"
  ```

  Y dentro del data dict:
  ```python
  'adr_display': _adr_display,
  'adr_value': _adr_value,
  ```

  **PITFALL CRÍTICO — Dict literal insertion:**
  NO insertar declaraciones `if`/`for`/`=` DENTRO del diccionario literal.
  Python solo acepta `key: value`. Pre-computar ARRIBA del `data = {`.

  Verificar que `_get_adr_from_benchmarks` ya existe (creado en FASE-1B).

- [ ] **T3: Añadir placeholders ADR en propuesta_v6_template.md**

  Buscar la sección de "Datos de referencia" o "Benchmarks regionales" en el template.
  Si no existe, añadir nueva subsección:

  ```markdown
  #### Referencia regional

  | Métrica | Valor |
  |---------|-------|
  | ADR regional promedio | ${adr_display} |
  ```

  **Pasos:**
  1. Leer el template para encontrar el mejor punto de inserción
  2. Añadir la subsección con el placeholder
  3. Verificar que `${adr_display}` es consistente con la key del data dict

  **Verificación caller (IMPORTANTE):**
  Después de añadir el placeholder, verificar que el generador efectivamente
  pasa la key en su placeholders dict:
  ```bash
  grep -n "adr_display" modules/commercial_documents/v4_proposal_generator.py
  ```

- [ ] **T4: Tests + Estado de fase**

  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli

  # Tests completos
  ./venv/Scripts/python.exe -m pytest tests/ --timeout=60 -x -q 2>&1 | tail -20

  # Verificación rápida de YAML
  ./venv/Scripts/python.exe -c "
  import yaml
  with open('config/regional_benchmarks.yaml') as f:
      data = yaml.safe_load(f)
  for region in ['eje_cafetero', 'caribe', 'andina', 'pacifico', 'amazonia_orinoquia', 'bogota']:
      adr = data.get(region, {}).get('adr', 'MISSING')
      print(f'  {region}: adr={adr}')
  "
  ```

  Marcar T1-T4 como completadas en `06-checklist-implementacion.md`.

### Restricciones

- **NO ejecutar v4complete** — solo código + tests
- **NO modificar `publication_gates.py`** — ya arreglado en FASE-1A
- **NO modificar `_build_coherence_checklist()`** — ya arreglado en FASE-1B
- Pre-computar variables ANTES de dict literals (no dentro)
- Los nombres de región en YAML deben ser lowercase_underscore
- Máximo 60 iteraciones (R2)

### Criterios de completitud

- [ ] `adr` key presente en todas las regiones de `regional_benchmarks.yaml`
- [ ] `adr_display` y `adr_value` en el data dict del proposal generator
- [ ] `${adr_display}` placeholder en el template con sección de benchmarks
- [ ] YAML parsea correctamente (sin errores de sintaxis)
- [ ] Todos los tests existentes pasan
- [ ] Estado actualizado en checklist

### Archivos involucrados

| Archivo | Cambio |
|---------|--------|
| `config/regional_benchmarks.yaml` | Añadir `adr` a todas las regiones |
| `modules/commercial_documents/v4_proposal_generator.py` | Inyectar adr en data dict |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Añadir sección ADR |

### Riesgos y mitigaciones

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|-----------|
| Nombre de región mal normalizado | ALTA | grep validated_regions antes de escribir |
| Dict literal insertion pitfall | MEDIA | Pre-computar variables arriba del `data = {` |
| Benchmark Loader no existe | MEDIA | Fallback a yaml.safe_load directo |
| Tests de coherence_checklist fallan | BAJA | El helper cascada (FASE-1B) ya es defensivo |

### Próxima sesión

```
Carga y ejecuta .opencode/plans/REFACTOR-PENDIENTE-V4.58.0/05-prompt-inicio-sesion-fase-3.md
```

Esa fase implementa MIN-01 (tabla Status Quo vs Implementación).
