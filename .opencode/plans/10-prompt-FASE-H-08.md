# Prompt: FASE-H-08 - Certificación E2E (End-to-End)

## Proyecto: iah-cli | hotelvisperas.com
## Fecha: 2026-03-26

---

## Pre-requisito

**FASE-H-06 y FASE-H-07 DEBEN estar completadas.**

---

## Contexto

Esta es la **fase de certificación E2E obligatoria**. El objetivo es ejecutar el flujo completo V4COMPLETE contra el sitio real https://www.hotelvisperas.com/es y certificar que todas las desconexiones han sido resueltas.

**Esta es la fase FINAL.** Si pasa, el proyecto se considera COMPLETADO y CERTIFICADO.

---

## TAREA PRINCIPAL: Ejecutar V4COMPLETE E2E

### Paso 1: Ejecutar V4COMPLETE sobre hotelvisperas.com

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es --nombre "Hotel Vísperas" --debug 2>&1
```

**ESTA EJECUCIÓN ES OBLIGATORIA.** No se puede certificar sin ejecutar. Guardar el output completo.

### Paso 2: Verificar Coherence Score

El coherence score debe ser ≥ 0.8:

```
Coherence Score: 0.XX
Status: READY_FOR_PUBLICATION ✅
```

### Paso 3: Verificar NO hay Desconexiones

Ejecutar el coherence_validator contra el delivery:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -c "
from modules.commercial_documents.coherence_validator import CoherenceValidator
import json

validator = CoherenceValidator()

# Cargar diagnostic y propuesta generados
with open('output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260326_*.md', encoding='utf-8') as f:
    diagnostic = f.read()

with open('output/v4_complete/02_PROPUESTA_COMERCIAL_20260326_*.md', encoding='utf-8') as f:
    proposal = f.read()

# Cargar assets generados
import glob
assets_dir = 'output/v4_complete/deliveries/'
asset_files = glob.glob(assets_dir + 'hotel_vísperas_*.zip')
if asset_files:
    import zipfile
    with zipfile.ZipFile(asset_files[0]) as z:
        assets = {n: z.read(n).decode('utf-8', errors='ignore') for n in z.namelist() if n.endswith('.md')}

result = validator.validate(diagnostic, proposal, assets)
print(f'Desconexiones: {result.disconnections}')
print(f'Coherence Score: {result.coherence_score}')
print(f'Status: {result.status}')
"
```

**Esperado:** 0 desconexiones, score ≥ 0.8

---

## Verificaciones Específicas

### 1. whatsapp_button Generado

```bash
unzip -l output/v4_complete/deliveries/hotel_vísperas_*.zip | grep whatsapp
```

**Esperado:** `ASSETS/whatsapp_button/ESTIMATED_...` (NO en `failed_assets/`)

### 2. optimization_guide Pasa Validación

Verificar que `optimization_guide` tiene status = VALID o solo WARNING (no BLOCKED).

### 3. ROI Corregido

En la propuesta comercial generada, verificar que:
- El ROI muestra "~2.6X" o "2.6X", NO "24.0XX"
- El template usa `${roi_6m}X en 6 meses`

```bash
grep -A1 "ROI Proyectado" output/v4_complete/02_PROPUESTA_COMERCIAL_20260326_*.md
```

---

## Checklist de Certificación E2E

| Verificación | Criterio | Estado |
|-------------|----------|--------|
| V4COMPLETE ejecuta sin errores fatales | 0 errores críticos | ___ |
| Coherence Score | ≥ 0.8 | ___ |
| whatsapp_button | Generado, no BLOCKED | ___ |
| optimization_guide | Pasa validación | ___ |
| ROI | ~2.6X (no "24.0XX") | ___ |
| Desconexiones restantes | 0 | ___ |
| Status | READY_FOR_PUBLICATION | ___ |

---

## Post-Ejecución

### 1. Actualizar REGISTRY.md

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-H-08 \
    --desc "E2E CERTIFICATION PASSED - 0 desconexiones" \
    --coherence 0.85 \
    --check-manual-docs
```

### 2. Documentación Incremental

Agregar a `09-documentacion-post-proyecto-GAPS-V4COMPLETE.md`:
- Sección FASE-H-08 completa
- Output de la ejecución E2E
- Métricas finales
- **Estado del proyecto: COMPLETADO Y CERTIFICADO ✅**

### 3. Checklist Final

- [ ] V4COMPLETE E2E ejecutado contra hotelvisperas.com
- [ ] REGISTRY.md actualizado
- [ ] Documentación post-proyecto actualizada
- [ ] Proyecto COMPLETADO Y CERTIFICADO ✅

---

## Criterios de Completitud

- [ ] V4COMPLETE E2E ejecuta sin errores fatales
- [ ] Coherence Score ≥ 0.8
- [ ] whatsapp_button generado (no BLOCKED)
- [ ] optimization_guide pasa validación
- [ ] ROI corregido (~2.6X, no "24.0XX")
- [ ] 0 desconexiones
- [ ] Status: READY_FOR_PUBLICATION
- [ ] REGISTRY.md actualizado
- [ ] **Proyecto COMPLETADO Y CERTIFICADO E2E ✅**

---

## Nota Importante

Si alguna verificación falla, volver a la fase correspondiente (H-06 o H-07) para corregir.

**Esta es la fase final.** Si pasa, el proyecto está CERTIFICADO E2E y puede ser entregado.

---

*Prompt creado: 2026-03-26*
*Depende de: FASE-H-06, FASE-H-07*
