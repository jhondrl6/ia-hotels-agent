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
- 🔗 **Red de referencia verificada (opt-in)**: Permitir que hoteles participantes vean (anonimizado, agregado) cómo hoteles similares mejoraron su score tras implementar ciertas mejoras (ej: "Hoteles que mejoraron su GBP subieron 0.15 en coherence en promedio").
- 📈 **Benchmark dinámico regional**: Actualizar rangos de referencia mensualmente usando nuevos datos de alta confianza (VERIFIED) de hoteles en la misma zona.
- 🛡️ **Modo cumplimiento turístico**: Validar automáticamente alignment con leyes locales de publicidad turística, precios mostrados y privacidad de datos (ej: Ley de Protección de Datos Personales en Colombia, GDPR para turistas EU).
- 🧠 **Asistente de implementación**: Guiar paso a paso al hoteleros en la puesta en marcha de assets recomendados (ej: "Así insertas el botón de WhatsApp en tu WordPress").
- ⚡ **Modo lite para emergencias**: Versión ultra-rápida (<90s) que da solo hook + recomendación crítica cuando se necesita velocidad absoluta (ej: en llamadas de ventas).
- 🔌 **Ecosistema de skills comunitario**: Permitir que terceros contribuyan con skills específicos (ej: análisis de sostenibilidad, acceso para discapacitados, energía renovable) bajo el framework of truth-first and explicit confidence.

---

> *Próxima revisión estratégica: 2026-06-19*  
> *Responsable: Equipo de Producto, Arquitectura y Calidad de iah-cli*  
> *Este documento vive en el repositorio y debe reflejarse en cada planning trimestral.*