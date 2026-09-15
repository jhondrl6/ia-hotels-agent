# FASE-P5: Seguridad y privacidad

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-P5
**Objetivo**: Cerrar la brecha de secretos y privacidad que FASE-P4 destapó (F-P4.5): sanear la salida de errores del provider, extender el control de secretos a lo que se prepara para publicar, y dejar medido y con dueño el estado de la superficie pública del repo. **Es la fase que abre la puerta (AC-S4) antes de cualquier nueva corrida o publicación.** Prioridad por encima de P6 y RELEASE.
**Dependencias**: FASE-P4 ✅ (origen del hallazgo F-P4.5) + inventario y límites de autorización de §4 del maestro. **No** depende de acceso a cuentas externas: el cierre técnico es offline; las acciones externas (rotación, retirada, cambio de visibilidad) son del operador y se autorizan aparte.
**Presupuesto**: **FUERA DE SERVICIO (R2.1, D-PRE.1/D-V2.1)** — sin calibración comparable; registrar medida real, unidad y corte al cerrar, sin inventar estimación.
**Complejidad técnica**: MEDIA-ALTA (toca validaciones, provider y política de versionado)
**Modo de ejecución**: SESIÓN PRINCIPAL (sin comando largo; pruebas offline con token sintético)
**Skill**: `phased_project_executor.md` v2.24.0

---

## Contexto

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P1 / P2 / P3-A / P3-B | ✅ (ver `dependencias-fases.md`) |
| FASE-P4 | ✅ cerrada — informe con 9 hallazgos; F-P4.5 alimenta esta fase |
| FASE-P5 | ← ESTA FASE |
| FASE-P6 / RELEASE | pendientes, después de P5 |

### Lecciones capitalizadas aplicables a esta fase
(filtras de `00-lecciones-capitalizadas.md` §2 y §1.b)

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-PF6 / L-PF10 | "Sin hallazgos" ≠ "no midió" — un check que no mira la ruta correcta da verde vacío | AC-S2: el control debe reportar explícitamente no-leíbles/no-cubiertos, y SIA `SIN-HALLAZGOS` sale de un lector que sí leyó |
| L-SR5 / L-PF3 | Un gate que solo loggea no previene | AC-S2: un secreto detectado en contenido staged escala a BLOQUEO, no a advertencia |
| EVIDENCE-TIER-FALSE-CONFIDENCE | Confianza declarada sin fuente | AC-S3: la superficie pública se mide por commit y ruta, no se afirma de memoria |

---

## Tareas (R3: 4 tareas, 0 comandos largos)

### Tarea 1: Inventario y decisiones operativas (AC-S3 / AC-S4)
- Medir la superficie pública del repo por commit, ruta y clase de material (evidencia de cliente, logs, artefactos), con dueño y evidencia **no secreta** por fila.
- Registrar el estado de rotación preventiva de la clave expuesta y de contención de datos del cliente, cada uno con dueño (operador) y evidencia.
- Comparar retirada desde HEAD contra saneamiento del historial y sus consecuencias **antes** de solicitar autorización específica.
- **No ejecutar** rotación, retirada, reescritura ni cambio de visibilidad por haber aprobado el plan: cada acción externa requiere autorización explícita del usuario.

### Tarea 2: Sanear errores del provider (AC-S1)
- Corregir `_query_gemini` / `_query_provider` en `modules/auditors/llm_mention_checker.py` para que secretos de URL, headers o excepciones no lleguen a logs ni stderr.
- Probar el error HTTP 403 con un **token sintético**, sin llamada de red y sin imprimir el valor del secreto en la prueba.

### Tarea 3: Controlar lo que se prepara para publicar (AC-S2)
- Ampliar `_check_no_secrets` en `scripts/run_all_validations.py` para caminar **contenido staged** de cualquier extensión de texto (no solo asignaciones en `*.py`), incluida salida redactada y tests.
- Dar estados explícitos a archivos no legibles / no cubiertos; separar la detección de claves de la política que impide versionar material de cliente.
- Verificar la conexión con los hooks existentes; cambios de hooks/configuración/dependencias requieren alcance autorizado, **nunca** un bypass.

### Tarea 4: Certificar los controles
- Pares NR7 (verde/rojo) por cada detección; baseline NR1 pre/post; pruebas divergentes staged vs worktree.
- Registro de la puerta operativa AC-S4 en `evidence/FASE-P5/`.

**Criterios de aceptación**: los de `06-checklist-implementacion.md` §FASE-P5 (AC-S1…AC-S4) y `01-plan-maestro.md` §4 FASE-P5.

---

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: P5 ✅ con fecha e iteraciones medidas (unidad + corte declarado).
2. `README.md`: tabla de progreso.
3. `09-documentacion-post-proyecto.md`: acumular (nuevo control de secretos; sin módulos nuevos).
4. `10-analisis-post-implementacion.md`: fila + lecciones + métricas + puerta AC-S4.
5. `00-lecciones-capitalizadas.md` §2: realidad contra promesa.
6. `evidence/FASE-P5/`: inventario medido, pares NR7, prueba 403 sintética.
7. `python scripts/build_lesson_index.py --check` (y regenerar el par `.md`+`.json` si vence).
8. `run_all_validations.py --quick`.

**NO esperar a la siguiente sesión.**

---

## Criterios de Completitud (CHECKLIST)

- [ ] AC-S1: error 403 con token sintético no filtra el secreto a logs/stderr (par NR7 rojo/verde)
- [ ] AC-S2: `_check_no_secrets` cubre contenido staged multi-extensión con estados no-leíble/no-cubierto; un secreto detectado bloquea
- [ ] AC-S3: inventario público medido por commit/ruta/clase con dueño y evidencia no secreta
- [ ] AC-S4: puerta operativa registrada (rotación/contención con dueño y estado), sin acción externa ejecutada sin autorización
- [ ] Iteraciones medidas y escritas (unidad + corte declarado — un `—` no cierra)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada (8 puntos)

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **NO** rotar claves, retirar/reescribir historial, cambiar visibilidad del repo ni hacer push en esta sesión sin autorización explícita específica del usuario.
- **NO** versionar valores de secretos ni cifras sensibles del cliente en ningún artefacto; el inventario referencia por ruta/hash, no por contenido.
- **NO** weaken gates ni añadir bypass al control de secretos para obtener verde.
- **NO** abrir P6/RELEASE desde aquí: P5 se cierra técnico-offline y registra su puerta; las acciones externas siguen pendientes del operador.
