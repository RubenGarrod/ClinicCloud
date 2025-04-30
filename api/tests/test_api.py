import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api"
DOCUMENT_URL = f"{BASE_URL}/documents"
SEARCH_URL = f"{BASE_URL}/search"
CATEGORY_URL = f"{BASE_URL}/categories"

# Para mantener un registro de los tests
test_results = {
    "passed": 0,
    "failed": 0,
    "total": 0
}

def print_response(response, title=None):
    """Muestra la respuesta en formato legible"""
    if title:
        print(f"\n=== {title} ===")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("No JSON response")
    print("=" * 50)

def assert_test(condition, message):
    """Verifica una condición y registra el resultado"""
    test_results["total"] += 1
    if condition:
        test_results["passed"] += 1
        print(f"✅ PASSED: {message}")
    else:
        test_results["failed"] += 1
        print(f"❌ FAILED: {message}")

def test_get_documento(id_documento):
    """Prueba obtener un documento específico por ID"""
    print(f"\n📄 Testing GET /api/documents/{id_documento}")
    response = requests.get(f"{DOCUMENT_URL}/{id_documento}")
    print_response(response, f"Documento {id_documento}")
    
    # Verificaciones
    assert_test(
        response.status_code == 200, 
        f"Obtener documento {id_documento} exitoso"
    )
    
    if response.status_code == 200:
        data = response.json()
        assert_test("id" in data, "El documento tiene ID")
        assert_test("titulo" in data, "El documento tiene título")
        assert_test("autor" in data and isinstance(data["autor"], list), 
                  "El autor es una lista")
        
        # Verificar formato de fecha
        if "fecha_publicacion" in data:
            try:
                datetime.fromisoformat(data["fecha_publicacion"])
                assert_test(True, "Fecha en formato ISO válido")
            except ValueError:
                assert_test(False, "Fecha en formato ISO inválido")
    
    return response.json() if response.status_code == 200 else None

def test_list_documentos(id_categoria=None, limit=10, offset=0):
    """Prueba listar documentos con filtros opcionales"""
    category_text = f"de categoría {id_categoria}" if id_categoria else ""
    print(f"\n📋 Testing GET /api/documents {category_text} (limit={limit}, offset={offset})")
    
    params = {"limit": limit, "offset": offset}
    if id_categoria:
        params["id_categoria"] = id_categoria
    
    response = requests.get(DOCUMENT_URL, params=params)
    print_response(response, f"Lista de documentos {category_text}")
    
    # Verificaciones
    assert_test(
        response.status_code == 200, 
        f"Listar documentos {category_text} exitoso"
    )
    
    if response.status_code == 200:
        data = response.json()
        assert_test(isinstance(data, list), "La respuesta es una lista")
        assert_test(len(data) <= limit, f"Respeta el límite de {limit} documentos")
        
        # Verificar estructura de cada documento
        if data:
            first_doc = data[0]
            assert_test("id" in first_doc, "Documento tiene ID")
            assert_test("titulo" in first_doc, "Documento tiene título")
            
            # Verificar filtro por categoría
            if id_categoria and len(data) > 0:  
                for doc in data:
                    if doc["categoria"]:
                        assert_test(
                            doc["categoria"]["id"] == id_categoria,
                            f"Documento {doc['id']} pertenece a categoría {id_categoria}"
                        )
    
    return response.json() if response.status_code == 200 else None

def test_search_documentos(query, id_categoria=None, limit=10, offset=0):
    """Prueba buscar documentos"""
    category_text = f"en categoría {id_categoria}" if id_categoria else ""
    print(f"\n🔍 Testing POST /api/search (query='{query}' {category_text})")
    
    payload = {
        "query": query,
        "limit": limit,
        "offset": offset
    }
    
    if id_categoria:
        payload["id_categoria"] = id_categoria
    
    response = requests.post(SEARCH_URL, json=payload)
    print_response(response, f"Búsqueda: '{query}' {category_text}")
    
    # Verificaciones
    assert_test(
        response.status_code == 200, 
        f"Búsqueda '{query}' exitosa"
    )
    
    if response.status_code == 200:
        data = response.json()
        assert_test("results" in data, "Contiene resultados")
        assert_test("total" in data, "Contiene total de resultados")
        assert_test("query" in data and data["query"] == query, "Contiene query original")
        
        # Verificar estructura de resultados
        if data["results"]:
            first_result = data["results"][0]
            assert_test("id_documento" in first_result, "Resultado tiene ID")
            assert_test("titulo" in first_result, "Resultado tiene título")
            assert_test("score" in first_result, "Resultado tiene puntuación")
            
            # Verificar que la puntuación es un valor entre 0 y 1
            if "score" in first_result:
                assert_test(
                    0 <= first_result["score"] <= 1, 
                    f"Score {first_result['score']} está entre 0 y 1"
                )
    
    return response.json() if response.status_code == 200 else None

def test_list_categorias():
    """Prueba listar todas las categorías"""
    print("\n📂 Testing GET /api/categories")
    response = requests.get(CATEGORY_URL)
    print_response(response, "Lista de categorías")
    
    # Verificaciones
    assert_test(
        response.status_code == 200, 
        "Listar categorías exitoso"
    )
    
    if response.status_code == 200:
        data = response.json()
        assert_test(isinstance(data, list), "La respuesta es una lista")
        
        # Verificar estructura de categorías
        if data:
            first_cat = data[0]
            assert_test("id" in first_cat, "Categoría tiene ID")
            assert_test("nombre" in first_cat, "Categoría tiene nombre")
    
    return response.json() if response.status_code == 200 else None

def test_get_categoria(id_categoria):
    """Prueba obtener una categoría específica por ID"""
    print(f"\n📁 Testing GET /api/categories/{id_categoria}")
    response = requests.get(f"{CATEGORY_URL}/{id_categoria}")
    print_response(response, f"Categoría {id_categoria}")
    
    # Verificaciones
    assert_test(
        response.status_code == 200, 
        f"Obtener categoría {id_categoria} exitoso"
    )
    
    if response.status_code == 200:
        data = response.json()
        assert_test("id" in data and data["id"] == id_categoria, 
                  f"ID corresponde a {id_categoria}")
        assert_test("nombre" in data, "Categoría tiene nombre")
    
    return response.json() if response.status_code == 200 else None

def test_error_handling():
    """Prueba manejo de errores en los endpoints"""
    print("\n🧪 Testing error handling")
    
    # Documento inexistente
    print("Probando documento inexistente (ID 999999)")
    response = requests.get(f"{DOCUMENT_URL}/999999")
    print_response(response, "Documento inexistente")
    assert_test(response.status_code == 404, "Retorna 404 para documento inexistente")
    
    # Categoría inexistente
    print("Probando categoría inexistente (ID 999999)")
    response = requests.get(f"{CATEGORY_URL}/999999")
    print_response(response, "Categoría inexistente")
    assert_test(response.status_code == 404, "Retorna 404 para categoría inexistente")
    
    # Parámetros inválidos en búsqueda
    print("Probando búsqueda con parámetros inválidos")
    response = requests.post(SEARCH_URL, json={"invalid": "params"})
    print_response(response, "Búsqueda con parámetros inválidos")
    assert_test(response.status_code in [400, 422], 
              "Retorna error para parámetros inválidos")

def run_all_tests():
    """Ejecuta todas las pruebas en secuencia"""
    print("\n🔬 INICIANDO PRUEBAS DE LA API\n")
    
    # Obtener categorías para las pruebas
    categorias = test_list_categorias()
    id_categoria_test = categorias[0]["id"] if categorias and len(categorias) > 0 else None
    
    # Pruebas de documentos
    documentos = test_list_documentos(limit=5)
    if documentos and len(documentos) > 0:
        test_get_documento(documentos[0]["id"])
    
    # Pruebas con categoría si existe
    if id_categoria_test:
        test_get_categoria(id_categoria_test)
        test_list_documentos(id_categoria=id_categoria_test, limit=3)
        test_search_documentos("test", id_categoria=id_categoria_test, limit=3)
    
    # Pruebas de búsqueda
    test_search_documentos("documento de prueba")
    
    # Pruebas de manejo de errores
    test_error_handling()
    
    # Resumen de resultados
    print("\n📊 RESUMEN DE PRUEBAS")
    print(f"Total de pruebas: {test_results['total']}")
    print(f"Pruebas exitosas: {test_results['passed']}")
    print(f"Pruebas fallidas: {test_results['failed']}")
    
    success_rate = test_results['passed'] / test_results['total'] * 100 if test_results['total'] > 0 else 0
    print(f"Tasa de éxito: {success_rate:.2f}%")

# Ejecutar pruebas
if __name__ == "__main__":
    # Para pruebas individuales:
    # test_get_documento(1)
    # test_list_documentos()
    # test_list_documentos(id_categoria=2, limit=5)
    # test_search_documentos("inteligencia artificial")
    
    # Para ejecutar todas las pruebas:
    run_all_tests()