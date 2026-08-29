# FASE-6: v4complete Hotel Castilla Real (Verificación E2E + Post-Análisis)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DELEGAR vía `delegate_task` con toolsets `['terminal']`
> (subagent para el comando largo de v4complete con timeout 900s).

## Contexto previo

- **FASE-0 a FASE-5** ✅ TODAS completadas:
  - IMP-03: CAPEX breakdown en template ✅
  - F7: Gate discrepancy unificada ✅
  - F5: ADR checklist bug corregido ✅
  - MIN-02: ADR en benchmarks + propuesta ✅
  - MIN-01: Status Quo table implementada ✅
  - MIN-03: Closing pitch dinámico ✅
  - Dead code eliminado ✅
- Tests pasando.

## Objetivo de esta fase

**ÚNICA ejecución de v4complete** del plan. Ejecutar para Hotel Castilla Real y
verificar post-implementación que todos los 7 fixes se reflejan en el output real.

**Hotel:** Hotel Castilla Real
**URL:** https://www.hotelcastillareal.com/
**Baseline:** coherence 0.83, 9/11 gates, Tier B

---

### Tareas

- [ ] **T1: Ejecutar v4complete**
  
  Comando con timeout extendido:
  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli
  ./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
  ```
  
  **Parámetros de ejecución:**
  - `terminal(timeout=900)` — el comando puede tardar 8-15 minutos
  - `background=true, notify_on_complete=true` si disponible
  - Si falla por timeout, reintentar UNA vez
  - Si falla por error de red/API, documentar y reportar

- [ ] **T2: Guardar evidencia (OBLIGATORIO — sin importar tiempo restante)**

  Inmediatamente después de que v4complete genere output:
  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli
  mkdir -p evidence/FASE-PENDIENTE-V4COMPLETE

  # Copiar TODOS los outputs
  cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-PENDIENTE-V4COMPLETE/ 2>/dev/null
  cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-PENDIENTE-V4COMPLETE/ 2>/dev/null
  cp -r output/v4_complete/*/v4_audit/ evidence/FASE-PENDIENTE-V4COMPLETE/v4_audit/ 2>/dev/null
  
  # Copiar gate report
  find output/ -name "gate_report_*.json" -exec cp {} evidence/FASE-PENDIENTE-V4COMPLETE/ \; 2>/dev/null

  # Verificar evidencia copiada
  ls -la evidence/FASE-PENDIENTE-V4COMPLETE/
  ```

- [ ] **T3: Post-análisis — Verificación de cada fix**

  Para cada gap, verificar en el output real:

  **IMP-03 (CAPEX breakdown):**
  ```bash
  grep -n "capex_breakdown\|CAPEX\|Desglose" evidence/FASE-PENDIENTE-V4COMPLETE/02_PROPUESTA_*.md
  ```
  ✅ Debe aparecer tabla de desglose CAPEX, no solo el total.

  **MIN-01 (Status Quo):**
  ```bash
  grep -n "Status Quo\|status_quo\|Sin IAO\|Implementación" evidence/FASE-PENDIENTE-V4COMPLETE/02_PROPUESTA_*.md
  ```
  ✅ Debe aparecer tabla comparativa "Sin IAO vs Con IAO".

  **MIN-02 (ADR evidenciado):**
  ```bash
  grep -n "ADR\|adr\|285.000\|285000" evidence/FASE-PENDIENTE-V4COMPLETE/02_PROPUESTA_*.md
  grep -n "ADR" evidence/FASE-PENDIENTE-V4COMPLETE/02_PROPUESTA_*.md
  ```
  ✅ Debe aparecer ADR regional en propuesta.

  **MIN-03 (Closing pitch):**
  ```bash
  grep -n "Oportunidad\|urgencia\|Siguiente paso\|ROICR" evidence/FASE-PENDIENTE-V4COMPLETE/02_PROPUESTA_*.md
  # También verificar que NO aparece el texto estático viejo
  grep -n "SIGUIENTE PASO" evidence/FASE-PENDIENTE-V4COMPLETE/02_PROPUESTA_*.md
  ```
  ✅ Debe aparecer pitch dinámico con datos financieros.
  ✅ NO debe aparecer "SIGUIENTE PASO" (texto estático eliminado).

  **F5 (ADR checklist):**
  ```bash
  grep -n "ADR\|adr.*Pendiente\|adr.*verificado\|adr.*COP" evidence/FASE-PENDIENTE-V4COMPLETE/02_PROPUESTA_*.md
  ```
  ✅ ADR en coherence checklist debe mostrar valor, no "Pendiente"
  (siempre que eje_cafetero tenga ADR en benchmarks — Fase-2 lo añadió).

  **F7 (Gate discrepancy):**
  ```bash
  # Leer el gate report JSON
  cat evidence/FASE-PENDIENTE-V4COMPLETE/gate_report_*.json | \
      ./venv/Scripts/python.exe -c "
  import sys, json
  data = json.load(sys.stdin)
  for gate in data.get('gates', []):
      if 'financial' in gate.get('gate_name','') or 'tier' in gate.get('gate_name',''):
          print(f\"  {gate['gate_name']}: {gate['status']} — {gate.get('message','')}\")
  "
  ```
  ✅ Ambos gates deben reportar el MISMO tier (debería ser B).

  **Dead code eliminado:**
  Verificación indirecta — el generador no crasheó, así que la eliminación fue limpia.

- [ ] **T4: Informe post-implementación + Estado de fase**

  Completar la siguiente tabla resumen:

  | Fix | Esperado | Encontrado | Status |
  |-----|----------|------------|--------|
  | IMP-03 CAPEX breakdown | Tabla en propuesta | ? | ✅/❌ |
  | MIN-01 Status Quo | Tabla comparativa | ? | ✅/❌ |
  | MIN-02 ADR evidenciado | Valor COP en benchmarks | ? | ✅/❌ |
  | MIN-03 Closing pitch | Pitch dinámico | ? | ✅/❌ |
  | F5 ADR checklist | Valor (no Pendiente) | ? | ✅/❌ |
  | F7 Gate discrepancy | Mismo tier en ambos gates | ? | ✅/❌ |

  **Métricas vs baseline:**
  ```
  | Métrica              | Baseline | Post-fix | Delta |
  |----------------------|----------|----------|-------|
  | Coherence score      | 0.83     | ?        | ?     |
  | Publication Gates    | 9/11     | ?        | ?     |
  | Tier                 | B        | ?        | ?     |
  | Blocking issues      | 0        | ?        | ?     |
  ```

  Marcar T1-T4 como completadas en `06-checklist-implementacion.md`.

### Restricciones

- **NO modificar código** en esta fase — solo ejecutar y verificar
- Evidencia DEBE guardarse inmediatamente (T2) antes de iniciar análisis (T3)
- Si v4complete falla 2 veces, documentar error y cerrar fase como INCOMPLETA
- Máximo 60 iteraciones (R2)

### Criterios de completitud

- [ ] v4complete ejecutado exitosamente
- [ ] Evidencia guardada en `evidence/FASE-PENDIENTE-V4COMPLETE/`
- [ ] Tabla de verificación de fixes completada
- [ ] Métricas vs baseline documentadas
- [ ] Estado actualizado en checklist (PASSED/PARTIAL/FAILED por fix)

### Archivos involucrados

| Archivo | Acción |
|---------|--------|
| `output/v4_complete/*` | Lectura (output generado) |
| `evidence/FASE-PENDIENTE-V4COMPLETE/` | Crear + copiar evidencia |

### Próxima sesión

```
Carga y ejecuta /.opencode/plans/Archives/REFACTOR-PENDIENTE-V4.58.0/05-prompt-inicio-sesion-fase-RELEASE.md
```

Esa fase ejecuta el cascade documental completo (REGISTRY, CHANGELOG, GUIA_TECNICA, sync).
