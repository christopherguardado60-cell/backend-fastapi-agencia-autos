from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class DocumentType(str, enum.Enum):
    DNI = "dni"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    document_number = Column(String(30), unique=True, nullable=False, index=True)
    driver_license_number = Column(String(30), unique=True, nullable=False)
    driver_license_expiry = Column(Date, nullable=False)
    address = Column(String(200))
    birth_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    rentals = relationship("Rental", back_populates="client", cascade="all, delete-orphan")
    rentals = relationship("Rental", back_populates="client")