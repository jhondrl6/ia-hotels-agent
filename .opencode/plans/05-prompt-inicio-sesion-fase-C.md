#FASE-C: Priorizacion Ponderada con Impacto Estimado

**ID**: FASE-C  
**Objetivo**: Reemplazar los porcentajes fijos (15%, 10%) de las brechas criticas por un modelo ponderado de 3 factores que justifique mejor el impacto en $ COP de cada oportunidad identificada.  
**Dependencias**: FASE-B ✅ (documentos pasan quality gate primero)  
**Duracion estimada**: 2-3 horas  
**Skill**: `phased_project_executor` v2.3.0

---

## Contexto

### Por que esta fase es necesaria

El diagnostico actual lista 4 brechas con pesos fijos:

```
BRECHA 1: FAQ Schema → $469.800 COP/mes (15%)
BRECHA 2: GBP incompleta → $469.800 COP/mes (15%)  
BRECHA 3: WhatsApp inconsistente → $313.200 COP/mes (10%)
BRECHA 4: Metadatos CMS → $313.200 COP/mes (10%)
```

Problemas:
- Los pesos son FIJOS, no derivados de datos del hotel
- El total es 50%, no 100% (el hotelero puede preguntar "¿y el otro 50%?")
- No hay justificacion de POR QUE 15% y no 20%
- El monto en $ es una derivacion del peso × total estimado, no una estimacion independiente

Esto debilita el argumento comercial. Un hotelero necesita saber: "¿que me conviene arreglar primero y cuantoo voy a recuperar?"

### Inspiracion

Patron adaptado de seomachine `opportunity_scorer.py`:
- 8 factores ponderados (volume 25%, position 20%, intent 20%, etc.)
- Traffic projection basado en CTR esperado por posicion

Para hoteles boutique, simplificamos a 3 factores con datos que YA TENEMOS del audit web.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-A | ⏳/✅ Pendiente o completada |
| FASE-B | ✅ Completada |

### Base Tecnica Disponible

- `modules/financial_engine/calculator_v2.py` — FinancialCalculatorV2, ya calcula montos
- `modules/financial_engine/no_defaults_validator.py` — Valida que no haya defaults en $
- `modules/commercial_documents/composer.py` — Genera diagnostico con brechas
- `data_models/canonical_assessment.py` — CanonicalAssessment con datos del hotel
- `modules/auditors/` — PageSpeed, Places, Rich Results, GBP audits (proveen datos de severidad)
- Competitor data de Places API/SerpAPI (proveen datos comparativos)
- Tests base: 1782 + 22 (FASE-B)

---

## Tareas

### Tarea 1: Crear Opportunity Scorer

**Objetivo**: Modelo ponderado que puntua cada brecha identificada con score 0-100.

**Archivos afectados**:
- `modules/financial_engine/opportunity_scorer.py` (NUEVO)

**Modelo de 3 Factores**:

```
FACTOR 1 — Severidad del Gap (0-40 pts)
  Criterio: Que tan grave es la brecha vs competencia
  Datos: audit web (schema detection), GBP audit, metadata validator
  
  40 pts: Brecha grave + competidor directo lo tiene resuelto
  30 pts: Brecha grave + competidor no lo tiene (pero deberia)
  20 pts: Brecha moderada
  10 pts: Brecha menor

  Ejemplo: "Sin FAQ Schema" cuando 3 de 5 competidores lo tienen → 40 pts
  Ejemplo: "Sin FAQ Schema" cuando nadie lo tiene → 25 pts

FACTOR 2 — Esfuerzo de Implementacion (0-30 pts)  
  Criterio: Que tan facil es para el hotelero implementar
  Datos: tipo de brecha + si ya existe asset generado
  
  30 pts: Ya tenemos el asset generado (solo instalar)
  25 pts: Requiere accion simple del hotelero (subir fotos)
  15 pts: Requiere accion tecnica moderada (modificar metadatos CMS)
  5 pts: Requiere acceso tecnico avanzado (cambiar tema WordPress)

  Ejemplo: FAQ Schema → 30 pts (ya generamos el JSON-LD)
  Ejemplo: GBP incompleta → 25 pts (hotelero sube fotos)

FACTOR 3 — Impacto en Conversion Directa (0-30 pts)
  Criterio: Que tan directamente afecta la reserva
  Datos: tipo de brecha + datos financieros
  
  30 pts: Reserva directa perdida (WhatsApp roto, sin boton reserva)
  25 pts: Visibilidad inmediata perdida (GBP sin fotos = no clickean)
  20 pts: SEO mediano plazo (rich snippets, metadatos)
  10 pts: SEO largo plazo (estructura de contenido)
  
  Ejemplo: WhatsApp inconsistente → 30 pts (reserva directa)
  Ejemplo: Metadatos CMS default → 20 pts (SEO)
```

**Estructura del modulo**:

```python
# modules/financial_engine/opportunity_scorer.py

@dataclass
class OpportunityScore:
    brecha_id: str
    brecha_name: str
    severity_score: float       # 0-40
    effort_score: float         # 0-30
    impact_score: float         # 0-30
    total_score: float          # 0-100
    estimated_monthly_cop: float
    justification: str          # Explicacion legible para el hotelero
    rank: int                   # 1 = prioridad mas alta
    
class OpportunityScorer:
    """Scores and ranks brechas by weighted model."""
    
    # Mapas de severidad por tipo de brecha
    BRECHA_SEVERITY_MAP = {
        "faq_schema_missing": {"base": 40, "competitor_factor": True},
        "gbp_incomplete": {"base": 30, "competitor_factor": True},
        "data_inconsistent": {"base": 35, "competitor_factor": False},
        "cms_defaults": {"base": 20, "competitor_factor": True},
    }
    
    # Mapas de esfuerzo por tipo de brecha
    BRECHA_EFFORT_MAP = {
        "faq_schema_missing": 30,   # Ya generamos el asset
        "gbp_incomplete": 25,       # Hotelero sube fotos
        "data_inconsistent": 20,    # Cambiar numero WhatsApp
        "cms_defaults": 15,         # Modificar metadatos
    }
    
    # Mapas de impacto por tipo de brecha
    BRECHA_IMPACT_MAP = {
        "faq_schema_missing": 20,   # Rich snippets (mediano plazo)
        "gbp_incomplete": 25,       # Visibilidad local inmediata
        "data_inconsistent": 30,    # Reserva directa perdida
        "cms_defaults": 20,         # SEO
    }
    
    def score_brechas(self, brechas: list, assessment: 'CanonicalAssessment', 
                      competitor_data: dict = None) -> List[OpportunityScore]:
        """Score and rank all brechas."""
        scores = []
        for brecha in brechas:
            severity = self._calc_severity(brecha, competitor_data)
            effort = self._calc_effort(brecha)
            impact = self._calc_impact(brecha)
            total = severity + effort + impact
            monthly_cop = self._estimate_monthly_impact(total, assessment)
            justification = self._generate_justification(brecha, severity, effort, impact)
            scores.append(OpportunityScore(...))
        
        # Sort by total_score descending, assign ranks
        scores.sort(key=lambda s: s.total_score, reverse=True)
        for i, s in enumerate(scores, 1):
            s.rank = i
        
        return scores
    
    def _estimate_monthly_impact(self, score: float, assessment) -> float:
        """Estimate COP impact based on score and hotel financials."""
        # Si hay datos financieros reales (ADR, occupancy), usarlos
        # Si no, usar estimacion regional del benchmark
        # score/100 × opportunity_pool = monthly COP
        pass
    
    def _generate_justification(self, brecha, severity, effort, impact) -> str:
        """Generate human-readable justification for hotelero."""
        # Ejemplo: "WhatsApp muestra numero diferente en Google vs web. 
        #           Clientes confundidos no completan reserva. 
        #           Solucion: unificar numero (2 min). 
        #           Impacto: reservas directas recuperadas."
        pass
```

**Criterios de aceptacion**:
- [ ] Cada brecha recibe score 0-100 desglosado en 3 factores
- [ ] Brechas se rankean por score total
- [ ] Monto en $ COP se estima desde score (no al reves)
- [ ] Justificacion legible para hotelero no tecnico
- [ ] Backward compatible: sin scorer = pesos fijos actuales

### Tarea 2: Integrar en Canonical Assessment

**Objetivo**: Agregar opportunity_scores al modelo de datos para que fluya por todo el pipeline.

**Archivos afectados**:
- `data_models/canonical_assessment.py` (MODIFICAR)

**Cambios**:
```python
# Agregar campo opcional
opportunity_scores: Optional[List[OpportunityScore]] = None
```

**Criterios de aceptacion**:
- [ ] Campo existe en CanonicalAssessment
- [ ] Es opcional (backward compatible)
- [ ] No rompe serializacion/deserializacion existente

### Tarea 3: Integrar en Composer

**Objetivo**: El diagnostico usa opportunity scores en vez de porcentajes fijos.

**Archivos afectados**:
- `modules/commercial_documents/composer.py` (MODIFICAR)

**Cambios en la seccion de brechas**:

```
ANTES:
  BRECHA 1: FAQ Schema → 15% → $469.800 COP/mes

DESPUES:
  BRECHA 1: FAQ Schema → Score 85/100
    ├ Severidad: 35/40 (competidores lo tienen)
    ├ Facilidad: 30/30 (asset ya generado, solo instalar)  
    ├ Impacto: 20/30 (rich snippets, mediano plazo)
    └ Recuperacion estimada: $532.400 COP/mes
    "Sin Schema FAQ, Google no muestra sus preguntas en resultados. 
     3 de 5 competidores en Santa Rosa de Cabal ya lo tienen."
```

**Criterios de aceptacion**:
- [ ] Diagnostico muestra score por brecha con desglose
- [ ] Justificacion usa datos reales del hotel (ciudad, competidores)
- [ ] Si opportunity_scorer no disponible, fallback a pesos fijos
- [ ] El monto total sigue siendo coherente con el financial_engine

### Tarea 4: Integrar en Calculator

**Objetivo**: Calculator usa scores del opportunity_scorer para pesos dinamicos.

**Archivos afectados**:
- `modules/financial_engine/calculator_v2.py` (MODIFICAR)

**Cambios**:
- Si `assessment.opportunity_scores` existe, usar `score.total_score/100` como peso
- Si no existe, usar pesos fijos actuales (backward compatible)

**Criterios de aceptacion**:
- [ ] Pesos dinamicos cuando opportunity_scores disponible
- [ ] Fallback a pesos fijos cuando no
- [ ] No rompe no_defaults_validator (montos siguen siendo no-default)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| Test severity con competidores | `tests/financial_engine/test_opportunity_scorer.py` | 40 pts cuando competidores lo tienen |
| Test severity sin competidores | `tests/financial_engine/test_opportunity_scorer.py` | 20-25 pts cuando nadie lo tiene |
| Test effort FAQ | `tests/financial_engine/test_opportunity_scorer.py` | 30 pts (asset ya generado) |
| Test effort GBP | `tests/financial_engine/test_opportunity_scorer.py` | 25 pts (hotelero sube fotos) |
| Test impact WhatsApp | `tests/financial_engine/test_opportunity_scorer.py` | 30 pts (reserva directa) |
| Test total score range | `tests/financial_engine/test_opportunity_scorer.py` | 0-100 siempre |
| Test ranking | `tests/financial_engine/test_opportunity_scorer.py` | Ordenado desc por score |
| Test COP estimation | `tests/financial_engine/test_opportunity_scorer.py` | Monto > 0 cuando score > 0 |
| Test justification | `tests/financial_engine/test_opportunity_scorer.py` | String legible no vacio |
| Test backward compat | `tests/financial_engine/test_opportunity_scorer.py` | Sin scores = pesos fijos |
| Test composer con scores | `tests/financial_engine/test_opportunity_scorer.py` | Diagnostico muestra desglose |
| Test composer sin scores | `tests/financial_engine/test_opportunity_scorer.py` | Diagnostico usa pesos fijos |
| Test calculator dynamic | `tests/financial_engine/test_opportunity_scorer.py` | Pesos dinamicos con scores |
| Test calculator fallback | `tests/financial_engine/test_opportunity_scorer.py` | Pesos fijos sin scores |

**Comando de validacion**:
```bash
python -m pytest tests/financial_engine/test_opportunity_scorer.py -v
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`** — Marcar FASE-A como ✅ Completada
2. **`06-checklist-implementacion.md`** — Marcar todos los items de FASE-A como ✅
3. **`09-documentacion-post-proyecto.md`** — Secciones A, B, D, E
4. **Ejecutar**: `python scripts/log_phase_completion.py --fase FASE-A --desc "Priorizacion Ponderada con Impacto Estimado" --archivos-nuevos "modules/financial_engine/opportunity_scorer.py,tests/financial_engine/test_opportunity_scorer.py" --archivos-mod "data_models/canonical_assessment.py,modules/commercial_documents/composer.py,modules/financial_engine/calculator_v2.py" --tests "14" --check-manual-docs`

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: 14/14 tests
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa
- [ ] **Sin regresiones**: Tests existentes siguen pasando
- [ ] **Prueba real**: Diagnostico muestra scores ponderados con justificacion
- [ ] **Backward compatible**: Sin opportunity_scorer = comportamiento actual
- [ ] **dependencias-fases.md actualizado**
- [ ] **Documentacion afiliada**: CHANGELOG.md actualizado
- [ ] **Post-ejecucion completada**: log_phase_completion.py ejecutado

---

## Restricciones

- NO modificar `document_quality_gate.py` ni `content_scrubber.py` (eso es FASE-B)
- NO agregar APIs externas (eso es FASE-B con GSC)
- Los scores deben poder calcularse con datos que YA TENEMOS del audit web
- Las justificaciones deben estar en espanol neutro, no tecnico
- El monto en $ COP debe pasar `no_defaults_validator`

---

## Prompt de Ejecucion

```
Actua como desarrollador Python senior especializado en modelos de scoring y priorizacion.

OBJETIVO: Implementar FASE-A — Opportunity Scorer con modelo ponderado de 3 factores.

CONTEXTO:
- Proyecto: iah-cli v4.22.0+ (FASE-B completada)
- Problema: Brechas del diagnostico usan porcentajes fijos sin justificacion
- Modelo: Severidad(0-40) + Esfuerzo(0-30) + Impacto(0-30) = Score 0-100
- Datos disponibles: audit web, GBP audit, competitor data, financial_engine

TAREAS:
1. Crear modules/financial_engine/opportunity_scorer.py (OpportunityScore dataclass + OpportunityScorer)
2. Modificar data_models/canonical_assessment.py (campo opportunity_scores)
3. Modificar modules/commercial_documents/composer.py (inyectar scores en brechas)
4. Modificar modules/financial_engine/calculator_v2.py (pesos dinamicos)
5. Crear 14 tests en tests/financial_engine/test_opportunity_scorer.py

CRITERIOS:
- Score 0-100 desglosado en 3 factores
- Ranking automatico por score
- Justificacion legible en espanol para hotelero
- Backward compatible (sin scorer = pesos fijos)
- Monto COP pasa no_defaults_validator

VALIDACIONES:
- pytest tests/financial_engine/test_opportunity_scorer.py -v (14/14)
- python scripts/run_all_validations.py --quick
```
