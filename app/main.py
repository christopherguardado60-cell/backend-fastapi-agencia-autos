from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.database import engine, Base
from app.cars.routes import router as cars_router
from app.clients.routes import router as clients_router
from app.rentals.routes import router as rentals_router

load_dotenv()

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=os.getenv("APP_TITLE", "Agencia de Alquiler de Autos API"),
    version="1.0.0",
    description="API REST para la gestión de una agencia de alquiler de autos",
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "True") == "True" else None,
    redoc_url="/redoc" if os.getenv("ENABLE_DOCS", "True") == "True" else None,
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(cars_router, prefix="/api/v1/cars", tags=["Autos"])
app.include_router(clients_router, prefix="/api/v1/clients", tags=["Clientes"])
app.include_router(rentals_router, prefix="/api/v1/rentals", tags=["Alquileres"])

@app.get("/")
async def root():
    """Endpoint de verificación de estado de la API"""
    return {
        "status": "ok",
        "message": "API Agencia de Autos funcionando correctamente",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Endpoint para health check"""
    return {"status": "healthy"}