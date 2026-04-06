---
description: FASE V6-4 - Verificar y corregir alineación Assets ↔ V6
version: 1.0.0
fase: V6-4
---

# FASE V6-4: Alineación Assets ↔ V6

## Contexto

Verificar que los assets generados son coherentes con lo que V6 promete en la propuesta comercial.

**Mapeo V6 → Asset esperado:**

| V6 Promete | Asset | Status Actual |
|------------|-------|-------------|
| Google Maps Optimizado (GEO) | `geo_playbook` | ✅ IMPLEMENTED |
| Visibilidad en ChatGPT (IAO) | `llms_txt` + `hotel_schema` | ✅ IMPLEMENTED |
| Búsqueda por Voz (AEO) | `voice_assistant_guide` | ✅ IMPLEMENTED |
| SEO Local | `optimization_guide` | ✅ IMPLEMENTED |
| Botón WhatsApp | `whatsapp_button` | ✅ IMPLEMENTED |
| Datos Estructurados | `hotel_schema` + `org_schema` | ✅ IMPLEMENTED |
| Informe Mensual | `financial_projection` | ✅ IMPLEMENTED |
| ROI 24X | (cálculo, no asset) | ✅ Viene de `financial_scenarios` |

**Dependencia:** FASE V6-3 (impact_cop dinámico)

## Tareas

### Tarea 1: Verificar Asset Catalog

Ejecutar para ver estado actual de assets:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -c "
from modules.asset_generation.asset_catalog import ASSET_CATALOG, get_implemented_assets
for asset_type, entry in ASSET_CATALOG.items():
    print(f'{asset_type}: {entry.status.value}')"
```

### Tarea 2: Verificar promised_by en ASSET_CATALOG

Cada asset debe tener `promised_by` que mapea a los problemas que resuelve.

### Tarea 3: Verificar coherencia pain_solution_mapper → ASSET_CATALOG

El `pain_solution_mapper.PAIN_SOLUTION_MAP` mapea problemas a assets. Verificar que cada asset prometido en V6 tenga对应 mapping.

### Tarea 4: Verificar que `voice_assistant_guide` existe y está en IMPLEMENTED

Según CHANGELOG v4.9.0, AEO Voice fue implementado con:
- `voice_assistant_guide` en asset_catalog
- 3 blueprints: Google Assistant, Apple Business Connect, Alexa Skill

Verificar que `modules/delivery/generators/voice_guide.py` existe y funciona.

## Criterios de Completitud

- [ ] Todos los assets de V6 están IMPLEMENTED en ASSET_CATALOG
- [ ] `voice_assistant_guide` tiene `promised_by` correctamente configurado
- [ ] No hay gaps entre lo que V6 promete y lo que los assets entregan
- [ ] Tests pasan

## Post-Ejecución

1. Marcar checklist como completado
2. NO ejecutar `log_phase_completion.py` aún - esperar a FASE V6-5

## Archivos a Verificar

| Archivo | Verificar |
|---------|-----------|
| `modules/asset_generation/asset_catalog.py` | Status de todos los assets V6 |
| `modules/commercial_documents/pain_solution_mapper.py` | Mapping problema → asset |
| `modules/delivery/generators/voice_guide.py` | Existe y funcional |

## Tests a Ejecutar

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -k "catalog or asset" --tb=short -q
```
