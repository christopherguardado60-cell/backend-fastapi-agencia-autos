from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional
from enum import Enum

class RentalStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"

class RentalBase(BaseModel):
    car_id: int
    client_id: int
    start_date: date
    end_date: date
    deposit_amount: Optional[float] = Field(0.0, ge=0)
    insurance_included: bool = True
    insurance_cost: Optional[float] = Field(0.0, ge=0)
    extra_charges: Optional[float] = Field(0.0, ge=0)
    notes: Optional[str] = None

    @validator('end_date')
    def validate_dates(cls, end_date, values):
        if 'start_date' in values and end_date <= values['start_date']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        if 'start_date' in values and (end_date - values['start_date']).days < 1:
            raise ValueError('El alquiler debe ser por al menos 1 día')
        return end_date

    @validator('start_date')
    def validate_start_date(cls, v):
        if v < date.today():
            raise ValueError('La fecha de inicio no puede ser en el pasado')
        return v

class RentalCreate(RentalBase):
    pass

class RentalUpdate(BaseModel):
    car_id: Optional[int] = None
    client_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    return_date: Optional[date] = None
    rental_status: Optional[RentalStatus] = None
    payment_status: Optional[PaymentStatus] = None
    deposit_amount: Optional[float] = Field(None, ge=0)
    insurance_included: Optional[bool] = None
    insurance_cost: Optional[float] = Field(None, ge=0)
    extra_charges: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None

    @validator('end_date')
    def validate_dates(cls, end_date, values):
        if end_date and 'start_date' in values and values['start_date']:
            if end_date <= values['start_date']:
                raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return end_date

class RentalResponse(RentalBase):
    id: int
    rental_code: str
    total_price: float
    rental_status: RentalStatus
    payment_status: PaymentStatus
    return_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RentalWithDetails(RentalResponse):
    car: dict  # Información del auto
    client: dict  # Información del cliente

class RentalStatistics(BaseModel):
    total_rentals: int
    active_rentals: int
    completed_rentals: int
    cancelled_rentals: int
    total_revenue: float
    pending_payments: float