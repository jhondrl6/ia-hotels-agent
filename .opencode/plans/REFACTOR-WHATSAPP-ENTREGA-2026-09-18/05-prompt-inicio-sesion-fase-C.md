# FASE-C — Número utilizable y botón seguro

**Estado:** PENDIENTE. **Dependencias:** A y B completas. **Complejidad técnica:** ALTA: confianza, presencia, identidad y precedencia del dato no son intercambiables. **Modo:** DIRECTO; no delegate_task para este cambio de política. **R3:** 4 tareas, 0 comandos largos externos.

## Contexto

Lee maestro, contrato de ejecución, resultados B y 00; ejecuta solo C. El centinela HTML puede viajar como teléfono, `phone_web` puede reemplazar la clave usada por el botón y SitePresence puede elevar incluso CONFLICT a 0.95. B evita prometer esos botones; C conserva una defensa efectiva si una ruta los fuerza.

**Hallazgo medido 2026-09-19 que C debe gobernar (AC19):** en el hotel de la corrida el canal existe y el lector no lo ve. La home viva tiene 0 referencias a WhatsApp y `/contacto/` tiene 54, todas dentro de `<style>` o de `href`/`src` del plugin `creame-whatsapp-me` (JoinChat 6.3.2); no hay `<a href="wa.me/…">` ni número en HTML estático. `SitePresenceChecker._check_html_element` solo inspecciona la raíz, solo mira texto/`<a href>`/clases, y su `except Exception` devuelve `{"found": False}`. Por tanto "no encontrado" hoy **no** significa ausencia.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-T4A.5 | Un test verde puede no alcanzar la rama que dice certificar. | AC3/AC6 pasan por productor, extracción, generador y serialización, no solo regex aislada. |
| L-VUP-5 | Un contrato ya verde exige mutación para demostrar sensibilidad. | Los mutantes de guarda y boost deben fallar con la misma expectativa negativa. |
| L-NC6 | El cable perdido se busca en el caller, no creando otra fuente. | Usar el campo validado; no añadir un número paralelo al builder. |
| L-PF6 | Ausencia observada y lector fallido no son equivalentes. | AC19 convierte el fallo de fetch y la página no inspeccionada en estado desconocido, no en dolor de ausencia. |

## Tareas

1. **PRE.** Medir baseline y releer construcción de whatsapp_number en `run_v4_complete_mode`, `_extract_validated_fields`, `ConditionalGenerator._generate_whatsapp_button` y `_check_whatsapp_verified`. Localizar normalizador/validador de teléfono ya existente antes de introducir otro criterio. Inventariar el alcance real de `SitePresenceChecker`: qué rutas consulta, qué atributos mira y qué excepciones traga, con el caso medido del hotel como referencia.
2. **Blindar el contrato y el lector.** Marcar `detected_via_html` no utilizable. El botón recibe exclusivamente número de WhatsApp validado, nunca `phone_web` por precedencia ni un placeholder. Validar forma del número al límite de generación: normalización explícita de formato, dígitos ASCII, longitud internacional válida conforme al contrato existente, sin inferir país ni completar partes. Rechazar cadena vacía, centinelas y entradas inválidas sin producir href; registrar causa y enrutar a setup solo cuando no se haya prometido un botón operativo. En coherencia eliminar promoción a VERIFIED por mero exists; la presencia evita duplicación, no verifica número. Mantener bloqueo de botón forzado inseguro, incluso con SitePresence exists. No bajar 0.9/0.8 ni cambiar blocking=True. **AC19:** el reporte de presencia publica `observation_scope`, `read_status` del fetch y `presence_evidence_kind` (`wa.me_href`, `plugin_fingerprint`, `ninguna`); una huella de plugin declara presencia sin aportar número, el fallo de red declara estado desconocido, y ningún camino produce la afirmación "no tiene WhatsApp". Ampliar el alcance de inspección como el contrato lo exija, sin scraping masivo ni dependencias nuevas.
3. **POST y mutation checks.** AC3 negativo: CONFLICT/UNKNOWN/ESTIMATED + botón forzado bloquean con y sin presencia; VERIFIED válido pasa. AC6: HTML-only producido por main, sin dígitos, separadores, dígitos Unicode, longitud inválida, teléfono alternativo distinto y número verificado formateado. AC19: fixture con el canal solo en página interna y fixture con huella de plugin sin `href` declaran presencia sin dolor de ausencia y sin número derivado; una excepción de transporte debe dar READ_ERROR, no `found=False`. Leer HTML y ZIP de writer real. Mutar guard de forma, restaurar boost indiscriminado, limitar el lector a la raíz o tragar la excepción deben romper pruebas distintas. Probar tanto clave canónica como rechazo de override `whatsapp=phone_web`.
4. **Cierre.** Evidencia por AC con síntoma original y resultado, hashes/PRE/POST, `thresholds.json` con fuentes, lecciones y cierre incremental. Diferenciar prueba offline del caso que la corrida única llegará a ejercitar; si E2E muestra el botón no observado, corresponde a AC19 y no a un hallazgo nuevo duplicado.


## Tests obligatorios

`tests/regression/test_whatsapp_conflicts.py`, conflictos Visperas, tests de coherent generated assets, site presence adapter y conditional generator; identificar tests espejo en todo el repo. No cambiar la aserción legítima de bloqueo para forzar verde. Verificar que no se rompe el skip de assets ya presentes ni se fabrican nuevos pains.

Evidence C: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-C/`. Reporte de generación debe explicar rechazo y destino del setup; no basta ausencia de archivo.

## Post-ejecución

Aplicar cierre completo del contrato y registrar datos medidos:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-C --desc "REFACTOR-WHATSAPP-ENTREGA: destino seguro y confianza no suplantada" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Completitud y restricciones

- [ ] AC3/AC5/AC6/AC19 cumplen; test rojo del producto significa protección viva, no test fallido.
- [ ] Ninguna ruta del lector afirma "no tiene WhatsApp" desde un fallo de fetch o una página no inspeccionada.
- [ ] Ningún wa.me vacío o destino tomado de un teléfono no validado en HTML/ZIP.
- [ ] El boost por presencia no neutraliza conflictos ni baja confianza requerida.
- [ ] PRE/POST, mutaciones y cierre incremental completos.
- Presupuesto referencia 60 tool_use; instrumento `measure_iterations.py`, corte commit de código, retirar métrica si no medible.
- No archivar domain_gates ni implementar F-B/F-E. No v4complete. D se ejecuta en nueva sesión.
