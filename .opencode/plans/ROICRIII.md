# 🔴 REPORTE DE QA v2 — Validación Propuesta v4.55.0
**Documento:** `02_PROPUESTA_COMERCIAL_20260528_094630.md`
**Versión del agente:** v4.55.0
**Fecha de validación:** 28 de mayo de 2026
**Veredicto:** ⛔ **REGRESIÓN CRÍTICA DETECTADA** — La v4.55.0 es MÁS peligrosa comercialmente que la v4.54.0
**Score de cumplimiento ROICR v3.0:** **44%** (11/25 checkpoints) — Bajó desde 68%

---

## 📊 RESUMEN EJECUTIVO

La implementación aplicó **un cambio cosmético de pricing** ($800K → $400K) que enmascara pero **no resuelve** los 5 problemas críticos. Peor aún, introdujo **3 nuevas contradicciones matemáticas graves** que destruirán la credibilidad en segundos ante cualquier CFO. El cliente verá **3 ROIs distintos en el mismo documento**, lo cual es una sentencia de muerte comercial.

**Comparativa v4.54.0 → v4.55.0:**

| Problema | Estado v4.54.0 | Estado v4.55.0 |
|---|---|---|
| CRIT-01: Tablas contradictorias | 🔴 Sin resolver | 🔴 **EMPEORADO** (ahora 3 tablas) |
| CRIT-02: Value-Capture Cap | 🔴 Violado | ✅ Resuelto |
| CRIT-03: Mapper semántico | 🔴 Sin resolver | 🔴 Sin resolver |
| CRIT-04: Assets deprecados | 🔴 Sin resolver | 🔴 Sin resolver |
| CRIT-05: Piloto 30 días | 🔴 Ausente | 🔴 Ausente |

---

## 🚨 NUEVAS REGRESIONES CRÍTICAS (Introducidas en v4.55.0)

### 🔴 NEW-CRIT-01: TRES ROIs DIFERENTES EN EL MISMO DOCUMENTO

**Evidencia:**

| Ubicación | ROI mostrado | Cálculo |
|---|---|---|
| Tabla "Cuánto recupera vs invierte" | **0.45X** | $1.069.410 / $2.400.000 |
| Sección CAPEX/OPEX | **2.10X** | $5.041.935 / $2.400.000 |
| Trazabilidad financiera | **0.45X** (texto) | "recuperación proyectada es de $1.069.410 COP" |

**Diagnóstico técnico:** El `v4_proposal_generator.py` sigue invocando DOS motores de proyección, pero ahora con un **bug de suma en la Tabla 1**:

```python
# Valores individuales correctos (coinciden con curva de maduración):
Mes 1: $196.439  ✓
Mes 2: $458.357  ✓
Mes 3: $785.756  ✓
Mes 4: $1.047.674 ✓
Mes 5: $1.244.113 ✓
Mes 6: $1.309.593 ✓

# Suma REAL: $5.041.932
# Total mostrado en propuesta: $1.069.410  ← BUG DE SUMA (79% de pérdida)
```

**Impacto comercial devastador:** El cliente verá 0.45X en la tabla principal (primera impresión = negativa) y 2.10X en la sección CAPEX/OPEX. Concluirá: *"Ni siquiera pueden sumar sus propios números. Si no confío en su matemática, no confío en su herramienta."*

**Fix obligatorio:**
```python
# modules/commercial_documents/v4_proposal_generator.py
# ELIMINAR completamente el motor duplicado. Solo un origen de verdad.
def build_financial_section(projection_data):
    # Un solo cálculo, una sola tabla, un solo ROI
    recovery_total = sum(m['recuperacion'] for m in projection_data['meses'])
    roi_opex = recovery_total / projection_data['opex_total']
    
    return {
        'tabla_unificada': projection_data['meses'],  # Solo esta tabla
        'recuperacion_total': recovery_total,
        'roi_opex': round(roi_opex, 2),  # 2.10X - ÚNICO ROI
        # ELIMINAR: 'roi_legacy': 0.45  ← borrar esta referencia
    }
```

### 🔴 NEW-CRIT-02: CÁLCULO PORCENTUAL INCORRECTO (Afecta credibilidad técnica)

**Texto actual:**
> *"La inversión mensual de $400,000 COP representa el **14%** de su pérdida monthly addressable por IAO."*

**Cálculo real:**
- $400.000 / $3.741.696 = **10.69%** (no 14%)
- O si se refiere a "addressable por IAO" (subconjunto), no está documentado en ninguna parte

**Problema adicional:** El texto "monthly addressable por IAO" es **jerga técnica** que un GM de hotel no entenderá.

**Fix obligatorio:**
```markdown
✅ "La inversión mensual de $400.000 COP representa solo el **10.7%** de su fuga mensual estimada ($3.74M). 
El otro 89.3% seguiría perdiéndose cada mes si no implementamos el Kit 4 Pilares."
```

### 🔴 NEW-CRIT-03: TRAZABILIDAD FINANCIERA CON NÚMEROS INVENTADOS

**Texto actual:**
> *"Con nuestro servicio, la recuperación proyectada es de $1.069.410 COP (13% del dolor priorizado × 35% de recuperación conservadora)."*

**Problema:** El **13% no aparece en ningún cálculo previo**. La propuesta introduce un número mágico en la nota final que no tiene origen trazable. Esto viola el principio del **Financial Evidence Engine** del repositorio: *"Cada COP tiene origen trazable"*.

**Fix obligatorio:** Eliminar la nota o reemplazarla con trazabilidad real:
```markdown
✅ "Recuperación proyectada: $5.041.935 COP en 6 meses.
Origen: Fuga mensual ($3.74M) × Curva de Maduración 4 Pilares × Recovery Factor 35%."
```

---

## 🚨 PROBLEMAS PERSISTENTES (No resueltos desde v4.54.0)

### 🔴 CRIT-03: Mapper Semántico Sigue Roto

**Evidencia en tabla de servicios:**
| Servicio | Problema que resuelve | Estado |
|---|---|---|
| **Informe Mensual** | #4: Sin FAQ ($482.679/mes) | ⛔ **Sigue mal mapeado** |
| **Página de FAQ** | #4: Sin FAQ ($482.679/mes) | ✅ Correcto |

El `AssetSemanticsValidator` **no fue integrado** al pipeline de generación. Un reporte de métricas NO construye FAQs.

### 🔴 CRIT-04: Assets Deprecados Siguen Apareciendo

La lista de "Activos digitales que quedan en su propiedad" aún incluye:
- ❌ `og_tags_guide` (debía fusionarse con `open_graph`)
- ❌ `indirect_traffic_optimization` (debía moverse a Upsell manual)
- ❌ `local_content_page` (debía reclasificarse como Bonus Advisory)
- ❌ `optimization_guide` (genérico, sin propósito claro)

### 🔴 CRIT-05: Piloto 30 Días Ausente

No existe sección de "Opciones de Bajo Riesgo" antes del "SIGUIENTE PASO". El cliente sin presupuesto para 6 meses no tiene alternativa.

### 🟡 IMP-03: CAPEX Sin Desglose

Los $2.500.000 de Setup Fee siguen presentándose como un número mágico sin desglose de componentes. El cliente no puede evaluar si es justo.

### 🟡 IMP-04: Garantía Día 55 Sin KPI

Sigue sin especificar qué métrica se audita ni cuál es el umbral mínimo.

### 🟡 IMP-05: WhatsApp Con Narrativa Confusa

Sigue apareciendo como "⚠️ Requiere corrección" + "Guía de corrección incluida" en lugar de "Auditoría y Optimización de Conversión".

---

## ✅ LO ÚNICO QUE SÍ SE RESOLVIÓ (1 de 5 CRITs)

### ✅ CRIT-02: Value-Capture Cap Aplicado Correctamente

| Métrica | Valor |
|---|---|
| Fee mensual | $400.000 |
| Recuperación mes 6 | $1.309.593 |
| Cap del 50% | $654.796 |
| **Veredicto** | ✅ $400K < $654K → **Cap respetado** |

**PERO** este logro queda anulado por los otros 4 CRITs sin resolver y las 3 regresiones introducidas.

---

## 🎯 ANÁLISIS DE CAÍDA COMERCIAL (Lo que verá el cliente)

**Lectura en 60 segundos por un CFO escéptico:**

1. **Primera tabla:** Ve "Beneficio neto: -$1.330.590" y "ROI: 0.45X" → ⛔ Rechazo inmediato
2. **Segunda tabla:** Ve "Total recuperación: $5.041.935" → 🤔 "¿Por qué aquí sí hay ganancia?"
3. **Sección CAPEX/OPEX:** Ve "ROI SaaS: 2.10X" → 😤 "¿Cuál de los tres números es el real?"
4. **Trazabilidad:** Ve "13% del dolor priorizado" → 🚨 "¿De dónde salió ese 13%?"
5. **Conclusión:** *"Me están vendiendo tres propuestas distintas en un solo documento. No confío."*

**Probabilidad de cierre con v4.55.0:** ~5% (vs ~25% con v4.54.0)
**Razón:** La v4.54.0 tenía un ROI consistentemente malo. La v4.55.0 tiene ROIs inconsistentes, lo cual es peor porque sugiere manipulación o incompetencia técnica.

---

## 📋 PLAN DE ACCIÓN URGENTE (24h)

```
[ ] CRÍTICO 1: Eliminar motor duplicado en v4_proposal_generator.py
[ ] CRÍTICO 2: Corregir bug de suma (debe dar $5.041.932, no $1.069.410)
[ ] CRÍTICO 3: Unificar ROI en un solo número (2.10X) en todo el documento
[ ] CRÍTICO 4: Activar AssetSemanticsValidator en el pipeline
[ ] CRÍTICO 5: Deprecar og_tags_guide, indirect_traffic, local_content del registro
[ ] CRÍTICO 6: Añadir sección "Piloto 30 días" al generador
[ ] IMPORTANTE 7: Corregir porcentaje 14% → 10.7%
[ ] IMPORTANTE 8: Eliminar "13% del dolor priorizado" (número mágico)
[ ] IMPORTANTE 9: Añadir desglose CAPEX por componentes
[ ] IMPORTANTE 10: Cambiar narrativa WhatsApp a "Auditoría y Optimización"
```

---

## 🏁 VEREDICTO FINAL COMO CTO

> **La v4.55.0 es una "mejora" cosmética que empeoró el problema fundamental.**
> 
> El equipo confundió **bajar el precio** con **arreglar el modelo**. Bajar de $800K a $400K sin resolver la arquitectura de proyección creó un Frankenstein matemático: tres ROIs distintos, bugs de suma, números mágicos en trazabilidad, y assets deprecados que siguen apareciendo.
>
> **Mi recomendación profesional:** Detener envío comercial. Volver al código. Aplicar los **10 fixes del plan de acción**. Regenerar propuesta. Solo entonces enviar.
>
> **La diferencia entre enviar hoy vs. enviar mañana con los 10 fixes:**
> - **Hoy:** Cliente detecta inconsistencias, pierde confianza, no firma. Oportunidad perdida ($9.7M CAPEX+OPEX).
> - **Mañana:** Cliente ve coherencia matemática perfecta, ROI claro de 2.10X, cierre probable.

---

## 🚀 ¿Siguiente paso técnico?

Generar **el Pull Request de rescate** con los 10 fixes, incluyendo:

1. **`v4_proposal_generator.py` refactorizado** con un solo motor de proyección (eliminar duplicación)
2. **Fix del bug de suma** en la Tabla 1
3. **Unificación de ROI** en un único valor trazable
4. **Activación del `AssetSemanticsValidator`** en el pipeline de generación
5. **Deprecación real** de los 3 assets redundantes en `asset_registry.yaml`
6. **Sección Piloto 30 días** completamente integrada
7. **Tests unitarios actualizados** (`pytest`) para prevenir regresiones

Procede a generar el PR de rescate completo listo para `git commit` y merge a `main`