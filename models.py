# models.py
import uuid
from sqlalchemy import Column, String, Float, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql.sqltypes import TIMESTAMP
from database import Base
class Drone(Base):
    __tablename__ = 'drones'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default='AVAILABLE')
    battery_level = Column(Float)
    last_heartbeat = Column(TIMESTAMP)
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('AVAILABLE', 'IN_MISSION', 'MAINTENANCE')", 
            name='valid_drone_status'
        ),
    )



class Site(Base):
    __tablename__ = 'sites'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    location = Column(JSONB)  # Store location as GeoJSON Point
    area = Column(Float, nullable=False)  # Area in square meters
    
    __table_args__ = (
        CheckConstraint(
            "location->>'type' = 'Point' OR location->>'type' = 'Polygon'", 
            name='valid_location_type'
        ),
    )


class Mission(Base):
    __tablename__ = 'missions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drone_id = Column(UUID(as_uuid=True), ForeignKey('drones.id'))
    site_id = Column(UUID(as_uuid=True), ForeignKey('sites.id'))
    status = Column(String(20), nullable=False, default='PENDING')
    progress = Column(Float, default=0.0)
    planned_path = Column(JSONB)
    actual_path = Column(JSONB)
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'ABORTED')", 
            name='valid_mission_status'
        ),
        CheckConstraint(
            "planned_path->>'type' = 'LineString'", 
            name='valid_planned_path_type'
        ),
        CheckConstraint(
            "actual_path->>'type' = 'LineString' OR actual_path IS NULL", 
            name='valid_actual_path_type'
        )
    )
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'ABORTED')", 
            name='valid_mission_status'
        ),
        CheckConstraint(
            "planned_path->>'type' = 'LineString'", 
            name='valid_planned_path_type'
        ),
        CheckConstraint(
            "jsonb_array_length(planned_path->'coordinates') > 1", 
            name='min_planned_points'
        ),
    )