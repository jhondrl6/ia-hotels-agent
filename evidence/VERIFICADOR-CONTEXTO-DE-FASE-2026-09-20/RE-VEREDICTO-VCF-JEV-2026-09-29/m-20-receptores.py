import importlib.util
import os
from pathlib import Path

ROOT = Path(os.getcwd())
spec = importlib.util.spec_from_file_location("vw", os.path.join(ROOT, "scripts", "validate_wiring.py"))
vw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vw)

rep = vw.construir_reporte(ROOT)
cob = rep.get("cobertura", {})
print("comando logico: validate_wiring.construir_reporte(raiz), la MISMA llamada del fixture reporte_repo")
print("archivos_en_alcance                    = %s" % cob.get("archivos_en_alcance"))
print("archivos_excluidos_por_rol             = %s" % cob.get("archivos_excluidos_por_rol"))
print("receptores_no_resueltos_en_produccion  = %s" % cob.get("receptores_no_resueltos_en_produccion"))
print("")
mala = [r for r in rep.get("poblacion", [])
        if r.get("clasificacion") == "RECEPTOR_NO_RESUELTO" and not r.get("en_tests")]
print("RECEPTORES_NO_RESUELTOS FUERA DE TESTS: %d" % len(mala))
bajo_tmp = [r for r in mala if str(r.get("archivo", "")).replace("\\", "/").startswith("tmp_test/")]
print("  de los cuales caen bajo tmp_test/    : %d" % len(bajo_tmp))
print("  de los cuales NO caen bajo tmp_test/ : %d" % (len(mala) - len(bajo_tmp)))
for r in mala:
    print("  %-78s linea=%-6s receptor=%s" % (r.get("archivo"), r.get("linea"), r.get("receptor")))
print("")
print("El aserto del test exige 0 y lee %d: la diferencia es la poblacion que descubre el walks"
      % len(mala))
print("sobre un entorno virtual ajeno al arbol. tmp_test esta en .gitignore y no tiene rutas")
print("versionadas (crudo 20- secciones 4), asi que el rojo no reproduce en un clon limpio.")
