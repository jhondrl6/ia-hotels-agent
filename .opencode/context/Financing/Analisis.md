 ANÁLISIS: Oportunidades sistémicas en iah-cli reveladas por el ejercicio

     El ejercicio hotelero expuso 6 áreas de oportunidad concretas en el repositorio — no bugs técnicos, sino debilidades en cómo el sistema genera, presenta y valida su propio output.
     1. El Financial Engine produce números con falsa precisión

     Lo que pasó:
     - El sistema generó $2.610.000 COP/mes con 8 decimales de desglose ($530.613, $212.193, etc.)
     - El archivo fuente financial_scenarios.json revela internamente: data_sources: {"adr": "legacy_hardcode", "occupancy": "default", "shift": "hardcoded: sin GA4"}
     - El diagnóstico muestra Tier C en el frontmatter pero no propagate esa incertidumbre al desglose de brechas

     Problema sistémico:
     El financial engine calcula分配 proporcional pero el output final se lee como medición real, no como estimación. Un dueño de hotel o un agente comercial puede presentar esos números a un cliente como
     "fact", y lo son menos de lo que parecen.

     Oportunidad:
     - Cuando evidence_tier = "C", el desglose por brecha debería mostrar rangos, no cifras exactas: $400K-$600K/mes en vez de $530.613/mes
     - Agregar un flag en el output: ⚠️ Figura con defaults — usar solo como dirección, no como auditoría
     - El desglose proporcional por brecha es innecesario en Tier C porque no hay granularidad real para soportarlo
     2. El sistema detecta canales pero no los prioriza

     Lo que pasó:
     - El diagnóstico identifica correctamente: WhatsApp verificado (+57 3104019049) y GBP con 203 reviews, 4.5★
     - Pero el plan de acción es 100% SEO/IA — 6 de 8 brechas, cero en WhatsApp
     - El owner señaló que 60-70% de sus reservas último minuto vienen por WhatsApp, y eso no está en el framework

     Problema sistémico:
     El framework tiene un módulo de evidence_ledger que registra qué datos existen, pero no tiene lógica de priorización basada en el mix de canales del negocio. Detecta que WhatsApp existe pero no lo
     usa para pesar las brechas.

     Oportunidad:
     - Crear un channel_weight module que lea el mix de canales del hotel (de onboarding data o GBP)
     - Cuando WhatsApp es >50% del tráfico, las brechas de WhatsApp (velocidad de respuesta, templates, horarios) deberían weighted más alto que SEO genérico
     - Un "quick wins" para alguien cuyo canal principal es WhatsApp es diferente que para alguien en Google Ads
     3. Los "quick wins" no incluyen costo de implementación

     Lo que pasó:
     - El diagnóstico lista: Schema Hotel (1-2 días), FAQ (2-3 días)
     - La realidad Divi/WordPress: 45-90 minutos de trabajo real + mantenimiento
     - Ningún documento del kit incluye: horas estimadas, costo de developer si se externaliza, o costo de oportunidad del owner

     Problema sistémico:
     No existe un implementation_cost_estimator en el pipeline. El output dice "quick" pero no cuantifica qué tan rápido es para alguien que no es desarrollador y tiene 3 horas disponibles entre atender
     huéspedes y gestionar la finca.

     Oportunidad:
     - Agregar a cada brecha: estimated_hours: X, can_owner_do_it: bool, external_cost_cop: Y
     - Crear un flag: quick_for_developer ≠ quick_for_owner
     - Para hotels pequeños con owner-operator, filtrar quick wins a los que son realmente ejecutables sin externalizar
     4. El GEO/AEO scoring no es transparente sobre qué mide

     Lo que pasó:
     - Hotel tiene 203 reviews, 4.5★, respuesta en <24h → GEO = 62/100
     - El owner pregunta: "¿El score considera la calidad de respuestas a reseñas?" → la respuesta real es no, pero el diagnóstico no lo aclara
     - El score baja por fotos y NAP consistency, no por engagement con reviews

     Problema sistémico:
     El scoring usa métricas técnicas (fotos, NAP, schema) pero no hay sección de "qué no mide". No existe un scoring_methodology.md linked desde el output que explique qué pesa 20% vs qué no está en el
     radar.

     Oportunidad:
     - Agregar score_methodology_url o scoring_breakdown en cada métrica: "GEO 62/100 = Fotos(25%) + NAP(30%) + Attributes(20%) + Reviews(10%) + Authority(15%)"
     - Mostrar explícitamente qué factores fueron excluidos del score (calidad de respuestas a reseñas, engagement rate, etc.)
     - Para GBP: documentar que el score no mide review_response_rate ni response_time
     5. El sistema no tiene módulo B2B/relaciones locales

     Lo que pasó:
     - El owner menciona: 40% de ocupación en temporada alta viene de alianzas con operadores de tours de café
     - El diagnóstico no tiene sección para esto
     - El framework completo está construido sobre search/IA/GBP, no sobre relaciones comerciales locales

     Problema sistémico:
     El repositorio asume que la visibilidad digital = SEO + IA + GBP. Para un hotel boutique en el Eje Cafetero, las relaciones con guías de turismo, operadores de tours y fincas son un canal primario
     que no existe en el modelo.

     Oportunidad:
     - Crear un módulo local_partnerships_scoring o b2b_channel_audit
     - Auditar: ¿tiene el hotel alianzas con operadores locales? ¿paquetes cross-selling? ¿referrals documentados?
     - Para la región Eje Cafetero específicamente, este canal puede ser más valioso que cualquier mejora de Schema
     6. No hay workflow de remediación post-diagnóstico

     Lo que pasó:
     - El diagnóstico termina con: "La solución detallada está en 02_PROPUESTA_COMERCIAL.md"
     - La propuesta comercial incluye pricing y garantías
     - No hay guía de implementación paso a paso para un owner-operator que quiera ejecutar sin contratar

     Problema sistémico:
     El pipeline genera diagnosis → propuesta comercial, pero el salto de "lea el diagnóstico" a "implemente Schema Hotel en Divi" no existe como asset. El kit de entrega no incluye un
     IMPLEMENTATION_GUIDE.md targeting non-technical owners.

     Oportunidad:
     - Crear un implementation_guide.md por CMS (Divi/WordPress, Wix, Squarespace, custom)
     - Para cada brecha: screenshot de dónde ir + qué cambiar + cómo verificar que funcionó
     - Incluir sección "验证" (verificación post-implementación) sin necesitar developer
     PRIORIZACIÓN SUGERIDA (impacto vs esfuerzo en el repo)

     | Área | Impacto sistémico | Esfuerzo de implementación | Prioridad |
     |------|------------------|-----------------------------|-----------|
     | Financial Engine: rangos en vez de cifras exactas (Tier C) | Alto — previene uso de datos假 como hechos | Bajo — regex en template | 🔴 Inmediato |
     | Scoring transparency: metodología visible en output | Alto — construye confianza | Medio — requiere refactor de scoring | 🔴 Inmediato |
     | Quick wins con costo de implementación | Alto — diferencia owner vs developer | Medio — nuevo módulo en asset generation | 🟡 Q2 |
     | Channel weight module (WhatsApp/B2B priorization) | Alto — relevance real para hotels pequeños | Alto — nuevo módulo | 🟡 Q2 |
     | Implementation guide por CMS | Medio — mejora conversión a implementación | Medio — templates por CMS | 🟢 Q3 |
     | B2B/Local partnerships module | Medio — diferenciado para Eje Cafetero | Alto — nuevo módulo completo | 🟢 Q3 |
     CONCLUSIÓN

     El ejerciciohotelero usó el diagnóstico como proxy para testear la madurez del framework, y lo que reveló es que iah-cli es más fuerte en detección técnica que en context-aware priorization. Detecta
     8 brechas con precisión técnica, pero las pesa con el mismo peso sin importar el mix de canales del hotel, el rol del owner, o la realidad operativa regional.

     La mayor oportunidad no es agregar más métricas — es hacer que las existentes se adapten al contexto específico del hotel antes de presentar el output.