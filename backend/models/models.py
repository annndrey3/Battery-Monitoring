from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Text, ForeignKey, CheckConstraint
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    measurements = relationship("Measurement", back_populates="measured_by_user")
    resolved_incidents = relationship("Incident", foreign_keys="Incident.resolved_by", back_populates="resolver")

class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    batteries = relationship("Battery", back_populates="equipment", cascade="all, delete-orphan")

class Battery(Base):
    __tablename__ = "batteries"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False)
    serial_number = Column(String(50), unique=True, nullable=False)
    capacity = Column(Decimal(10, 2), nullable=False)
    voltage_nominal = Column(Decimal(5, 2), nullable=False)
    install_date = Column(Date, nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    equipment = relationship("Equipment", back_populates="batteries")
    measurements = relationship("Measurement", back_populates="battery", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="battery")

class Measurement(Base):
    __tablename__ = "measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    battery_id = Column(Integer, ForeignKey("batteries.id", ondelete="CASCADE"), nullable=False)
    voltage = Column(Decimal(6, 3), nullable=False)
    current = Column(Decimal(8, 3), nullable=False)
    charge_level = Column(Decimal(5, 2), nullable=False)
    temperature = Column(Decimal(5, 2), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    measured_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    battery = relationship("Battery", back_populates="measurements")
    measured_by_user = relationship("User", back_populates="measurements")
    incidents = relationship("Incident", back_populates="measurement")
    
    __table_args__ = (
        CheckConstraint('voltage > 0', name='check_voltage_positive'),
        CheckConstraint('current >= 0', name='check_current_non_negative'),
        CheckConstraint('charge_level >= 0 AND charge_level <= 100', name='check_charge_level_range'),
        CheckConstraint('temperature <= 80', name='check_temperature_max'),
    )

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    measurement_id = Column(Integer, ForeignKey("measurements.id", ondelete="SET NULL"), nullable=True)
    battery_id = Column(Integer, ForeignKey("batteries.id", ondelete="CASCADE"), nullable=True)
    incident_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    measurement = relationship("Measurement", back_populates="incidents")
    battery = relationship("Battery", back_populates="incidents")
    resolver = relationship("User", foreign_keys=[resolved_by], back_populates="resolved_incidents")
