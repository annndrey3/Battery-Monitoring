from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from datetime import datetime, timedelta
from database.database import get_db
from models import models, schemas

router = APIRouter(prefix="/measurements", tags=["measurements"])

@router.get("/", response_model=List[schemas.MeasurementResponse])
def get_measurements(
    skip: int = 0,
    limit: int = 100,
    battery_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Measurement)
    
    if battery_id:
        query = query.filter(models.Measurement.battery_id == battery_id)
    if start_date:
        query = query.filter(models.Measurement.timestamp >= start_date)
    if end_date:
        query = query.filter(models.Measurement.timestamp <= end_date)
    
    measurements = query.order_by(models.Measurement.timestamp.desc()).offset(skip).limit(limit).all()
    
    result = []
    for measurement in measurements:
        battery = db.query(models.Battery).filter(models.Battery.id == measurement.battery_id).first()
        user = db.query(models.User).filter(models.User.id == measurement.measured_by).first()
        
        measurement_dict = {
            "id": measurement.id,
            "battery_id": measurement.battery_id,
            "voltage": measurement.voltage,
            "current": measurement.current,
            "charge_level": measurement.charge_level,
            "temperature": measurement.temperature,
            "timestamp": measurement.timestamp.isoformat(),
            "measured_by": measurement.measured_by,
            "operator_name": user.full_name if user else None,
            "battery_serial": battery.serial_number if battery else None
        }
        result.append(schemas.MeasurementResponse(**measurement_dict))
    
    return result

@router.get("/{measurement_id}", response_model=schemas.MeasurementResponse)
def get_measurement_by_id(measurement_id: int, db: Session = Depends(get_db)):
    measurement = db.query(models.Measurement).filter(models.Measurement.id == measurement_id).first()
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    
    battery = db.query(models.Battery).filter(models.Battery.id == measurement.battery_id).first()
    user = db.query(models.User).filter(models.User.id == measurement.measured_by).first()
    
    return schemas.MeasurementResponse(
        id=measurement.id,
        battery_id=measurement.battery_id,
        voltage=measurement.voltage,
        current=measurement.current,
        charge_level=measurement.charge_level,
        temperature=measurement.temperature,
        timestamp=measurement.timestamp,
        measured_by=measurement.measured_by,
        operator_name=user.full_name if user else None,
        battery_serial=battery.serial_number if battery else None
    )

@router.post("/", response_model=schemas.MeasurementResponse)
def create_measurement(measurement: schemas.MeasurementCreate, db: Session = Depends(get_db)):
    # Check if battery exists
    battery = db.query(models.Battery).filter(models.Battery.id == measurement.battery_id).first()
    if not battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    
    db_measurement = models.Measurement(**measurement.model_dump())
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    
    # Auto-create incidents for critical values
    if measurement.temperature > 60:
        incident = models.Incident(
            battery_id=measurement.battery_id,
            measurement_id=db_measurement.id,
            incident_type="overheat",
            description=f"Critical temperature detected: {measurement.temperature}°C",
            severity="critical" if measurement.temperature > 70 else "high",
            is_resolved=False
        )
        db.add(incident)
        db.commit()
    
    if measurement.charge_level < 20:
        incident = models.Incident(
            battery_id=measurement.battery_id,
            measurement_id=db_measurement.id,
            incident_type="low_charge",
            description=f"Low charge level detected: {measurement.charge_level}%",
            severity="critical" if measurement.charge_level < 10 else "high",
            is_resolved=False
        )
        db.add(incident)
        db.commit()
    
    user = db.query(models.User).filter(models.User.id == db_measurement.measured_by).first()
    
    return schemas.MeasurementResponse(
        id=db_measurement.id,
        battery_id=db_measurement.battery_id,
        voltage=db_measurement.voltage,
        current=db_measurement.current,
        charge_level=db_measurement.charge_level,
        temperature=db_measurement.temperature,
        timestamp=db_measurement.timestamp,
        measured_by=db_measurement.measured_by,
        operator_name=user.full_name if user else None,
        battery_serial=battery.serial_number
    )

@router.get("/history/{battery_id}", response_model=List[schemas.MeasurementHistory])
def get_battery_history(
    battery_id: int,
    days: int = 7,
    db: Session = Depends(get_db)
):
    # Check if battery exists
    battery = db.query(models.Battery).filter(models.Battery.id == battery_id).first()
    if not battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = text("""
        SELECT 
            strftime('%Y-%m-%d %H:00:00', m.timestamp) AS hour,
            b.serial_number,
            ROUND(AVG(m.voltage), 3) AS avg_voltage,
            ROUND(AVG(m.current), 3) AS avg_current,
            ROUND(AVG(m.charge_level), 2) AS avg_charge,
            ROUND(AVG(m.temperature), 2) AS avg_temp,
            COUNT(*) AS measurement_count
        FROM measurements m
        JOIN batteries b ON m.battery_id = b.id
        WHERE b.id = :battery_id
        AND m.timestamp >= :start_date
        GROUP BY strftime('%Y-%m-%d %H:00:00', m.timestamp), b.serial_number
        ORDER BY hour DESC
    """)
    
    result = db.execute(query, {"battery_id": battery_id, "start_date": start_date})
    
    history = []
    for row in result:
        history.append(schemas.MeasurementHistory(
            hour=row.hour,
            serial_number=row.serial_number,
            avg_voltage=row.avg_voltage,
            avg_current=row.avg_current,
            avg_charge=row.avg_charge,
            avg_temp=row.avg_temp,
            measurement_count=row.measurement_count
        ))
    
    return history

@router.delete("/{measurement_id}")
def delete_measurement(measurement_id: int, db: Session = Depends(get_db)):
    db_measurement = db.query(models.Measurement).filter(models.Measurement.id == measurement_id).first()
    if not db_measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    
    db.delete(db_measurement)
    db.commit()
    return {"message": "Measurement deleted successfully"}
