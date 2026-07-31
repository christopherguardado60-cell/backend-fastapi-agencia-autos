from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.rentals.routes import router as rentals_router
from app.cars.routes import router as cars_router
from app.clients.routes import router as clients_router
from app import errors

# Crear tablas en la base de datos (Opcional si usas Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Agencia de Autos",
    description="Sistema de gestión de alquileres, autos y clientes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración de CORS (Para permitir conexiones desde el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MANEJO GLOBAL DE ERRORES (Consistente)
@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error interno del servidor: {str(exc)}"}
    )

# Registro de Routers
app.include_router(cars_router)
app.include_router(clients_router)
app.include_router(rentals_router)

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Bienvenido a la API de la Agencia de Autos"}