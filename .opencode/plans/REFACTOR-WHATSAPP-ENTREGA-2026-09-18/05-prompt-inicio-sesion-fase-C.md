# FASE-C — Número utilizable y botón seguro

**Estado:** PENDIENTE. **Dependencias:** B completo (y, por la cadena A → G → 0 → B, el verificador de cableado de G ya está en su sitio: corre antes que B). **Complejidad técnica:** ALTA: confianza, presencia, identidad y precedencia del dato no son intercambiables, y el blast radius medido del reporte canónico es grande — 8 consumidores de ese reporte, 816 funciones de test (método canónico) que tocan `whatsapp_button`/`site_presence_report` y cuatro aserciones de igualdad exacta de forma, en `TestNormalizeSitePresence.test_normalize_from_none` (`tests/asset_generation/test_site_presence_adapter.py`) y en `test_ruta_fallo_checker_snapshot_vacio_canonico` (en `tests/test_site_presence_persistence.py`, que vive en la raíz de `tests/`, no bajo `tests/asset_generation/`)—: C publica claves nuevas, pero su presupuesto **no** cubre la migración de esos consumidores (AC19b). **Modo:** DIRECTO; no delegate_task para este cambio de política. **R3:** 4 tareas, 0 comandos largos externos.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Contexto

Lee maestro, contrato de ejecución, resultados B y 00; ejecuta solo C. El centinela HTML puede viajar como teléfono, `phone_web` puede reemplazar la clave usada por el botón y SitePresence puede elevar incluso CONFLICT a 0.95. B evita prometer esos botones; C conserva una defensa efectiva si una ruta los fuerza.

**Hallazgo medido 2026-09-19 que C debe gobernar (AC19a):** medido ejecutando el propio lector del repo, `SitePresenceChecker._check_html_element`, contra la URL viva: el resultado es `found=True` por la sonda de clases CSS (`css_class:joinchat joinchat--left joinchat--btn`) sobre la **raíz**, y la corrida archivada `output/TAREA7-2026-09-19/v4_complete/hotel_don_alfonso/v4_audit/site_presence_snapshot.json` registra `whatsapp_button: exists` con `confidence 0.85` y `site_verified true`. **Se retracta** el enunciado anterior de esta fase (home con 0 referencias a WhatsApp y lector incapaz de ver el canal): no fue medido y es falso. Lo que sí queda en pie y C debe gobernar: `_check_asset_presence` pasa a la sonda HTML solo la URL raíz, sin crawls; el `except Exception` de `_check_html_element` colapsa cualquier fallo de transporte en `{"found": False}`; `verification_failed` se estampa en `_check_asset_presence` porque falló el reporte de SCHEMA, no la lectura HTML — que es lo que la corrida de FASE-P4 registró para los 5 assets del snapshot—; `_presence_result_to_canonical` descarta `details`, incluido el `whatsapp_href_number` que `_check_html_element` sí extrae de los `href` `wa.me`; y existen dos lectores distintos con patrones distintos (`SitePresenceChecker._check_html_element` frente a `V4ComprehensiveAuditor._detect_whatsapp_from_html`). El riesgo vivo, por tanto, es un **falso positivo de presencia** (huella de plugin → `exists` 0.85 → boost a 0.95), no una falsa ausencia.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-T4A.5 | Un test verde puede no alcanzar la rama que dice certificar. | AC3/AC6 pasan por productor, extracción, generador y serialización, no solo regex aislada. |
| L-VUP-5 | Un contrato ya verde exige mutación para demostrar sensibilidad. | Los mutantes de guarda y boost deben fallar con la misma expectativa negativa. |
| L-NC6 | El cable perdido se busca en el caller, no creando otra fuente. | Usar el campo validado; no añadir un número paralelo al builder. |
| L-PF6 | Ausencia observada y lector fallido no son equivalentes. | AC19 convierte el fallo de fetch y la página no inspeccionada en estado desconocido, no en dolor de ausencia. |

## Tareas

1. **PRE.** Medir baseline y releer construcción de whatsapp_number en `run_v4_complete_mode`, `_extract_validated_fields`, `ConditionalGenerator._generate_whatsapp_button` y `_check_whatsapp_verified`. Localizar normalizador/validador de teléfono ya existente antes de introducir otro criterio. Inventariar el alcance real de `SitePresenceChecker`: qué rutas consulta, qué atributos mira y qué excepciones traga, con el caso medido del hotel como referencia.
2. **Blindar el contrato y el lector.** Marcar `detected_via_html` no utilizable. El botón recibe exclusivamente número de WhatsApp validado, nunca `phone_web` por precedencia ni un placeholder. Validar forma del número al límite de generación: normalización explícita de formato, dígitos ASCII, longitud internacional válida conforme al contrato existente, sin inferir país ni completar partes. Rechazar cadena vacía, centinelas y entradas inválidas sin producir href; registrar causa y enrutar a setup solo cuando no se haya prometido un botón operativo. En coherencia eliminar promoción a VERIFIED por mero exists; la presencia evita duplicación, no verifica número. Mantener bloqueo de botón forzado inseguro, incluso con SitePresence exists. No bajar 0.9/0.8 ni cambiar blocking=True. **AC19a (aditivo, y solo aditivo):** el reporte de presencia publica `observation_scope`, `read_status` del fetch y `presence_evidence_kind` (`wa.me_href`, `plugin_fingerprint`, `ninguna`) **como claves nuevas**, sin redefinir `status`, `site_verified` ni `confidence` y sin eliminar `details` en el adaptador. La migración de los 8 consumidores al tri-estado es **AC19b**, deuda diferida del §6 del maestro, y **no** forma parte de C. Una huella de plugin declara presencia sin aportar número, el fallo de red declara estado desconocido, y ningún camino produce la afirmación "no tiene WhatsApp". **Prerrequisito de C:** unificar o designar expresamente los dos lectores de WhatsApp (`SitePresenceChecker._check_html_element` y `V4ComprehensiveAuditor._detect_whatsapp_from_html`), porque hoy alimentan decisiones distintas con patrones distintos. Ampliar el alcance de inspección como el contrato lo exija, sin scraping masivo ni dependencias nuevas.
3. **POST y mutation checks.** AC3 negativo: CONFLICT/UNKNOWN/ESTIMATED + botón forzado bloquean con y sin presencia; VERIFIED válido pasa. AC6: HTML-only producido por main, sin dígitos, separadores, dígitos Unicode, longitud inválida, teléfono alternativo distinto y número verificado formateado. AC19a: fixture con el canal solo en página interna y fixture con huella de plugin sin `href` declaran presencia sin dolor de ausencia y sin número derivado; una excepción de transporte debe dar READ_ERROR, no `found=False`. **Rojo invertido (el caso realmente medido en Don Alfonso):** si una huella de plugin llegara a producir `exists` con confianza ≥0.9 y un botón con número, un test debe romperse; el caso esperado no es el lector ciego sino el falso positivo de presencia. Leer HTML y ZIP de writer real. Mutar guard de forma, restaurar boost indiscriminado, limitar el lector a la raíz o tragar la excepción deben romper pruebas distintas. Probar tanto clave canónica como rechazo de override `whatsapp=phone_web`.
4. **Cierre.** Evidencia por AC con síntoma original y resultado, hashes/PRE/POST, `thresholds.json` con fuentes, lecciones y cierre incremental. Diferenciar prueba offline del caso que la corrida única llegará a ejercitar; lo medido en Don Alfonso es el botón **sí observado** por huella de plugin, y ese caso corresponde a AC19a, no a un hallazgo nuevo duplicado.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

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

- [ ] AC3/AC5/AC6/AC19a cumplen; test rojo del producto significa protección viva, no test fallido.
- [ ] AC19a cerró en modo aditivo: los 8 consumidores del reporte canónico, las 816 funciones de test (método canónico) que tocan `whatsapp_button`/`site_presence_report` y las cuatro aserciones de igualdad exacta (`TestNormalizeSitePresence.test_normalize_from_none`, `test_ruta_fallo_checker_snapshot_vacio_canonico`) siguen verdes. La migración al tri-estado es AC19b (deuda del §6 del maestro) y el presupuesto de C **no** la cubre: no se intentó ni se declara hecha.
- [ ] Los dos lectores de WhatsApp fueron unificados o designados expresamente antes de publicar las claves nuevas.
- [ ] Ninguna ruta del lector afirma "no tiene WhatsApp" desde un fallo de fetch o una página no inspeccionada.
- [ ] Ningún wa.me vacío o destino tomado de un teléfono no validado en HTML/ZIP.
- [ ] El boost por presencia no neutraliza conflictos ni baja confianza requerida.
- [ ] PRE/POST, mutaciones y cierre incremental completos.
- Presupuesto referencia 60 tool_use; instrumento `measure_iterations.py`. El corte es el que la sesión tenga autorizado: con el commit de código autorizado, «hasta el commit»; sin él, «hasta listo para revisión», y se declara cuál de los dos se usó — **los cinco cortes se sostienen sin commit**. Retirar la métrica si no es medible; nunca estimar cumplimiento.
- No archivar domain_gates ni implementar F-B/F-E. No v4complete. D se ejecuta en nueva sesión.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`
