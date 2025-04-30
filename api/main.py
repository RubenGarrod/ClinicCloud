from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import search, documents, categories

app = FastAPI(
    title="ClinicCloud API",
    description="API para el motor de búsqueda de información médica con procesamiento de lenguaje natural",
    version="0.1.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringe a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de los endpoints
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de ClinicCloud"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)