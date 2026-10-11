"""Diente del barrido por FORMA DE FRAGMENTO de credencial (check [4/13]).

Que goberna: que `sk-` + recorte + cola (y las demas familias de
`config/secret_fragment_policy.yaml`) se detecte TAMBIEN dentro de `archives/`, `evidence/` y
`.opencode/`, que el scan general exempta para poder contener referencias a secretos. La forma
completa no servia: `AIzaSy{30,}` y `sk-{20,}` exigen mas chars de los que tiene un recorte, y
fue exactamente ese recorte el que el viejo `config_checker` publico en `evidence/FASE-I/`.

Convencion anti-auto-comprension: los literales que casan con la forma se ENSAMBLAN en runtime
(`PUNTOS = "." * 3`). Si este archivo los escribiera pegados, su propio barredor lo detectaria.
"""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "run_all_validations_para_fragmentos", ROOT / "scripts" / "run_all_validations.py"
)
rav = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rav)

PUNTOS = "." * 3
POLITICA_REAL = ROOT / "config" / "secret_fragment_policy.yaml"
# Revision del instrumento ANTES de este diente: no tenia barrido de exentos.
REV_SIN_BARRIDO = "d35cb3d"
RUTA_PRODUCTOR = "scripts/run_all_validations.py"


def _fragmento(prefijo: str, cabeza: str = "b", cola: str = "5a12") -> str:
    return prefijo + cabeza + PUNTOS + cola


def _runner_con_tracked(tmp_path, monkeypatch, archivos: dict, politica_dir: Path | None):
    """Runner sobre un arbol sintetico: `_git_tracked_files` devuelve lo que le damos."""
    if politica_dir is not None:
        monkeypatch.setattr(rav, "ROOT_DIR", politica_dir)
    runner = rav.ValidationRunner(quick=True, repo_root=tmp_path)
    paths = []
    for rel, lineas in archivos.items():
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        paths.append(f)
    monkeypatch.setattr(runner, "_git_tracked_files", lambda: paths)
    monkeypatch.setattr(runner, "_untracked_output_files", lambda: [])
    monkeypatch.setattr(runner, "_check_staged_content", lambda patterns: [])
    return runner


def _politica_en(dir_raiz: Path, grandfathered: list, exentos=("archives", "evidence", ".opencode")):
    cfg = dir_raiz / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    datos = {
        "version": 1,
        "duenio": "test",
        "directorios_exentos_barridos": list(exentos),
        "prefijos": ["sk-", "AIza", "ghp_", "gho_", "ghu_", "ghs_", "ghr_", "pplx-"],
        "grandfathered": grandfathered,
    }
    import yaml
    (cfg / "secret_fragment_policy.yaml").write_text(
        yaml.safe_dump(datos, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return dir_raiz


class TestLaForma:
    def test_caza_todas_las_familias_que_declara_la_politica(self):
        import yaml
        politica = yaml.safe_load(POLITICA_REAL.read_text(encoding="utf-8"))
        regex = rav.ValidationRunner._fragment_regex(politica["prefijos"])
        for prefijo in politica["prefijos"]:
            assert regex.search(_fragmento(prefijo)), f"la familia {prefijo!r} no esta anclada"

    def test_no_caza_el_placeholder_de_guia_de_env_template(self):
        import yaml
        politica = yaml.safe_load(POLITICA_REAL.read_text(encoding="utf-8"))
        regex = rav.ValidationRunner._fragment_regex(politica["prefijos"])
        guia = "OPENAI_API_KEY=your_o" + PUNTOS + "here"
        assert not regex.search(guia), "la forma etiquetada de guia se colaria como credencial"
        assert not regex.search("prefijo" + PUNTOS + "sufijo")
        assert not regex.search("el patron " + PUNTOS)
        real = (ROOT / ".env.template").read_text(encoding="utf-8")
        assert not regex.search(real), ".env.template casaria con la regla y el gate iria a rojo"


class TestElBarridoLeeLoQueLaExencionNoLeia:
    def test_rojo_fragmento_bajo_el_directorio_exempto(self, tmp_path, monkeypatch):
        runner = _runner_con_tracked(
            tmp_path, monkeypatch,
            {"evidence/FASE-X/corrida.txt": ["cabecera", "la clave es " + _fragmento("sk-")]},
            _politica_en(tmp_path / "politica", []))
        runner._check_no_secrets()
        result = runner.results[-1]
        assert not result.passed, "el directorio exento sigue sin leerse: el hueco original"
        assert "BLOCKING" in result.message
        assert any("evidence/FASE-X/corrida.txt" in d for d in result.details)
        assert _fragmento("sk-") not in " ".join(result.details), "la salida debe estar redactada"

    def test_green_el_mismo_fragmento_abuelado_con_lineas_cuadradas(self, tmp_path, monkeypatch):
        runner = _runner_con_tracked(
            tmp_path, monkeypatch,
            {"evidence/FASE-X/corrida.txt": ["cabecera", "la clave es " + _fragmento("sk-")]},
            _politica_en(tmp_path / "politica",
                         [{"ruta": "evidence/FASE-X/corrida.txt", "lineas": [2],
                           "motivo": "abuelado de prueba", "duenio": "test"}]))
        runner._check_no_secrets()
        result = runner.results[-1]
        assert result.passed, result.details
        assert "1 grandfathered con lineas cuadadas" in result.message

    def test_rojo_si_el_abuelado_gana_una_linea_nueva(self, tmp_path, monkeypatch):
        runner = _runner_con_tracked(
            tmp_path, monkeypatch,
            {"evidence/FASE-X/corrida.txt": ["cabecera", "vieja " + _fragmento("AIza"),
                                              "nueva " + _fragmento("sk-")]},
            _politica_en(tmp_path / "politica",
                         [{"ruta": "evidence/FASE-X/corrida.txt", "lineas": [2],
                           "motivo": "solo la linea 2 estaba declarada", "duenio": "test"}]))
        runner._check_no_secrets()
        result = runner.results[-1]
        assert not result.passed
        assert any("contra 1 declaradas" in d for d in result.details), \
            "el abuelado se trago la linea nueva: seria un perdon permanente"

    def test_rojo_si_la_politica_y_el_check_discrepan_de_la_exencion(self, tmp_path, monkeypatch):
        runner = _runner_con_tracked(
            tmp_path, monkeypatch, {"notas.md": ["limpio"]},
            _politica_en(tmp_path / "politica", [], exentos=("evidence",)))
        runner._check_no_secrets()
        result = runner.results[-1]
        assert not result.passed
        assert any("discrepan" in d for d in result.details), \
            "una politica que exenta menos directorios perderia alcance en silencio"

    def test_politica_ausente_no_puede_decir_sin_hallazgos(self, tmp_path, monkeypatch):
        runner = _runner_con_tracked(tmp_path, monkeypatch, {"notas.md": ["limpio"]},
                                     tmp_path / "sin_config")
        runner._check_no_secrets()
        result = runner.results[-1]
        assert not result.passed, "un barrido sin politica no puede informar ausencia"
        assert "NO_CUBIERTO" in result.message


class TestControlesContraElDefecto:
    def test_control_negativo_el_instrumento_versionado_leia_verde_ese_fragmento(
            self, tmp_path, monkeypatch):
        """Sobre el MISMO arbol que el rojo de arriba, el verificador de `d35cb3d` (sin barrido)
        dice SIN_HALLAZGOS. Prueba que la pata nueva cierra un hueco que existia, no otro."""
        proc = subprocess.run(["git", "show", f"{REV_SIN_BARRIDO}:{RUTA_PRODUCTOR}"],
                              capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))
        assert proc.returncode == 0, f"{REV_SIN_BARRIDO} no resuelve: re-anclar el control"
        monkeypatch.setattr(rav, "ROOT_DIR", _politica_en(tmp_path / "politica", []))
        ruta_vieja = tmp_path / "rav_viejo.py"
        ruta_vieja.write_text(proc.stdout, encoding="utf-8", newline="\n")
        espec = importlib.util.spec_from_file_location("rav_versionado", ruta_vieja)
        viejo = importlib.util.module_from_spec(espec)
        espec.loader.exec_module(viejo)
        assert not hasattr(viejo.ValidationRunner, "_barrido_fragmentos"), (
            f"la revision {REV_SIN_BARRIDO} ya trae el barrido: re-anclar a una anterior")

        archivos = {"evidence/FASE-X/corrida.txt": ["cabecera", "la clave es " + _fragmento("sk-")]}
        paths = []
        for rel, lineas in archivos.items():
            f = tmp_path / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("\n".join(lineas) + "\n", encoding="utf-8")
            paths.append(f)
        runner = viejo.ValidationRunner(quick=True, repo_root=tmp_path)
        monkeypatch.setattr(runner, "_git_tracked_files", lambda: paths)
        monkeypatch.setattr(runner, "_untracked_output_files", lambda: [])
        monkeypatch.setattr(runner, "_check_staged_content", lambda patterns: [])
        runner._check_no_secrets()
        result = runner.results[-1]
        assert result.passed and "SIN_HALLAZGOS" in result.message, (
            "el control negativo ya no reproduce el hueco: el rojo de arriba no demuestra nada")

    def test_la_poblacion_real_del_repo_casa_con_la_politica_linea_a_linea(self):
        """El grandfathered del repo no es decorativo: las cuatro entradas casan con las lineas
        que hoy tienen forma de fragmento, y no hay ninguna otra. Si alguien publica un fragmento
        nuevo, o purga uno declarado, este test corta."""
        import yaml
        politica = yaml.safe_load(POLITICA_REAL.read_text(encoding="utf-8"))
        regex = rav.ValidationRunner._fragment_regex(politica["prefijos"])
        runner = rav.ValidationRunner(quick=True, repo_root=ROOT)
        declaradas = {str(g["ruta"]).replace("\\", "/"): sorted(g.get("lineas", []))
                      for g in politica["grandfathered"]}
        halladas = {}
        auto_excluido = ("config/" + runner._FRAGMENT_POLICY).lower()
        for path in list(runner._git_tracked_files()) + runner._untracked_output_files():
            try:
                rel = path.relative_to(ROOT).as_posix()
                if rel.lower() == auto_excluido:
                    continue
                if path.is_symlink() or not path.is_file():
                    continue
                if path.suffix.lower() in runner._KNOWN_BINARY_EXTS:
                    continue
                if path.stat().st_size > runner._MAX_SCAN_BYTES:
                    continue
                raw = path.read_bytes()
            except (OSError, ValueError):
                continue
            if b"\x00" in raw[:8192]:
                continue
            lineas = [i for i, l in enumerate(raw.decode("utf-8", "ignore").splitlines(), 1)
                      if regex.search(l)]
            if lineas:
                halladas[rel] = sorted(lineas)
        assert halladas == declaradas, (
            "la politica y el arbol discrepan: " + json.dumps(
                {"solo_en_arbol": {k: v for k, v in halladas.items() if declaradas.get(k) != v},
                 "solo_en_politica": {k: v for k, v in declaradas.items() if halladas.get(k) != v}},
                ensure_ascii=False)[:600])


def test_la_politica_del_repo_declaradamente_excluye_su_propio_archivo():
    """El barredor no puede cazar la nota que el mismo escribe: la politica cita el ejemplo."""
    contenido = POLITICA_REAL.read_text(encoding="utf-8")
    runner = rav.ValidationRunner(quick=True, repo_root=ROOT)
    assert ("config/" + runner._FRAGMENT_POLICY).lower() in runner._FRAGMENT_SELF_EXCLUDE
    assert _fragmento("sk-") not in contenido, "la politica no debe llevar el literal ensamblado"
