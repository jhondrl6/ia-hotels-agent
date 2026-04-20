# FASE-2C: Regenerar optimization_guide con datos de entrada corregidos

**ID**: FASE-2C  
**Objetivo**: Regenerar `optimization_guide/ESTIMATED_*.md` corrigiendo contradicción interna  
**Dependencias**: FASE-1 (BookingScraper real) COMPLETADA  
**Duración estimada**: 30 minutos  
**Skill**: `iah-cli-cross-document-audit`

---

## Contexto

**Hallazgo H5**: optimization_guide contradiccion title tag - el diagnostico dice "detectado" y "no detectado" simultáneamente.

**Asset actual**: `output/v4_complete/amaziliahotel/optimization_guide/ESTIMATED_optimization_guide.md`
- Contradicción interna: title tag detectado Y no detectado

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |
| FASE-2A | PENDIENTE |
| FASE-2B | PENDIENTE |

---

## Tareas

### Tarea 1: Diagnosticar la contradiccion
**Objetivo**: Entender por qué el generador produce contradicciones

**Archivos afectados**:
- `modules/asset_generation/optimization_generator.py` (~líneas 80-90, función `_analyze_metadata()`)

**Criterios de aceptación**:
- [ ] Identificar cuál de las dos afirmaciones es correcta
- [ ] Documentar la causa de la contradicción (datos de entrada vs. lógica del generador)

### Tarea 2: Corregir generador y regenerar asset
**Objetivo**: Eliminar la contradicción regenerando con datos reales

**Criterios de aceptación**:
- [ ] optimization_guide NO tiene contradicciones internas
- [ ] Title tag: SOLO una evaluación (detectado O no detectado, no ambos)
- [ ] Meta description: coherente con el estado real del sitio

### Tarea 3: Resolver placeholder "en  en"
**Objetivo**: Eliminar texto corrupto en el asset

**Criterio de aceptación**:
- [ ] No existe "en  en" en el contenido

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_optimization_guide_no_contradiction` | `tests/asset_generation/test_optimization_generator.py` | Sin contradicciones internas |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_optimization_generator.py -v
grep -c "en  en" output/v4_complete/amaziliahotel/optimization_guide/ESTIMATED_optimization_guide.md  # debe ser 0
```

---

## Restricciones

- Solo usar datos verificados del GBP/scraper
- NO inferir datos que no se pueden verificar

---

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2C \
    --desc "optimization_guide regenerado - eliminada contradiccion title tag" \
    --archivos-mod "modules/asset_generation/optimization_generator.py" \
    --archivos-nuevos "output/v4_complete/amaziliahotel/optimization_guide/ESTIMATED_optimization_guide.md" \
    --tests "1" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Sin contradicciones**: Title tag solo una evaluación
- [ ] **Sin "en  en"**: placeholder corrupto eliminado
- [ ] **Tests pasan**: test_optimization_generator.py pasa
- [ ] **`dependencias-fases.md` actualizado**: FASE-2C marcada ✅
