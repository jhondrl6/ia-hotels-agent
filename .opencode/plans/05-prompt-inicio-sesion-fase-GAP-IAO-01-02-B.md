# GAP-IAO-01-02-B: Integración de 6 Elementos al Pipeline de Auditoría

**ID**: GAP-IAO-01-02-B
**Objetivo**: Implementar detectores reales para 6 elementos KB que actualmente usan默认值
**Dependencias**: GAP-IAO-01-02 (original)
**Duración estimada**: 1.5 horas (95 min)
**Skills**: test-driven-development, systematic-debugging
**Documento de soporte**: `00-PRE-GAP-01-02-ANALISIS-DESCONEXIONES-v2.md` — leer ANTES de implementar

---

## Contexto

### Estado Actual

| Elemento | Detector Actual | Problema |
|----------|----------------|----------|
| `ssl` |默认值 `False` | Debería ser `url.startswith("https")` |
| `contenido_extenso` |默认值 `False` | CitabilityScorer existe pero no se usa |
| `nap_consistente` | Solo WhatsApp | No valida dirección ni email |
| `open_graph` |默认值 `False` | No existe detector |
| `imagenes_alt` |默认值 `False` | No existe detector |
| `redes_activas` |默认值 `False` | No existe detector |

### Arquitectura Final

```
AUDITORÍA v4.0                           v4.1 (con GAP-IAO-01-02-B)
─────────────────                        ───────────────────────────
CitabilityResult ✅                      CitabilityResult ✅
CrossValidator ⚠️ (solo WhatsApp)        CrossValidator v2 ✅ (extendido)
  - WhatsApp ✅                           - WhatsApp ✅
                                            - Address ✨ NUEVO
                                            - Email ✨ NUEVO
SSL:默认值 ❌                             SSL: real ✅
contenido_extenso:默认值 ❌               contenido_extenso: real ✅
open_graph:默认值 ❌                      open_graph: stub ✅
imagenes_alt:默认值 ❌                    imagenes_alt: stub ✅
redes_activas:默认值 ❌                  redes_activas: stub ✅
```

---

## Tareas (Orden de ejecución OBLIGATORIO)

### SUBFASE B1: ssl — Detector Trivial (5 min, RIESGO NULO)

**Archivo**: `modules/auditors/v4_comprehensive.py`

**Tarea B1.1: Agregar `_check_ssl()`**

```python
def _check_ssl(self, url: str) -> bool:
    """
    SSL detection is trivial - just check URL scheme.
    
    Returns:
        True if URL uses https://, False otherwise.
    """
    return url.startswith("https://") if url else False
```

**Tarea B1.2: Llamar desde `_run_audit()`**

En el método `audit()`, después de obtener la URL y antes de construir `V4AuditResult`:

```python
# SSL check (trivial)
ssl_detected = self._check_ssl(url)
# NOTA: V4AuditResult no tiene campo ssl directo,
# se extrae en _extraer_elementos_de_audit() via url.startswith("https")
```

**Tarea B1.3: Modificar `_extraer_elementos_de_audit()` en v4_diagnostic_generator.py**

```python
# CAMBIAR línea 376:
elementos["ssl"] = audit_result.url.startswith('https') if audit_result.url else False
# POR (más explícito):
elementos["ssl"] = self._check_ssl(audit_result.url) if hasattr(self, '_check_ssl') else (audit_result.url.startswith('https') if audit_result.url else False)
```

**Efecto**: `ssl` deja de ser默认值 y usa detección real.

---

### SUBFASE B2: contenido_extenso — Mapear CitabilityScorer (15 min, RIESGO BAJO)

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Tarea B2.1: Modificar `_extraer_elementos_de_audit()`**

```python
# CAMBIAR (línea ~386):
elementos["contenido_extenso"] = False

# POR:
elementos["contenido_extenso"] = (
    audit_result.citability is not None 
    and audit_result.citability.overall_score > 50
) if hasattr(audit_result, 'citability') and audit_result.citability else False
```

**Tarea B2.2: Verificar que CitabilityScorer se ejecuta en audit()**

En `v4_comprehensive.py`, método `audit()`:

```python
# Verificar que citability scoring está habilitado
if self.config.get("enable_citability", True):
    citability_result = self._run_citability_audit(url, html_content)
    # ...
```

**Efecto**: `contenido_extenso` usa CitabilityScorer real (overall_score > 50 = True).

---

### SUBFASE B3: nap_consistente — Extender CrossValidator (30 min, RIESGO BAJO)

**Archivo**: `modules/data_validation/cross_validator.py`

**Tarea B3.1: Agregar métodos de validación**

```python
def validate_address(self, web_value: str, gbp_value: str) -> Optional[DataPoint]:
    """
    Validate address consistency between web and GBP.
    
    Returns:
        DataPoint with confidence level, or None if cannot validate.
    """
    if not web_value or not gbp_value:
        return None
    
    # Normalize for comparison
    web_normalized = self._normalize_address(web_value)
    gbp_normalized = self._normalize_address(gbp_value)
    
    if web_normalized == gbp_normalized:
        return DataPoint(
            field="address",
            web_value=web_value,
            gbp_value=gbp_value,
            confidence=ConfidenceLevel.VERIFIED,
            match=True,
            discrepancy=None,
        )
    else:
        return DataPoint(
            field="address",
            web_value=web_value,
            gbp_value=gbp_value,
            confidence=ConfidenceLevel.CONFLICT,
            match=False,
            discrepancy=f"Web: {web_value} vs GBP: {gbp_value}",
        )

def validate_email(self, web_value: str, gbp_value: str) -> Optional[DataPoint]:
    """
    Validate email consistency.
    
    Returns:
        DataPoint with confidence level, or None if cannot validate.
    """
    if not web_value:
        return None
    
    # GBP typically doesn't have email, so just verify web email is valid
    if self._is_valid_email(web_value):
        return DataPoint(
            field="email",
            web_value=web_value,
            gbp_value=gbp_value,
            confidence=ConfidenceLevel.ESTIMATED,  # Single source
            match=True,
            discrepancy=None,
        )
    return None

def _normalize_address(self, address: str) -> str:
    """Normalize address for comparison."""
    import re
    if not address:
        return ""
    # Remove extra spaces, lowercase
    normalized = re.sub(r'\s+', ' ', address.lower().strip())
    # Remove common abbreviations
    normalized = normalized.replace('carrera', 'kr').replace('calle', 'cl')
    normalized = normalized.replace('no.', '#').replace(' No ', ' #')
    return normalized

def _is_valid_email(self, email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))
```

**Tarea B3.2: Extender CrossValidationResult**

**Archivo**: `modules/auditors/v4_comprehensive.py`

```python
# CAMBIAR el dataclass CrossValidationResult:
@dataclass
class CrossValidationResult:
    """Result of cross-validation between sources."""
    whatsapp_status: str
    phone_web: Optional[str]
    phone_gbp: Optional[str]
    adr_status: str
    adr_web: Optional[float]
    adr_benchmark: Optional[float]
    conflicts: List[Dict] = field(default_factory=list)
    validated_fields: Dict[str, Any] = field(default_factory=dict)
    
    # NUEVOS CAMPOS (GAP-IAO-01-02-B):
    address_status: str = "unknown"
    email_status: str = "unknown"
    address_web: Optional[str] = None
    address_gbp: Optional[str] = None
```

**Tarea B3.3: Modificar `_run_cross_validation()`**

```python
def _run_cross_validation(
    self,
    url: str,
    schema: SchemaAuditResult,
    gbp: GBPApiResult,
) -> CrossValidationResult:
    """Run cross-validation between data sources."""
    # ... código existente de WhatsApp y ADR ...
    
    # NUEVO: Validate address
    web_address = schema.properties.get("address")
    gbp_address = gbp.address
    address_dp = self.cross_validator.validate_address(web_address, gbp_address)
    
    # NUEVO: Validate email
    web_email = schema.properties.get("email")
    gbp_email = None  # GBP no typically provides email
    email_dp = self.cross_validator.validate_email(web_email, gbp_email)
    
    return CrossValidationResult(
        whatsapp_status=whatsapp_dp.confidence.value if whatsapp_dp else ConfidenceLevel.UNKNOWN.value,
        phone_web=web_phone,
        phone_gbp=gbp_phone,
        adr_status=adr_dp.confidence.value if adr_dp else ConfidenceLevel.UNKNOWN.value,
        adr_web=adr_web,
        adr_benchmark=None,
        conflicts=conflicts,
        validated_fields={
            "whatsapp": whatsapp_dp.to_dict() if whatsapp_dp else None,
            "adr": adr_dp.to_dict() if adr_dp else None,
            "address": address_dp.to_dict() if address_dp else None,
            "email": email_dp.to_dict() if email_dp else None,
        },
        # NUEVOS CAMPOS:
        address_status=address_dp.confidence.value if address_dp else "unknown",
        email_status=email_dp.confidence.value if email_dp else "unknown",
        address_web=web_address,
        address_gbp=gbp_address,
    )
```

**Tarea B3.4: Modificar `_extraer_elementos_de_audit()` para nap_consistente**

```python
# CAMBIAR:
elementos["nap_consistente"] = (
    ws_status == ConfidenceLevel.VERIFIED.value
    if ws_status else False
)

# POR:
def _es_nap_consistente(self, audit_result: V4AuditResult) -> bool:
    """NAP es consistente si WhatsApp Y dirección Y email están verificados."""
    validation = audit_result.validation
    
    # WhatsApp verificado
    whatsapp_ok = (
        getattr(validation, 'whatsapp_status', None) == ConfidenceLevel.VERIFIED.value
    )
    
    # Dirección verificada (si existe el campo)
    address_status = getattr(validation, 'address_status', 'unknown')
    address_ok = address_status == ConfidenceLevel.VERIFIED.value
    
    # Email verificado (si existe el campo)
    email_status = getattr(validation, 'email_status', 'unknown')
    email_ok = email_status in [ConfidenceLevel.VERIFIED.value, ConfidenceLevel.ESTIMATED.value]
    
    # NAP completo = WhatsApp + Address (email es bonus)
    return whatsapp_ok and address_ok

elementos["nap_consistente"] = self._es_nap_consistente(audit_result)
```

---

### SUBFASE B4: SEOElementsDetector — Stubs para 3 elementos (45 min, RIESGO BAJO)

**Tarea B4.1: Crear `modules/auditors/seo_elements_detector.py`**

```python
"""SEO Elements Detector - Stubs para elementos sin detector real.

Este módulo proporciona detectores básicos para elementos SEO.
Actualmente son stubs que retornan默认值 False hasta que se implementen
detectores reales usando BeautifulSoup/Playwright.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class SEOElementsResult:
    """Result of SEO elements detection."""
    open_graph: bool = False
    imagenes_alt: bool = False
    redes_activas: bool = False
    confidence: str = "estimated"  # estimated | low | medium | high
    notes: str = ""
    open_graph_tags: dict = None  # Detalles de og tags encontrados
    images_without_alt: int = 0   # Count de imágenes sin alt
    social_links_found: list = None  # Lista de URLs de redes sociales

    def __post_init__(self):
        if self.open_graph_tags is None:
            self.open_graph_tags = {}
        if self.images_without_alt is None:
            self.images_without_alt = 0
        if self.social_links_found is None:
            self.social_links_found = []

class SEOElementsDetector:
    """
    Detecta elementos SEO básicos en páginas web.
    
    Stacy actual: Stub que retorna todos默认值 False.
    Implementación completa requiere BeautifulSoup.
    """
    
    def __init__(self):
        self.confidence = "estimated"
    
    def detect(self, html: str, url: str) -> SEOElementsResult:
        """
        Detecta presencia de elementos SEO en el HTML.
        
        Args:
            html: Contenido HTML de la página
            url: URL de la página (para validación)
            
        Returns:
            SEOElementsResult con campos individuales
            
        TODO (implementación completa):
        - Usar BeautifulSoup para parseo
        - Detectar og:image, og:title, og:description
        - Contar imágenes sin atributo alt
        - Buscar enlaces a redes sociales conocidas
        """
        return SEOElementsResult(
            open_graph=False,  # TODO: implementar con BeautifulSoup
            imagenes_alt=False,  # TODO: implementar con BeautifulSoup
            redes_activas=False,  # TODO: implementar con BeautifulSoup
            confidence="estimated",
            notes="Stub detector - awaiting BeautifulSoup implementation"
        )
    
    def _detect_open_graph(self, soup) -> tuple[bool, dict]:
        """Detect Open Graph tags. Requires BeautifulSoup."""
        # PLACEHOLDER - would use soup.find_all('meta', property='og:*')
        return False, {}
    
    def _detect_images_alt(self, soup) -> tuple[bool, int]:
        """Count images without alt text. Requires BeautifulSoup."""
        # PLACEHOLDER - would use soup.find_all('img')
        return False, 0
    
    def _detect_social_links(self, soup, url: str) -> tuple[bool, list]:
        """Detect social media links. Requires BeautifulSoup."""
        # PLACEHOLDER - would search for known social domain patterns
        return False, []
```

**Tarea B4.2: Extender V4AuditResult**

**Archivo**: `modules/auditors/v4_comprehensive.py`

```python
# AGREGAR al imports:
from modules.auditors.seo_elements_detector import SEOElementsDetector, SEOElementsResult

# AGREGAR al dataclass V4AuditResult (después de citability):
@dataclass
class V4AuditResult:
    # ... campos existentes ...
    
    # SEO Elements (GAP-IAO-01-02-B)
    seo_elements: Optional[SEOElementsResult] = None
```

**Tarea B4.3: Ejecutar SEOElementsDetector en audit()**

```python
def _run_seo_elements_audit(self, html: str, url: str) -> SEOElementsResult:
    """Run SEO elements detection."""
    detector = SEOElementsDetector()
    return detector.detect(html, url)

# En el método audit(), después de citability:
seo_elements = self._run_seo_elements_audit(html, url)
```

**Tarea B4.4: Mapear en `_extraer_elementos_de_audit()`**

```python
# AGREGAR después de contenido_extenso:
elementos["open_graph"] = (
    audit_result.seo_elements.open_graph 
    if audit_result.seo_elements else False
)
elementos["imagenes_alt"] = (
    audit_result.seo_elements.imagenes_alt 
    if audit_result.seo_elements else False
)
elementos["redes_activas"] = (
    audit_result.seo_elements.redes_activas 
    if audit_result.seo_elements else False
)
```

---

## Archivos a modificar (en orden)

| # | Archivo | Qué modificar | Prioridad |
|---|---------|--------------|----------|
| 1 | `modules/auditors/seo_elements_detector.py` | **CREAR** nuevo archivo | 1 |
| 2 | `modules/data_validation/cross_validator.py` | Agregar validate_address, validate_email | 2 |
| 3 | `modules/auditors/v4_comprehensive.py` | CrossValidationResult v2 + SEOElementsResult + ssl | 3 |
| 4 | `modules/commercial_documents/v4_diagnostic_generator.py` | Mapear elementos desde audit real | 4 |

---

## Tests requeridos

```python
def test_check_ssl_https():
    detector = V4ComprehensiveAuditor()
    assert detector._check_ssl("https://example.com") == True

def test_check_ssl_http():
    detector = V4ComprehensiveAuditor()
    assert detector._check_ssl("http://example.com") == False

def test_contenido_extenso_con_citability_alto():
    # Citability score > 50 = contenido_extenso True
    mock_audit.citability = CitabilityResult(overall_score=75)
    elementos = _extraer_elementos_de_audit(mock_audit)
    assert elementos["contenido_extenso"] == True

def test_contenido_extenso_con_citability_bajo():
    # Citability score < 50 = contenido_extenso False
    mock_audit.citability = CitabilityResult(overall_score=30)
    elementos = _extraer_elementos_de_audit(mock_audit)
    assert elementos["contenido_extenso"] == False

def test_nap_consistente_full():
    # WhatsApp + Address verificados = True
    mock_audit.validation.whatsapp_status = "VERIFIED"
    mock_audit.validation.address_status = "VERIFIED"
    mock_audit.validation.email_status = "ESTIMATED"
    elementos = _extraer_elementos_de_audit(mock_audit)
    assert elementos["nap_consistente"] == True

def test_nap_consistente_parcial():
    # Solo WhatsApp = False (falta address)
    mock_audit.validation.whatsapp_status = "VERIFIED"
    mock_audit.validation.address_status = "unknown"
    elementos = _extraer_elementos_de_audit(mock_audit)
    assert elementos["nap_consistente"] == False

def test_seo_elements_stub():
    mock_audit.seo_elements = SEOElementsResult(
        open_graph=False,
        imagenes_alt=False,
        redes_activas=False,
        confidence="estimated"
    )
    elementos = _extraer_elementos_de_audit(mock_audit)
    assert elementos["open_graph"] == False
    assert elementos["imagenes_alt"] == False
    assert elementos["redes_activas"] == False
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`06-checklist-implementacion.md`**: Marcar GAP-IAO-01-02-B como completada
2. **`09-documentacion-post-proyecto.md`**: Agregar sección para GAP-IAO-01-02-B
3. **Ejecutar**:
```bash
python scripts/log_phase_completion.py \
    --fase GAP-IAO-01-02-B \
    --desc "Integración ssl trivial + contenido_extenso (CitabilityScorer) + nap_consistente (CrossValidator extendido) + 3 stubs (SEOElementsDetector)" \
    --archivos-mod "modules/auditors/seo_elements_detector.py,modules/data_validation/cross_validator.py,modules/auditors/v4_comprehensive.py,modules/commercial_documents/v4_diagnostic_generator.py" \
    --check-manual-docs
```

---

## Criterios de Completitud

- [ ] `_check_ssl()` retorna `url.startswith("https")` correctamente
- [ ] `contenido_extenso` usa `citability.overall_score > 50`
- [ ] `CrossValidationResult` tiene `address_status` y `email_status`
- [ ] `_es_nap_consistente()` retorna True solo con WhatsApp + Address verificados
- [ ] `SEOElementsDetector` existe y se ejecuta en audit()
- [ ] `open_graph`, `imagenes_alt`, `redes_activas` usan `seo_elements`
- [ ] Score técnico ahora usa datos reales donde existen
- [ ] Todos los tests pasan
- [ ] `log_phase_completion.py` ejecutado

---

## Nota sobre SEOElementsDetector

Este detector es un **STUB**. Los elementos `open_graph`, `imagenes_alt`, y `redes_activas` seguirán retornando `False` hasta que se implemente la detección real con BeautifulSoup.

**Próximos pasos para implementación completa**:
1. Instalar `beautifulsoup4` si no está
2. Reemplazar stubs con parseo real de HTML
3. Agregar unit tests con HTML de prueba
4. Medir coverage de los nuevos detectores

**Esto está fuera del scope de GAP-IAO-01-02-B** — la fase actual solo establece la estructura para recibir datos reales cuando existan detectores.
