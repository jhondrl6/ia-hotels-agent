# FASE-RELEASE — Revisión y cierre documental

**Estado: PENDIENTE.** No cambia código ni activa proveedores globales. Requiere C con resultado válido o instrucción expresa de cierre administrativo sin inferencias, conservando los AC no ejercitados.

## Lecturas y contexto

Leer maestro, contrato, dependencias, checklist, 00, 09, 10 y los artefactos A/B/C existentes. Re-medir HEAD/status. No deducir resultados de un resumen si falta el JSON/JSONL fuente.

| Lección del Paso 0 | Aplicación en RELEASE |
|---|---|
| L-R.3 | AC11: todos los AC se revisan con denominador y artefacto propio |
| L-R.4 | AC11: no presentar una regla pendiente como control ejecutado |
| L-ENT.9 | AC4/AC12: no certificar un proveedor por el éxito agregado de otro |
| L-P6.3 | AC5: declarar alcance de la muestra y calidad no medida |

## Tareas

1. Revisar cada AC contra su artefacto nombrado. Regenerar comparación y decisión mediante el modo local del runner si hubo corrida. No llamar a modelos ni reparar código.
2. Confirmar por separado recomendación Jev, elegibilidad de D6 y estado de transferencia. Con permiso literal para editar la deuda: re-leer maestro/dependencias vigentes del hermano, localizar su estado real y hacer solo el cambio autorizado. Sin permiso, registrar transferencia PENDIENTE aquí, nunca deuda cerrada en otro plan.
3. Completar 09/10 con resultados medidos, límites, errores, coste calculado/facturado y lecciones. Si hubo cierre sin inferencias, conservar NO-EJERCITADO y motivo en cada AC afectado; no declarar implementación exitosa del piloto.
4. Seguir el flujo documental oficial para fases ejecutadas, verificando comandos actuales y autorización de archivos externos al plan. Este es un cierre documental sin bump de VERSION ni cambio de configuración central. Si el flujo exige cambios fuera de alcance, pedirlos antes; sin permiso, checkpoint.
5. Re-leer la interfaz vigente del writer QMind; el hermano de escritura puede haber cambiado sus flags/semántica. Solo con autorización de write-back, publicar el aporte durable y verificar contenido según el contrato vigente. No confundir título existente con contenido fresco.
6. Solo después de un cierre válido, write-back confirmado y permiso de archivado, mover el plan a Archives según el workflow; regenerar índice después. No ejecutar movimientos, commit o push por inercia.

## Verificaciones obligatorias

```bash
venv/Scripts/python.exe scripts/validate_lesson_capitalization.py
venv/Scripts/python.exe scripts/validate_plan_citations.py
venv/Scripts/python.exe scripts/validate_plan_closure.py
venv/Scripts/python.exe scripts/validate_opencode_refs.py
venv/Scripts/python.exe scripts/build_lesson_index.py --check
```

En el cierre de fases ejecutadas, usar además los tests y validaciones del contrato. No escribir baselines nuevos ni editar configuración central para neutralizar un rojo.

## Post-ejecución y completitud

Actualizar README, dependencias, checklist, 00, 09 y 10. La declaración de cierre real vive en `10-analisis-post-implementacion.md`, coherente con todos los estados; no se escribe antes de terminar los requisitos aplicables.

- [ ] ACs contrastados contra archivos reales, con parciales/no ejercitados visibles.
- [ ] Coste observado/calculado/facturado y limitación de versión DeepSeek distinguidos.
- [ ] D7/D6 registradas o transferencia pendiente explícita, sin cambios no autorizados.
- [ ] Documentación oficial/write-back/archivado con permisos resueltos o checkpoint, nunca cierre fingido.
- [ ] Índice fresco y validadores ejecutados después de la última edición.
- [ ] Ninguna inferencia, cambio de runtime, instalación, commit o push implícitos.
