"""
Fantasy Draft Co-Pilot - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import routers
from routes.auth import router as auth_router
from routes.leagues import router as leagues_router
from routes.projections import router as projections_router
from routes.scoring import router as scoring_router
from routes.vor import router as vor_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Fantasy Draft Co-Pilot API",
    description="AI-powered fantasy football draft assistant",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(leagues_router)
app.include_router(projections_router)
app.include_router(scoring_router)
app.include_router(vor_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Fantasy Draft Co-Pilot API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
