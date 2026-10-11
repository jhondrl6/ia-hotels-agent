# Lección: `git commit` con pathspec no toma archivos *untracked*

**Fecha:** 2026-10-11 · **Sesión:** cura del emisor de fragmentos de credenciales (`config_checker`)
**Comandos involucrados:** `git commit -F <msg> -- <ruta>`, `git add`, `git write-tree`, `git ls-files`

---

## Qué pasó

Se intentaron dos commits separados por pathspec sobre rutas explícitas. El primero (`.gitignore`,
archivo ya versionado) landed. El segundo llevaba cuatro rutas, **dos de ellas nuevas**
(`config/secret_fragment_policy.yaml` y `tests/test_secrets_check_forma_fragmento.py`, nunca vistas
por Git). Ese commit **no landed**: `git commit -- <ruta>` toma el contenido del árbol de trabajo
solo para rutas que Git ya conoce; una ruta *untracked* no entra por ese camino, y el comando puede
terminar sin commitear nada.

El fallo pasó inadvertido dos veces:

1. La salida del commit se filtró con `grep -E "files changed|master "`, que excluye tanto el banner
   del hook como las líneas `error:`/`fatal:`. Resultado: **cero líneas de salida**, que se lee como
   «todo bien» cuando en realidad no hubo commit.
2. En la misma cadena se borró el archivo temporal del mensaje (`rm -f "$MA" "$MB"`), así que el
   mensaje escrito se perdió junto con el intento.

Se detectó al ir a verificar `git log` y contra-poner `HEAD^{tree}` contra el árbol materializado en
el pre-vuelo — es decir, por la verificación, no por la salida del comando.

## Regla

**Un commit con pathspec va precedido de `git add` de esas mismas rutas.** Y su verificación es el
árbol resultante, no la impresión del comando.

## Checklist

- [ ] Antes del commit: `git add -- <las rutas>` y confirmar con `git diff --cached --name-only -- <las rutas>`
      que cada una aparece. Las rutas nuevas (aunque las creaste tú con un editor) **no** están en el
      índice hasta ese `add`.
- [ ] Mostrar la salida del commit **cruda** (`tail`), sin filtrarla con patrones que solo coinciden
      con el caso verde. Si un comando no imprime nada, eso es un estado por sí mismo: investigar, no
      asumir.
- [ ] No borrar el archivo del mensaje (`-F`) ni ningún scratch del pre-vuelo hasta tener `git log -1`
      y el árbol confirmados.
- [ ] Verificar identidad: `git rev-parse HEAD^{tree}` debe casar con el árbol que se pre-voló. Si se
      materializó un índice temporal, comparar también que el hook evaluó ese mismo árbol
      (`verify_packs_in_committed_tree.py` imprime el rev que lee).
- [ ] Si el commit se bifurca en dos (por ejemplo una regla de `.gitignore` aparte de un cambio de
      código), repetir el pre-vuelo por árbol: los cinco cortes documentales terminan en espera de
      autorización y **ninguno** usa el `git commit` como evidencia.

## Por qué el pre-vuelo en árbol temporal es lo que salva el acto

La casa ya medía otro fallo de la misma familia: materializar el árbol de un commit con
`GIT_INDEX_FILE` + `git read-tree HEAD` + `git update-index --add -- <directorio>/` deja el árbol
**igual a HEAD**, porque `update-index` no desciende por directorios (avisa `Ignoring path …` y
sigue). Un verificador de árbol corrido sobre ese rev aprueba un árbol que no contiene lo del
commit: verde sin insumo. Las dos trampas comparten forma — *el instrumento no ve lo que debería*
y lo reporta como conformidad — y comparten cura: **exigir que el árbol cambiado se demuestre**
(`git diff --name-status HEAD <tree>` con el recuento de archivos que se espera), antes de confiar
en cualquier `EXIT=0`.

## Alcance y contrafactual

- Aplica a `git commit -- <pathspec>`, `git commit --amend --only -- <pathspec>` y a cualquier
  pre-vuelo que emule un commit con `write-tree`/`commit-tree`.
- **No aplica** a `git commit -a` (ese toma el árbol de trabajo de lo *tracked*, y deja fuera lo
  untracked por la misma razón) ni a `git add -A && git commit` sin pathspec.
- En este repo hay una razón extra para el pathspec explícito: con trabajo ajeno en el índice, un
  `git add -A` puede arrastrar evidencia que la política de cuarentena excluyó a propósito. Por eso
  se comitea por ruta, y por eso la ruta nueva hay que **stagearla** antes, no asumirla.
