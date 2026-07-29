from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class RentalStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"  # Auto entregado al cliente
    COMPLETED = "completed"  # Auto devuelto
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    rental_code = Column(String(20), unique=True, nullable=False, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    return_date = Column(Date)  # Fecha real de devolución
    rental_status = Column(Enum(RentalStatus), default=RentalStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    total_price = Column(Float, nullable=False)
    deposit_amount = Column(Float, default=0.0)  # Depósito de seguridad
    insurance_included = Column(Boolean, default=True)
    insurance_cost = Column(Float, default=0.0)
    extra_charges = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    car = relationship("Car", back_populates="rentals")
    client = relationship("Client", back_populates="rentals")