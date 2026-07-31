from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional
from app.rentals.models import RentalStatus, PaymentStatus

class RentalBase(BaseModel):
    car_id: int
    client_id: int
    start_date: date
    end_date: date
    total_price: float = Field(..., gt=0, description="El precio debe ser mayor a 0")
    insurance_included: bool = True

    # REGLA DE NEGOCIO: Validar que la fecha de inicio no sea posterior a la de fin
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class RentalCreate(RentalBase):
    pass

class RentalUpdate(BaseModel):
    status: Optional[RentalStatus] = None
    payment_status: Optional[PaymentStatus] = None
    end_date: Optional[date] = None

class RentalResponse(RentalBase):
    id: int
    status: RentalStatus
    payment_status: PaymentStatus
    created_at: datetime

    class Config:
        orm_mode = True