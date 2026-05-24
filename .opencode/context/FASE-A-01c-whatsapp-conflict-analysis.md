# Contexto Técnico — FASE-A-01c: WhatsApp Conflict + hotel_schema confidence

**Fecha:** 2026-05-23
**Fase:** FASE-A-01c (v4complete Hotel Castilla Real)
**Proyecto:** AGENTSMD-DRIFT

---

## Resumen Ejecutivo

El v4complete para Hotel Castilla Real generó dos warnings no bloqueantes en G8 (asset_confidence). El análisis detallado reveló:

1. **WhatsApp conflict es un conflicto REAL**, no un false positive
2. **hotel_schema confidence 0.00** es correcto — el sitio genuinamente no tiene Schema.org markup

---

## 1. WhatsApp Conflict — Detalle Técnico

### Datos del conflicto
```
web_scraping (sitio web):  63332192
gbp_api (Google Business): 3104692201
```

El sitio web y el Google Business Profile del hotel tienen **dos números de WhatsApp completamente diferentes**. Esto es un conflicto real de datos, no un error de detección.

### Por qué confidence bajo (0.30)

El `whatsapp_conflict_guide` tiene confidence 0.30 porque:
- El conflicto fue detectado correctamente (2 números distintos)
- El activo necesita evidence consistente para generar contenido de alta confianza
- Con dos fuentes contradictorias, el sistema no puede determinar cuál número es el correcto → confidence bajo

### Código relevante

**contradiction_engine.py:304** — `_whatsapp_number_mismatch`:
```python
def _whatsapp_number_mismatch(self, claims: List[Claim]) -> List[Conflict]:
    # Extrae teléfonos de claims
    # Si hay más de un número → conflicto HARD
    phone_numbers = list(phones.keys())
    if len(phone_numbers) > 1:
        # genera Conflict con resolution_hint
```

**audit_report** — conflictos detectados:
```json
{
  "field_name": "whatsapp",
  "value": "63332192",
  "confidence": "conflict",
  "discrepancies": [
    "web_scraping (63332192) != gbp_api (3104692201)"
  ],
  "requires_manual_review": true
}
```

### Implicación para el pipeline

- El pipeline **actuó correctamente**: detectó el conflicto real, generó el asset con WARNING
- Coherence pasó (0.83) porque el sistema sabe que hay un conflicto y lo documenta
- El delivery package se creó con estado **WARNING non-blocking** ⚠️ — G8 (asset_confidence) falló con 2 assets bajo threshold 0.7, pero blocking=false permite entrega

---

## 2. hotel_schema — confidence 0.00

### Por qué 0.00 (correcto)

El audit encontró **0 schemas** en la página del hotel. No es un false positive ni un bug de detección — el sitio genuinamente no tiene Schema.org markup implementado.

```
[1/5] Validating structured data schemas...
      Found 0 schemas
      Hotel: unknown
      FAQ: unknown
```

### Código relevante

**contradiction_engine.py:189** — `_whatsapp_verified_not_visible` busca claims de "whatsapp" en el category del claim, no relacionado con schema.

El schema validation corre independientemente en `schema_validator_v2.py` que reporta 0 schemas encontrados → confidence 0.00.

---

## 3. Visibilidad del Warning en el Diagnóstico

### Cómo aparece actualmente

El warning de WhatsApp conflict aparece en la sección **"Validación de Calidad"**, dentro de una tabla de 3 filas sin separador visual claro:

```
| Conflicto: whatsapp             | 🔴 Alta  | Revisión manual requerida |
```

### Problemas de legibilidad para un hotelero

| Problema | Detalle |
|---|---|
| **Sección técnica** | "Validación de Calidad" suena a jerga interna — el hotelero lee "Diagnóstico" y "Oportunidad" |
| **Contexto diluido** | "Revisión manual requerida" compite visualmente con "Fotos GBP" y "Core Web Vitals" — suena menos urgente |
| **Sin impacto financiero** | Las 7 BRECHAS principales tienen `$X COP/mes`. WhatsApp conflict no tiene cifra — refuerza que no es "oportunidad" pero confunde |
| **Sin conexión a cuerpo** | Las BRECHAS 1-7 no referencian este warning. Hotelero que va directo a brechas no lo ve |
| **Indicador único** | Solo el emoji 🔴 señala gravedad — insuficiente para un tema que mata reservas |

### Implicación comercial real (no documentada)

GBP mostrando número diferente al sitio = **cliente llama/wasappea al número equivocado = reserva perdida sin que el hotel lo sepa**.

Este impacto NO está cuantificado ni mencionado en el diagnóstico.

### Decisión: NO incluir como BRECHA/OPORTUNIDAD

Tratarlo como BRECHA implicaría afirmar que tenemos un ASSET para resolverlo. No lo tenemos. La solución requiere que el hotelero:
1. Decida cuál número es el correcto
2. Actualice manualmente su CMS y su GBP

Eso es operativo, no técnico — fuera de nuestro alcance como deliverable de iah-cli.

### Recomendación de visibilidad (opcional)

Si se quisiera hacer la advertencia más notable para el hotelero, debería:
- Aparecer como nota directa en la sección de contexto, no en "Validación de Calidad"
- Incluir phrasing de impacto de negocio: "Su Google Business muestra un número diferente al de su sitio — cada cliente que intenta reservar por WhatsApp desde Google podría estar escribiendo al número equivocado"
- Sin costo mensual asociado (no tenemos activo para cuantificarlo)

---

## 4. Recommendation

**Sin fase adicional requerida.** El pipeline funcionó correctamente.

### Para FASE-RELEASE futuras (nota técnica)
Estos comportamientos no son intuitivos y merecen documentarse como nota en GUIA_TECNICA.md:
- El `whatsapp_conflict_guide` genera con confidence < 0.50 cuando múltiples fuentes tienen números distintos — es comportamiento esperado, no bug de detección
- El `hotel_schema` con confidence 0.00 indica ausencia total de Schema.org markup en el sitio — no es un false positive del validador
- G8 (asset_confidence) con 2 assets bajo threshold 0.7 produce WARNING non-blocking, no BLOCK — el delivery sigue siendo válido

### Para fases futuras (opcional)
Si se quisiera atacar el problema de raíz:
- Corregir conflicto de WhatsApp real requiere que el hotel unifique sus números (no es un fix de código)
- Implementar hotel_schema requiere trabajo en el sitio del hotel, no en iah-cli

---

## 5. Archivos de evidencia

Todo guardado en `evidence/FASE-A-01c/`:
- `audit_report_20260523_220753.json` — datos crudos del conflicto
- `pain_ledger.json` — 11 entries incluyendo whatsapp_conflict
- `gate_report_*.json` — 9/11 gates PASS

---

## 6. Tags para búsqueda

- `whatsapp_conflict` `number_mismatch` `contradiction_engine` `confidence_low`
- `hotel_schema` `schema_validation` `zero_schemas`
- `false_positive_analysis` `not_a_bug`
- `warning_visibility` `diagnostic_readability` `hotelero_comprehension`