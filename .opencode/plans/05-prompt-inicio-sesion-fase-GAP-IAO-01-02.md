# GAP-IAO-01-02: Diagnóstico con KB + Pain ID Alignment + Cierre de Desconexiones

**ID**: GAP-IAO-01-02
**Objetivo**: Implementar scoring KB Y cerrar las 5 desconexiones identificadas en pre-análisis
**Dependencias**: GAP-IAO-01-00 (auditoría runtime)
**Duración estimada**: 3-4 horas
**Skills**: test-driven-development, systematic-debugging
**Documento de soporte**: `00-PRE-GAP-01-02-ANALISIS-DESCONEXIONES-v3.md` — leer ANTES de implementar

---

## Contexto

### Hallazgos de Auditoría Runtime (GAP-IAO-01-00)

**Solo 5 de 12 elementos CHECKLIST_IAO se detectan con el audit actual:**

| Elemento KB | Detector | Peso |
|---|---|---|
| schema_hotel | `schema.hotel_schema_detected` ✅ | 15 |
| schema_reviews | `bool(gbp.rating)` como proxy ⚠️ | 15 |
| LCP_ok | `performance.lcp <= 2.5` ✅ | 10 |
| CLS_ok | `performance.cls <= 0.1` ✅ | 5 |
| schema_faq | `schema.faq_schema_detected` ✅ | 8 |
| nap_consistente | Solo WhatsApp ⚠️ | 7 |
| ssl |默认值 `url.startswith('https')` ✅ | 10 |
| contenido_extenso |默认值 `False` ❌ | 10 |
| open_graph |默认值 `False` ❌ | 5 |
| imagenes_alt |默认值 `False` ❌ | 5 |
| blog_activo |默认值 `False` ❌ | 5 |
| redes_activas |默认值 `False` ❌ | 5 |

### Desconexiones Identificadas (documentadas en `00-PRE-GAP-01-02-ANALISIS-DESCONEXIONES-v3.md`)

| # | Desconexión | Solución |
|---|-------------|----------|
| 1 | No existe `FALTANTE_TO_PAIN_ID_MAP` | Crear constante en `v4_diagnostic_generator.py` |
| 2 | `score_ia` usa `str` en vez de `int` | Cambiar a `Optional[int]` con `-1` para N/A |
| 3 | 6 pain_ids nuevos no existen en mapper | Agregar a `PAIN_SOLUTION_MAP` |
| 4 | 5 assets nuevos no existen en `ASSET_CATALOG` | Agregar como `MISSING` |
| 5 | Mezcla de `brechas` vs `faltantes` | Documentar separación explícita |

---

## Arquitectura Final — Flujo Completo

```
AUDIT RESULT
    │
    ├── _identify_brechas() ──────────────→ 4 brechas comerciales (brechas[])
    │   └── Cada brecha tiene: nombre, impacto, detalle, pain_id
    │
    ├── _extraer_elementos_de_audit() ───→ 12 elementos KB (faltantes[])
    │   └── 5 extraídos reales + 7默认值 (False)
    │
    ├── calcular_cumplimiento(faltantes) ─→ score_tecnico (int 0-100)
    │
    ├── _asset_para_pain(pain_id) ───────→ Filtro: solo assets IMPLEMENTED
    │   └── Si asset es MISSING → pain_id NO pasa a DiagnosticSummary
    │
    └── DiagnosticSummary(
        score_tecnico=int,        # 0-100
        score_ia=Optional[int],   # None=sin datos, -1=error, >=0=score real
        paquete=str,              # "basico" | "avanzado" | "premium"
        faltantes=List[str],      # TODOS los 12 elementos KB que fallan
        pain_ids=List[str],       # SOLO los que tienen asset IMPLEMENTED
    )
```

**VALIDACIÓN**: `pain_ids` solo contiene pain_ids cuyo asset principal es `IMPLEMENTED`. Los assets `MISSING` (ssl_guide, og_tags_guide, alt_text_guide, blog_strategy_guide, social_strategy_guide) son visibles en scoring pero NO se monetizan ni se prometen al cliente.

---

## Tareas (Orden de ejecución OBLIGATORIO)

### FASE A: Preparar datos de soporte

**Tarea A1: Crear `ELEMENTO_KB_TO_PAIN_ID` en `v4_diagnostic_generator.py`**

**Ubicación**: Al inicio del archivo, después de los imports.

```python
# ============================================================
# ELEMENTO_KB_TO_PAIN_ID — ÚNICA FUENTE DE VERDAD
# Conecta cada elemento del CHECKLIST_IAO (KB) con su pain_id
# y el asset que lo resuelve.
# Sincronizar con:
#   - PainSolutionMapper.PAIN_SOLUTION_MAP
#   - ASSET_CATALOG
# ============================================================

ELEMENTO_KB_TO_PAIN_ID: Dict[str, tuple] = {
    # Elemento KB: (pain_id, asset_principal, asset_secundario)
    # CORREGIDO v3: schema_reviews → no_schema_reviews (no missing_reviews)
    "ssl":                ("no_ssl",              "ssl_guide",           None),
    "schema_hotel":      ("no_hotel_schema",     "hotel_schema",        None),
    "schema_reviews":     ("no_schema_reviews",   "hotel_schema",        None),  # ANTES: missing_reviews
    "LCP_ok":             ("poor_performance",    "performance_audit",   "optimization_guide"),
    "CLS_ok":             ("poor_performance",    "optimization_guide",  None),
    "contenido_extenso":  ("low_citability",      "optimization_guide",  None),
    "open_graph":         ("no_og_tags",          "og_tags_guide",       None),
    "schema_faq":         ("no_faq_schema",       "faq_page",            None),
    "nap_consistente":    ("whatsapp_conflict",   "whatsapp_button",     None),
    "imagenes_alt":       ("missing_alt_text",    "alt_text_guide",      None),
    "blog_activo":        ("no_blog_content",     "blog_strategy_guide", None),
    "redes_activas":      ("no_social_links",     "social_strategy_guide", None),
}

ELEMENTOS_MONETIZABLES: set = {
    elem for elem, (_, asset, _) in ELEMENTO_KB_TO_PAIN_ID.items()
    if asset is not None
}
```

### FASE B: Modificar PainSolutionMapper

**Tarea B1: Agregar 5 pain_ids faltantes a `PAIN_SOLUTION_MAP`**

**Archivo**: `modules/commercial_documents/pain_solution_mapper.py`

**Nota**: `poor_performance` YA EXISTE. Solo agregar los 5 nuevos.

```python
# AGREGAR DESPUÉS de "no_social_links" (línea ~188):

# === ELEMENTOS KB CON DEFAULT (GAP-IAO-01-02) ===
"no_ssl": {
    "assets": ["ssl_guide"],
    "confidence_required": 0.0,
    "priority": 1,
    "validation_fields": ["ssl_detected"],
    "estimated_impact": "high",
    "name": "Sin SSL/HTTPS",
    "description": "El sitio no tiene certificado SSL o no fuerza HTTPS"
},
"no_og_tags": {
    "assets": ["og_tags_guide"],
    "confidence_required": 0.0,
    "priority": 2,
    "validation_fields": ["og_tags_detected"],
    "estimated_impact": "medium",
    "name": "Sin Open Graph Tags",
    "description": "Faltan meta tags de Open Graph para redes sociales"
},
"missing_alt_text": {
    "assets": ["alt_text_guide"],
    "confidence_required": 0.0,
    "priority": 3,
    "validation_fields": ["alt_text_detected"],
    "estimated_impact": "medium",
    "name": "Imágenes sin Texto Alternativo",
    "description": "Las imágenes no tienen atributo alt descriptivo"
},
"no_blog_content": {
    "assets": ["blog_strategy_guide"],
    "confidence_required": 0.0,
    "priority": 3,
    "validation_fields": ["blog_detected"],
    "estimated_impact": "low",
    "name": "Blog Inactivo",
    "description": "No se detecta blog activo en el sitio"
},
"no_social_links": {
    "assets": ["social_strategy_guide"],
    "confidence_required": 0.0,
    "priority": 3,
    "validation_fields": ["social_links_detected"],
    "estimated_impact": "low",
    "name": "Sin Presencia en Redes Sociales",
    "description": "No se detectan enlaces a redes sociales"
},
"low_content_length": {
    "assets": ["optimization_guide"],
    "confidence_required": 0.0,
    "priority": 2,
    "validation_fields": ["content_length"],
    "estimated_impact": "medium",
    "name": "Contenido Muy Corto",
    "description": "El contenido es demasiado corto para ser citado por IA"
},
```

### FASE C: Modificar ASSET_CATALOG

**Tarea C1: Agregar 5 assets como MISSING**

**Archivo**: `modules/asset_generation/asset_catalog.py`

```python
# AGREGAR ANTES de la línea `def is_asset_implemented` (~línea 213):
# === MISSING ASSETS (GAP-IAO-01-02) ===
"ssl_guide": AssetCatalogEntry(
    asset_type="ssl_guide",
    template="ssl_guide_template.md",
    output_name="{prefix}guia_ssl{suffix}.md",
    required_field="ssl_detected",
    required_confidence=0.0,
    fallback="generate_ssl_checklist",
    block_on_failure=False,
    status=AssetStatus.MISSING,
    promised_by=["no_ssl"]
),
"og_tags_guide": AssetCatalogEntry(
    asset_type="og_tags_guide",
    template="og_tags_guide_template.md",
    output_name="{prefix}guia_og_tags{suffix}.md",
    required_field="og_tags_detected",
    required_confidence=0.0,
    fallback="generate_og_tags_checklist",
    block_on_failure=False,
    status=AssetStatus.MISSING,
    promised_by=["no_og_tags"]
),
"alt_text_guide": AssetCatalogEntry(
    asset_type="alt_text_guide",
    template="alt_text_guide_template.md",
    output_name="{prefix}guia_alt_text{suffix}.md",
    required_field="alt_text_detected",
    required_confidence=0.0,
    fallback="generate_alt_text_checklist",
    block_on_failure=False,
    status=AssetStatus.MISSING,
    promised_by=["missing_alt_text"]
),
"blog_strategy_guide": AssetCatalogEntry(
    asset_type="blog_strategy_guide",
    template="blog_strategy_template.md",
    output_name="{prefix}estrategia_blog{suffix}.md",
    required_field="blog_detected",
    required_confidence=0.0,
    fallback="generate_blog_strategy",
    block_on_failure=False,
    status=AssetStatus.MISSING,
    promised_by=["no_blog_content"]
),
"social_strategy_guide": AssetCatalogEntry(
    asset_type="social_strategy_guide",
    template="social_strategy_template.md",
    output_name="{prefix}estrategia_social{suffix}.md",
    required_field="social_links_detected",
    required_confidence=0.0,
    fallback="generate_social_strategy",
    block_on_failure=False,
    status=AssetStatus.MISSING,
    promised_by=["no_social_links"]
),
```

### FASE D: Modificar DiagnosticSummary

**Tarea D1: Agregar 5 campos KB a `DiagnosticSummary`**

**Archivo**: `modules/commercial_documents/data_structures.py`

```python
@dataclass
class DiagnosticSummary:
    """Summary of diagnostic for proposal generation.
    
    Atributos KB (GAP-IAO-01-02):
        score_tecnico: Score 0-100 del CHECKLIST_IAO (calcular_cumplimiento)
        score_ia: None=sin datos, -1=error, >=0=score real de IATester
        paquete: "basico" (<40), "avanzado" (40-69), "premium" (>=70)
        faltantes: Lista de elementos KB que fallan
        pain_ids: Lista de pain_ids desde brechas[] (conecta con PainSolutionMapper)
    """
    hotel_name: str
    critical_problems_count: int
    quick_wins_count: int
    overall_confidence: ConfidenceLevel
    top_problems: List[str] = field(default_factory=list)
    validated_data_summary: Dict[str, Any] = field(default_factory=dict)
    coherence_score: Optional[float] = None
    # === CAMPOS KB (GAP-IAO-01-02) ===
    score_tecnico: Optional[int] = None   # 0-100, None si sin datos
    score_ia: Optional[int] = None        # None=sin intentarlo, -1=error, >=0=score
    paquete: Optional[str] = None          # "basico" | "avanzado" | "premium" | None
    faltantes: Optional[List[str]] = None  # Elementos KB que fallan (e.g. ["ssl", "open_graph"])
    pain_ids: Optional[List[str]] = None  # Pain IDs de brechas[] para PainSolutionMapper
```

### FASE E: Implementar lógica de scoring

**Tarea E1: Implementar `calcular_cumplimiento()` y `sugerir_paquete()`**

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

```python
def calcular_cumplimiento(elementos: dict) -> int:
    """
    Calcula score de cumplimiento del CHECKLIST_IAO (0-100).
    DE LA KB: [SECTION:SCORING_ALGORITHM]
    
    Args:
        elementos: Dict con 12 elementos KB, cada uno True/False.
                   Usar _extraer_elementos_de_audit() para obtener.
    
    Returns:
        int 0-100. Si elementos está vacío o es None, retorna 0.
    """
    if not elementos:
        return 0
    
    pesos = {
        "ssl":               10,
        "schema_hotel":      15,
        "schema_reviews":    15,
        "LCP_ok":            10,
        "CLS_ok":             5,
        "contenido_extenso": 10,
        "open_graph":         5,
        "schema_faq":         8,
        "nap_consistente":    7,
        "imagenes_alt":       5,
        "blog_activo":        5,
        "redes_activas":      5,
    }
    
    score = sum(
        pesos[k] for k, v in elementos.items()
        if v is True and k in pesos
    )
    return min(score, 100)


def sugerir_paquete(score_tecnico: int) -> str:
    """
    Recomienda paquete según score técnico.
    DE LA KB: [SECTION:PACKAGE_TIERS]
    
    Args:
        score_tecnico: Score 0-100 de calcular_cumplimiento().
    
    Returns:
        "basico" (<40), "avanzado" (40-69), "premium" (>=70)
    """
    if score_tecnico < 40:
        return "basico"
    elif score_tecnico < 70:
        return "avanzado"
    else:
        return "premium"
```

**Tarea E2: Implementar `_extraer_elementos_de_audit()`**

```python
def _extraer_elementos_de_audit(self, audit_result: V4AuditResult) -> dict:
    """
    Extrae los 12 elementos del CHECKLIST_IAO desde V4AuditResult.
    
    RETORNA:
        dict con 12 elementos: {elemento_kb: bool}
        - 5 elementos se extraen REALMENTE del audit
        - 7 elementos usan默认值 (False) hasta que existan detectores
    
    VALIDAR CON: ELEMENTO_KB_TO_PAIN_ID.keys()
    """
    from .data_structures import ConfidenceLevel
    
    elementos = {}
    
    # Elementos REALES (detectables con audit actual)
    elementos["schema_hotel"] = bool(audit_result.schema.hotel_schema_detected)
    elementos["schema_reviews"] = bool(audit_result.gbp.rating)  # Proxy: gbp.rating existe
    elementos["LCP_ok"] = (
        audit_result.performance.lcp is not None 
        and audit_result.performance.lcp <= 2.5
    )
    elementos["CLS_ok"] = (
        audit_result.performance.cls is not None 
        and audit_result.performance.cls <= 0.1
    )
    elementos["schema_faq"] = bool(audit_result.schema.faq_schema_detected)
    
    # SSL: detectable trivially
    elementos["ssl"] = audit_result.url.startswith('https') if audit_result.url else False
    
    # NAP parcial: solo WhatsApp verificado
    ws_status = getattr(audit_result.validation, 'whatsapp_status', None)
    elementos["nap_consistente"] = (
        ws_status == ConfidenceLevel.VERIFIED.value
        if ws_status else False
    )
    
    # Elementos con默认值 (no hay detectores aún)
    elementos["contenido_extenso"] = False
    elementos["open_graph"] = False
    elementos["imagenes_alt"] = False
    elementos["blog_activo"] = False
    elementos["redes_activas"] = False
    
    # Validación: todos los 12 elementos deben estar presentes
    for elem in ELEMENTO_KB_TO_PAIN_ID.keys():
        if elem not in elementos:
            elementos[elem] = False  # Fallback defensivo
    
    return elementos
```

**Tarea E3: Modificar `_identify_brechas()` para retornar `pain_id`**

```python
def _identify_brechas(self, audit_result: V4AuditResult) -> List[Dict[str, Any]]:
    """
    Identify the 4 main brechas (gaps) from audit results.
    
    RETORNA:
        List[Dict] con campos: pain_id, nombre, impacto, detalle
        - pain_id: conecta con PainSolutionMapper
        - nombre: narrativa comercial para el cliente
        - impacto: peso para cálculo de pérdida (0.0-1.0)
        - detalle: explicación técnica
    
    NOTA:brechas[] alimenta pain_ids en DiagnosticSummary.
          faltantes[] viene de _extraer_elementos_de_audit() por separado.
    """
    from .data_structures import ConfidenceLevel
    
    brechas = []
    
    # Brecha 1: Visibilidad GBP/GEO
    if not audit_result.gbp.place_found or audit_result.gbp.geo_score < 60:
        brechas.append({
            'pain_id': 'low_gbp_score',
            'nombre': 'Visibilidad Local (Google Maps)',
            'impacto': 0.30,
            'detalle': '73% de búsquedas son "cerca de mí". Su GBP no aparece o está sub-optimizado.'
        })
    
    # Brecha 2: Sin Schema de Hotel
    if not audit_result.schema.hotel_schema_detected:
        brechas.append({
            'pain_id': 'no_hotel_schema',
            'nombre': 'Sin Schema de Hotel (Invisible para IA)',
            'impacto': 0.25,
            'detalle': 'ChatGPT, Gemini y Perplexity no pueden "leer" su hotel.'
        })
    
    # Brecha 3: WhatsApp No Configurado
    if not audit_result.validation.phone_web:
        brechas.append({
            'pain_id': 'no_whatsapp_visible',
            'nombre': 'Canal Directo Cerrado (Sin WhatsApp)',
            'impacto': 0.20,
            'detalle': 'Viajeros quieren reservar instantáneamente. Sin botón WhatsApp, pierden el impulso.'
        })
    
    # Brecha 4: Performance Web
    if audit_result.performance.mobile_score and audit_result.performance.mobile_score < 70:
        brechas.append({
            'pain_id': 'poor_performance',
            'nombre': 'Web Lenta (Abandono Móvil)',
            'impacto': 0.15,
            'detalle': f"{audit_result.performance.mobile_score}/100 en velocidad móvil."
        })
    
    # Brecha 5: Conflictos de Datos
    if audit_result.validation.whatsapp_status == ConfidenceLevel.CONFLICT.value:
        brechas.append({
            'pain_id': 'whatsapp_conflict',
            'nombre': 'Datos Inconsistentes (Confusión Cliente)',
            'impacto': 0.10,
            'detalle': 'WhatsApp diferente en web vs Google.'
        })
    
    # Brecha 6: Metadata por Defecto
    if audit_result.metadata and audit_result.metadata.has_issues:
        brechas.append({
            'pain_id': 'metadata_defaults',
            'nombre': 'Metadatos por Defecto del CMS',
            'impacto': 0.10,
            'detalle': 'Título y descripción usan valores por defecto.'
        })
    
    # Brecha 7: Reviews Faltantes
    if audit_result.gbp.reviews < 10:
        brechas.append({
            'pain_id': 'missing_reviews',
            'nombre': 'Falta de Reviews',
            'impacto': 0.10,
            'detalle': f"Solo {audit_result.gbp.reviews} reviews en Google."
        })
    
    # Si hay NAP conflict, agregar como brecha
    if audit_result.validation.whatsapp_status == ConfidenceLevel.CONFLICT.value:
        if not any(b['pain_id'] == 'whatsapp_conflict' for b in brechas):
            brechas.append({
                'pain_id': 'whatsapp_conflict',
                'nombre': 'Datos Inconsistentes (Confusión Cliente)',
                'impacto': 0.10,
                'detalle': 'WhatsApp diferente en web vs Google.'
            })
    
    # Priorizar por impacto y limitar a 4
    brechas.sort(key=lambda x: x.get('impacto', 0), reverse=True)
    return brechas[:4]
```

**Tarea E4: Modificar `_calculate_iao_score()`**

```python
def _calculate_iao_score(self, audit_result: V4AuditResult, hotel_data: dict = None) -> int:
    """
    Calcula IAO score usando IATester + AEOKPIs.

    RETORNA:
        int >= 0: Score real (0-100)
        int -1: Error en IATester (no disponible o falló)
        None: No se intentó (sin hotel_data)

    NOTA: Usa -1 para "error" y None para "sin intentar" — son estados distintos.
    """
    if not hotel_data:
        # Sin hotel_data: no se intentó
        return None

    try:
        from modules.analyzers.ia_tester import IATester

        ia_tester = IATester()
        ia_result = ia_tester.test_hotel(hotel_data)

        if not ia_result or not ia_result.get('queries_testeadas'):
            return -1  # Error: IATester falló

        # Calcular score basado en menciones reales
        total = ia_result.get('total_queries', 1)
        menciones = sum([
            ia_result.get('perplexity', {}).get('menciones', 0),
            ia_result.get('chatgpt', {}).get('menciones', 0),
        ])

        if total > 0:
            return min(100, int((menciones / total) * 100))
        return -1

    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"IATester failed: {e}")
        return -1
```

**Tarea E5: Agregar `_asset_para_pain()` y filtrar en `generate()`**

```python
def _asset_para_pain(self, pain_id: str) -> Optional[str]:
    """
    Retorna el asset principal para un pain_id, o None si es MISSING/inexistente.

    Útiles para filtrar pain_ids antes de pasarlos a la propuesta:
    - Si retorna None → el pain tiene asset MISSING → NO se monetiza
    - Si retorna un string → el asset está IMPLEMENTED → SÍ se monetiza
    """
    mapping = PainSolutionMapper.PAIN_SOLUTION_MAP.get(pain_id, {})
    assets = mapping.get("assets", [])
    if not assets:
        return None
    from modules.asset_generation.asset_catalog import is_asset_implemented
    return assets[0] if is_asset_implemented(assets[0]) else None
```

```python
def generate(self, audit_result: V4AuditResult, ...) -> DiagnosticSummary:
    # ... código existente de validación y coherence_score ...

    # Calcular score KB
    elementos = self._extraer_elementos_de_audit(audit_result)
    score_tecnico = calcular_cumplimiento(elementos)
    paquete = sugerir_paquete(score_tecnico)

    # Identificar faltantes (TODOS los elementos KB que fallan)
    faltantes = [k for k, v in elementos.items() if not v]

    # Identificar brechas
    brechas = self._identify_brechas(audit_result)

    # Extraer pain_ids SOLO si tienen asset IMPLEMENTED
    # (los assets MISSING no se prometen al cliente)
    pain_ids = [
        b['pain_id'] for b in brechas
        if b.get('pain_id') and self._asset_para_pain(b['pain_id']) is not None
    ]

    # Calcular score IA
    score_ia = self._calculate_iao_score(audit_result, hotel_data)

    # Crear DiagnosticSummary con campos KB
    summary = DiagnosticSummary(
        hotel_name=hotel_name,
        critical_problems_count=critical_count,
        quick_wins_count=quick_wins_count,
        overall_confidence=overall_conf,
        top_problems=[b['nombre'] for b in brechas[:4]],
        validated_data_summary=self._build_validated_summary(audit_result),
        coherence_score=coherence_score,
        # === CAMPOS KB (GAP-IAO-01-02) ===
        score_tecnico=score_tecnico,
        score_ia=score_ia,
        paquete=paquete,
        faltantes=faltantes,       # TODOS los elementos KB que fallan
        pain_ids=pain_ids,          # SOLO los que tienen asset IMPLEMENTED
    )

    return summary
```

---

## Archivos a modificar

| # | Archivo | Qué modificar | Orden |
|---|---------|--------------|-------|
| 1 | `modules/commercial_documents/pain_solution_mapper.py` | Agregar 5 pain_ids nuevos | PRIMERO |
| 2 | `modules/asset_generation/asset_catalog.py` | Agregar 5 assets MISSING | SEGUNDO |
| 3 | `modules/commercial_documents/data_structures.py` | Agregar 5 campos a DiagnosticSummary | TERCERO |
| 4 | `modules/commercial_documents/v4_diagnostic_generator.py` | ELEMENTO_KB_TO_PAIN_ID + lógica | CUARTO |

**IMPORTANTE**: Modificar en orden. Los archivos posteriores importan de los anteriores.

---

## Tests requeridos

```python
def test_calcular_cumplimiento_vacio():
    assert calcular_cumplimiento({}) == 0
    assert calcular_cumplimiento(None) == 0

def test_calcular_cumplimiento_completo():
    elementos = {k: True for k in ELEMENTO_KB_TO_PAIN_ID.keys()}
    assert calcular_cumplimiento(elementos) == 100

def test_calcular_cumplimiento_parcial():
    # Solo ssl(10) + schema_hotel(15) + schema_reviews(15) = 40
    elementos = {k: False for k in ELEMENTO_KB_TO_PAIN_ID.keys()}
    elementos["ssl"] = True
    elementos["schema_hotel"] = True
    elementos["schema_reviews"] = True
    assert calcular_cumplimiento(elementos) == 40

def test_sugerir_paquete():
    assert sugerir_paquete(0) == "basico"
    assert sugerir_paquete(39) == "basico"
    assert sugerir_paquete(40) == "avanzado"
    assert sugerir_paquete(69) == "avanzado"
    assert sugerir_paquete(70) == "premium"
    assert sugerir_paquete(100) == "premium"

def test_identify_brechas_tiene_pain_id():
    brechas = mapper._identify_brechas(mock_audit_result)
    for brecha in brechas:
        assert 'pain_id' in brecha
        assert brecha['pain_id'] in PainSolutionMapper.PAIN_SOLUTION_MAP

def test_extraer_elementos_tiene_12():
    elementos = _extraer_elementos_de_audit(mock_audit_result)
    assert len(elementos) == 12
    for elem in ELEMENTO_KB_TO_PAIN_ID.keys():
        assert elem in elementos

def test_score_ia_tipos():
    # None = sin hotel_data
    assert _calculate_iao_score(audit_result, None) is None
    # -1 = error
    assert _calculate_iao_score(audit_result, {}) == -1
    # >= 0 = score real
    result = _calculate_iao_score(audit_result, {"nombre": "Test"})
    assert result is None or result >= -1

def test_faltantes_son_elementos_kb():
    elementos = _extraer_elementos_de_audit(mock_audit_result)
    faltantes = [k for k, v in elementos.items() if not v]
    for f in faltantes:
        assert f in ELEMENTO_KB_TO_PAIN_ID
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`06-checklist-implementacion.md`**: Marcar GAP-IAO-01-02 como completada
2. **`09-documentacion-post-proyecto.md`**: Secciones A y E
3. **Ejecutar**:
```bash
python scripts/log_phase_completion.py \
    --fase GAP-IAO-01-02 \
    --desc "Scoring KB + pain_id alignment + 5 pain_ids nuevos + 5 assets MISSING + DiagnosticSummary campos KB" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/pain_solution_mapper.py,modules/commercial_documents/data_structures.py,modules/asset_generation/asset_catalog.py" \
    --check-manual-docs
```

---

## Criterios de Completitud

- [ ] Los 5 pain_ids nuevos existen en `PAIN_SOLUTION_MAP`
- [ ] Los 5 assets nuevos existen en `ASSET_CATALOG` con status `MISSING`
- [ ] `DiagnosticSummary` tiene 5 campos KB nuevos con defaults correctos
- [ ] `ELEMENTO_KB_TO_PAIN_ID` tiene los 12 elementos
- [ ] `calcular_cumplimiento()` retorna 0 con vacío, 100 con todo
- [ ] `sugerir_paquete()` usa umbrales correctos
- [ ] `_identify_brechas()` retorna `pain_id` en cada brecha
- [ ] `_extraer_elementos_de_audit()` retorna 12 elementos
- [ ] `_calculate_iao_score()` retorna `int` (None/-1/>=0)
- [ ] `_asset_para_pain()` retorna `None` para pain_ids con asset MISSING
- [ ] `pain_ids` en DiagnosticSummary NO incluye pain_ids con asset MISSING
- [ ] Todos los tests pasan
- [ ] `log_phase_completion.py` ejecutado
