from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, date, timedelta
import random
import string

from app.database import get_db
from app.rentals import models, schemas
from app.cars import models as car_models
from app.clients import models as client_models
from app.errors import (
    RentalNotFoundError,
    CarNotFoundError,
    ClientNotFoundError,
    CarNotAvailableError
)

router = APIRouter()

def generate_rental_code():
    """Generar un código único para el alquiler"""
    prefix = "RENT"
    timestamp = datetime.now().strftime("%y%m%d")
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_chars}"

def calculate_total_price(car, start_date, end_date, insurance_included, insurance_cost):
    """Calcular el precio total del alquiler"""
    nights = (end_date - start_date).days
    base_price = nights * car.daily_price
    insurance_total = insurance_cost if insurance_included else 0
    return base_price + insurance_total

def check_car_availability(db, car_id, start_date, end_date, exclude_rental_id=None):
    """Verificar si un auto está disponible para las fechas dadas"""
    query = db.query(models.Rental).filter(
        models.Rental.car_id == car_id,
        models.Rental.rental_status.in_([
            models.RentalStatus.CONFIRMED,
            models.RentalStatus.ACTIVE
        ])
    )

    if exclude_rental_id:
        query = query.filter(models.Rental.id != exclude_rental_id)

    # Verificar solapamiento de fechas
    overlapping = query.filter(
        or_(
            and_(
                models.Rental.start_date <= start_date,
                models.Rental.end_date >= start_date
            ),
            and_(
                models.Rental.start_date <= end_date,
                models.Rental.end_date >= end_date
            ),
            and_(
                models.Rental.start_date >= start_date,
                models.Rental.end_date <= end_date
            )
        )
    ).first()

    return overlapping is None

@router.post("/", response_model=schemas.RentalResponse, status_code=201)
def create_rental(rental: schemas.RentalCreate, db: Session = Depends(get_db)):
    """Crear un nuevo alquiler"""
    # Validar que el auto existe
    car = db.query(car_models.Car).filter(car_models.Car.id == rental.car_id).first()
    if not car:
        raise CarNotFoundError(rental.car_id)

    # Validar que el cliente existe
    client = db.query(client_models.Client).filter(
        client_models.Client.id == rental.client_id,
        client_models.Client.is_active == True
    ).first()
    if not client:
        raise ClientNotFoundError(rental.client_id)

    # Verificar disponibilidad del auto
    if not check_car_availability(db, rental.car_id, rental.start_date, rental.end_date):
        raise CarNotAvailableError(rental.car_id, rental.start_date, rental.end_date)

    # Calcular precio total
    total_price = calculate_total_price(
        car,
        rental.start_date,
        rental.end_date,
        rental.insurance_included,
        rental.insurance_cost
    )

    # Crear el alquiler
    db_rental = models.Rental(
        rental_code=generate_rental_code(),
        **rental.dict(),
        total_price=total_price,
        rental_status=models.RentalStatus.CONFIRMED,
        payment_status=models.PaymentStatus.PENDING
    )

    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental

@router.get("/", response_model=List[schemas.RentalResponse])
def get_rentals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    car_id: Optional[int] = None,
    client_id: Optional[int] = None,
    status: Optional[schemas.RentalStatus] = None,
    payment_status: Optional[schemas.PaymentStatus] = None,
    start_date_min: Optional[date] = None,
    start_date_max: Optional[date] = None,
    end_date_min: Optional[date] = None,
    end_date_max: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de alquileres con filtros"""
    query = db.query(models.Rental)

    if car_id:
        query = query.filter(models.Rental.car_id == car_id)
    if client_id:
        query = query.filter(models.Rental.client_id == client_id)
    if status:
        query = query.filter(models.Rental.rental_status == status)
    if payment_status:
        query = query.filter(models.Rental.payment_status == payment_status)
    if start_date_min:
        query = query.filter(models.Rental.start_date >= start_date_min)
    if start_date_max:
        query = query.filter(models.Rental.start_date <= start_date_max)
    if end_date_min:
        query = query.filter(models.Rental.end_date >= end_date_min)
    if end_date_max:
        query = query.filter(models.Rental.end_date <= end_date_max)

    return query.offset(skip).limit(limit).all()

@router.get("/{rental_id}", response_model=schemas.RentalResponse)
def get_rental(rental_id: int, db: Session = Depends(get_db)):
    """Obtener un alquiler por su ID"""
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise RentalNotFoundError(rental_id)
    return rental

@router.get("/code/{rental_code}", response_model=schemas.RentalResponse)
def get_rental_by_code(rental_code: str, db: Session = Depends(get_db)):
    """Obtener un alquiler por su código"""
    rental = db.query(models.Rental).filter(models.Rental.rental_code == rental_code).first()
    if not rental:
        raise HTTPException(status_code=404, detail=f"Alquiler con código {rental_code} no encontrado")
    return rental

@router.put("/{rental_id}", response_model=schemas.RentalResponse)
def update_rental(
    rental_id: int,
    rental_update: schemas.RentalUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un alquiler"""
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise RentalNotFoundError(rental_id)

    # Si se cambian las fechas o el auto, verificar disponibilidad
    if (rental_update.start_date or rental_update.end_date or rental_update.car_id):
        car_id = rental_update.car_id or rental.car_id
        start_date = rental_update.start_date or rental.start_date
        end_date = rental_update.end_date or rental.end_date

        if not check_car_availability(db, car_id, start_date, end_date, rental_id):
            raise CarNotAvailableError(car_id, start_date, end_date)

        # Recalcular precio si cambian fechas o auto
        car = db.query(car_models.Car).filter(car_models.Car.id == car_id).first()
        if car and (rental_update.start_date or rental_update.end_date):
            total_price = calculate_total_price(
                car,
                start_date,
                end_date,
                rental.insurance_included,
                rental.insurance_cost
            )
            setattr(rental, 'total_price', total_price)

    # Actualizar campos
    update_data = rental_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rental, field, value)

    db.commit()
    db.refresh(rental)
    return rental

@router.patch("/{rental_id}", response_model=schemas.RentalResponse)
def partial_update_rental(
    rental_id: int,
    rental_update: schemas.RentalUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar parcialmente un alquiler"""
    return update_rental(rental_id, rental_update, db)

@router.patch("/{rental_id}/status", response_model=schemas.RentalResponse)
def update_rental_status(
    rental_id: int,
    status: schemas.RentalStatus,
    db: Session = Depends(get_db)
):
    """Actualizar el estado de un alquiler"""
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise RentalNotFoundError(rental_id)

    rental.rental_status = status

    # Si se completa el alquiler, registrar fecha de devolución y actualizar estado del auto
    if status == models.RentalStatus.COMPLETED:
        rental.return_date = date.today()
        # Cambiar estado del auto a disponible
        car = db.query(car_models.Car).filter(car_models.Car.id == rental.car_id).first()
        if car:
            car.status = car_models.CarStatus.AVAILABLE

    db.commit()
    db.refresh(rental)
    return rental

@router.patch("/{rental_id}/payment", response_model=schemas.RentalResponse)
def update_payment_status(
    rental_id: int,
    payment_status: schemas.PaymentStatus,
    db: Session = Depends(get_db)
):
    """Actualizar el estado de pago de un alquiler"""
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise RentalNotFoundError(rental_id)

    rental.payment_status = payment_status
    db.commit()
    db.refresh(rental)
    return rental

@router.delete("/{rental_id}", status_code=204)
def cancel_rental(rental_id: int, db: Session = Depends(get_db)):
    """Cancelar un alquiler"""
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise RentalNotFoundError(rental_id)

    # Solo se pueden cancelar alquileres que no estén activos o completados
    if rental.rental_status in [models.RentalStatus.ACTIVE, models.RentalStatus.COMPLETED]:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede cancelar un alquiler en estado {rental.rental_status.value}"
        )

    rental.rental_status = models.RentalStatus.CANCELLED
    db.commit()
    return None

@router.get("/statistics", response_model=schemas.RentalStatistics)
def get_rental_statistics(db: Session = Depends(get_db)):
    """Obtener estadísticas de alquileres"""
    total = db.query(models.Rental).count()
    active = db.query(models.Rental).filter(
        models.Rental.rental_status == models.RentalStatus.ACTIVE
    ).count()
    completed = db.query(models.Rental).filter(
        models.Rental.rental_status == models.RentalStatus.COMPLETED
    ).count()
    cancelled = db.query(models.Rental).filter(
        models.Rental.rental_status == models.RentalStatus.CANCELLED
    ).count()

    revenue = db.query(func.sum(models.Rental.total_price)).filter(
        models.Rental.rental_status == models.RentalStatus.COMPLETED,
        models.Rental.payment_status == models.PaymentStatus.PAID
    ).scalar() or 0.0

    pending_payments = db.query(func.sum(models.Rental.total_price)).filter(
        models.Rental.payment_status == models.PaymentStatus.PENDING,
        models.Rental.rental_status.in_([
            models.RentalStatus.CONFIRMED,
            models.RentalStatus.ACTIVE,
            models.RentalStatus.COMPLETED
        ])
    ).scalar() or 0.0

    return schemas.RentalStatistics(
        total_rentals=total,
        active_rentals=active,
        completed_rentals=completed,
        cancelled_rentals=cancelled,
        total_revenue=revenue,
        pending_payments=pending_payments
    )

@router.get("/client/{client_id}/history", response_model=List[schemas.RentalResponse])
def get_client_rental_history(
    client_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Obtener historial de alquileres de un cliente"""
    client = db.query(client_models.Client).filter(
        client_models.Client.id == client_id
    ).first()
    if not client:
        raise ClientNotFoundError(client_id)

    return db.query(models.Rental).filter(
        models.Rental.client_id == client_id
    ).order_by(models.Rental.created_at.desc()).limit(limit).all()