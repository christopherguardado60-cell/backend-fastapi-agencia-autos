from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

class AppError(Exception):
    """Excepción base de la aplicación"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class CarNotFoundError(AppError):
    def __init__(self, car_id: int):
        super().__init__(
            message=f"Auto con ID {car_id} no encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )

class ClientNotFoundError(AppError):
    def __init__(self, client_id: int):
        super().__init__(
            message=f"Cliente con ID {client_id} no encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )

class RentalNotFoundError(AppError):
    def __init__(self, rental_id: int):
        super().__init__(
            message=f"Alquiler con ID {rental_id} no encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )

class CarNotAvailableError(AppError):
    def __init__(self, car_id: int, start_date, end_date):
        super().__init__(
            message=f"Auto {car_id} no está disponible para las fechas {start_date} - {end_date}",
            status_code=status.HTTP_409_CONFLICT
        )

class DuplicateCarError(AppError):
    def __init__(self, license_plate: str):
        super().__init__(
            message=f"Ya existe un auto con la placa {license_plate}",
            status_code=status.HTTP_409_CONFLICT
        )

class DuplicateClientError(AppError):
    def __init__(self, email: str):
        super().__init__(
            message=f"Ya existe un cliente con el email {email}",
            status_code=status.HTTP_409_CONFLICT
        )

class DuplicateLicenseError(AppError):
    def __init__(self, license_number: str):
        super().__init__(
            message=f"Ya existe un cliente con la licencia {license_number}",
            status_code=status.HTTP_409_CONFLICT
        )

# Manejo de errores global
def handle_errors(app):
    @app.exception_handler(AppError)
    async def app_error_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "body": exc.body}
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Conflicto de integridad de datos"}
        )