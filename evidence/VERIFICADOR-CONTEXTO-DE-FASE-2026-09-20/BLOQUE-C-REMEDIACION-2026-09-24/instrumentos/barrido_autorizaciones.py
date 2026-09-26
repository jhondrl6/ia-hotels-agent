"""Barrido de autorizaciones vencidas, reparado (M1 + M2 + M3).

Diferencias frente al antecedente de C, que no podia ver B1/B2:
  M2  todo comparador opera sobre texto NORMALIZADO (NFD sin caracteres de marca, minusculas),
      no sobre variantes con/sin tilde escritas a mano.
  M1  control positivo en la misma corrida y con el mismo instrumento, antes de informar ausencias.
  M3  dos etapas: (1) co-ocurrencia amplia; (2) el filtro estilo C (que exige adyacencia y la raiz
      "autorizad*") y su CEGUERA DECLARADA, mas la busqueda aparte de las copulas.
      Clasificacion a/b/c con conteos que suman exactamente el total de coincidencias.

Uso: barrido_autorizaciones.py [etiqueta]
"""
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-REMEDIACION-2026-09-24"
SNAPS = {
    ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/README.md": "B1-README.md",
    ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/06-checklist-implementacion.md":
        "B2-06-checklist-implementacion.md",
}
OPEN = chr(10214)   # ⟦
CLOSE = chr(10215)  # ⟧
VENTANA = 6
PATRON_ANOTACION = re.compile(
    r"vencid|rectificad|re-?lectur|precisi|actualiza|retirad|aclaraci|enmendad", re.I
)


def norm(s):
    d = unicodedata.normalize("NFD", s)
    return "".join(c for c in d if not unicodedata.combining(c)).lower()


def poblacion():
    rutas = sorted((ROOT / ".opencode" / "plans").glob("*/*.md"))
    rutas += sorted((ROOT / ".opencode" / "context").glob("ORDEN-*.md"))
    rutas += sorted(
        (ROOT / "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24").glob("*.md")
    )
    return [p for p in rutas if p.is_file()]


# --- etapa 1: co-ocurrencia de "bloque c" con CUALQUIER forma de no-autorizacion -------------
NO_AUT = [
    "sin autorizacion", "sin mandato", "sin autorización", "no esta autorizad", "no estan autorizad",
    "no esta claro que este autorizad", "no se autoriza", "sigue sin autorizaci", "pendiente de autorizaci",
    "no lo esta", "no lo estan", "no la esta", "no los esta", "no estan", "no esta",
    "requiere un mandato propio", "requiere su mandato", "con mandato propio", "autorizacion pendiente",
    "no ejecutada", "bloqueada por", "no se ejecuto", "falta el piloto", "sin ejecutar",
]
RX_NOAUT = re.compile("|".join(re.escape(norm(k)) for k in NO_AUT))
RX_BLOQUE_C = re.compile(norm("bloque C").replace(" ", r"\s+"))
RX_AFIRMA_EJEC = re.compile(r"bloque\s*c[^.]{0,120}?(se\s+autorizo|autorizado\s+y\s+ejecutado|se\s+ejecuto|ejecuto\s+el)")
# regla estrecha: la negacion recae PREDICADAMENTE sobre el bloque C (no es co-ocurrencia accidental)
RX_NIEGA_BLOQUE_C = re.compile(
    r"bloque\s*c[^.|]{0,60}?(no\s+lo\s+est|sin\s+autorizaci|no\s+est\s+autorizad|sigue\s+sin\s+autorizaci)"
)

# --- etapa 2: el filtro que C usaba (adyacencia + raiz "autorizad*") y su ceguera -------------
RX_ESTILO_C = re.compile(r"bloque\s*c.{0,40}?autorizad|autorizad.{0,40}?bloque\s*c", re.S)
RX_COPULAS = re.compile(r"no\s+lo\s+est[aá]n|no\s+lo\s+est[aá]|no\s+la\s+est[aá]|no\s+los\s+est[aá]n")


def lineas(f):
    with open(f, encoding="utf-8", errors="replace") as fh:
        return norm(fh.read()).splitlines()


def spans_anotacion(txt_norm):
    """[(linea_apertura, linea_cierre, interior)] de cada bloque ⟦…⟧ del archivo.

    Se calculan como SPANS y no como "pareja completa dentro de la ventana": una anotacion de
    varias lineas que ABRE en la linea falsa y CIERRA mas alla de +/-6 dejaba de detectarse, y el
    barrido devolvia un falso «vencida sin anotacion». Ese fue el defecto de la primera version de
    este instrumento, y va aqui declarado en vez de callado.
    """
    out = []
    for m in re.finditer(re.escape(OPEN) + r"(.*?)" + re.escape(CLOSE), txt_norm, re.S):
        a = txt_norm.count("\n", 0, m.start()) + 1
        b = txt_norm.count("\n", 0, m.end()) + 1
        out.append((a, b, m.group(1)))
    return out


def anotado(spans, i):
    for a, b, interior in spans:
        if not PATRON_ANOTACION.search(interior):
            continue
        if a <= i <= b:
            return True
        if abs(i - a) <= VENTANA or abs(i - b) <= VENTANA:
            return True
    return False


def main():
    etiqueta = sys.argv[1] if len(sys.argv) > 1 else "PASADA"
    rutas = poblacion()
    print(f"=== {etiqueta} ===")
    print(f"poblacion: {len(rutas)} archivos .md "
          f"(.opencode/plans/*/*.md + .opencode/context/ORDEN-*.md + expediente BLOQUE-C-ENMIENDAS)")

    print()
    print("=== CONTROL POSITIVO (M1) ===")
    readme = (ROOT / ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/README.md").read_text(encoding="utf-8")
    probes = [
        ("SABE-PRESENTE", "el bloque C y el piloto FASE-C no lo están", readme),
        ("SABE-PRESENTE", "Estado de B: consultar", readme),
        ("SABE-AUSENTE", "cadena_que_no_existe_en_este_archivo_zzz", readme),
    ]
    for tipo, sonda, cuerpo in probes:
        hallado = norm(sonda) in norm(cuerpo)
        esperado = tipo == "SABE-PRESENTE"
        ok = "OK" if hallado == esperado else "FALLO DEL INSTRUMENTO"
        print(f"  [{ok}] {tipo} {sonda!r} -> {hallado}")
        if ok != "OK":
            raise SystemExit("control positivo roto: el barrido no es fiable")

    hits = []
    SPANS = {}
    pre = etiqueta.startswith("PRE")
    for f in rutas:
        rel = f.relative_to(ROOT).as_posix()
        # en la pasada PRE se leen las copias congeladas en antes/: es el unico modo de medir el
        # arbol previo sin stash ni checkout sobre trabajo ajeno (prohibido por el mandato).
        lectura = (EXP / "antes" / SNAPS[rel]) if (pre and rel in SNAPS) else f
        lines = lineas(lectura)
        SPANS[rel] = spans_anotacion("\n".join(lines))
        for i, ln in enumerate(lines):
            if RX_BLOQUE_C.search(ln) and RX_NOAUT.search(ln):
                hits.append((rel, i + 1, ln, lines))
    print(f"  pasada PRE sobre copias de antes/: {pre} ({len([r for r in SNAPS])} rutas sustituidas)")
    TODOS = [(r, sp) for r, sps in SPANS.items() for sp in sps]
    print()
    print(f"=== ETAPA 1 (co-ocurrencia normalizada): {len(hits)} coincidencias ===")
    print()
    print("=== CONTROL POSITIVO de la deteccion de anotacion ===")
    _06 = ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/06-checklist-implementacion.md"
    _s = SPANS.get(_06, [])
    _pares = [sp for sp in _s if PATRON_ANOTACION.search(sp[2])]
    print(f"  spans ⟦…⟧ en 06-checklist: {len(_s)} ; con patron de rectificacion: {len(_pares)}")
    _e5 = [sp for sp in _s if "restriccion de e5" in sp[2]]
    print(f"  span de E5 (el precedente correcto del arbol) detectado: {bool(_e5)} "
          f"(lineas {_e5[0][0] if _e5 else '-'}-{_e5[0][1] if _e5 else '-'})")
    _larga = [(r, sp) for r, sp in TODOS if sp[1] > sp[0] + VENTANA]
    print(f"  spans de MAS DE {VENTANA} lineas (los que la ventana a secas no cerraba): {len(_larga)}")
    for r, sp in _larga:
        print(f"    {r}:{sp[0]}-{sp[1]}  «{sp[2][:40]}…»")

    print()
    print("=== ETAPA 2: filtro estilo C (adyacencia + raiz 'autorizad*') y su ceguera ===")
    ve = [(r, n, l, ls) for (r, n, l, ls) in hits if RX_ESTILO_C.search(l)]
    ciegas = [h for h in hits if h not in ve]
    print(f"  casadas por el filtro C : {len(ve)}")
    print(f"  NO casadas (ceguera)    : {len(ciegas)}")
    print("  formas que el filtro C no puede casar (cobertura declarada):")
    print("    - copulas sin la raiz 'autorizad*': «no lo esta», «no lo estan», «no la esta»")
    print("    - negaciones con «sigue sin» / «pendiente» / «requiere mandato» a mas de 40 caracteres")
    print("    - cualquier forma en la que la no-autorizacion este en una linea distinta")
    cop = [(r, n, l) for (r, n, l, ls) in hits if RX_COPULAS.search(l)]
    print(f"  busqueda aparte de las copulas: {len(cop)} coincidencias")
    for r, n, l in cop:
        print(f"    {r}:{n}  {l.strip()[:130]}")
    for r, n, l, ls in ciegas:
        print(f"    [CIEGA] {r}:{n}  {l.strip()[:130]}")

    print()
    print("=== CLASIFICACION (regla mecanica, mutuamente excluyente) ===")
    print("  (b) vencida-con-anotacion : hay un bloque ⟦…⟧ con el patron de rectificacion que cubre la")
    print("                              linea (span que la contiene, o apertura/cierre a +/-%d lineas)" % VENTANA)
    print("  (a) vigente               : no (b), y la ventana ya AFIRMA que el bloque C se autorizo/ejecuto")
    print("  (c) vencida-sin-anotacion : ni (b) ni (a)")
    print("  (b) se evalua PRIMERO: una linea rectificada in situ es 'vencida con anotacion', y esa es la")
    print("      categoria que importa para saber si hace falta intervenir.")
    b = [h for h in hits if anotado(SPANS[h[0]], h[1])]
    a = [h for h in hits if h not in b
         and RX_AFIRMA_EJEC.search("\n".join(h[3][max(0, h[1] - 1 - VENTANA):h[1] + VENTANA]))]
    c = [h for h in hits if h not in a and h not in b]
    for cls, nombre in ((a, "a vigente"), (b, "b vencida-con-anotacion"), (c, "c vencida-sin-anotacion")):
        print(f"  {nombre}: {len(cls)}")
    total = len(a) + len(b) + len(c)
    print(f"  SUMA {len(a)} + {len(b)} + {len(c)} = {total} | total coincidencias etapa 1 = {len(hits)} | "
          f"{'CIERRA' if total == len(hits) else 'NO CIERRA'}")
    c1 = [h for h in c if RX_NIEGA_BLOQUE_C.search(h[2])]
    c0 = [h for h in c if h not in c1]
    b1 = [h for h in b if RX_NIEGA_BLOQUE_C.search(h[2])]
    print()
    print("  DESGLOSE DE PRECISION (limite declarado del instrumento):")
    print("    la etapa 1 es co-ocurrencia, no analisis de dependencia: una linea puede mencionar")
    print("    «bloque C» y una negacion que no le pertenece. Se subdivide (c) y (b) exigiendo que la")
    print("    negacion recaiga predicadamente sobre «bloque C» (regla estrecha, <=60 caracteres).")
    print(f"    c-1 negada predicadamente del bloque C (las que el mandato pide cazar): {len(c1)}")
    print(f"    c-0 co-ocurrencia accidental, no afirma nada sobre el bloque C        : {len(c0)}")
    print(f"    suma del desglose (c): {len(c1)} + {len(c0)} = {len(c1)+len(c0)} | clase (c) = {len(c)}")
    print(f"    b-1 negada predicadamente del bloque C, ya anotada                   : {len(b1)}")
    print()
    print("--- detalle c-1 (vencida SIN anotacion, negacion predicada) ---")
    for r, n, l, ls in c1:
        print(f"  {r}:{n}  {l.strip()[:150]}")
    print("--- detalle c-0 (fuera de la mira por analisis de predicacion) ---")
    for r, n, l, ls in c0:
        print(f"  {r}:{n}  {l.strip()[:150]}")
    print("--- detalle (b) ---")
    for r, n, l, ls in b:
        print(f"  {r}:{n}  {l.strip()[:150]}")
    print("--- detalle (a) ---")
    for r, n, l, ls in a:
        print(f"  {r}:{n}  {l.strip()[:150]}")


if __name__ == "__main__":
    main()
