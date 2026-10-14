# Cierre de seguimientos asignados a FASE-VERIFY (2026-10-14)

El prompt de FASE-E2E dejó dos cosas que el run único **no** certifica solo, y una tercera abierta
desde FASE-C. Esta nota las re-mide contra los artefactos (L-V.2) y dice qué queda abierto.

## 1. «AC10 emitió 2 CRITICAL donde FASE-B anticipaba 3» — **CERRADA, sin hallazgo**

`FASE-B/medicion-falso-positivo.md` publicaba sobre el run de referencia: «la propuesta del run
único de Don Alfonso **sí** producirá CRITICAL por los dos absolutos de prosa de garantía **más la
celda «(Verificado)» de la tabla de timeline»**. El acta de la corrida emitió 2.

Re-medido con el patrón del módulo y la bandera de su llamada (`03-re-medicion-ac10-crudo.txt`):

| Documento | `LENGUAJE_VERIFICACION` (literales) | `CUANTIFICADOR_ABSOLUTO` (literales) | Emitidas por el revisor |
|-----------|------------------------------------:|-------------------------------------:|------------------------:|
| Propuesta del run único (2026-10-12, 14.559 car.) | **0** | 10 (6 en fila de tabla o monto declarado) | **2** |
| Propuesta que generó la predicción (2026-10-07, 14.690 car.) | **1** («Verificado») | 10 | **3** |

La diferencia es **del dato, no del patrón**: la propuesta de esta corrida no contiene ninguna
celda con lenguaje de verificación, y el grupo `LENGUAJE_VERIFICACION` no lleva filtro estructural
(DEC-B1), así que no había nada que filtrar ni nada que detectar. Con 0 literales, 2 emitidas es
la salida correcta del criterio curado. La predicción de FASE-B estaba bien medida sobre su propio
documento; lo que no previó es que la propuesta del run único traería otra fila de timeline.

**Consecuencia para la certificación**: AC10 queda ✅ y AC14 queda ✅ con los dos CRITICAL
clasificados como **verdaderos** (absolutos de prosa de garantía bajo tier declarado `B+`), que es
lo que la propia AC14 pedía nombrar.

## 2. «AC19 no se ejercitó en flujo real» — **queda como límite declarado, no como hallazgo**

Medido en el acta del run: el `extraccion.estado` de los cuatro revisores es de la familia `OK_*`
(`OK_CON_PROMESAS` en el report de Bot 4), así que la fila nueva (`verified_critical` /
`verified_block` sin exigir `status.is_ok`) no tenía nada que decidir: el bloqueo salió por el
camino viejo (`OK_WITH_FINDINGS` con 2 CRITICAL). Lo que el run **sí** ejercitó de AC19 es su
vecino: `derive_corrective_actions` nombró `OVER_PRESENTATION` con dueño `comercial` en vez de
disfrazarse de `VEREDICTO_BLOQUEANTE_SIN_HALLAZGO`, y `blocks_delivery_zip` suprimió el ZIP
(`package_evidence.suppressed: true`, 56 miembros).

AC19 se certifica, por tanto, **por la suite** (`FASE-C2/01`–`04`: rojo pre-cura 6 failed, M1 6
failed, M2 2 failed con la causa nombrada, y el differential de los tres estados leídos por la rama
real). Para verla en producción haría falta una corrida con proveedor fallido o respuesta ilegible,
es decir **otra inferencia pagada**, y el plan fija una sola corrida (maestro §4). Se registra con
dueño **Operador** en `10-analisis` §Seguimientos; VERIFY no la da por certificada «en producción».

## 3. `P6.5` sigue negando al revisor que corrió (`L-CST-7`) — **ABERTA, re-confirmada**

Leída otra vez en el acta de la corrida única, clave `clauses.P6.5`:

- `status: NOT_EVALUABLE`, `source_artifact: null`, finding «Reservada para Bot 4 (honestidad NL) —
  D-T1.3 opción a».
- En el **mismo archivo**, `reviewer_reports` muestra `honesty_reviewer` con `status:
  OK_WITH_FINDINGS`, `findings_count: 3`, `critical_count: 2`, `recommendation: BLOQUEAR` y su
  `report_path` a `revision_honestidad.json`; y el `verdict` del acta es `BLOQUEADO` **por los
  hallazgos de ese revisor al que la matriz declara no evaluable**.

Es la forma exacta del defecto que AC12 curó para `P6.2`, y ninguna AC de este plan gobierna esa
fila, así que no se tocó. El caso es más grave que el de P6.2: aquí la cláusula `NOT_EVALUABLE`
convive con el bloqueo que esa misma cláusula produjo, y quien lea solo la matriz concluirá que la
honestidad NL no se evaluó en la única corrida del plan. Queda con dueño **Operador**, con la
decisión pendiente de si una cláusula `NOT_EVALUABLE` puede ser la fuente de un `BLOQUEADO`.

## Lo que esta fase añade al registro

Ninguna AC falló, así que no hay ❌ ni parches. Se cierra la fila 1, se re-confirma la fila 3 con su
dueño y se estampa la fila 2 como límite declarado de AC19. Las lecciones que dejó la verificación
están en `10-analisis` (una generalización de `L-CST-4` y la lectura de `L-V.2` en esta fase).
