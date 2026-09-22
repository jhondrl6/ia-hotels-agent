"""AC9 - extensibilidad **probada**, no prometida: anadir un segundo proveedor cuesta un archivo.

Ningun proveedor de pago se activa en este plan (contrato §Regla de cero red; deuda **D7**). Lo que
se certifica aqui es la geometria de la costura: se copia la puerta y sus proveedores falsos a un
directorio temporal, se anade **un** archivo nuevo, y se mide por sha256 que ningun otro archivo se
toco - y ademas que los dos proveedores se despachan por la misma puerta y contestan distinto, para
que el «1» no pueda salir de una costura que en realidad devuelve siempre el mismo modulo.

La comparacion proveedor contra proveedor **no** es de esta fase: con un solo proveedor real no hay
eleccion que medir, y exigirla producira un `NO-EJERCITADO` que certifica humo. Es la deuda D7.
"""

import json


def test_anadir_un_segundo_proveedor_toca_un_archivo(dc, proveedores_falsos, raiz_repo):
    medida = dc.medir_costura(proveedores_falsos, raiz_repo)
    assert medida["files_changed_to_add_provider"] == 1, {
        k: medida[k] for k in ("archivos_tocados", "agregados", "modificados")}
    assert medida["agregados"] == ["falsos_proveedores/falso_segundo.py"]
    assert medida["modificados"] == [], (
        f"la costura obligo a tocar {medida['modificados']} (incluida la propia puerta): no es una "
        "puerta, es un registro central")


def test_los_dos_proveedores_se_despachan_por_la_misma_puerta(dc, proveedores_falsos, raiz_repo):
    medida = dc.medir_costura(proveedores_falsos, raiz_repo)
    assert medida["costura_funciona_con_ambos"] == ["falso-forma", "falso-segundo-medido"]
    assert medida["provider_status"] == ["RESUELTO", "RESUELTO"]
    assert medida["los_dos_despachan_respuestas_distintas"] is True, (
        "los dos proveedores contestaron igual: la costura no despacho al segundo, repitio el primero")


def test_el_arbol_del_repo_no_se_toca_para_medir(dc, proveedores_falsos, raiz_repo):
    """La medicion es en copia: si escribiera en el arbol, el «1» contaria archivos de la propia prueba."""
    antes = {p: p.stat().st_mtime_ns for p in list(proveedores_falsos.glob("*.py"))
             + [raiz_repo / "scripts" / "decision_client.py"]}
    medida = dc.medir_costura(proveedores_falsos, raiz_repo)
    despues = {p: p.stat().st_mtime_ns for p in antes}
    assert medida["coverage_basis"]["corte"].startswith("copias temporales")
    assert antes == despues, "la medicion toco archivos reales"


def test_la_prueba_de_extensibilidad_declara_lo_que_no_cuenta(dc, proveedores_falsos, raiz_repo):
    """El `1` es de la frontera de produccion; los tests paralelos se publican, no se esconden."""
    medida = dc.medir_costura(proveedores_falsos, raiz_repo)
    paralelos = medida["archivos_de_test_paralelos"]
    assert paralelos["valor"] == 1
    assert "no se esconde" in paralelos["nota"]
    assert medida["coverage_basis"]["instrumento"] == "sha256 por archivo + despacho real por la costura"
    assert medida["coverage_basis"]["comando"].startswith("python scripts/decision_client.py --costura")
    assert medida["coverage_basis"]["medido_el"]


def test_costura_json_publica_su_clave_con_su_poblacion(dc, proveedores_falsos, raiz_repo):
    medida = dc.medir_costura(proveedores_falsos, raiz_repo)
    volcado = json.dumps(medida, ensure_ascii=False)
    assert "files_changed_to_add_provider" in volcado
    b = medida["coverage_basis"]
    assert b["archivos_base_antes"] == ["decision_client.py",
                                        "falsos_proveedores/falso_forma.py",
                                        "falsos_proveedores/falso_ilegible.py"]
    assert b["archivos_base_despues"] == b["archivos_base_antes"] + [
        "falsos_proveedores/falso_segundo.py"]
    assert b["proveedor_base_usado"] == "falso-forma"
    assert b["directorio_base"].endswith("falsos_proveedores")
