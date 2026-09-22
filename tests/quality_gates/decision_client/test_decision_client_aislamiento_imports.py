"""AC6 - aislamiento de imports sobre el **arbol real**, con su conteo y su poblacion (L-D3, L-R.3).

Dos cosas y no una: que no haya coincidencias, y **sobre cuantos archivos** se midio. Un «0
coincidencias» sin denominador no distingue «nadie importa el SDK» de «el escaneo no leyo nada»
(L-R.3, y la variante lexica D5 del maestro). Por eso `test_sin_poblacion_no_hay_favorable` es la
otra mitad del criterio.

Un solo estado por test (R2.9): aqui se observa el `SIN-HALLAZGOS` del escaneo y sus tres caminos de
fallo (ausente / lector fallido / hallazgo), sobre el arbol vigente del repo.
"""

import ast
import pytest


def test_ningun_archivo_fuera_de_la_puerta_importa_el_sdk_o_el_adapter(dc, raiz_repo):
    scan = dc.escanear_aislamiento(raiz_repo)
    assert scan["status"] == "SIN-HALLAZGOS", scan["hallazgos"] + scan["hallazgos_carga_dinamica"]
    assert scan["conteos"]["coincidencias_de_import_fuera_de_la_puerta"] == 0
    assert scan["conteos"]["hallazgos_de_carga_dinamica"] == 0


def test_el_escaneo_publica_la_poblacion_que_lo_sostiene(dc, raiz_repo):
    scan = dc.escanear_aislamiento(raiz_repo)
    b = scan["coverage_basis"]
    assert b["archivos_escaneados"] > 600, (
        f"poblacion sospechosamente chica: {b['archivos_escaneados']} .py escaneados")
    assert b["archivos_py_en_el_arbol"] >= b["archivos_escaneados"]
    assert b["nodos_de_import_vistos"] > 1000
    assert b["tokens_buscados"], "el escaneo no declaro que tokens busca"
    assert b["comando"] and b["medido_el"]
    assert b["limites"], "un escaneo sin limites declarados se lee como cobertura total (L-HF1)"


def test_sin_poblacion_no_hay_favorable(dc, tmp_path, raiz_repo):
    """Un arbol sin archivos no produce `SIN-HALLAZGOS` creible: la poblacion tiene que existir."""
    vacio = tmp_path / "arbol-vacio"
    vacio.mkdir()
    scan = dc.escanear_aislamiento(vacio, puerta=vacio / "decision_client.py")
    assert scan["coverage_basis"]["archivos_escaneados"] == 0
    # Y aqui el status SI es SIN-HALLAZGOS (no hay nada que violar): lo que informa es el 0 de
    # poblacion, que esta publicado. La prueba deja la lectura explicita, no el silencio.
    assert scan["status"] == "SIN-HALLAZGOS"
    assert scan["coverage_basis"]["archivos_py_en_el_arbol"] == 0


def test_un_import_prohibido_plantado_fuera_de_la_puerta_es_hallazgo(dc, tmp_path):
    """El verde anterior no prueba que el guard funciona: se planta una violacion y se mide."""
    raiz = tmp_path / "repo"
    (raiz / "modules").mkdir(parents=True)
    (raiz / "scripts").mkdir(parents=True)
    (raiz / "modules" / "trampolin.py").write_text(
        "import typesafe\nfrom httpx2 import Client\n", encoding="utf-8")
    puerta = raiz / "scripts" / "decision_client.py"
    puerta.write_text("import json\n", encoding="utf-8")
    scan = dc.escanear_aislamiento(raiz, puerta=puerta)
    assert scan["status"] == "HALLAZGOS"
    c = scan["conteos"]
    assert c["coincidencias_de_import_fuera_de_la_puerta"] == 2
    assert {h["token"] for h in scan["hallazgos"]} == {"typesafe", "httpx2"}
    assert all(h["archivo"] == "modules/trampolin.py" for h in scan["hallazgos"])


def test_la_misma_carga_dentro_de_la_puerta_no_es_hallazgo(dc, tmp_path):
    """La puerta si puede importar al proveedor: es el unico sitio donde esa linea esta permitida."""
    raiz = tmp_path / "repo"
    scripts = raiz / "scripts"
    scripts.mkdir(parents=True)
    puerta = scripts / "decision_client.py"
    puerta.write_text("import typesafe\n", encoding="utf-8")
    scan = dc.escanear_aislamiento(raiz, puerta=puerta)
    assert scan["status"] == "SIN-HALLAZGOS", scan["hallazgos"]
    assert scan["conteos"]["coincidencias_de_import_total"] == 1
    assert scan["en_la_puerta"], "la excepcion de la puerta debe publicarse, no aplicarse a escondidas"


def test_un_proveedor_que_cuela_el_sdk_por_nombre_armado_es_hallazgo(dc, tmp_path):
    """La superficie de contrabando es el directorio de proveedores: ahi una carga no literal SI cuenta."""
    raiz = tmp_path / "repo"
    provs = raiz / "tests" / "falsos_proveedores"
    provs.mkdir(parents=True)
    (provs / "falso_tramposo.py").write_text(
        "import importlib\n\n"
        "PROVEEDOR = {'nombre': 'tramposo'}\n\n"
        "def evaluar(state, preguntas):\n"
        "    return importlib.import_module('types' + 'afe')\n", encoding="utf-8")
    puerta = raiz / "decision_client.py"
    puerta.write_text("import json\n", encoding="utf-8")
    scan = dc.escanear_aislamiento(raiz, puerta=puerta)
    assert scan["conteos"]["cargas_dinamicas_no_resueltas"] == 1
    assert scan["conteos"]["cargas_no_resueltas_en_directorios_de_proveedor"] == 1
    assert scan["status"] == "HALLAZGOS", scan["hallazgos_carga_dinamica"]


def test_un_archivo_que_no_parsea_no_se_cuenta_como_limpio(dc, tmp_path):
    """R2.9: si un .py no se puede parsear, el escaneo lo dice; no suma un silencio al 0."""
    raiz = tmp_path / "repo"
    raiz.mkdir()
    (raiz / "roto.py").write_text("def x(\n", encoding="utf-8")
    puerta = raiz / "decision_client.py"
    puerta.write_text("import json\n", encoding="utf-8")
    scan = dc.escanear_aislamiento(raiz, puerta=puerta)
    assert scan["conteos"]["archivos_no_parseables"] == 1
    assert scan["no_parseables"][0]["archivo"] == "roto.py"
    assert "sintaxis" in scan["no_parseables"][0]["motivo"]


def test_en_el_arbol_real_no_hay_archivos_no_parseables(dc, raiz_repo):
    """Con la poblacion del repo: si algo no parsea, el escaneo dejaria de ser una prueba de AC6."""
    scan = dc.escanear_aislamiento(raiz_repo)
    assert scan["no_parseables"] == [], scan["no_parseables"][:5]


def test_la_puerta_y_sus_proveedores_no_importan_nada_que_pueda_hacer_red(dc, script_ruta,
                                                                         proveedores_falsos):
    """Cero red verificado estaticamente, con denegatoria (no con whitelist que uno olvida ampliar).

    Lista negra: todo modulo desde el que se puede abrir una conexion o negociar TLS. Si manana la
    puerta necesita uno, este test se pone rojo y la decision de romper el cero red deja de ser
    implicita - que es el punto del contrato de ejecucion.
    """
    DENEGADOS = {"socket", "ssl", "select", "asyncio", "subprocess", "multiprocessing", "threading",
                 "http", "httpx", "httpcore", "httpx2", "urllib", "urllib3", "requests", "aiohttp",
                 "ftplib", "smtplib", "telnetlib", "smbclient", "tenacity", "typesafe", "jev"}
    rutas = [script_ruta] + sorted(proveedores_falsos.glob("*.py"))
    assert len(rutas) >= 3, "la poblacion de esta prueba se redujo a nada"
    usados = set()
    for path in rutas:
        arbol = ast.parse(path.read_text(encoding="utf-8"))
        modulos = set()
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                modulos |= {a.name.split(".")[0] for a in nodo.names}
            elif isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.level == 0:
                modulos.add(nodo.module.split(".")[0])
        usados |= modulos
        tocados = modulos & DENEGADOS
        assert not tocados, f"{path.name} importa {sorted(tocados)}: eso ya no es cero red"
    assert {"argparse", "ast"} <= usados or "importlib" in usados


# --- el guard de cero red, probado vivo ------------------------------------------------------
# Un «no hice llamadas» afirmado no es verificable (lo pide el contrato de ejecucion de este plan).
# Estas dos pruebas son las que convierten esa frase en una medicion: el guard del `conftest` tiene
# que explotar cuando alguien llama, y tiene que dejar pasar cuando la costura trabaja.

def test_el_guard_de_red_explota_si_alguien_intenta_llamar(excpcion_de_red):
    import socket
    RedProhibida = excpcion_de_red
    with pytest.raises(RedProhibida):
        socket.socket()
    with pytest.raises(RedProhibida):
        socket.create_connection(("api.example.invalid", 443), timeout=1)
    with pytest.raises(RedProhibida):
        socket.getaddrinfo("api.example.invalid", 443)


def test_la_costura_trabaja_bajo_el_guard_sin_dispararlo(dc, preguntas, entorno_falso,
                                                         proveedores_falsos):
    """`RESUELTO` bajo el guard armado: la unica prueba de que el verde no vino de la red."""
    import socket
    r = dc.evaluar("estado de prueba", preguntas, entorno_falso)
    assert r.provider_status == "RESUELTO"
    with pytest.raises(Exception) as exc:
        socket.socket()
    assert "RedProhibida" in type(exc.value).__name__
