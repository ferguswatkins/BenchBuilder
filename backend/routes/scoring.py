"""
Scoring calculation API routes
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging

from services.scoring_service import scoring_service
from services.projection_service import projection_service
from models.league import League, ScoringType
from models.player import PlayerProjection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scoring", tags=["scoring"])

class CalculatePointsRequest(BaseModel):
    """Request model for calculating points"""
    player_id: int
    league_id: Optional[str] = None
    scoring_rules: Optional[Dict[str, float]] = None

class CustomLeagueRequest(BaseModel):
    """Request model for creating custom league"""
    name: str
    scoring_type: ScoringType = ScoringType.PPR
    custom_rules: Optional[Dict[str, float]] = None

@router.post("/calculate-points")
async def calculate_points(request: CalculatePointsRequest):
    """
    Calculate fantasy points for a specific player
    """
    try:
        # Get player projection
        player_data = projection_service.get_player_projection(request.player_id)
        if not player_data:
            raise HTTPException(status_code=404, detail="Player not found")
        
        projection = PlayerProjection(**player_data['projection'])
        
        # Calculate points
        league = None
        if request.league_id:
            # In a real implementation, you'd fetch the league from a database
            # For now, we'll use default PPR league
            league = League(
                id=request.league_id,
                name="Default League",
                scoring_type=ScoringType.PPR
            )
        
        fantasy_points = scoring_service.calculate_fantasy_points(
            projection=projection,
            league=league,
            scoring_rules=request.scoring_rules
        )
        
        # Get detailed breakdown
        breakdown = scoring_service.get_scoring_breakdown(
            projection=projection,
            league=league,
            scoring_rules=request.scoring_rules
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "player_id": request.player_id,
                "player_name": player_data['player']['name'],
                "projected_points": fantasy_points,
                "breakdown": breakdown
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating points: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/calculate-all")
async def calculate_all_points(
    scoring_type: ScoringType = Query(ScoringType.PPR, description="Scoring system to use"),
    position: Optional[str] = Query(None, description="Filter by position")
):
    """
    Calculate fantasy points for all players with projections
    """
    try:
        # Get all projections
        projections_data = projection_service.get_projections(position=position)
        
        if not projections_data:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "No projections found",
                    "players": [],
                    "total": 0
                }
            )
        
        # Create league with specified scoring type
        league = League(
            id="temp_league",
            name="Calculation League",
            scoring_type=scoring_type
        )
        
        # Calculate points for each player
        results = []
        for player_data in projections_data:
            projection = PlayerProjection(**player_data['projection'])
            fantasy_points = scoring_service.calculate_fantasy_points(projection, league)
            
            # Update the result with calculated points
            result = player_data.copy()
            result['projection']['fantasy_points'] = fantasy_points
            result['calculated_points'] = fantasy_points
            results.append(result)
        
        # Sort by fantasy points
        results.sort(key=lambda x: x['calculated_points'], reverse=True)
        
        return JSONResponse(
            status_code=200,
            content={
                "players": results,
                "total": len(results),
                "scoring_type": scoring_type.value
            }
        )
        
    except Exception as e:
        logger.error(f"Error calculating all points: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/compare-systems/{player_id}")
async def compare_scoring_systems(player_id: int):
    """
    Compare how a player scores in different scoring systems
    """
    try:
        # Get player projection
        player_data = projection_service.get_player_projection(player_id)
        if not player_data:
            raise HTTPException(status_code=404, detail="Player not found")
        
        projection = PlayerProjection(**player_data['projection'])
        
        # Compare across scoring systems
        comparison = scoring_service.compare_scoring_systems(projection)
        
        return JSONResponse(
            status_code=200,
            content={
                "player_id": player_id,
                "player_name": player_data['player']['name'],
                "scoring_comparison": comparison,
                "difference": {
                    "ppr_vs_standard": comparison.get("ppr", 0) - comparison.get("standard", 0),
                    "half_ppr_vs_standard": comparison.get("half_ppr", 0) - comparison.get("standard", 0)
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing scoring systems: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/breakdown/{player_id}")
async def get_scoring_breakdown(
    player_id: int,
    scoring_type: ScoringType = Query(ScoringType.PPR, description="Scoring system to use")
):
    """
    Get detailed scoring breakdown for a player
    """
    try:
        # Get player projection
        player_data = projection_service.get_player_projection(player_id)
        if not player_data:
            raise HTTPException(status_code=404, detail="Player not found")
        
        projection = PlayerProjection(**player_data['projection'])
        
        # Create league with specified scoring type
        league = League(
            id="temp_league",
            name="Breakdown League",
            scoring_type=scoring_type
        )
        
        # Get breakdown
        breakdown = scoring_service.get_scoring_breakdown(projection, league)
        
        return JSONResponse(
            status_code=200,
            content={
                "player_id": player_id,
                "player_name": player_data['player']['name'],
                "position": player_data['player']['position'],
                "scoring_type": scoring_type.value,
                "breakdown": breakdown
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scoring breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/create-custom-league")
async def create_custom_league(request: CustomLeagueRequest):
    """
    Create a custom league with specific scoring rules
    """
    try:
        league = scoring_service.create_custom_league(
            league_name=request.name,
            scoring_type=request.scoring_type,
            custom_rules=request.custom_rules
        )
        
        # Validate scoring rules
        warnings = scoring_service.validate_scoring_rules(league.scoring_rules)
        
        return JSONResponse(
            status_code=200,
            content={
                "league": league.dict(),
                "validation_warnings": warnings
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating custom league: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/default-rules")
async def get_default_scoring_rules():
    """
    Get default scoring rules for all scoring types
    """
    try:
        return JSONResponse(
            status_code=200,
            content={
                "scoring_rules": scoring_service.DEFAULT_SCORING_RULES
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting default rules: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/validate-rules")
async def validate_scoring_rules(rules: Dict[str, float]):
    """
    Validate custom scoring rules
    """
    try:
        warnings = scoring_service.validate_scoring_rules(rules)
        
        return JSONResponse(
            status_code=200,
            content={
                "valid": len(warnings) == 0,
                "warnings": warnings,
                "rules": rules
            }
        )
        
    except Exception as e:
        logger.error(f"Error validating rules: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
