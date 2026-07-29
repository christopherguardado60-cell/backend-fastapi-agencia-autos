from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.cars import models, schemas
from app.errors import CarNotFoundError, DuplicateCarError
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/", response_model=schemas.CarResponse, status_code=201)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    """Crear un nuevo auto"""
    try:
        db_car = models.Car(**car.dict())
        db.add(db_car)
        db.commit()
        db.refresh(db_car)
        return db_car
    except IntegrityError:
        db.rollback()
        raise DuplicateCarError(car.license_plate)

@router.get("/", response_model=List[schemas.CarResponse])
def get_cars(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    brand: Optional[str] = None,
    model: Optional[str] = None,
    status: Optional[schemas.CarStatus] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    available: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de autos con filtros opcionales"""
    query = db.query(models.Car)

    # Aplicar filtros
    if brand:
        query = query.filter(models.Car.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(models.Car.model.ilike(f"%{model}%"))
    if status:
        query = query.filter(models.Car.status == status)
    if min_price:
        query = query.filter(models.Car.daily_price >= min_price)
    if max_price:
        query = query.filter(models.Car.daily_price <= max_price)
    if available is True:
        query = query.filter(models.Car.status == models.CarStatus.AVAILABLE)

    return query.offset(skip).limit(limit).all()

@router.get("/{car_id}", response_model=schemas.CarResponse)
def get_car(car_id: int, db: Session = Depends(get_db)):
    """Obtener un auto por su ID"""
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise CarNotFoundError(car_id)
    return car

@router.get("/license/{license_plate}", response_model=schemas.CarResponse)
def get_car_by_license(license_plate: str, db: Session = Depends(get_db)):
    """Obtener un auto por su placa"""
    car = db.query(models.Car).filter(models.Car.license_plate == license_plate.upper()).first()
    if not car:
        raise HTTPException(status_code=404, detail=f"Auto con placa {license_plate} no encontrado")
    return car

@router.put("/{car_id}", response_model=schemas.CarResponse)
def update_car(car_id: int, car_update: schemas.CarUpdate, db: Session = Depends(get_db)):
    """Actualizar completamente un auto"""
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise CarNotFoundError(car_id)

    update_data = car_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(car, field, value)

    try:
        db.commit()
        db.refresh(car)
        return car
    except IntegrityError:
        db.rollback()
        raise DuplicateCarError(car_update.license_plate)

@router.patch("/{car_id}", response_model=schemas.CarResponse)
def partial_update_car(car_id: int, car_update: schemas.CarUpdate, db: Session = Depends(get_db)):
    """Actualizar parcialmente un auto"""
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise CarNotFoundError(car_id)

    update_data = car_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(car, field, value)

    try:
        db.commit()
        db.refresh(car)
        return car
    except IntegrityError:
        db.rollback()
        raise DuplicateCarError(car_update.license_plate)

@router.delete("/{car_id}", status_code=204)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    """Eliminar un auto"""
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise CarNotFoundError(car_id)

    db.delete(car)
    db.commit()
    return None

@router.patch("/{car_id}/status", response_model=schemas.CarResponse)
def update_car_status(
    car_id: int,
    status: schemas.CarStatus,
    db: Session = Depends(get_db)
):
    """Actualizar el estado de un auto"""
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise CarNotFoundError(car_id)

    car.status = status
    db.commit()
    db.refresh(car)
    return car