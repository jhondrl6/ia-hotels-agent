# FASE-B: Document Quality Gate + Content Scrubber

**ID**: FASE-B  
**Objetivo**: Implementar validacion de calidad post-generacion y limpieza de contenido LLM para documentos comerciales (diagnostico y propuesta). Prevenir que documentos con errores visibles ("default", "COP COP", portugues mezclado) lleguen al cliente.  
**Dependencias**: Ninguna obligatoria. FASE-A es nice-to-have.  
**Duracion estimada**: 2-3 horas  
**Skill**: `phased_project_executor` v2.3.0

---

## Contexto

### Por que esta fase es necesaria

El analisis del diagnostico generado para Hotel Visperas revelo errores que un hotelero percibe inmediatamente:

- Linea 21: `Lo que esta pasando en default` — la ciudad NO se resolvio
- Linea 58: `$3.132.000 COP COP` — moneda duplicada
- Linea 92: `Con 0% de confianza en el analisis` — destruye credibilidad comercial
- Linea 120: `PROXIMO PASSO` — portugues mezclado con espanol
- Linea 116: `siguiente generacion de guests` — ingles mezclado

Estos errores NO son de datos (el coherence score paso 0.87). Son de GENERACION DE TEXTO. El LLM genera el contenido y se entrega sin revision. Un hotelero lee "default" 5 veces y piensa "esto es generico, no es para mi hotel".

### Inspiracion

Patron adaptado de TheCraigHewitt/seomachine:
- `content_scorer.py` → 5 dimensiones de calidad con auto-revision
- `content_scrubber.py` → Eliminacion de watermarks AI, em-dashes, unicode invisible

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-A | ⏳ Pendiente (no bloquea esta fase) |

### Base Tecnica Disponible

- `modules/asset_generation/asset_content_validator.py` — YA EXISTE con deteccion de placeholders. **DEBE EXTENDERSE** con:
  - Deteccion de "default" como valor de region
  - Deteccion de "COP COP" (moneda duplicada)
  - Deteccion de idioma mezclado (portugues/ingles en documento espanol)
  - Deteccion de "0% de confianza" en documentos comerciales
- `modules/quality_gates/publication_gates.py` — YA EXISTE con 5 gates. **AGREGAR** gate #6: content_quality_gate
- `modules/commercial_documents/coherence_validator.py` — Valida coherencia entre documentos (NO calidad de texto)
- Tests base: 1782 funciones

### Lo que ya existe y NO se toca

- `AssetContentValidator` tiene `PLACEHOLDER_PATTERNS` y `GENERIC_PHRASES` — solo se EXTENDEN
- `PublicationGatesOrchestrator` ya orquesta gates — solo se AGREGA uno nuevo
- El flujo v4complete en `main.py` ya tiene punto de inyeccion pre-delivery

---

## Tareas

### Tarea 1: Crear Document Quality Gate

**Objetivo**: Nuevo modulo que valida documentos comerciales ANTES de entrega al cliente.

**Archivos afectados**:
- `modules/postprocessors/__init__.py` (NUEVO)
- `modules/postprocessors/document_quality_gate.py` (NUEVO)

**Estructura del modulo**:

```python
# modules/postprocessors/document_quality_gate.py

@dataclass
class DocumentQualityIssue:
    check_name: str       # "placeholder_region", "duplicate_currency", "mixed_language"
    severity: str         # "blocker", "warning"
    line_number: int
    detected_value: str
    message: str
    auto_fixable: bool    # True si el scrubber puede resolverlo

@dataclass  
class DocumentQualityResult:
    passed: bool
    score: float          # 0.0 - 1.0 (1.0 = sin issues)
    issues: List[DocumentQualityIssue]
    document_type: str    # "diagnostico", "propuesta", "asset"
    
class DocumentQualityGate:
    """Validates commercial documents before client delivery."""
    
    BLOCKER_CHECKS = [
        "placeholder_region",      # "default" donde deberia haber ciudad
        "duplicate_currency",      # "COP COP" 
        "zero_confidence",         # "0% confianza" en documento comercial
    ]
    
    WARNING_CHECKS = [
        "mixed_language",          # Portugues o ingles en doc espanol
        "generic_ai_phrases",      # Frases tipicas de LLM
        "missing_contact_info",    # Placeholders en contacto
    ]
    
    def validate_document(self, content: str, doc_type: str, hotel_data: dict) -> DocumentQualityResult:
        """Run all checks and return result."""
        # 1. Check placeholders de region ("default" donde deberia haber datos)
        # 2. Check duplicacion de moneda ("COP COP")  
        # 3. Check confianza baja explicita ("0% confianza")
        # 4. Check idioma mezclado (portugues/ingles)
        # 5. Check frases genericas AI
        # Retorna passed=False si algun BLOCKER_CHECK falla
```

**Criterios de aceptacion**:
- [ ] Detecta "default" como valor de region (no como palabra comun en codigo)
- [ ] Detecta "COP COP" como moneda duplicada
- [ ] Detecta "0% de confianza" en contexto comercial
- [ ] Detecta palabras portuguesas comunes: "passo", "protecao", "complicated"
- [ ] Retorna `passed=False` si hay blocker issues
- [ ] Retorna `passed=True` si solo hay warnings
- [ ] Cada issue indica si es auto-fixable por el scrubber

### Tarea 2: Crear Content Scrubber

**Objetivo**: Post-procesador que corrige automaticamente los issues detectados por el Quality Gate.

**Archivos afectados**:
- `modules/postprocessors/content_scrubber.py` (NUEVO)

**Estructura del modulo**:

```python
# modules/postprocessors/content_scrubber.py

class ContentScrubber:
    """Post-processor that fixes common LLM output issues."""
    
    def scrub(self, content: str, hotel_data: dict, doc_type: str) -> ScrubResult:
        """Apply all scrubbing rules. Idempotent (safe to run repeatedly)."""
        content = self._fix_region_placeholders(content, hotel_data)
        content = self._fix_duplicate_currency(content)
        content = self._fix_confidence_statement(content, doc_type)
        content = self._fix_mixed_language(content)
        content = self._fix_generic_ai_phrases(content, hotel_data)
        return ScrubResult(original=..., scrubbed=content, fixes_applied=[...])
    
    # REGLA 1: Reemplazar "default" con ciudad/region real del hotel
    def _fix_region_placeholders(self, content, hotel_data):
        # Si hotel_data tiene city="Santa Rosa de Cabal", state="Risaralda"
        # Reemplazar "en default" → "en Santa Rosa de Cabal"
        # Reemplazar "region de default" → "region del Eje Cafetero"
        # NO reemplazar "default" en contexto tecnico (ej: "valor por defecto")
        
    # REGLA 2: Eliminar duplicacion de moneda
    def _fix_duplicate_currency(self, content):
        # "$X COP COP" → "$X COP"
        # "$X.XXX.XXX COP COP" → "$X.XXX.XXX COP"
        
    # REGLA 3: Corregir declaracion de confianza en documentos comerciales
    def _fix_confidence_statement(self, content, doc_type):
        # En diagnostico/propuesta: "0% de confianza" → 
        #   "estimacion basada en datos web disponibles. Para mayor precision, 
        #    configure GA4 y Google Search Console"
        # NO alterar en documentos tecnicos internos
        
    # REGLA 4: Corregir idioma mezclado
    def _fix_mixed_language(self, content):
        # "PRÓXIMO PASSO" → "PRÓXIMO PASO"
        # "Proteção" → "Protección"
        # "guests" → "huéspedes" (en contexto hotelero)
        # Diccionario de reemplazos portugues→espanol
        # Diccionario de reemplazos ingles→espanol (solo en contexto hotelero)
        
    # REGLA 5: Suavizar frases genericas AI
    def _fix_generic_ai_phrases(self, content, hotel_data):
        # "oportunidades de crecimiento en presencia digital hotelera" →
        #   frase concreta con datos del hotel
        # "cada vez mas competitivo" → 
        #   dato especifico de la region
```

**Criterios de aceptacion**:
- [ ] Es idempotente: ejecutar 2 veces produce el mismo resultado que 1 vez
- [ ] Reemplaza "default" con datos reales del hotel (city, state, region)
- [ ] Elimina "COP COP" → "COP"
- [ ] Reemplaza "0% confianza" con texto comercial aceptable
- [ ] Convierte portugues→espanol con diccionario de ~20 palabras comunes
- [ ] No altera contenido tecnico valido (ej: "valor por defecto" no se toca)

### Tarea 3: Integrar en Publication Gates

**Objetivo**: Agregar el quality gate como gate #6 en el sistema de publication gates existente.

**Archivos afectados**:
- `modules/quality_gates/publication_gates.py` (MODIFICAR)
- `modules/asset_generation/asset_content_validator.py` (MODIFICAR)

**Cambios en publication_gates.py**:
- Importar `DocumentQualityGate`
- Agregar funcion `content_quality_gate(assessment, config)` que retorna `PublicationGateResult`
- Agregar al orquestador como gate #6 (despues de `critical_recall_gate`)
- Este gate es BLOQUEANTE: si el documento tiene blockers, no se publica

**Cambios en asset_content_validator.py**:
- Agregar `"default"` a `PLACEHOLDER_PATTERNS` como regex: `r'\ben\s+default\b'` (solo en contexto regional)
- Agregar `"COP COP"` a `PLACEHOLDER_PATTERNS` como regex: `r'COP\s*COP'`

**Criterios de aceptacion**:
- [ ] `content_quality_gate` es gate #6 en `PublicationGatesOrchestrator`
- [ ] Gate es BLOQUEANTE (FAILED si hay blockers)
- [ ] Gate pasa con warnings (no bloquea por warnings solos)
- [ ] `AssetContentValidator` detecta "default" y "COP COP"
- [ ] Tests existentes de publication gates siguen pasando

### Tarea 4: Integrar en flujo v4complete

**Objetivo**: El scrubber se ejecuta automaticamente despues de generar documentos comerciales y ANTES de empaquetar delivery.

**Archivos afectados**:
- `main.py` (MODIFICAR en la seccion de v4complete donde se generan documentos)

**Punto de inyeccion**: Despues de `composer.generate_diagnostico()` y `composer.generate_propuesta()`, ANTES de `DeliveryPackager.create_package()`.

**Logica**:
```python
# 1. Generar documentos (ya existe)
diagnostico = composer.generate_diagnostico(assessment, ...)
propuesta = composer.generate_propuesta(assessment, ...)

# 2. NUEVO: Scrub (limpiar)
scrubber = ContentScrubber()
diagnostico = scrubber.scrub(diagnostico, hotel_data, "diagnostico").scrubbed
propuesta = scrubber.scrub(propuesta, hotel_data, "propuesta").scrubbed

# 3. NUEVO: Quality Gate (validar)
gate = DocumentQualityGate()
diag_result = gate.validate_document(diagnostico, "diagnostico", hotel_data)
prop_result = gate.validate_document(propuesta, "propuesta", hotel_data)

# 4. Si gate falla, log warnings (no bloquear flujo completo, pero alertar)
if not diag_result.passed:
    logger.warning(f"Document quality issues: {[i.message for i in diag_result.issues if i.severity == 'blocker']}")

# 5. Continuar con delivery (ya existe)
packager = DeliveryPackager()
```

**Criterios de aceptacion**:
- [ ] Scrubber se ejecuta automaticamente en v4complete
- [ ] Quality gate se ejecuta despues del scrubber
- [ ] Blockers se loguean como WARNING
- [ ] El flujo NO se bloquea por issues (se loguea y continua)
- [ ] Los fixes aplicados se registran en el metadata del delivery

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| Test placeholder region | `tests/postprocessors/test_document_quality_gate.py` | Detecta "en default" como blocker |
| Test duplicate currency | `tests/postprocessors/test_document_quality_gate.py` | Detecta "COP COP" como blocker |
| Test zero confidence | `tests/postprocessors/test_document_quality_gate.py` | Detecta "0% confianza" como blocker |
| Test mixed language pt | `tests/postprocessors/test_document_quality_gate.py` | Detecta "passo", "protecao" como warning |
| Test mixed language en | `tests/postprocessors/test_document_quality_gate.py` | Detecta "guests" como warning |
| Test clean document | `tests/postprocessors/test_document_quality_gate.py` | Retorna passed=True sin issues |
| Test scrubber region fix | `tests/postprocessors/test_content_scrubber.py` | Reemplaza "default" con ciudad real |
| Test scrubber currency fix | `tests/postprocessors/test_content_scrubber.py` | "COP COP" → "COP" |
| Test scrubber confidence fix | `tests/postprocessors/test_content_scrubber.py` | Reemplaza "0% confianza" con texto comercial |
| Test scrubber language fix | `tests/postprocessors/test_content_scrubber.py` | "PASSO" → "PASO" |
| Test scrubber idempotent | `tests/postprocessors/test_content_scrubber.py` | 2 ejecuciones = mismo resultado |
| Test scrubber no over-fix | `tests/postprocessors/test_content_scrubber.py` | No altera "valor por defecto" |

**Comando de validacion**:
```bash
python -m pytest tests/postprocessors/ -v
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`** — Marcar FASE-B como ✅ Completada
2. **`06-checklist-implementacion.md`** — Marcar todos los items de FASE-B como ✅
3. **`09-documentacion-post-proyecto.md`** — Secciones A (modulos nuevos), D (metricas), E (afiliados)
4. **Ejecutar**: `python scripts/log_phase_completion.py --fase FASE-B --desc "Document Quality Gate + Content Scrubber" --archivos-nuevos "modules/postprocessors/__init__.py,modules/postprocessors/document_quality_gate.py,modules/postprocessors/content_scrubber.py,tests/postprocessors/test_document_quality_gate.py,tests/postprocessors/test_content_scrubber.py" --archivos-mod "modules/quality_gates/publication_gates.py,modules/asset_generation/asset_content_validator.py,main.py" --tests "22" --check-manual-docs`

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: 22/22 tests en tests/postprocessors/
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa 4/4
- [ ] **Sin regresiones**: Tests existentes (1782 funciones) siguen pasando
- [ ] **Prueba real**: Generar diagnostico para Hotel Visperas y verificar que NO contiene "default", "COP COP", "0% confianza", portugues
- [ ] **dependencias-fases.md actualizado**
- [ ] **Documentacion afiliada**: CHANGELOG.md actualizado con entrada FASE-B
- [ ] **Post-ejecucion completada**: log_phase_completion.py ejecutado

---

## Restricciones

- NO modificar `coherence_validator.py` (valida coherencia entre docs, no calidad de texto)
- NO modificar el `financial_engine` (eso es FASE-A)
- NO agregar dependencias externas nuevas (solo stdlib + lo que ya existe)
- El scrubber debe ser SEGURO: nunca alterar datos financieros validos
- El gate no debe ser tan estricto que bloquee flujos legitimos
- Los diccionarios de reemplazo (pt→es, en→es) deben ser CONTEXTUALES (solo hotelero)

---

## Prompt de Ejecucion

```
Actua como desarrollador Python senior especializado en calidad de contenido y post-procesamiento.

OBJETIVO: Implementar FASE-B — Document Quality Gate + Content Scrubber para iah-cli.

CONTEXTO:
- Proyecto: iah-cli v4.22.0 (CLI de diagnostico hotelero)
- Problema: Documentos comerciales generados por LLM contienen errores visibles
- Modulos existentes: AssetContentValidator, PublicationGatesOrchestrator, CoherenceValidator
- Tests base: 1782 funciones

TAREAS:
1. Crear modules/postprocessors/__init__.py
2. Crear modules/postprocessors/document_quality_gate.py (3 blocker checks + 2 warning checks)
3. Crear modules/postprocessors/content_scrubber.py (5 reglas de limpieza, idempotente)
4. Modificar modules/quality_gates/publication_gates.py (agregar gate #6)
5. Modificar modules/asset_generation/asset_content_validator.py (agregar patterns)
6. Integrar en main.py flujo v4complete (scrub → validate → log → delivery)
7. Crear 22 tests en tests/postprocessors/

CRITERIOS:
- "default" detectado y reemplazado con datos reales del hotel
- "COP COP" eliminado
- "0% confianza" reemplazado con texto comercial aceptable
- Portugues/ingles en documento espanol detectado y corregido
- Scrubber idempotente
- Sin regresiones en 1782 tests existentes

VALIDACIONES:
- pytest tests/postprocessors/ -v (22/22 passing)
- python scripts/run_all_validations.py --quick
- Generar diagnostico de prueba y verificar limpieza
```
