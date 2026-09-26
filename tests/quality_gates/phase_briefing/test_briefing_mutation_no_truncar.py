"""AC23 (R2.8) — mutation check sobre el **simbolo real** que niega el truncamiento silencioso.

El guard es `build_phase_briefing.GUARD_NO_TRUNCAMIENTO_ACTIVO`, leido por `_declarar_recorte()`
en el momento de escribir el pack: apagarlo no cambia ninguna otra ruta del programa, pero deja
de escribir el bloque que nombra la seccion pedida y las rutas intentadas — el pack se achica **y
nadie lo dice**, que es justo lo que AC22 prohibe (L-PF6, L-PF10). Sin ese rojo, el verde de AC22
no diria que el guard existe (L-T4A.5).

Disciplina S13 (heredada del arnes de FASE-A y aplicada en FASE-C): el destino de la evidencia es
**argumento obligatorio** — ninguna constante de este archivo apunta al directorio de otra fase — y
la prueba de que no se piso pasado se hace **observando las operaciones de escritura** con el
observador compartido, **mas** contenido y metadatos del expediente protegido.

**El insumo se planta, no se lee del plan vivo (medido el 2026-09-25).** AC23 necesita un recorte
real para que apagar el guard se note. Cuando se escribio, el pack de FASE-RELEASE del plan CONTEXTO
traia `SECCION-NO-RESUELTA`; al cerrar esa fase sus secciones quedaron resueltas y el pack paso a
`COMPLETO`, asi que el arnes sobre el arbol vivo se quedo sin muestra y sus cuatro verde se
convirtieron en verde vacio — lo que esta prueba prohibe. `plantear()` fabrica el mismo estado por
construction (`§99` no existe en el `01-doc.md` plantado) y ya no caduca cuando el corpus crece.
"""

from __future__ import annotations

import importlib.util
import inspect
import re
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "build_phase_briefing.py"
SUPPORT_OBSERVADOR = ROOT / "tests" / "support_observador_escrituras.py"
# Solo lectura: se observa para probar que NADIE escribe aqui (S13). No es destino de escritura.
EVIDENCIA_SOLO_LECTURA = ROOT / "evidence" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20" / "FASE-A"
SIMBOLO_MUTADO = "GUARD_NO_TRUNCAMIENTO_ACTIVO"
MARCA = "[SECCION-NO-RESUELTA]"
SALIDAS_ESPERADAS = ("verde_baseline.json", "mutante_M-AC23-guard-no-truncamiento.json",
                     "resumen.txt")
LECTURA_CON_RECORTE = "01-doc.md §1 y §99 y el workflow canónico"
FASE_PLANTADA = "X"


def _observador():
    spec = importlib.util.spec_from_file_location("observador_escrituras", SUPPORT_OBSERVADOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cargar_script():
    spec = importlib.util.spec_from_file_location("bpb_para_evidencia", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def medir(bpb, mut: bool, caso: dict) -> dict:
    """Genera el pack del plan **plantado** con el guard activo o apagado, sobre un arbol temporal."""
    if mut:
        setattr(bpb, SIMBOLO_MUTADO, False)
    try:
        with tempfile.TemporaryDirectory(prefix="bpb_mut_") as tmp:
            destinos = Path(tmp) / "briefing"
            paquetes, _ = bpb.generar(caso["plan_dir"], destinos, caso["raiz"])
            pack = next((p for p in paquetes if p["fase"] == FASE_PLANTADA), None)
            cuerpo = ""
            if pack is not None and pack["estado"] != bpb.ESTADO_AUSENTE:
                archivo = destinos / f"FASE-{pack['fase']}.md"
                cuerpo = archivo.read_text(encoding="utf-8") if archivo.is_file() else ""
                emitido, bytes_pack = archivo.is_file(), (
                    archivo.stat().st_size if archivo.is_file() else 0)
            else:
                emitido, bytes_pack = False, 0
    finally:
        setattr(bpb, SIMBOLO_MUTADO, True)
    return {
        "mut": mut,
        "simbolo": f"build_phase_briefing.{SIMBOLO_MUTADO}",
        "guard_activo": bool(getattr(bpb, SIMBOLO_MUTADO)),
        "estado": pack["estado"] if pack else "FASE-AUSENTE-DE-LA-MUESTRA",
        "emitido": emitido,
        "bytes_pack": bytes_pack,
        # Anclaje exclusivo del generador: «rutas intentadas» y «seccion pedida» tambien
        # aparecen en los documentos que el pack copia, y hubieran dado un verde bajo mutacion.
        "declara_recorte": MARCA in cuerpo and "titulos disponibles en el documento" in cuerpo,
        "conserva_lo_resuelto": "contenido" in cuerpo or "Medición que justifica" in cuerpo,
        "lista_los_tres_estados": sorted(
            [bpb.ESTADO_COMPLETO, bpb.ESTADO_RECORTE, bpb.ESTADO_AUSENTE]),
    }


def correr_a_destino(destino: Path, caso: dict, bpb=None) -> dict:
    """Unicas salidas: las que el llamador nombra. Sin destino ni insumo por defecto (S13)."""
    if bpb is None:
        bpb = _cargar_script()
    verde = medir(bpb, mut=False, caso=caso)
    rojo = medir(bpb, mut=True, caso=caso)
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    obs = _observador()
    (destino / "verde_baseline.json").write_text(
        json.dumps(verde, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destino / "mutante_M-AC23-guard-no-truncamiento.json").write_text(
        json.dumps(rojo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destino / "resumen.txt").write_text("\n".join([
        "AC23 — mutation check del guard que niega el truncamiento silencioso (FASE-D)",
        f"simbolo mutado: build_phase_briefing.{SIMBOLO_MUTADO} "
        "(leido por _declarar_recorte al escribir el pack)",
        f"insumo: plan plantado con lectura {LECTURA_CON_RECORTE!r} (fase {FASE_PLANTADA})",
        f"alcance del observador de escrituras: {obs.ALCANCE}",
        f"destino declarado por el cierre: {destino.as_posix()}",
        f"VERDE  (guard activo): estado={verde['estado']} declara_el_recorte="
        f"{verde['declara_recorte']} bytes={verde['bytes_pack']}",
        f"ROJO   (guard apagado): estado={rojo['estado']} declara_el_recorte="
        f"{rojo['declara_recorte']} bytes={rojo['bytes_pack']}",
        "lectura: apagado el guard, el pack plantado conserva el estado SECCION-NO-RESUELTA",
        "  pero pierde el bloque que nombra la seccion pedida y las rutas intentadas — se achica",
        "  sin decirlo. Eso es lo que assertiona test_briefing_seccion_no_resuelta con el mismo",
        "  insumo, y por que el verde no es un verde por ausencia de oportunidad de recortar.",
        "",
    ]) + "\n", encoding="utf-8")
    return {"verde": verde, "rojo": rojo, "destino": destino.as_posix()}


def test_verde_con_el_guard_activo(bpb, plantear):
    v = medir(bpb, mut=False, caso=plantear(lectura=LECTURA_CON_RECORTE))
    assert v["estado"] == "SECCION-NO-RESUELTA", (
        "la muestra dejo de tener recorte: el mutation check quedaria verde vacio")
    assert v["declara_recorte"]
    assert v["guard_activo"] is True


def test_rojo_con_el_guard_apagado(bpb, plantear):
    r = medir(bpb, mut=True, caso=plantear(lectura=LECTURA_CON_RECORTE))
    assert r["declara_recorte"] is False, (
        f"apagado {SIMBOLO_MUTADO} el pack sigue declarando el recorte: el mutante no toca el "
        "guard real (L-T4A.5)")
    assert r["declara_recorte"] is False
    assert r["estado"] == "SECCION-NO-RESUELTA", (
        "el mutante cambi6 el estado, no la declaracion: apunta a otra rama")


def test_el_rojo_es_mas_corto_que_el_verde_y_no_lo_dice(bpb, plantear):
    caso = plantear(lectura=LECTURA_CON_RECORTE)
    v, r = medir(bpb, mut=False, caso=caso), medir(bpb, mut=True, caso=caso)
    assert r["bytes_pack"] < v["bytes_pack"], (
        f"el pack mutante no se achico ({r['bytes_pack']} vs {v['bytes_pack']}): el guard no "
        "goberna el tamano del pack")
    assert r["emitido"] is True, "el mutante no emite: el rojo vendria de otra parte"


def test_apagar_el_guard_no_altera_los_otros_dos_estados(bpb, plantear):
    """El mutante mira la declaracion del recorte, no la clasificacion de estados (L-V2.1)."""
    caso = plantear(lectura=LECTURA_CON_RECORTE)
    v, r = medir(bpb, mut=False, caso=caso), medir(bpb, mut=True, caso=caso)
    assert v["lista_los_tres_estados"] == r["lista_los_tres_estados"]
    assert v["estado"] == r["estado"]
    assert sorted([bpb.ESTADO_COMPLETO, bpb.ESTADO_RECORTE, bpb.ESTADO_AUSENTE]) == [
        "COMPLETO", "FUENTE-AUSENTE", "SECCION-NO-RESUELTA"]


def test_las_dos_salidas_van_a_destino_explicito_y_no_al_expediente_ajeno(plantear, tmp_path):
    obs = _observador()
    protegido_antes = obs.huellas(EVIDENCIA_SOLO_LECTURA)
    assert protegido_antes, f"no hay expediente que proteger en {EVIDENCIA_SOLO_LECTURA}"
    destino = tmp_path / "mutation"
    caso = plantear(lectura=LECTURA_CON_RECORTE)
    with obs.observador_de_escrituras() as registro:
        resultado = correr_a_destino(destino, caso)
    vistas = registro.dentro_de(destino)
    nombres_vistos = {Path(r).name for _, r, _ in vistas}
    assert set(SALIDAS_ESPERADAS) <= nombres_vistos, (
        f"el observador no vio las escrituras reales del arnes ({nombres_vistos}); sin esa ancla "
        "positiva, una ausencia en evidence/ no probaria nada")
    assert registro.dentro_de(EVIDENCIA_SOLO_LECTURA) == [], (
        f"el arnes escribio dentro del expediente de FASE-A: "
        f"{registro.dentro_de(EVIDENCIA_SOLO_LECTURA)}")
    assert obs.huellas(EVIDENCIA_SOLO_LECTURA) == protegido_antes, (
        "contenido o metadatos del expediente protegido se movieron")
    assert resultado["verde"]["declara_recorte"] and not resultado["rojo"]["declara_recorte"]


def test_el_destino_no_puede_apuntar_a_otra_fase_por_defecto():
    """S13: `destino` es obligatorio; el arnes no hereda una constante de evidencia."""
    firma = inspect.signature(correr_a_destino)
    assert firma.parameters["destino"].default is inspect.Parameter.empty, (
        "el arnes define un destino por defecto: eso es lo que re-escribio evidencia cerrada")
    fuente = Path(__file__).read_text(encoding="utf-8")
    constantes = re.findall(r"^([A-Z_]+)\s*=\s*(.+)$", fuente, re.M)
    destinos = [(n, v) for n, v in constantes if "evidence" in v and "SOLO_LECTURA" not in n]
    assert destinos == [], f"el arnes vuelve a fijar un destino de evidencia: {destinos}"
    assert "Solo lectura" in fuente and "No es destino de escritura" in fuente


def test_resumen_publica_el_alcance_del_observador_y_las_dos_salidas(plantear, tmp_path):
    obs = _observador()
    destino = tmp_path / "m"
    resumen = Path(correr_a_destino(destino, plantear(lectura=LECTURA_CON_RECORTE))["destino"]) / "resumen.txt"
    texto = resumen.read_text(encoding="utf-8")
    assert obs.ALCANCE in texto, "el alcance del observador debe publicarse con la evidencia"
    assert "VERDE" in texto and "ROJO" in texto
    assert SIMBOLO_MUTADO in texto, "el rojo debe nombrar el simbolo mutado"
