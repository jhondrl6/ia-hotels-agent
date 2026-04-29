Excelente. Ya tengo la verificación completa cruzada contra código real. Aquí va mi análisis:
     VEREDICTO DEL CONTEXT .opencode/context/02_PROPUESTA_COMERCIAL_AUDITORIA_20260429.md
     1. CONFIRMACIONES (lo que el audit dice BIEN)

     | Hallazgo | Veredicto |
     |----------|-----------|
     | BUG-1: ROI pierde la "X" | CONFIRMADO con matiz -- La X se elimina en L556 (replace("X","")) y el template v6 NO la re-adds. Sin embargo el template v4 SÍ la re-adds (${roi_6m}X). El bug es real
     para v6, no para v4 |
     | BUG-2: Beneficio neto $0 | CONFIRMADO y PEOR de lo reportado -- No es solo pain_ratio=0.05. El código aplica DOBLE descuento: pain_ratio (0.20 default) que ya reduce el gain, y luego
     recovery_factor=0.20 que lo reduce OTRA VEZ en _calculate_roi(). Tasa efectiva = 4% en vez del 20% pretendido |
     | WhatsApp verificado | CONFIRMADO |
     | Datos financieros consistentes JSONs<->propuesta | CONFIRMADO |
     | Coherence score consistente 01<->report | CONFIRMADO |
     | DISCREPANCIA-1: 6 vs 7 servicios | CONFIRMADO -- total_services=6 en details pero 2+4+1=7 reales. El campo excluye el present_in_production |
     2. HALLAZGOS QUE FALTAN (no estaban en el audit)

     El audit encontró 8 hardcoded + 2 bugs. La verificación contra código real reveló 17 adicionales:

     CRITICOS (deberian ser config/dinamicos y NO lo son):

     | # | Elemento | Archivo:Linea | Impacto |
     |---|----------|---------------|---------|
     | 1 | recovery_factor=0.20/0.15/0.25 (4 valores) | generador L486,519,523,909 | Causa raíz de BUG-2 -- doble descuento |
     | 2 | pain_ratio default=0.20 (2 ocurrencias) | generador L204,483 | Complementa el doble descuento |
     | 3 | benchmark_score = 58 "Promedio regional" | generador L1035 | Debería venir del v4_regional_resolver |
     | 4 | web_score = "85" placeholder explicito | generador L554 | SIEMPRE muestra 85, nunca datos reales |
     | 5 | coherence_score fallback = 70 | generador L564 | Mascara un score real bajo |
     | 6 | score_tecnico fallback = 50 | generador L568,981 | Mismo problema |
     | 7 | Version '4.0.0' hardcodeada | generador L492 | Debería leer de VERSION.yaml |

     IMPORTANTES (comercialmente sensibles):

     | # | Elemento | Archivo:Linea |
     |---|----------|---------------|
     | 8 | Garantías: "10% en 90 dias", "1 mes gratis" | generador L961-974 |
     | 9 | Descuentos: 10% pago unico, 5% trimestral | generador L597-600 |
     | 10 | Formula precio: 2%, min 800k, max 2.5M | generador L1096-1099 |
     | 11 | Pesos escenarios: 70/20/10 | generador L1096 |
     | 12 | ROI cap = 5.0X | generador L929-930 |
     | 13 | Break-even default = 6 meses | generador L936 |

     MENORES pero deberian ser constantes de clase:

     | # | Elemento | Archivo:Linea |
     |---|----------|---------------|
     | 14 | Nombre empresa "IA Hoteles" (2 lugares) | generador L419,445 |
     | 15 | Validez propuesta = 15 dias | generador L467 + template L433 |
     | 16 | IAO stubs permanentes (8 campos siempre --) | generador L626-633 |
     | 17 | hotel_id no normaliza unicode (acentos) | generador L464 |
     3. QUE NO DEBERIA ESTAR HARDCODEADO Y LO ESTA (respuesta directa a tu pregunta)

     Los 5 peores (impacto comercial + tecnico):

     1. recovery_factor + pain_ratio -- Producen el BUG-2 ($0 beneficio). Son la causa raíz. Deberían venir de config o calcularse dinámicamente. Ahora están como magic numbers esparcidos en 6 lugares.

     2. web_score = "85" -- Es un PLACEHOLDER que se presenta como dato real. El cliente ve "85/100" en su propuesta y es un numero inventado.

     3. benchmark_score = 58 -- Se presenta como "promedio regional hotels pequeños" pero es un literal hardcodeado. Existe un modulo v4_regional_resolver que debería proveer este dato.

     4. Garantías y descuentos -- Los terminos comerciales (10%, 90 dias, 1 mes gratis, 5% trimestral) estan enterrados en el codigo. Si cambian la politica comercial, hay que tocar el generador Python.

     5. IAO stubs permanentes -- 8 campos que SIEMPRE muestran --. Si no hay data, deberían omitirse del documento, no mostrarse como placeholder vacío.
     4. QUE AMERITA INTERVENCION (priorizado)

     URGENTE (proximo PATCH):
     - BUG-2 reformulado: Eliminar el doble descuento (pain_ratio + recovery_factor). Un solo factor, configurable, con nombre claro.
     - web_score placeholder: Conectar al audit real o eliminar del documento.
     - benchmark_score=58: Conectar al v4_regional_resolver.

     ALTO (siguiente fase):
     - Extraer todos los magic numbers a constantes de clase o config.
     - Template v6: Fix BUG-1 (agregar la X al template).
     - IAO stubs: Remover si no hay data, o implementar tracking real.

     MEDIO (refactor):
     - hotel_id normalizar unicode.
     - Version leer de VERSION.yaml.
     - Nombre empresa como constante.
     5. ALGO QUE FALTO EN EL CONTEXT

     El audit original NO detectó:
     - El doble descuento real (pain_ratio=0.20 + recovery_factor=0.20 = efectivo 4%). Solo vio el sintoma ($0 neto) pero no la causa raíz completa.
     - Los 6 placeholders/defaults falsos (web_score 85, benchmark 58, coherence fallback 70, score_tecnico fallback 50, version 4.0.0, IAO stubs).
     - Que propuesta_v6_template.md NO EXISTE en disco -- el codigo usa _get_default_template() como fallback, lo cual concentra TODOS los hardcoded en el Python en vez de separar template de logica.

     