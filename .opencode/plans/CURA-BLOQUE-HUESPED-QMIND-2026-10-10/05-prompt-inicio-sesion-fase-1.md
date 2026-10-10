# Prompt de inicio de sesión — FASE-1 de CURA-BLOQUE-HUESPED-QMIND-2026-10-10

## 1. Encabezado

- **Plan:** `CURA-BLOQUE-HUESPED-QMIND-2026-10-10` (`.opencode/plans/CURA-BLOQUE-HUESPED-QMIND-2026-10-10/01-plan-maestro.md`)
- **Fase:** FASE-1, única fase del plan. Ejecuta **AC-N1** y **AC-N2**.
- **Sesión:** una. Presupuesto 90 `tool_use`, con checkpoint declarado si se excede.
- **Corte autorizado:** «listo para revisión», sin commit. `git commit`, L3 y push solo con literal del operador.

## 2. Contexto

**Estado de fases anteriores:** no hay. FASE-1 es la primera y la última fase de implementación del plan.

**Base técnica.** El instrumento es `scripts/validate_qmind_writeback.py`. El defecto está dictaminado con medición
en `evidence/DIAGNOSTICO-HUESPEDES-JEV-2026-10-10/00-acta.md`: el bloque que emite `[DUPLICADO-VIGENTE]` por
fuente huésped solo se recorre en 4 de las 12 rutas del bucle de `verificar_contenido()`; en las otras 8 el
instrumento no mira, y su `[CONTADOR]` publica `0 fuente(s) huesped(s)` como si fuera un dato del censo. Dos de
esas 8 rutas se toman cuando `descargar_fuente()` falla, y son las que produjeron la varianza observada (5
huéspedes en una corrida, 1 en la siguiente, mismo repo y mismo censo). La reproducción offline está en el crudo
`04-repro_offline_2x2.txt` de esa evidencia: matriz de cinco configuraciones con censo idéntico y una sola
variable, la respuesta de `source download`.

El censo se lee una vez por corrida en `main()` con `fetch_sources()`, y esa misma lista se pasa a
`verificar_contenido()`; `_huespedes_sin_contabilidad()` lee solo el registro y el censo, **no baja nada**. Ese es
el hecho que hace del salto un defecto y no una abstención legítima: el hallazgo no necesita la observación que la
rama fallida no tiene.

**Lecciones capitalizadas aplicables** (`00-lecciones-capitalizadas.md` §2): `L-QW.4` (un límite escrito no se
cierra solo: este plan es el AC que faltaba), `L-QW.2` (las huéspedes son los duplicados que el corpus ya
documentó), `DA-C3` y `L-D5` (vacío no es ausente; el denominador se cuenta donde se mide, no se deriva),
`L-ENT.12` (el verde no prueba cobertura: mutation check y cobertura medida).

## 3. Tareas

1. **PRE.** Re-medir HEAD y paridad; correr la selección literal
   `tests/test_validate_qmind_writeback_escritura.py` + `tests/test_build_lesson_index_s15_fecha_versionada.py`
   con `PYTHONUTF8=1` y archivar el crudo con el EXIT dentro y el intérprete declarado en
   `evidence/CURA-BLOQUE-HUESPED-QMIND-2026-10-10/FASE-1/`.
2. **AC-N1.** Reestructurar `verificar_contenido()` según DA-BH.2: el dictamen por entrada pasa a un ámbito cuyo
   `return` reemplaza a cada `continue`, y el bloque huésped queda como última sentencia del bucle, de modo que
   **ninguna** ruta pueda saltarlo. Retirar la llamada duplicada que vivía dentro de la rama de migración y
   actualizar la docstring de `_huespedes_sin_contabilidad()`, que describe el estado anterior.
3. **AC-N2.** Añadir al `[CONTADOR]` su denominador de observación, contado en el sitio donde el bloque corre.
   Colocarlo **después** del recuento de huéspedes: medido, hay dientes que anclan la secuencia literal de la
   aritmética seguida del recuento, e intercalar texto entre ambos los rompe sin que la cura sea la causa.
4. **Dientes.** Escribir `test_una_bajada_que_falla_no_suprime_a_su_huesped_de_contabilidad` (AC-N1) y
   `test_el_contador_publica_su_denominador_de_observacion` (AC-N2). Re-anclar
   `test_un_vencido_por_cuerpo_en_la_mesma_entrada_no_evalua_a_su_huesped_limite_declarado`, que se pone rojo
   **por diseño**: su docstring declara que ese día llega, y se re-escribe como diente de la cura con la
   justificación dentro del test.
5. **Mutantes (R2.8).** Un mutante por AC, aplicado en el árbol y restaurado con verificación de sha256; las dos
   salidas (rojo con el guard apagado y verde restaurado) archivadas como crudos.
6. **POST.** Selección literal de nuevo, quick, y el modo completo con `PYTHONUTF8=1` si el presupuesto alcanza.
7. **Cierre.** `10-analisis-post-implementacion.md`, `log_phase_completion.py --fase FASE-1 --fecha 2026-10-10`,
   regenerar el índice de lecciones, y declarar los cinco cortes sin commitear.

## 4. Tests obligatorios

- Los dos dientes nuevos, nombrados por su causa.
- El re-anclaje gobernado del diente de caracterización de la deuda hermana.
- La selección literal completa verde: la referencia de apertura es **65 passed, EXIT=0**; el POST debe sumar los
  dientes nuevos y no perder ninguno de los existentes salvo el re-anclado, cuya pérdida se declara con su motivo.
- Quick 13/13 con EXIT=0 (el denominador lo imprime la corrida, no se fija aquí).

## 5. Post-ejecución

Archivar en `evidence/CURA-BLOQUE-HUESPED-QMIND-2026-10-10/FASE-1/`: crudo PRE, crudo POST, las dos salidas de
cada mutante, el quick POST y, si se corre, el modo completo. Los crudos de pytest se archivan **sin
re-codificar**. Ningún secreto ni enlace firmado en los crudos.

## 6. Criterios de completitud

- AC-N1: las 12 rutas del bucle evalúan a su huésped; una bajada que falla no cambia el EXIT por esa vía; el
  mutante apaga el bloque universal y el diente cae por la causa nombrada.
- AC-N2: el `[CONTADOR]` publica el denominador de observación contado, no derivado; `0 fuente(s) huesped(s)` solo
  puede imprimirlo una corrida que recorrió el bloque en todas sus entradas.
- Sin regresión en el rojo vivo de la era G: `--strict` sigue cerrando EXIT=1 por `[DUPLICADO-VIGENTE]`.

## 7. Restricciones

Cero escrituras remotas (`source upload` y `source delete` prohibidos; `source list` y `source download` de solo
lectura, con racha contada y sin reintentos en bucle). No editar `AGENTS.md`, `.cursorrules`, `VERSION.yaml` ni
documentos de planes archivados. No tocar el notebook ni marcar reemplazos. Ningún `git commit` sin pathspec: el
índice tiene 13 rutas staged ajenas (deuda `S-CIM-7` del plan hermano). Citar por símbolo, nunca por número de
línea (R2.2).

## 8. Prompt de ejecución

```
Lee .opencode/plans/CURA-BLOQUE-HUESPED-QMIND-2026-10-10/01-plan-maestro.md y ejecuta su FASE-1 completa: PRE
medido, AC-N1 y AC-N2 sobre scripts/validate_qmind_writeback.py, los dos dientes nuevos y el re-anclaje gobernado
en tests/test_validate_qmind_writeback_escritura.py, un mutante por AC con restauración verificada por sha256,
POST, cierre documental con 10-analisis y log_phase_completion.py, índice de lecciones regenerado, y los cinco
cortes declarados sin commitear. Presupuesto 90 tool_use. Cero escrituras remotas y ningún git commit sin
pathspec.
```
