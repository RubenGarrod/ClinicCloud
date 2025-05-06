"""
Script para probar la comunicación entre la API y el motor de búsqueda.
Este script prueba tanto la comunicación directa con el motor de búsqueda
como la comunicación a través de la API.
"""

import requests
import json
import sys
import time

def test_motor_busqueda_direct():
    """Prueba directamente el motor de búsqueda"""
    print("\n=== Probando motor de búsqueda directamente ===")
    
    url = "http://localhost:8001/search"
    
    # Lista de consultas para probar
    queries = [
        "cardiology",       # Inglés
        "cardiología",      # Español
        "medic",            # Término parcial en inglés
        "salud",            # Término general en español
        "",                 # Consulta vacía
        "*"                 # Wildcard - puede funcionar en algunos motores
    ]
    
    for query in queries:
        print(f"\n----- Probando consulta: '{query}' -----")
        
        payload = {
            "query": query,
            "limit": 5,
            "offset": 0
        }
        
        try:
            print(f"Enviando solicitud a: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, json=payload, timeout=10)
            
            print(f"Código de estado: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Motor de búsqueda respondió correctamente")
                print(f"Total de resultados: {data.get('total', 0)}")
                
                # Imprimir respuesta completa para depuración
                print("Respuesta completa:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Verificar si hay resultados
                if data.get('results', []):
                    print(f"Primer resultado: {data['results'][0]['titulo']} (Score: {data['results'][0]['score']:.4f})")
                else:
                    print("⚠️ No se encontraron resultados para esta consulta")
            else:
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    # Consultar índice info si existe
    try:
        print("\n----- Consultando información del índice -----")
        index_url = "http://localhost:8001/index-info"
        response = requests.get(index_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Información del índice:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"⚠️ No se pudo obtener información del índice: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error al consultar información del índice: {e}")
    
    return True

def test_api_endpoint():
    """Prueba el endpoint de búsqueda a través de la API"""
    print("\n=== Probando API de búsqueda ===")
    
    url = "http://localhost:8000/api/search/"
    
    # Lista de consultas para probar
    queries = [
        "medical",         # Inglés
        "médico",          # Español
        "salud",           # Término general en español
        ""                 # Consulta vacía
    ]
    
    for query in queries:
        print(f"\n----- Probando consulta: '{query}' -----")
        
        payload = {
            "query": query,
            "limit": 5,
            "offset": 0
        }
        
        try:
            print(f"Enviando solicitud a: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, json=payload, timeout=10)
            
            print(f"Código de estado: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API respondió correctamente")
                print(f"Total de resultados: {data.get('total', 0)}")
                
                # Imprimir respuesta completa para depuración
                print("Respuesta completa:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Verificar si hay resultados
                if data.get('results', []):
                    print(f"Primer resultado: {data['results'][0]['titulo']} (Score: {data['results'][0]['score']:.4f})")
                else:
                    print("⚠️ No se encontraron resultados para esta consulta")
            else:
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    return True

def test_health_endpoints():
    """Prueba los endpoints de health check de ambos servicios"""
    print("\n=== Probando endpoints de health check ===")
    
    # Probar API principal
    try:
        print("Probando API principal...")
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"API principal: {response.status_code} - {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ No se pudo conectar a la API principal: {e}")
    
    # Probar Motor de búsqueda
    try:
        print("\nProbando motor de búsqueda...")
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"Motor de búsqueda: {response.status_code} - {response.json()}")
        
        # Intentar obtener información adicional del motor
        try:
            config_response = requests.get("http://localhost:8001/config", timeout=5)
            if config_response.status_code == 200:
                print("\nConfiguración del motor de búsqueda:")
                print(json.dumps(config_response.json(), indent=2, ensure_ascii=False))
        except:
            pass
            
    except requests.exceptions.RequestException as e:
        print(f"❌ No se pudo conectar al motor de búsqueda: {e}")

if __name__ == "__main__":
    print("Test de comunicación entre servicios de ClinicCloud")
    print("==================================================")
    
    # Probar endpoints de health
    test_health_endpoints()
    
    # Probar motor de búsqueda directamente
    motor_ok = test_motor_busqueda_direct()
    
    # Si el motor de búsqueda funciona, probar la API
    if motor_ok:
        test_api_endpoint()
    else:
        print("\n⚠️ Omitiendo prueba de API ya que el motor de búsqueda no respondió correctamente")
    
    print("\n==================================================")
    print("Test completado.")