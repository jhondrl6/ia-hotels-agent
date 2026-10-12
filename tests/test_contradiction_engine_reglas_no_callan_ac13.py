"""AC13 (cura N8): las reglas del motor de contradicciones ya no callan sus excepciones.

Hasta esta fase, los **cuatro** sitios de captura del motor tragaban la excepción con un
`print` y devolvían la lista tal cual: `detect_conflicts()` (bloque HARD y bloque SOFT),
`detect_hard_conflicts()` y `detect_soft_conflicts()`. Como `has_hard_conflicts()` es
`len(detect_hard_conflicts(claims)) > 0`, una regla que reventaba producía el mismo verde
que una regla que no encontró nada.

Los tests de este archivo nombran **el sitio** en su causa, para que la cura no pueda
consistir en tapar uno y dejar los otros tres. Lo que NO cubre: el cableado
motor→assessment→gate, que es la deuda `S-CST-1` con dueño Operador (maestro §5). Su
consecuencia declarada: aunque el motor ahora publique `LECTOR_FALLIDO`, el gate blocking
`hard_contradictions` sigue sin poder fallar, así que **el verde del gate no es evidencia
de esta cura**.
"""

import json

import pytest

from data_validation.contradiction_engine import (
    ESTADO_CON_HALLAZGOS,
    ESTADO_LECTOR_FALLIDO,
    ESTADO_SIN_HALLAZGOS,
    SITIO_DETECT_CONFLICTS_HARD,
    SITIO_DETECT_CONFLICTS_SOFT,
    SITIO_DETECT_HARD_CONFLICTS,
    SITIO_DETECT_SOFT_CONFLICTS,
    Claim,
    ContradictionEngine,
)


CAUSA_DE_RUPTURA = "el lector se cayó"


def regla_que_revienta(claims):
    """Regla con nombre: `RuleFailure.regla` tiene que poder citarla."""
    raise RuntimeError(CAUSA_DE_RUPTURA)


@pytest.fixture
def engine():
    return ContradictionEngine()


def claims_whatsapp_contradictorio():
    """Par REAL que atraviesa `_whatsapp_verified_not_visible`: hallazgo legítimo."""
    return [
        Claim(
            claim_id="a",
            category="whatsapp_presence",
            message="WhatsApp verificado en el sitio",
            confidence=0.95,
        ),
        Claim(
            claim_id="b",
            category="whatsapp_presence",
            message="Botón no visible en la home",
            confidence=0.6,
        ),
    ]


def motor_con(engine, grupo, reglas_extra):
    """Monta la lista del grupo: las sanas de producción + la que revienta.

    Se parte de la lista de la INSTANCIA (lo que `_register_*_rules` dejó), no del
    atributo de clase: en la clase está vacía y un test sobre ella certificaría una
    corrida con una sola regla.
    """
    atributo = f"{grupo}_CONFLICT_RULES"
    setattr(engine, atributo, list(getattr(engine, atributo)) + reglas_extra)
    return engine


# ── el tri-estado honesto (R2.9) ─────────────────────────────────────────


def test_una_lectura_sina_sin_conflictos_se_declara_sin_hallazgos(engine):
    report = engine.detect_conflicts([
        Claim(claim_id="a", category="schema_presence", message="Schema detectado", confidence=0.9),
    ])

    estado = engine.estado_reglas(report)
    assert estado["estado"] == ESTADO_SIN_HALLAZGOS
    assert estado["reglas_fallidas"] == 0
    assert estado["reglas_ejecutadas"] == 8
    assert estado["fallas"] == []


def test_una_lectura_sina_con_conflicto_se_declara_con_hallazgos(engine):
    report = engine.detect_conflicts(claims_whatsapp_contradictorio())

    estado = engine.estado_reglas(report)
    assert estado["estado"] == ESTADO_CON_HALLAZGOS
    assert len(report) > 0


# ── los cuatro sitios de captura, por causa ─────────────────────────────


def test_detect_conflicts_bloque_hard_no_traga_la_excepcion(engine, capsys):
    motor_con(engine, "HARD", [regla_que_revienta])

    engine.detect_conflicts([])

    estado = engine.estado_reglas([])
    assert estado["estado"] == ESTADO_LECTOR_FALLIDO
    assert estado["sitios_con_fallo"] == [SITIO_DETECT_CONFLICTS_HARD]
    assert estado["reglas_fallidas"] == 1
    assert captured_sin_stdout(capsys)


def test_detect_conflicts_bloque_soft_no_traga_la_excepcion(engine, capsys):
    motor_con(engine, "SOFT", [regla_que_revienta])

    engine.detect_conflicts([])

    estado = engine.estado_reglas([])
    assert estado["estado"] == ESTADO_LECTOR_FALLIDO
    assert estado["sitios_con_fallo"] == [SITIO_DETECT_CONFLICTS_SOFT]
    assert estado["fallas"][0]["grupo"] == "SOFT"
    assert captured_sin_stdout(capsys)


def test_detect_hard_conflicts_deja_de_devolver_ese_verde(engine, capsys):
    motor_con(engine, "HARD", [regla_que_revienta])

    conflictos = engine.detect_hard_conflicts([])

    estado = engine.estado_reglas(conflictos)
    assert conflictos == []
    assert estado["estado"] == ESTADO_LECTOR_FALLIDO
    assert estado["sitios_con_fallo"] == [SITIO_DETECT_HARD_CONFLICTS]
    assert captured_sin_stdout(capsys)


def test_detect_soft_conflicts_deja_de_devolver_ese_verde(engine, capsys):
    motor_con(engine, "SOFT", [regla_que_revienta])

    conflictos = engine.detect_soft_conflicts([])

    estado = engine.estado_reglas(conflictos)
    assert conflictos == []
    assert estado["estado"] == ESTADO_LECTOR_FALLIDO
    assert estado["sitios_con_fallo"] == [SITIO_DETECT_SOFT_CONFLICTS]
    assert estado["fallas"][0]["grupo"] == "SOFT"
    assert captured_sin_stdout(capsys)


def test_los_cuatro_sitios_son_claves_distintas():
    """Sin identificador por sitio, «una regla falló» no diría cuál rama tragaba."""
    sitios = {
        SITIO_DETECT_CONFLICTS_HARD,
        SITIO_DETECT_CONFLICTS_SOFT,
        SITIO_DETECT_HARD_CONFLICTS,
        SITIO_DETECT_SOFT_CONFLICTS,
    }
    assert len(sitios) == 4


# ── la causa queda escrita, no implícita ────────────────────────────────


def test_la_falla_nombra_regla_excepcion_y_causa(engine):
    motor_con(engine, "HARD", [regla_que_revienta])

    engine.detect_hard_conflicts(claims_whatsapp_contradictorio())

    falla = engine.estado_reglas([])["fallas"][0]
    assert falla["regla"] == "regla_que_revienta"
    assert falla["excepcion"] == "RuntimeError"
    assert falla["causa"] == CAUSA_DE_RUPTURA
    assert falla["sitio"] == SITIO_DETECT_HARD_CONFLICTS


def test_lector_fallido_manda_sobre_los_hallazgos_de_las_reglas_sanas(engine):
    """Con conflictos legítimos Y una regla rota el estado es LECTOR_FALLIDO, no CON_HALLAZGOS."""
    motor_con(engine, "HARD", [regla_que_revienta])

    conflictos = engine.detect_hard_conflicts(claims_whatsapp_contradictorio())

    assert len(conflictos) > 0
    assert engine.estado_reglas(conflictos)["estado"] == ESTADO_LECTOR_FALLIDO


def test_has_hard_conflicts_sin_la_regla_que_revento_no_es_un_falso_verde(engine):
    """El predicado del gate sigue siendo False; lo que cambia es que el estado lo desmiente."""
    motor_con(engine, "HARD", [regla_que_revienta])

    assert engine.has_hard_conflicts([]) is False
    estado = engine.estado_reglas([])
    assert estado["estado"] == ESTADO_LECTOR_FALLIDO
    assert estado["sitios_con_fallo"] == [SITIO_DETECT_HARD_CONFLICTS]


def test_el_report_publica_el_estado_junto_al_conteo_de_hard(engine):
    """Un `hard_conflicts: []` del JSON ya no se lee solo: viaja con su estado de lectura."""
    motor_con(engine, "SOFT", [regla_que_revienta])
    conflictos = engine.detect_conflicts(claims_whatsapp_contradictorio())

    report = json.loads(json.dumps(engine.generate_conflict_report(conflictos), default=str))

    assert report["estado_reglas"]["estado"] == ESTADO_LECTOR_FALLIDO
    assert report["estado_reglas"]["sitios_con_fallo"] == [SITIO_DETECT_CONFLICTS_SOFT]
    assert report["summary"]["hard_conflicts"] > 0


def test_el_estado_se_reinicia_entre_corridas(engine):
    """La falla de la corrida anterior no acusa la siguiente: el estado es por corrida."""
    motor_con(engine, "HARD", [regla_que_revienta])
    engine.detect_hard_conflicts([])
    assert engine.estado_reglas([])["estado"] == ESTADO_LECTOR_FALLIDO

    engine.HARD_CONFLICT_RULES = [
        r for r in engine.HARD_CONFLICT_RULES if r is not regla_que_revienta
    ]
    limpio = engine.detect_conflicts(claims_whatsapp_contradictorio())

    estado = engine.estado_reglas(limpio)
    assert estado["estado"] == ESTADO_CON_HALLAZGOS
    assert estado["reglas_fallidas"] == 0
    assert estado["sitios_con_fallo"] == []


def captured_sin_stdout(capsys) -> bool:
    """El `print` del motor se fue: la cura no puede consistir en seguir hablando por stdout."""
    return capsys.readouterr().out == ""


def test_el_motor_ya_no_imprime_por_stdout():
    """Barrido por literal sobre el módulo: los cuatro `print` de captura desaparecieron."""
    import data_validation.contradiction_engine as motor

    fuente = motor.__file__
    with open(fuente, encoding="utf-8") as f:
        codigo = f.read()

    assert "print(" not in codigo
    assert "Error en regla" not in codigo
