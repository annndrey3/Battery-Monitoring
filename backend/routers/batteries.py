from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from models import models, schemas

router = APIRouter(prefix="/batteries", tags=["batteries"])

@router.get("/", response_model=List[schemas.BatteryResponse])
def get_batteries(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Battery)
    
    if equipment_id:
        query = query.filter(models.Battery.equipment_id == equipment_id)
    if status:
        query = query.filter(models.Battery.status == status)
    
    batteries = query.offset(skip).limit(limit).all()
    
    result = []
    for battery in batteries:
        equipment = db.query(models.Equipment).filter(models.Equipment.id == battery.equipment_id).first()
        battery_dict = {
            "id": battery.id,
            "equipment_id": battery.equipment_id,
            "serial_number": battery.serial_number,
            "capacity": battery.capacity,
            "voltage_nominal": battery.voltage_nominal,
            "install_date": battery.install_date,
            "status": battery.status,
            "created_at": battery.created_at,
            "updated_at": battery.updated_at,
            "equipment_name": equipment.name if equipment else None
        }
        result.append(schemas.BatteryResponse(**battery_dict))
    
    return result

@router.get("/{battery_id}", response_model=schemas.BatteryResponse)
def get_battery_by_id(battery_id: int, db: Session = Depends(get_db)):
    battery = db.query(models.Battery).filter(models.Battery.id == battery_id).first()
    if not battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    
    equipment = db.query(models.Equipment).filter(models.Equipment.id == battery.equipment_id).first()
    
    return schemas.BatteryResponse(
        id=battery.id,
        equipment_id=battery.equipment_id,
        serial_number=battery.serial_number,
        capacity=battery.capacity,
        voltage_nominal=battery.voltage_nominal,
        install_date=battery.install_date,
        status=battery.status,
        created_at=battery.created_at,
        updated_at=battery.updated_at,
        equipment_name=equipment.name if equipment else None
    )

@router.post("/", response_model=schemas.BatteryResponse)
def create_battery(battery: schemas.BatteryCreate, db: Session = Depends(get_db)):
    # Check if equipment exists
    equipment = db.query(models.Equipment).filter(models.Equipment.id == battery.equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    db_battery = models.Battery(**battery.model_dump())
    db.add(db_battery)
    db.commit()
    db.refresh(db_battery)
    
    return schemas.BatteryResponse(
        id=db_battery.id,
        equipment_id=db_battery.equipment_id,
        serial_number=db_battery.serial_number,
        capacity=db_battery.capacity,
        voltage_nominal=db_battery.voltage_nominal,
        install_date=db_battery.install_date,
        status=db_battery.status,
        created_at=db_battery.created_at,
        updated_at=db_battery.updated_at,
        equipment_name=equipment.name
    )

@router.put("/{battery_id}", response_model=schemas.BatteryResponse)
def update_battery(battery_id: int, battery: schemas.BatteryUpdate, db: Session = Depends(get_db)):
    db_battery = db.query(models.Battery).filter(models.Battery.id == battery_id).first()
    if not db_battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    
    update_data = battery.model_dump(exclude_unset=True)
    
    # Check if equipment exists if updating equipment_id
    if "equipment_id" in update_data:
        equipment = db.query(models.Equipment).filter(
            models.Equipment.id == update_data["equipment_id"]
        ).first()
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
    
    for field, value in update_data.items():
        setattr(db_battery, field, value)
    
    db.commit()
    db.refresh(db_battery)
    
    equipment = db.query(models.Equipment).filter(
        models.Equipment.id == db_battery.equipment_id
    ).first()
    
    return schemas.BatteryResponse(
        id=db_battery.id,
        equipment_id=db_battery.equipment_id,
        serial_number=db_battery.serial_number,
        capacity=db_battery.capacity,
        voltage_nominal=db_battery.voltage_nominal,
        install_date=db_battery.install_date,
        status=db_battery.status,
        created_at=db_battery.created_at,
        updated_at=db_battery.updated_at,
        equipment_name=equipment.name if equipment else None
    )

@router.delete("/{battery_id}")
def delete_battery(battery_id: int, db: Session = Depends(get_db)):
    db_battery = db.query(models.Battery).filter(models.Battery.id == battery_id).first()
    if not db_battery:
        raise HTTPException(status_code=404, detail="Battery not found")
    
    db.delete(db_battery)
    db.commit()
    return {"message": "Battery deleted successfully"}
