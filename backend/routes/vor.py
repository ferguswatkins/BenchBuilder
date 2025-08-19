"""
Value Over Replacement (VOR) API routes
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel
import logging

from services.vor_service import vor_service
from models.league import League, ScoringType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vor", tags=["vor"])

class VORRequest(BaseModel):
    """Request model for VOR calculations"""
    num_teams: int = 12
    include_flex: bool = True
    scoring_type: ScoringType = ScoringType.PPR
    custom_roster: Optional[dict] = None

class ComparePlayersRequest(BaseModel):
    """Request model for comparing players"""
    player_ids: List[int]
    scoring_type: ScoringType = ScoringType.PPR

@router.get("/rankings")
async def get_vor_rankings(
    num_teams: int = Query(12, description="Number of teams in league"),
    include_flex: bool = Query(True, description="Include flex positions"),
    scoring_type: ScoringType = Query(ScoringType.PPR, description="Scoring system"),
    limit: Optional[int] = Query(None, description="Limit number of results")
):
    """
    Get overall VOR rankings for all players
    """
    try:
        # Create temporary league for scoring
        league = League(
            id="temp_vor_league",
            name="VOR Calculation League",
            num_teams=num_teams,
            scoring_type=scoring_type
        )
        
        # Calculate VOR rankings
        vor_data = vor_service.calculate_vor_rankings(
            league=league,
            num_teams=num_teams,
            include_flex=include_flex
        )
        
        # Check if there was an error (no projection data)
        if "error" in vor_data:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot calculate VOR: {vor_data['error']}. Please upload projection data first using POST /api/projections/upload-sample"
            )
        
        # Apply limit if specified
        rankings = vor_data['vor_rankings']
        if limit:
            rankings = rankings[:limit]
        
        return JSONResponse(
            status_code=200,
            content={
                "vor_rankings": [
                    {
                        "overall_rank": p['overall_rank'],
                        "player": {
                            "id": p['player'].id,
                            "name": p['player'].name,
                            "position": p['player'].position.value if hasattr(p['player'].position, 'value') else str(p['player'].position),
                            "team": p['player'].team
                        },
                        "fantasy_points": p['fantasy_points'],
                        "vor": p['vor'],
                        "value_tier": p['value_tier'],
                        "position_rank": p['position_rank'],
                        "replacement_level": p['replacement_level']
                    }
                    for p in rankings
                ],
                "metadata": {
                    "total_players": vor_data['total_players'],
                    "league_size": vor_data['league_size'],
                    "replacement_levels": vor_data['replacement_levels'],
                    "roster_construction": vor_data['roster_construction']
                }
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting VOR rankings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/position/{position}")
async def get_position_vor_rankings(
    position: str,
    num_teams: int = Query(12, description="Number of teams in league"),
    scoring_type: ScoringType = Query(ScoringType.PPR, description="Scoring system"),
    limit: Optional[int] = Query(20, description="Limit number of results")
):
    """
    Get VOR rankings for a specific position
    """
    try:
        # Validate position
        valid_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DST']
        if position.upper() not in valid_positions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid position. Must be one of: {', '.join(valid_positions)}"
            )
        
        # Create temporary league
        league = League(
            id="temp_vor_league",
            name="VOR Calculation League",
            num_teams=num_teams,
            scoring_type=scoring_type
        )
        
        # Get position rankings
        position_rankings = vor_service.get_position_vor_rankings(
            position=position,
            league=league,
            limit=limit
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "position": position.upper(),
                "rankings": [
                    {
                        "position_rank": p['position_rank'],
                        "overall_rank": p['overall_rank'],
                        "player": {
                            "id": p['player'].id,
                            "name": p['player'].name,
                            "team": p['player'].team
                        },
                        "fantasy_points": p['fantasy_points'],
                        "vor": p['vor'],
                        "value_tier": p['value_tier']
                    }
                    for p in position_rankings
                ],
                "total": len(position_rankings)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting position VOR rankings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/compare-players")
async def compare_players_vor(request: ComparePlayersRequest):
    """
    Compare VOR between specific players
    """
    try:
        if len(request.player_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="Must provide at least 2 player IDs for comparison"
            )
        
        # Create temporary league
        league = League(
            id="temp_compare_league",
            name="Player Comparison League",
            scoring_type=request.scoring_type
        )
        
        # Compare players
        comparison_data = vor_service.compare_players_vor(
            player_ids=request.player_ids,
            league=league
        )
        
        if "error" in comparison_data:
            raise HTTPException(status_code=400, detail=comparison_data["error"])
        
        return JSONResponse(
            status_code=200,
            content={
                "comparison": [
                    {
                        "player": {
                            "id": p['player'].id,
                            "name": p['player'].name,
                            "position": p['player'].position.value if hasattr(p['player'].position, 'value') else str(p['player'].position),
                            "team": p['player'].team
                        },
                        "fantasy_points": p['fantasy_points'],
                        "vor": p['vor'],
                        "value_tier": p['value_tier'],
                        "overall_rank": p['overall_rank']
                    }
                    for p in comparison_data['players']
                ],
                "best_value": {
                    "player": {
                        "id": comparison_data['best_value']['player'].id,
                        "name": comparison_data['best_value']['player'].name,
                        "position": comparison_data['best_value']['player'].position.value if hasattr(comparison_data['best_value']['player'].position, 'value') else str(comparison_data['best_value']['player'].position)
                    },
                    "vor": comparison_data['best_value']['vor']
                } if comparison_data['best_value'] else None,
                "vor_differences": comparison_data['vor_differences']
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing players VOR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/draft-targets")
async def get_draft_targets(
    round_number: int = Query(..., description="Draft round number"),
    draft_position: int = Query(..., description="Position in draft order"),
    num_teams: int = Query(12, description="Number of teams in league"),
    scoring_type: ScoringType = Query(ScoringType.PPR, description="Scoring system")
):
    """
    Get best VOR targets for a specific draft position
    """
    try:
        if round_number < 1:
            raise HTTPException(status_code=400, detail="Round number must be at least 1")
        if draft_position < 1 or draft_position > num_teams:
            raise HTTPException(
                status_code=400, 
                detail=f"Draft position must be between 1 and {num_teams}"
            )
        
        # Create temporary league
        league = League(
            id="temp_draft_league",
            name="Draft Targets League",
            num_teams=num_teams,
            scoring_type=scoring_type
        )
        
        # Get draft targets
        targets_data = vor_service.get_draft_targets_by_vor(
            round_number=round_number,
            draft_position=draft_position,
            league=league,
            num_teams=num_teams
        )
        
        if "error" in targets_data:
            raise HTTPException(status_code=400, detail=targets_data["error"])
        
        # Format response
        formatted_targets = {}
        for position, players in targets_data.get('targets_by_position', {}).items():
            formatted_targets[position] = [
                {
                    "player": {
                        "id": p['player'].id,
                        "name": p['player'].name,
                        "team": p['player'].team
                    },
                    "fantasy_points": p['fantasy_points'],
                    "vor": p['vor'],
                    "overall_rank": p['overall_rank']
                }
                for p in players
            ]
        
        return JSONResponse(
            status_code=200,
            content={
                "draft_info": {
                    "round": targets_data['round'],
                    "pick": targets_data['pick'],
                    "overall_pick": targets_data['overall_pick']
                },
                "targets_by_position": formatted_targets,
                "top_overall_targets": [
                    {
                        "player": {
                            "id": p['player'].id,
                            "name": p['player'].name,
                            "position": p['player'].position.value if hasattr(p['player'].position, 'value') else str(p['player'].position),
                            "team": p['player'].team
                        },
                        "fantasy_points": p['fantasy_points'],
                        "vor": p['vor'],
                        "value_tier": p['value_tier']
                    }
                    for p in targets_data.get('top_targets', [])
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting draft targets: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/value-tiers")
async def get_value_tiers(
    scoring_type: ScoringType = Query(ScoringType.PPR, description="Scoring system"),
    num_teams: int = Query(12, description="Number of teams in league")
):
    """
    Get players grouped by value tiers
    """
    try:
        # Create temporary league
        league = League(
            id="temp_tiers_league",
            name="Value Tiers League",
            num_teams=num_teams,
            scoring_type=scoring_type
        )
        
        # Calculate VOR rankings
        vor_data = vor_service.calculate_vor_rankings(
            league=league,
            num_teams=num_teams
        )
        
        # Check if there was an error (no projection data)
        if "error" in vor_data:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot calculate VOR: {vor_data['error']}. Please upload projection data first using POST /api/projections/upload-sample"
            )
        
        # Group by value tiers
        tiers = {}
        for player_data in vor_data['vor_rankings']:
            tier = player_data['value_tier']
            if tier not in tiers:
                tiers[tier] = []
            
            tiers[tier].append({
                "player": {
                    "id": player_data['player'].id,
                    "name": player_data['player'].name,
                    "position": player_data['player'].position.value if hasattr(player_data['player'].position, 'value') else str(player_data['player'].position),
                    "team": player_data['player'].team
                },
                "fantasy_points": player_data['fantasy_points'],
                "vor": player_data['vor'],
                "overall_rank": player_data['overall_rank']
            })
        
        # Order tiers by value
        tier_order = ["Elite", "High", "Medium", "Low", "Below Replacement"]
        ordered_tiers = {}
        for tier in tier_order:
            if tier in tiers:
                ordered_tiers[tier] = tiers[tier]
        
        return JSONResponse(
            status_code=200,
            content={
                "value_tiers": ordered_tiers,
                "tier_counts": {tier: len(players) for tier, players in ordered_tiers.items()}
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting value tiers: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
