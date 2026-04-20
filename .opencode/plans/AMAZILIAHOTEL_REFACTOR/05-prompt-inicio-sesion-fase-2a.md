# FASE-2A: Regenerar hotel_schema con datos reales

**ID**: FASE-2A  
**Objetivo**: Regenerar `hotel_schema/ESTIMATED_*.json` con datos reales del BookingScraper  
**Dependencias**: FASE-1 (BookingScraper real) COMPLETADA  
**Duración estimada**: 30 minutos  
**Skill**: `iah-cli-cross-document-audit`

---

## Contexto

**Hallazgo H2**: hotel_schema es genérico porque `BookingScraper.scrape()` retornaba vacío.

**Datos verificados disponibles** (del GBP):
```
nombre: Amazilia Hotel Campestre
rating: 4.5 | reviews: 202 | photos: 10
phone: 310 4019049
address: mts a la derecha, Via Pereira a #Entrada 8 Cafelia, 600, CERRITOS, Pereira, Risaralda
geo_score: 62/100
```

**Asset actual**: `output/v4_complete/amaziliahotel/hotel_schema/ESTIMATED_hotel_schema.json`
- PARCIAL - existe pero generico (address=None, tel=None, geo=None)

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |
| FASE-2B | PENDIENTE |
| FASE-2C | PENDIENTE |

---

## Tareas

### Tarea 1: Regenerar hotel_schema con datos reales
**Objetivo**: Generar schema real usando `modules/asset_generation/schema_generator.py`

**Archivos afectados**:
- `modules/asset_generation/schema_generator.py`
- `output/v4_complete/amaziliahotel/hotel_schema/`

**Criterios de aceptación**:
- [ ] Schema contiene `name`: "Amazilia Hotel Campestre"
- [ ] Schema contiene `telephone`: "+57 310 4019049"
- [ ] Schema contiene `address` completo (no None)
- [ ] Schema contiene `geo` con latitud/longitud (no None)
- [ ] Schema contiene `aggregateRating`: 4.5, 202 reviews

### Tarea 2: Eliminar duplicado en geo_enriched
**Objetivo**: Resolver H4 (duplicación hotel_schema)

**Archivo duplicado**: `geo_enriched/hotel_schema_rich.json` (mismo propósito que hotel_schema/)

**Criterios de aceptación**:
- [ ] Unificar en `hotel_schema/` como fuente única
- [ ] `geo_enriched/hotel_schema_rich.json` eliminado o marcado deprecated

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_hotel_schema_has_real_data` | `tests/asset_generation/test_schema_generator.py` | address, tel, geo no None |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_schema_generator.py -v
```

---

## Restricciones

- NO modificar `geo_enriched/hotel_schema_rich.json` sin antes eliminarlo/marcarlo
- Mantener formato JSON-LD válido para Schema.org

---

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2A \
    --desc "hotel_schema regenerado con datos reales - elimino duplicado geo_enriched" \
    --archivos-mod "modules/asset_generation/schema_generator.py" \
    --archivos-nuevos "output/v4_complete/amaziliahotel/hotel_schema/ESTIMATED_hotel_schema.json" \
    --tests "1" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Schema con datos reales**: address, tel, geo no None
- [ ] **Duplicado eliminado**: `geo_enriched/hotel_schema_rich.json` removido
- [ ] **Tests pasan**: test_schema_generator.py pasa
- [ ] **`dependencias-fases.md` actualizado**: FASE-2A marcada ✅
