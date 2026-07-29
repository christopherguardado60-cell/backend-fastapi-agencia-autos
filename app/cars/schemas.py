from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from enum import Enum

class CarStatus(str, Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"

class TransmissionType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"

class FuelType(str, Enum):
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"

class CarBase(BaseModel):
    brand: str = Field(..., min_length=2, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1900, le=datetime.now().year + 1)
    license_plate: str = Field(..., min_length=5, max_length=20)
    color: Optional[str] = Field(None, max_length=30)
    transmission: TransmissionType
    fuel_type: FuelType
    daily_price: float = Field(..., gt=0)
    seats: int = Field(..., ge=1, le=9)
    doors: Optional[int] = Field(None, ge=2, le=5)
    air_conditioning: bool = True
    has_gps: bool = False
    has_bluetooth: bool = False
    status: CarStatus = CarStatus.AVAILABLE
    description: Optional[str] = None

    @validator('license_plate')
    def validate_license_plate(cls, v):
        # Validación básica de placa (puedes ajustar según tu país)
        if len(v) < 5:
            raise ValueError('La placa debe tener al menos 5 caracteres')
        return v.upper()

class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    brand: Optional[str] = Field(None, min_length=2, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 1)
    license_plate: Optional[str] = Field(None, min_length=5, max_length=20)
    color: Optional[str] = Field(None, max_length=30)
    transmission: Optional[TransmissionType] = None
    fuel_type: Optional[FuelType] = None
    daily_price: Optional[float] = Field(None, gt=0)
    seats: Optional[int] = Field(None, ge=1, le=9)
    doors: Optional[int] = Field(None, ge=2, le=5)
    air_conditioning: Optional[bool] = None
    has_gps: Optional[bool] = None
    has_bluetooth: Optional[bool] = None
    status: Optional[CarStatus] = None
    description: Optional[str] = None

    @validator('license_plate')
    def validate_license_plate(cls, v):
        if v is not None:
            if len(v) < 5:
                raise ValueError('La placa debe tener al menos 5 caracteres')
            return v.upper()
        return v

class CarResponse(CarBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True