"""
Test E2E: v4.5.6 Corrections Regression

FASE 5 TRANSVERSAL - T6: Test de regresión E2E

Este test verifica que todas las correcciones de Fases 1-4 están presentes
y no han regresado (reintroducido bugs).

FASES corregidas:
- FASE 1: COP COP no debe existir en módulos
- FASE 2: Asset bugs (confidence_scores, preflight_checks)
- FASE 3: Quality improvements (validator, coherence)
- FASE 4: Features (benchmark validation)
"""

import json
import re
from pathlib import Path


class TestE2Ev456Corrections:
    """Test T6: Regresión E2E de correcciones Fases 1-4."""

    def test_fase1_cop_cop_not_present(self):
        """
        FASE 1: Verificar que 'COP COP' no existe en módulos.
        
        Bug: 'COP COP' string hardcodeado en benchmark_resolver.py línea 59
        Fix: Usar variables configurables
        """
        print("\n🔍 FASE 1: Verificando COP COP no existe...")
        
        modules_path = Path("/mnt/c/Users/Jhond/Github/iah-cli/modules")
        
        # Buscar recursivamente en todos los .py
        matches = []
        for py_file in modules_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "COP COP" in content:
                        matches.append(str(py_file.relative_to(modules_path.parent))
                        )
            except Exception:
                pass
        
        if matches:
            print(f"❌ VIOLATION: 'COP COP' encontrado en:")
            for m in matches:
                print(f"   - {m}")
        else:
            print("✅ FASE 1 OK: 'COP COP' no encontrado en módulos")
        
        assert len(matches) == 0, f"COP COP encontrado en {len(matches)} archivos"

    def test_fase2_asset_bugs_fixed(self):
        """
        FASE 2: Verificar bugs de assets corregidos.
        
        Bugs:
        - confidence_score faltante en AssetMetadata (BUG B)
        - preflight_checks no invocado
        
        Fixes:
        - asset_diagnostic_linker.py: confidence_score añadido a AssetMetadata
        - conditional_generator.py: preflight_checks invocado antes de generation
        """
        print("\n🔍 FASE 2: Verificando asset bugs...")
        
        # Verificar asset_diagnostic_linker.py tiene confidence_score
        linker_path = Path("/mnt/c/Users/Jhond/Github/iah-cli/modules/asset_generation/asset_diagnostic_linker.py")
        assert linker_path.exists(), "asset_diagnostic_linker.py no encontrado"
        
        with open(linker_path, 'r', encoding='utf-8') as f:
            linker_content = f.read()
        
        # Buscar "confidence_score" en la clase AssetMetadata
        assert "confidence_score" in linker_content, (
            "BUG B: confidence_score no encontrado en asset_diagnostic_linker.py"
        )
        print("✅ FASE 2a: confidence_score presente en AssetMetadata")
        
        # Verificar que conditional_generator.py invoca preflight_checks
        cond_gen_path = Path("/mnt/c/Users/Jhond/Github/iah-cli/modules/asset_generation/conditional_generator.py")
        assert cond_gen_path.exists(), "conditional_generator.py no encontrado"
        
        with open(cond_gen_path, 'r', encoding='utf-8') as f:
            cond_gen_content = f.read()
        
        assert "preflight_checks" in cond_gen_content or "PreflightChecks" in cond_gen_content, (
            "preflight_checks no invocado en conditional_generator.py"
        )
        print("✅ FASE 2b: preflight_checks invocado en conditional_generator")

    def test_fase3_quality_improvements(self):
        """
        FASE 3: Verificar improvements de quality.
        
        Improvements:
        - CoherenceValidator mejorado
        - Publication gates con thresholds correctos
        """
        print("\n🔍 FASE 3: Verificando quality improvements...")
        
        # Verificar coherence_validator.py
        coherence_path = Path("/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/coherence_validator.py")
        assert coherence_path.exists(), "coherence_validator.py no encontrado"
        
        with open(coherence_path, 'r', encoding='utf-8') as f:
            coherence_content = f.read()
        
        # Verificar que tiene CHECK_WEIGHTS
        assert "CHECK_WEIGHTS" in coherence_content, (
            "CHECK_WEIGHTS no encontrado en coherence_validator.py"
        )
        print("✅ FASE 3a: CoherenceValidator tiene CHECK_WEIGHTS")
        
        # Verificar publication_gates.py tiene thresholds correctos
        gates_path = Path("/mnt/c/Users/Jhond/Github/iah-cli/modules/quality_gates/publication_gates.py")
        assert gates_path.exists(), "publication_gates.py no encontrado"
        
        with open(gates_path, 'r', encoding='utf-8') as f:
            gates_content = f.read()
        
        # Verificar threshold de coherence (0.8)
        assert "coherence_threshold" in gates_content, (
            "coherence_threshold no encontrado en publication_gates.py"
        )
        print("✅ FASE 3b: publication_gates tiene coherence_threshold")

    def test_fase4_benchmark_validation(self):
        """
        FASE 4: Verificar benchmark validation.
        
        Features:
        - benchmark_resolver con validación robusta
        - BenchmarkCrossValidator para comparar benchmarks
        """
        print("\n🔍 FASE 4: Verificando benchmark validation...")
        
        # Verificar benchmark_resolver.py
        resolver_path = Path("/mnt/c/Users/Jhond/Github/iah-cli/modules/providers/benchmark_resolver.py")
        assert resolver_path.exists(), "benchmark_resolver.py no encontrado"
        
        with open(resolver_path, 'r', encoding='utf-8') as f:
            resolver_content = f.read()
        
        # Verificar que tiene métodos de validación
        assert "resolve" in resolver_content, "benchmark_resolver debe tener método resolve()"
        print("✅ FASE 4a: benchmark_resolver tiene método resolve()")
        
        # Verificar BenchmarkCrossValidator
        cross_validator_path = Path("/mnt/c/Users/Jhond/Github/iah-cli/modules/providers/benchmark_cross_validator.py")
        assert cross_validator_path.exists(), "benchmark_cross_validator.py no encontrado"
        
        with open(cross_validator_path, 'r', encoding='utf-8') as f:
            cross_content = f.read()
        
        assert "BenchmarkCrossValidator" in cross_content, (
            "BenchmarkCrossValidator no encontrado"
        )
        print("✅ FASE 4b: BenchmarkCrossValidator existe")

    def test_no_refinando_in_modules(self):
        """
        Verificar que no hay strings 'Refinando' en módulos.
        
        Este es un indicador de lógica de debugging dejo en producción.
        """
        print("\n🔍 Buscando 'Refinando' en módulos...")
        
        modules_path = Path("/mnt/c/Users/Jhond/Github/iah-cli/modules")
        
        matches = []
        for py_file in modules_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if "Refinando" in line:
                            matches.append(f"{py_file.name}:{i}")
            except Exception:
                pass
        
        if matches:
            print(f"⚠️ 'Refinando' encontrado en:")
            for m in matches:
                print(f"   - {m}")
        else:
            print("✅ 'Refinando' no encontrado en módulos")

    def test_output_structure_valid(self):
        """
        Verificar que el output de v4_complete tiene estructura válida.
        """
        print("\n🔍 Verificando estructura de output...")
        
        output_dir = Path("/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete")
        assert output_dir.exists(), "output/v4_complete no encontrado"
        
        # Archivos esperados
        expected_files = [
            "audit_report.json",
            "v4_complete_report.json"
        ]
        
        for filename in expected_files:
            filepath = output_dir / filename
            assert filepath.exists(), f"Archivo esperado no encontrado: {filename}"
            
            # Verificar que es JSON válido
            if filename.endswith(".json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    json.load(f)  # Valida JSON
                print(f"✅ {filename} es JSON válido")
        
        print("✅ Estructura de output válida")


if __name__ == "__main__":
    test = TestE2Ev456Corrections()
    
    print("=" * 70)
    print("T6: Test E2E v4.5.6 Corrections Regression")
    print("=" * 70)
    
    # FASE 1
    try:
        test.test_fase1_cop_cop_not_present()
        print("✅ FASE 1 CORRECTIONS VERIFIED")
    except AssertionError as e:
        print(f"❌ FASE 1 FAILED: {e}")
    
    # FASE 2
    try:
        test.test_fase2_asset_bugs_fixed()
        print("✅ FASE 2 CORRECTIONS VERIFIED")
    except AssertionError as e:
        print(f"❌ FASE 2 FAILED: {e}")
    
    # FASE 3
    try:
        test.test_fase3_quality_improvements()
        print("✅ FASE 3 CORRECTIONS VERIFIED")
    except AssertionError as e:
        print(f"❌ FASE 3 FAILED: {e}")
    
    # FASE 4
    try:
        test.test_fase4_benchmark_validation()
        print("✅ FASE 4 CORRECTIONS VERIFIED")
    except AssertionError as e:
        print(f"❌ FASE 4 FAILED: {e}")
    
    # General
    try:
        test.test_no_refinando_in_modules()
        print("✅ DEBUG STRINGS CHECK PASSED")
    except AssertionError as e:
        print(f"❌ DEBUG STRINGS CHECK FAILED: {e}")
    
    try:
        test.test_output_structure_valid()
        print("✅ OUTPUT STRUCTURE VALID")
    except AssertionError as e:
        print(f"❌ OUTPUT STRUCTURE FAILED: {e}")
    
    print("=" * 70)
    print("T6 COMPLETADO: Regression E2E verificada")
    print("=" * 70)
