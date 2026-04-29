Perfecto, las 3 auditorías completadas. Voy a sintetizar todo.
     RESULTADO DE AUDITORÍA COMPLETA
     Context: 02_PROPUESTA_COMERCIAL vs Código Real
     CONFIRMACIÓN DE HALLAZGOS EXISTENTES

     BUG-1 (ROI sin "X"): ✅ CONFIRMADO
       v4_proposal_generator.py L556: roi_6m.replace("X","") lo quita.
       Template v6 L98: ${roi_6m} no lo re-agrega.
       NOTA: el template v4 SÍ lo hacía bien (${roi_6m}X). Es regresión v4→v6.

     BUG-2 (Beneficio neto $0): ✅ CONFIRMADO y PEOR de lo reportado
       No es solo pain_ratio=0.05. Hay DOUBLE DISCOUNT:
       - pain_ratio=0.05 → gain = 130,500 = exactamente el investment
       - recovery_factor=0.20 → reduce aún más el ROI efectivo a ~1%
       - Resultado: ROI 0.2X, beneficio neto $0 en 6 meses
       El documento NO explica NINGUNO de estos factores.

     DISCREPANCIA-1 (6 vs 7 servicios): ✅ CONFIRMADA
       SERVICE_CATALOG: 7 base + 1 condicional (aeo<20)
       PROPOSAL_SERVICE_TO_ASSET: 7 entries
       Gate usa mapping estático (6) vs propuesta dinámica (7+1)

     HARDCODED (tabla del contexto): ✅ CONFIRMADA, pero INCOMPLETA ↓
     NUEVOS HALLAZGOS (no estaban en el contexto)
     🔴 CRÍTICOS NUEVOS

     H-1: web_score "85" HARDCODEADO como placeholder
       Archivo: v4_proposal_generator.py L554
       Texto: "ideally from audit" (comentario del dev)
       IMPACTO: si no viene audit_result, usa 85 como score SEO.
       El 01_DIAGNOSTICO dice seo_score=25. Si falla el paso de datos,
       la propuesta mostraría 85 en vez de 25.

     H-2: two_phase_flow.py L553 tiene "+57 300 123 4567"
       Otro placeholder de teléfono en código de producción.
       NO detectado en el contexto original.

     H-3: blog_activo = False SIEMPRE (hardcoded)
       v4_diagnostic_generator.py L1964
       El diagnóstico NUNCA detecta blog activo, sin importar la web.

     H-4: speakable_schema = False SIEMPRE (hardcoded)
       v4_diagnostic_generator.py L2030
       IAO score pierde puntos por algo que nunca se evalúa.

     H-5: ga4_indirect = False SIEMPRE (hardcoded)
       v4_diagnostic_generator.py L2083
       Mismo patrón: stub que nunca cambia.

     H-6: Evidence Tier SIEMPRE "C" (sin GA4)
       scenario_calculator.py L443
       No importa qué datos reales existan, el tier es siempre el peor.
     🔴 DOCUMENTALES (AGENTS.md vs realidad)

     H-7: AGENTS.md se CONTRADICE sobre test count
       - Línea 104 dice: "2224 funciones, 140 archivos"
       - Líneas 346, 361, 438 dicen: "1782 funciones, 140 archivos"
       - Conteo real: 2363 funciones, 185 archivos
       - TRES números diferentes, TODOS incorrectos.

     H-8: AGENTS.md documenta SOLO 5 gates, código tiene 9
       publication_gates.py define 9 gates (6 blocking + 3 advisory).
       AGENTS.md solo menciona 5. Faltan: ethics, content_quality,
       asset_confidence, proposal_asset_alignment.
     🟡 HARDCODED QUE FALTABAN EN EL CONTEXTO

     | # | Elemento | Archivo:Línea | Severidad |
     |---|----------|---------------|-----------|
     | H-9 | MONTHLY_PACKAGE_PRICE=1,200,000 | proposal L52 | HIGH |
     | H-10 | SETUP_FEE=2,500,000 | proposal L53 | HIGH |
     | H-11 | benchmark_score=58 | proposal L1035 | HIGH |
     | H-12 | score_tecnico fallback=50 | proposal L568/L981 | HIGH |
     | H-13 | coherence fallback='70' | proposal L564 | HIGH |
     | H-14 | recovery_factor: 0.15/0.20/0.25 | proposal L519/486/523 | HIGH |
     | H-15 | ROI cap 5.0X | proposal L929 | MEDIUM |
     | H-16 | break_even default=6 meses | proposal L936 | MEDIUM |
     | H-17 | Scenario weights 70/20/10 | proposal L1096 | HIGH |
     | H-18 | Price floor 800K / ceiling 2.5M | proposal L1099 | HIGH |
     | H-19 | TIER_CONFIG completo hardcoded | pricing_calculator L48-68 | HIGH |
     | H-20 | degradation_rate=2%/mes | loss_projector L65 | HIGH |
     | H-21 | Shift OTA→direct: 5/10/20% | scenario_calculator L178/243/286 | HIGH |
     | H-22 | IA boost: 5/10% | scenario_calculator L248/287 | HIGH |
     | H-23 | Discount 10% trimestral / 18% semestral | template L171-172 | HIGH |
     | H-24 | 3 cuotas sin interés | template L168 | LOW |
     | H-25 | Guarantee 90 días / 10% / 15 días | proposal L959-974 | MEDIUM |
     | H-26 | plan text stubs (7d/30d/60d) | diagnostic L414-417 | HIGH |
     | H-27 | voice_readiness fallback='0' | diagnostic L613 | HIGH |
     🟢 VERIFICACIONES POSITIVAS (lo que SÍ funciona bien)

     - Coherence score: 0.8933 en 01, 0.8933 en v4_complete_report → CONSISTENTE
     - Financial scenarios: $2.610.000 y $130.500 alineados entre JSONs y propuesta → OK
     - WhatsApp SitePresenceChecker: verificado correctamente en producción → OK
     - Tier "boutique": existe en código, pricing_calculator lo define → OK
     - Template embebido (CV5): ya corregido, _load_template() levanta error → OK
     - Scale bug (0-1 vs 0-100): NO encontrado en ejecución actual → OK
     ¿QUÉ AMERITA INTERVENCIÓN INMEDIATA?

     PRIORIDAD 1 (bloquea credibilidad del entregable):
       BUG-1: Quitar .replace("X","") de L556 → 1 línea
       BUG-2: El ROI 0.2X es matemáticamente correcto pero comercialmente
              inaceptable. Necesita O ajustar pain_ratio/recovery_factor O
              agregar texto explicativo en la sección de proyección.

     PRIORIDAD 2 (datos falsos en entregable):
       H-1: web_score "85" placeholder → usar audit_result real
       H-3/H-4/H-5: blog/speakable/ga4 siempre False → evaluar o documentar
       H-6: Evidence Tier siempre "C" → integrar GA4 o justificar

     PRIORIDAD 3 (documentación desactualizada):
       H-7: AGENTS.md test count → actualizar a 2363/185
       H-8: Gates count → actualizar de 5/6 a 9
     ¿QUÉ NO DEBERÍA ESTAR HARDCODEADO?

     Los más graves por impacto comercial directo:

     1. "+57 300 000 0000" y "contacto@iahoteles.co" en template → CRITICAL
        El cliente ve un número falso en SU propuesta.

     2. MONTHLY_PACKAGE_PRICE y SETUP_FEE → HIGH
        Deberían venir de pricing_calculator, no ser constantes fijas.

     3. TIER_CONFIG (porcentajes, min/max) → HIGH
        Todo el sistema de pricing está hardcodeado en vez de configurable.

     4. recovery_factor (0.15/0.20/0.25) → HIGH
        Estos definen el ROI que ve el cliente. No deberían ser literales.

     5. benchmark_score=58 → HIGH
        El score regional de referencia es un número fijo, no se consulta.

     6. Todos los fallbacks de score (50, 70, 85) → HIGH
        Si un módulo falla silenciosamente, el cliente ve un score inventado.

     7. Scenario assumptions (shift 5/10/20%, IA boost 5/10%) → HIGH
        Son la base del cálculo financiero y son literales en el código.
     CONCLUSIÓN

     El contexto actual captura bien los 2 bugs principales y los hardcodes
     más obvios del template. Pero se queda corto en 3 dimensiones:

     1. HARDCODES EN CÓDIGO: el contexto solo cubre los del template.
        Hay 20+ hardcodes en proposal_generator, diagnostic_generator,
        scenario_calculator y pricing_calculator que no están documentados.

     2. STUBS SILENCIOSOS: blog, speakable, ga4, voice_readiness siempre
        retornan False/0 sin evaluar. El diagnóstico pierde puntos de IAO
        por infraestructura que nunca se mide.

     3. INCONSISTENCIA DOCUMENTAL: AGENTS.md tiene 3 números diferentes
        para tests y documenta solo 5 de 9 gates. Esto socava la confianza
        en la documentación del proyecto.