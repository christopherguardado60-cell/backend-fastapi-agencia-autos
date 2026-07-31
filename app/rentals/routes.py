from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.rentals import models, schemas
from app.cars import models as car_models
from app.clients import models as client_models

# ¡Aquí está el TAG para que aparezca en /docs!
router = APIRouter(prefix="/rentals", tags=["Rentals"])

@router.post("/", response_model=schemas.RentalResponse, status_code=201)
def create_rental(rental: schemas.RentalCreate, db: Session = Depends(get_db)):
    car = db.query(car_models.Car).filter(car_models.Car.id == rental.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    client = db.query(client_models.Client).filter(client_models.Client.id == rental.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db_rental = models.Rental(**rental.dict())
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental

@router.get("/", response_model=List[schemas.RentalResponse])
def get_rentals(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Rental)
    
    if status:
        query = query.filter(models.Rental.status == status)
    
    if client_id:
        query = query.filter(models.Rental.client_id == client_id)
        
    return query.offset(skip).limit(limit).all()

@router.get("/{rental_id}", response_model=schemas.RentalResponse)
def get_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Alquiler no encontrado")
    return rental

@router.put("/{rental_id}", response_model=schemas.RentalResponse)
def update_rental(rental_id: int, rental_update: schemas.RentalUpdate, db: Session = Depends(get_db)):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Alquiler no encontrado")
    
    for key, value in rental_update.dict(exclude_unset=True).items():
        setattr(rental, key, value)
        
    db.commit()
    db.refresh(rental)
    return rental

@router.delete("/{rental_id}", status_code=204)
def delete_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Alquiler no encontrado")
    db.delete(rental)
    db.commit()
    return None