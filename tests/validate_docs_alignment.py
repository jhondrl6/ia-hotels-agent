"""
Script de validación de alineación documental (JSON vs MD).
Verifica que los umbrales clave de v2.4.2 estén presentes en el Plan Maestro MD.
"""
"""
Verifica que los umbrales clave de v2.4.2 estén presentes en el Plan Maestro MD.

Nota: Este test se considera parte de la suite legacy (decision_core_v24).
Para v2.5 (delivery/deploy) se debe usar documento_oficial del JSON.
"""
import json
import os
import sys

# Force UTF-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def validate_alignment():
    json_path = "data/benchmarks/plan_maestro_data.json"
    md_path = "data/benchmarks/Plan_maestro_v2_5.md"
    
    print(f"Validando alineación entre:\n- {json_path}\n- {md_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    errors = []
    
    # 1. Validar Versión
    json_version = data.get('version')
    if json_version not in md_content:
        errors.append(f"❌ Versión {json_version} no encontrada en MD")
    else:
        print(f"✅ Versión {json_version} encontrada")

    # 2. Validar Umbrales Nuevos
    umbrales = data.get('umbrales_decision', {})
    keys_to_check = [
        "inactividad_max_mensual",
        "descuento_motor_inexistente",
        "descuento_motor_no_prominente"
    ]
    
    for k in keys_to_check:
        if k in umbrales:
            # Buscamos la clave o una descripción humana del concepto
            # Simplificación: buscamos la clave literal para asegurar precisión técnica en docs
            if k not in md_content:
                errors.append(f"❌ Umbral '{k}' no documentado en MD")
            else:
                print(f"✅ Umbral '{k}' documentado")

    # 3. Validar Sección de Pesos de Actividad
    if "actividad_gbp_pesos" not in md_content and "posts_90d_peso" not in md_content:
        errors.append("❌ Sección 'actividad_gbp_pesos' no documentada en MD")
    else:
        print("✅ Sección 'actividad_gbp_pesos' documentada")

    # 4. Validar Enlaces en INDICE_DOCUMENTACION.md
    print("-" * 30)
    print("Validando enlaces en INDICE_DOCUMENTACION.md...")
    
    index_path = "INDICE_DOCUMENTACION.md"
    if not os.path.exists(index_path):
         errors.append(f"❌ {index_path} no encontrado")
    else:
        import re
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex para enlaces Markdown: [texto](url)
        # Excluir enlaces HTTP/HTTPS externos
        links = re.findall(r'\[.*?\]\((.*?)\)', content)
        
        for link in links:
            # Limpiar anclas (#section)
            link_clean = link.split('#')[0]
            
            # Ignorar externos, vacíos o email
            if not link_clean or link_clean.startswith('http') or link_clean.startswith('mailto:'):
                continue
                
            # Resolver ruta relativa
            # El índice está en raíz, así que los links son relativos a raíz
            target_path = link_clean
            
            # Casos especiales de rutas dinámicas (ignorar validación estricta si es output generado)
            if "delivery_assets" in target_path or "output/" in target_path:
                print(f"⚠️ Ignorando validación estricta de activo dinámico: {target_path}")
                continue
                
            if not os.path.exists(target_path):
                errors.append(f"❌ Enlace roto en índice: {target_path}")

    # Reporte Final
    print("-" * 30)
    if errors:
        print(f"⚠️ SE ENCONTRARON {len(errors)} ERRORES DE ALINEACIÓN:")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("🎉 DOCUMENTACIÓN ALINEADA CON V2.4.2 Y ENLACES VÁLIDOS")
        sys.exit(0)

if __name__ == "__main__":
    # Ajustar cwd si es necesario
    # Detectar si estamos en tests/ o raíz
    cwd = os.getcwd()
    if cwd.endswith("tests"):
        os.chdir("..")
        print(f"Cambiando directorio de trabajo a: {os.getcwd()}")
    
    validate_alignment()
