# FASE-4: Generar Asset B4 Open Graph

**ID**: FASE-4  
**Objetivo**: Crear asset Open Graph Meta Tags para cerrar brecha B4 ($379K/mes expuesto)  
**Dependencias**: FASE-1 COMPLETADA (recomendado), puede ejecutarse independientemente  
**Duración estimada**: 1 hora  
**Skill**: `iah-cli-cross-document-audit`

---

## Contexto

**Hallazgo C3 (CRITICO)**: B4 Open Graph sin cobertura - NO existe asset generado.

**Diagnóstico actual**: Detectó "Sin Meta Tags Sociales (Open Graph)" como brecha B4  
**Propuesta**: NO hay servicio que atienda B4  
**Asset**: 0% cobertura

**Costo expuesto**: $379,755/mes sin protección

**Datos disponibles** (del GBP verificado):
```
nombre: Amazilia Hotel Campestre
rating: 4.5 | reviews: 202
address: Via Pereira a #Entrada 8 Cafelia, CERRITOS, Pereira, Risaralda
phone: +57 310 4019049
```

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |
| FASE-2A/2B/2C | ✅ Completada |
| FASE-3 | ✅ Completada |

---

## Tareas

### Tarea 1: Crear Open Graph Generator
**Objetivo**: Implementar `modules/asset_generation/open_graph_generator.py`

**Datos requeridos**:
- `og:title`: Amazilia Hotel Campestre
- `og:description`: Breve descripción del hotel (usar datos GBP)
- `og:image`: URL de foto del hotel (usar photo[0] del GBP si disponible)
- `og:url`: URL del sitio del hotel
- `og:type`: hotel
- `og:locale`: es_CO
- `og:site_name`: Amazilia Hotel Campestre

**Archivo nuevo**:
- `modules/asset_generation/open_graph_generator.py`

**Criterios de aceptación**:
- [ ] Generator implementado en `modules/asset_generation/`
- [ ] Extensión `.html` o `.php` (para inyectar en WordPress)
- [ ] Contenido: meta tags Open Graph completos

### Tarea 2: Integrar en pipeline v4_asset_orchestrator
**Objetivo**: Incluir Open Graph en generación condicional

**Archivo afectado**:
- `modules/asset_generation/v4_asset_orchestrator.py`
- `modules/asset_generation/asset_catalog.py`

**Criterios de aceptación**:
- [ ] Open Graph aparece en catálogo de assets
- [ ] `is_asset_implemented` = True para B4
- [ ] Gate de publicación incluye Open Graph

### Tarea 3: Generar asset para Amaziliahotel
**Objetivo**: Producir `open_graph_meta/ESTIMATED_open_graph.html`

**Carpeta nueva**:
- `output/v4_complete/amaziliahotel/open_graph_meta/`

**Criterios de aceptación**:
- [ ] Archivo generado con meta tags reales (no placeholders)
- [ ] Datos usados: nombre, rating, reviews, address del GBP
- [ ] Archivo listo para inyectar en WordPress

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_open_graph_generator` | `tests/asset_generation/test_open_graph_generator.py` | Meta tags completos |
| `test_open_graph_in_catalog` | `tests/asset_generation/test_asset_catalog.py` | is_asset_implemented=True |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_open_graph_generator.py tests/asset_generation/test_asset_catalog.py -v
```

---

## Restricciones

- NO generar placeholder - SOLO datos verificados del GBP
- Usar formato inyectable en WordPress (header.php o plugin SEO)

---

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-4 \
    --desc "Asset B4 Open Graph generado - cierra brecha $379K/mes" \
    --archivos-nuevos "modules/asset_generation/open_graph_generator.py,output/v4_complete/amaziliahotel/open_graph_meta/ESTIMATED_open_graph.html" \
    --archivos-mod "modules/asset_generation/v4_asset_orchestrator.py,modules/asset_generation/asset_catalog.py" \
    --tests "2" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [x] **Generator implementado**: open_graph_generator.py existe (341 líneas, clase OpenGraphGenerator)
- [x] **En pipeline**: Integrado via ConditionalGenerator._generate_content() L482 handler
- [x] **En catálogo**: asset_catalog.py L333: status=AssetStatus.IMPLEMENTED
- [x] **Asset generado**: open_graph_meta/ESTIMATED_open_graph.html (2112 bytes, datos reales GBP)
- [x] **Tests pasan**: 9/9 tests pasan
- [x] **`dependencias-fases.md` actualizado**: FASE-4 marcada ✅
