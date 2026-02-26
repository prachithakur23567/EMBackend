from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .routers import employee, attendance

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI()

# CORS (for frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"message": "HRMS Backend Running 🚀"}

# Include routers
app.include_router(employee.router)
app.include_router(attendance.router)