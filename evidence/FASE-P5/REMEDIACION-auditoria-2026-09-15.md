REMEDIACIÓN FASE-P5 — auditoría forense de b25b63a (2026-09-15)
================================================================
Origen: auditoría externa al cierre de FASE-P5. Halló la fase cerrada con 4/8
puntos post-ejecución, sin iteraciones registradas, con una afirmación falsa en
`NR7-AC-S2-green.txt` y —medido en esta sesión— con el escaneo staged **muerto**.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. HALLAZGO NUEVO (mayor que los de la auditoría): el escaneo staged no ejecutaba nunca
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Causa: en b25b63a, `import re` vive solo dentro de `_check_no_secrets` (scope de
función). `_check_staged_content` usa `re.search` buscando el global → `NameError`
→ tragado por su propio `except Exception: return []`. Con cualquier contenido
staged presente, el check devolvía [] sin mirar. Es L-T2C.2 exacta (NameError
latente bajo un except ancho), reproducida en el detector de secretos.

Reproducción mínima (pre-parche, repo temporal con secreto solo en el índice):
    staged violations (esperado 1, bug=0): []
    el patron SI coincide con el staged diff: True
    NameError replicado: name 're' is not defined

Efecto sobre la evidencia de P5: el par NR7 de AC-S2 mutaba los patrones de
valor, no la ruta staged — un verde que no ejercitaba la rama (hermano de
L-P3B.2: el test no *llegó* a la aserción).

Fix: `import re` a nivel de módulo; el `except Exception` se queda pero ya no
puede ocultar el NameError; y el camino queda **permanentemente vigilado** por
`tests/test_p5_ac_s2_remediacion.py::TestStagedVsWorktreeDivergence`.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. REMENDADOS DE LA AUDITORÍA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

a) NO_CUBIERTO real (AC-S2 / L-PF6): el whitelist de 13 extensiones se reemplaza
   por alcance tracked (`git ls-files`) + sniff NUL. Todo archivo versionable con
   pinta de texto se lee (`.cursorrules`, `.gitignore`, `pre-commit`, `per-hotel`,
   `.ps1`, `.diff`, sin-extensión…); binarios conocidos se excluyen **declarados**
   en el mensaje; lo no clasificable bloquea con estado NO_CUBIERTO. El verde se
   nombra SIN_HALLAZGOS con el conteo de leídos. Cambio de semántica deliberado y
   registrado: de "workspace" (3084 archivos, 41 % nunca versionables) a "lo que
   se prepara para publicar" (tracked + staged) — que es literalmente el objetivo
   de P5 en el plan maestro.
b) Política de material de cliente SEPARADA del detector de claves: nuevo check
   `[5/10]` (`_check_client_material`) + `config/client_material_policy.yaml`.
   Bloquea tracked/staged con marcadores de cliente fuera de cuarentena
   (archives/, evidence/, .opencode/). Grandfathered con dueño y pendencia AC-S4:
   `tests/fixtures/donalfonsohotel_onboarding.yaml` (blob de cliente real en
   origin/master, F-P4.5 — su retirada es acción externa, no se ejecuta aquí).
c) Par NS7 staged-vs-worktree: test con repo git real donde el secreto vive solo
   en el índice y el árbol está limpio → BLOCKING (rojo) / repo limpio →
   SIN_HALLAZGOS (verde). La mutación del rojo es el propio bug histórico.
d) Numeración: 9 → 10 checks rápidos; modo completo 14 (las etiquetas full
   venían mezclando denominadores 12/13 desde antes de P5 — homogeneizado). El
   contract test del cableado (`test_run_all_validations_registra_el_check_...`)
   y el template de lecciones se actualizaron a /10; ese test existe justo porque
   renumerar rompió silanciosamente etiquetas en fases anteriores.
e) Nota: `AGENTS.md` sigue diciendo "--quick 9/9" y "13 en el completo"; su
   edición/commit exige instrucción explícita (clasificador) → se deja para
   RELEASE con el bump, declarado en Seguimientos.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. MEDICIONES DE LA REMEDIACIÓN (unidad declarada donde el instrumento no alcanza)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- `--quick`: 10/10. Secrets: SIN_HALLAZGOS sobre tracked+staged con excluidos
  declarados (0 binarios conocidos, 1 symlink). Client Material: SIN_HALLAZGOS
  sobre 2182 rutas × 4 marcadores, 1 grandfathered.
- Tests nuevos: 10 funciones (`tests/test_p5_ac_s2_remediacion.py`); suite P5
  anterior (11) sigue verde; contract tests cableados: verdes.
- NR1 POST completo: ver NR1-baseline-post-remediacion.txt (corrida 2026-09-15).
- Iteraciones de la sesión de remediación: FUERA DE SERVICIO (R2.1/D-V2.1) — el
  transcript de la sesión P5 original está fuera del alcance del instrumento y
  el acceso fue denegado al clasificador (mismo caso D-V2.1 de P2). Unidad
  auto-declarada y medida por git: **commits de ejecución por sesión de fase**;
  corte = HEAD al cerrar. P5 original: 1 (`b25b63a`), 0 rechazos de hook.
  Remediación: 1 (este commit), 0 rechazos esperados.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. LO QUE LA REMEDIACIÓN NO HACE (restricciones de P5 intactas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- No rota claves, no reescribe historial, no cambia visibilidad, no hace push.
- No retira los blobs grandfathered: registra su dueño y deja la decisión en la
  puerta AC-S4.
- No weakenea gates: agrega un check, estrecha el alcance del existente y hace
  visible un detector que daba verde sin leer.
