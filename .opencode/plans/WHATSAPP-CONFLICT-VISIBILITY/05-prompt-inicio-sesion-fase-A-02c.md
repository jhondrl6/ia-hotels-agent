# FASE-A-02c: Ajuste de Impacto y Phrasing en Pain Narratives

**ID**: FASE-A-02c  
**Objetivo**: Ajustar el `impacto` y `detalle` de `whatsapp_conflict` en el narratives dict para que refleje el impacto de negocio real — no subestimado.  
**Dependencias**: FASE-A-02b (implementación de nota de contexto)  
**Duración estimada**: 30-45 min  
**Skill**: systematic-debugging

---

## Contexto

**Basado en hallazgos de FASE-A-02a y FASE-A-02b**:

El `impacto` actual de `whatsapp_conflict` en `pain_narratives` es `0.10` (L 2605 de v4_diagnostic_generator.py) — el más bajo de todos los pains. Esto refuerza la percepción de que es un problema menor cuando en realidad es un problema de **reservas perdidas sin conocimiento del hotelero**.

La regla establecida en FASE-A-01c (L 115-121): NO tratarlo como BRECHA porque no tenemos asset para resolverlo operativamente. PERO el impacto narrativo debe reflejar la gravedad real.

**Cambio requerido**:
- `impacto`: subir de `0.10` a `0.20` (mismo nivel que `no_whatsapp_visible`)
- `detalle`: phrasing de impacto de negocio que contextualice la confusión del cliente

### Base Técnica Disponible
- `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 2603-2607: `pain_narratives['whatsapp_conflict']`)
- `modules/financial_engine/opportunity_scorer.py` — scores de pain
- `evidence/FASE-A-02a/hallazgos_02a.md` — hallazgos de investigación

---

## Tareas

### Tarea 1: Ajustar pain_narratives en v4_diagnostic_generator.py Y regional_benchmarks.yaml
**Objetivo**: Subir el impacto y mejorar el phrasing de detalle para whatsapp_conflict

**ATENCIÓN (G3)**: `pain_narratives` se carga desde `config/regional_benchmarks.yaml` (4 regiones, L21/84/116/148). El `.get('whatsapp_conflict', 0.10)` en Python es solo el DEFAULT. Hay que modificar AMBAS fuentes.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (línea 2605: cambiar default de `.get()`)
- `config/regional_benchmarks.yaml` (4 regiones: L21, L84, L116, L148 — cambiar `whatsapp_conflict: 0.10` → `0.20`)

**Criterios de aceptación**:
- [ ] `config/regional_benchmarks.yaml`: `whatsapp_conflict: 0.10` → `0.20` en las 4 regiones (L21, L84, L116, L148)
- [ ] `v4_diagnostic_generator.py` L2605: `.get('whatsapp_conflict', 0.10)` → `.get('whatsapp_conflict', 0.20)`
- [ ] `detalle`: mantener el actual o ajustar ligeramente (el actual ya es bueno: "WhatsApp diferente en web vs Google. Cliente confundido = reserva perdida.")
- [ ] `nombre`: puede mantener "Datos Inconsistentes" o ajustar a "Conflicto de WhatsApp (Reservas Perdidas)" para más claridad

**Nuevo detalle propuesto**:
```
'WhatsApp diferente en web vs Google. Cliente confundido = reserva perdida sin que usted lo sepa.'
```

### Tarea 2: Verificar alignment con opportunity_scorer
**Objetivo**: Confirmar que el cambio de impacto no rompe alignment con scores del opportunity_scorer

**Archivos afectados**:
- `modules/financial_engine/opportunity_scorer.py` (líneas 145, 168: scores de whatsapp_conflict)

**Criterios de aceptación**:
- [ ] Verificar que scores en opportunity_scorer no necesitan ajuste
- [ ] Documentar si hay misalignment o está bien

### Tarea 3: Verificar que la nota contexto de FASE-A-02b sigue siendo compatible
**Objetivo**: Confirmar que el phrasing de la nota negocio en `_build_whatsapp_conflict_note()` es consistente con el nuevo narratives

**Criterios de aceptación**:
- [ ] La nota de contexto NO necesita cambio (phrasing ya correcto de L 127 FASE-A-01c)
- [ ] Narratives y nota contexto hablan del mismo problema

---

## Tests Obligatorios

No hay tests nuevos para esta fase — es cambio de valores hardcoded en dict.

**Comando de validación**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar, ejecutar en orden:

1. **`dependencias-fases.md`**: Marcar FASE-A-02c como ✅ Completada
2. **`README.md` del plan**: Marcar fase
3. **`09-documentacion-post-proyecto.md`**:
   - Sección A: N/A
   - Sección B: "Impacto whatsapp_conflict ajustado 0.10→0.20, phrasing mejorado"
   - Sección D: +0 tests
   - Sección E: `v4_diagnostic_generator.py`
4. **Ejecutar validaciones** y verificar no hay regresiones

---

## Criterios de Completitud (CHECKLIST)

- [ ] `impacto` de `whatsapp_conflict` en `pain_narratives` cambiado a `0.20`
- [ ] `detalle` actualizado con phrasing de impacto de negocio
- [ ] Alignment con `opportunity_scorer` verificado (no requiere cambio)
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` sin errores críticos
- [ ] `dependencias-fases.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado

---

## Restricciones

- NO cambiar scores en `opportunity_scorer.py` a menos que haya misalignment claro
- NO alterar otros pains — solo whatsapp_conflict
- NO cambiar asset generation — la lógica de FASE-A-02b ya maneja la nota condicional

---

*Fase: WHATSAPP-CONFLICT-VISIBILITY / FASE-A-02c*  
*Depende de: FASE-A-02b*  
*Creado: 2026-05-24*