# drone_survey_api/routers/sites.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from geopy.distance import geodesic

router = APIRouter()

def calculate_area(coordinates: list) -> float:
    """Calculate area of a polygon using the Shoelace formula"""
    n = len(coordinates)
    area = 0.0
    for i in range(n):
        x1, y1 = coordinates[i]
        x2, y2 = coordinates[(i + 1) % n]
        area += x1 * y2 - y1 * x2
    return abs(area) / 2.0

@router.post("/", response_model=schemas.Site)
def create_site(site: schemas.SiteCreate, db: Session = Depends(get_db)):
    # Validate location format
    location_type = site.location.get("type")
    if location_type not in ["Point", "Polygon"]:
        raise HTTPException(status_code=400, detail="Location must be a Point or Polygon")
    
    # Calculate area if location is a Polygon
    area = site.area
    if location_type == "Polygon":
        coordinates = site.location["coordinates"]
        area = calculate_area(coordinates[0])  # First ring of coordinates
    
    db_site = models.Site(
        name=site.name,
        location=site.location,
        area=area
    )
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site

@router.get("/", response_model=list[schemas.Site])
def get_all_sites(db: Session = Depends(get_db)):
    return db.query(models.Site).all()

@router.get("/{site_id}", response_model=schemas.Site)
def get_site(site_id: uuid.UUID, db: Session = Depends(get_db)):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.delete("/{site_id}")
def delete_site(site_id: uuid.UUID, db: Session = Depends(get_db)):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Check if site has active missions
    active_missions = db.query(models.Mission).filter(
        models.Mission.site_id == site_id,
        models.Mission.status.in_("PENDING", "IN_PROGRESS")
    ).count()
    
    if active_missions > 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete site with active missions"
        )
    
    db.delete(site)
    db.commit()
    return {"status": "Site deleted"}
