#!/usr/bin/env python3
"""
Validate Structure - Script de Validación Post-Reestructuración
================================================================

Valida que la estructura del proyecto esté coherente después de la
reestructuración de reportes (Funnel Optimizado Eje Cafetero).

Verifica:
- Módulos críticos existen
- Métodos nuevos están implementados
- Documentación actualizada
- No hay referencias a estructura antigua

Author: IA Hoteles Team
Date: 2025-11-22
"""

import sys
from pathlib import Path


def validate_structure():
    """
    Valida coherencia de estructura post-reestructuración.
    
    Returns:
        int: 0 si todo OK, 1 si hay errores críticos
    """
    errors = []
    warnings = []
    
    print("=" * 60)
    print("VALIDACIÓN DE ESTRUCTURA - IA Hoteles Agent")
    print("=" * 60)
    print()
    
    # ========================================
    # 1. Verificar módulos críticos existen
    # ========================================
    print("[1/5] Verificando módulos críticos...")
    required_modules = [
        'modules/generators/report_builder.py',
        'modules/generators/toolkit_consultor_gen.py',
        'modules/orchestrator/pipeline.py',
        'modules/analyzers/competitor_analyzer.py',  # NUEVO
    ]
    
    for module in required_modules:
        if not Path(module).exists():
            errors.append(f"Módulo crítico faltante: {module}")
        else:
            print(f"   ✓ {module}")
    
    if not errors:
        print("   [OK] Todos los módulos críticos existen")
    print()
    
    # ========================================
    # 2. Verificar métodos nuevos existen
    # ========================================
    print("[2/5] Verificando métodos nuevos implementados...")
    
    report_builder_path = Path('modules/generators/report_builder.py')
    if report_builder_path.exists():
        report_builder = report_builder_path.read_text(encoding='utf-8')
        
        # Métodos de reestructuración
        if '_generate_diagnostico_y_oportunidad' not in report_builder:
            errors.append("Método _generate_diagnostico_y_oportunidad no encontrado en report_builder.py")
        else:
            print("   ✓ _generate_diagnostico_y_oportunidad()")
        
        if '_generate_client_readme' not in report_builder:
            errors.append("Método _generate_client_readme no encontrado")
        else:
            print("   ✓ _generate_client_readme()")
        
        # Nuevo método de competidores
        if '_format_competitors_section' not in report_builder:
            warnings.append("Método _format_competitors_section no encontrado (Competidores no integrados)")
        else:
            print("   ✓ _format_competitors_section()")
        
        # Verificar que recibe competitors_data como parámetro
        if 'competitors_data: Optional[List[Dict]]' not in report_builder:
            warnings.append("Parámetro competitors_data no encontrado en métodos (integración incompleta)")
        else:
            print("   ✓ Parámetro competitors_data integrado")
    else:
        errors.append("report_builder.py no encontrado")
    
    if not errors:
        print("   [OK] Métodos nuevos implementados correctamente")
    print()
    
    # ========================================
    # 3. Verificar templates obsoletos no están en uso
    # ========================================
    print("[3/5] Verificando que templates obsoletos no estén en uso...")
    
    if report_builder_path.exists():
        if 'diagnostico_ejecutivo.md' in report_builder:
            warnings.append("Template diagnostico_ejecutivo.md aún referenciado en report_builder.py")
        else:
            print("   ✓ Template diagnostico_ejecutivo.md no referenciado")
    print()
    
    # ========================================
    # 4. Verificar outputs viejos en archives
    # ========================================
    print("[4/5] Verificando outputs con estructura antigua...")
    
    old_outputs_client_dir = Path('output/clientes')
    if old_outputs_client_dir.exists():
        old_outputs = list(old_outputs_client_dir.glob('*/00_RESUMEN_EJECUTIVO.md'))
        if old_outputs:
            warnings.append(
                f"{len(old_outputs)} output(s) con estructura antigua en output/clientes/ "
                "(ejecutar cleanup_old_structure.py para mover a archives)"
            )
            for output in old_outputs:
                print(f"   ⚠️  {output.parent.name}")
        else:
            print("   ✓ No hay outputs con estructura antigua en output/clientes/")
    else:
        print("   ✓ Directorio output/clientes/ no existe (limpio)")
    print()
    
    # ========================================
    # 5. Verificar documentación actualizada
    # ========================================
    print("[5/5] Verificando documentación actualizada...")
    
    readme_path = Path('README.md')
    if readme_path.exists():
        readme = readme_path.read_text(encoding='utf-8')
        
        # Verificar que NO mencione estructura antigua
        if '00_RESUMEN_EJECUTIVO.md' in readme:
            errors.append("README.md aún menciona 00_RESUMEN_EJECUTIVO.md (estructura antigua)")
        else:
            print("   ✓ README no menciona 00_RESUMEN_EJECUTIVO.md")
        
        if '03_SEO_ACCELERATOR.md' in readme and 'documento separado' in readme:
            warnings.append("README.md menciona 03_SEO_ACCELERATOR.md como documento separado")
        
        # Verificar que mencione estructura nueva
        if '01_DIAGNOSTICO_Y_OPORTUNIDAD.md' not in readme:
            errors.append("README.md no menciona 01_DIAGNOSTICO_Y_OPORTUNIDAD.md (estructura nueva)")
        else:
            print("   ✓ README menciona 01_DIAGNOSTICO_Y_OPORTUNIDAD.md")
        
        if '_toolkit_consultor' not in readme:
            warnings.append("README.md no menciona _toolkit_consultor/")
        else:
            print("   ✓ README menciona _toolkit_consultor/")
    else:
        errors.append("README.md no encontrado")
    
    # Verificar ROADMAP.md existe
    roadmap_path = Path('ROADMAP.md')
    if roadmap_path.exists():
        print("   ✓ ROADMAP.md creado (features futuras documentadas)")
    else:
        warnings.append("ROADMAP.md no encontrado (features de videos no documentadas)")
    
    print()
    
    # ========================================
    # REPORTE FINAL
    # ========================================
    print("=" * 60)
    print("RESULTADO DE VALIDACIÓN")
    print("=" * 60)
    print()
    
    if errors:
        print("❌ ERRORES CRÍTICOS:")
        for error in errors:
            print(f"  - {error}")
        print()
    
    if warnings:
        print("⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    if not errors and not warnings:
        print("✅ Estructura validada correctamente")
        print("   Todos los checks pasaron sin errores ni advertencias")
        print()
    
    # Estadísticas
    print(f"Total checks: {5}")
    print(f"Errores críticos: {len(errors)}")
    print(f"Advertencias: {len(warnings)}")
    print()
    
    if errors:
        print("⚠️  Hay errores críticos que deben corregirse antes de continuar")
        return 1
    elif warnings:
        print("ℹ️  Hay advertencias pero el sistema puede funcionar")
        return 0
    else:
        print("✅ Sistema listo para operar")
        return 0


if __name__ == '__main__':
    sys.exit(validate_structure())
