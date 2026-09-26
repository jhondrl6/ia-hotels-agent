import importlib.util
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_document_integration.py"
REV_DEFECTO = "da382b1"
PRE_DETECTOR = (ROOT / "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
                / "BLOQUE-B-REMEDIACION-2026-09-23/CORRECCION-2026-09-24/PRE_detector.py.snapshot")
VERIFICADORES = [
    "validate_cross_refs", "validate_changelog_format", "validate_version_headers",
    "validate_python_path_consistency", "validate_agents_cross_ref_table",
    "validate_domain_primer_version", "validate_readme_counts", "validate_line_endings",
]
GOBERNADOS = ["CONTRIBUTING", "EXECUTOR", "DOMAIN_PRIMER", "AGENTS_MD", "TEMPLATE", "CHANGELOG"]
ESTADOS = {"limpio": "", "modificado": " M doc.md\n", "stageado": "M  doc.md\n",
           "stageado_y_modificado": "MM doc.md\n", "nuevo": "?? doc.md\n"}


def _cargar(nombre, ruta=SCRIPT):
    spec = importlib.util.spec_from_loader(nombre, loader=None, origin=str(ruta))
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = str(ruta)
    sys.modules[nombre] = mod
    exec(compile(ruta.read_bytes(), str(ruta), "exec"), mod.__dict__)
    return mod


def _fuente_versionada(tmp_path, rev, rel):
    proc = subprocess.run(["git", "show", f"{rev}:{rel}"], capture_output=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stderr
    destino = tmp_path / Path(rel).name
    destino.write_bytes(proc.stdout)
    return destino


def _cuenta_por_inyeccion(mod, fallan):
    contador = {}
    for nombre in VERIFICADORES:
        def envuelto(nombre=nombre):
            contador[nombre] = contador.get(nombre, 0) + 1
            return mod.ValidationResult(check=nombre, passed=nombre not in fallan,
                                        issues=[f"inyectado: {nombre}"] if nombre in fallan else [])
        setattr(mod, nombre, envuelto)
    return contador


def _un_solo_verificador_vivo(mod, activo, fn):
    for nombre in VERIFICADORES:
        setattr(mod, nombre, fn if nombre == activo else
                lambda nombre=nombre: mod.ValidationResult(check=nombre, passed=True))


def test_cada_verificador_se_calcula_una_sola_vez_por_ejecucion(capsys):
    mod = _cargar("vdi_una_vez")
    contador = _cuenta_por_inyeccion(mod, set(VERIFICADORES))
    assert mod.run_all() is False
    assert contador == {n: 1 for n in VERIFICADORES}
    assert "RESULT: 8 issue(s) found" in capsys.readouterr().out


def test_control_negativo_el_instrumento_versionado_re_llamaba_y_el_de_hoy_no(tmp_path, capsys):
    pre = _cargar("vdi_versionado", _fuente_versionada(tmp_path, REV_DEFECTO,
                                                     "scripts/validate_document_integration.py"))
    cuenta_pre = _cuenta_por_inyeccion(pre, {"validate_line_endings"})
    assert pre.run_all() is False
    assert cuenta_pre == {n: 3 if n == "validate_line_endings" else 2 for n in VERIFICADORES}
    assert sum(cuenta_pre.values()) == 17
    assert "RESULT: 1 issue(s) found" in capsys.readouterr().out
    post = _cargar("vdi_actual")
    cuenta_post = _cuenta_por_inyeccion(post, {"validate_line_endings"})
    assert post.run_all() is False
    assert cuenta_post == {n: 1 for n in VERIFICADORES}
    assert sum(cuenta_pre.values()) - sum(cuenta_post.values()) == 9
    assert "RESULT: 1 issue(s) found" in capsys.readouterr().out


def test_el_conteo_impreso_sale_del_mismo_calculo_que_el_diagnostico_impreso(capsys):
    mod = _cargar("vdi_diagnostico")
    llamadas = []

    def inestable():
        llamadas.append(1)
        return mod.ValidationResult(check="Inestable", passed=False,
                                    issues=[f"issue-{i}" for i in range(len(llamadas) * 2)])

    _un_solo_verificador_vivo(mod, "validate_cross_refs", inestable)
    assert mod.run_all() is False
    salida = capsys.readouterr().out
    assert len(llamadas) == 1
    assert "RESULT: 2 issue(s) found" in salida
    assert "issue-0" in salida and "issue-1" in salida and "issue-2" not in salida
    assert "RESULT: 4 issue(s)" not in salida and "RESULT: 6 issue(s)" not in salida


def test_una_ejecucion_nueva_con_entradas_cambiadas_no_reutiliza_el_resultado(tmp_path, capsys):
    mod = _cargar("vdi_frescura")
    executor = tmp_path / "executor.md"
    contributing = tmp_path / "contributing.md"
    executor.write_bytes(b"# Valid\n")
    contributing.write_bytes(b"# Valid\n")
    mod.EXECUTOR, mod.CONTRIBUTING = executor, contributing
    _un_solo_verificador_vivo(mod, "validate_cross_refs", mod.validate_cross_refs)
    assert mod.run_all() is True
    capsys.readouterr()
    executor.write_bytes(b"# Invalid reference: section \xc2\xa7L12-15\n")
    assert mod.run_all() is False
    salida = capsys.readouterr().out
    assert "Executor has 1 hardcoded line refs" in salida
    assert "RESULT: 1 issue(s) found" in salida


def _git_fixture(monkeypatch, mod, repo, estado, indice="lf"):
    llamadas = []

    def run(argv, **kwargs):
        assert Path(kwargs["cwd"]) == repo
        llamadas.append(argv)
        if argv[:3] == ["git", "ls-files", "--eol"]:
            out = "" if estado == "nuevo" else f"i/{indice} w/lf attr/\tdoc.md\n"
        else:
            assert argv[:3] == ["git", "status", "--porcelain"]
            out = ESTADOS[estado]
        return SimpleNamespace(returncode=0, stdout=out, stderr="")

    monkeypatch.setattr(mod, "subprocess", SimpleNamespace(run=run))
    return llamadas


def _gobernar(mod, repo, doc):
    mod.PROJECT_ROOT = repo
    for nombre in GOBERNADOS:
        setattr(mod, nombre, doc)


def test_el_detector_ve_crlf_en_bytes_y_read_text_no_lo_ve(tmp_path):
    mod = _cargar("vdi_bytes")
    doc = tmp_path / "doc.md"
    doc.write_bytes(b"a\r\nb\r\n")
    assert mod.eol_en_disco(doc) == "CRLF"
    assert "\r\n" not in doc.read_text(encoding="utf-8")
    assert mod.eol_en_disco(tmp_path / "ausente") == "ERROR-LECTURA"


@pytest.mark.parametrize("estado", ESTADOS)
@pytest.mark.parametrize("datos,disco,ok", [(b"a\n", "LF", True), (b"", "VACIO", True),
                                           (b"a\r\n", "CRLF", False),
                                           (b"a\r\nb\n", "MIXTO", False),
                                           (b"a\r", "CR", False)])
def test_bytes_reales_en_todos_los_estados_git(tmp_path, monkeypatch, estado, datos, disco, ok):
    mod = _cargar("vdi_matriz")
    doc = tmp_path / "doc.md"
    doc.write_bytes(datos)
    llamadas = _git_fixture(monkeypatch, mod, tmp_path, estado)
    lecturas = []
    leer = Path.read_bytes

    def observar(path):
        lecturas.append(path)
        return leer(path)

    monkeypatch.setattr(Path, "read_bytes", observar)
    resultado = mod.eol_veredicto(doc, tmp_path)
    assert lecturas == [doc], "El veredicto debe leer los bytes una vez incluso si Git dice LIMPIO"
    assert resultado["disco"] == disco
    assert resultado["ok"] is ok
    assert "bytes reales" in resultado["detail"]
    assert len(llamadas) == (1 if estado == "nuevo" else 2)


@pytest.mark.parametrize("estado", ESTADOS)
@pytest.mark.parametrize("causa", ["ausente", "denegada", "directorio"])
def test_lectura_fallida_nunca_certifica(tmp_path, monkeypatch, estado, causa):
    mod = _cargar("vdi_lectura_fallida")
    doc = tmp_path / "doc.md"
    _git_fixture(monkeypatch, mod, tmp_path, estado)
    intentos = []
    if causa == "directorio":
        doc.mkdir()
    elif causa == "denegada":
        doc.write_bytes(b"a\n")
        def denegar(path):
            intentos.append(path)
            raise PermissionError("denegada por fixture")
        monkeypatch.setattr(Path, "read_bytes", denegar)
    resultado = mod.eol_veredicto(doc, tmp_path)
    assert resultado["ok"] is False
    assert resultado["disco"] == "ERROR-LECTURA"
    assert "lectura fallida" in resultado["detail"]
    if causa == "denegada":
        assert intentos == [doc]


def test_eol_almacenado_denuncia_un_blob_que_almacena_crlf(tmp_path, monkeypatch):
    mod = _cargar("vdi_indice_crlf")
    _git_fixture(monkeypatch, mod, tmp_path, "stageado", "crlf")
    resultado = mod.eol_almacenado(tmp_path / "doc.md", tmp_path)
    assert resultado["almacenado"] == "crlf" and resultado["ok"] is False


def test_correccion_lf_no_hereda_el_fallo_del_indice_viejo(tmp_path, monkeypatch):
    mod = _cargar("vdi_correccion_lf")
    doc = tmp_path / "doc.md"
    doc.write_bytes(b"corregido\n")
    _git_fixture(monkeypatch, mod, tmp_path, "modificado", "crlf")
    resultado = mod.eol_veredicto(doc, tmp_path)
    assert resultado["ok"] is True and resultado["disco"] == "LF"
    assert resultado["almacenado"] == "crlf"


def test_validate_line_endings_denuncia_los_seis_blobs_crlf(tmp_path, monkeypatch):
    mod = _cargar("vdi_seis")
    doc = tmp_path / "doc.md"
    doc.write_bytes(b"a\r\n")
    _git_fixture(monkeypatch, mod, tmp_path, "limpio")
    _gobernar(mod, tmp_path, doc)
    resultado = mod.validate_line_endings()
    assert resultado.passed is False and len(resultado.issues) == len(GOBERNADOS)
    assert all("bytes reales CRLF" in issue for issue in resultado.issues)


def test_validate_line_endings_publica_cobertura_real_de_nuevos(tmp_path, monkeypatch):
    mod = _cargar("vdi_nuevos")
    doc = tmp_path / "doc.md"
    doc.write_bytes(b"a\n")
    _git_fixture(monkeypatch, mod, tmp_path, "nuevo")
    _gobernar(mod, tmp_path, doc)
    resultado = mod.validate_line_endings()
    assert resultado.passed is True
    assert "sin registrar en git" in " ".join(resultado.details)
    assert "bytes reales comprobados" in " ".join(resultado.details)


@pytest.mark.parametrize("comando", ["ls-files", "status"])
@pytest.mark.parametrize("causa", ["exit", "excepcion"])
def test_lector_git_roto_es_hallazgo_y_no_silencio(tmp_path, monkeypatch, comando, causa):
    mod = _cargar("vdi_git_roto")
    doc = tmp_path / "doc.md"
    doc.write_bytes(b"a\n")
    _git_fixture(monkeypatch, mod, tmp_path, "limpio")
    original = mod.subprocess.run

    def roto(argv, **kwargs):
        if argv[1] == comando:
            if causa == "excepcion":
                raise OSError("lector caido a proposito")
            return SimpleNamespace(returncode=7, stdout="", stderr="lector caido a proposito")
        return original(argv, **kwargs)

    monkeypatch.setattr(mod.subprocess, "run", roto)
    resultado = mod.eol_veredicto(doc, tmp_path)
    assert resultado["ok"] is False
    assert resultado["disco"] == "LF"
    assert "lector caido a proposito" in resultado["detail"]


@pytest.mark.parametrize("respuesta", ["desconocido", "i/lf w/? attr/\tdoc.md\n",
                                         "i/lf w/lf attr/\ta.md\ni/lf w/lf attr/\tb.md\n"])
def test_respuesta_git_ilegible_no_certifica(tmp_path, monkeypatch, respuesta):
    mod = _cargar("vdi_git_ilegible")
    doc = tmp_path / "doc.md"
    doc.write_bytes(b"a\n")
    monkeypatch.setattr(mod, "subprocess", SimpleNamespace(run=lambda *a, **k:
                        SimpleNamespace(returncode=0, stdout=respuesta, stderr="")))
    resultado = mod.eol_veredicto(doc, tmp_path)
    assert resultado["ok"] is False
    assert resultado["almacenado"] == "LECTOR-FALLIDO"
    assert resultado["disco"] == "LF"


def _exigir_rechazo(resultado, causa):
    assert resultado["ok"] is False, f"FALSO-FAVORABLE: {causa}"
    assert resultado["disco"] == causa


@pytest.mark.parametrize("causa", ["CRLF", "ERROR-LECTURA"])
def test_control_snapshot_limpio_omite_bytes_y_post_los_lee(tmp_path, monkeypatch, causa):
    pre = _cargar("vdi_pre_snapshot", PRE_DETECTOR)
    post = _cargar("vdi_post_snapshot")
    doc = tmp_path / "doc.md"
    doc.write_bytes(b"a\r\n")
    for mod in (pre, post):
        _git_fixture(monkeypatch, mod, tmp_path, "limpio")
    intentos = []
    leer = Path.read_bytes

    def lectura(path):
        intentos.append(path)
        if causa == "ERROR-LECTURA":
            raise PermissionError("denegada por fixture")
        return leer(path)

    monkeypatch.setattr(Path, "read_bytes", lectura)
    anterior = pre.eol_veredicto(doc, tmp_path)
    assert anterior["ok"] is True and intentos == []
    with pytest.raises(AssertionError, match=f"FALSO-FAVORABLE: {causa}"):
        _exigir_rechazo(anterior, causa)
    actual = post.eol_veredicto(doc, tmp_path)
    _exigir_rechazo(actual, causa)
    assert intentos == [doc]


def test_lectores_git_reales_sin_escrituras():
    mod = _cargar("vdi_git_real")
    for path in (mod.DOMAIN_PRIMER, mod.EXECUTOR):
        indice = mod.eol_almacenado(path, ROOT)
        assert indice["almacenado"] == "lf", indice
        assert mod.eol_tocada(path, ROOT) in ("LIMPIO", "SUCIO")
        resultado = mod.eol_veredicto(path, ROOT)
        assert resultado["disco"] == mod.eol_en_disco(path)
        assert resultado["ok"] == (mod.eol_en_disco(path) in ("LF", "VACIO"))
