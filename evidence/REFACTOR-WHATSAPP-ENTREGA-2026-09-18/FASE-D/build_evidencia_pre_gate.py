"""FASE-D: produce la evidencia con los writers de produccion (no a mano).

Emite cuatro artefactos en este directorio:

* `coherence_pre_gate_ejemplo.json` — lo que escribe `_persist_coherence_pre_gate`
  sobre un reporte con DOS checks de severidad error (el caso SalentoReal: score
  0.88 por encima del umbral, veredicto False).
* `gate_report_coherence_ejemplo.json` — la forma canonica de
  `_build_gate_report_payload`, con `gate_results[coherence].details.failed_check_names`
  y sus mensajes.
* `log_saneado_pre_gate.txt` — el log del bloqueo con el numero enmascarado.
* `resumen_escritura.json` — la conciliacion de lo que publican los dos JSON.

Los datos son sinteticos: ningun numero de hotel real, ninguna credencial.
"""

import json
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
EV = Path(__file__).resolve().parent

import main  # noqa: E402
from modules.assessment_builder import AssessmentBuilder  # noqa: E402
from modules.commercial_documents.coherence_validator import (  # noqa: E402
    CoherenceCheck,
    CoherenceReport,
    mask_telephone_digits,
)
from modules.quality_gates.publication_gates import (  # noqa: E402
    PublicationGatesOrchestrator,
    check_publication_readiness,
)

SCORE = 0.88
UMBRAL = 0.8
CULPABLES = [
    CoherenceCheck(
        name="whatsapp_verified",
        passed=False,
        score=0.0,
        message=(
            "WhatsApp con confidence insuficiente (0.30) - requiere >= 0.9 "
            "| destino +573001234567"
        ),
        severity="error",
    ),
    CoherenceCheck(
        name="assets_are_justified",
        passed=False,
        score=0.75,
        message="3/4 assets justificados por problemas del diagnostico",
        severity="error",
    ),
]
SANOS = [
    CoherenceCheck(
        "problems_have_solutions", True, 0.9, "90% de problemas tienen solucion", "warning"
    ),
    CoherenceCheck(
        "financial_data_validated", True, 0.8, "Datos financieros validados", "info"
    ),
    CoherenceCheck("price_matches_pain", True, 0.9, "Precio dentro de rango", "warning"),
    CoherenceCheck(
        "promised_assets_exist",
        True,
        1.0,
        "Todos los assets prometidos estan implementados",
        "info",
    ),
]


def reporte() -> CoherenceReport:
    return CoherenceReport(
        is_coherent=False,
        overall_score=SCORE,
        checks=[*CULPABLES, *SANOS],
        errors=[f"[{c.name}] {c.message}" for c in CULPABLES],
        warnings=[],
    )


def principal() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        salida = Path(tmp)

        # 1) Reporte del pre-gate, escrito por el writer de produccion.
        decision = main._coherence_pre_gate_decision(
            report=reporte(), threshold=UMBRAL, is_blocking=False
        )
        ruta_pre = Path(
            main._persist_coherence_pre_gate(
                output_dir=salida,
                hotel_id="hotelsintetico",
                report=reporte(),
                decision=decision,
                hotel_url="https://ejemplo-hotelsintetico.test",
            )
        )
        destino_pre = EV / "coherence_pre_gate_ejemplo.json"
        shutil.copyfile(ruta_pre, destino_pre)

        # 2) Gate report canonico: assessment real -> gate real -> writer real.
        assessment = (
            AssessmentBuilder()
            .with_core("https://ejemplo-hotelsintetico.test", "Hotel Sintetico")
            .with_coherence(reporte(), None)
            .build()
        )
        gate = PublicationGatesOrchestrator().gates["coherence"](assessment)
        readiness = check_publication_readiness(assessment, [gate])
        payload = main._build_gate_report_payload(
            [gate], readiness, hotel_url=assessment["url"]
        )
        destino_gr = EV / "gate_report_coherence_ejemplo.json"
        destino_gr.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # 3) Log saneado de la ruta: las causas impresas y el skip de FASE 4.
        bitacora = StringIO()
        orquestador = MagicMock()
        with redirect_stdout(bitacora):
            print(
                f"🔒 Gate de Coherencia: score {decision['score']:.2f} "
                f"(umbral {decision['threshold']}), status {decision['status']}, "
                f"is_coherent={decision['verdict']}"
            )
            for culpable in decision["guilty_checks"]:
                print(
                    f"     - {culpable['name']}: {mask_telephone_digits(culpable['message'])}"
                )
            resultado = main._run_asset_generation(
                orchestrator=orquestador,
                pre_gate_blocked=decision["blocks_asset_generation"],
                audit_result=MagicMock(),
                validation_summary={},
                hotel_name="Hotel Sintetico",
            )
            print(f"   asset_result = {resultado}")
            print(
                "   generate_assets invocado: "
                f"{orquestador.generate_assets.called}"
            )
        destino_log = EV / "log_saneado_pre_gate.txt"
        texto_log = bitacora.getvalue()
        assert "+573001234567" not in texto_log, "el log filtraria el numero completo"
        assert orquestador.generate_assets.called is False
        destino_log.write_text(texto_log, encoding="utf-8")

    details = next(
        g["details"] for g in payload["gate_results"] if g["gate_name"] == "coherence"
    )
    resumen = {
        "score": SCORE,
        "umbral": UMBRAL,
        "veredicto_del_validador": False,
        "passed": decision["passed"],
        "status": decision["status"],
        "blocks_asset_generation": decision["blocks_asset_generation"],
        "generate_proposal": decision["generate_proposal"],
        "culpables_del_pre_gate": decision["guilty_check_names"],
        "failed_check_names_en_el_gate_report": details.get("failed_check_names"),
        "failed_check_messages_en_el_gate_report": details.get("failed_check_messages"),
        "numero_completo_en_el_log": "+573001234567" in texto_log,
        "artefactos": [destino_pre.name, destino_gr.name, destino_log.name],
    }
    (EV / "resumen_escritura.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
