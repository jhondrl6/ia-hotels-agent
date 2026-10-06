"""FASE-E — rectificacion de los sellos "sin commit" tras la orden literal del operador.

Convencion heredada de C y practicada por D: el sha y el rango empujado NO se estampen
aqui (seria un sello recursivo por acciones git); se declaran en el sello de FASE-RELEASE.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PLAN = ROOT / ".opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18"

FRASE_ESTADO_D = (
    "**Estado:** COMPLETADA y **commiteada + empujada por orden literal del operador al cierre de la "
    "sesión** (el mandato de implementación no autorizaba el commit: los cinco cortes se sostuvieron sin "
    "él y ese fue el corte que midió R2). El sha y el rango empujado se estampan en el sello documental de "
    "FASE-RELEASE. La orden cubrió commit + L3 + push; la revisión L3 del cierre no arrojó hallazgos."
)

REEMPLAZOS = [
    (
        PLAN / "05-prompt-inicio-sesion-fase-E.md",
        "**Estado:** COMPLETADA 2026-10-06, **sin commit ni push** (el mandato no los autorizaba; los cinco cortes se sostienen sin commit).",
        "**Estado:** COMPLETADA 2026-10-06 y **commiteada + empujada por orden literal del operador** (commit + L3 + push); el mandato de implementación no autorizaba el commit y los cinco cortes se sostuvieron sin él — ese fue el corte que midió R2. El sha y el rango empujado se estampan en el sello de FASE-RELEASE, y la L3 del cierre quedó sin hallazgos.",
        1,
    ),
    (
        PLAN / "06-checklist-implementacion.md",
        "**COMPLETADA 2026-10-06, SIN COMMIT** (mandato sin autorizacion de commit; los cinco cortes se sostienen sin el).",
        "**COMPLETADA 2026-10-06, commiteada y empujada por orden literal del operador** (el mandato de implementación no autorizaba el commit; sha y rango se estampan en el sello de RELEASE; L3 del cierre sin hallazgos).",
        1,
    ),
    (
        PLAN / "dependencias-fases.md",
        "**COMPLETADA 2026-10-06, SIN COMMIT** — AC9/AC10/AC11/AC12 VERIFICADOS OFFLINE",
        "**COMPLETADA 2026-10-06, commiteada y empujada por orden literal del operador** (sha y rango al sello de RELEASE; L3 sin hallazgos) — AC9/AC10/AC11/AC12 VERIFICADOS OFFLINE",
        1,
    ),
    (
        ROOT / "evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E/resultados-y-observaciones.md",
        "**Estado:** COMPLETADA, **sin commit** (el mandato no autorizaba el commit; los cinco cortes se\nsostienen sin él y ese es el corte que midió R2).",
        FRASE_ESTADO_D,
        1,
    ),
    (
        ROOT / "evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E/resultados-y-observaciones.md",
        "1. **Commit** (producto + tests + evidencia) y **push**: no autorizados por el mandato.",
        "1. ~~**Commit** (producto + tests + evidencia) y **push**: no autorizados por el mandato.~~ "
        "**CERRADO en la misma sesión**: orden literal del operador «Git Commit + L3 + Push». El sha y el rango "
        "empujado se estampan en el sello documental de FASE-RELEASE (decisión de C: no abrir sellos recursivos "
        "por acciones git). La revisión L3 corrió sobre los commits de la fase y no arrojó hallazgos.",
        1,
    ),
]


def main() -> None:
    for ruta, old, new, esperado in REEMPLAZOS:
        texto = ruta.read_text(encoding="utf-8")
        vistos = texto.count(old)
        if vistos != esperado:
            raise SystemExit(f"ANCLA {ruta.name}: {vistos} ocurrencias, se exigian {esperado} :: {old[:60]!r}")
        ruta.write_text(texto.replace(old, new), encoding="utf-8", newline="")
        print(f"[OK] {ruta.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
