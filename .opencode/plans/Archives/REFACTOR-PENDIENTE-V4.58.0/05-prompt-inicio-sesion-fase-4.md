# FASE-4: MIN-03 (Closing Pitch Dinámico)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DELEGAR vía `delegate_task` con toolsets `['terminal', 'file']`

## Contexto previo

- **FASE-0 a FASE-3** ✅: Todos los gaps previos implementados.
- Gaps restantes: MIN-03 (closing pitch), dead code (FASE-5).
- ADR evidenciado ✅, Status Quo ✅, CAPEX breakdown ✅.
- Tests pasando.

## Objetivo de esta fase

Implementar **MIN-03: Closing pitch dinámico** que reemplace el texto estático
"SIGUIENTE PASO" del template con un cierre personalizado basado en los datos
financieros del hotel (ROICR, payback, recuperación mensual).

---

### Tareas

- [ ] **T1: Implementar `_build_closing_pitch()` en v4_proposal_generator.py**

  ```python
  def _build_closing_pitch(self, financial_data: dict, hotel_name: str) -> str:
      """Genera pitch de cierre personalizado basado en ROI y payback.
      
      Reemplaza el texto estático "SIGUIENTE PASO" con copy dinámico.
      """
      roicr = financial_data.get('roicr', 0)
      payback_months = financial_data.get('payback_months', 12)
      recovered_monthly = financial_data.get('recovered_amount_cop', 0)
      
      # Tier de urgencia basado en ROICR
      if roicr >= 3.0:
          urgency = "urgente"
          emoji = "🔴"
      elif roicr >= 1.5:
          urgency = "significativa"
          emoji = "🟡"
      else:
          urgency = "moderada"
          emoji = "🟢"
      
      # Formato COP
      recovery_fmt = f"${recovered_monthly:,.0f}".replace(',', '.')
      
      # Payback en meses/años
      if payback_months and payback_months > 0:
          if payback_months <= 12:
              payback_text = f"{payback_months:.0f} meses"
          else:
              payback_text = f"{payback_months/12:.1f} años"
      else:
          payback_text = "el primer año"
      
      pitch = (
          f"### {emoji} Oportunidad de {urgency.title()} para {hotel_name}\n\n"
          f"Su hotel puede recuperar **{recovery_fmt} COP mensuales** "
          f"con una inversión que se paga sola en **{payback_text}** "
          f"(ROICR: {roicr:.2f}x).\n\n"
          f"**Siguiente paso:** Agendemos una llamada de 15 minutos para "
          f"revisar su caso específico y diseñar el plan de implementación.\n"
      )
      return pitch
  ```

  **Pasos:**
  1. Verificar qué datos financieros están disponibles en el scope:
     ```bash
     grep -n "roicr\|payback\|recovered" modules/commercial_documents/v4_proposal_generator.py | head -15
     ```
  2. Adaptar las keys del método con lo disponible realmente
  3. El hotel_name puede venir de `validated_data.get('hotel_name')` o similar
  4. Insertar el método en la clase

- [ ] **T2: Reemplazar texto duro en template con `${closing_pitch}`**

  Buscar el texto estático alrededor de L214-220:
  ```bash
  grep -n "SIGUIENTE PASO\|Siguiente paso\|PRÓXIMO PASO" modules/commercial_documents/templates/propuesta_v6_template.md
  ```

  Reemplazar el bloque de texto estático con:
  ```markdown
  ${closing_pitch}
  ```

  **Nota:** Si el texto estático es multi-línea y tiene formato de tabla o lista,
  reemplazar TODO el bloque con el placeholder.

- [ ] **T3: Inyectar `closing_pitch` en el data dict**

  ```python
  # Pre-computar ANTES del data dict
  _hotel_name = validated_data.get('hotel_name', 'su hotel')
  _closing = self._build_closing_pitch(financial_data, _hotel_name)
  ```

  En el data dict:
  ```python
  'closing_pitch': _closing,
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
- **NO modificar gates**
- Formato COP con puntos como separadores de miles
- Si ROICR es 0 o None, usar valores por defecto sin crash
- Máximo 60 iteraciones (R2)

### Criterios de completitud

- [ ] `_build_closing_pitch()` implementado con datos financieros dinámicos
- [ ] Texto estático "SIGUIENTE PASO" eliminado del template
- [ ] `${closing_pitch}` placeholder en el template
- [ ] `closing_pitch` key en el data dict del generador
- [ ] Copy incluye: emoji de urgencia + monto recuperación + payback + ROICR
- [ ] Todos los tests existentes pasan
- [ ] Estado actualizado en checklist

### Archivos involucrados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | Nuevo método + data dict |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Reemplazar texto estático |

### Próxima sesión

```
Carga y ejecuta /.opencode/plans/Archives/REFACTOR-PENDIENTE-V4.58.0/05-prompt-inicio-sesion-fase-5.md
```

Esa fase elimina el template embebido muerto (deuda técnica).
