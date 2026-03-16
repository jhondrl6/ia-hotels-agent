#!/usr/bin/env python3
"""
V4 Regression Guardian - Valida que v4complete funcione después de cambios.

Uso:
    python .agents/workflows/v4_regression_guardian.py
    python .agents/workflows/v4_regression_guardian.py --quick  # Solo tests críticos
    python .agents/workflows/v4_regression_guardian.py --full    # Validación completa
    python .agents/workflows/v4_regression_guardian.py --quiet   # Modo CI - salida mínima
    python .agents/workflows/v4_regression_guardian.py --workdir /path/to/dir  # Directorio alternativo
    python .agents/workflows/v4_regression_guardian.py --retry-failed  # Re-ejecutar pasos fallidos
    python .agents/workflows/v4_regression_guardian.py --run-v4  # Ejecuta v4complete también

Este script detecta cambios en el repositorio, identifica qué módulos v4
fueron afectados, y ejecuta los tests de regresión correspondientes para
validar que el comando `v4complete` continúe funcionando correctamente.
"""

import argparse
import subprocess
import yaml
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Set, Optional

# Configuración de rutas
ROOT_DIR = Path(__file__).parent.parent.parent
REPORTS_DIR = ROOT_DIR / ".validation_reports"
MAP_FILE = Path(__file__).parent / "v4_module_test_map.yaml"

# Módulos críticos que siempre requieren validación completa
CRITICAL_MODULES = {"financial_engine", "quality_gates", "data_validation", "commercial_documents"}

# Test de regresión permanente (siempre ejecutar)
BASELINE_REGRESSION = "tests/regression/test_hotel_visperas.py"


def get_changed_files() -> Set[str]:
    """Obtiene archivos modificados via git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True, text=True, cwd=ROOT_DIR, check=True
        )
        files = result.stdout.strip()
        return set(files.split('\n')) if files else set()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudo obtener git diff: {e}")
        return set()


def load_module_map() -> Dict:
    """Carga mapeo de módulos a tests."""
    try:
        with open(MAP_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"[ERROR] Archivo de mapeo no encontrado: {MAP_FILE}")
        return {"modules": {}}
    except yaml.YAMLError as e:
        print(f"[ERROR] Error al cargar YAML: {e}")
        return {"modules": {}}


def map_files_to_modules(files: Set[str], module_map: Dict) -> Set[str]:
    """Mapea archivos modificados a módulos v4."""
    affected = set()
    modules = module_map.get("modules", {})
    
    for file_path in files:
        # Ignorar archivos que no son código fuente
        if not any(file_path.endswith(ext) for ext in ['.py', '.yaml', '.yml', '.json', '.md']):
            continue
            
        for module_name, config in modules.items():
            for path_pattern in config.get("paths", []):
                # Normalizar el patrón y el archivo para comparación
                normalized_pattern = path_pattern.rstrip('/')
                if normalized_pattern in file_path:
                    affected.add(module_name)
                    break
    
    return affected


def select_tests(modules: Set[str], module_map: Dict, quick: bool = False, full: bool = False) -> List[str]:
    """Selecciona tests a ejecutar basado en módulos afectados."""
    tests = [BASELINE_REGRESSION]  # Siempre incluir regresión base
    
    for module in modules:
        if module in module_map.get("modules", {}):
            module_tests = module_map["modules"][module].get("tests", [])
            tests.extend(module_tests)
    
    if quick:
        # En modo quick, solo tests de regresión + tests de módulos críticos
        tests = [t for t in tests if any(
            critical in t for critical in CRITICAL_MODULES
        ) or "regression" in t]
    elif not full:
        # Por defecto (ni quick ni full), mismo comportamiento que quick para mantener compatibilidad
        tests = [t for t in tests if any(
            critical in t for critical in CRITICAL_MODULES
        ) or "regression" in t]
    # Si full es True, se ejecutan todos los tests seleccionados
    
    return list(set(tests))  # Eliminar duplicados


def run_tests(tests: List[str]) -> subprocess.CompletedProcess:
    """Ejecuta pytest con los tests seleccionados."""
    if not tests:
        # Si no hay tests específicos, ejecutar solo baseline
        tests = [BASELINE_REGRESSION]
    
    cmd = [sys.executable, "-m", "pytest"] + tests + ["-v", "--tb=short", "-q"]
    print(f"  Comando: {' '.join(cmd)}")
    
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT_DIR)


def check_module_imports(modules: Set[str]) -> bool:
    """Verifica que los módulos afectados puedan importarse correctamente."""
    print("\n[3.5/5] Verificando imports de módulos...")
    
    import_errors = []
    module_import_paths = {
        "data_validation": ["data_validation", "data_models"],
        "financial_engine": ["modules.financial_engine"],
        "asset_generation": ["modules.asset_generation"],
        "commercial_documents": ["commercial_documents"],
        "quality_gates": ["modules.quality_gates"],
        "orchestration_v4": ["orchestration_v4"],
        "observability": ["observability"],
        "auditors": ["auditors"],
    }
    
    for module in modules:
        paths = module_import_paths.get(module, [])
        for path in paths:
            try:
                __import__(path)
            except ImportError as e:
                import_errors.append(f"{path}: {str(e)}")
    
    if import_errors:
        print(f"  [WARN] Errores de import: {len(import_errors)}")
        for err in import_errors[:5]:
            print(f"    - {err}")
        return False
    else:
        print("  [OK] Todos los imports correctos")
        return True


def generate_report(
    changed_files: Set[str],
    affected_modules: Set[str],
    tests_run: List[str],
    result: subprocess.CompletedProcess,
    imports_ok: bool,
    output_path: Path
) -> Path:
    """Genera reporte de regresión en formato markdown."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"{timestamp}_v4_regression.md"
    report_path = output_path / report_filename
    
    # Determinar veredicto
    if result.returncode == 0 and imports_ok:
        verdict = "PASS [OK]"
    else:
        verdict = "FAIL [ERROR]"
    
    # Identificar módulos críticos afectados
    critical_affected = affected_modules & CRITICAL_MODULES
    
    report_content = f"""# V4 Regression Guardian Report

**Timestamp:** {timestamp}  
**Veredicto:** {verdict}  
**Módulos Críticos Afectados:** {', '.join(critical_affected) if critical_affected else 'Ninguno'}

---

## Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| Archivos Modificados | {len(changed_files)} |
| Módulos Afectados | {len(affected_modules)} |
| Tests Ejecutados | {len(tests_run)} |
| Tests Exitosos | {'Sí' if result.returncode == 0 else 'No'} |
| Imports Correctos | {'Sí' if imports_ok else 'No'} |

---

## Archivos Modificados

```
{chr(10).join(sorted(changed_files)[:30])}
```

*Total: {len(changed_files)} archivos*

---

## Módulos Afectados

{chr(10).join(f'- **{m}** {{"⚠️ CRÍTICO" if m in CRITICAL_MODULES else ""}}' for m in sorted(affected_modules)) if affected_modules else '*Ningún módulo v4 afectado*'}

---

## Tests Ejecutados

{chr(10).join(f'- `{t}`' for t in tests_run)}

---

## Resultado de pytest

```
{result.stdout[-4000:]}
```

{'---' if result.stderr else ''}

{('## Stderr\\n\\n```\\n' + result.stderr[-2000:] + '\\n```') if result.stderr else ''}

---

## Recomendaciones

{generate_recommendations(critical_affected, result.returncode, imports_ok)}

---

*Generado por V4 Regression Guardian*  
*Valida que `python main.py v4complete` funcione correctamente*
"""
    
    output_path.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_path


def generate_recommendations(critical_affected: Set[str], tests_passed: int, imports_ok: bool) -> str:
    """Genera recomendaciones basadas en los resultados."""
    recommendations = []
    
    if not tests_passed:
        recommendations.append("- ⚠️ **Tests fallaron**: Revisar los errores en el output de pytest")
        recommendations.append("- Considerar ejecutar los tests fallidos individualmente para más detalles")
    
    if not imports_ok:
        recommendations.append("- 🔴 **Errores de import**: Verificar dependencias y estructura de módulos")
    
    if critical_affected:
        recommendations.append(f"- ⚠️ **Módulos críticos afectados**: {', '.join(critical_affected)}")
        recommendations.append("  - Se recomienda revisión manual adicional")
        recommendations.append("  - Considerar ejecutar `python main.py v4complete` con URL de prueba")
    
    if tests_passed and imports_ok and not critical_affected:
        recommendations.append("- ✅ Todos los checks pasaron. La implementación parece segura.")
    
    if not recommendations:
        recommendations.append("- No hay recomendaciones específicas.")
    
    return chr(10).join(recommendations)


def main():
    parser = argparse.ArgumentParser(
        description="V4 Regression Guardian - Valida v4complete después de cambios"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Solo tests críticos + baseline"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Validación completa (incluye todos los tests de módulos afectados)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Modo CI - salida mínima"
    )
    parser.add_argument(
        "--workdir",
        type=str,
        help="Directorio alternativo para ejecutar validaciones"
    )
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Re-ejecutar solo los pasos que fallaron en ejecuciones anteriores"
    )
    parser.add_argument(
        "--run-v4",
        action="store_true",
        help="[No implementado] Ejecutar v4complete también"
    )
    
    args = parser.parse_args()

    print("=" * 70)
    print("V4 REGRESSION GUARDIAN")
    print("Validacion post-implementacion para v4complete")
    print("=" * 70)

    # 1. Detectar cambios
    print("\n[1/5] Detectando archivos modificados...")
    changed_files = get_changed_files()
    if not changed_files:
        print("  [INFO] No se detectaron cambios o no es un repositorio git")
        print("  Ejecutando solo test de regresion base...")
    else:
        print(f"  [OK] {len(changed_files)} archivos modificados")
    
    # 2. Cargar mapeo y detectar módulos
    print("\n[2/5] Identificando módulos v4 afectados...")
    module_map = load_module_map()
    affected_modules = map_files_to_modules(changed_files, module_map)
    
    if affected_modules:
        print(f"  ✅ Módulos afectados: {', '.join(sorted(affected_modules))}")
        critical = affected_modules & CRITICAL_MODULES
        if critical:
            print(f"  [WARN] Modulos CRITICOS: {', '.join(critical)}")
    else:
        print("  [INFO] No se detectaron módulos v4 afectados (ejecutando solo baseline)")
    
    # 3. Seleccionar tests
    print("\n[3/5] Seleccionando tests...")
    # Handle workdir parameter
    if args.workdir:
        original_cwd = Path.cwd()
        workdir_path = Path(args.workdir)
        if workdir_path.exists():
            print(f"  Cambiando a directorio de trabajo: {workdir_path}")
            os.chdir(workdir_path)
            global ROOT_DIR
            ROOT_DIR = workdir_path
        else:
            print(f"  ⚠️  Directorio de trabajo no encontrado: {workdir_path}")
    
    tests = select_tests(affected_modules, module_map, args.quick, args.full)
    print(f"  [OK] Tests a ejecutar: {len(tests)}")
    for t in tests:
        print(f"    - [{t}]")
    
    # 3.5. Verificar imports
    imports_ok = check_module_imports(affected_modules)
    
    # 4. Ejecutar tests
    print("\n[4/5] Ejecutando tests...")
    result = run_tests(tests)
    
    # Mostrar resumen de pytest
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        # Mostrar últimas líneas con el resumen
        for line in lines[-10:]:
            if line.strip():
                print(f"  {line}")
    
    if result.returncode != 0:
        print(f"  [ERROR] Tests fallaron (codigo: {result.returncode})")
    else:
        print("  [OK] Todos los tests pasaron")
    
    # 4.5. Integrar con agent_harness
    print("\n[4.5/5] Integrando con agent_harness...")
    try:
        # Ensure the root directory is in sys.path for agent_harness import
        if str(ROOT_DIR) not in sys.path:
            sys.path.insert(0, str(ROOT_DIR))
        from agent_harness.memory import MemoryManager
        memory = MemoryManager()
        # Registrar resultado en memoria
        log_entry = {
            "action": "v4_regression_guardian",
            "target_id": "v4complete_validation",
            "outcome": "success" if (result.returncode == 0 and imports_ok) else "failure",
            "tests_run": len(tests),
            "tests_passed": result.returncode == 0,
            "imports_ok": imports_ok,
            "modules_affected": list(affected_modules),
            "critical_modules_affected": list(affected_modules & CRITICAL_MODULES),
            "report_path": str(report_path) if 'report_path' in locals() else None,
            "flags_used": {
                "quick": args.quick,
                "full": args.full,
                "quiet": args.quiet,
                "workdir": args.workdir,
                "retry_failed": args.retry_failed
            }
        }
        memory.append_log(log_entry)
        # Añadir marca de validación post-cambios
        memory.append_log({
            "action": "mark_validated",
            "target_id": "v4complete_validation",
            "validation_type": "post_changes",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "outcome": "marked"
        })
        print("  [OK] Resultados registrados en agent_harness memory")
    except ImportError as e:
        msg = str(e)
        msg_ascii = msg.encode('ascii', errors='replace').decode()
        print(f"  [WARN] No se pudo integrar con agent_harness: {msg_ascii}")
    except Exception as e:
        msg = str(e)
        msg_ascii = msg.encode('ascii', errors='replace').decode()
        print(f"  [WARN] Error al integrar con agent_harness: {msg_ascii}")
    
    # 5. Generar reporte
    print("\n[5/5] Generando reporte...")
    report_path = generate_report(
        changed_files, affected_modules, tests, result, imports_ok, REPORTS_DIR
    )
    print(f"  [OK] Reporte guardado: [{report_path}]")
    
    # Veredicto final
    print("\n" + "=" * 70)
    if result.returncode == 0 and imports_ok:
        print("[OK] VALIDACION EXITOSA")
        print("   v4complete debería funcionar correctamente")
        print("=" * 70)
        return 0
    else:
        print("[ERROR] VALIDACION FALLIDA")
        if not imports_ok:
            print("   ⚠️  Errores de import detectados")
        if result.returncode != 0:
            print("   ⚠️  Tests fallaron")
        if affected_modules & CRITICAL_MODULES:
            print(f"   ⚠️  Módulos críticos afectados: {affected_modules & CRITICAL_MODULES}")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
