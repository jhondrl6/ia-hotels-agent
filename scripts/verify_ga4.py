
import os
import sys
from dotenv import load_dotenv

# Añadir el directorio raíz al path para poder importar módulos
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)

def verify_config():
    # Cargar variables del .env explícitamente desde la raíz
    env_path = os.path.join(root_dir, '.env')
    print(f"Cargando .env desde: {env_path}")
    load_dotenv(dotenv_path=env_path)
    
    from modules.analytics.google_analytics_client import GoogleAnalyticsClient
    
    print("--- Verificando Conexión con Google Analytics 4 ---")
    
    property_id = os.getenv("GA4_PROPERTY_ID")
    credentials_path = os.getenv("GA4_CREDENTIALS_PATH")
    
    print(f"Propiedad ID: {property_id}")
    print(f"Ruta JSON: {credentials_path}")
    
    if not property_id or not credentials_path:
        print("\n❌ ERROR: Faltan variables en el archivo .env (GA4_PROPERTY_ID o GA4_CREDENTIALS_PATH)")
        return

    if not os.path.exists(credentials_path):
        print(f"\n❌ ERROR: No se encuentra el archivo JSON en: {credentials_path}")
        return

    client = GoogleAnalyticsClient()
    
    print("\nIniciando cliente de GA4...")
    if client.is_available():
        print("✅ Cliente inicializado correctamente.")
        
        print("\nConsultando tráfico de los últimos 30 días...")
        try:
            data = client.get_indirect_traffic(date_range="last_30_days")
            
            if data.get("data_source") == "GA4":
                print("\n✅ ¡CONEXIÓN EXITOSA!")
                print(f"Tráfico Indirecto Detectado: {data.get('sessions_indirect')}")
                print(f"Tráfico Directo: {data.get('sessions_direct')}")
                print(f"Fuentes principales: {data.get('top_sources')}")
            else:
                print(f"\n❌ Error al obtener datos: {data.get('note')}")
                print("\nCONSEJO: Verifica que el Email de la Cuenta de Servicio tenga permiso de 'Lector' en la Propiedad de GA4.")
                
        except Exception as e:
            print(f"\n❌ Ocurrió un error inesperado: {e}")
    else:
        print(f"\n❌ No se pudo inicializar el cliente: {client._init_error}")

if __name__ == "__main__":
    verify_config()
