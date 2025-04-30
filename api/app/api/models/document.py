from typing import Optional, List
from datetime import date
from pydantic import BaseModel

class ResumenBase(BaseModel):
    texto_resumen: str

class Resumen(ResumenBase):
    id: int
    id_documento: int
    
class CategoriaBase(BaseModel):
    nombre: str

class Categoria(CategoriaBase):
    id: int

class DocumentoBase(BaseModel):
    titulo: str
    autor: Optional[List[str]] = []  # Ahora es una lista de autores
    fecha_publicacion: date
    url_fuente: Optional[str] = None

class DocumentoCreate(DocumentoBase):
    id_categoria: Optional[int] = None
    texto_resumen: Optional[str] = None

class Documento(DocumentoBase):
    id: int
    categoria: Optional[Categoria] = None
    resumen: Optional[Resumen] = None
    
    class Config:
        orm_mode = True