from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import drones, missions, sites
from database import engine, Base, get_db
from sqlalchemy.orm import Session

app = FastAPI(
    title="Drone Survey Management API",
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers with proper versioning
app.include_router(
    drones.router,
    prefix="/api/v1/drones",
    tags=["drones"]
)

app.include_router(
    missions.router,
    prefix="/api/v1/missions",
    tags=["missions"]
)

app.include_router(
    sites.router,
    prefix="/api/v1/sites",
    tags=["sites"]
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Drone Survey Management API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy"}
    except:
        raise HTTPException(status_code=500, detail="Database connection failed")