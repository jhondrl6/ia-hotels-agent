#!/usr/bin/env python3
"""
Test de conexión con Alibaba Cloud Dashscope API
"""

import requests
import json
import os

# Load API key from environment variable - NEVER hardcode API keys
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "your_api_key_here")

# Posibles endpoints de Alibaba Cloud Dashscope
ENDPOINTS = [
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    "https://dashscope.aliyuncs.com/api/v1",
    "https://dashscope-intl.aliyuncs.com/api/v1",
]

MODELS_TO_TEST = [
    "qwen-turbo",
    "qwen-plus",
    "qwen-max",
]

def test_endpoint(base_url, model="qwen-turbo"):
    """Probar un endpoint específico"""
    url = f"{base_url}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Hola, ¿quién eres? Responde brevemente."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7,
        "stream": False
    }
    
    print(f"\n{'='*60}")
    print(f"Probando: {url}")
    print(f"Modelo: {model}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Headers recibidos: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ ¡ÉXITO!")
            print(f"\nRespuesta completa:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Extraer información relevante
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                print(f"\nContenido de respuesta: {content}")
            
            if "model" in result:
                print(f"\nModelo usado: {result['model']}")
            
            return True, base_url, result
        else:
            print(f"\n❌ Error HTTP {response.status_code}")
            print(f"Respuesta de error: {response.text}")
            return False, base_url, response.text
            
    except requests.exceptions.Timeout:
        print("\n❌ Timeout - El endpoint no respondió a tiempo")
        return False, base_url, "Timeout"
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Error de conexión: {e}")
        return False, base_url, str(e)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False, base_url, str(e)


def test_models_endpoint(base_url):
    """Probar endpoint de lista de modelos"""
    url = f"{base_url}/models"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print(f"\n{'='*60}")
    print(f"Probando lista de modelos: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ ¡ÉXITO!")
            print(f"\nModelos disponibles:")
            if "data" in result:
                for model in result["data"][:10]:  # Mostrar primeros 10
                    model_id = model.get("id", "N/A")
                    print(f"  - {model_id}")
            return True, result
        else:
            print(f"\n❌ Error: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False, str(e)


if __name__ == "__main__":
    print("="*60)
    print("TEST DE ALIBABA CLOUD DASHSCOPE API")
    print("="*60)
    
    # Primero probar endpoints de chat
    working_endpoints = []
    
    for endpoint in ENDPOINTS:
        success, url, result = test_endpoint(endpoint)
        if success:
            working_endpoints.append((url, result))
            break  # Si uno funciona, no necesitamos probar los demás
    
    # Si ningún endpoint de chat funcionó, intentar con modelos
    if not working_endpoints:
        print("\n\n" + "="*60)
        print("Ningún endpoint de chat funcionó. Probando lista de modelos...")
        print("="*60)
        
        for endpoint in ENDPOINTS:
            success, result = test_models_endpoint(endpoint)
            if success:
                break
    
    # Resumen final
    print("\n\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    if working_endpoints:
        base_url, response = working_endpoints[0]
        print(f"\n✅ ¡API KEY FUNCIONA!")
        print(f"\nBase URL válido: {base_url}")
        print(f"Modelo probado: {response.get('model', 'N/A')}")
        print(f"\nPara configurar en iah-cli, usa:")
        print(f"  DASHSCOPE_API_KEY={API_KEY}")
        print(f"  DASHSCOPE_BASE_URL={base_url}")
    else:
        print(f"\n❌ La API KEY no funcionó con ningún endpoint")
        print(f"\nPosibles causas:")
        print(f"  1. API Key inválida o expirada")
        print(f"  2. API Key sin permisos para los modelos probados")
        print(f"  3. Endpoints incorrectos para tu región")
        print(f"  4. Requiere configuración especial de autenticación")
