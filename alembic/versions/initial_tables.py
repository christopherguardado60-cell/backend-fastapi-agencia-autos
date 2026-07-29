"""initial tables

Revision ID: 001
Revises:
Create Date: 2026-07-28 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Crear enum types
    car_status = ENUM('available', 'rented', 'maintenance', 'out_of_service', name='carstatus')
    car_status.create(op.get_bind())

    transmission_type = ENUM('manual', 'automatic', name='transmissiontype')
    transmission_type.create(op.get_bind())

    fuel_type = ENUM('gasoline', 'diesel', 'electric', 'hybrid', name='fueltype')
    fuel_type.create(op.get_bind())

    document_type = ENUM('dni', 'passport', 'driver_license', name='documenttype')
    document_type.create(op.get_bind())

    rental_status = ENUM('pending', 'confirmed', 'active', 'completed', 'cancelled', 'overdue', name='rentalstatus')
    rental_status.create(op.get_bind())

    payment_status = ENUM('pending', 'partial', 'paid', 'refunded', name='paymentstatus')
    payment_status.create(op.get_bind())

    # Crear tabla cars
    op.create_table(
        'cars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=50), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('license_plate', sa.String(length=20), nullable=False),
        sa.Column('color', sa.String(length=30), nullable=True),
        sa.Column('transmission', transmission_type, nullable=False),
        sa.Column('fuel_type', fuel_type, nullable=False),
        sa.Column('daily_price', sa.Float(), nullable=False),
        sa.Column('seats', sa.Integer(), nullable=False),
        sa.Column('doors', sa.Integer(), nullable=True),
        sa.Column('air_conditioning', sa.Boolean(), nullable=True),
        sa.Column('has_gps', sa.Boolean(), nullable=True),
        sa.Column('has_bluetooth', sa.Boolean(), nullable=True),
        sa.Column('status', car_status, nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('license_plate')
    )
    op.create_index(op.f('ix_cars_id'), 'cars', ['id'], unique=False)
    op.create_index(op.f('ix_cars_license_plate'), 'cars', ['license_plate'], unique=True)

    # Crear tabla clients
    op.create_table(
        'clients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('document_type', document_type, nullable=False),
        sa.Column('document_number', sa.String(length=30), nullable=False),
        sa.Column('driver_license_number', sa.String(length=30), nullable=False),
        sa.Column('driver_license_expiry', sa.Date(), nullable=False),
        sa.Column('address', sa.String(length=200), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_number'),
        sa.UniqueConstraint('driver_license_number'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)
    op.create_index(op.f('ix_clients_email'), 'clients', ['email'], unique=True)
    op.create_index(op.f('ix_clients_document_number'), 'clients', ['document_number'], unique=True)

    # Crear tabla rentals
    op.create_table(
        'rentals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rental_code', sa.String(length=20), nullable=False),
        sa.Column('car_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('return_date', sa.Date(), nullable=True),
        sa.Column('rental_status', rental_status, nullable=True),
        sa.Column('payment_status', payment_status, nullable=True),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('deposit_amount', sa.Float(), nullable=True),
        sa.Column('insurance_included', sa.Boolean(), nullable=True),
        sa.Column('insurance_cost', sa.Float(), nullable=True),
        sa.Column('extra_charges', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rental_code')
    )
    op.create_index(op.f('ix_rentals_id'), 'rentals', ['id'], unique=False)
    op.create_index(op.f('ix_rentals_rental_code'), 'rentals', ['rental_code'], unique=True)

def downgrade():
    op.drop_table('rentals')
    op.drop_table('clients')
    op.drop_table('cars')

    # Eliminar enum types
    ENUM(name='paymentstatus').drop(op.get_bind())
    ENUM(name='rentalstatus').drop(op.get_bind())
    ENUM(name='documenttype').drop(op.get_bind())
    ENUM(name='fueltype').drop(op.get_bind())
    ENUM(name='transmissiontype').drop(op.get_bind())
    ENUM(name='carstatus').drop(op.get_bind())