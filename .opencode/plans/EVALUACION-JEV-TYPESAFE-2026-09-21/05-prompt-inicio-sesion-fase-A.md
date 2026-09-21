# FASE-A — Corpus y protocolo offline

**Estado: PENDIENTE.** Prompt preparado para una sesión futura, no orden de ejecución actual.

Objetivo: preparar una muestra revisable y su instrumento determinista, sin llamar a proveedores. Dependencias: instrucción del operador, corpus local y persona responsable de etiquetas/saneamiento. B/C del hermano no bloquean esta fase.

## Lecturas y contexto

Leer README, maestro, contrato, dependencias y `00-lecciones-capitalizadas.md`; consultar workflow canónico y documentación de contribución aplicable. Re-medir HEAD/status y frescura del índice. No heredar un número de corpus como constante de tests.

DeepSeek es el comparador habilitado; Anthropic está excluido. Todavía no existen costura ni consumidor al redactar este prompt, y no se crean aquí.

| Lección del Paso 0 | Aplicación en A |
|---|---|
| L-D5 | AC10: validar cálculos con casos cuyo resultado pueda comprobarse por otra vía |
| L-R.3 | AC3/AC10: denominadores, excluidos y recuperación distinta de clasificación |
| L-R.4 | AC11: distinguir control implementado, validación humana y requisito todavía sin instrumento |
| L-P6.3 | AC3/AC5: 60–100 pares es objetivo exploratorio, no garantía estadística |

## Tareas

1. Crear `scripts/evaluate_jev_pilot.py` con modos locales de preparación/check y cálculo determinista de métricas; no importar clientes ni leer credenciales. El `--help` fija la CLI real. Crear tests en `tests/quality_gates/jev_pilot/`.
2. Preparar candidatos desde corpus propio: identificar fragmentos originales, corte temporal, SHA, saneamiento y exclusiones. Recuperar texto suficiente, no usar sin revisión el enunciado truncado del índice. Separar metadatos que revelan la etiqueta de inputs que verán los modelos.
3. Acordar rúbrica y obtener etiquetas humanas ciegas a resultados, importancia y casos insuficientes; incluir omisiones conocidas, negativos difíciles y ambigüedad. Si la persona todavía no revisó, escribir BORRADOR, no «etiquetado humano».
4. Separar ajuste/evaluación por plan, deduplicar y publicar distribución y dependencias. Documentar disponibilidad histórica de las lecciones; las aprendidas después no cuentan como omisiones previas.
5. Preparar `muestra.json`, `etiquetas.json`, `protocolo.json` bajo `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/`. Proponer criterios de adopción/suficiencia, consultas de búsqueda fría, política de ajuste, caché y presupuestos con base explícita. Los valores pendientes impiden inferencias; no inventar aprobación.
6. Implementar el checker de esquema, hashes, splits, estados y prerequisitos. Su éxito solo acredita controles mecánicos, no sustituye juicio humano ni autorización de gasto. Fijar cómo se calculan incertidumbre y denominadores sin tratar todos los pares como independientes.

## Tests obligatorios y evidencia

| Prueba prevista | AC / resultado exigido |
|---|---|
| `test_sample_detects_content_change` | AC3: cambiar un fragmento invalida SHA |
| `test_split_rejects_same_plan_in_both_sets` | AC3: no fuga por plan |
| `test_labels_do_not_enter_payload` | AC3: etiquetas y metadatos de aceptación fuera de inputs |
| `test_unreviewed_sample_is_not_frozen` | AC3: revisión humana pendiente no pasa por aprobada |
| `test_metrics_known_counts_and_empty_denominator` | AC10: resultados conocidos; denominador cero no es 100 % |
| `test_prepare_and_check_do_not_construct_clients` | AC11: modos locales sin clientes/red |

Evidencia en `FASE-A/selftest.txt` y `FASE-A/muestra_check.json` dentro del directorio propio. Todo guard nuevo exige par verde/rojo causal; no basta una suite verde.

Una vez creados los tests, ejecutar:

```bash
venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot -v
venv/Scripts/python.exe scripts/validate_lesson_capitalization.py
venv/Scripts/python.exe scripts/validate_plan_citations.py
```

El comando del checker se toma de su CLI implementada y se copia literalmente al registro, con salida y exit code. No fingir que los comandos previstos del maestro ya existen.

## Post-ejecución y completitud

Aplicar el post-fase completo del contrato: README, dependencias, checklist, 09, 10 y 00 actualizados; registro oficial según permisos, validaciones y regeneración del índice. Registrar tests e iteraciones con unidad/corte, no cifras estimadas.

- [ ] Muestra revisada o borrador explícito con dueño; ninguna etiqueta humana fabricada.
- [ ] Instrumentos auto-verificados y evidencia legible.
- [ ] AC3 pendiente de commit se declara como tal; el commit se pide por separado antes de cualquier inferencia futura.
- [ ] Criterios/valores pendientes visibles; no llamar FASE-A plenamente verificada mientras falte lo exigido.
- [ ] Ningún paquete instalado, credencial inspeccionada, proveedor llamado ni archivo del hermano creado.

Si falta revisión humana o una decisión necesaria, dejar checkpoint dentro de A con el pendiente concreto, sin ejecutar B ni degradar las condiciones.
