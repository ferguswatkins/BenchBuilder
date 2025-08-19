"""
Projection API routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging

from services.projection_service import projection_service
from utils.csv_parser import create_sample_csv

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projections", tags=["projections"])

@router.post("/upload")
async def upload_projections(
    file: UploadFile = File(...),
    source_name: str = Query("uploaded", description="Name of the projection source"),
    source_type: str = Query("auto", description="CSV format type (auto, fantasypros, yahoo, espn)")
):
    """
    Upload projection data from CSV file
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.CSV')):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file content
        content = await file.read()
        
        # Process projections
        results = projection_service.upload_projections(
            file_content=content,
            source_name=source_name,
            source_type=source_type
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Successfully uploaded {results['players_processed']} player projections",
                "results": results
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading projections: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/upload-sample")
async def upload_sample_projections():
    """
    Upload sample projection data for testing
    """
    try:
        sample_csv = create_sample_csv()
        results = projection_service.upload_projections(
            file_content=sample_csv,
            source_name="sample_data",
            source_type="fantasypros"
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Successfully uploaded sample projection data",
                "results": results
            }
        )
        
    except Exception as e:
        logger.error(f"Error uploading sample projections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_projections(
    position: Optional[str] = Query(None, description="Filter by position (QB, RB, WR, TE, K, DST)"),
    team: Optional[str] = Query(None, description="Filter by team abbreviation"),
    limit: Optional[int] = Query(None, description="Limit number of results")
):
    """
    Get player projections with optional filtering
    """
    try:
        projections = projection_service.get_projections(
            position=position,
            team=team,
            limit=limit
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "projections": projections,
                "total": len(projections)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting projections: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/player/{player_id}")
async def get_player_projection(player_id: int):
    """
    Get projection for specific player
    """
    try:
        projection = projection_service.get_player_projection(player_id)
        
        if not projection:
            raise HTTPException(status_code=404, detail="Player not found")
        
        return JSONResponse(
            status_code=200,
            content=projection
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting player projection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search")
async def search_players(
    q: str = Query(..., description="Search query (player name)"),
    limit: int = Query(20, description="Maximum number of results")
):
    """
    Search players by name
    """
    try:
        results = projection_service.search_players(q, limit)
        
        return JSONResponse(
            status_code=200,
            content={
                "players": results,
                "total": len(results),
                "query": q
            }
        )
        
    except Exception as e:
        logger.error(f"Error searching players: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sources")
async def get_projection_sources():
    """
    Get all projection sources
    """
    try:
        sources = projection_service.get_sources()
        
        return JSONResponse(
            status_code=200,
            content={
                "sources": sources,
                "total": len(sources)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats")
async def get_projection_statistics():
    """
    Get projection statistics and summary
    """
    try:
        stats = projection_service.get_statistics()
        
        return JSONResponse(
            status_code=200,
            content=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/clear")
async def clear_projections(
    source: Optional[str] = Query(None, description="Clear projections for specific source")
):
    """
    Clear all projections or projections from specific source
    """
    try:
        projection_service.clear_projections(source)
        
        message = f"Cleared projections{' for source: ' + source if source else ''}"
        
        return JSONResponse(
            status_code=200,
            content={"message": message}
        )
        
    except Exception as e:
        logger.error(f"Error clearing projections: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sample-csv")
async def get_sample_csv():
    """
    Get sample CSV format for reference
    """
    try:
        sample_csv = create_sample_csv()
        
        return JSONResponse(
            status_code=200,
            content={
                "sample_csv": sample_csv,
                "description": "Sample CSV format with FantasyPros-style columns",
                "columns": [
                    "Player", "Pos", "Team", "Pass Yds", "Pass TD", "Int", 
                    "Rush Yds", "Rush TD", "Rec", "Rec Yds", "Rec TD", "FPTS"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting sample CSV: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
