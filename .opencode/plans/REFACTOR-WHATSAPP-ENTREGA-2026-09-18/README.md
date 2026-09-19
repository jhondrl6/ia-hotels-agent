# REFACTOR-WHATSAPP-ENTREGA-2026-09-18

**Estado: DISEÑADO, SIN IMPLEMENTAR.** Diseño congelado en el maestro y el contrato. Las once sesiones están PENDIENTES; no hay aprobación, certificación ni resultado de implementación declarado. **Contador v4complete: 0/1. Siguiente sesión: A.**

Objetivo: alinear promesas y entrega WhatsApp con los datos realmente utilizables, impedir botones inseguros y conservar causas y evidencia de bloqueo. La meta de entrega no autoriza ocultar bloqueos legítimos ni prometer READY.

## Índice documental

- [Lecciones capitalizadas](00-lecciones-capitalizadas.md): antecedentes contrastados y límites de las consultas.
- [Plan maestro](01-plan-maestro.md): decisiones, alcance, AC1–AC19 y única corrida.
- [Contrato de ejecución](04-contrato-ejecucion.md): permisos, PRE/POST, R2 y cierre incremental.
- [Dependencias y bloqueantes](dependencias-fases.md): cadena secuencial, archivos compartidos y condiciones de avance.
- [Checklist de implementación](06-checklist-implementacion.md): estados, aceptación y controles de cierre.
- [Documentación post-proyecto](09-documentacion-post-proyecto.md): cierre documental previsto.
- [Análisis post-implementación](10-analisis-post-implementacion.md): matriz final, límites y seguimientos previstos.

Los enlaces a prompts y documentos de cierre identifican los destinos previstos del plan; esta escritura no verifica su existencia ni declara que se hayan ejecutado.

## Once sesiones, una fase por sesión

| Sesión / prompt | Objetivo | Complejidad técnica | Estado |
|---|---|---|---|
| [A](05-prompt-inicio-sesion-fase-A.md) | Baseline, ratificación de contratos y resolución de prerrequisitos | ALTA: producto, identidad y permisos transversales | PENDIENTE |
| [B](05-prompt-inicio-sesion-fase-B.md) | Pains, promesas y guía de setup sin número | ALTA: mapper, catálogo y productores de narrativa/coverage | PENDIENTE |
| [C](05-prompt-inicio-sesion-fase-C.md) | Confianza, campo validado y destino seguro del botón | ALTA: precedencia de datos y falso VERIFIED | PENDIENTE |
| [D](05-prompt-inicio-sesion-fase-D.md) | Veredicto único, fail-fast y causas serializadas | ALTA: gates y consumidores del assessment | PENDIENTE |
| [E](05-prompt-inicio-sesion-fase-E.md) | Writer real, snapshot interno y revisión de documentos retenidos | ALTA: orden temporal y separación interno/cliente | PENDIENTE |
| [F](05-prompt-inicio-sesion-fase-F.md) | Redacción de salidas y estado operativo de credencial | MEDIA-ALTA: seguridad de salidas y prueba externa de revocación | PENDIENTE |
| [G](05-prompt-inicio-sesion-fase-G.md) | Descubrimiento AST de callers y retirada del contrato muerto | ALTA: cobertura sin lista fija y firmas compartidas | PENDIENTE |
| [H](05-prompt-inicio-sesion-fase-H.md) | Integración offline, onboarding derivado y runner acotado | ALTA: identidad, frescura, reserva persistente y evidencia | PENDIENTE |
| [E2E](05-prompt-inicio-sesion-fase-E2E.md) | Única invocación real y conservación inmediata de evidencia | MEDIA técnica / ALTA operativa: APIs y un solo intento | PENDIENTE |
| [VERIFY](05-prompt-inicio-sesion-fase-VERIFY.md) | Análisis directo de artefactos y matriz de certificación | ALTA: atribución causal y límites de una sola muestra | PENDIENTE |
| [RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md) | Cierre y sincronización documental autorizados | MEDIA: coherencia y orden documental | PENDIENTE |

Cadena estricta: **A → B → C → D → E → F → G → H → E2E → VERIFY → RELEASE**. No ejecutar fases en paralelo ni encadenarlas dentro de una sesión. Un checkpoint no habilita la fase siguiente.

A–H no ejecutan auditorías externas ni v4complete. H prepara tests/runner sin nuevos flags CLI. Solo E2E puede consumir el intento mediante ese runner; no se lanza el comando hijo por separado. Un fallo o timeout no concede otra corrida. VERIFY es directo, sin delegación, cambios de código, tests nuevos ni nueva ejecución; lee evidencia existente. RELEASE es documental, no una fase de reparación ni otra corrida.

## Prerrequisitos y límites visibles

- El maestro registra un PRE quick **9/10** con fallo preexistente de Version Sync. No se ha repetido aquí. A necesita autorización central para resolverlo; no se asume permiso sobre AGENTS.md, .cursorrules o configuración.
- La deuda **F-B de privacidad** permanece diferida: no transportar WhatsApp/PII en warehouse ni cambiar formulario/esquema sin decisión escrita. No confundir esta deuda con la sesión B.
- Fuente Don Alfonso: observación del **2026-07-22**. A resuelve vigencia y H contrasta `ONBOARDING_FRESHNESS_HOURS` efectivo; no cambiar fechas, desactivar frescura ni sustituir por defaults.
- Binding explícito y local: URL original **https://hoteldonalfonso.com/**; solicitada **https://www.donalfonsohotel.com/**. Conservar ambas y su procedencia; no afirmar redirección ni crear alias global.
- La revocación de una key expuesta no es inferible del código, tests o una key nueva: requiere evidencia operativa sin secreto; mientras falte, permanece pendiente.
- QMind fue accesible para consulta según las lecciones. Eso no autoriza upload; no hay autorización de subida en esta preparación.
- A debe resolver la divergencia documental sobre cuándo regenerar DOMAIN_PRIMER, sin editar reglas centrales para silenciarla.

## Inicio de la siguiente sesión

Copiar en una sesión nueva:

```text
Ejecuta únicamente FASE-A del plan C:/Users/Jhond/Github/iah-cli/.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/. Lee 05-prompt-inicio-sesion-fase-A.md, 01-plan-maestro.md, 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md y el estado de dependencias/checklist. Respeta permisos y bloqueantes; no inicies B ni ejecutes v4complete. Conserva el contador 0/1 y deja checkpoint si falta autorización.
```

## Cierre y aceptación

Cada fase incorpora su evidencia y cierre incremental; no se difieren todos los controles a RELEASE. R2 toma como referencia 60 tool_use hasta el corte autorizado de código, medidos con el instrumento del contrato; sin transcript, declarar **FUERA DE SERVICIO (R2.1)**, no estimar cumplimiento. En sesiones sin código, registrar corte documental separado.

AC1–AC19 permanecen PENDIENTES. Tests offline y resultados realmente ejercitados por Don Alfonso se informarán por separado. READY requiere gates y acta favorables, además de ZIP válido; exit code cero no basta. Un bloqueo legítimo o un caso no ejercitado no se etiqueta como superado. Esta preparación no ejecuta scripts, red, git ni commits y no autoriza implementación, publicación o subida de datos.
