from fastapi import APIRouter, HTTPException, Path
from typing import List

from app.api.models.document import Documento
from app.db.database import execute_query

router = APIRouter()

@router.get("/{id_documento}", response_model=Documento)
async def get_document(id_documento: int = Path(..., description="ID del documento a recuperar")):
    """
    Recupera un documento específico por su ID, incluyendo su resumen y categoría.
    """
    try:
        # Obtener información del documento
        doc_sql = """
        SELECT d.id, d.titulo, d.autor, d.fecha_publicacion, d.url_fuente, 
               c.id as id_categoria, c.nombre as categoria_nombre,
               r.id as resumen_id, r.texto_resumen
        FROM documento d
        LEFT JOIN categoria c ON d.id_categoria = c.id
        LEFT JOIN resumen r ON d.id = r.id_documento
        WHERE d.id = %s
        """
        
        result = execute_query(doc_sql, [id_documento], fetchone=True)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Documento con ID {id_documento} no encontrado")
        
        # Si el autor es una cadena, convertirlo a lista. Si es None, usar lista vacía
        autor = []
        if result[2]:
            autor = [result[2]]
        
        # Construir el objeto documento con su categoría y resumen
        documento = {
            "id": result[0],
            "titulo": result[1],
            "autor": autor,  # Lista de autores
            "fecha_publicacion": result[3],
            "url_fuente": result[4],
            "categoria": {
                "id": result[5],
                "nombre": result[6]
            } if result[5] else None,
            "resumen": {
                "id": result[7],
                "id_documento": result[0],
                "texto_resumen": result[8]
            } if result[7] else None
        }
        
        return documento
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al recuperar el documento: {str(e)}")

@router.get("/", response_model=List[Documento])
async def list_documents(id_categoria: int = None, limit: int = 20, offset: int = 0):
    """
    Recupera una lista de documentos, opcionalmente filtrados por categoría.
    """
    try:
        # Construir consulta SQL base
        sql = """
        SELECT d.id, d.titulo, d.autor, d.fecha_publicacion, d.url_fuente, 
               c.id as id_categoria, c.nombre as categoria_nombre, 
               r.id as resumen_id, r.texto_resumen
        FROM documento d
        LEFT JOIN categoria c ON d.id_categoria = c.id
        LEFT JOIN resumen r ON d.id = r.id_documento
        """
        
        params = []
        
        # Añadir filtro por categoría si se especificó
        if id_categoria:
            sql += " WHERE d.id_categoria = %s"
            params.append(id_categoria)
        
        # Añadir límite y offset para paginación
        sql += f" ORDER BY d.fecha_publicacion DESC LIMIT {limit} OFFSET {offset}"
        
        results = execute_query(sql, params)
        
        # Formatear resultados
        documentos = []
        for row in results:
            # Manejo consistente del campo autor
            autor = []
            if row[2]:
                autor = [row[2]]

            documentos.append({
                "id": row[0],
                "titulo": row[1],
                "autor": autor,  # Lista de autores
                "fecha_publicacion": row[3],
                "url_fuente": row[4],
                "categoria": {
                    "id": row[5],
                    "nombre": row[6]
                } if row[5] else None,
                "resumen": {
                    "id": row[7],
                    "id_documento": row[0],
                    "texto_resumen": row[8]
                } if row[7] else None
            })
        return documentos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar documentos: {str(e)}")