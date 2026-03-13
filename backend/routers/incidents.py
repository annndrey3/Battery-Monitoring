from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database.database import get_db
from models import models, schemas

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("/", response_model=List[schemas.IncidentResponse])
def get_incidents(
    skip: int = 0,
    limit: int = 100,
    battery_id: Optional[int] = None,
    incident_type: Optional[str] = None,
    severity: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Incident)
    
    if battery_id:
        query = query.filter(models.Incident.battery_id == battery_id)
    if incident_type:
        query = query.filter(models.Incident.incident_type == incident_type)
    if severity:
        query = query.filter(models.Incident.severity == severity)
    if is_resolved is not None:
        query = query.filter(models.Incident.is_resolved == is_resolved)
    
    incidents = query.order_by(models.Incident.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for incident in incidents:
        battery = db.query(models.Battery).filter(models.Battery.id == incident.battery_id).first()
        equipment = None
        if battery:
            equipment = db.query(models.Equipment).filter(models.Equipment.id == battery.equipment_id).first()
        
        incident_dict = {
            "id": incident.id,
            "measurement_id": incident.measurement_id,
            "battery_id": incident.battery_id,
            "incident_type": incident.incident_type,
            "description": incident.description,
            "severity": incident.severity,
            "is_resolved": incident.is_resolved,
            "resolved_at": incident.resolved_at,
            "resolved_by": incident.resolved_by,
            "created_at": incident.created_at,
            "battery_serial": battery.serial_number if battery else None,
            "equipment_name": equipment.name if equipment else None
        }
        result.append(schemas.IncidentResponse(**incident_dict))
    
    return result

@router.get("/{incident_id}", response_model=schemas.IncidentResponse)
def get_incident_by_id(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    battery = db.query(models.Battery).filter(models.Battery.id == incident.battery_id).first()
    equipment = None
    if battery:
        equipment = db.query(models.Equipment).filter(models.Equipment.id == battery.equipment_id).first()
    
    return schemas.IncidentResponse(
        id=incident.id,
        measurement_id=incident.measurement_id,
        battery_id=incident.battery_id,
        incident_type=incident.incident_type,
        description=incident.description,
        severity=incident.severity,
        is_resolved=incident.is_resolved,
        resolved_at=incident.resolved_at,
        resolved_by=incident.resolved_by,
        created_at=incident.created_at,
        battery_serial=battery.serial_number if battery else None,
        equipment_name=equipment.name if equipment else None
    )

@router.post("/", response_model=schemas.IncidentResponse)
def create_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    # Check if battery exists
    battery = db.query(models.Battery).filter(models.Battery.id == incident.battery_id).first()
    if not battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    
    db_incident = models.Incident(**incident.model_dump())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    
    equipment = db.query(models.Equipment).filter(models.Equipment.id == battery.equipment_id).first()
    
    return schemas.IncidentResponse(
        id=db_incident.id,
        measurement_id=db_incident.measurement_id,
        battery_id=db_incident.battery_id,
        incident_type=db_incident.incident_type,
        description=db_incident.description,
        severity=db_incident.severity,
        is_resolved=db_incident.is_resolved,
        resolved_at=db_incident.resolved_at,
        resolved_by=db_incident.resolved_by,
        created_at=db_incident.created_at,
        battery_serial=battery.serial_number,
        equipment_name=equipment.name if equipment else None
    )

@router.put("/{incident_id}", response_model=schemas.IncidentResponse)
def update_incident(incident_id: int, incident_update: schemas.IncidentUpdate, db: Session = Depends(get_db)):
    db_incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    update_data = incident_update.model_dump(exclude_unset=True)
    
    # If resolving incident, set resolved_at
    if "is_resolved" in update_data and update_data["is_resolved"] and not db_incident.is_resolved:
        update_data["resolved_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_incident, field, value)
    
    db.commit()
    db.refresh(db_incident)
    
    battery = db.query(models.Battery).filter(models.Battery.id == db_incident.battery_id).first()
    equipment = None
    if battery:
        equipment = db.query(models.Equipment).filter(models.Equipment.id == battery.equipment_id).first()
    
    return schemas.IncidentResponse(
        id=db_incident.id,
        measurement_id=db_incident.measurement_id,
        battery_id=db_incident.battery_id,
        incident_type=db_incident.incident_type,
        description=db_incident.description,
        severity=db_incident.severity,
        is_resolved=db_incident.is_resolved,
        resolved_at=db_incident.resolved_at,
        resolved_by=db_incident.resolved_by,
        created_at=db_incident.created_at,
        battery_serial=battery.serial_number if battery else None,
        equipment_name=equipment.name if equipment else None
    )

@router.delete("/{incident_id}")
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    db_incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    db.delete(db_incident)
    db.commit()
    return {"message": "Incident deleted successfully"}
