"""AC8 - contract test de **forma**: que una subida del SDK rompa ESTE test, no una fase ajena.

Regla de la fase (L-V2.3): se afirma la **forma**, nunca los literales del proveedor ni de su
version. El nombre del modelo que sale del `evaluar()` es el que **reporta** el proveedor falso, no
una cadena pineada en el assert, y la prueba comprueba por separado que `PIN_MODELO_DECLARADO` esta
declarado, fechado y **fuera de toda decision del codigo** - que es justo lo que hace que la costura
siga siendo neutra.

Estado 3 de 3 (R2.9): aqui solo se observa `RESUELTO`; el fixture apunta a un proveedor falso que
cumple la forma, y `sin_red` (autouse) garantiza que «resuelto» no puede haber salido de una llamada.
"""

import ast
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_evaluar_devuelve_una_respuesta_tipada_por_pregunta(dc, preguntas, entorno_falso):
    r = dc.evaluar("estado de prueba", preguntas, entorno_falso)
    assert r.provider_status == "RESUELTO"
    assert [a.pregunta_id for a in r.respuestas] == [p.id for p in preguntas]
    tipos = [a.tipo for a in r.respuestas]
    assert tipos == ["choice", "score", "noul"]
    assert isinstance(r.respuestas[0], dc.RespuestaEleccion)
    assert isinstance(r.respuestas[1], dc.RespuestaNivel)
    assert isinstance(r.respuestas[2], dc.RespuestaNoul)


def test_la_forma_de_choice_incluye_probabilidades_sobre_todas_las_opciones(dc, preguntas,
                                                                           entorno_falso):
    r = dc.evaluar("estado", preguntas, entorno_falso)
    eleccion = r.por_pregunta("c1")
    assert set(eleccion.probabilidades) == set(preguntas[0].opciones)
    assert eleccion.eleccion in preguntas[0].opciones
    assert abs(sum(eleccion.probabilidades.values()) - 1.0) <= dc.TOLERANCIA_SUMA_PROBABILIDADES
    assert 0.0 <= eleccion.confidence <= 1.0


def test_la_forma_de_score_devuelve_el_nivel_con_su_leyenda(dc, preguntas, entorno_falso):
    r = dc.evaluar("estado", preguntas, entorno_falso)
    nivel = r.por_pregunta("s1")
    assert 0 <= nivel.nivel < len(preguntas[1].leyenda)
    assert nivel.leyenda == preguntas[1].leyenda[nivel.nivel]
    assert 0.0 <= nivel.confidence <= 1.0


def test_la_forma_de_noul_no_inventa_confidence(dc, preguntas, entorno_falso):
    """`noul` trae probabilidad de si y confidence **None con su motivo**, no 0.0 (L-PF10)."""
    r = dc.evaluar("estado", preguntas, entorno_falso)
    noul = r.por_pregunta("n1")
    assert 0.0 <= noul.probabilidad_si <= 1.0
    assert noul.confidence is None
    d = noul.to_dict()
    assert d["confidence_motivo"] == "la primitiva noul no expone confidence"
    assert d["confidence"] is None


def test_el_modelo_reportado_sobrevive_a_la_costura_sin_quedar_pineado(dc, preguntas,
                                                                       entorno_falso,
                                                                       proveedores_falsos):
    """La contract test afirma que el modelo **viene del proveedor y sobrevive**, no que vale X.

    La comparacion es contra lo que el propio modulo falso declara (leyendolo de el, no escrito
    aqui): asi el test sigue siendo de forma si manana el proveedor cambia de nombre de modelo, y
    no acopla el repo a un literal del proveedor real (maestro §2, L-V2.3).
    """
    r = dc.evaluar("estado", preguntas, entorno_falso)
    declaracion = dc.resolver_proveedor(entorno_falso)["declara"]
    assert isinstance(r.modelo, str) and r.modelo.strip()
    assert r.modelo == declaracion["modelo"]
    assert r.proveedor == declaracion["nombre"]
    # Y ningun token del proveedor real aparece en un literal de ESTE archivo. La lista de tokens se
    # lee del modulo (no se escribe aqui): si la escribiera a mano, el test se refutaria a si mismo
    # por contener las propias cadenas que busca, que es la variante de D5 del maestro.
    arbol = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    literales = [n.value for n in ast.walk(arbol)
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    tokens = [t2.lower() for t2 in list(dc.NOMBRES_PROHIBIDOS) + list(dc.ALIAS_ADAPTER)]
    encontrados = sorted({lit for lit in literales for tok in set(tokens)
                          if len(tok) > 4 and tok in lit.lower()})
    assert not encontrados, f"contract test con literales del proveedor real: {encontrados}"


def test_el_pin_del_modelo_esta_declarado_y_no_decide_nada(dc):
    """AC8 pide «version de modelo pineada y declarada»; la neutralidad pide que nadie la compare."""
    pin = dc.PIN_MODELO_DECLARADO
    assert pin["modelo"] and pin["fuente"] and pin["verificado_desde_este_repo"] is False
    assert pin["usado_por_el_codigo"] is False
    arbol = ast.parse(dc.__file__ and Path(dc.__file__).read_text(encoding="utf-8"))
    usos = [n.lineno for n in ast.walk(arbol)
            if isinstance(n, ast.Name) and n.id == "PIN_MODELO_DECLARADO"]
    assert len(usos) == 1, f"el pin se usa en {len(usos)} sitios y la puerta dejo de ser neutra"
    assert dc.TECHO_CONTEXTO_DECLARADO["comparado_por_el_codigo"] is False


def test_alterar_la_forma_del_proveedor_falso_rompe_este_mismo_test(script_ruta, tmp_path,
                                                                    raiz_repo):
    """El rojo de AC8, probado **contra este archivo** (R2.8 y L-V2.1).

    Copia el directorio de proveedores falsos, le quita `confidence` a una respuesta `choice`, y
    vuelve a correr ESTE contract test contra la copia alterada: tiene que ponerse rojo. Correr el
    mismo test (no uno que simula) es lo que prueba que la ruptura la detecta la forma y no una
    asercion escrita a mano en otro sitio.
    """
    import shutil
    falsos = raiz_repo / "tests" / "quality_gates" / "decision_client" / "falsos_proveedores"
    copia = tmp_path / "falsos_proveedores"
    shutil.copytree(falsos, copia)
    victim = copia / "falso_forma.py"
    texto = victim.read_text(encoding="utf-8")
    blanco = ', "confidence": 0.91'
    assert blanco in texto
    alterado = texto.replace(blanco, "", 1)
    assert '"confidence"' not in alterado.split("def evaluar")[1].split("elif")[0]
    victim.write_text(alterado, encoding="utf-8")

    entorno = {"IAH_DECISION_PROVIDER": "falso-forma", "IAH_DECISION_PROVIDERS_DIR": str(copia)}
    r = subprocess.run([sys.executable, "-m", "pytest", __file__, "-k",
                        "test_evaluar_devuelve_una_respuesta_tipada_por_pregunta", "-q", "--no-header",
                        "--tb=long", "-p", "no:cacheprovider"],
                       capture_output=True, text=True, cwd=str(raiz_repo), env={
                           **os.environ, "PYTHONPATH": str(raiz_repo), **entorno})
    salida = r.stdout + r.stderr
    assert r.returncode != 0, "alterar la forma NO rompio el contract test (falso verde, L-VUP-5)"
    assert "1 failed" in salida, salida[-2000:]
    assert "RespuestaIlegible" in salida, salida[-2000:]
    # Que la cayo **esa** verificacion y no otra se comprueba en el proceso padre (la anchura del
    # terminal del hijo trunca los motivos): sin esto el rojo no nombraria al guard mutado (L-V2.1).
    mod_spec = importlib.util.spec_from_file_location("dc_rojo", script_ruta)
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    alterado = mod.resolver_proveedor(entorno)
    with pytest.raises(mod.RespuestaIlegible) as exc:
        mod.evaluar("estado", [mod.Pregunta("c1", "choice", "?",
                                           opciones=("pertinente", "no-pertinente", "insuficiente")),
                               mod.Pregunta("s1", "score", "?",
                                            leyenda=("bajo", "medio", "alto", "critico")),
                               mod.Pregunta("n1", "noul", "?")],
             entorno)
    # L-V2.1 exige que el rojo NOMBRE a los guards que detectan la mutacion — `campos-conocidos`
    # es el contrato de campos (confidence declarada) y `forma-choice` la forma de la choice con
    # su confidence — pero NO fija la particion: la doctrina del propio cierre (criterio d del
    # instrumento, «sin particion fijada») permite que un guard futuro detecte tambien esta
    # malformacion y se sume a los motivos sin romper la atribucion de causa (medido en sesion 4:
    # con un guard extra legitimo, el pin de igualdad producia un falso rojo y el superset seguia
    # sosteniendo la causa).
    nombres = {mod._nombre_de_la_verificacion(m) for m in exc.value.motivos}
    assert {"campos-conocidos", "forma-choice"} <= nombres, nombres
    assert "confidence" in " ".join(exc.value.motivos)
    del alterado
