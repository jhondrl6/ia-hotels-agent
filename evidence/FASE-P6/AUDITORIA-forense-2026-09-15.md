# Auditoría forense — FASE-P6 (2026-09-15)

**Objeto**: contrastar la implementación de FASE-P6 (AC-G1…AC-G5) contra
`05-prompt-inicio-sesion-fase-P6.md`, `01-plan-maestro.md` §4 y `06-checklist-implementacion.md`,
incluida la documentación de fase. **Método**: lectura de diffs y código en disco, corrida propia
de tests y validaciones, grep de símbolos declarados. Nada se aceptó por declaración documental.

## Veredicto

**Parcialmente conforme.** El código existe, funciona y no degrada nada (medido en corrida propia);
pero la tarea 4 del plan se ejecutó con actas escritas a mano —explícitamente prohibidas por el
propio plan—, la cláusula WhatsApp/evidencia de AC-G2 nunca se tocó, NR7 está sobredichado, hay
falsedades documentales en los cinco registros de cierre, la celda de iteraciones repite L-P5.3 y
la fase quedó sin commitear pese a declararse ✅.

## Lo que SÍ se verificó conforme (medido, no declarado)

| Hecho | Medición de esta auditoría |
|-------|---------------------------|
| Suite completa | `pytest tests/ -q` → **4.189 passed, 2 failed (mismo par ajeno), 41 skipped, 4 xfailed** — idéntico al POST claimed |
| Tests nuevos | 4 archivos, `def test_` = 5+4+6+5 = **20**, 20/20 verdes en 1.08 s |
| `--quick` | **10/10** (corrido aquí, no heredado) |
| Índice de lecciones | `build_lesson_index.py --check` → `[OK] fresco (299 IDs)` |
| `judge.py` | `git diff` vacío — intacto, como declara el checklist |
| AC-G2 cargador | `main.py` (`_load_latest_onboarding_data`): quitado el guard `clientes_dir.exists()`, el fallback `observations.json` resuelve sin `clientes/`; 4 tests lo ejercitan |
| AC-G3 orden | `_compute_package_evidence` → acta → segunda escritura → `suppress()`; la huella es del `.zip.tmp` real leído por los revisores |
| AC-G1 esencial | `asset_zip_paths` hasta `generate_delivery_template`; `ESTIMATED_` preservado; desconocidos con sección explícita (no desaparecen) |

## Incumplimientos

### I1 — Tarea 4 ejecutada contra su propia prohibición (mayor)
El plan: "Probar el productor, ZIP real, revisores y Juez juntos" y "**No** escribir un acta a mano
como sustituto del flujo". `tests/test_ac_g4_g5_multi_hotel_matrix.py` construye `base_acta` dict y
`ReviewerReport` a mano y llama `enrich/finalize`. Grep `DeliveryPackager` en los 4 archivos nuevos:
**0 coincidencias**. Ningún ZIP real, ningún revisor real. AC-G4/G5 verificados solo sobre la lógica
del Juez (que P2 ya cubría), no sobre el flujo multi-hotel que esta fase pedía.

### I2 — Perfil "Don Alfonso" no fiel
Se declara "Don Alfonso anonimizado" como tier A; el caso real midió techo **B_PLUS** con veredicto
BLOQUEADO y 4 revisores con hallazgos (P4). El perfil no reproduce el caso que nombra.

### I3 — NR7 sobredichado y de tipo equivocado
Checklist, `00-lecciones`, `09` y `10` declaran "5 pares, **uno por AC-G**".
`nr7_mutation_checks.md` contiene 4 pares de AC-G5 y 1 de AC-G4 — **cero para AC-G1, G2, G3**.
Las mutaciones registradas cambian inputs/expectativas del test, no revierten el fix
(exigido por AC-G5/L-T4A.5: "cerrar revirtiendo el fix, no simulando el veredicto").

### I4 — AC-G2 cláusula 2 sin implementar ni testear
`_observation_to_onboarding_format` (intacto, no tocado por P6) fabrica por defecto:
`epistemic_status='verified'`, `rooms=10`, `canal_directo_pct=20.0`, y fija
`campos_confirmados` a 4 campos esté o no esté el dato. El plan prohíbe literalmente que la
ausencia se convierta en `verified`. Ningún test cubre la cadena fuente→converter→validación.
El "CERRADO F-P4.3" de `10-analisis` es por redacción, no por código.

### I5 — AC-G1: la "ruta real" es una segunda representación
`main.py` re-deriva el prefijo `ASSETS/` duplicando el predicado del packager (len(parts)>1 ∨ sufijo)
sobre una base de path distinta, en vez de consumir los `dest` que el packager escribe — anti-patrón
L-SR3/DA-P1.5 que el propio plan nombra. Diverge para archivos sin extensión en ruta anidada.
`ImplementationOrderGenerator` (alcance explícito de T1) no fue revisado ni dispuesto en documento
alguno.

## Falsedades documentales (registro ≠ artefacto)

| Dónde | Afirmación | Estado medido |
|-------|-----------|---------------|
| `00-lecciones` §2 (bloque P6) | "los tests de AC-G1 corren contra un **ZIP real construido por `DeliveryPackager`** en `tmp_path`, no contra un diccionario escrito a mano" | FALSO — es exactamente al revés. Reincidencia de L-P5.2 (acta desde la intención, no desde el artefacto) |
| `06-checklist` AC-G1 | `asset_responsibility_contract.py` "con `asset_zip_paths()` y `_classify_unknown_assets()`" | Esos símbolos **no existen** (grep 0); son un parámetro inline y una clasificación inline |
| `09` (tabla Aporte) | "unknown assets … **visible en el acta**"; "el consumidor (Bot 3) lee rutas normalizadas" | La sección vive en IMPLEMENTATION_ORDER.md, no en el acta; `asset_reviewer.py` no menciona `asset_zip_paths` (grep 0) |
| `09` | "F-P4.1 (contrafactual de enforcement) vía AC-G5" | F-P4.1 era el stub; el contrafactual sigue sin observar (lo dice `10-analisis` — contradicción entre ambos docs) |
| `10-analisis` F-P4.9 | `package_evidence.{sha256,member_count,files_sample}` | La clave `files_sample` **no existe** en el código |
| `nr1_baseline_post.txt` | "Corte: HEAD con AC-G1..AC-G5 implementados" | FALSO — HEAD es `48a242b` (P5); todo P6 estaba en working tree sin commitear |

## Post-ejecución del prompt (8 puntos)

1 dependencias ✔ · 2 README **✘** (fila P6 sigue "⬜ Pendiente", encabezado "6/8") · 3 09 ✔ con
falsedades · 4 10 ✔ con falsedades · 5 00 ✔ con falsedad · 6 evidencia **parcial** (no hay artefactos
de perfiles/caminos; NR7 incompleto) · 7 índice ✔ · 8 quick ✔.

## Déficit formal

- Cero commits de la fase (13 modificados + 5 nuevos). REGISTRY sin FASE-P5 ni FASE-P6 (rompe el
  patrón P1-P4).
- Celda de iteraciones: "unidad declarada" sin nombrar unidad, valor ni corte — L-P5.3 (recién
  capitalizada el mismo día: "un `—` no cierra") reproducida en la fase siguiente.

## Riesgo nuevo introducido por el código (hallazgo de esta auditoría)

`main.py` rama de supresión: la **segunda escritura del acta** (AC-G3) quedó dentro del `try`
never-block cuyo `except` hace `publish(quarantine_tmp_path)` cuando `delivery_zip_path is None`.
Un fallo de I/O al re-escribir el acta en la rama de bloqueo **publicaría el ZIP bloqueado**.
Baja probabilidad, blast radius alto (entrega de paquete no certificado).

## Remediación acordada (sesión P6-R, autorización del operador 2026-09-15)

- **R1**: matriz AC-G4/G5 contra el flujo real (packager.write → ZIP real → 4 revisores → Juez →
  suppress/publish), 3 caminos causales + perfil B+ con primer piso (Don Alfonso anonimizado);
  los actas-a-mano quedan reetiquetados como unitarios del Juez.
- **R2**: pares NR7 por **reversión del fix**, incluidos G1/G2/G3; `nr7_mutation_checks.md` con
  método declarado por par y anotación del error original.
- **R3**: anotaciones (no reescritura) de las 6 falsedades sobre el registro histórico.
- **R4**: converter sin defaults inventados (`verified`, rooms, pct, campos_confirmados) + tests.
- **R5**: re-escritura del acta fuera del camino cuyo fallo publicarí­a el ZIP bloqueado.
- **R6**: mapeo ZIP de fuente única (el packager expone los `dest` reales) + disposición de
  `ImplementationOrderGenerator`.
- **R7**: commits con corte real, REGISTRY P5+P6, README 7/8, celda de iteraciones con
  unidad+valor+corte, NR1 re-medido tras la remediación.

**Estado R1-R7**: ✅ CERRADOS el 2026-09-15 en la misma sesión de remediación.
R1/R2 → `tests/test_p6r_full_flow_matrix.py` (5/5 verdes) y `nr7_p6r_mutation_checks.py`
(5/5 pares verde→rojo→restaurado). R3 → anotaciones en `00`/`06`/`09`/`10` y en el propio
`nr7_mutation_checks.md`. R4/R5/R6 → commit `c31422a`. R7 → REGISTRY P5+P6 vía
`log_phase_completion.py`, README 7/8, iteraciones con unidad+valor+corte, NR1 POST-P6-R
**4.196 passed** (`nr1_post_p6r.txt`), `--quick` 10/10 e índice regenerado.
Lección nueva nacida de la remediación: **L-P6.4** en `10-analisis` (el instrumento de
reversión falló tres veces por criterios propios no auto-verificados).
