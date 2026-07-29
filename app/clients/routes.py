from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.clients import models, schemas
from app.errors import ClientNotFoundError, DuplicateClientError, DuplicateLicenseError
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/", response_model=schemas.ClientResponse, status_code=201)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    """Crear un nuevo cliente"""
    try:
        db_client = models.Client(**client.dict())
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    except IntegrityError as e:
        db.rollback()
        if "email" in str(e):
            raise DuplicateClientError(client.email)
        elif "driver_license_number" in str(e):
            raise DuplicateLicenseError(client.driver_license_number)
        raise

@router.get("/", response_model=List[schemas.ClientResponse])
def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de clientes"""
    query = db.query(models.Client)

    if search:
        query = query.filter(
            (models.Client.first_name.ilike(f"%{search}%")) |
            (models.Client.last_name.ilike(f"%{search}%")) |
            (models.Client.email.ilike(f"%{search}%"))
        )

    if is_active is not None:
        query = query.filter(models.Client.is_active == is_active)

    return query.offset(skip).limit(limit).all()

@router.get("/{client_id}", response_model=schemas.ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Obtener un cliente por su ID"""
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise ClientNotFoundError(client_id)
    return client

@router.get("/license/{license_number}", response_model=schemas.ClientResponse)
def get_client_by_license(license_number: str, db: Session = Depends(get_db)):
    """Obtener un cliente por su número de licencia"""
    client = db.query(models.Client).filter(
        models.Client.driver_license_number == license_number
    ).first()
    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"Cliente con licencia {license_number} no encontrado"
        )
    return client

@router.put("/{client_id}", response_model=schemas.ClientResponse)
def update_client(
    client_id: int,
    client_update: schemas.ClientUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar completamente un cliente"""
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise ClientNotFoundError(client_id)

    update_data = client_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    try:
        db.commit()
        db.refresh(client)
        return client
    except IntegrityError as e:
        db.rollback()
        if "email" in str(e):
            raise DuplicateClientError(client_update.email)
        elif "driver_license_number" in str(e):
            raise DuplicateLicenseError(client_update.driver_license_number)
        raise

@router.patch("/{client_id}", response_model=schemas.ClientResponse)
def partial_update_client(
    client_id: int,
    client_update: schemas.ClientUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar parcialmente un cliente"""
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise ClientNotFoundError(client_id)

    update_data = client_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    try:
        db.commit()
        db.refresh(client)
        return client
    except IntegrityError as e:
        db.rollback()
        if "email" in str(e) and client_update.email:
            raise DuplicateClientError(client_update.email)
        if "driver_license_number" in str(e) and client_update.driver_license_number:
            raise DuplicateLicenseError(client_update.driver_license_number)
        raise

@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Eliminar un cliente"""
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise ClientNotFoundError(client_id)

    db.delete(client)
    db.commit()
    return None