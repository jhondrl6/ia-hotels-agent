# Lección: archivar un CONTEXT y el `--fix` que el hook `[3/8]` corre solo

**Fecha:** 2026-10-16 · **Sesión:** archivado de los dos contexto cerrados a `Historico/` (`26bd0f5`)
**Comandos involucrados:** `git mv`, `scripts/validate_opencode_refs.py` (`--fix`, `--write-baseline`), `scripts/build_lesson_index.py --check`, `scripts/verify_qmind_context_freshness.py`, hook pre-commit `[3/8]`

---

## Qué pasó

Mover un contexto de `.opencode/context/` a `.opencode/context/Historico/` rompe las referencias que
lo nombran por ruta. La herramienta tiene **escrita a propósito** esa mudanza:
`validate_opencode_refs.py::archived_promotion()` (líneas 127-144) promueve `plans/<X>` →
`plans/Archives/<X>` y `context/<Y>` → `context/Historico/<Y>`, y `fix_broken()` la usa primero. Como
el hook `[3/8]` invoca `--fix` en **todo** commit, la primera tentativa de commitear el `git mv`
reescribe las rutas dentro de los archivos que citan, no solo en los vivos.

Medido en la tanda: 7 roturas, de las cuales **5 viven en documentos byte-publicados o archivados**
(el `10-analisis` de `CURA-COSTURA-TRIBUNAL-2026-10-11`, dos citas del `CONTEXT-CONTRATO-PLANTILLA-TIER`
y dos autocitas del propio contexto movido). Reescribirlas cambia sus bytes, y esos bytes son la
prueba de su publicación en QMind: el verificador de frescura los pinta **VENCIDO** y el rojo aparece
en `run_all_validations.py` en modo completo (y en el write-back), es decir **en otro instrumento**,
lejos del commit que lo causó.

## Regla

**Cuando la mudanza toca archivos byte-publicados, el baseline se escribe y se stagea ANTES del
commit, y `--fix` no se corre a mano.** El orden no es negociable: el hook decide con el baseline que
ya está en disco.

## Checklist (orden ejecutado)

- [ ] `git mv` de las rutas (los bytes no se tocan) y `sha256sum` antes/después: tienen que casar.
- [ ] `python scripts/validate_opencode_refs.py` **en solo-lectura**: contar las roturas y nombrar
      `archivo:línea`. Si el número no es el que se predijo, parar y re-medir.
- [ ] `python scripts/validate_opencode_refs.py --write-baseline`: absorbe las roturas actuales en
      `.opencode/refs_baseline.txt`. La clave es el **par `archivo|referencia`**, así que dos citas de
      la misma referencia en un mismo archivo son **una** entrada (medido: 7 roturas → 5 entradas).
      El archivo se reescribe completo con `newline="\n"`; esperar adiciones, no supresiones.
- [ ] Volver a la corrida de solo-lectura: `[PASS] EXIT=0`. **Esta es la corrida que el hook hará con
      `--fix`**: si da PASS, el hook no toca nada y el commit no puede editar un congelado.
- [ ] `git add .opencode/refs_baseline.txt` y commit con pathspec de **ambas** mitades de cada rename
      (más el baseline). El `add` antes del pathspec, por la lección hermana de abajo.
- [ ] Después: `git show --name-status -M` (los renombres deben salir `R100`), `sha256sum`,
      `build_lesson_index.py --check` y la población de frescura por lectura local.

## Lo que NO cambia con la mudanza (y por eso no hay que regenerar nada)

- **Índice de lecciones**: `build_lesson_index.py` recorre `.opencode/context/` con `rglob` y etiqueta
  `context/<stem>` (:303-305), sin el subdirectorio. El mv es invisible para `[6/8]`; el par no viaja.
- **Frescura QMind**: `Historico/` está excluido por diseño (R2.5, `verify_qmind_context_freshness.py:118`
  y `:264-266`). El contexto pasa a `[EXCLUIDO]` con su razón impresa y la fuente del notebook queda
  como instantánea byte-exacta. No se re-subе nada.
- **`registro.json` del write-back** no tiene campo de ruta: no se toca.
- **La segunda vía de gobernación** resuelve los nombres citados por los planes archivados **solo en la
  raíz** de `context/`. Un citado que ya no resuelve cae en silencio — no es rojo. Si esa caída importa,
  se consigna en el sello de la tanda, no se espera que el instrumento la grite.

## Contrafactual y alcance

- Aplica también a `plans/<X>` → `plans/Archives/<X>` (misma promoción, misma trampa).
- **No aplica** cuando ninguna ruta publicada o archivada cita el archivo con prefijo `.opencode/`: el
  commit es un rename limpio, como `0c29d23`, que tocó una sola ruta y cero baseline.
- Las referencias relativas sin prefijo (p. ej. `../../context/…` en un prompt archivado) **no** las ve
  el validador: quedan obsoletas en silencio. No contarlas como curadas.
- Lo congelado no se re-escribe: si un documento byte-publicado necesita un cambio de contenido, la vía
  es re-publicación con título nuevo que conserve el stem, no editar el archivo.
- Lección hermana: `leccion-git-pathspec-untracked.md` (el pathspec que no toma *untracked*), misma
  familia: el instrumento reporta conformidad sobre un insumo que no está mirando.
