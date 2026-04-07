## 🧠 Hotel Graph — Knowledge Graph para el Dominio Hotelero (Iniciativa Estratégica v5.0)

> Inspirado por el patrón de knowledge graph de GitNexus (grafo de código → insights), adaptado al dominio hotelero: entidades, métricas, canales y recomendaciones conectados en un grafo consultable.

### Visión

Construir un **grafo de conocimiento hotelero** donde cada nodo es una entidad del dominio (canal, metrica, servicio, tipo de huésped, activo digital) y cada arista es una relación cuantificada (AFECTA, OPTIMIZA, GENERA, DEPENDE_DE). Esto permite:

- **Análisis de impacto en lenguaje natural**: "¿Qué pasa con el revenue si elimino photos de GBP?" → traza todas las aristas descendentes.
- **Recomendaciones justificables por grafo**: cada score en el diagnóstico se explica como path en el grafo, no como número mágico.
- **Detección automática de comunidades**: clusteres tipo Leiden agrupan servicios correlacionados (ej: "termas + gastronomía + experiencias de café" se detectan como comunidad sin configuración manual).
- **Impact propagation**: cambiar un input (ej: occupancy_rate) propaga por el grafo → actualiza todos los scores, proyecciones y assets afectados.
- **Consultas estructuradas**: "¿Qué métricas dependen de reviews_score?" → respuesta determinística del grafo, no del LLM.

### Arquitectura propuesta

```
Hotel Graph (LadybugDB o Neo4j local)
├── Nodos
│   ├── Canal (booking_channel, GBP, sitio_web, OTAs, PMS)
│   ├── Metrica (geo_score, coherence_score, occupancy_rate, ADR, RevPAR, review_rating)
│   ├── Activo (faq_page, org_schema, aeo_faq, whatsapp_widget, booking_engine)
│   ├── Servicio (restaurante, spa, pool, wifi, tours, termas)
│   ├── HuéspedTipo (business, leisure, couple, family, digital_nomad)
│   ├── Fuente (ga4, profound, semrush, places_api, pagespeed, manual)
│   └── Dolor (low_visibility, no_booking_engine, outdated_photos, no_ga4)
├── Aristas (CodeRelation → HotelRelation)
│   ├── AFECTA (metrica → metrica, con peso cuantificable)
│   ├── OPTIMIZA (activo → metrica, con ganancia estimada)
│   ├── DEPENDE_DE (metrica → fuente, con nivel de confianza)
│   ├── GENERA (dolor → pérdida_estimada en COP)
│   └── PERTENECE_A (servicio → comunidad funcional)
└── Motores
    ├── CommunityDetector (Leiden algorithm sobre el grafo hotelero)
    ├── ImpactAnalyzer (blast radius de cambios en inputs)
    ├── RecommendationEngine (paths de optimización de mayor ROI)
    └── NaturalQuery (BM25 + embeddings sobre nodos/aristas para preguntas en lenguaje natural)
```

### Fases de implementación (con milestones por escala de clientes)

| Fase | Entregable | Dependencias | Estimación | Disparador de inicio |
|------|-----------|-------------|-----------|---------------------|
| **HG-01: Schema Definition** | Definir nodos, aristas, propiedades. Script que genera schema desde data_models/ actuales | data_models/canonical_assessment.py, aeo_kpis.py | 1 sesión | 5+ hoteles activos |
| **HG-02: Graph Builder** | Python module que lee output/v4_complete/*.json → construye grafo en memoria (NetworkX) | HG-01 | 1-2 sesiones | HG-01 completada |
| **HG-03: Persistence Layer** | Persistir grafo en LadybugDB (.gitnexus equivalente) o SQLite con extension graph | HG-02 | 1 sesión | HG-02 completada |
| **HG-04: Impact Analyzer** | Función `analyze_impact(cambio) → blast_radius, métricas_afectadas, riesgo` | HG-03 | 1 sesión | 10+ hoteles activos |
| **HG-05: Community Detection** | Leiden sobre grafo hotelero → agrupación automática de áreas del negocio | HG-03 | 1 sesión | 15+ hoteles activos |
| **HG-06: Diagnostic Integration** | Reemplazar scores numéricos aislados → scores explicados como paths en el grafo | HG-02, HG-04 | 2 sesiones | 20+ hoteles activos |
| **HG-07: NaturalQuery** | BM25 + embeddings sobre grafo → preguntas como "¿por qué mi review_score es bajo?" | HG-03, embeddings locales | 1-2 sesiones | 25+ hoteles activos |
| **HG-08: Regional Graph** | Grafo multi-hotel anonimizado del Eje Cafetero → benchmark real, no estático | HG-03, 5+ hoteles indexados | Futuro | 25+ hoteles activos (piloto ya corriendo) |

**Criterio de parada por fase**: No avanzar a la siguiente HG hasta cumplir el disparador de escala O hasta que el beneficio comercial sea verificable (hotelero pide explicacion del score, necesita benchmark regional, etc.).

### Patrones aprendidos de referencia

| Fuente | Patrón | Adaptación a Hotel Graph |
|--------|--------|------------------------|
| GitNexus | Code graph con Tree-sitter | Hotel graph con canonical_assessment + GA4 + GBP como "parsers" |
| GitNexus | Leiden communities (áreas funcionales) | Clusteres hoteleros: F&B, Rooms, Digital, F&E detectados automáticamente |
| GitNexus | Execution flows (entry → terminal) | Cadena de impacto: "Baja en reviews → menos clicks GBP → menos ocupación → menor revenue" |
| GitNexus | Hybrid search (BM25 + vectors) | Preguntas sobre el grafo en lenguaje natural del hotelero |
| GitNexus | Impact analysis (blast radius) | "Si subes precio 15%, ¿qué scores cambian y en cuánto?" |
| Goose | 82 providers, canonical models | Canonical metrics: normalizar nombres de métricas entre fuentes (GA4 vs SerpAPI vs manual) |
| Goose | Recipes (YAML workflows) | HotelGraph queries predefinidas: "auditoria_rapida", "benchmark_regional", "impacto_cambio" |

### Principios de diseño

1. **Grafo vivo, no snapshot**: se actualiza con cada análisis v4complete. Historial de cambios en el tiempo.
2. **Explicabilidad sobre complejidad**: el hotelero debe entender en 10 segundos por qué su score es X.
3. **Honesto por defecto**: si una arista no tiene datos reales, usa `ESTIMATED` con nota explicativa. Nunca inventar conexiones.
4. **Dominio primero**: este grafo NO es un grafo de código. Es un modelo mental del negocio hotelero del Eje Cafetero.
5. **Complemento, no reemplazo**: el Hotel Graph potencia el pipeline existente (v4complete → diagnóstico → propuesta → assets). No lo reemplaza.

### Métricas de éxito para Hotel Graph

| Métrica | Objetivo | Por qué importa |
|---------|----------|----------------|
| % de scores del diagnóstico explicables como path en el grafo | ≥ 90% | Elimina "números mágicos" del scorecard |
| Tiempo de respuesta query natural sobre grafo | < 500ms | Experiencia fluida en CLI y portal |
| Comunidades detectadas con coherencia > 0.7 | ≥ 3 por hotel | Demuestra que el grafo captura estructuras reales del negocio |
| Impact predictions correctas (vs resultado real) | ≥ 80% | Confianza en recomendaciones del sistema |

---

## 📊 Métricas de Éxito (OKRs Trimestrales)

| Métrica | Objetivo Q2 2026 | Umbral de éxito | Frecuencia de medición |
|--------|------------------|-----------------|------------------------|
| Coherence Score promedio (entre análisis) | ≥ 0.86 | ≥ 0.80 | Por análisis completado |
| Tiempo medio de ejecución por hotel | < 6.5s | < 8s | Medido en CI y producción |
| % de activos generados como VERIFIED (vs ESTIMATED/BLOCKED) | ≥ 65% | ≥ 50% | Por lote de generación |
| Hoteles activos (uso mensual activo del CLI o portal) | 25 | 15 | Mensual |
| NPS de usuarios técnicos (desarrolladores, consultores que integran) | ≥ 45 | ≥ 35 | Trimestral, encuesta breve |
| Tests de regresión pasando (suite completa) | 100% | ≥ 95% | En cada push a main and release |
| Tiempo de onboarding para nuevo usuario técnico | < 15 min | < 30 min | Medido en nuevos contribuyentes |
| Precio/Pérdida estimado (financiero) | Rango 3x-6x mantenido | 3x-6x | Por escenario financiero generado |
| Cobertura de evidencia (claims con soporte / total) | ≥ 96% | ≥ 95% | Por análisis completo |

---

## 📣 Habilitadores de Crecimiento y Adquisición (Enfoque: Eje Cafetero, Colombia)

Estas iniciativas no son tácticas de marketing, pero **crean las condiciones para que el marketing y las ventas escalen eficientemente en tu nicho inicial** (Santa Rosa de Cabal, Pereira, Dosquebradas y alrededores):

- **🟢 Portal de auto-servicio con diagnóstico gratis**:  
  Permite que hoteles de finca, boutique y termales del Eje Cafetero suban su GBP y obtengan un informe inicial de visibilidad digital sin costo.  
  → Canal de captación de leads calificados: identifica quiénes están activos en línea y qué tan bien presentan su propuesta de valor (café, paisaje, termalismo).

- **🟢 Guía de interpretación de reporte para no-técnicos (en español, tono cercano)**:  
  Diseñada para gerentes de hoteles familiares, dueños de fincas cafeteras o administradores de alojamientos rurales.  
  → Reduce la brecha técnica: un propietario puede entender por qué su hotel no aparece en búsquedas de “termales en Santa Rosa” o “café tourism en Pereira” sin necesidad de un consultor.  
  → Habilita ventas self-serve y reduce costo de adquisición (CAC).

- **🟢 Exportar propuesta a Notion, Google Docs y Pipedrive (con branding opcional del hotel)**:  
  Un agente o consultor local puede generar una propuesta profesional y enviarla directamente al hoteleros — o usarla en reuniones con asociaciones como Cotelco, Cámara de Comercio de Pereira, o fondos de turismo del Eje Cafetero.  
  → Aumenta profesionalismo percibido y facilita el cierre.

- **🟢 Índice trimestral de "Salud Digital Hotelera del Eje Cafetero" (anonimizado)**:  
  Publica un reporte sencillo cada 3 meses con métricas agregadas (ej: "Hoteles en Pereira tienen promedio de coherence 0.62; quienes actualizan su GBP semanalmente suben a 0.78").  
  → Posiciona a iah-cli como fuente de conocimiento local.  
  → Ideal para compartir en boletines de turismo del departamento, eventos de la Alcaldía, o redes de hotelería del Risaralda.  
  → Puede generar menciones en medios locales (La Patria, Otú, El Diario del Sur).

- **🟢 Conector sencillo para PMS populares en el eje (ej: sistemas usados en hoteles termales y fincas cafeteras)**:  
  Integración ligera con herramientas de gestión de reservas (incluso si son locales o basadas en Excel/web simple) para extraer datos de ocupación, ADR, origen de reservas.  
  → Enriquece el input de validación con datos operativos reales.  
  → Hace que el producto se sienta "hecho para nuestro contexto", no una solución genérica importada.

- **🟢 Mensaje de valor diferenciado para el Eje Cafetero**:  
  En materiales de comunicación (aún por crear), destacar:  
  _"No solo te decimos si estás en Google — te ayudamos a ser encontrado por quienes buscan vivir el café, no solo tomar un taza."_  
  → Vincula lo digital con lo auténtico: tu presencia online debe reflejar lo que hace único al Eje Cafetero.

- **🟢 Piloto cerrado con 5-10 hoteles del eje (con seguimiento de resultados)**:  
  Ofrecer análisis completo + activos + soporte de implementación a cambio de:  
  - Permiso para usar resultados anonimizados en el índice regional  
  - Testimonio breve (video o texto) si hay mejora medida  
  - Sugerencias para mejorar la herramienta  
  → Genera **casos de uso reales, confianza local y defensores del producto** en tu zona de influencia.

> Estos habilitadores están diseñados para que, cuando llegue el momento de escalar (marketing pagos, alianzas con OTAs locales, participación en ferias de turismo), el producto ya tenga traction, credibilidad y material real para contar una historia de valor:  
> _"No vendemos diagnósticos — ayudamos a los hoteles del Eje Cafetero a ser encontrados por quienes realmente valoran lo que ofrecen."_

---

## 🔧 Deuda Técnica y Mejoras Pendientes

> Temas identificados que requieren atencion pero no son urgentes.

- **Ortogonalidad de metricas en pipeline legacy (gbp_auditor.py)**: El `gbp_auditor.py:_calcular_activity_score` (usado por `report_builder.py`) mide una mezcla entre completitud y engagement que no es ortogonal al GEO score. El pipeline `v4complete` ya usa el score competitivo corregido en `v4_diagnostic_generator.py`. Cuando se active ese pipeline legacy, aplicar el mismo principio de metricas independientes. Tracking: CHANGELOG v4.22.0.

---

## 🔭 Exploración Futura (No comprometido – Ideas a largo plazo)

> Estas son líneas de investigación o experimentación que **no están comprometidas aún**, pero que vale la pena seguir.

- 🤖 **Modo autónomo semanal**: Ejecutar análisis completo cada lunes por la mañana y notificar cambios significativos en coherence, ranking o assets.
- 🌐 **Multi-idioma nativo**: Generar diagnóstico, propuesta y assets automáticamente en inglés y portugués (además de español), con validación cruzada en fuentes locales.
|- ~~🔗 Red de referencia verificada (opt-in)~~ — **Absorbido por Hotel Graph HG-08: Regional Graph**. El grafo multi-hotel anonimizado cubre esta capacidad con más precisión: no solo comparaciones agregadas sino paths de impacto reales entre hoteles similares.
|- ~~📈 Benchmark dinámico regional~~ — **Absorbido por Hotel Graph HG-05 + HG-08**. La deteccion de comunidades (Leiden) + el grafo regional hacen que los benchmarks sean automaticamente dinamicos y basados en estructura, no en rangos estaticos.
- 🛡️ **Modo cumplimiento turístico**: Validar automáticamente alignment con leyes locales de publicidad turística, precios mostrados y privacidad de datos (ej: Ley de Protección de Datos Personales en Colombia, GDPR para turistas EU).
- 🧠 **Asistente de implementación**: Guiar paso a paso al hoteleros en la puesta en marcha de assets recomendados (ej: "Así insertas el botón de WhatsApp en tu WordPress").
- ⚡ **Modo lite para emergencias**: Versión ultra-rápida (<90s) que da solo hook + recomendación crítica cuando se necesita velocidad absoluta (ej: en llamadas de ventas).
- 🔌 **Ecosistema de skills comunitario**: Permitir que terceros contribuyan con skills específicos (ej: análisis de sostenibilidad, acceso para discapacitados, energía renovable) bajo el framework of truth-first and explicit confidence.

---

> *Próxima revisión estratégica: 2026-06-19*  
> *Responsable: Equipo de Producto, Arquitectura y Calidad de iah-cli*  
> *Este documento vive en el repositorio y debe reflejarse en cada planning trimestral.*