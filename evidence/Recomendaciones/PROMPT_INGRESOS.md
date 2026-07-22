# === BLOQUE DE CONTEXTO (pegar una vez — se cachea a $1/Mtok) ===

PROYECTO: iah-cli — plataforma agéntica que audita visibilidad digital de hoteles boutique. Detecta fuga de reservas directas a Booking/OTAs/IA, cuantifica en COP (Financial Evidence Engine, 3 escenarios, recovery_factor 35%) y genera assets deployables (JSON-LD, FAQ, llms.txt, OpenGraph, GA4). Pilares: SEO → AEO → IAO → GEO.

NICHO Y MERCADO: Hoteles boutique independientes (10-25 habitaciones), Eje Cafetero, Colombia. ADR regional: $420K COP. Ocupación: 51.2%. Comisiones OTA: 15-25% por reserva. Competencia regional: scores de visibilidad digital 2-3× superiores al cliente típico (GEO 77/100 vs 61/100; SEO 59 vs 25).

VALIDACIÓN: Producto funcional comprobado. Caso piloto "luxorhotel" (Pereira). v4_complete genera resultados dinámicos por hotel — cada ejecución produce sus propios datos en 2 documentos .md + 1 JSON + assets en ZIP. Los números del piloto (de los documentos generados por v4_complete): fuga detectada $3.7M COP/mes (expected_monthly, escenario realista), recuperación proyectada $5M COP/6 meses (curva de maduración 4 pilares GEO→SEO→AEO→IAO × recovery factor 35%), ROI 2.10X (sobre OPEX), score SEO 25/100, 277 reseñas Google 4.1★ (capturadas del GBP por el sistema), 3 brechas principales con COP estimado cada una, pricing $400K COP/mes + $2.5M setup único. Cada hotel nuevo ejecuta v4_complete y obtiene SUS propios números — el caso Luxorhotel es referencia del piloto, no un asset estático reutilizable. Propuesta de valor: "Nosotros implementamos todo. Usted solo atiende huéspedes."

FORMA DE OPERACIÓN: Herramienta CLI (línea de comandos, Python). Yo ejecuto v4_complete por cada hotel — el output es dinámico, no estático: cada cliente recibe sus propios datos (fuga en COP, brechas, scores, pricing). Output: documentos .md + assets compilados en ZIP (entrega post-venta) + PDF gancho de 2 páginas con datos del propio hotel (pre-venta, segundo contacto post-WhatsApp). El cliente no interactúa con la herramienta — recibe los documentos por correo/WhatsApp. Una auditoría completa (v4complete) toma ~20-30 minutos con datos precargados. El PDF gancho se genera en segundos desde el JSON del hotel.

ESTRATEGIA COMERCIAL DOCUMENTADA: Producto 1 — Diagnóstico Express ($120K COP, validación willingness-to-pay). Producto 2 — Implementación ($1.5M-$3.5M COP, solo a quien ya pagó). Producto 2.5/3 — Reporte mensual + seguimiento recurrente (futuro). Métricas 90 días: 3-5 entrevistas, 1-5 Express pagos, 0-1 implementación. Principio: "Manual antes que automático, específico antes que general." No construir SaaS/dashboard hasta tracción validada.

RESTRICCIÓN CRÍTICA: Yo solo, sin equipo. No tengo diseñadores, vendedores ni desarrolladores. Todo lo que se haga debe caber en mis horas disponibles.

# === PROMPT PRINCIPAL ===

Actúa como consultor de monetización B2B especializado en SaaS vertical para hotelería independiente en Latinoamérica. Responde en ESPAÑOL. Solo tablas y bullets, prosa solo donde sea estrictamente necesario. Máximo 600 palabras.

Usa el contexto anterior + tu conocimiento del mercado hotelero colombiano y SaaS B2B. Dame:

1. GAP ANALYSIS (de producto a ingreso): qué falta HOY para generar ingresos recurrentes. El producto y el pricing del piloto están validados. El cuello de botella real es DISTRIBUCIÓN: cómo llegar a hoteleros boutique del Eje Cafetero de forma recurrente sin equipo de ventas. Analiza los gaps alrededor de ese cuello de botella: lead gen sin equipo, empaquetado no técnico, automatización del ciclo de venta, legal/facturación en Colombia, onboarding autoguiado. Separa claramente lo que requiere equipo de lo que puedo hacer YO SOLO.

2. MODELO DE NEGOCIO (2-3 opciones comparadas): para cada opción — precio sugerido (COP), ticket anual estimado, cuántos clientes necesito para $10M COP/mes, ventaja y riesgo principal. Evalúa cuál es viable para UNA PERSONA SOLA.

3. ROADMAP (fases, no tareas): 4-5 fases en orden de prioridad. La Fase 1 debe ser accionable esta semana sin escribir código. Cada fase debe tener: objetivo, acción principal, criterio de avance, estimación de esfuerzo (horas/semana).

4. RIESGOS + MITIGACIÓN (específicos para fundador solo): identifica los 3-4 riesgos más letales y cómo mitigarlos sin contratar.

NO repitas el contexto. NO saludes. Cada recomendación debe asumir "yo solo, sin equipo".

# === MICRO-PREGUNTAS (misma conversación — el contexto YA está cacheado) ===

P2: "Del gap analysis, dame el top 3 de lo que PUEDO resolver yo solo esta semana sin escribir código. Tabla: acción | resultado esperado | horas estimadas | cómo medir si funcionó."

P3: "Toma el modelo de negocio más viable para una persona sola según tu análisis. Desglósalo a fondo: pricing exacto (mínimo 2 tiers), qué incluye cada tier, objeción principal de un hotelero y cómo refutarla, plantilla de propuesta de 5 líneas."

P4: "Roadmap de 30 días en 6 pasos numerados, 1 frase por paso, KPI medible de cada paso. Asume que la Fase 1 ya está completa. Solo acciones que yo pueda ejecutar sin equipo."
