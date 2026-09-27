"""Poblacion S16: prompts de fase archivados y cuantos declaran lectura con la convencion `Lee ...`."""
import pathlib
import re

arch = pathlib.Path(".opencode/plans/Archives")
prompts = sorted(arch.glob("*/05-prompt-inicio-sesion-fase-*.md"))
print(f"prompts de fase bajo Archives/          : {len(prompts)}")

# El generador busca la cadena que empieza por `Lee ` dentro del bloque «Prompt de ejecucion».
con_le = [p for p in prompts if re.search(r"^\s*(?:>\s*)?Lee ", p.read_text(encoding="utf-8",
                                                                                errors="replace"), re.M)]
print(f"prompts con una linea que arranca `Lee `: {len(con_le)}")

# Y cuantos de esos los resolveria el propio generador (los 5 de este plan ya salen en su pack).
vivo = [p for p in con_le if "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20" in p.as_posix()]
print(f"  de ellos, del plan de esta orden      : {len(vivo)}")
