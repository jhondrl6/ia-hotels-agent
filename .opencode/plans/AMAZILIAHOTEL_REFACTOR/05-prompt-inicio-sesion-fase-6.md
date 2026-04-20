# FASE-6: Corrección Documentos Comerciales (A4, A5, M4)

**ID**: FASE-6  
**Objetivo**: Corregir errores en documentos comerciales (01 y 02) aplicando decisiones de FASE-5  
**Dependencias**: FASE-1 (BookingScraper real), FASE-5 (decisiones producto) COMPLETADAS  
**Duración estimada**: 1.5 horas  
**Skill**: `iah-cli-plan-reality-check`

---

## Contexto

**Hallazgos no abordados en fases anteriores**:

| ID | Hallazgo | Tipo | Problema |
|----|----------|------|----------|
| A4 | ROI 20X sin base Tier C | INFLACION | Propuesta comercial exagera ROI sin base real |
| A5 | 3 servicios sin brecha | DESALINEACION | WhatsApp, Voice e Informe Mensual no tienen brecha B1-B4 en diagnostico |
| M4 | WhatsApp numero no verificado | VERIFICACION | Numero 573104019049 ya verificado contra GBP |

**Documento comercial verificado - claims falsos identificados**:

| Linea | Propuesta | Claim | Realidad | Accion |
|-------|-----------|-------|----------|--------|
| 29 | Tabla problemas | "No hay boton de WhatsApp" | **FALSO** - hotel YA tiene WhatsApp | Eliminar fila |
| 51 | Tabla servicios | "Boton de WhatsApp" como servicio | Ya existe, no se puede vender | Eliminar fila |
| 49 | Tabla servicios | "Busqueda por Voz (AEO)" | No hay brecha de voz detectada | Eliminar fila |
| 53 | Tabla servicios | "Informe Mensual" | No es fix de brecha, es servicio incluido | Reclasificar |
| 69 | Tabla entregables | "Boton de WhatsApp" | Idem linea 51 | Eliminar fila |
| 113 | ROI | "ROI: 20.0 (24X en 6 meses)" | Insostenible con Tier C | Corregir |
| 124 | Timeline | "Boton de WhatsApp instalado" | Ya existe | Eliminar |

**Documentos afectados**:
- `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260415_113914.md`
- `output/v4_complete/02_PROPUESTA_COMERCIAL_20260415_113915.md`

**Impacto**: Sin estas correcciones, el score forense no llega a 80/100 porque los tri-plays siguen fallando.

---

## Tareas

### Tarea 1: Corregir A5 - Eliminar WhatsApp de documentos comerciales
**Objetivo**: Remover todas las claims falsas sobre WhatsApp

**Problema**: La propuesta dice "No hay boton de WhatsApp" (linea 29) y lo vende como servicio (linea 51). El hotel YA TIENE WhatsApp. Esto destruye credibilidad.

**Cambios en 02_PROPUESTA_COMERCIAL_*.md**:
1. Linea 29: Eliminar fila "Entra a su web | No hay boton de WhatsApp | No reserva directo"
2. Linea 51: Eliminar fila "Boton de WhatsApp | Sus guests reservan con 1 clic desde su web"
3. Linea 69: Eliminar fila "Boton de WhatsApp | ⚠️ Requiere datos"
4. Linea 124: Eliminar "Boton de WhatsApp instalado" del timeline

**Cambios en 01_DIAGNOSTICO_*.md**:
- NO modificar -- el diagnostico no menciona WhatsApp como brecha (correcto)

**Criterios de aceptacion**:
- [ ] Propuesta NO menciona WhatsApp como servicio vendible
- [ ] Propuesta NO dice que falta boton de WhatsApp
- [ ] Tabla de problemas tiene 3 filas (sin fila WhatsApp)
- [ ] Tabla de servicios tiene 5 servicios (sin WhatsApp, sin Voice)

### Tarea 2: Corregir A5 - Eliminar Voice de documentos comerciales
**Objetivo**: Remover claims de busqueda por voz

**Cambios en 02_PROPUESTA_COMERCIAL_*.md**:
1. Linea 49: Eliminar fila "Busqueda por Voz (AEO) | Aparece cuando alguien dice..."
2. Linea 67: Eliminar fila "Busqueda por Voz | ⚠️ Requiere datos"

**Cambios en 01_DIAGNOSTICO_*.md**:
- NO modificar AEO score (0/100 es correcto como metrica)
- El diagnostico no vende servicios de voz, solo reporta el score

**Criterios de aceptacion**:
- [ ] Propuesta NO ofrece "Busqueda por Voz" como servicio
- [ ] Tabla de servicios tiene solo servicios con brecha real B1-B4 + Informe

### Tarea 3: Corregir A5 - Reclasificar Informe Mensual
**Objetivo**: Mover Informe Mensual de "servicio de brecha" a "servicio incluido"

**Cambios en 02_PROPUESTA_COMERCIAL_*.md**:
1. Separar servicios en dos secciones:
   - "Servicios de Optimizacion" (basados en brechas B1-B4): GEO, IAO, SEO Local, Datos Estructurados
   - "Servicios Incluidos" (valor agregado): Informe Mensual
2. El Informe Mensual pasa a ser "Servicio Incluido en su plan" no un fix de brecha

**Criterios de aceptacion**:
- [ ] Propuesta tiene seccion "Servicios de Optimizacion" con 4-5 servicios con brecha real
- [ ] Propuesta tiene seccion "Servicios Incluidos" con Informe Mensual
- [ ] Informe Mensual NO se presenta como resolucion de brecha

### Tarea 4: Corregir A4 - ROI realista por Tier
**Objetivo**: Ajustar ROI a valores honestos basados en nivel de evidencia

**Problema actual**:
- Inversion: $130,500/mes
- Recuperacion: $2,610,000/mes
- ROI declarado: 20X (24X en 6 meses)
- Nivel de evidencia: Tier C (datos limitados)

**ROI propuesto por nivel de evidencia**:

| Tier | Base de calculo | ROI realista | Recuperacion/mes |
|------|----------------|-------------|-----------------|
| **C** (actual) | Datos limitados web + benchmarks | **3X** | ~$391,500 |
| **B** (con benchmarks) | Benchmarks regionales + datos web | **8-10X** | ~$1,040,000-$1,305,000 |
| **A** (con GA4+GSC) | Analytics reales + Search Console | **15-20X** | ~$1,960,000-$2,610,000 |

**Cambios en 02_PROPUESTA_COMERCIAL_*.md**:
1. Linea 113: Cambiar "ROI: 20.0" a "ROI proyectado: 3X (Tier C) → 20X (con GA4)"
2. Agregar disclaimer: "ROI basado en Tier C (datos limitados). Con GA4 y Search Console, el ROI puede alcanzar 20X."
3. Tabla de proyeccion 6 meses: usar escenario Tier C ($391,500/mes) como base
4. Beneficio neto: $1,563,000 (6 meses Tier C) en lugar de $14,877,000

**Criterios de aceptacion**:
- [ ] ROI <= 5X para escenario Tier C actual
- [ ] ROI 15-20X solo como "potencial con GA4"
- [ ] Sin claims de "20X garantizado"
- [ ] Disclaimer de Tier C visible
- [ ] Proyeccion financiera coherente con escenario Tier C

### Tarea 5: Verificar M4 - WhatsApp numero (CERRADO)
**Objetivo**: Documentar verificacion completa del numero WhatsApp

**Verificacion ya realizada**:
```
Asset: 573104019049
GBP:   310 4019049
Mismo numero: SI (con prefijo pais 57)
```

**Accion**: M4 ya esta verificado. El numero coincide. Dado que el asset se ELIMINA (D1 en FASE-5), M4 se cierra como verificado-sin-accion.

**Criterios de aceptacion**:
- [ ] M4 documentado como verificado
- [ ] Numero coincide con GBP (confirmado)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| `test_propuesta_no_whatsapp_service` | `tests/commercial_documents/test_proposal_consistency.py` | WhatsApp NO aparece como servicio |
| `test_propuesta_no_voice_service` | `tests/commercial_documents/test_proposal_consistency.py` | Voice NO aparece como servicio |
| `test_propuesta_roi_tier_c` | `tests/commercial_documents/test_proposal_consistency.py` | ROI <= 5X para Tier C |
| `test_diagnostico_4_brechas` | `tests/commercial_documents/test_diagnostic_consistency.py` | Exactamente 4 brechas B1-B4 |
| `test_servicios_alineados_brechas` | `tests/commercial_documents/test_proposal_consistency.py` | Servicios de optimizacion alineados con B1-B4 |

**Comando de validacion**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -v
```

> **NO ejecutar v4complete en esta fase.** La validacion E2E final con v4complete se ejecuta despues de completar todas las fases. Ver `06-checklist-implementacion.md` seccion "VALIDACION E2E FINAL".

**Validacion manual (post-correccion)**:
```bash
# Verificar que WhatsApp ya no aparece como servicio vendible
grep -n -i "boton de whatsapp\|botón de whatsapp" output/v4_complete/02_PROPUESTA_COMERCIAL_*.md
# Debe retornar 0 matches

# Verificar que Voice ya no aparece como servicio vendible
grep -n -i "busqueda por voz\|búsqueda por voz\|AEO" output/v4_complete/02_PROPUESTA_COMERCIAL_*.md
# Debe retornar 0 matches en tabla de servicios

# Verificar ROI <= 5X
grep -n "ROI" output/v4_complete/02_PROPUESTA_COMERCIAL_*.md
# Debe mostrar "ROI proyectado: 3X" no "ROI: 20.0"
```

---

## Restricciones

- NO inventar datos financieros - solo usar datos verificados
- NO eliminar servicios sin decision de FASE-5 ya ejecutada
- NO crear brechas artificiales
- El diagnostico (01) NO se modifica excepto si se necesitan ajustes de coherencia
- Mantener backwards compatibility con formato de documentos

---

## Post-Ejecucion (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-6 \
    --desc "Documentos comerciales corregidos: WhatsApp eliminado (hotel ya tiene), Voice eliminado, Informe reclasificado, ROI Tier C 3X realista" \
    --archivos-mod "output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md,output/v4_complete/02_PROPUESTA_COMERCIAL_*.md" \
    --tests "5" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **A4 corregido**: ROI 3X para Tier C, 20X solo como potencial con GA4
- [ ] **A5 corregido**: WhatsApp eliminado (claim falso), Voice eliminado, Informe reclasificado
- [ ] **M4 cerrado**: Numero verificado contra GBP, asset eliminado
- [ ] **Tests pasan**: 5/5 tests pasan
- [ ] **`dependencias-fases.md` actualizado**: FASE-6 marcada ✅
- [ ] **Documentos actualizados**: 01 y 02 coherentes entre si
- [ ] **Propuesta tiene 5 servicios**: GEO, IAO, SEO Local, Datos Estructurados, Informe Mensual (reclasificado)
- [ ] **Tri-play valido**: Cada servicio tiene brecha en diagnostico + propuesta + asset real
