from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from database.database import get_db
from models import models, schemas

router = APIRouter(prefix="/equipment", tags=["equipment"])

@router.get("/", response_model=List[schemas.EquipmentResponse])
def get_equipment(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        models.Equipment,
        func.count(models.Battery.id).label('battery_count')
    ).outerjoin(models.Battery, models.Equipment.id == models.Battery.equipment_id)
    
    if status:
        query = query.filter(models.Equipment.status == status)
    
    results = query.group_by(models.Equipment.id).offset(skip).limit(limit).all()
    
    equipment_list = []
    for equipment, battery_count in results:
        eq_dict = {
            "id": equipment.id,
            "name": equipment.name,
            "type": equipment.type,
            "location": equipment.location,
            "description": equipment.description,
            "status": equipment.status,
            "created_at": equipment.created_at,
            "updated_at": equipment.updated_at,
            "battery_count": battery_count
        }
        equipment_list.append(schemas.EquipmentResponse(**eq_dict))
    
    return equipment_list

@router.get("/{equipment_id}", response_model=schemas.EquipmentResponse)
def get_equipment_by_id(equipment_id: int, db: Session = Depends(get_db)):
    result = db.query(
        models.Equipment,
        func.count(models.Battery.id).label('battery_count')
    ).outerjoin(models.Battery, models.Equipment.id == models.Battery.equipment_id).filter(
        models.Equipment.id == equipment_id
    ).group_by(models.Equipment.id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    equipment, battery_count = result
    return schemas.EquipmentResponse(
        id=equipment.id,
        name=equipment.name,
        type=equipment.type,
        location=equipment.location,
        description=equipment.description,
        status=equipment.status,
        created_at=equipment.created_at,
        updated_at=equipment.updated_at,
        battery_count=battery_count
    )

@router.post("/", response_model=schemas.EquipmentResponse)
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    db_equipment = models.Equipment(**equipment.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return schemas.EquipmentResponse(**{**db_equipment.__dict__, "battery_count": 0})

@router.put("/{equipment_id}", response_model=schemas.EquipmentResponse)
def update_equipment(equipment_id: int, equipment: schemas.EquipmentUpdate, db: Session = Depends(get_db)):
    db_equipment = db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    update_data = equipment.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_equipment, field, value)
    
    db.commit()
    db.refresh(db_equipment)
    
    battery_count = db.query(func.count(models.Battery.id)).filter(
        models.Battery.equipment_id == equipment_id
    ).scalar()
    
    return schemas.EquipmentResponse(**{**db_equipment.__dict__, "battery_count": battery_count})

@router.delete("/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    db_equipment = db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    db.delete(db_equipment)
    db.commit()
    return {"message": "Equipment deleted successfully"}
