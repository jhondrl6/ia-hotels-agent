"""Tests para scripts/build_lesson_index.py (capa fría del Paso 0).

Cubren lo que hace útil al índice y lo que lo vuelve peligroso si se rompe:
que una definición en tabla se capture con su enunciado, que una cita inline NO
se haga pasar por definición, que el plan dueño sea el más antiguo y las
redefiniciones queden visibles, que `AC-*` no se indexe, que un archivo marcado
OBSOLETO no done lecciones, que la salida sea determinista (sin timestamps: el
gate de frescura compara bytes) y que `--check` se dispare con el índice vencido.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from scripts import build_lesson_index as bli

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_lesson_index.py"
ANALISIS = "10-analisis-post-implementacion.md"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _plan(root: Path, nombre: str, cuerpo: str, archivo: str = ANALISIS) -> Path:
    plan = root / nombre
    plan.mkdir(parents=True)
    (plan / archivo).write_text(cuerpo, encoding="utf-8")
    return plan


def _base(plans: Path, tmp_path: Path, out: Path) -> list[str]:
    """Args del CLI aislados del repo: sin el `context/` real contaminando la corrida."""
    return [
        "--plans-dir",
        str(plans),
        "--context-dir",
        str(tmp_path / "context-vacio"),
        "--out-dir",
        str(out),
    ]


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    """Dos planes fechados: el viejo define L-X1 y S-V1; el nuevo solo los cita."""
    plans = tmp_path / "plans"
    plans.mkdir()
    (tmp_path / "context-vacio").mkdir()
    _plan(
        plans,
        "PLAN-VIEJO-2026-01-01",
        "## Lecciones Aprendidas\n\n"
        "### Lecciones nuevas de este plan\n\n"
        "| ID | Enunciado | Evidencia |\n|----|-----------|-----------|\n"
        "| L-X1 | Un gate que solo loggea no previene | 3 corridas |\n"
        "| S-V1 | El ZIP se escribía dos veces | hallazgo V1 |\n",
    )
    _plan(
        plans,
        "PLAN-NUEVO-2026-02-01",
        "## Prompt\n\n"
        "- Aplicar L-X1 al gate nuevo y retomar S-V1.\n"
        "- Citar AC-D1 y D-NC9 sin definirlos.\n",
    )
    return plans


class TestDefinicionVsCita:
    def test_definicion_en_tabla_capture_enunciado_y_seccion(self, corpus):
        index, _ = bli.build(corpus)
        entry = index["lessons"]["L-X1"]
        assert entry["enunciado"] == "Un gate que solo loggea no previene — 3 corridas"
        assert entry["plan"] == "PLAN-VIEJO-2026-01-01"
        assert entry["seccion"] == "Lecciones nuevas de este plan"
        assert entry["familia"] == "L"

    def test_cita_inline_no_se_hace_pasar_por_definicion(self, corpus):
        index, _ = bli.build(corpus)
        assert "D-NC9" not in index["lessons"]
        assert "D-NC9" in {e["id"] for e in index["undefined"]}

    def test_las_citas_del_plan_dueño_no_cuentan_como_diffusion(self, corpus):
        index, _ = bli.build(corpus)
        assert index["lessons"]["L-X1"]["planes_que_lo_citan"] == ["PLAN-NUEVO-2026-02-01"]
        assert index["lessons"]["L-X1"]["total_citas"] == 1  # su propia definición no cuenta


class TestFamilias:
    def test_ac_no_se_indexa_ni_aparece_como_hueco(self, corpus):
        index, _ = bli.build(corpus)
        assert not any(lesson_id.startswith("AC-") for lesson_id in index["lessons"])
        assert "AC-D1" not in [e["id"] for e in index["undefined"]]

    def test_la_cobertura_declara_lo_excluido_y_lo_escaneado(self, corpus):
        _, coverage = bli.build(corpus)
        assert "AC-* (criterios de aceptación por plan)" in coverage["familias_excluidas"]
        assert coverage["ids_con_definicion"] == 2
        assert coverage["archivos_analysis_escaneados"] == 2


class TestAntiguedadYObsoleto:
    def test_el_plan_mas_antiguo_es_dueño_y_redefinir_otros_queda_visible(self, corpus):
        _plan(
            corpus,
            "PLAN-POSTERIOR-2026-03-01",
            "## Lecciones Aprendidas\n\n| L-X1 | redefinición posterior | x |\n",
        )
        index, _ = bli.build(corpus)
        assert index["lessons"]["L-X1"]["plan"] == "PLAN-VIEJO-2026-01-01"
        assert index["lessons"]["L-X1"]["redefiniciones"] == ["PLAN-POSTERIOR-2026-03-01"]

    def test_archivo_obsoleto_no_done_lecciones(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        _plan(
            plans,
            "PLAN-2026-01-01",
            "| L-OBS1 | lección en archivo obsoleto | x |\n",
            archivo="09-analisis-fases-1-4--OBSOLETO.md",
        )
        index, coverage = bli.build(plans)
        assert "L-OBS1" not in index["lessons"]
        assert coverage["archivos_analysis_escaneados"] == 0
        assert coverage["ids_citados_sin_definicion"] == 1


class TestArtefactoGenerado:
    def test_render_es_determinista_sin_timestamp_de_corrida(self, corpus):
        index, coverage = bli.build(corpus)
        assert bli.render_md(index, coverage) == bli.render_md(index, coverage)
        assert bli.render_json(index, coverage) == bli.render_json(index, coverage)
        assert "2026-01-01" in bli.render_md(index, coverage)  # fecha del plan, no de corrida

    def test_check_falla_con_indice_vencido_y_pasa_regenerado(self, corpus, tmp_path):
        out = tmp_path / "out"
        base = _base(corpus, tmp_path, out)

        vencido = _run(*base, "--check")
        assert vencido.returncode == 1, "--check no se disparó con el índice ausente"
        assert "vencido" in vencido.stdout

        assert _run(*base).returncode == 0
        assert _run(*base, "--check").returncode == 0

        (out / bli.MD_NAME).write_text("contenido vencido\n", encoding="utf-8")
        rerun = _run(*base, "--check")
        assert rerun.returncode == 1 and bli.MD_NAME in rerun.stdout

    def test_json_expone_cobertura_y_aviso_de_no_edicion(self, corpus, tmp_path):
        _run(*_base(corpus, tmp_path, tmp_path / "out"))
        payload = json.loads((tmp_path / "out" / bli.JSON_NAME).read_text(encoding="utf-8"))
        assert payload["cobertura"]["ids_con_definicion"] == 2
        assert payload["_notice"].startswith("Artefacto generado")


class TestCorpusContexto:
    """Las lecciones tambien viven en `.opencode/context/` (Paso 0 lo declara)."""

    def test_un_context_define_leccion_y_es_su_dueño(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        context = tmp_path / "context"
        context.mkdir()
        (context / "CONTEXT-SALENTO-REAL-2026-08-27.md").write_text(
            "## 8.2 Lecciones\n\n| L-Z1 | Un gate que cicla sin tope reintiene infinito | x |\n",
            encoding="utf-8",
        )
        _plan(plans, "PLAN-POSTERIOR-2026-09-01", "- Retomar L-Z1 en el tribunal.\n")
        index, coverage = bli.build(plans, context)
        entry = index["lessons"]["L-Z1"]
        assert entry["plan"] == "context/CONTEXT-SALENTO-REAL-2026-08-27"
        assert entry["origen"] == "contexto"
        assert entry["planes_que_lo_citan"] == ["PLAN-POSTERIOR-2026-09-01"]
        assert coverage["archivos_contexto_escaneados"] == 1

    def test_un_plan_no_usurpa_el_dueno_aunque_sea_mas_nuevo(self, tmp_path):
        """La fecha manda: el contexto de agosto define, el plan de septiembre cita."""
        plans = tmp_path / "plans"
        _plan(plans, "PLAN-VIVO-2026-09-01", "| L-Z1 | redacción posterior | x |\n")
        context = tmp_path / "context"
        context.mkdir()
        (context / "CONTEXT-VIEJO-2026-08-01.md").write_text(
            "| L-Z1 | definición original | x |\n", encoding="utf-8"
        )
        index, _ = bli.build(plans, context)
        assert index["lessons"]["L-Z1"]["plan"] == "context/CONTEXT-VIEJO-2026-08-01"
        assert index["lessons"]["L-Z1"]["redefiniciones"] == ["PLAN-VIVO-2026-09-01"]


class TestSueloDeDefinicion:
    """Fijado tras medir 5 definiciones falsas (2 % del índice en la primera corrida)."""

    @pytest.mark.parametrize(
        "linea",
        [
            "### Lecciones nuevas de este plan (L-PF1+ — registrar al cierre de cada fase)",
            "### ACs propuestos §5.1/§5.4 (dueño FASE-VERIFY, DA-T4B.3)",
            "### Lecciones nuevas de este plan (numeración L-VUP-n)",
        ],
    )
    def test_id_dentro_del_parentesis_de_un_titulo_no_define(self, linea):
        lesson_id = bli.ID_RE.search(linea).group(1)
        assert bli._extract_definition(linea, lesson_id) is None

    def test_titulo_que_abre_con_el_id_si_define(self):
        statement = bli._extract_definition(
            "### L-Q1 — un título que abre con la lección y su texto completo", "L-Q1"
        )
        assert statement and statement.startswith("un título")

    def test_enunciado_corto_no_define(self):
        assert bli._extract_definition("| L-Q2 | ok |", "L-Q2") is None


class TestEtiquetadoDePlan:
    def test_planes_bajo_archives_se_etiquetan_como_archivados(self, tmp_path):
        plans = tmp_path / "plans"
        _plan(
            plans / "Archives",
            "PLAN-ARCHIVADO-2026-01-01",
            "| L-A1 | lección archivada | x |\n",
        )
        index, _ = bli.build(plans)
        assert index["lessons"]["L-A1"]["plan"] == "Archives/PLAN-ARCHIVADO-2026-01-01"
