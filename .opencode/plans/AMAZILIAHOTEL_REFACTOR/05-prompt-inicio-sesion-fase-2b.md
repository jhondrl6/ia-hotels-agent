# FASE-2B: Regenerar monthly_report con datos reales

**ID**: FASE-2B  
**Objetivo**: Regenerar `monthly_report/ESTIMATED_*.csv` con datos reales del BookingScraper  
**Dependencias**: FASE-1 (BookingScraper real) COMPLETADA  
**Duración estimada**: 30 minutos  
**Skill**: `iah-cli-cross-document-audit`

---

## Contexto

**Hallazgo H6**: monthly_report plantilla vacia (46 blanks) porque `has_real_data=False`.

**Asset actual**: `output/v4_complete/amaziliahotel/monthly_report/ESTIMATED_monthly_report.csv`
- `has_real_data=False` → 46 campos vacíos

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |
| FASE-2A | PENDIENTE |
| FASE-2C | PENDIENTE |

---

## Tareas

### Tarea 1: Regenerar monthly_report con datos reales
**Objetivo**: Generar reporte real usando `modules/asset_generation/report_generator.py`

**Archivos afectados**:
- `modules/asset_generation/report_generator.py` (~línea 50)
- `output/v4_complete/amaziliahotel/monthly_report/`

**Criterios de aceptación**:
- [ ] Reporte tiene `has_real_data=True`
- [ ] Campos llenos con datos verificados (reviews, rating, etc.)
- [ ] No más 46 blanks

### Tarea 2: Verificar字段 requeridas
**Objetivo**: Asegurar que el reporte tiene todos los campos financieros y operativos

**Criterios de aceptación**:
- [ ] `total_reviews` = 202 (del GBP)
- [ ] `average_rating` = 4.5 (del GBP)
- [ ] `total_photos` = 10 (del GBP)
- [ ] `occupancy_metrics` lleno (no placeholder)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_monthly_report_has_real_data` | `tests/asset_generation/test_report_generator.py` | `has_real_data=True` |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_report_generator.py -v
```

---

## Restricciones

- Mantener formato CSV compatible con análisis financiero
- No inventar datos - solo usar datos verificados del GBP

---

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2B \
    --desc "monthly_report regenerado con datos reales del GBP" \
    --archivos-mod "modules/asset_generation/report_generator.py" \
    --archivos-nuevos "output/v4_complete/amaziliahotel/monthly_report/ESTIMATED_monthly_report.csv" \
    --tests "1" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **has_real_data=True**: Verificado en CSV
- [ ] **0 blanks**: No más 46 campos vacíos
- [ ] **Datos del GBP**: reviews=202, rating=4.5, photos=10
- [ ] **Tests pasan**: test_report_generator.py pasa
- [ ] **`dependencias-fases.md` actualizado**: FASE-2B marcada ✅
