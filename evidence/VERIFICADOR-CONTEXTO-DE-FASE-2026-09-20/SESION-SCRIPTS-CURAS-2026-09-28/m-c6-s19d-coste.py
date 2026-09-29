"""C6 crudo: el coste de §S19(d) medido hoy y si la cura C2 la alcanza.

(d) es sellar `generado_por_sha` en el pack como procedencia **no gobernante**. La fila la tasó el
2026-09-27 en «+1 linea por pack y un quinto patron en `NORMALIZAR`». Aqui se re-mide contra el
escritor y el verificador vigentes, con revisiones que de verdad mueven el sha del escritor, para
decidir la salida de C6 con su base.
"""
import hashlib
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
S = pathlib.Path(__file__)
ESCRITOR = "scripts/build_phase_briefing.py"
VERIFICADOR = "scripts/verify_packs_in_committed_tree.py"
BRIEFING = (ROOT / ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing")
# Revisiones que tocaron el escritor: las tres dan sha distintos, y esa es la premisa del quinto
# patron. Medirlas sobre tres commits que NO lo tocaron daba un falso «no se mueve» (1 distinto).
REVISIONES_ESCRITOR = ["ae21d09", "941530e", "a020306", "84c1aca"]


def git_show(rev: str, ruta: str) -> bytes:
    proc = subprocess.run(["git", "show", f"{rev}:{ruta}"], capture_output=True, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stderr[:200]
    return proc.stdout


def main():
    linea = []
    verif = (ROOT / VERIFICADOR).read_text(encoding="utf-8")
    bloque = re.search(r"NORMALIZAR = \((.*?)\n\)", verif, re.S)
    patrones = [l.strip() for l in bloque.group(1).splitlines() if l.strip()] if bloque else []
    linea += ["=== 1. patrones de NORMALIZAR del verificador versionado, hoy ===",
              f"archivo: {VERIFICADOR}",
              f"patrones={len(patrones)}"]
    for i, p in enumerate(patrones, 1):
        linea.append(f"  [{i}] {p}")
    linea += ["ningun patron cubre un futuro `generado_por_sha`: anadirlo al pack sin anadir patron "
              "es el rojo del verificador del arbol commiteado", ""]

    packs = sorted(BRIEFING.glob("FASE-*.md"))
    linea += ["=== 2. que publica hoy el escritor sobre su propia identidad ===",
              "-- la clave se lee dentro del bloque BRIEFING-META, no por substring del pack: la "
              "prosa de §S19 que los packs copian de `dependencias-fases.md` menciona "
              "`generado_por_sha` como texto y eso no es publicarla (primer barrido dio el falso SI) --"]
    meta_re = re.compile(r"<!-- BEGIN BRIEFING-META\n(.*?)\nEND BRIEFING-META -->", re.S)
    for pack in packs:
        bruto = pack.read_text(encoding="utf-8")
        m = meta_re.search(bruto)
        meta = json.loads(m.group(1)) if m else {}
        linea.append(f"  {pack.name}: generado_por={meta.get('generado_por')} "
                     f"generado_por_sha={'SI' if 'generado_por_sha' in meta else 'NO'} "
                     f"clave_en_prosa_ajena={'SI' if 'generado_por_sha' in bruto else 'NO'}")
    fuente_escritor = (ROOT / ESCRITOR).read_text(encoding="utf-8")
    linea += [f"ocurrencias_de_generado_por_sha_en_el_escritor="
              f"{fuente_escritor.count('generado_por_sha')}", ""]

    linea += ["=== 3. el valor sellado se mueve entre commits (premisa del quinto patron) ===",
              f"comando: git show <rev>:{ESCRITOR} | sha256sum"]
    digests = {}
    for rev in REVISIONES_ESCRITOR:
        digests[rev] = hashlib.sha256(git_show(rev, ESCRITOR)).hexdigest()[:16]
        linea.append(f"  {rev}: {digests[rev]}")
    disco = hashlib.sha256((ROOT / ESCRITOR).read_bytes()).hexdigest()[:16]
    linea.append(f"  arbol de trabajo (con la cura C2): {disco}")
    todos = set(digests.values()) | {disco}
    linea += [f"distintos={len(todos)} sobre {len(REVISIONES_ESCRITOR) + 1} mediciones",
              "el sha del escritor no es constante entre commits ni entre commit y arbol: publicado "
              "en el pack, el `--check` del arbol commiteado tendria que normalizarlo (quinto patron) "
              "o daria DIVERGE entre revisiones correctas, que es el defecto de instrumento ya "
              "documentado en §S20.", ""]

    linea += ["=== 4. si C2 alcanza a (d) ===",
              "C2 goberna la proyeccion de BYTES del workflow canonico contra disco "
              "(funcion `proyecciones_de_lectura_aparte`).",
              f"`generado_por_sha` en el escritor tras C2={fuente_escritor.count('generado_por_sha')} "
              "(C2 no toca la identidad del generador)",
              "la fila afirma ademas que la cura (b) no necesita (d) para atribuir el rojo, y C2 es "
              "otra puerta: (d) sigue siendo una superficie distinta.", ""]

    linea += ["=== 5. superficie que exige (d), contra la poblacion autorizada de esta orden ===",
              "la linea nueva vive en el meta de `build_phase_briefing.py` (autorizado), pero su "
              "contrapartida obligatoria vive en `NORMALIZAR` de "
              f"{VERIFICADOR} (NO autorizado: la orden nombra cinco guiones y sus tests, y este no "
              "es uno de ellos)",
              f"coste medido en packs del plan: {len(packs)} lineas nuevas (+1 por pack) y 1 patron "
              "nuevo",
              "salida elegida: (c) requiere otra superficie -> queda abierta con justificacion "
              "escrita en la fila"]

    destino = S.parent / "21-c6-s19d-coste-medido.txt"
    destino.write_text("\n".join(linea) + "\n", encoding="utf-8", newline="\n")
    print("# crudo en", destino.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
