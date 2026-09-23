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


def test_ningun_archivo_fuera_de_la_puerta_importa_el_sdk_o_el_adapter(escaneo_arbol_real):
    scan = escaneo_arbol_real
    assert scan["status"] == "SIN-HALLAZGOS", scan["hallazgos"] + scan["hallazgos_carga_dinamica"]
    assert scan["conteos"]["coincidencias_de_import_fuera_de_la_puerta"] == 0
    assert scan["conteos"]["hallazgos_de_carga_dinamica"] == 0


def test_el_escaneo_publica_la_poblacion_que_lo_sostiene(escaneo_arbol_real):
    scan = escaneo_arbol_real
    b = scan["coverage_basis"]
    assert b["archivos_escaneados"] > 600, (
        f"poblacion sospechosamente chica: {b['archivos_escaneados']} .py escaneados")
    assert b["archivos_py_en_el_arbol"] >= b["archivos_escaneados"]
    assert b["nodos_de_import_vistos"] > 1000
    assert b["tokens_buscados"], "el escaneo no declaro que tokens busca"
    assert b["comando"] and b["medido_el"]
    assert b["limites"], "un escaneo sin limites declarados se lee como cobertura total (L-HF1)"


# --- S11: el denominador de AC6 tiene su propia prueba de poblacion ---------------------------
# Un `0 coincidencias` sobre una poblacion que nadie declaro no distingue «nadie importa el SDK» de
# «el escaneo contaba otra cosa» (L-R.3). S11 medido el 2026-09-22: `.venv-wsl/bin/activate_this.py`
# entraba en los .py escaneados porque `.venv-wsl` no estaba en la lista de exclusiones, y el
# numerador no se movia (0 imports). La cura no es un `except` ni un umbral mas abajo: es excluir el
# directorio y **publicar la exclusion con su conteo**, que es lo que estas dos pruebas afirman.

def test_un_directorio_de_venv_se_excluye_y_su_exclusion_se_publica_con_su_conteo(dc, tmp_path):
    raiz = tmp_path / "repo-venv"
    (raiz / ".venv-wsl" / "bin").mkdir(parents=True)
    (raiz / "modules").mkdir(parents=True)
    (raiz / ".venv-wsl" / "bin" / "activate_this.py").write_text(
        "import typesafe\n", encoding="utf-8")
    (raiz / "modules" / "limpio.py").write_text("import json\n", encoding="utf-8")
    puerta = raiz / "decision_client.py"
    puerta.write_text("import json\n", encoding="utf-8")
    scan = dc.escanear_aislamiento(raiz, puerta=puerta)
    b = scan["coverage_basis"]
    assert b["archivos_escaneados"] == 2, "el venv se col6 en el numerador de archivos leidos"
    assert b["excluidos_por_directorio"] == {".venv-wsl": 1}, (
        "la exclusion se callo: un denominador que no publica lo que saca no informa (L-R.3)")
    assert b["archivos_py_en_el_arbol"] == 3, "el arbol completo sigue contado, exclusion incluida"


def test_en_el_arbol_vigente_un_venv_presente_aparece_como_exclusion_publicada(dc,
                                                                               escaneo_arbol_real,
                                                                               raiz_repo):
    """Contra el arbol real: si el directorio existe tiene que estar del lado de las exclusiones
    publicadas, no del lado de la poblacion leida.

    La regla en si la prueba la de arriba con un arbol plantado; esta es la que se pone roja si alguien
    quita `.venv-wsl` de la lista y devuelve el residuo al denominador de S11.
    """
    presentes = [n for n in dc.ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION
                 if "venv" in n and (raiz_repo / n).is_dir()]
    if not presentes:
        pytest.skip("la maquina no tiene ningun directorio de venv: nada que publicar")
    excluidos = escaneo_arbol_real["coverage_basis"]["excluidos_por_directorio"]
    for nombre in presentes:
        assert excluidos.get(nombre), (
            f"{nombre} existe en el arbol y no esta publicado como exclusion: o se leyo su contenido "
            "como codigo propio, o el denominador se callo lo que sac6 (L-R.3)")


def test_sin_poblacion_no_hay_favorable(dc, tmp_path, raiz_repo):
    """Un arbol sin archivos no cierra en favorable: `SIN-POBLACION` es un estado de que no se miro
    nada, y el CLI lo sale distinto de `SIN-HALLAZGOS` (orden 2026-09-22 §4.A-a)."""
    vacio = tmp_path / "arbol-vacio"
    vacio.mkdir()
    scan = dc.escanear_aislamiento(vacio, puerta=vacio / "decision_client.py")
    assert scan["coverage_basis"]["archivos_escaneados"] == 0
    assert scan["status"] == "SIN-POBLACION", (
        "un 0 de poblacion no puede publicarse con el mismo status que un escaneo completo: se "
        "leeria como certificacion favorable sobre un arbol que no se miro")
    assert scan["coverage_basis"]["archivos_py_en_el_arbol"] == 0


def test_exclusiones_solapadas_no_inflan_el_denominador(dc, tmp_path):
    """Un archivo bajo DOS directorios excluidos es UN archivo: la atribucion por directorio puede
    repetirlo, pero el total del arbol se cuenta contra los excluidos unicos (L-VCF-11; la suma de
    `excluidos_por_directorio` nunca reprodujo el universo, y como comprobacion aritmetica mentia)."""
    raiz = tmp_path / "repo-solapado"
    (raiz / ".venv-wsl" / "lib" / "site-packages").mkdir(parents=True)
    (raiz / "modules").mkdir(parents=True)
    (raiz / ".venv-wsl" / "lib" / "site-packages" / "x.py").write_text(
        "import typesafe\n", encoding="utf-8")
    (raiz / "modules" / "limpio.py").write_text("import json\n", encoding="utf-8")
    puerta = raiz / "decision_client.py"
    puerta.write_text("import json\n", encoding="utf-8")
    scan = dc.escanear_aislamiento(raiz, puerta=puerta)
    b = scan["coverage_basis"]
    assert b["excluidos_por_directorio"] == {".venv-wsl": 1, "site-packages": 1}
    assert b["excluidos_archivos_unicos"] == 1, "el archivo solapado se conto dos veces como excluido"
    assert b["archivos_escaneados"] == 2
    assert b["archivos_py_en_el_arbol"] == 3, (
        f"el denominador se infl6 con la exclusion solapada: {b['archivos_py_en_el_arbol']} != "
        "2 escaneados + 1 archivo unico excluido")


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
    """R2.9: si un .py no se puede parsear, el escaneo lo dice; no suma un silencio al 0.

    Y desde la orden 2026-09-22 §4.A-a el status del escaneo tampoco cierra favorable con la lectura
    incompleta: `LECTURA-INCOMPLETA` es un estado propio, distinto de `SIN-HALLAZGOS`.
    """
    raiz = tmp_path / "repo"
    raiz.mkdir()
    (raiz / "roto.py").write_text("def x(\n", encoding="utf-8")
    puerta = raiz / "decision_client.py"
    puerta.write_text("import json\n", encoding="utf-8")
    scan = dc.escanear_aislamiento(raiz, puerta=puerta)
    assert scan["status"] == "LECTURA-INCOMPLETA", scan["status"]
    assert scan["conteos"]["archivos_no_parseables"] == 1
    assert scan["no_parseables"][0]["archivo"] == "roto.py"
    assert "sintaxis" in scan["no_parseables"][0]["motivo"]


def test_en_el_arbol_real_no_hay_archivos_no_parseables(escaneo_arbol_real):
    """Con la poblacion del repo: si algo no parsea, el escaneo dejaria de ser una prueba de AC6."""
    scan = escaneo_arbol_real
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
