---
description: FASE-LLMSTXT-FIX — Fix llms.txt generator para usar geo_enriched
version: 1.0.0
---

# FASE-LLMSTXT-FIX: Fix llms.txt Generator — Fallback a geo_enriched

**ID**: FASE-LLMSTXT-FIX  
**Objetivo**: Que el generador de llms.txt use datos de geo_enriched/ como fallback y no genere placeholders vacíos  
**Dependencias**: FASE-GEO-BRIDGE (usa el bridge para enrichment)  
**Duración estimada**: 1-2 horas  
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Problema (D3 del AUDIT)

```
D3: llms.txt con placeholders vacíos — IMPACTO ALTO

El archivo llms_txt/ESTIMATED_llms_*.txt generado contiene:
  # Hotel  (debería ser "Amaziliahotel")
  > Hotel es un hotel boutique en , Eje Cafetero, Colombia.
    (nombre vacío antes de la coma)
  - [Homepage](): Main hotel website  (URL vacía)
  - Phone: N/A, Email: N/A, Address: N/A

Pero geo_enriched/llms.txt tiene datos reales:
  # Amaziliahotel
  **URL:** https://amaziliahotel.com/
  **Servicios:** Hospedaje, restaurante, WiFi, recepción 24 horas.
```

### Raíz del Problema

`LLMSTXTGenerator.generate()` recibe `hotel_data` del audit, que tiene datos limitados:

```python
# llmstxt_generator.py líneas 36-43
name = hotel_data.get("name", "Hotel")  # "Hotel" por defecto
url = hotel_data.get("website", "")      # "" por defecto
# ...
usp = hotel_data.get("usp", f"{name} es un hotel boutique en {city}, {region}, Colombia.")
# Si city está vacío → "Hotel es un hotel boutique en , Eje Cafetero, Colombia."
```

El generador NO tiene acceso a `geo_enriched/llms.txt` que ya fue generado con datos enriquecidos.

### Solución: Fallback chain

```
1. Intentar usar geo_enriched/llms.txt si existe
2. Si no existe, usar hotel_data enriquecido del assessment
3. Si hotel_data también está vacío, generar con marcadores PENDIENTE_ONBOARDING
4. Nunca generar con placeholders engañosos (\"Hotel\", \"\", \"N/A\")
```

### Relación con FASE-GEO-BRIDGE

**IMPORTANTE**: Esta fase NO duplica la lógica del bridge. Son dos capas distintas:

- **FASE-GEO-BRIDGE** (capa post-generación): Intercepta assets DESPUÉS de generarse y los enriquece desde geo_enriched/ si confidence < 0.7. Es un fallback genérico para TODOS los assets.
- **FASE-LLMSTXT-FIX** (capa del generador): Modifica el LLMSTXTGenerator directamente para que use geo_enriched/llms.txt como fuente primaria ANTES de generar. Además agrega validación de datos mínimos.

**Flujo combinado**:
```
LLMSTXTGenerator.generate()  ← FASE-LLMSTXT-FIX: lee geo_enriched/llms.txt si existe
         │
         ▼
  [asset generado]
         │
         ▼
  geo_enriched_bridge()       ← FASE-GEO-BRIDGE: fallback si confidence sigue < 0.7
```

Si LLMSTXT-FIX funciona bien, el bridge NO necesitara intervenir en llms_txt (confidence ya sera >= 0.7). El bridge es la red de seguridad, no el mecanismo primario.

---

## Tareas

### Tarea 1: Modificar LLMSTXTGenerator para aceptar fallback path

**Ubicación**: `modules/asset_generation/llmstxt_generator.py`

**Cambios**:

1. Agregar parámetro `geo_enriched_path: Optional[Path] = None` al método `generate()`
2. Si `geo_enriched_path` existe y contiene `llms.txt`, leer y retornar ese contenido
3. Si no, proceder con generación normal pero validar que los datos mínimos existan

**Código a agregar/modificar**:

```python
from pathlib import Path
from typing import Dict, List, Any, Optional

class LLMSTXTGenerator:
    """Generator for llms.txt files following the llmstxt.org standard."""
    
    def generate(
        self, 
        hotel_data: Dict[str, Any],
        geo_enriched_path: Optional[Path] = None
    ) -> str:
        """
        Generate llms.txt content for a hotel website.
        
        Args:
            hotel_data: Dictionary with hotel information.
            geo_enriched_path: Optional path to geo_enriched directory.
                              If llms.txt exists there, use it directly.
        
        Returns:
            llms.txt content as string.
        """
        # ═══════════════════════════════════════════════════════════════
        # FASE-LLMSTXT-FIX: Fallback a geo_enriched
        # ═══════════════════════════════════════════════════════════════
        if geo_enriched_path:
            geo_llms_path = Path(geo_enriched_path) / "llms.txt"
            if geo_llms_path.exists():
                content = geo_llms_path.read_text(encoding="utf-8")
                logger.info(f"[LLMSTXTGenerator] Using geo_enriched/llms.txt")
                return content
        # ═══════════════════════════════════════════════════════════════
        
        # Validación: si datos mínimos faltan, marcar como PENDIENTE
        name = hotel_data.get("name", "")
        url = hotel_data.get("website", "")
        
        if not name or name == "Hotel":
            # Advertir pero no bloquear
            logger.warning("[LLMSTXTGenerator] Hotel name is generic, marking as PENDING_ONBOARDING")
        
        # ... resto del generate() ...
```

---

### Tarea 2: Actualizar调用 en ConditionalGenerator

**Ubicación**: `modules/asset_generation/conditional_generator.py`

**Buscar** dónde se llama a `LLMSTXTGenerator.generate()` y agregar el path de geo_enriched:

```python
# En el método que genera llms_txt
llms_generator = get_llmstxt_generator()

# Pasar geo_enriched path si existe
geo_enriched_path = output_dir / hotel_id / "geo_enriched"

result = llms_generator.generate(
    validated_data.get("hotel_data", {}),
    geo_enriched_path=geo_enriched_path  # NUEVO
)
```

---

### Tarea 3: Verificar que geo_enriched/llms.txt tiene formato compatible

**Contexto**: El geo_enriched/llms.txt tiene formato diferente al que espera el delivery:

**geo_enriched/llms.txt (formato actual)**:
```
# Amaziliahotel
**URL:** https://amaziliahotel.com/
**Servicios:** Hospedaje, restaurante, WiFi, recepción 24 horas.
```

**llms.txt estándar (llmstxt.org)**:
```
# Amaziliahotel

> Amaziliahotel es un hotel boutique en Salento, Eje Cafetero, Colombia.

## Important Pages

- [Homepage](https://amaziliahotel.com/): Main hotel website
- [Rooms](https://amaziliahotel.com/habitaciones): Room types and rates
```

**Decisión**: Usar geo_enriched/llms.txt TAL CUAL es aceptable porque:
- Tiene los datos reales (nombre, URL, servicios)
- El formato es legible para LLMs
- Si el formato difiere, el enrichment bridge lo procesará

**Pero**: Si geo_enriched/llms.txt tiene formato propietario (con `**URL:**` en lugar de `[Homepage]()`), debemos convertirlo o usar solo los datos.

**Acción requerida**: Leer `modules/geo_enrichment/llms_txt_generator.py` para entender el formato de salida.

---

### Tarea 4: Tests

**Archivo**: `tests/asset_generation/test_llmstxt_generator.py` (o agregar a existente)

**Casos**:
1. `test_generator_uses_geo_enriched_fallback` — si geo_enriched_path dado con llms.txt, usa ese contenido
2. `test_generator_skips_geo_enriched_if_file_missing` — si path dado pero archivo no existe, usa generación normal
3. `test_generator_warns_on_generic_name` — si name="Hotel", genera warning log
4. `test_generator_produces_valid_llms_txt_format` — output sigue el estándar llmstxt.org

---

## Restricciones

- NO modificar el formato estándar de llms.txt del delivery
- Si geo_enriched/llms.txt se usa tal cual, debe ser legible y útil
- Mantener backward compatibility: si no hay geo_enriched/, generar normal
- Si datos mínimos faltan, no generar con información engañosa

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_generator_uses_geo_enriched_fallback` | `tests/asset_generation/test_llmstxt_generator.py` | PASA |
| `test_generator_skips_geo_enriched_if_file_missing` | `tests/asset_generation/test_llmstxt_generator.py` | PASA |
| `test_generator_warns_on_generic_name` | `tests/asset_generation/test_llmstxt_generator.py` | PASA |
| `test_generator_produces_valid_llms_txt_format` | `tests/asset_generation/test_llmstxt_generator.py` | PASA |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_llmstxt_generator.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: Los 4 tests del generador ejecutan exitosamente
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: FASE-LLMSTXT-FIX marcada como ✅ Completada
- [ ] **Fallback funciona**: geo_enriched/llms.txt se usa cuando existe
- [ ] **No hay regresión**: Generación normal sigue funcionando

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-LLMSTXT-FIX como ✅ Completada con fecha
2. **`06-checklist-implementacion.md`**: Marcar Tareas 1-4 como completadas
3. **`09-documentacion-post-proyecto.md`**:
   - Sección E: `modules/asset_generation/llmstxt_generator.py` modificado
   - Sección D: Métrica "llms_txt placeholders: 1 → 0"
