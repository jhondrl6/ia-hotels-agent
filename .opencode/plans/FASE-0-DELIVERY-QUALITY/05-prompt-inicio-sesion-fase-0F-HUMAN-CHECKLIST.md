# FASE-0F: Checklist Humano Reducido

> **Fase:** 0F  
> **Tipo:** Código + tests  
> **Comando largo:** No  
> **Dependencias:** 0E  
> **Máximo iteraciones:** 60  
> **Restricción:** TDD obligatorio. No ejecutar v4complete.

---

## Contexto

Lee primero:
1. `modules/quality_gates/delivery_quality_report.py` (estructura del reporte)
2. Este prompt

---

## Tareas

### Tarea 1: Implementar HumanChecklistGenerator

Crear `modules/quality_gates/human_checklist_generator.py`:

```python
class HumanChecklistGenerator:
    def generate(self, report: DeliveryQualityReport) -> str  # markdown
    def save(self, checklist: str, path: Path)
```

Reglas:
- Derivar desde `delivery_quality_report.json`.
- <= 10 items.
- Items: datos reales pendientes, conflictos, assets estimados relevantes, decisión comercial, tono final.
- El humano revisa excepciones, no reconstruye coherencia.

### Tarea 2: TDD — Tests

Crear `tests/quality_gates/test_human_checklist_generator.py`:

**RED:**
- `test_checklist_has_at_most_10_items()`
- `test_checklist_includes_exceptions_only()`

**GREEN:** Implementar.

**REFACTOR.**

### Tarea 3: Integrar en main.py

Modificar `main.py`:
- Después de generar `delivery_quality_report.json`, generar `human_checklist.md`.
- Guardar en `output/v4_complete/<hotel>/v4_audit/human_checklist.md`.

### Tarea 4: Regresión focalizada

```bash
pytest tests/quality_gates/test_human_checklist_generator.py -v
pytest tests/ -v -k "checklist or human" --timeout=60
```

---

## Criterios de Completitud

- [ ] `modules/quality_gates/human_checklist_generator.py` existe
- [ ] `tests/quality_gates/test_human_checklist_generator.py` existe, >= 2 tests, todos PASS
- [ ] `main.py` escribe `human_checklist.md`
- [ ] Checklist generado desde fixture tiene <= 10 items

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-0F-HUMAN-CHECKLIST \
    --desc "Checklist humano reducido <= 10 items" \
    --archivos-nuevos "modules/quality_gates/human_checklist_generator.py,tests/quality_gates/test_human_checklist_generator.py" \
    --archivos-mod "main.py" \
    --tests "2" \
    --check-manual-docs
```

Actualizar `06-checklist-implementacion.md`: marcar 0F-1..0F-4 como ✅.
