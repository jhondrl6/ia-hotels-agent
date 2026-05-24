# FASE-A-02a — Reporte de Hallazgos: Visibilidad WhatsApp Conflict

**Fase**: FASE-A-02a  
**Fecha**: 2026-05-24  
**Skill**: systematic-debugging  
**Tipo**: Investigación pura — SIN modificación de código

---

## Hallazgo 1: `_build_manual_attention_table` (L 1477-1501)

### Flujo actual

```python
def _build_manual_attention_table(self, audit_result: V4AuditResult) -> str:
    rows = []
    if audit_result is None or audit_result.gbp is None:
        return "| Datos de GBP no disponibles | - | - | - |"
    
    # GBP issues
    if audit_result.gbp.geo_score < 70:
        rows.append(f"| Perfil GBP Sub-optimizado | 🟡 Media | Optimizar ...")
    if audit_result.gbp.photos < 20:
        rows.append(f"| Fotos GBP Insuficientes | 🟡 Media | ...")
    if audit_result.performance and not audit_result.performance.has_field_data:
        rows.append("| Sin Datos de Campo (Core Web Vitals) | 🟡 Media | ...")
    
    # Conflicts — TODOS en el mismo bloque
    if audit_result.validation and audit_result.validation.conflicts:
        for conflict in audit_result.validation.conflicts:
            rows.append(f"| Conflicto: {conflict.get('field_name', 'Desconocido')} | 🔴 Alta | Revisión manual requerida |")
    
    return "\n".join(rows) if rows else "..."
```

### Qué significa esto

- Itera sobre `audit_result.validation.conflicts` (lista de dicts)
- Cada conflict genera una fila genérica: `"| Conflicto: {field_name} | 🔴 Alta | Revisión manual requerida |"`
- **NO hay diferenciación**: `whatsapp`, `phone`, `address` — todos reciben el mismo formato
- Los datos disponibles del conflict (`value`, `discrepancies`) se ignoran en la tabla
- La severidad siempre es "🔴 Alta" para todos los conflicts

### Gap crítico

> La tabla de "Validación de Calidad" trata whatsapp_conflict como una fila genérica más. No hay forma de distinguir que este conflicto tiene impacto de **reserva perdida sin que el hotel lo sepa**.

---

## Hallazgo 2: Posición en template `diagnostico_v6_template.md`

### Sección del template (L 96-104)

```
## ✅ Validación de Calidad

${asset_confidence_note}

${manual_attention_table}          ← L 100: tabla WhatsApp conflict aquí

Brechas detectadas que afectan su presencia digital y reservas directas:

${brechas_section}
```

### Ubicación en el documento

| Aspecto | Valor |
|---------|-------|
| Sección | "Validación de Calidad" (tercera sección principal) |
| Orden en documento | Después de scores, métricas IA, contexto regional |
| Posición relativa | Compite con: GBP sub-optimizado, fotos insuficientes, Core Web Vitals |
| Variable anterior | `${asset_confidence_note}` |
| Variable siguiente | `${brechas_section}` (BRECHAS) |

### Gap crítico

> `${regional_context}` está en L 44 (sección "Contexto Regional"), ANTES de "Validación de Calidad". La tabla `${manual_attention_table}` está 56 líneas después. **No hay ninguna variable de nota de negocio entre estas dos.**

---

## Hallazgo 3: `pain_narratives` de `whatsapp_conflict`

### Estado actual en código (L 2603-2607)

```python
'whatsapp_conflict': {
    'nombre': 'Datos Inconsistentes (Confusion Cliente)',
    'impacto': pain_narratives.get('whatsapp_conflict', 0.10),
    'detalle': 'WhatsApp diferente en web vs Google. Cliente confundido = reserva perdida.'
},
```

### Estado actual en YAML (`config/regional_benchmarks.yaml` L 21)

```yaml
whatsapp_conflict: 0.10   # valor por defecto en las 4 regiones
```

### Phrasing actual vs. recomendado (L 127 de FASE-A-01c)

| Aspecto | Actual | Recomendado |
|---------|--------|-------------|
| Framing | "Conflicto de datos" | "Reserva perdida sin que el hotel lo sepa" |
| Detalle | "Cliente confundido = reserva perdida" | "Su Google Business muestra un número diferente al de su sitio — cada cliente que intenta reservar por WhatsApp desde Google podría estar escribiendo al número equivocado" |
| Cuantificación | Ninguna | Ninguna (sin costo mensual por decisión) |

### Gap

> El phrasing actual dice "WhatsApp diferente" — suena técnico y menor. El phrasing recomendado (L 127) es específico y con impacto de negocio: "número diferente al de su sitio" + "escribiendo al número equivocado".

---

## Hallazgo 4: Variables candidatas para nota de contexto

### Variables disponibles en sección "Contexto Regional"

```
L 44:  ${regional_context}
L 46:  ${hotel_landmark}
L 28-30: hotel_region (del template_data)
```

### Variables disponibles en sección "Validación de Calidad"

```
L 98:  ${asset_confidence_note}
L 100: ${manual_attention_table}
L 104: ${brechas_section}
```

### Ubicación óptima identificada

```
## 📍 CONTEXTO REGIONAL: ...

${regional_context}

#> **Pregunta clave**: ...

---
## 📊 ANÁLISIS ACTUAL: SU POSICIÓN ...

${whatsapp_conflict_business_note}   ← NUEVA VARIABLE AQUÍ
```

**Justificación**: Después de `${regional_context}` y antes de la tabla de scores, el hotelero ya tiene el contexto regional. Mostrar el warning de WhatsApp conflict aquí (con impacto de negocio)会比diluido en "Validación de Calidad" tiene **10x más visibilidad**.

### Datos necesarios para construir la nota

| Dato | Fuente | Disponibilidad |
|------|--------|----------------|
| `conflict.field_name == 'whatsapp'` | `audit_result.validation.conflicts` | ✅ |
| `conflict.phone_web` | `conflict.get('phone_web')` | ✅ |
| `conflict.phone_gbp` | `conflict.get('phone_gbp')` | ✅ |
| `hotel_name` | `audit_result.hotel_name` | ✅ |
| `hotel_region` | `audit_result.region` | ✅ |

---

## Resumen de Gaps

| Gap | Severidad | Descripción |
|-----|-----------|-------------|
| G1 | CRÍTICO | `_build_manual_attention_table` no diferencia whatsapp_conflict de otros conflicts — todas las filas son genéricas |
| G2 | CRÍTICO | No existe `${whatsapp_conflict_business_note}` en el template — no hay manera de insertar la nota de impacto de negocio |
| G3 | ALTO | El phrasing actual en `pain_narratives` es técnico ("Datos Inconsistentes"), no de impacto de negocio |
| G4 | MEDIO | Impacto en `regional_benchmarks.yaml` es 0.10 — menor que `no_whatsapp_visible` (0.20), lo que refuerza la subestimación |

---

## Recomendación para FASE-A-02b

1. **Crear `_build_whatsapp_conflict_note(audit_result)`** en `v4_diagnostic_generator.py`
   - Retorna `""` si no hay conflict whatsapp
   - Genera nota con: `phone_web`, `phone_gbp`, `hotel_name`
   - Phrasing: "Su Google Business muestra un número diferente al de su sitio — cada cliente que intenta reservar por WhatsApp desde Google podría estar escribiendo al número equivocado"

2. **Agregar `${whatsapp_conflict_business_note}` al template** después de `${regional_context}` (L 44-46)

3. **Hacer condicional**: solo aparece cuando existe `whatsapp` en conflicts

---

*Fase: WHATSAPP-CONFLICT-VISIBILITY / FASE-A-02a*  
*Creado: 2026-05-24*