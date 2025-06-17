# Drone Survey Management System

A backend system for managing drone survey operations, including drone management, site management, and mission planning.

## Features

### 1. Drone Management
- Create and manage drone fleet
- Monitor drone status (AVAILABLE, IN_MISSION, MAINTENANCE)
- Track battery levels and last heartbeat

### 2. Site Management
- Create survey sites with geospatial locations
- Support for both point locations and polygon areas
- Automatic area calculation for polygon sites
- GeoJSON support for location data

### 3. Mission Management
- Plan and execute drone survey missions
- Associate missions with specific sites and drones
- Track mission progress with percentage completion
- Mission status tracking (PENDING, IN_PROGRESS, COMPLETED, ABORTED)
- Store planned and actual flight paths using GeoJSON LineStrings
- Validate planned paths with minimum 2 points requirement

## API Endpoints

### Drone Endpoints
```
POST /api/v1/drones/ - Create new drone
GET /api/v1/drones/ - List all drones
GET /api/v1/drones/{drone_id} - Get specific drone
```

### Site Endpoints
```
POST /api/v1/sites/ - Create new survey site
GET /api/v1/sites/ - List all sites
GET /api/v1/sites/{site_id} - Get specific site
```

### Mission Endpoints
```
POST /api/v1/missions/ - Create new mission
GET /api/v1/missions/ - List all missions
GET /api/v1/missions/{mission_id} - Get specific mission
```

## Data Models

### Drone
- id: UUID
- model: string
- status: string (AVAILABLE, IN_MISSION, MAINTENANCE)
- battery_level: float
- last_heartbeat: timestamp

### Site
- id: UUID
- name: string
- location: GeoJSON (Point or Polygon)
- area: float (square meters)

### Mission
- id: UUID
- drone_id: UUID (foreign key)
- site_id: UUID (foreign key)
- status: string (PENDING, IN_PROGRESS, COMPLETED, ABORTED)
- progress: float (0.0 - 100.0)
- planned_path: GeoJSON LineString
- actual_path: GeoJSON LineString (optional)

GET /api/v1/sites/{site_id} - Get specific site
```

### Mission Endpoints
```
POST /api/v1/missions/ - Create new mission
GET /api/v1/missions/ - List all missions
GET /api/v1/missions/{mission_id} - Get specific mission
```

## Data Models

### Drone
- id: UUID
- model: string
- status: string (AVAILABLE, IN_MISSION, MAINTENANCE)

### Site
- id: UUID
- name: string
- location: GeoJSON (Point or Polygon)
- area: float (square meters)

### Mission
- id: UUID
- drone_id: UUID (foreign key)
- site_id: UUID (foreign key)
- status: string (PENDING, IN_PROGRESS, COMPLETED, ABORTED)

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - POSTGRES_SERVER
   - POSTGRES_USER
   - POSTGRES_PASSWORD
   - POSTGRES_DB

4. Run the application:
   ```
   uvicorn main:app --reload
   ```

## Technology Stack
- FastAPI - Web framework
- SQLAlchemy - ORM
- PostgreSQL - Database
- Pydantic - Data validation
- GeoJSON - Spatial data format
- JWT - Authentication

## Development

The project follows a modular architecture with clear separation of concerns:
- `models/` - Database models
- `routers/` - API endpoints
- `schemas/` - Data validation
- `core/` - Core utilities and services
- `config/` - Configuration management

## License

MIT License
