# FASE-1B: F5 (ADR Checklist siempre [PENDING])

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DELEGAR vía `delegate_task` con toolsets `['terminal', 'file']`

## Contexto previo

- **FASE-0** ✅: Verificación completada.
- **FASE-1A** ✅: IMP-03 (CAPEX breakdown en template) + F7 (gate unificado) implementados.
- Tests pasando.

## Objetivo de esta fase

Corregir el bug F5: la coherence checklist siempre muestra `[PENDING]` para ADR
porque `_build_coherence_checklist()` busca `validated_data.get('adr')` que siempre es `None`.

---

### Tareas

- [ ] **T1: Trazar el flujo de datos de ADR**

  Antes de cambiar código, entender:
  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli

  # 1. Dónde se construye validated_data
  grep -n "validated_data" modules/commercial_documents/v4_proposal_generator.py | head -20

  # 2. De dónde viene diagnostic_summary.validated_data_summary
  grep -rn "validated_data_summary" modules/commercial_documents/

  # 3. Dónde _extract_adr_from_audit() se usa
  grep -n "_extract_adr_from_audit" modules/commercial_documents/v4_diagnostic_generator.py

  # 4. La línea exacta del bug (alrededor de L1934)
  grep -n "adr" modules/commercial_documents/v4_proposal_generator.py
  ```

  **Nota importante:** El fix aquí es PARCIAL. Esta fase solo corrige el PUNTO DE LECTURA
  para que use una fuente real (benchmark YAML o _extract_adr_from_audit). La inyección
  completa de ADR en benchmarks va en **FASE-2**. Aquí solo hacemos que el código
  NO siempre retorne "Pendiente" cuando hay datos disponibles.

- [ ] **T2: Fix de `_build_coherence_checklist()`**

  **Archivo:** `modules/commercial_documents/v4_proposal_generator.py`
  **Alrededor de L1934:**

  El código actual (aproximado):
  ```python
  adr_value = validated_data.get('adr')   # ← siempre None
  adr_verified = adr_value is not None     # ← siempre False
  adr_detail = "Pendiente"                 # ← siempre "Pendiente"
  ```

  **Fix propuesto:** Buscar ADR en múltiples fuentes (cascada):
  ```python
  # Cascada de fuentes para ADR
  adr_value = (
      validated_data.get('adr')
      or self._get_adr_from_benchmarks(region)
      or None
  )
  adr_verified = adr_value is not None and adr_value > 0
  adr_display = f"${adr_value:,.0f} COP" if adr_verified else "Pendiente"
  ```

  **Crear método helper** `_get_adr_from_benchmarks(self, region)`:
  ```python
  def _get_adr_from_benchmarks(self, region: str) -> Optional[float]:
      """Obtener ADR desde benchmarks regionales."""
      try:
          from modules.utils.benchmark_loader import load_benchmarks
          benchmarks = load_benchmarks()
          region_data = benchmarks.get(region, {})
          return region_data.get('adr')
      except (ImportError, FileNotFoundError):
          return None
  ```

  **IMPORTANTE:**
  - Verificar primero si `benchmark_loader` existe; si no, usar `yaml.safe_load` directamente
  - No romper el contrato existente de `_build_coherence_checklist()`
  - El método `_get_adr_from_benchmarks` se reutilizará en FASE-2

- [ ] **T3: Tests de regresión**
  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli
  ./venv/Scripts/python.exe -m pytest tests/ --timeout=60 -x -q 2>&1 | tail -20
  ```

- [ ] **T4: Actualizar estado de fase**
  Marcar T1-T4 como completadas en `06-checklist-implementacion.md`.

### Restricciones

- **NO modificar `regional_benchmarks.yaml`** — los valores ADR se añaden en FASE-2
- **NO ejecutar v4complete**
- **NO modificar el template** — solo el generador
- El fix debe ser defensivo: si ADR no está en benchmarks, seguir mostrando "Pendiente"
  (eso es correcto; el benchmark se añade en FASE-2)
- Máximo 60 iteraciones (R2)

### Criterios de completitud

- [ ] `_build_coherence_checklist()` busca ADR en cascada (validated_data → benchmarks → None)
- [ ] Método `_get_adr_from_benchmarks()` implementado
- [ ] Cuando hay ADR en benchmarks, la checklist muestra valor real (no "Pendiente")
- [ ] Cuando NO hay ADR, sigue mostrando "Pendiente" (comportamiento defensivo correcto)
- [ ] Todos los tests existentes pasan
- [ ] Estado actualizado en checklist

### Archivos involucrados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | Fix cascada ADR + nuevo helper |

### Próxima sesión

```
Carga y ejecuta /.opencode/plans/Archives/REFACTOR-PENDIENTE-V4.58.0/05-prompt-inicio-sesion-fase-2.md
```

Esa fase implementa MIN-02 (ADR completo en propuesta) — **la más compleja del plan, ejecución directa sin delegar**.
