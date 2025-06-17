# drone_survey_api/routers/missions.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from geopy.distance import geodesic

router = APIRouter()

def calculate_path_distance(coordinates: list) -> float:
    """Calculate total distance of a path in meters"""
    if len(coordinates) < 2:
        return 0.0
    
    total = 0.0
    points = [(coord[1], coord[0]) for coord in coordinates]  # Convert to (lat, lng)
    
    for i in range(1, len(points)):
        total += geodesic(points[i-1], points[i]).meters
    
    return total

@router.post("/", response_model=schemas.Mission)
def create_mission(mission: schemas.MissionCreate, db: Session = Depends(get_db)):
    # Check if drone exists
    drone = db.query(models.Drone).filter(models.Drone.id == mission.drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    # Check if site exists
    site = db.query(models.Site).filter(models.Site.id == mission.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Create mission
    db_mission = models.Mission(
        drone_id=mission.drone_id,
        site_id=mission.site_id,
        status="PENDING",
        planned_path=mission.planned_path.dict()
    )
    
    db.add(db_mission)
    
    # Update drone status
    drone.status = "IN_MISSION"
    db.add(drone)
    
    db.commit()
    db.refresh(db_mission)
    return db_mission

@router.get("/", response_model=list[schemas.Mission])
def get_all_missions(db: Session = Depends(get_db)):
    return db.query(models.Mission).all()

@router.get("/{mission_id}", response_model=schemas.Mission)
def get_mission(mission_id: uuid.UUID, db: Session = Depends(get_db)):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@router.post("/{mission_id}/start", response_model=schemas.Mission)
def start_mission(mission_id: uuid.UUID, db: Session = Depends(get_db)):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if mission.status != "PENDING":
        raise HTTPException(status_code=400, detail="Mission can only be started from PENDING state")
    
    mission.status = "IN_PROGRESS"
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission

@router.post("/{mission_id}/complete", response_model=schemas.Mission)
def complete_mission(mission_id: uuid.UUID, db: Session = Depends(get_db)):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if mission.status != "IN_PROGRESS":
        raise HTTPException(status_code=400, detail="Mission must be IN_PROGRESS to complete")
    
    # Update mission status
    mission.status = "COMPLETED"
    
    # Update drone status
    drone = db.query(models.Drone).filter(models.Drone.id == mission.drone_id).first()
    if drone:
        drone.status = "AVAILABLE"
        db.add(drone)
    
    # Calculate mission statistics
    if mission.actual_path and mission.actual_path.get("coordinates"):
        mission.distance = calculate_path_distance(mission.actual_path["coordinates"])
    
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission

@router.post("/{mission_id}/abort", response_model=schemas.Mission)
def abort_mission(mission_id: uuid.UUID, db: Session = Depends(get_db)):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if mission.status not in ["PENDING", "IN_PROGRESS"]:
        raise HTTPException(status_code=400, detail="Mission cannot be aborted in current state")
    
    mission.status = "ABORTED"
    
    # Update drone status
    drone = db.query(models.Drone).filter(models.Drone.id == mission.drone_id).first()
    if drone:
        drone.status = "AVAILABLE"
        db.add(drone)
    
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission

@router.websocket("/{mission_id}/telemetry")
async def mission_telemetry(websocket: WebSocket, mission_id: str, db: Session = Depends(get_db)):
    await websocket.accept()
    
    # Get mission
    mission = db.query(models.Mission).filter(models.Mission.id == uuid.UUID(mission_id)).first()
    if not mission:
        await websocket.close(code=1008, reason="Mission not found")
        return
    
    if mission.status != "IN_PROGRESS":
        await websocket.close(code=1008, reason="Mission not in progress")
        return
    
    try:
        while True:
            # Receive telemetry data
            data = await websocket.receive_json()
            position = schemas.Coordinate(**data)
            
            # Update actual path
            if not mission.actual_path:
                mission.actual_path = {
                    "type": "LineString",
                    "coordinates": []
                }
            
            mission.actual_path["coordinates"].append([
                position.lng, 
                position.lat, 
                position.alt or 0.0
            ])
            
            # Calculate progress
            if mission.planned_path and mission.planned_path.get("coordinates"):
                total_points = len(mission.planned_path["coordinates"])
                current_points = len(mission.actual_path["coordinates"])
                mission.progress = min(100.0, (current_points / total_points) * 100)
            
            db.commit()
            
            # Send acknowledgment
            await websocket.send_json({
                "status": "ACK",
                "progress": mission.progress
            })
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()