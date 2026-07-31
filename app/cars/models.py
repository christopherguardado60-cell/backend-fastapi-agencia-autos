from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class CarStatus(str, enum.Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"

class TransmissionType(str, enum.Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"

class FuelType(str, enum.Enum):
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False, index=True)
    color = Column(String(30))
    transmission = Column(Enum(TransmissionType), nullable=False)
    fuel_type = Column(Enum(FuelType), nullable=False)
    daily_price = Column(Float, nullable=False)
    seats = Column(Integer, nullable=False)
    doors = Column(Integer)
    air_conditioning = Column(Boolean, default=True)
    has_gps = Column(Boolean, default=False)
    has_bluetooth = Column(Boolean, default=False)
    status = Column(Enum(CarStatus), default=CarStatus.AVAILABLE)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    rentals = relationship("Rental", back_populates="car", cascade="all, delete-orphan")
    rentals = relationship("Rental", back_populates="car")