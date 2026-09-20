# REFACTOR-WHATSAPP-ENTREGA-2026-09-18

**Estado: DISEÑADO, SIN IMPLEMENTAR.** Diseño congelado en el maestro y el contrato. Las doce sesiones están PENDIENTES; no hay aprobación, certificación ni resultado de implementación declarado. **Contador v4complete: 0/1. Siguiente sesión: A.**

**Revisión 2 (2026-09-19).** El plan se re-midió contra código vivo y contra una corrida real ya archivada (`output/TAREA7-2026-09-19/`, mismo hotel y URL del §5, 2026-09-19 15:01). Cuatro premisas del maestro cayeron, se añadieron **AC20** y **FASE-0**, **G adelanta a segunda sesión** y **AC19 se parte en 19a (aditivo) y 19b (diferido)**. Motivo central: la corrida medida terminó `BLOQUEADO` con ZIP suprimido **con los 13 gates verdes y readiness `READY_FOR_PUBLICATION`**, por un único hallazgo CRITICAL (`VACUOUS_RECALL`) que ninguna fase cubría y que el Knowledge Center registró el 2026-09-11 como "fix candidato fuera de este plan". Sin FASE-0, la meta de entrega de este plan era inalcanzable con independencia de B–H. Detalle en maestro §1, §2, §4 y §7.

Objetivo: alinear promesas y entrega WhatsApp con los datos realmente utilizables, impedir botones inseguros y conservar causas y evidencia de bloqueo. La meta de entrega no autoriza ocultar bloqueos legítimos ni prometer READY.

## Índice documental

- [Lecciones capitalizadas](00-lecciones-capitalizadas.md): antecedentes contrastados y límites de las consultas.
- [Plan maestro](01-plan-maestro.md): decisiones, alcance, AC1–AC20 y única corrida.
- [Contrato de ejecución](04-contrato-ejecucion.md): permisos, PRE/POST, R2 y cierre incremental.
- [Dependencias y bloqueantes](dependencias-fases.md): cadena secuencial, archivos compartidos y condiciones de avance.
- [Checklist de implementación](06-checklist-implementacion.md): estados, aceptación y controles de cierre.
- [Documentación post-proyecto](09-documentacion-post-proyecto.md): cierre documental previsto.
- [Análisis post-implementación](10-analisis-post-implementacion.md): matriz final, límites y seguimientos previstos.

Los enlaces a prompts y documentos de cierre identifican los destinos previstos del plan; esta escritura no verifica su existencia ni declara que se hayan ejecutado.

## Doce sesiones, una fase por sesión

| Orden / prompt | Objetivo | Complejidad técnica | Estado |
|---|---|---|---|
| 1 · [A](05-prompt-inicio-sesion-fase-A.md) | Baseline, ratificación de contratos (incluida FASE-0 y AC19a/AC19b) y resolución de prerrequisitos | ALTA: producto, identidad y permisos transversales | PENDIENTE |
| 2 · [G](05-prompt-inicio-sesion-fase-G.md) | Descubrimiento AST de callers y retirada del contrato muerto. **Adelantado: es el guard de las ediciones de B–F** | ALTA: cobertura sin lista fija y firmas compartidas | PENDIENTE |
| 3 · [0](05-prompt-inicio-sesion-fase-0.md) | **Nueva.** Evidencia del veredicto serializada: recall fundado, hallazgos en el acta y hash del paquete publicado | MEDIA técnica / ALTA consecuencia: decide si puede existir un ZIP entregable | PENDIENTE |
| 4 · [B](05-prompt-inicio-sesion-fase-B.md) | Pains, promesas y guía de setup sin número | ALTA: mapper, catálogo y productores de narrativa/coverage | PENDIENTE |
| 5 · [C](05-prompt-inicio-sesion-fase-C.md) | Confianza, campo validado, destino seguro del botón y AC19a aditivo | ALTA: precedencia del dato, falso VERIFIED y dos lectores que hay que unificar | PENDIENTE |
| 6 · [D](05-prompt-inicio-sesion-fase-D.md) | Veredicto único, fail-fast y causas serializadas | ALTA: gates y consumidores del assessment | PENDIENTE |
| 7 · [E](05-prompt-inicio-sesion-fase-E.md) | Writer real, resolvedor único de artefactos y snapshot interno revisable | ALTA: orden temporal y separación interno/cliente | PENDIENTE |
| 8 · [F](05-prompt-inicio-sesion-fase-F.md) | Redacción de salidas (sumidero único) y estado operativo de credencial | MEDIA-ALTA: seguridad de salidas y prueba externa de revocación | PENDIENTE |
| 9 · [H](05-prompt-inicio-sesion-fase-H.md) | Integración offline, onboarding derivado con procedencia y runner acotado | ALTA: entorno, identidad, reserva y evidencia antes de gastar el único intento | PENDIENTE |
| 10 · [E2E](05-prompt-inicio-sesion-fase-E2E.md) | Única invocación real y conservación inmediata de evidencia | MEDIA técnica / ALTA operativa: APIs y un solo intento | PENDIENTE |
| 11 · [VERIFY](05-prompt-inicio-sesion-fase-VERIFY.md) | Análisis directo de artefactos y matriz de certificación AC1–AC20 | ALTA: atribución causal y límites de una sola muestra | PENDIENTE |
| 12 · [RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md) | Cierre y sincronización documental autorizados | MEDIA: coherencia y orden documental | PENDIENTE |

Cadena estricta: **A → G → 0 → B → C → D → E → F → H → E2E → VERIFY → RELEASE**. No ejecutar fases en paralelo ni encadenarlas dentro de una sesión. Un checkpoint no habilita la fase siguiente.

A–H no ejecutan auditorías externas ni v4complete. H prepara tests/runner sin nuevos flags CLI. Solo E2E puede consumir el intento mediante ese runner; no se lanza el comando hijo por separado. Un fallo o timeout no concede otra corrida. VERIFY es directo, sin delegación, cambios de código, tests nuevos ni nueva ejecución; lee evidencia existente. RELEASE es documental, no una fase de reparación ni otra corrida.

## Prerrequisitos y límites visibles

- **Nueva (revisión 2):** la meta certificable de E2E es **ZIP publicado con veredicto no bloqueante**, no `READY_FOR_PUBLICATION`. Medido: readiness READY y 13/13 gates verdes convivieron con `BLOQUEADO` y ZIP suprimido. El techo con tier B es `APROBADO-CONDICIONAL-PENDING-ONBOARDING`; `APROBADO-PARA-ENTREGA` exige tier A (GA4+GSC verificados) y hoy el tier sale **B por defecto**.
- **Nueva:** FASE-0/AC20 es prerrequisito del intento único. Sin él, la supresión se reproduce pase lo que pase en B–H.
- **Nueva:** `--output` no aísla la corrida. `v4complete` muta `.agent/memory`, puede borrar sesiones de más de 20 días y reutiliza análisis previo por `canonical_url` (`L-PF11`). H congela `--permission-mode` (default `auto`, que autoriza APIs de pago) y snapshot de memoria antes del spawn.
- El PRE quick del 2026-09-18 fue **9/10** por Version Sync y la re-medición del 2026-09-19 da **10/10**: eran cuatro documentos sucios en el árbol, hoy idénticos a HEAD. No queda prerrequisito de autorización central; A vuelve a medir el quick al abrir la fase.
- La deuda **F-B de privacidad** permanece diferida: no transportar WhatsApp/PII en warehouse ni cambiar formulario/esquema sin decisión escrita. No confundir esta deuda con la sesión B.
- Fuente Don Alfonso: observación del **2026-07-22**. A resuelve vigencia y H contrasta `ONBOARDING_FRESHNESS_HOURS` efectivo; no cambiar fechas, desactivar frescura ni sustituir por defaults.
- Binding explícito y local: URL original **https://hoteldonalfonso.com/**; solicitada **https://www.donalfonsohotel.com/**. Conservar ambas y su procedencia; no afirmar redirección ni crear alias global.
- La revocación de una key expuesta no es inferible del código, tests o una key nueva: requiere evidencia operativa sin secreto; mientras falte, permanece pendiente.
- QMind fue accesible para consulta según las lecciones. Eso no autoriza upload; no hay autorización de subida en esta preparación.
- A debe resolver la divergencia documental sobre cuándo regenerar DOMAIN_PRIMER, sin editar reglas centrales para silenciarla.

## Inicio de la siguiente sesión

Copiar en una sesión nueva:

```text
Ejecuta únicamente FASE-A del plan C:/Users/Jhond/Github/iah-cli/.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/. Lee 05-prompt-inicio-sesion-fase-A.md, 01-plan-maestro.md (revisión 2), 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md (§1bis y las filas nuevas de §2) y el estado de dependencias/checklist. Ratifica explícitamente la FASE-0 con AC20, la división AC19a/AC19b, el orden A → G → 0 → B y la meta re-anclada de E2E (ZIP publicado con veredicto no bloqueante, no READY). Re-mide las premisas antes de la primera tarea: quick, git, y el baseline ya archivado en output/TAREA7-2026-09-19/. Reintenta la consulta a QMind que quedó denegada y registra el resultado. Respeta permisos y bloqueantes; no inicies G ni ejecutes v4complete. Conserva el contador 0/1 y deja checkpoint si falta autorización.
```

## Cierre y aceptación

Cada fase incorpora su evidencia y cierre incremental; no se difieren todos los controles a RELEASE. R2 toma como referencia 60 tool_use hasta el corte autorizado de código, medidos con el instrumento del contrato; sin transcript, declarar **FUERA DE SERVICIO (R2.1)**, no estimar cumplimiento. En sesiones sin código, registrar corte documental separado.

AC1–AC20 permanecen PENDIENTES. Tests offline y resultados realmente ejercitados por Don Alfonso se informarán por separado. READY requiere gates y acta favorables, además de ZIP válido; exit code cero no basta. Un bloqueo legítimo o un caso no ejercitado no se etiqueta como superado. **Alcance ejecutado a 2026-09-19:** la preparación del 2026-09-18 fue read-only y no ejecutó nada; la revisión 2 del 2026-09-19 sí ejecutó validaciones y lecturas de artefactos, y su cierre documental entró en el repo con el commit `9b0af4f` (anclas medidas sobre `938f59f`) y `master` en paridad con `origin/master`. Lo que sigue **sin** ejecutar y sin autorización: `v4complete` (contador 0/1), publicación, entrega a cliente y subida de datos a ningún servicio.
