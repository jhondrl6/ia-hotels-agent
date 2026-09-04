"""Pre-flight I1: caza nombres globalesreferenciados que no existen en el modulo.

Usa symtable (stdlib) porque el venv no tiene pyflakes/flake8. Objetivo: la leccion
del plan anterior (L: NameError en rama poco ejercida revierte una corrida unika).
Un nombre cargado desde un scope de funcion, que no es local, no es closure (free),
no esta en globals del modulo y no es builtin => NameError en tiempo de ejecucion.
"""

import builtins
import symtable
import sys

BUILTIN_NAMES = set(dir(builtins)) | {"__file__", "__name__", "__doc__", "__spec__", "__package__", "__loader__", "__builtins__"}
FILES = sys.argv[1:]


def collect_module_names(table):
    names = set()
    for sym in table.get_symbols():
        if sym.is_assigned() or sym.is_imported() or sym.is_namespace():
            names.add(sym.get_name())
        if sym.is_parameter():
            names.add(sym.get_name())
    return names


def walk(table, module_names, path, findings):
    for sym in table.get_symbols():
        # global sin asignacion local y sin binding free (closure) => debe existir en globals/builtins
        if sym.is_referenced() and sym.is_global() and not sym.is_assigned() and not sym.is_imported():
            name = sym.get_name()
            if name not in module_names and name not in BUILTIN_NAMES:
                findings.append((path, table.get_name(), name, sym.get_lineno()))
    for child in table.get_children():
        walk(child, module_names, f"{path}::{child.get_name()}", findings)


all_findings = []
for path in FILES:
    try:
        source = open(path, encoding="utf-8").read()
    except OSError as exc:
        print(f"SKIP {path}: {exc}")
        continue
    try:
        top = symtable.symtable(source, path, "exec")
    except SyntaxError as exc:
        all_findings.append((path, "<module>", f"SYNTAXERROR {exc}", exc.lineno or 0))
        continue
    module_names = collect_module_names(top)
    findings = []
    walk(top, module_names, path, findings)
    all_findings.extend(findings)

if not all_findings:
    print("OK: 0 nombres globales indefinidos en ramas nuevas")
else:
    print(f"ALERTA: {len(all_findings)} referencias posiblemente indefinidas")
    for path, scope, name, lineno in sorted(all_findings):
        print(f"  {path}:{lineno} scope={scope} name={name}")
