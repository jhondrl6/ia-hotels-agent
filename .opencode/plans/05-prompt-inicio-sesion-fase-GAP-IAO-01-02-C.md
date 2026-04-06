# GAP-IAO-01-02-C: Assets IAO Completos

**ID**: GAP-IAO-01-02-C
**Objetivo**: Implementar los 5 assets MISSING para cerrar el flujo IAO completo
**Dependencias**: GAP-IAO-01-02-B
**Duración estimada**: 2 horas
**Skills**: writing-plans, test-driven-development
**Documento de soporte**: `00-IAO-FLUJO-COMPLETO.md` — leer ANTES de implementar

---

## Contexto

### Assets MISSING en ASSET_CATALOG

| Asset | pain_id que lo promete | Prioridad | Impacto IAO |
|-------|----------------------|----------|-------------|
| `ssl_guide` | `no_ssl` | BAJA |ssl es básico para cualquier web moderna |
| `og_tags_guide` | `no_og_tags` | BAJA | Open Graph mejora social sharing |
| `alt_text_guide` | `missing_alt_text` | MEDIA | Alt text mejora citabilidad de imágenes por IA |
| `blog_strategy_guide` | `no_blog_content` | BAJA | Blog activo = señales de autoridad |
| `social_strategy_guide` | `no_social_links` | BAJA | Redes sociales = señales E-E-A-T |

### Estado Actual del Flujo

```
V4AuditResult → DiagnosticSummary → pain_ids → PAIN_SOLUTION_MAP → ASSET_CATALOG
                                                                 ├── ✅ hotel_schema
                                                                 ├── ✅ faq_page
                                                                 ├── ✅ performance_audit
                                                                 ├── ✅ optimization_guide
                                                                 ├── ✅ whatsapp_button
                                                                 ├── ✅ review_plan
                                                                 ├── ❌ ssl_guide      ← MISSING
                                                                 ├── ❌ og_tags_guide  ← MISSING
                                                                 ├── ❌ alt_text_guide ← MISSING
                                                                 ├── ❌ blog_strategy_guide ← MISSING
                                                                 └── ❌ social_strategy_guide ← MISSING
```

### Impacto de NO implementar

- `no_ssl` pain_id existe pero no puede generar asset → se pierde monetización
- `no_og_tags` pain_id existe pero no puede generar asset → se pierde monetización
- `missing_alt_text` pain_id existe pero no puede generar asset → se pierde monetización
- `no_blog_content` pain_id existe pero no puede generar asset → se pierde monetización
- `no_social_links` pain_id existe pero no puede generar asset → se pierde monetización

### Beneficio de IMPLEMENTAR

- El sistema puede generar guías para TODOS los pain_ids IAO
- La propuesta puede ofrecer solución completa
- El cliente recibe guía práctica para cadaGap

---

## Tareas

### TAREA C1: Implementar `ssl_guide`

**Archivo**: `modules/asset_generation/conditional_generator.py`

**Primero**: Agregar a `ASSET_CATALOG` con status `IMPLEMENTED`:

```python
"ssl_guide": AssetCatalogEntry(
    asset_type="ssl_guide",
    template="ssl_guide_template.md",
    output_name="{prefix}guia_ssl{suffix}.md",
    required_field="ssl_detected",
    required_confidence=0.0,
    fallback="generate_ssl_checklist",
    block_on_failure=False,
    status=AssetStatus.IMPLEMENTED,
    promised_by=["no_ssl"]
),
```

**Segundo**: Implementar generador:

```python
def generate_ssl_guide(self, hotel_data: dict, audit_result: V4AuditResult) -> AssetResult:
    """
    Genera guía de implementación SSL/HTTPS.
    
    Content:
    - Verificación de certificado SSL actual
    - Pasos para forzar HTTPS
    - Configuración de redirección 301
    - Checkpoints de verificación
    """
    url = audit_result.url
    
    # Verificar SSL actual
    has_ssl = url.startswith("https") if url else False
    
    content = f"""# Guía de Implementación SSL/HTTPS

## Estado Actual
{'✅ Su sitio YA tiene SSL instalado' if has_ssl else '❌ Su sitio NO tiene SSL'}

## ¿Por qué SSL es importante?

1. **Seguridad**: Cifra la comunicación entre el usuario y su sitio
2. **SEO**: Google penaliza sitios sin HTTPS
3. **IAO**: Los crawlers de IA prefieren sitios seguros

## Pasos de Implementación

### Paso 1: Verificar Certificado
Visite: https://www.ssllabs.com/ssltest/analyze.html?d={url.replace('https://', '')}

### Paso 2: Forzar HTTPS
Agregue en su .htaccess o configuración del servidor:

```apache
RewriteEngine On
RewriteCond %{{HTTPS}} off
RewriteRule ^(.*)$ https://%{{HTTP_HOST}}%{{REQUEST_URI}} [L,R=301]
```

### Paso 3: Actualizar Enlaces Internos
 Asegúrese que todos los enlaces internos usen https://

### Paso 4: Verificar en Google Search Console
1. Vaya a Google Search Console
2. Seleccione su propiedad
3. Vaya a Configuración → Configuración de dominio
4. Verifique que el dominio esté verificado con https://

## Checkpoint Final
Su sitio debe mostrar candado verde en el navegador.
"""
    
    return AssetResult(
        asset_type="ssl_guide",
        content=content,
        generated_at=datetime.now().isoformat(),
        confidence=1.0 if has_ssl else 0.9,
        errors=[],
        warnings=["Considere HSTS para mayor seguridad"] if has_ssl else []
    )
```

---

### TAREA C2: Implementar `og_tags_guide`

**Archivo**: `modules/asset_generation/conditional_generator.py`

**Primero**: Agregar a `ASSET_CATALOG`:

```python
"og_tags_guide": AssetCatalogEntry(
    asset_type="og_tags_guide",
    template="og_tags_guide_template.md",
    output_name="{prefix}guia_og_tags{suffix}.md",
    required_field="og_tags_detected",
    required_confidence=0.0,
    fallback="generate_og_tags_checklist",
    block_on_failure=False,
    status=AssetStatus.IMPLEMENTED,
    promised_by=["no_og_tags"]
),
```

**Segundo**: Implementar generador:

```python
def generate_og_tags_guide(self, hotel_data: dict, audit_result: V4AuditResult) -> AssetResult:
    """
    Genera guía de implementación de Open Graph tags.
    
    Open Graph permite control sobre cómo se muestra el sitio en redes sociales.
    Impacto directo en: Facebook, LinkedIn, Twitter, WhatsApp, Telegram
    """
    url = audit_result.url
    hotel_name = hotel_data.get("nombre", "Su Hotel")
    
    # Verificar OG tags actuales (si seo_elements disponible)
    og_status = "No detectable (requiere implementación)"
    if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
        og_status = "✅ Detectados" if audit_result.seo_elements.open_graph else "❌ No detectados"
    
    content = f"""# Guía de Open Graph Tags

## ¿Qué son Open Graph Tags?

Son meta tags que controlan cómo se muestra su sitio cuando se comparte en redes sociales.

## Estado Actual
{og_status}

## Impacto

| Red Social | Sin OG | Con OG |
|-----------|--------|--------|
| Facebook | Imagen aleatoria | Imagen seleccionada por usted |
| LinkedIn | Sin preview rica | Con imagen, título, descripción |
| WhatsApp | Solo URL | Con imagen y título |
| Twitter | Sin imagen | Con tarjeta rica |

## Implementación

Agregue en el <head> de su sitio:

```html
<!-- Open Graph / Facebook -->
<meta property="og:type" content="website" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{hotel_name} - Hotel Boutique en [Ciudad]" />
<meta property="og:description" content="[Descripción de 155-200 caracteres]" />
<meta property="og:image" content="[URL de imagen 1200x630px]" />

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{hotel_name}" />
<meta name="twitter:description" content="[Descripción]" />
<meta name="twitter:image" content="[URL de imagen]" />
```

## Imagen Recomendada
- Dimensiones: 1200x630px (Facebook/LinkedIn)
- Formato: JPG o PNG
- Tamaño máximo: 5MB
- Contenido: Foto atractiva del hotel con buena iluminación

## Verificación

1. Facebook Sharing Debugger: https://developers.facebook.com/tools/debug/
2. LinkedIn Post Inspector: https://www.linkedin.com/post-inspector/
3. Twitter Card Validator: https://cards-dev.twitter.com/validator
"""
    
    return AssetResult(
        asset_type="og_tags_guide",
        content=content,
        generated_at=datetime.now().isoformat(),
        confidence=0.9,
        errors=[],
        warnings=[]
    )
```

---

### TAREA C3: Implementar `alt_text_guide`

**Archivo**: `modules/asset_generation/conditional_generator.py`

**Primero**: Agregar a `ASSET_CATALOG`:

```python
"alt_text_guide": AssetCatalogEntry(
    asset_type="alt_text_guide",
    template="alt_text_guide_template.md",
    output_name="{prefix}guia_alt_text{suffix}.md",
    required_field="alt_text_detected",
    required_confidence=0.0,
    fallback="generate_alt_text_checklist",
    block_on_failure=False,
    status=AssetStatus.IMPLEMENTED,
    promised_by=["missing_alt_text"]
),
```

**Segundo**: Implementar generador:

```python
def generate_alt_text_guide(self, hotel_data: dict, audit_result: V4AuditResult) -> AssetResult:
    """
    Genera guía de texto alternativo para imágenes.
    
    El atributo alt es crítico para:
    1. Accesibilidad (lectores de pantalla)
    2. Indexación por IA (AI puede "ver" la imagen)
    3. SEO en Google Images
    """
    url = audit_result.url
    images_count = 0
    images_without_alt = 0
    
    # Obtener datos de SEOElements si disponible
    if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
        images_count = getattr(audit_result.seo_elements, 'images_analyzed', 0)
        images_without_alt = audit_result.seo_elements.images_without_alt or 0
    
    content = f"""# Guía de Texto Alternativo (Alt Text)

## ¿Qué es el Texto Alternativo?

El atributo `alt` describe una imagen para:
- Personas con discapacidad visual (lectores de pantalla)
- Cuando la imagen no carga
- Indexación por IA y SEO

## Estado Actual del Sitio
- Imágenes analizadas: {images_count if images_count > 0 else "No disponible"}
- Imágenes sin alt: {images_without_alt if images_without_alt > 0 else "No disponible"}

## Reglas de Escritura

### ✅ HAGA:
1. Describa lo que muestra la imagen
2. Incluya el nombre del hotel cuando sea relevante
3. Sea específico: "Habitación doble con vista al jardín" no "habitación"
4. Mantenga entre 50-125 caracteres

### ❌ NO HAGA:
1. No comience con "Imagen de" o "Foto de"
2. No use palabras genéricas como "imagen" o "foto"
3. No stuffed keywords (spam de palabras clave)

## Ejemplos para Hoteles

| Tipo de Imagen | ❌ MAL | ✅ BIEN |
|---------------|--------|---------|
| Habitación | "habitacion" | "Habitación doble con cama king y vista al jardín tropical" |
| Restaurante | "comida" | "Desayuno tropical con frutas frescas y café colombiano" |
| Fachada | "hotel" | "Fachada del Hotel Visperas con arquitectura colonial" |
| Piscina | "piscina" | "Piscina infinity con vista al valle cafetero al atardecer" |
| Spa | "spa" | "Área de masajes al aire libre rodeada de plantas nativas" |

## Implementación Técnica

```html
<!-- Con alt descriptivo -->
<img src="/images/habitacion-doble.jpg" alt="Habitación doble con cama king, balcón privado y vista al jardín tropical" />

<!-- Imagen decorativa (puede ir vacía) -->
<img src="/images/borde-decorativo.png" alt="" />
```

## Herramientas de Verificación

1. **WAVE** (WebAIM): https://wave.webaim.org/
2. **axe DevTools**: Extensión de Chrome
3. **Google Search Console**: Informe de Accesibilidad

## Checklist de Auditoría

- [ ] Todas las imágenes de contenido tienen alt
- [ ] Los alt no comienzan con "Imagen de" o "Foto de"
- [ ] Los alt describen específicamente el contenido
- [ ] Las imágenes decorativas tienen alt=""
- [ ] El alt incluye nombre del hotel cuando es relevante
"""
    
    return AssetResult(
        asset_type="alt_text_guide",
        content=content,
        generated_at=datetime.now().isoformat(),
        confidence=0.9,
        errors=[],
        warnings=["Implemente auditoria de imágenes para datos precisos"] if images_count == 0 else []
    )
```

---

### TAREA C4: Implementar `blog_strategy_guide`

**Archivo**: `modules/asset_generation/conditional_generator.py`

**Primero**: Agregar a `ASSET_CATALOG`:

```python
"blog_strategy_guide": AssetCatalogEntry(
    asset_type="blog_strategy_guide",
    template="blog_strategy_template.md",
    output_name="{prefix}estrategia_blog{suffix}.md",
    required_field="blog_detected",
    required_confidence=0.0,
    fallback="generate_blog_strategy",
    block_on_failure=False,
    status=AssetStatus.IMPLEMENTED,
    promised_by=["no_blog_content"]
),
```

**Segundo**: Implementar generador:

```python
def generate_blog_strategy_guide(self, hotel_data: dict, audit_result: V4AuditResult) -> AssetResult:
    """
    Genera estrategia de blog para hotel boutique.
    
    Blog activo mejora:
    1. Autoridad de dominio (SEO)
    2. Contenido nuevo para indexación IA
    3. Señales E-E-A-T (Experience, Expertise, Authority)
    4. Engagement con potenciales huéspedes
    """
    url = audit_result.url
    hotel_name = hotel_data.get("nombre", "Su Hotel")
    
    content = f"""# Estrategia de Blog para {hotel_name}

## ¿Por qué su hotel necesita un blog?

1. **Visibilidad IA**: LLMs como ChatGPT citan fuentes con contenido fresco
2. **SEO**: Google indexa contenido nuevo y relevante
3. **E-E-A-T**: Demuestra experiencia y conocimiento del destino
4. **Conexión emocional**: Historias del hotel humanizan su marca

## Frecuencia Recomendada

| Objetivo | Frecuencia | Posts/mes |
|----------|-----------|-----------|
| Mínimo | 1 cada 2 semanas | 2 |
| Recomendado | 1 por semana | 4 |
| Óptimo | 2 por semana | 8 |

## Ideas de Contenido IAO-Optimizado

### Tipo 1: Guías del Destino (HIGH IAO VALUE)
```
"La mejor época para visitar [destino] según los locales"
"5 experiencias auténticas en [ciudad] que los turistas raramente descubren"
"Guía definitiva: Cómo llegar a [atractivo] desde [hotel]"
```

### Tipo 2: Experiencias del Hotel (MEDIUM-HIGH VALUE)
```
"Un día en [hotel]: De la mañana a la noche"
"Cómo preparamos el desayuno típico que aman nuestros huéspedes"
"Detrás de escenas: El equipo que hace posible su estadía perfecta"
```

### Tipo 3: Consejos Prácticos (MEDIUM VALUE)
```
"Qué empacar para una estadía rural en [región]"
"Guía de supervivencia: Cómo moverse en [ciudad] como local"
"Errores comunes al planificar viajes a [destino] y cómo evitarlos"
```

### Tipo 4: Estacional (HIGH SEO VALUE)
```
"Qué hacer en [ciudad] en temporada alta/baja"
"Eventos culturales de [mes] en [región]"
"Festival de [nombre]: Por qué debería planificar su visita"
```

## Formato para Ser Citado por IA

Cada post debe incluir:

### 1. Datos Estructurados (Schema.org)
```json
{{
  "@type": "Article",
  "headline": "[Título descriptivo]",
  "author": {{ "@type": "Person", "name": "[Nombre del autor]" }},
  "datePublished": "[YYYY-MM-DD]",
  "description": "[Resumen de 150-160 caracteres]"
}}
```

### 2. Sección de Datos
```
**Información práctica:**
- Ubicación: [dirección]
- Horarios: [si aplica]
- Costo: [si aplica]
- Contacto: [teléfono/email]
```

### 3. Autoridad Local
```
**Sobre [hotel]:**
[Breve descripción de 2-3 oraciones sobre el hotel y su conexión con el tema]
```

## Checklist Técnico

- [ ] Cada post tiene al menos 600 palabras
- [ ] Incluye al menos 3 imágenes con alt descriptivo
- [ ] Tiene Schema.org Article o BlogPosting
- [ ] Los enlaces internos conectan con páginas del hotel
- [ ] El título tiene menos de 60 caracteres
- [ ] La meta descripción tiene 150-160 caracteres

## Métricas a Monitorear

1. Vistas orgánicas por mes
2. Tiempo en página (>3 min = bueno)
3. Tasa de rebote (<70% = bueno)
4. Backlinks generados
5. Apariciones en resultados de IA
"""
    
    return AssetResult(
        asset_type="blog_strategy_guide",
        content=content,
        generated_at=datetime.now().isoformat(),
        confidence=0.9,
        errors=[],
        warnings=[]
    )
```

---

### TAREA C5: Implementar `social_strategy_guide`

**Archivo**: `modules/asset_generation/conditional_generator.py`

**Primero**: Agregar a `ASSET_CATALOG`:

```python
"social_strategy_guide": AssetCatalogEntry(
    asset_type="social_strategy_guide",
    template="social_strategy_template.md",
    output_name="{prefix}estrategia_social{suffix}.md",
    required_field="social_links_detected",
    required_confidence=0.0,
    fallback="generate_social_strategy",
    block_on_failure=False,
    status=AssetStatus.IMPLEMENTED,
    promised_by=["no_social_links"]
),
```

**Segundo**: Implementar generador:

```python
def generate_social_strategy_guide(self, hotel_data: dict, audit_result: V4AuditResult) -> AssetResult:
    """
    Genera estrategia de redes sociales para hotel boutique.
    
    Redes sociales activas mejoran:
    1. Señales E-E-A-T (Trustworthiness)
    2. Visibilidad en búsquedas locales
    3. Autoridad de contenido
    4. Interacción con potenciales huéspedes
    """
    url = audit_result.url
    hotel_name = hotel_data.get("nombre", "Su Hotel")
    
    # Detectar redes actuales si seo_elements disponible
    redes_actuales = "No detectable"
    if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
        if audit_result.seo_elements.social_links_found:
            redes_actuales = ", ".join(audit_result.seo_elements.social_links_found)
        else:
            redes_actuales = "No se detectaron enlaces a redes sociales"
    
    content = f"""# Estrategia de Redes Sociales para {hotel_name}

## Estado Actual de Presencia Social
{redes_actuales}

## ¿Por qué importan las redes sociales para IAO?

1. **Señales de Confianza**: IA evalúa presencia social como señal de legitimidad
2. **sameAs en Schema.org**: Permite conectar su sitio con redes verificadas
3. **Contenido indexable**: Posts pueden ser citados por LLMs
4. **Señales E-E-A-T**: Demuestra autoridad y trustworthiness

## Plataformas Prioritarias para Hoteles Boutique

### 1. Instagram (PRIORIDAD ALTA)
**Por qué**: Visual, orientado a viajes y experiencias
**Frecuencia mínima**: 3-4 posts/semana + stories diarias
**Contenido sugerido**:
- Fotos del hotel (habitaciones, áreas comunes, vistas)
- Detalles de experiencias únicas
- Contenido detrás de escenas
- Stories con respondiendo preguntas

### 2. Facebook (PRIORIDAD MEDIA-ALTA)
**Por qué**: Audiencia más amplia, especialmente 35+
**Frecuencia mínima**: 2-3 posts/semana
**Contenido sugerido**:
- Ofertas especiales y paquetes
- Eventos y noticias del hotel
- Reseñas y testimonios de huéspedes
- Guías de viaje del destino

### 3. LinkedIn (PRIORIDAD MEDIA)
**Por qué**: Viajes de negocio, eventos corporativos
**Frecuencia mínima**: 1-2 posts/semana
**Contenido sugerido**:
- Noticias de la industria hotelera
- Articles sobre el destino
- Reconocimientos y certificaciones
- Vacantes y cultura del equipo

### 4. TikTok (PRIORIDAD BAJA-MEDIA)
**Por qué**: Audiencia joven en crecimiento
**Frecuencia mínima**: 1-2 videos/semana
**Contenido sugerido**:
- Tours rápidos del hotel
- "Day in the life" del equipo
- Momentos destacados del destino
- Trends adaptados al hotel

## Integración con Schema.org

Agregue sus redes sociales al Hotel Schema:

```json
{{
  "@type": "Hotel",
  "name": "{hotel_name}",
  "url": "{url}",
  "sameAs": [
    "https://www.instagram.com/[cuenta]",
    "https://www.facebook.com/[cuenta]",
    "https://www.linkedin.com/company/[cuenta]"
  ]
}}
```

## Checklist de Implementación

- [ ] Crear cuentas en mínimo 2 plataformas
- [ ] Crear enlace "Síguenos" visible en web (header o footer)
- [ ] Agregar redes sociales al Schema.org del sitio
- [ ] Crear calendario de contenido mensual
- [ ] Definir horarios óptimos de publicación
- [ ] Configurar links UTM para tracking

## Métricas Clave

| Plataforma | Seguidores | Engagement Rate | Respuesta |
|-----------|-----------|-----------------|-----------|
| Instagram | - | >3% | <1 hora |
| Facebook | - | >2% | <2 horas |
| LinkedIn | - | >5% | <24 horas |

## Vinculación con Web

Implemente estos enlaces en su sitio:

```html
<!-- Footer o Header -->
<div class="social-links">
  <a href="https://instagram.com/[cuenta]" target="_blank" rel="noopener">Instagram</a>
  <a href="https://facebook.com/[cuenta]" target="_blank" rel="noopener">Facebook</a>
</div>
```
"""
    
    return AssetResult(
        asset_type="social_strategy_guide",
        content=content,
        generated_at=datetime.now().isoformat(),
        confidence=0.9,
        errors=[],
        warnings=[]
    )
```

---

## Archivos a modificar

| # | Archivo | Cambio |
|---|---------|--------|
| 1 | `asset_catalog.py` | Cambiar 5 assets de `MISSING` a `IMPLEMENTED` |
| 2 | `conditional_generator.py` | Agregar 5 métodos de generación |

---

## Post-Ejecución (OBLIGATORIO)

1. **`06-checklist-implementacion.md`**: Marcar GAP-IAO-01-02-C como completada
2. **Ejecutar**:
```bash
python scripts/log_phase_completion.py \
    --fase GAP-IAO-01-02-C \
    --desc "Implementación de 5 assets IAO: ssl_guide, og_tags_guide, alt_text_guide, blog_strategy_guide, social_strategy_guide" \
    --archivos-mod "modules/asset_generation/asset_catalog.py,modules/asset_generation/conditional_generator.py" \
    --check-manual-docs
```

---

## Criterios de Completitud

- [ ] `ssl_guide` genera contenido válido
- [ ] `og_tags_guide` genera contenido válido
- [ ] `alt_text_guide` genera contenido válido
- [ ] `blog_strategy_guide` genera contenido válido
- [ ] `social_strategy_guide` genera contenido válido
- [ ] Los 5 assets tienen status `IMPLEMENTED` en ASSET_CATALOG
- [ ] Los 5 pain_ids (`no_ssl`, `no_og_tags`, `missing_alt_text`, `no_blog_content`, `no_social_links`) ahora pueden generar assets
- [ ] `log_phase_completion.py` ejecutado
- [ ] Flujo completo IAO funciona: V4AuditResult → DiagnosticSummary → pain_ids → ASSET_CATALOG → conditional_generator

---

## Nota sobre Impacto IAO

Estos 5 assets, aunque son guías (no código), tienen impacto directo en IAO:

| Asset | Impacto IAO |
|-------|-------------|
| `ssl_guide` | SSL es requisito para crawlers modernos |
| `og_tags_guide` | Control sobre cómo IA interpreta contenido social |
| `alt_text_guide` | Imágenes pueden ser "leídas" por IA |
| `blog_strategy_guide` | Contenido fresco = más citas por LLMs |
| `social_strategy_guide` | Señales de autoridad y confianza |
