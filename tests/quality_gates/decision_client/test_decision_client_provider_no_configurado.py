"""AC7 / estado 1 de 3 - `NO-CONFIGURADO`: sin proveedor resuelto **no hay decision** (L-PF6).

Cubre un solo estado: ninguno de sus casos provoca `ILEGIBLE` (aqui ni siquiera se llega a un
proveedor que conteste) ni afirma `RESUELTO`. Lo que se prueba es la prohibicion del default: un
`except` que devolviera «la opcion mas probable» o «no» seria leido como una decision del proveedor
y ese fue el mecanismo del dolor falso de L-PF6.
"""

import pytest


def test_sin_la_variable_del_proveedor_falla_y_no_decide(dc, preguntas):
    with pytest.raises(dc.ProveedorNoConfigurado) as exc:
        dc.evaluar("estado", preguntas, {"IAH_DECISION_PROVIDERS_DIR": "/ruta/que/no/existe"})
    assert "IAH_DECISION_PROVIDER" in str(exc.value)
    assert exc.value.motivo_clase == "env-de-proveedor-sin-definir"


def test_sin_directorio_de_proveedores_falla_y_no_decide(dc, preguntas):
    """La ruta buscada se imprime: `AUSENTE` dicho con la letra de `NO-CONFIGURADO` (L-PF10)."""
    with pytest.raises(dc.ProveedorNoConfigurado) as exc:
        dc.evaluar("estado", preguntas, {"IAH_DECISION_PROVIDER": "jev"})
    assert "IAH_DECISION_PROVIDERS_DIR" in str(exc.value)
    assert exc.value.motivo_clase == "env-de-directorio-sin-definir"


def test_un_directorio_que_no_existe_imprime_lo_buscado(dc, preguntas, tmp_path):
    con_busado = tmp_path / "donde-nadie-puso-nada"
    with pytest.raises(dc.ProveedorNoConfigurado) as exc:
        dc.evaluar("estado", preguntas, {"IAH_DECISION_PROVIDER": "jev",
                                        "IAH_DECISION_PROVIDERS_DIR": str(con_busado)})
    assert str(con_busado) in str(exc.value)
    assert exc.value.motivo_clase == "directorio-buscado-no-existe"


def test_un_nombre_no_registrado_lista_los_que_si_lo_estan(dc, preguntas, proveedores_falsos):
    """«No esta» no se escribe como «no hay»: publica los nombres que encontro en la ruta."""
    with pytest.raises(dc.ProveedorNoConfigurado) as exc:
        dc.evaluar("estado", preguntas, {"IAH_DECISION_PROVIDER": "jev-sdk",
                                        "IAH_DECISION_PROVIDERS_DIR": str(proveedores_falsos)})
    assert exc.value.motivo_clase == "nombre-no-esta-en-el-directorio"
    assert "falso-forma" in str(exc.value)


def test_los_tres_motivos_no_colapsan_entre_si(dc, preguntas, tmp_path, proveedores_falsos):
    """R2.9: tres causas distintas del mismo estado, tres `motivo_clase` legibles."""
    casos = {
        "env-de-proveedor-sin-definir": {"IAH_DECISION_PROVIDERS_DIR": str(proveedores_falsos)},
        "env-de-directorio-sin-definir": {"IAH_DECISION_PROVIDER": "jev"},
        "directorio-buscado-no-existe": {"IAH_DECISION_PROVIDER": "jev",
                                        "IAH_DECISION_PROVIDERS_DIR": str(tmp_path / "x")},
    }
    vistos = []
    for esperado, entorno in casos.items():
        with pytest.raises(dc.ProveedorNoConfigurado) as exc:
            dc.evaluar("estado", preguntas, entorno)
        vistos.append(exc.value.motivo_clase)
    assert vistos == list(casos)
    assert len(set(vistos)) == 3


def test_estado_proveedor_publica_el_estado_sin_llamar_a_nadie(dc, proveedores_falsos):
    """La sonda de diagnostico resuelve estados sin despachar: cero red también aqui."""
    est = dc.estado_proveedor({"IAH_DECISION_PROVIDER": "jev-sdk",
                              "IAH_DECISION_PROVIDERS_DIR": str(proveedores_falsos)})
    assert est["provider_status"] == "NO-CONFIGURADO"
    assert est["motivo_clase"] == "nombre-no-esta-en-el-directorio"
    assert est.get("decision") is None and "respuestas" not in est


MARCADOR = "NO-ES-UNA-CLAVE-REAL-PERO-SI-UN-MARCADOR"


def test_un_proveedor_sin_credencial_declara_que_no_la_necesita(dc, proveedores_falsos):
    """`falso-forma` no declara `credencial_env`: presente=False, y no se busca ninguna clave."""
    prov = dc.resolver_proveedor({"IAH_DECISION_PROVIDER": "falso-forma",
                                 "IAH_DECISION_PROVIDERS_DIR": str(proveedores_falsos)})
    est = dc._credencial(prov.get("credencial_env"), {dc.ENV_PROVIDER: "falso-forma"})
    assert est == {"env_var": None, "presente": False,
                   "motivo": "el proveedor no declara credencial"}


def test_con_la_clave_en_el_entorno_solo_se_publica_el_bool(dc):
    """Ni el valor, ni su longitud, ni un prefijo: un parcial revelado tambien es revelado."""
    informada = dc._credencial("IAH_SECRETOS_DE_PRUEBA", {"IAH_SECRETOS_DE_PRUEBA": MARCADOR})
    ausente = dc._credencial("IAH_SECRETOS_DE_PRUEBA", {})
    assert (informada["env_var"], informada["presente"]) == ("IAH_SECRETOS_DE_PRUEBA", True)
    assert ausente["presente"] is False
    volcado = str(informada)
    assert MARCADOR not in volcado
    assert str(len(MARCADOR)) not in volcado
    assert not any(frag in volcado for frag in (MARCADOR[:6], MARCADOR[-6:]))


def test_evaluar_tampoco_filtra_la_clave(dc, preguntas, monkeypatch, proveedores_falsos):
    """El camino completo: una resolucion con la clave en el entorno no la deja en el resultado."""
    monkeypatch.setenv("IAH_SECRETOS_DE_PRUEBA", MARCADOR)
    r = dc.evaluar("estado", preguntas, {"IAH_DECISION_PROVIDER": "falso-forma",
                                        "IAH_DECISION_PROVIDERS_DIR": str(proveedores_falsos),
                                        "IAH_SECRETOS_DE_PRUEBA": MARCADOR})
    assert MARCADOR not in str(r.to_dict())
    assert r.credencial["presente"] is False     # el falso no declara env_var: nada que revelar
