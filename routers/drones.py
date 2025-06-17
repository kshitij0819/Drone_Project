# drone_survey_api/routers/drones.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from pydantic import BaseModel
import schemas
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Drone)
def create_drone(drone: schemas.DroneCreate, db: Session = Depends(get_db)):
    db_drone = models.Drone(**drone.dict())
    db.add(db_drone)
    db.commit()
    db.refresh(db_drone)
    return db_drone

@router.get("/", response_model=list[schemas.Drone])
def get_all_drones(db: Session = Depends(get_db)):
    return db.query(models.Drone).all()

@router.get("/{drone_id}", response_model=schemas.Drone)
def get_drone(drone_id: uuid.UUID, db: Session = Depends(get_db)):
    drone = db.query(models.Drone).filter(models.Drone.id == drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    return drone

@router.patch("/{drone_id}/status")
def update_drone_status(
    drone_id: uuid.UUID, 
    status_update: schemas.DroneStatusUpdate,
    db: Session = Depends(get_db)
):
    drone = db.query(models.Drone).filter(models.Drone.id == drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    valid_statuses = ["AVAILABLE", "IN_MISSION", "MAINTENANCE"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    drone.status = status_update.status
    db.commit()
    return {"status": "Drone status updated"}

@router.delete("/{drone_id}")
def delete_drone(drone_id: uuid.UUID, db: Session = Depends(get_db)):
    drone = db.query(models.Drone).filter(models.Drone.id == drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    # Check if drone has active missions
    active_missions = db.query(models.Mission).filter(
        models.Mission.drone_id == drone_id,
        models.Mission.status.in_(["PENDING", "IN_PROGRESS"])
    ).count()
    
    if active_missions > 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete drone with active missions"
        )
    
    db.delete(drone)
    db.commit()
    return {"status": "Drone deleted"}

# Add to schemas.py
class DroneStatusUpdate(BaseModel):
    status: str