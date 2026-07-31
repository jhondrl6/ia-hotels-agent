# FASE-3: MIN-01 (Tabla Status Quo vs Implementación)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DELEGAR vía `delegate_task` con toolsets `['terminal', 'file']`

## Contexto previo

- **FASE-0** ✅: Verificación completada.
- **FASE-1A** ✅: IMP-03 (CAPEX) + F7 (gate) implementados.
- **FASE-1B** ✅: F5 (ADR checklist) corregido.
- **FASE-2** ✅: MIN-02 (ADR evidenciado) implementado en YAML+código+template.
- Tests pasando.

## Objetivo de esta fase

Implementar **MIN-01: Tabla comparativa Status Quo vs Implementación IAO** en la propuesta comercial.
El hotelero necesita visualizar el costo de NO implementar (pérdida mensual actual)
frente al escenario con implementación (reducción de pérdida + ROI).

---

### Tareas

- [ ] **T1: Implementar `_build_status_quo_table()` en v4_proposal_generator.py**

  Crear método que genera tabla markdown comparativa:

  ```python
  def _build_status_quo_table(self, financial_data: dict, region: str) -> str:
      """Construye tabla comparativa: sin IAO vs con IAO.
      
      Muestra pérdida mensual actual, reducción esperada y ROI.
      """
      # Datos disponibles del scenario calculator
      current_loss = financial_data.get('monthly_loss_cop', 0)
      recovery_pct = financial_data.get('recovery_percentage', 0)
      recovered_amount = financial_data.get('recovered_amount_cop', 0)
      roicr = financial_data.get('roicr', 0)
      payback_months = financial_data.get('payback_months', 'N/A')
      
      # Escenario sin implementar (status quo)
      annual_loss = current_loss * 12
      loss_formatted = f"${annual_loss:,.0f} COP".replace(',', '.')
      
      # Escenario con implementación
      annual_recovery = recovered_amount * 12
      recovery_formatted = f"${annual_recovery:,.0f} COP".replace(',', '.')
      
      table = (
          "| Escenario | Pérdida anual | Recuperación | ROI |\n"
          "|-----------|--------------|-------------|-----|\n"
          f"| Sin IAO (actual) | -{loss_formatted}/año | — | — |\n"
          f"| Con IAO | Reducción {recovery_pct*100:.0f}% | +{recovery_formatted}/año | {roicr:.2f}x |\n"
      )
      return table
  ```

  **Pasos:**
  1. Leer el generador para encontrar datos financieros disponibles:
     ```bash
     grep -n "monthly_loss\|recovery\|roicr\|payback" modules/commercial_documents/v4_proposal_generator.py
     ```
  2. Identificar qué keys están en el financial_data dict al momento de construir la propuesta
  3. Adaptar el método con las keys reales encontradas (no asumir)
  4. Insertar el método en la clase antes del data dict

  **PITFALL:** Los valores financieros pueden venir de `financial_breakdown`, `scenarios`,
  o `diagnostic_summary`. Verificar cuáles están disponibles en el scope de construcción
  del data dict.

- [ ] **T2: Añadir `${status_quo_table}` en propuesta_v6_template.md**

  Insertar ANTES de la sección de escenarios detallados (si existe) o después de
  la sección de impacto financiero:

  ```markdown
  ### Status Quo vs Implementación

  ${status_quo_table}

  > **Interpretación:** La diferencia entre ambos escenarios representa el valor
  > anual que el hotel deja sobre la mesa al no implementar IAO.
  ```

  **Pasos:**
  1. Leer el template para encontrar la mejor ubicación
  2. Insertar la sección con el placeholder
  3. Verificar consistencia del placeholder con la key del data dict

- [ ] **T3: Inyectar `status_quo_table` en el data dict**

  ```python
  # Pre-computar ANTES del data dict
  _status_quo = self._build_status_quo_table(financial_data, region)
  ```

  Y en el data dict:
  ```python
  'status_quo_table': _status_quo,
  ```

- [ ] **T4: Tests + Estado de fase**
  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli
  ./venv/Scripts/python.exe -m pytest tests/ --timeout=60 -x -q 2>&1 | tail -20
  ```
  Marcar T1-T4 como completadas en `06-checklist-implementacion.md`.

### Restricciones

- **NO ejecutar v4complete**
- **NO modificar `regional_benchmarks.yaml`**
- **NO modificar `publication_gates.py`**
- Usar `.replace(',', '.')` para formato COP colombiano
- Si algún valor financiero es 0/None, mostrar "—" en vez de "$0 COP"
- Máximo 60 iteraciones (R2)

### Criterios de completitud

- [ ] `_build_status_quo_table()` implementado con datos financieros reales
- [ ] `${status_quo_table}` placeholder en el template
- [ ] `status_quo_table` key en el data dict del generador
- [ ] Formato COP correcto (puntos como separadores de miles)
- [ ] Todos los tests existentes pasan
- [ ] Estado actualizado en checklist

### Archivos involucrados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | Nuevo método + data dict |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Nueva sección + placeholder |

### Próxima sesión

```
Carga y ejecuta .opencode/plans/REFACTOR-PENDIENTE-V4.58.0/05-prompt-inicio-sesion-fase-4.md
```

Esa fase implementa MIN-03 (closing pitch dinámico basado en ROICR).
