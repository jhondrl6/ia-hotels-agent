# FASE-5: Decisiones de Producto + Quality Gates

**ID**: FASE-5  
**Objetivo**: Ejecutar decisiones de producto sobre assets sin brecha y validar quality gates  
**Dependencias**: FASE-1, FASE-3 COMPLETADAS  
**Duración estimada**: 1.5 horas  
**Skill**: `iah-cli-plan-reality-check`

---

## Decisiones Tomadas (Pre-FASE-5)

### D1: WhatsApp (H7) -- ELIMINAR

**Verificacion contra realidad**: El hotel Amazilia Hotel Campestre **YA TIENE** boton de WhatsApp implementado en su web. El numero verificado (573104019049 = GBP phone 310 4019049) confirma que el canal existe.

**Por que ELIMINAR**:
1. La propuesta comercial (linea 29) dice "No hay boton de WhatsApp" -- esto es **FALSO**
2. Vender un servicio que el cliente ya tiene destruye la credibilidad de TODA la propuesta
3. El asset_catalog.py tiene `promised_by=["no_whatsapp_visible", "whatsapp_conflict", "always"]` -- el tag `"always"` fuerza generacion sin importar si el hotel ya tiene WhatsApp. Esto es un **bug sistemico** que afecta a TODOS los clientes.
4. No se puede "reclasificar como enhancement" porque el feature YA EXISTE en el sitio del hotel

**Acciones en FASE-5**:
- Eliminar asset whatsapp_button del output de Amaziliahotel
- Corregir bug sistemico: cambiar `promised_by` de `["no_whatsapp_visible", "whatsapp_conflict", "always"]` a `["no_whatsapp_visible", "whatsapp_conflict"]`
- El asset solo debe generarse cuando `site_presence_checker` detecta que NO hay WhatsApp visible

### D2: Voice Assistant (H8) -- ELIMINAR de pipeline automatico

**Verificacion contra realidad**: El diagnostico muestra AEO score 0/100, pero esto se refiere a visibilidad en busqueda por voz, NO a necesitar un "voice assistant guide". El asset contiene 3 archivos genericos (alexa_skill_blueprint.md, apple_business_connect_guide.md, google_assistant_checklist.md) que no resuelven ninguna brecha real.

**Por que ELIMINAR de pipeline automatico**:
1. No hay brecha de voz en el diagnostico B1-B4
2. Un hotel Tier C en Cerritos, Risaralda no va a crear una Alexa Skill
3. El asset_catalog.py tiene `promised_by=["low_voice_readiness", "always_aeo"]` -- el tag `"always_aeo"` genera el asset SIEMPRE que hay cualquier problema AEO, lo cual es un bug de configuracion
4. "Anticipatory" es una justificacion debil para un documento comercial que el cliente va a firmar
5. Los modulos de infraestructura (voice_guide.py, voice_readiness_proxy.py) se MANTIENEN en el codigo para uso manual futuro

**Acciones en FASE-5**:
- Cambiar `promised_by` de voice_assistant_guide a `[]` (no se genera automaticamente)
- Eliminar voice_assistant_guide del output de Amaziliahotel
- Si en el futuro el pipeline detecta low_voice_readiness REAL, puede reactivarse

### D3: Informe Mensual -- MANTENER, reclasificar como servicio

**Justificacion**: Es un entregable de servicio incluido (reporte de metricas), no un fix de brecha. La propuesta lo menciona como "Informe Mensual: Metricas claras". Es legitimo como servicio de valor agregado. Se reclasifica en FASE-6 como "Servicio Incluido" (no como resolucion de brecha).

---

## Contexto

**Items resueltos con decision de producto** (H7, H8):

|| ID | Hallazgo | Decision | Justificacion |
|----|----------|----------|---------------|
| H7 | WhatsApp sin brecha | **ELIMINAR** | Hotel YA tiene WhatsApp. Claim falso en propuesta. Bug `promised_by=["always"]` |
| H8 | voice_assistant sin brecha | **ELIMINAR de pipeline** | Sin brecha real. Tag `always_aeo` genera siempre. Modulos se mantienen |
| - | monthly_report | **MANTENER, reclasificar** | Servicio incluido legitimo. No es fix de brecha |

**Items se resuelven solos con FASE-1** (H9, H11):
- H9: 75% assets ESTIMATED -> confidence sube con scraping real
- H11: delivery_ready 25% -> gate pasa con FASE-1

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |
| FASE-2A/2B/2C | ✅ Completada |
| FASE-3 | ✅ Completada |
| FASE-4 | ✅ Completada |

---

## Tareas

### Tarea 1: Ejecutar D1 -- Eliminar WhatsApp de pipeline y output
**Objetivo**: Corregir bug sistemico y eliminar asset falso

**Archivos afectados**:
- `modules/asset_generation/asset_catalog.py` (linea 63: cambiar promised_by)
- `output/v4_complete/amaziliahotel/whatsapp_button/` (eliminar o marcar deprecated)

**Pasos**:
1. En `asset_catalog.py`, cambiar linea 63:
   - ANTES: `promised_by=["no_whatsapp_visible", "whatsapp_conflict", "always"]`
   - DESPUES: `promised_by=["no_whatsapp_visible", "whatsapp_conflict"]`
2. Eliminar carpeta `output/v4_complete/amaziliahotel/whatsapp_button/` o agregar `_DEPRECATED_NO_BRECHA.txt`
3. Verificar que `site_presence_checker.py` detecta WhatsApp correctamente para Amaziliahotel

**Criterios de aceptacion**:
- [ ] `promised_by` de whatsapp_button NO contiene `"always"`
- [ ] Carpeta whatsapp_button eliminada o marcada deprecated
- [ ] `site_presence_checker` tiene logica para detectar WhatsApp existente

### Tarea 2: Ejecutar D2 -- Eliminar Voice Assistant de pipeline automatico
**Objetivo**: Desactivar generacion automatica de voice_assistant_guide

**Archivos afectados**:
- `modules/asset_generation/asset_catalog.py` (linea 219: cambiar promised_by)
- `output/v4_complete/amaziliahotel/voice_assistant_guide/` (eliminar o marcar deprecated)

**Pasos**:
1. En `asset_catalog.py`, cambiar linea 219:
   - ANTES: `promised_by=["low_voice_readiness", "always_aeo"]`
   - DESPUES: `promised_by=[]` (no se genera automaticamente)
2. Eliminar carpeta `output/v4_complete/amaziliahotel/voice_assistant_guide/` o agregar `_DEPRECATED_NO_BRECHA.txt`
3. Verificar que los modulos `modules/delivery/generators/voice_guide.py` y `modules/auditors/voice_readiness_proxy.py` PERMANECEN intactos (no se borran, solo se desactiva la generacion automatica)

**Criterios de aceptacion**:
- [ ] `promised_by` de voice_assistant_guide es `[]`
- [ ] Carpeta voice_assistant_guide eliminada o marcada deprecated
- [ ] Modulos voice_guide.py y voice_readiness_proxy.py SIN MODIFICAR

### Tarea 3: Validar Quality Gates actualizados
**Objetivo**: Verificar que con FASE-1 resuelta y assets eliminados, delivery_ready pasa

**Archivo afectado**:
- `modules/quality_gates/publication_gates.py`

**Criterios de aceptacion**:
- [ ] `delivery_ready` >= 80% (antes era 25%)
- [ ] Gate 8 `asset_confidence` pasa
- [ ] Gate 9 coherencia pasa
- [ ] Assets eliminados (WhatsApp, Voice) no penalizan gates

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| `test_no_whatsapp_always_promised` | `tests/asset_generation/test_asset_catalog.py` | `promised_by` no contiene `"always"` |
| `test_no_voice_always_aeo` | `tests/asset_generation/test_asset_catalog.py` | `promised_by` es `[]` para voice |
| `test_delivery_ready_above_80` | `tests/quality_gates/test_publication_gates.py` | >= 80% |
| `test_asset_confidence_gate` | `tests/quality_gates/test_publication_gates.py` | Pasa gate 8 |

**Comando de validacion**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_asset_catalog.py tests/quality_gates/test_publication_gates.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

> **NO ejecutar v4complete en esta fase.** La validacion E2E se reserva para despues de FASE-6. Usar tests unitarios + py_compile + grep.

---

## Restricciones

- Los modulos voice_guide.py y voice_readiness_proxy.py NO se eliminan, solo se desactiva generacion automatica
- El bug `promised_by=["always"]` es SISTEMICO -- afecta a todos los clientes, no solo Amaziliahotel
- NO crear brechas artificiales para justificar assets eliminados

---

## Post-Ejecucion (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-5 \
    --desc "Decisiones producto: WhatsApp ELIMINADO (hotel ya tiene, bug always), Voice ELIMINADO de pipeline; gates 80%+" \
    --archivos-mod "modules/asset_generation/asset_catalog.py,modules/quality_gates/publication_gates.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **H7 ejecutado**: WhatsApp ELIMINADO, bug `"always"` corregido, carpeta eliminada
- [ ] **H8 ejecutado**: Voice ELIMINADO de pipeline automatico, modulos intactos
- [ ] **promised_by corregidos**: Ni WhatsApp ni Voice tienen tags `"always"` / `"always_aeo"`
- [ ] **delivery_ready >= 80%**: Verificado post-FASE-1
- [ ] **Gates pasan**: 8 y 9 pasan
- [ ] **Tests pasan**: 4/4 tests pasan
- [ ] **`dependencias-fases.md` actualizado**: FASE-5 marcada ✅
- [ ] **Proyecto COMPLETO**: Todas las fases completadas
