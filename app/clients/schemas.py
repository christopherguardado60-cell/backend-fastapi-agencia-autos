from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime, date
from typing import Optional
from enum import Enum

class DocumentType(str, Enum):
    DNI = "dni"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"

class ClientBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=20)
    document_type: DocumentType
    document_number: str = Field(..., min_length=5, max_length=30)
    driver_license_number: str = Field(..., min_length=5, max_length=30)
    driver_license_expiry: date
    address: Optional[str] = Field(None, max_length=200)
    birth_date: Optional[date] = None
    is_active: bool = True

    @validator('driver_license_expiry')
    def validate_license_expiry(cls, v):
        if v <= date.today():
            raise ValueError('La licencia de conducir debe tener fecha de vencimiento futura')
        return v

    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v and v >= date.today():
            raise ValueError('La fecha de nacimiento debe ser anterior a hoy')
        if v and (date.today().year - v.year) < 18:
            raise ValueError('El cliente debe ser mayor de 18 años')
        return v

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=7, max_length=20)
    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = Field(None, min_length=5, max_length=30)
    driver_license_number: Optional[str] = Field(None, min_length=5, max_length=30)
    driver_license_expiry: Optional[date] = None
    address: Optional[str] = Field(None, max_length=200)
    birth_date: Optional[date] = None
    is_active: Optional[bool] = None

class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True