# Consentimiento de la corrida unica — Hotel Don Alfonso

**Plan**: REFACTOR-WHATSAPP-ENTREGA-2026-09-18 — requisito verificado por FASE-H y consumido como condicion de
entrada de FASE-E2E.

**Quien declara**: el operador del proyecto. El texto del bloque de abajo es su dictado, recibido en el chat del
2026-10-07 y transcrito literal; el agente no redacto el alcance ni modifico campo alguno.

**Resuelve**: el requisito `consentimiento_datado_sobre_la_url_viva`, abierto por FASE-A el 2026-09-19
(`dependencias-fases.md:99`) con dueño operador, y la deuda registrada en
`10-analisis-post-implementacion.md:132` / leccion `L-ENT.6`.

**Alcance declarado**: autoriza la entrega —no solo la observacion— de la corrida unica sobre la URL viva, y el ZIP
publicable que produzca. No ampara la publicacion del contacto del hotel: F-B (campo de contacto en el warehouse)
sigue diferida con decision de privacidad pendiente. La fuente `data/hotel_observations/observations.json` no se
edita, y la fecha de captura se conserva en 2026-07-22.

<!-- iah-consentimiento -->
{"url_amparada": "https://www.donalfonsohotel.com/", "fecha_captura_aceptada": "2026-07-22", "limite_de_frescura_dias": 90, "autoriza": "Autorizo la entrega de la corrida única v4complete sobre la URL amparada y el ZIP publicable que produzca", "declarado_por": "Jhond (operador)", "fecha": "2026-10-07"}

**Ventana**: el limite de 90 dias vence el **2026-10-20** (dia 90 desde la captura). Pasado ese dia este
consentimiento no habilita el spawn: el plan prohíbe editar la fecha de captura
(`01-plan-maestro.md:143`), asi que hari falta una captura nueva del hotel.

**Límites que este documento no cierra**: la revocación de claves sigue acreditada por afirmación del operador del
2026-09-18 (`05-prompt-inicio-sesion-fase-A.md:23`), no por evidencia operativa; y el contador de intentos queda en
**0/1** — este documento autoriza, no lanza.
