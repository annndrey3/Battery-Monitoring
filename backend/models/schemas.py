from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# ============ Equipment Schemas ============
class EquipmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=50)
    location: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    status: str = Field(default="active", pattern="^(active|inactive|maintenance)$")

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    location: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|maintenance)$")

class EquipmentResponse(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    battery_count: Optional[int] = 0

    class Config:
        from_attributes = True

# ============ Battery Schemas ============
class BatteryBase(BaseModel):
    equipment_id: int
    serial_number: str = Field(..., min_length=1, max_length=50)
    capacity: Decimal = Field(..., gt=0)
    voltage_nominal: Decimal = Field(..., gt=0)
    install_date: date
    status: str = Field(default="active", pattern="^(active|inactive|maintenance|decommissioned)$")

class BatteryCreate(BatteryBase):
    pass

class BatteryUpdate(BaseModel):
    equipment_id: Optional[int] = None
    serial_number: Optional[str] = Field(None, min_length=1, max_length=50)
    capacity: Optional[Decimal] = Field(None, gt=0)
    voltage_nominal: Optional[Decimal] = Field(None, gt=0)
    install_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|maintenance|decommissioned)$")

class BatteryResponse(BatteryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    equipment_name: Optional[str] = None

    class Config:
        from_attributes = True

# ============ Measurement Schemas ============
class MeasurementBase(BaseModel):
    battery_id: int
    voltage: Decimal = Field(..., gt=0)
    current: Decimal = Field(..., ge=0)
    charge_level: Decimal = Field(..., ge=0, le=100)
    temperature: Decimal = Field(..., le=80)

class MeasurementCreate(MeasurementBase):
    measured_by: Optional[int] = None

class MeasurementResponse(MeasurementBase):
    id: int
    timestamp: datetime
    measured_by: Optional[int] = None
    operator_name: Optional[str] = None
    battery_serial: Optional[str] = None

    class Config:
        from_attributes = True

class MeasurementHistory(BaseModel):
    hour: datetime
    serial_number: str
    avg_voltage: Decimal
    avg_current: Decimal
    avg_charge: Decimal
    avg_temp: Decimal
    measurement_count: int

# ============ Incident Schemas ============
class IncidentBase(BaseModel):
    incident_type: str = Field(..., pattern="^(overheat|low_charge|voltage_spike|current_surge|critical_failure|warning)$")
    description: str = Field(..., min_length=1)
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")

class IncidentCreate(IncidentBase):
    measurement_id: Optional[int] = None
    battery_id: int

class IncidentUpdate(BaseModel):
    description: Optional[str] = None
    is_resolved: Optional[bool] = None
    resolved_by: Optional[int] = None

class IncidentResponse(IncidentBase):
    id: int
    measurement_id: Optional[int] = None
    battery_id: Optional[int] = None
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    created_at: datetime
    battery_serial: Optional[str] = None
    equipment_name: Optional[str] = None

    class Config:
        from_attributes = True

# ============ Report Schemas ============
class ChargeReport(BaseModel):
    equipment_name: str
    location: str
    battery_count: int
    avg_charge_level: Decimal
    min_charge_level: Decimal
    max_charge_level: Decimal

class TemperatureAlert(BaseModel):
    equipment_name: str
    serial_number: str
    capacity: Decimal
    temperature: Decimal
    charge_level: Decimal
    timestamp: datetime
    alert_level: str

class IncidentStats(BaseModel):
    incident_type: str
    month: str
    incident_count: int
    resolved_count: int
    critical_count: int
    avg_resolution_hours: Optional[float] = None

class VoltageDeviation(BaseModel):
    id: int
    serial_number: str
    equipment_name: str
    voltage_nominal: Decimal
    avg_voltage: Decimal
    voltage_deviation: Decimal
    deviation_percent: Decimal
    status: str

class EquipmentIncidentSummary(BaseModel):
    id: int
    equipment_name: str
    equipment_type: str
    location: str
    battery_count: int
    total_incidents: int
    critical_incidents: int
    overheat_count: int
    low_charge_count: int
    last_incident_date: Optional[datetime] = None

class CurrentStats(BaseModel):
    equipment_name: str
    serial_number: str
    current_range: str
    avg_current: Decimal
    max_current: Decimal
    min_current: Decimal
    measurement_count: int

class EquipmentMeasurementStats(BaseModel):
    equipment_id: int
    equipment_name: str
    location: str
    battery_count: int
    total_measurements: int
    days_with_measurements: int
    avg_measurements_per_battery: Optional[float] = None
    operator_count: int
    operators: Optional[str] = None
    last_measurement: Optional[datetime] = None
