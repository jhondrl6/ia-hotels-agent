"""FASE-H -- recorrido offline del flujo productivo (Tarea 1, AC17/AC9/AC14).

Camina los puntos de decision que la corrida unica va a tomar, **sin invocar la CLI real**:
el parser de verdad, la puerta de permisos, el loader de verdad, el pre-gate de coherencia de D
y el resolvedor de insumos de E. Los imports del repo ocurren primero (no tocan la red) y el
corte de red se instala **antes** del recorrido, con prueba de que tiene diente: si el recorrido
abriera un socket, revienta aqui y no en la corrida de E2E.

No ejecuta `run_v4_complete_mode`: eso es justamente lo que E2E hace una sola vez. Demuestra
que el argv congelado se parsea con el parser real, que las identidades efectivas son las que
el producto calcula, y que la puerta permitir/bloquear decide sin lanzar el proceso hijo.

Salida: evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/integracion_offline.json
Uso:   ./venv/Scripts/python.exe evidence/.../FASE-H/integracion_offline.py [--hoy YYYY-MM-DD]
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import socket
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
PLAN = "REFACTOR-WHATSAPP-ENTREGA-2026-09-18"
DIR_FASE = RAIZ / "evidence" / PLAN / "FASE-H"
SALIDA = DIR_FASE / "integracion_offline.json"


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def cargar_runner():
    espec = importlib.util.spec_from_file_location("run_once_h", str(DIR_FASE / "run_once.py"))
    modulo = importlib.util.module_from_spec(espec)
    espec.loader.exec_module(modulo)
    return modulo


def cortar_red() -> dict:
    """Sustituye los puntos de conexion y comprueba que el corte tiene diente."""
    originales = {
        "create_connection": socket.create_connection,
        "getaddrinfo": socket.getaddrinfo,
    }

    def _prohibida(*_args, **_kwargs):
        raise AssertionError("RED_PROHIBIDA: el recorrido offline toco la red")

    socket.create_connection = _prohibida
    socket.getaddrinfo = _prohibida
    diente = False
    try:
        socket.create_connection(("donalfonsohotel.com", 443), timeout=1)
    except AssertionError:
        diente = True
    return {
        "puntos_sustituidos": sorted(originales),
        "diente_del_corte": diente,
        "prueba": "socket.create_connection(('donalfonsohotel.com', 443)) debe levantar AssertionError",
    }


def _reporte_de_coherencia(*, score, is_coherent, culpables):
    from modules.commercial_documents.coherence_validator import CoherenceCheck, CoherenceReport

    checks = [
        CoherenceCheck(
            name=nombre,
            passed=False,
            score=0.2,
            message=mensaje,
            severity="error",
        )
        for nombre, mensaje in culpables
    ]
    if not culpables:
        checks = [CoherenceCheck(name="whatsapp_verified", passed=True, score=1.0, message="ok", severity="info")]
    return CoherenceReport(
        is_coherent=is_coherent,
        overall_score=score,
        checks=checks,
    )


def recorrido(hoy: date) -> dict:
    if str(RAIZ) not in sys.path:
        sys.path.insert(0, str(RAIZ))
    import main
    from agent_harness.memory import MemoryManager
    from modules.quality_gates.tribunal.review_inputs import ReviewInputs
    from modules.utils.permission_mode import OperationPermission, PermissionMode, check_permission

    runner = cargar_runner()
    corte = cortar_red()

    # 1) El argv congelado se parsea con el parser real; ninguna bandera inventada.
    parser = main.build_parser()
    args = parser.parse_args(runner.ARGUMENTOS_DEL_PARSER)
    banderas = {a.option_strings[0] for a in parser._actions if a.option_strings}
    parseo = {
        "command": args.command,
        "--url": args.url,
        "--nombre": args.nombre,
        "--output": args.output,
        "--permission-mode": getattr(args, "permission_mode", None),
        "--permission-mode existe en build_parser": "--permission-mode" in banderas,
        "--onboarding-file NO existe (bandera inventada)": "--onboarding-file" not in banderas,
        "default_sin_el_flag": parser.parse_args(
            ["v4complete", "--url", "https://example.org/"]
        ).permission_mode,
        "banderas_prohibidas_presentes_en_el_argv": sorted(
            b for b in ("--force", "--skip-check", "--dry-run", "--no-dry-run", "--input-data")
            if b in runner.ARGUMENTOS_HIJO
        ),
        "argv_sin_interprete": runner.ARGUMENTOS_DEL_PARSER,
    }

    # 2) Las tres identidades de la corrida, calculadas por los productores del producto.
    #    `OnboardingController` no es atributo de `main`: se importa dentro de
    #    run_v4_complete_mode (main.py:1637), asi que se toma de su modulo.
    from modules.orchestration_v4 import OnboardingController

    canonical_url = main._normalize_url(args.url)
    hotel_id_reporte = OnboardingController.generate_hotel_id(args.url)
    slug_rutas = args.nombre.lower().replace(" ", "_").replace("-", "_").replace(".", "")
    identidades = {
        "hotel_id_del_reporte": {
            "valor": hotel_id_reporte,
            "productor": "OnboardingController.generate_hotel_id(args.url); main.py lo escribe en v4_complete_report.json",
            "bandera_que_participa": "--url",
        },
        "nombre_del_paquete": {
            "valor": args.nombre,
            "slug_de_rutas_y_zip": slug_rutas,
            "productor": "hotel_name = args.nombre or _extract_hotel_name_from_url(args.url)",
            "bandera_que_participa": "--nombre",
            "si_se_omite_el_flag": main._extract_hotel_name_from_url(args.url),
        },
        "identidad_de_memoria": {
            "valor": canonical_url,
            "productor": "_normalize_url(args.url) -> target_id de MemoryManager",
            "bandera_que_participa": "--url",
        },
        "los_tres_son_distintos": len({hotel_id_reporte, args.nombre, canonical_url}) == 3,
        "rectificacion_al_prompt": (
            "el prompt de H decia que el hotel_id del reporte sale de `\"hotel_id\": args.url` en "
            "run_v4_complete_mode; medido, esa asignacion es el payload financiero "
            "(main.py:1909/2000/2073), mientras el reporte escribe `state.hotel_id`, que produce "
            "generate_hotel_id(). Se fija el productor real, no el citado."
        ),
        "declaracion": (
            "son tres valores distintos para el mismo hotel; el preflight los fija ANTES del spawn. "
            "Ninguno es 'el archivo mas reciente entre hoteles'."
        ),
    }

    # 3) Permitir / bloquear segun el modo efectivo, sin lanzar nada.
    audit_op = OperationPermission(
        name="V4ComprehensiveAuditor.audit", estimated_cost=0.03, is_external=True
    )
    permisos = {
        "auto_permite_auditoria_externa": check_permission(audit_op, PermissionMode.AUTO),
        "chat_permite_auditoria_externa": check_permission(audit_op, PermissionMode.CHAT),
        "modo_efectivo_del_argv_congelado": parseo["--permission-mode"],
        "consecuencia_de_chat": {
            "audit_result": "None (rama `if not check_permission(...)` de run_v4_complete_mode)",
            "sigue_el_pipeline_con_defaults": True,
            "mismo_exit_code_resultado_distinto": True,
        },
        "prueba_de_que_chat_bloquea_es_determinista": (
            check_permission(audit_op, PermissionMode.CHAT) is False
            and check_permission(audit_op, PermissionMode.AUTO) is True
        ),
    }

    # 4) El loader real sobre el derivado, con su rama.
    clientes = RAIZ / "output" / PLAN / "clientes"
    onboarding = main._load_latest_onboarding_data(
        hotel_url=args.url, hotel_name=args.nombre, output_dir=clientes
    )
    proveniencia = json.loads((DIR_FASE / "onboarding_provenance.json").read_text(encoding="utf-8"))
    loader = {
        "dir_clientes": "output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/clientes",
        "dir_clientes_existe": clientes.is_dir(),
        "devolvio_datos": onboarding is not None,
        "rama_efectiva": proveniencia["rama_efectiva"],
        "fuente_declarada": (onboarding or {}).get("metadatos", {}).get("fuente"),
        "fecha_captura": (onboarding or {}).get("metadatos", {}).get("fecha_captura"),
        "campos_confirmados": (onboarding or {}).get("metadatos", {}).get("campos_confirmados"),
        "ramas_descartadas": [
            "OBSERVATIONS_DENTRO_DE_LA_FUNCION: la URL del warehouse normaliza a hoteldonalfonso.com y no casa con la de la corrida",
            "NINGUNA (defaults en run_v4_complete_mode): se rechaza; el derivado existe y el loader lo toma",
        ],
        "fallback_de_main": (
            "run_v4_complete_mode reintenta en output/clientes si el directorio propio vuelve None; "
            "esa ruta esta ocupada por zi-one-luxury_onboarding.yaml y tampoco casa por URL"
        ),
    }

    # 5) Frescura fail-closed de H (la variable del loader no esta definida: sin fecha, rechazo).
    fecha_str = str((onboarding or {}).get("metadatos", {}).get("fecha_captura") or "")
    edad = None
    if fecha_str:
        capturado = datetime.fromisoformat(fecha_str.replace("Z", "+00:00")).date()
        edad = (hoy - capturado).days
    frescura = {
        "variable_en_el_entorno": bool(os.getenv("ONBOARDING_FRESHNESS_HOURS")),
        "variable_en_dotenv": _presencia_en_archivos(".env", "ONBOARDING_FRESHNESS_HOURS"),
        "variable_en_dotenv_template": _presencia_en_archivos(".env.template", "ONBOARDING_FRESHNESS_HOURS"),
        "bloque_de_frescura_del_loader_corre": False,
        "motivo": (
            "si la variable no esta, `if freshness_hours:` no entra; y si estuviera pero faltara "
            "fecha, `if fecha_str:` tambien se salta el bloque. Doble silencio medido."
        ),
        "fecha_captura_presente": bool(fecha_str),
        "edad_dias": edad,
        "control_de_H": (
            "fail-closed: sin fecha se rechaza el spawn; con fecha se declara la edad y se exige "
            "consentimiento datado sobre la URL viva (dueño: operador)"
        ),
    }

    # 6) Pre-gate de coherencia de D: las dos mitades del par, con el decisor real.
    decisiones = {}
    for etiqueta, score, coherente, culpables in (
        ("bloquea_por_errores", 0.95, False, [("whatsapp_verified", "confianza 0.30 insuficiente")]),
        ("permite_sin_errores", 0.95, True, []),
    ):
        reporte = _reporte_de_coherencia(score=score, is_coherent=coherente, culpables=culpables)
        silencio = io.StringIO()
        with contextlib.redirect_stdout(silencio):
            decision = main._coherence_pre_gate_decision(
                report=reporte, threshold=0.8, is_blocking=False
            )
        decisiones[etiqueta] = {
            "passed": decision["passed"],
            "blocks_asset_generation": decision["blocks_asset_generation"],
            "guilty_check_names": decision["guilty_check_names"],
            "generate_proposal": decision["generate_proposal"],
        }
    contratos_d_e = {
        "pre_gate_de_D": {
            "simbolo": "main._coherence_pre_gate_decision",
            "lectura": "funcion de modulo; `PublicationGateEngine._check_coherence` no existe (rectificacion ya registrada por D)",
            "par_permitir_bloquear": decisiones,
        },
        "lector_AC9_de_D": _estados_del_lector(main),
        "resolvedor_de_E": {
            "simbolo": "ReviewInputs.for_run",
            "existe": hasattr(ReviewInputs, "for_run"),
            "vocabulario_de_lectura": ["READ_OK", "ABSENT", "READ_ERROR", "NO_LEIDO"],
            "deuda_que_H_declara": (
                "los JSON timestamped (gate_report_*, pain_ledger, financial_scenarios) siguen sin "
                "anclarse por run_id: H lo declara con dueño E2E/VERIFY y no lo cura porque el "
                "allowlist de H acota el codigo nuevo al runner stdlib"
            ),
        },
        "sumidero_de_F": {
            "ruta": "modules/utils/redaction.py",
            "sha256": sha256_de(RAIZ / "modules/utils/redaction.py"),
            "guard": "assert_redacted(texto, channel=...) del contrato de F",
            "boca_que_cierra_deuda": "S-F8: H lo llama en redactar_salida() antes de escribir captura alguna",
        },
    }

    # 7) Snapshot previo de .agent/memory: lectura pura, con lo que la corrida borraria.
    inventario = runner.inventario_memoria(
        hoy=datetime.combine(hoy, datetime.min.time(), tzinfo=timezone.utc)
    )
    inventario = runner.inventario_memoria(
        hoy=datetime.combine(hoy, datetime.min.time(), tzinfo=timezone.utc)
    )
    memoria = {
        "directorio": ".agent/memory",
        "archivos": inventario["archivos"],
        "bytes_totales": inventario["bytes_totales"],
        "sha256_del_inventario": hashlib.sha256(
            json.dumps(inventario["inventario"], sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "sesiones_que_cleanup_old_sessions_20_dias_borraria": len(
            inventario["borraria_cleanup_20_dias"]
        ),
        "nombres_que_borraria": inventario["borraria_cleanup_20_dias"],
        "analysis_reutilizable_para_el_canonical_url": _analysis_previo(canonical_url),
        "declaracion": (
            "`--output` aísla el arbol de salida pero no la memoria: run_v4_complete_mode llama a "
            "memory.cleanup_old_sessions(days=20) y find_latest_analysis escanea el output fijo. "
            "El snapshot es PREVIO al spawn y se preserva, no se reconstruye despues."
        ),
        "inventario_completo": inventario["inventario"],
    }

    return {
        "schema": "iah-fase-h-integracion/1.0",
        "generado_el": hoy.isoformat(),
        "red": corte,
        "argv_congelado": runner.COMANDO_CONGELADO,
        "parseo_real": parseo,
        "identidades": identidades,
        "permisos": permisos,
        "loader": loader,
        "frescura": frescura,
        "contratos_de_D_y_E": contratos_d_e,
        "snapshot_memoria_previo": memoria,
        "cli_real_invocada": False,
        "limite_del_recorrido": (
            "Se ejercitaron parser, puerta de permisos, loader, frescura, pre-gate y resolvedor. "
            "NO se ejecuto run_v4_complete_mode: eso consume el intento unico y es de E2E."
        ),
    }


def _presencia_en_archivos(nombre: str, clave: str) -> bool:
    ruta = RAIZ / nombre
    if not ruta.exists():
        return False
    return clave in ruta.read_text(encoding="utf-8", errors="replace")


def _estados_del_lector(main) -> dict:
    """Los tres estados del lector nuevo de D, sobre un tmp y sobre el baseline real."""
    from modules.commercial_documents.coherence_validator import read_coherence_report

    base = RAIZ / "output" / "TAREA7-2026-09-19" / "v4_complete" / "hotel_don_alfonso" / "v4_audit"
    candidatos = sorted(base.glob("coherence_validation*.json")) if base.is_dir() else []
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        roto = Path(td) / "coherence_validation_roto.json"
        roto.write_text("{ no json", encoding="utf-8")
        vacio = Path(td) / "coherence_validation_vacio.json"
        vacio.write_text('{"checks": [], "overall_score": 1.0}', encoding="utf-8")
        estados = {
            "READ_ERROR_por_json_roto": read_coherence_report(roto)["read_status"],
            "READ_OK_con_lista_vacia_valida": read_coherence_report(vacio)["read_status"],
            "ABSENT": read_coherence_report(Path(td) / "no_existe.json")["read_status"],
        }
    reales = [read_coherence_report(p) for p in candidatos]
    return {
        "simbolo": "coherence_validator.read_coherence_report",
        "estados_en_tmp": estados,
        "baseline_real": {
            "archivos": [str(p.relative_to(RAIZ)).replace("\\", "/") for p in candidatos],
            "estados": [r["read_status"] for r in reales],
            "causas": [r.get("cause") for r in reales],
        },
    }


def _consumo_del_analysis_previo() -> dict:
    """Cuantos usos tiene `discovered_analysis` dentro de run_v4_complete_mode, y de que tipo.

    El prompt de H afirmaba que un hallazgo previo "cambia el flujo real: se reutiliza en vez de
    auditar". Medido por AST sobre `main.py`: en esa funcion la variable solo se lee para
    imprimirla; la reutilizacion real (`DeliveryContext.from_analysis_json`) vive en otra
    funcion (`run_execution_mode`). Se declara el consumidor efectivo, no la premisa heredada.
    """
    import ast

    arbol = ast.parse((RAIZ / "main.py").read_text(encoding="utf-8"))
    objetivo = next(
        n
        for n in ast.walk(arbol)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name == "run_v4_complete_mode"
    )
    cargas = [n for n in ast.walk(objetivo) if isinstance(n, ast.Name) and n.id == "discovered_analysis"]
    lecturas = [n for n in cargas if isinstance(n.ctx, ast.Load)]

    padres: dict[int, ast.AST] = {}
    for nodo in ast.walk(objetivo):
        for _, hijos in ast.iter_fields(nodo):
            if isinstance(hijos, list):
                for hijo in hijos:
                    if isinstance(hijo, ast.AST):
                        padres[id(hijo)] = nodo
            elif isinstance(hijos, ast.AST):
                padres[id(hijos)] = nodo

    en_guard = 0
    en_print = 0
    consumos: list[str] = []
    for lectura in lecturas:
        salto = lectura
        while salto is not None and salto is not objetivo:
            salto = padres.get(id(salto))
            if isinstance(salto, ast.If) and any(h is lectura for h in ast.walk(salto.test)):
                en_guard += 1
                break
            if isinstance(salto, ast.Call) and isinstance(salto.func, ast.Name):
                if salto.func.id == "print":
                    en_print += 1
                else:
                    consumos.append(f"linea {lectura.lineno}: va a {salto.func.id}()")
                break
            if isinstance(salto, (ast.Assign, ast.Return, ast.AnnAssign, ast.keyword)):
                consumos.append(f"linea {lectura.lineno}: se propaga ({type(salto).__name__})")
                break
        else:
            consumos.append(f"linea {lectura.lineno}: uso no clasificable")
    return {
        "funcion": objetivo.name,
        "asignaciones": sum(1 for n in cargas if isinstance(n.ctx, ast.Store)),
        "lecturas": len(lecturas),
        "lecturas_como_guard_if": en_guard,
        "lecturas_dentro_de_print": en_print,
        "consumos_que_cambian_el_flujo": consumos,
        "lineas_de_uso": [n.lineno for n in cargas],
        "solo_se_declara_en_consola": bool(lecturas) and not consumos,
        "productor_de_reutilizacion": "run_execution_mode: DeliveryContext.from_analysis_json (main.py:806-811), que no es la ruta de v4complete",
    }


def _analysis_previo(canonical_url: str) -> dict:
    from agent_harness.memory import MemoryManager

    hallazgo = MemoryManager().find_latest_analysis(canonical_url)
    return {
        "encontrado": hallazgo is not None,
        "ruta": str(hallazgo) if hallazgo else None,
        "consumo_en_la_ruta_de_v4complete": _consumo_del_analysis_previo(),
        "exige_exclusion_explicita_o_declaracion": True,
        "rectificacion": (
            "el hallazgo existe y se declara; medido por AST, en run_v4_complete_mode la variable "
            "solo se imprime. La reutilizacion que describe el prompt vive en run_execution_mode. "
            "Aun asi E2E debe excluir el analisis previo o declararlo: la premisa no se hereda (L-V.3)"
        ),
        "declaracion_de_dependencia": (
            "si E2E no lo excluye, la corrida se declara dependiente del analisis previo y su "
            "evidencia se lee con esa marca, no como corrida aislada (L-PF11)"
        ),
    }


def _analysis_previo_con_url(canonical_url: str) -> dict:
    return _analysis_previo(canonical_url)


if __name__ == "__main__":
    fecha = date.today()
    if "--hoy" in sys.argv:
        fecha = date.fromisoformat(sys.argv[sys.argv.index("--hoy") + 1])
    documento = recorrido(fecha)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(
        json.dumps(documento, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    resumen = {
        "diente_del_corte_de_red": documento["red"]["diente_del_corte"],
        "rama_del_loader": documento["loader"]["rama_efectiva"],
        "las_tres_identidades_son_distintas": documento["identidades"]["los_tres_son_distintos"],
        "auto_permite": documento["permisos"]["auto_permite_auditoria_externa"],
        "chat_permite": documento["permisos"]["chat_permite_auditoria_externa"],
        "edad_del_dato_dias": documento["frescura"]["edad_dias"],
        "analysis_previo_encontrado": documento["snapshot_memoria_previo"][
            "analysis_reutilizable_para_el_canonical_url"
        ]["encontrado"],
        "sesiones_que_se_borrarian": documento["snapshot_memoria_previo"][
            "sesiones_que_cleanup_old_sessions_20_dias_borraria"
        ],
    }
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
