from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.cars import models, schemas

router = APIRouter(prefix="/cars", tags=["Cars"])

@router.post("/", response_model=schemas.CarResponse, status_code=201)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    db_car = models.Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

@router.get("/", response_model=List[schemas.CarResponse])
def get_cars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cars = db.query(models.Car).offset(skip).limit(limit).all()
    return cars

@router.get("/{car_id}", response_model=schemas.CarResponse)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    return car

@router.put("/{car_id}", response_model=schemas.CarResponse)
def update_car(car_id: int, car_update: schemas.CarUpdate, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    for key, value in car_update.dict(exclude_unset=True).items():
        setattr(car, key, value)
        
    db.commit()
    db.refresh(car)
    return car

@router.delete("/{car_id}", status_code=204)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    db.delete(car)
    db.commit()
    return None

# Rutas extra que tenías en la captura:
@router.get("/license/{license_plate}", response_model=schemas.CarResponse)
def get_car_by_license(license_plate: str, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.license_plate == license_plate).first()
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado por matrícula")
    return car

@router.patch("/{car_id}/status", response_model=schemas.CarResponse)
def update_car_status(car_id: int, status_update: dict, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    if "status" in status_update:
        car.status = status_update["status"]
    
    db.commit()
    db.refresh(car)
    return car