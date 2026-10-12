# Consentimiento de la corrida unica — Hotel Don Alfonso (plan CURA-COSTURA-TRIBUNAL)

**Plan**: CURA-COSTURA-TRIBUNAL-2026-10-11 — condicion de entrada de FASE-E2E, requisito
`consentimiento_datado_sobre_la_url_viva` del preflight.

**Quien declara**: el operador del proyecto. El texto del bloque de abajo es su dictado, recibido en el chat del
2026-10-12 y transcrito literal en `autoriza`, `url_amparada`, `fecha_captura_aceptada`,
`limite_de_frescura_dias` y `declarado_por`; la `fecha` del acto la dicto el mismo dia. El agente no redacto el
alcance ni modifico campo alguno.

**No reutiliza el acto ajeno**: este documento ampara **la corrida de este plan** y no sustituye ni enmienda
`evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/consentimiento-corrida.md` (dictado el 2026-10-07 para la
corrida única de aquel plan, que sigue publicado e intacto). El arnés lo lee por parametro `ruta=` del lector
`leer_consentimiento` / `evaluar_consentimiento`, asi que la via stdin de T0(c) apunta a **este** archivo y no al
del otro plan: un verde prestado de consentimiento es el mismo defecto por el que se rechazo la opcion C del
preflight (L-V.2).

**Alcance declarado**: autoriza la entrega —no solo la observacion— de la corrida unica de v4complete sobre la URL
amparada, y el ZIP publicable que produzca. Si el veredicto del tribunal sale `BLOQUEADO` (con AC19 vigente, un
CRITICAL del escaneo determinista suprime el ZIP tambien bajo extraccion no-OK), la cuarentena del paquete es un
resultado valido del sistema curado y no requiere una decision nueva: este documento autoriza el intento, no
garantiza la entrega. La fuente `data/hotel_observations/observations.json` no se edita y la fecha de captura se
conserva en 2026-07-22.

<!-- iah-consentimiento -->
{"url_amparada": "https://www.donalfonsohotel.com/", "fecha_captura_aceptada": "2026-07-22", "limite_de_frescura_dias": 90, "autoriza": "Autorizo la entrega de la corrida única v4complete sobre la URL amparada y el ZIP publicable que produzca", "declarado_por": "Jhond (operador)", "fecha": "2026-10-12"}

**Ventana**: el limite de 90 dias desde la captura vence el **2026-10-20** (dia 90 desde 2026-07-22;
medido el 2026-10-12: **82 dias** de edad). El chequeo del arnes es dinamico contra la fecha del run, asi que
este acto habilita el spawn en cualquier dia hasta ese techo. Pasado el 2026-10-20 no habilita: el plan prohibe
editar la fecha de captura (`01-plan-maestro.md`, DEC-A4 y la invariante de T0), asi que hari falta una captura
nueva del hotel, no una firma nueva sobre el dato viejo.

**Limites que este documento no cierra**: el contador de intentos queda en **0/1** — autoriza, no lanza (el
`control_productivo_intacto` de FASE-E2E se ancla a `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/run_control.json`,
que a la fecha no existe). La revocacion de claves sigue acreditada por afirmacion del operador del 2026-09-18, no
por evidencia operativa. Y la presencia de credencial (`DEEPSEEK_API_KEY` / `ANTHROPIC_API_KEY` / `LLM_PROVIDER`)
se declara por nombre de variable en `pre-vuelo.md`, nunca por valor.
