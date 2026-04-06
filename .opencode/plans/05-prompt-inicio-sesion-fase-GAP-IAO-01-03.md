# GAP-IAO-01-03: Propuesta con Monetización de Debilidades

**ID**: GAP-IAO-01-03
**Objetivo**: Que la propuesta comercial use score real y monetice las debilidades del CHECKLIST_IAO
**Dependencias**: GAP-IAO-01-02 (diagnóstico con KB)
**Duración estimada**: 1-2 horas
**Skill**: Ninguna específica (conectar lo que existe)

---

## Contexto

### Qué debe hacer esta fase

1. **Recibir score real** del diagnóstico (técnico + IA)
2. **Mostrar faltantes** del CHECKLIST_IAO con impacto monetizado
3. **Mapear cada faltante a una recomendación** con costo y beneficio

### De FASE-0

```
Debilidades KB → Score (KB算法) → Monetización → Recomendación → Asset

Ejemplo:
"Sin Schema FAQ" → -8 pts → "Pierde X% CTR en Google" → "Implementar FAQPage Schema" → faq_page
```

### Flujo de datos

```
DIAGNÓSTICO (GAP-IAO-01-02)
    │
    ├── score_final: 52
    ├── score_tecnico: 60
    ├── score_ia: 38
    ├── paquete: "avanzado"
    ├── faltantes: ["ssl", "schema_faq", "open_graph", "nap_consistente"]
    │
    ▼
PROPUESTA (ESTA FASE)
    │
    ├── Recibe: DiagnosticSummary con score real
    ├── Muestra: Score con benchmark regional
    ├── Monetiza: Cada faltante = pérdida mensual
    └── Recomienda: Paquete basado en score real
```

---

## Tareas

### Tarea 1: Modificar DiagnosticSummary para recibir score KB

**Archivo**: `modules/commercial_documents/data_structures.py`

**Agregar campos** a `DiagnosticSummary`:

```python
@dataclass
class DiagnosticSummary:
    """Summary of diagnostic for proposal generation."""
    hotel_name: str
    critical_problems_count: int
    quick_wins_count: int
    overall_confidence: ConfidenceLevel
    top_problems: List[str] = field(default_factory=list)
    validated_data_summary: Dict[str, Any] = field(default_factory=dict)
    coherence_score: Optional[float] = None
    
    # === CAMPOS NUEVOS (GAP-IAO-01-03) ===
    score_tecnico: Optional[int] = None      # 0-100 de calcular_cumplimiento()
    score_ia: Optional[int] = None           # 0-100 de AEOKPIs
    paquete: Optional[str] = None             # "basico" / "avanzado" / "premium"
    faltantes: List[str] = field(default_factory=list)  # Elementos KB que fallan
    data_source: Optional[str] = None        # "IATester+BingProxy" / "KB" / "N/A"
```

**Criterios de aceptación**:
- [ ] `DiagnosticSummary` tiene campos `score_tecnico`, `score_ia`, `paquete`, `faltantes`, `data_source`
- [ ] Backwards compatible: si no existen, la propuesta funciona igual

### Tarea 2: Modificar v4_proposal_generator para monetizar faltantes

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Agregar lógica** de monetización:

```python
# Tabla de monetización de faltantes
# BASADO EN: KB [SECTION:CHECKLIST_IAO] + [SECTION:PRIORITY_MATRIX]

FALTANTE_MONETIZACION = {
    "ssl": {
        "impacto": "Riesgo de seguridad - HTTPS es requisito",
        "monetizacion": "Perdida de posicionamiento Google",
        "asset": None,  # Guía SSL manual
    },
    "schema_hotel": {
        "impacto": "Invisible para ChatGPT, Gemini, Perplexity",
        "monetizacion": "15-25% menos apariciones en respuestas de IA",
        "asset": "hotel_schema",
    },
    "schema_reviews": {
        "impacto": "Sin estrellas en Google (rich snippets)",
        "monetizacion": "8-12% menor CTR en búsquedas",
        "asset": "hotel_schema",  # Con aggregateRating
    },
    "LCP_ok": {
        "impacto": "53% abandono si >3 segundos",
        "monetizacion": "Perdida de reservas móviles",
        "asset": None,  # Guía optimización LCP
    },
    "schema_faq": {
        "impacto": "Sin rich snippets en Google",
        "monetizacion": "10-15% menor visibilidad",
        "asset": "faq_page",
    },
    # ... continuar según KB
}
```

**Criterios de aceptación**:
- [ ] Cada faltante del diagnóstico se monetiza
- [ ] La propuesta muestra: score real + benchmark + faltantes + monetización
- [ ] Si no hay datos IA → propuesta muestra "N/A" y usa solo score técnico

### Tarea 3: Conectar score real a paquete

```python
def _determinar_paquete(diagnostic_summary: DiagnosticSummary) -> dict:
    """
    Usa score_tecnico de KB para sugerir paquete.
    BASADO EN: KB sugerir_paquete()
    """
    score = diagnostic_summary.score_tecnico or 50  # Default si no existe
    
    if score < 40:
        paquete = "basico"
    elif score < 70:
        paquete = "avanzado"
    else:
        paquete = "premium"
    
    # Ajustar por score IA si disponible
    if diagnostic_summary.score_ia is not None:
        score_ia = diagnostic_summary.score_ia
        # Si score IA es muy bajo, puede recomendar paquete mayor
        if score_ia < 30 and paquete == "basico":
            paquete = "avanzado"  # IAI bajo necesita más work
    
    return {
        "paquete": paquete,
        "score_final": score,
        "score_ia": diagnostic_summary.score_ia,
        "confianza": "ALTA" if diagnostic_summary.score_ia else "N/A",
    }
```

---

## Archivos a modificar

| Archivo | Qué modificar |
|---------|--------------|
| `modules/commercial_documents/data_structures.py` | Agregar campos a `DiagnosticSummary` |
| `modules/commercial_documents/v4_proposal_generator.py` | Usar score real, monetizar faltantes |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`06-checklist-implementacion.md`**: Marcar GAP-IAO-01-03 como completada

2. **Ejecutar**:
```bash
python scripts/log_phase_completion.py \
    --fase GAP-IAO-01-03 \
    --desc "Propuesta con score KB real + monetización de faltantes CHECKLIST_IAO" \
    --archivos-mod "modules/commercial_documents/data_structures.py,modules/commercial_documents/v4_proposal_generator.py" \
    --check-manual-docs
```

---

## Criterios de Completitud

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] `DiagnosticSummary` tiene campos para score KB
- [ ] Propuesta muestra score real si disponible
- [ ] Propuesta muestra "N/A" si no hay datos IA
- [ ] Cada faltante tiene monetización en la propuesta
- [ ] Paquete usa umbrales KB: <40 basico, <70 avanzado, ≥70 premium
- [ ] Backwards compatible: funciona aunque diagnóstico no tenga nuevos campos
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- **No modificar el template HTML de propuesta** — solo la lógica
- **Mantener backwards compatibility** — si no hay score IA, funcionar igual que antes
- **Monetización por defecto** si no hay ROI calculator — mostrar pérdida aproximada

---

## Tabla de Monetización Completa (para implementar)

| Faltante KB | Impacto | Monetización | Asset |
|------------|---------|-------------|-------|
| `ssl` | HTTPS requerido | Posicionamiento Google afectado | Guía SSL |
| `schema_hotel` | Invisible para IA | 15-25% menos apariciones en IA | `hotel_schema` |
| `schema_reviews` | Sin estrellas | 8-12% menor CTR | `hotel_schema` |
| `LCP_ok` | >2500ms = lento | 53% abandono móvil | Guía LCP |
| `CLS_ok` | >0.1 = inestable | UX deficiente | Guía CLS |
| `contenido_extenso` | <300 palabras | SEO débil | Estrategia contenido |
| `open_graph` | Sin social | Menor compartición | Asset meta |
| `schema_faq` | Sin rich snippets | 10-15% menor visibilidad | `faq_page` |
| `nap_consistente` | Inconsistente | Desconfianza del usuario | Guía NAP |
| `imagenes_alt` | Sin alt text | IA no entiende imágenes | Asset optimización |
| `blog_activo` | Sin blog | Autoridad baja | Estrategia contenido |
| `redes_activas` | Sin redes | Señal secundaria | Recomendación social |
