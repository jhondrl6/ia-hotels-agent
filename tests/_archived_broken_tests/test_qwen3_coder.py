#!/usr/bin/env python3
"""
Test específico para el modelo qwen3-coder-plus
"""

import requests
import json
import os

# Load API key from environment variable - NEVER hardcode API keys
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "your_api_key_here")
BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

# Modelos a probar relacionados con qwen3-coder
MODELS_TO_TEST = [
    "qwen3-coder-plus",
    "qwen-coder-plus",
    "qwen3-coder",
    "qwen-coder",
    "qwen2.5-coder-32b-instruct",
]

def test_model(model_name):
    """Probar un modelo específico"""
    url = f"{BASE_URL}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prompt de prueba para coding
    data = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": "Write a Python function that calculates the factorial of a number. Return only the code."
            }
        ],
        "max_tokens": 200,
        "temperature": 0.7,
        "stream": False
    }
    
    print(f"\n{'='*60}")
    print(f"Probando modelo: {model_name}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ ¡MODELO DISPONIBLE Y FUNCIONAL!")
            print(f"\nRespuesta:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                print(f"\nContenido generado:\n{content}")
            
            print(f"\nUso de tokens:")
            usage = result.get("usage", {})
            print(f"  - Prompt tokens: {usage.get('prompt_tokens', 0)}")
            print(f"  - Completion tokens: {usage.get('completion_tokens', 0)}")
            print(f"  - Total tokens: {usage.get('total_tokens', 0)}")
            
            return True, model_name, result
        else:
            print(f"\n❌ Error HTTP {response.status_code}")
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"Detalle del error:")
            print(json.dumps(error_data, indent=2, ensure_ascii=False) if isinstance(error_data, dict) else error_data)
            return False, model_name, error_data
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False, model_name, str(e)


def list_available_models():
    """Intentar obtener lista de modelos disponibles"""
    url = f"{BASE_URL}/models"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print(f"\n{'='*60}")
    print(f"Obteniendo lista de modelos disponibles")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Lista de modelos obtenida")
            
            if "data" in result:
                print(f"\nTotal de modelos: {len(result['data'])}")
                
                # Filtrar modelos que contengan 'coder' o 'qwen'
                coder_models = [m for m in result['data'] if 'coder' in m.get('id', '').lower()]
                qwen3_models = [m for m in result['data'] if 'qwen3' in m.get('id', '').lower()]
                
                print(f"\nModelos 'coder' encontrados ({len(coder_models)}):")
                for m in coder_models[:20]:
                    print(f"  - {m.get('id')}")
                
                print(f"\nModelos 'qwen3' encontrados ({len(qwen3_models)}):")
                for m in qwen3_models[:20]:
                    print(f"  - {m.get('id')}")
                    
                return True, result
            return False, "No data field"
        else:
            print(f"\n❌ Error: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False, str(e)


if __name__ == "__main__":
    print("="*60)
    print("TEST DE MODELOS QWEN3-CODER")
    print("="*60)
    
    # Primero intentar obtener lista de modelos
    success, models_data = list_available_models()
    
    # Probar modelos específicos
    working_models = []
    
    for model in MODELS_TO_TEST:
        success, model_name, result = test_model(model)
        if success:
            working_models.append((model_name, result))
    
    # Resumen final
    print("\n\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    if working_models:
        print(f"\n✅ Modelos que funcionan ({len(working_models)}):")
        for model_name, response in working_models:
            usage = response.get("usage", {})
            print(f"  - {model_name} (total tokens: {usage.get('total_tokens', 'N/A')})")
        
        print(f"\n🎯 Modelo objetivo 'qwen3-coder-plus': " + 
              ("✅ FUNCIONA" if any(m[0] == "qwen3-coder-plus" for m in working_models) else "❌ NO DISPONIBLE"))
    else:
        print(f"\n❌ Ningún modelo de la lista funcionó")
        print(f"\nPosibles causas:")
        print(f"  1. Modelos no disponibles para tu cuenta/región")
        print(f"  2. API Key sin permisos para estos modelos")
        print(f"  3. Nombres de modelo incorrectos")
