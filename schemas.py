# drone_survey_api/schemas.py
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

class Coordinate(BaseModel):
    lng: float
    lat: float
    alt: Optional[float] = None

class GeoJsonLineString(BaseModel):
    type: str = "LineString"
    coordinates: List[List[float]]

class SiteBase(BaseModel):
    name: str
    location: dict  # GeoJSON Point or Polygon
    area: float  # Area in square meters

class SiteCreate(SiteBase):
    pass

class Site(SiteBase):
    id: uuid.UUID
    
    class Config:
        orm_mode = True

class MissionBase(BaseModel):
    drone_id: uuid.UUID
    site_id: uuid.UUID
    planned_path: GeoJsonLineString

class MissionCreate(MissionBase):
    pass

class Mission(MissionBase):
    id: uuid.UUID
    status: str
    progress: Optional[float] = None
    distance: Optional[float] = None
    actual_path: Optional[dict] = None
    
    class Config:
        orm_mode = True

class TelemetryData(BaseModel):
    lat: float
    lng: float
    alt: Optional[float] = None
    battery: Optional[float] = None
    timestamp: Optional[datetime] = None
    speed: Optional[float] = None
    heading: Optional[float] = None

class DroneBase(BaseModel):
    model: str
    status: str

class DroneCreate(DroneBase):
    pass

class Drone(DroneBase):
    id: uuid.UUID
    
    class Config:
        orm_mode = True



class DroneStatusUpdate(BaseModel):
    status: str
    
    class Config:
        orm_mode = True