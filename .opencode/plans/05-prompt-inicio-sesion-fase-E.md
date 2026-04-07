# FASE-E: Micro-Content Local Generator

**ID**: FASE-E  
**Objetivo**: Generador de paginas de contenido local (3-5 por hotel) orientadas a keywords de alto valor para hoteles boutique, como add-on comercial al Kit Hospitalidad Digital.  
**Dependencias**: FASE-B ✅ (content pasa por quality gate)  
**Duracion estimada**: 2-3 horas  
**Skill**: `phased_project_executor` v2.3.0

---

## Contexto

### Por que esta fase es necesaria

Los hoteles boutique del Eje Cafetero NO necesitan 20 articulos de blog (patron seomachine). Necesitan 3-5 paginas que capturen busquedas locales de alto valor:

```
"termales santa rosa de cabal precios"     → 1.200 busquedas/mes
"hotel boutique cerca termales"            → 800 busquedas/mes  
"donde hospedarse en santa rosa de cabal"  → 600 busquedas/mes
"hotel con termales incluidas"             → 400 busquedas/mes
```

Estas paginas son:
- FACILES de posicionar (long-tail local, poca competencia)
- CONVierten bien (el que busca ya quiere reservar)
- El hotelero NO las va a escribir solo
- Son un ADD-ON vendible ($50K COP extra por 3 paginas)

### Inspiracion

Adaptacion simplificada de seomachine `topic_cluster_strategy.md`:
- NO pillar cluster de 20 articulos (eso es para SaaS)
- SI micro-contenido local (3-5 paginas por hotel)
- Cada pagina: keyword target + schema Article + link a reservas directas

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |

### Base Tecnica Disponible

- `modules/asset_generation/` — Generadores existentes con patron condicional
- `modules/asset_generation/asset_catalog.py` — Catalogo de tipos de asset
- `modules/providers/` — LLM providers (DeepSeek/Anthropic)
- Templates en `templates/` — Patrones de generacion
- Content Scrubber (FASE-B) — Limpieza post-generacion
- Tests base: 1782 + 22 (D) + 14 (E) + 18 (F)

---

## Tareas

### Tarea 1: Crear Local Content Generator

**Objetivo**: Generador de paginas de contenido local orientadas a keywords.

**Archivos afectados**:
- `modules/asset_generation/local_content_generator.py` (NUEVO)

**Estructura**:

```python
# modules/asset_generation/local_content_generator.py

@dataclass
class LocalContentPage:
    keyword_target: str          # "termales santa rosa de cabal"
    title: str                   # "Guia de Termales de Santa Rosa de Cabal 2026"
    slug: str                    # "termales-santa-rosa-de-cabal"
    content_md: str              # Contenido markdown 800-1200 palabras
    schema_article: dict         # JSON-LD Article schema
    internal_links: List[str]    # Links a pagina principal y reservas
    meta_description: str        # 150-160 chars
    word_count: int

@dataclass
class LocalContentSet:
    hotel_name: str
    location: str
    pages: List[LocalContentPage]
    total_word_count: int

class LocalContentGenerator:
    """Generates local content pages for boutique hotels."""
    
    # Templates de keywords por tipo de hotel/ubicacion
    KEYWORD_TEMPLATES = {
        "termales": [
            "termales {location} precios",
            "hotel cerca termales {location}",
            "que llevar a termales {location}",
        ],
        "boutique": [
            "hotel boutique {location}",
            "donde hospedarse en {location}",
            "mejor hotel boutique {region}",
        ],
        "general": [
            "que hacer en {location}",
            "como llegar a {location}",
            "restaurantes cerca de {location}",
        ]
    }
    
    CONTENT_RULES = {
        "word_count_min": 800,
        "word_count_max": 1200,
        "internal_links_min": 2,     # Link a home + link a reservas
        "heading_count_min": 4,      # H2 sections
        "paragraph_max_sentences": 4, # Legibilidad
    }
    
    def generate_content_set(self, hotel_data: dict, hotel_type: str = "boutique",
                              location_context: dict = None) -> LocalContentSet:
        """Generate 3-5 local content pages for a hotel."""
        
        # 1. Seleccionar keyword templates segun tipo de hotel
        keywords = self._select_keywords(hotel_data, hotel_type, location_context)
        
        # 2. Generar pagina por keyword (via LLM)
        pages = []
        for kw in keywords[:5]:  # Max 5 paginas
            page = self._generate_page(kw, hotel_data, location_context)
            pages.append(page)
        
        return LocalContentSet(
            hotel_name=hotel_data.get("name", ""),
            location=hotel_data.get("city", ""),
            pages=pages,
            total_word_count=sum(p.word_count for p in pages)
        )
    
    def _generate_page(self, keyword: str, hotel_data: dict, 
                        location_context: dict) -> LocalContentPage:
        """Generate a single local content page via LLM."""
        
        # Prompt al LLM:
        # - Eres experto en contenido turistico local
        # - Escribe sobre {keyword} en {location}
        # - Menciona naturalmente {hotel_name} como opcion de hospedaje
        # - Incluye link a reservas directas (WhatsApp)
        # - Longitud: 800-1200 palabras
        # - Estructura: intro + 4 secciones H2 + conclusion
        # - Tono: informativo, no vendedor (el hotel se menciona naturalmente)
        # - Idioma: espanol neutro latinoamericano
        
        pass
    
    def _select_keywords(self, hotel_data, hotel_type, location_context) -> list:
        """Select best keywords based on hotel type and location."""
        # Combinar templates de "termales" + "boutique" + "general"
        # Rellenar {location} y {region} con datos reales
        # Priorizar por volumen estimado (heuristica basada en tipo)
        pass
    
    def _generate_article_schema(self, page: LocalContentPage, 
                                  hotel_data: dict) -> dict:
        """Generate JSON-LD Article schema for the page."""
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page.title,
            "description": page.meta_description,
            "author": {
                "@type": "Organization",
                "name": hotel_data.get("name", "")
            },
            "publisher": {
                "@type": "Organization", 
                "name": hotel_data.get("name", "")
            }
        }
```

**Criterios de aceptacion**:
- [ ] Genera 3-5 paginas por hotel
- [ ] Cada pagina tiene keyword target, titulo, slug, contenido, schema
- [ ] Contenido 800-1200 palabras
- [ ] Mencion natural del hotel (no vendedora)
- [ ] Link a reservas directas (WhatsApp)
- [ ] Schema Article JSON-LD generado
- [ ] Pasa por Content Scrubber (FASE-B)

### Tarea 2: Registrar en Asset Catalog

**Objetivo**: Agregar `local_content_page` como tipo de asset en el catalogo.

**Archivos afectados**:
- `modules/asset_generation/asset_catalog.py` (MODIFICAR)

**Cambios**:
- Agregar `local_content_page` al enum/catalogo de tipos
- Agregar metadata: formato (.md), dependencias (hotel_data), es_condicional (True)

**Criterios de aceptacion**:
- [ ] `local_content_page` aparece en el catalogo
- [ ] `is_asset_implemented("local_content_page")` retorna True

### Tarea 3: Crear Templates

**Objetivo**: Templates de prompts para generacion de contenido local.

**Archivos afectados**:
- `templates/local_content/page_template.md` (NUEVO)
- `templates/local_content/keyword_selection.md` (NUEVO)

**Contenido del page_template.md**:
```markdown
## Prompt Template: Local Content Page

Eres un escritor de contenido turistico local para el Eje Cafetero colombiano.

CONTEXTO:
- Hotel: {hotel_name} ({hotel_type})
- Ubicacion: {city}, {state}
- Keyword objetivo: {keyword}
- Servicios: {services}

REGLAS:
1. Escribe 800-1200 palabras sobre {keyword}
2. Menciona {hotel_name} naturalmente como opcion de hospedaje (NO vendedor)
3. Incluye informacion util y verificable sobre la zona
4. Estructura: intro + 4 secciones H2 + conclusion con CTA suave
5. Agrega link: "Para reservar: [WhatsApp {hotel_name}](https://wa.me/{phone})"
6. Tono: informativo, calido, local (no corporativo)
7. Idioma: espanol neutro latinoamericano
8. SIN frases genericas AI ("en el vibrante corazon", "descubre la magia")

OUTPUT FORMAT: Markdown con frontmatter YAML
```

**Criterios de aceptacion**:
- [ ] Templates existen en `templates/local_content/`
- [ ] Son referenciados por `LocalContentGenerator`

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| Test keyword selection termales | `tests/asset_generation/test_local_content_generator.py` | Genera keywords con {location} reemplazado |
| Test keyword selection boutique | `tests/asset_generation/test_local_content_generator.py` | Genera keywords de hotel boutique |
| Test page structure | `tests/asset_generation/test_local_content_generator.py` | Tiene titulo, slug, contenido, schema |
| Test word count range | `tests/asset_generation/test_local_content_generator.py` | 800-1200 palabras por pagina |
| Test internal links | `tests/asset_generation/test_local_content_generator.py` | Minimo 2 links (home + reservas) |
| Test article schema | `tests/asset_generation/test_local_content_generator.py` | JSON-LD Article valido |
| Test hotel mention natural | `tests/asset_generation/test_local_content_generator.py` | Hotel mencionado pero no vendedor |
| Test content scrubber pass | `tests/asset_generation/test_local_content_generator.py` | Pasa quality gate de FASE-B |
| Test max 5 pages | `tests/asset_generation/test_local_content_generator.py` | No genera mas de 5 paginas |
| Test asset catalog entry | `tests/asset_generation/test_local_content_generator.py` | local_content_page en catalogo |

**Comando de validacion**:
```bash
python -m pytest tests/asset_generation/test_local_content_generator.py -v
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`** — Marcar FASE-A como ✅ Completada
2. **`06-checklist-implementacion.md`** — Marcar todos los items de FASE-A como ✅
3. **`09-documentacion-post-proyecto.md`** — Secciones A, B, D, E
4. **Ejecutar**: `python scripts/log_phase_completion.py --fase FASE-A --desc "Micro-Content Local Generator" --archivos-nuevos "modules/asset_generation/local_content_generator.py,templates/local_content/page_template.md,templates/local_content/keyword_selection.md,tests/asset_generation/test_local_content_generator.py" --archivos-mod "modules/asset_generation/asset_catalog.py" --tests "10" --check-manual-docs`

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: 10/10 tests
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa
- [ ] **Sin regresiones**: Tests existentes siguen pasando
- [ ] **Prueba real**: Generar 3 paginas para Hotel Visperas con keywords de Santa Rosa de Cabal
- [ ] **Contenido limpio**: Pasa content scrubber sin warnings
- [ ] **Asset catalog**: local_content_page registrado
- [ ] **dependencias-fases.md actualizado**
- [ ] **Documentacion afiliada**: CHANGELOG.md, AGENTS.md
- [ ] **Post-ejecucion completada**: log_phase_completion.py ejecutado

---

## Restricciones

- NO generar mas de 5 paginas por hotel (no es un blog completo)
- NO usar keywords competitivos genericos ("hotel Colombia")
- SI usar long-tail local ("hotel boutique termales santa rosa de cabal")
- El contenido pasa por Content Scrubber (FASE-B) antes de entrega
- NO es una fase bloqueante — es add-on comercial
- El LLM debe usar prompt en espanol neutro (no argentino, no espanol)
- Sin datos reales de volumen de busqueda (usar heuristica por tipo de keyword)

---

## Prompt de Ejecucion

```
Actua como desarrollador Python senior especializado en generacion de contenido SEO local.

OBJETIVO: Implementar FASE-A — Micro-Content Local Generator para iah-cli.

CONTEXTO:
- Proyecto: iah-cli v4.22.0+ (FASE-A,D,E,F completadas)
- Cliente: Hoteles boutique pequenos del Eje Cafetero
- Necesidad: 3-5 paginas de contenido local por hotel
- LLM disponible: DeepSeek/Anthropic via providers existentes
- Content Scrubber activo (FASE-B)

TAREAS:
1. Crear modules/asset_generation/local_content_generator.py
2. Crear templates/local_content/page_template.md + keyword_selection.md
3. Modificar modules/asset_generation/asset_catalog.py
4. Crear 10 tests en tests/asset_generation/test_local_content_generator.py

CRITERIOS:
- 3-5 paginas por hotel, 800-1200 palabras cada una
- Keywords long-tail locales (no genericos)
- Mencion natural del hotel (no vendedora)
- Schema Article JSON-LD por pagina
- Link a reservas directas (WhatsApp)
- Pasa content scrubber
- Espanol neutro latinoamericano

VALIDACIONES:
- pytest tests/asset_generation/test_local_content_generator.py -v (10/10)
- python scripts/run_all_validations.py --quick
```
