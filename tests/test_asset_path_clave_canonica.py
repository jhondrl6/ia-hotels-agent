"""FASE-HOTFIX-PRE-RELEASE / H7 (S-I3): una ruta, dos claves — fijada por
contract test **por artefacto** y documentada en el DTO.

Medido en el plan: el mismo hecho (ruta local de un asset) se serializa como
`asset_path` en `proposal_asset_matrix.json` y como `path` en
`v4_complete_report.assets_generated[]`. El script de comparacion de FASE-I leyo
`asset_path` en el report, obtuvo `null` en **ambas** corridas y habria afirmado
que A6 seguia roto.

La decision NO es unificar las claves a machetazo: son DTOs distintos con
consumidores distintos y romper una clave de artefacto rompe al lector externo
que la usa. Lo que se fija aqui es **cual es la clave canonica de cada uno**, y
que la documentacion del DTO no se pueda borrar sin que este test se queje
(modelo: memoria `unificar-conteos-derivados-en-dtos-multi-consumer`).
"""

import inspect
import json
from pathlib import Path

from modules.asset_generation.proposal_asset_alignment import (
    AssetAlignmentMatrix,
    ProposalAssetMatrixEntry,
)
from modules.asset_generation.v4_asset_orchestrator import GeneratedAsset

CORRIDA = Path("evidence/FASE-I/corrida")
MATRIZ_REAL = CORRIDA / "hotelsalentoreal/v4_audit/proposal_asset_matrix.json"
REPORT_REAL = CORRIDA / "v4_complete_report.json"

# Whitelist AC-F3 (FASE-P3-B) — contrato de §5.1 en
# evidence/FASE-P1/decision-enforcement.md. NO es un xfail ni una rendición: cada
# nombre extra tiene un contrato escrito que lo limita a re-publicar un hecho que ya
# resolvió otro, no a afirmar uno nuevo sobre la producción del asset.
EMISORES_LEGITIMOS = {
    # Emisor canónico: la ruta prometida al cliente.
    "asset_generation/proposal_asset_alignment.py",
    # Bot 3: eco de la ruta que ya resolvió al leer la matriz, dentro de su propio
    # `revision_assets.json`. No añade un hecho nuevo sobre la producción del asset.
    "quality_gates/tribunal/asset_reviewer.py",
}
CONSUMIDORES_LEGITIMOS = {
    # Lector QA del entregable.
    "quality_gates/delivery_quality_report.py",
    # Bot 3 lee la clave canónica de la matriz para poder hacer su eco contratado.
    "quality_gates/tribunal/asset_reviewer.py",
}


def _entries_reales() -> list:
    data = json.loads(MATRIZ_REAL.read_text(encoding="utf-8"))
    return [
        ProposalAssetMatrixEntry(
            service_name=e["service_name"],
            pain_ids=e["pain_ids"],
            asset_type=e["asset_type"],
            asset_path=e.get("asset_path"),
            confidence=e["confidence"],
            status=e["status"],
        )
        for e in data["entries"]
    ]


class TestClaveCanonicaPorArtefacto:
    def test_matriz_emite_asset_path_en_disco(self, tmp_path):
        """Writer real de la matriz: la clave es `asset_path`, nunca `path`."""
        path = tmp_path / "proposal_asset_matrix.json"
        AssetAlignmentMatrix(entries=_entries_reales()).save(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        entrada_con_ruta = next(e for e in data["entries"] if e["status"] == "LINKED")
        assert "asset_path" in entrada_con_ruta
        assert entrada_con_ruta["asset_path"]
        assert "path" not in entrada_con_ruta, "la matriz no debe duplicar la clave del report"

    def test_report_emite_path_en_disco(self):
        """El unico `v4_complete_report.json` del plan: la clave es `path`."""
        data = json.loads(REPORT_REAL.read_text(encoding="utf-8"))
        assert data["assets_generated"], "la corrida real no dejo assets_generated"
        for a in data["assets_generated"]:
            assert "path" in a
            assert "asset_path" not in a, (
                "el report cambio de clave: rompe a todo lector externo del ZIP "
                "(contrato fijado en FASE-HOTFIX, S-I3)"
            )

    def test_la_proyeccion_del_report_no_copia_asset_path(self):
        """El writer vivo del report sigue proyectando `path` (no `asset_path`).

        La proyeccion esta en `main.py` dentro del flujo v4complete, que no es
        invocable sin corrida; lo que si es verificable mecanicamente es que
        ninguna de sus dos proyecciones `assets_generated` introduzca la clave
        de la matriz.
        """
        import re

        import main

        src = inspect.getsource(main.run_v4_complete_mode)
        bloques = [
            src[i.start(): src.index("]", i.start())]
            for i in re.finditer(r"'assets_generated': \[", src)
        ]
        assert bloques, "main.py ya no proyecta assets_generated"
        assert any("'path': a.path" in b for b in bloques), (
            "la proyeccion del report perdio su clave canonica `path`"
        )
        for b in bloques:
            assert "asset_path" not in b

    def test_consumer_delivery_lee_la_clave_de_la_matriz(self):
        """El lector cruzado (delivery ← matriz) usa la clave del artefacto que lee."""
        from modules.quality_gates.delivery_quality_report import (
            DeliveryQualityReportGenerator,
        )

        src = inspect.getsource(DeliveryQualityReportGenerator)
        assert 'e.get("asset_path")' in src
        assert 'e.get("path")' not in src


class TestDocumentacionDelContrato:
    """Si el DTO deja de documentar la clave del otro artefacto, la conjetura vuelve."""

    def test_entry_de_matriz_documenta_su_clave_y_la_del_report(self):
        doc = ProposalAssetMatrixEntry.__doc__ or ""
        assert "asset_path" in doc
        assert "path" in doc
        assert "v4_complete_report" in doc

    def test_generated_asset_documenta_su_clave_y_la_de_la_matriz(self):
        doc = GeneratedAsset.__doc__ or ""
        assert "path" in doc
        assert "asset_path" in doc
        assert "proposal_asset_matrix" in doc

    def test_barreda_un_solo_emisor_de_la_clave(self):
        """Barreda L-H6: `asset_path` la EMITE un solo archivo y la CONSUME uno.

        La barra es una **igualdad de conjuntos**, no una contención: un emisor o
        consumidor nuevo sin contrato la pone en rojo, y retirar la autorización de
        Bot 3 también (AC-F3, NR7).

        Medido en FASE-P3-B: hasta esta fase la segunda aserción nunca se había
        evaluado — la primera fallaba antes, así que el conjunto de consumidores
        estaba sin vigilar pese a que el test estaba en rojo por otra causa.
        """
        import re

        raiz = Path(__file__).resolve().parents[1] / "modules"
        emite = re.compile(r"""["']asset_path["']\s*:""")
        consume = re.compile(r"""\[\s*["']asset_path["']\s*\]|get\(\s*["']asset_path["']""")
        emisores: set = set()
        consumidores: set = set()
        for py in sorted(raiz.rglob("*.py")):
            texto = py.read_text(encoding="utf-8")
            rel = py.relative_to(raiz).as_posix()
            if emite.search(texto):
                emisores.add(rel)
            if consume.search(texto):
                consumidores.add(rel)
        assert emisores == EMISORES_LEGITIMOS, emisores
        assert consumidores == CONSUMIDORES_LEGITIMOS, consumidores
