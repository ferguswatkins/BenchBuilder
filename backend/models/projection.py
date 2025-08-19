"""
Projection and analysis models
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ProjectionSource(BaseModel):
    """Projection data source"""
    name: str
    url: Optional[str] = None
    last_updated: datetime
    reliability_score: Optional[float] = None

class WeeklyProjection(BaseModel):
    """Weekly player projection"""
    player_id: int
    week: int
    season: int
    
    # Projected stats (same as PlayerProjection but for specific week)
    passing_yards: Optional[float] = None
    passing_tds: Optional[float] = None
    interceptions: Optional[float] = None
    rushing_yards: Optional[float] = None
    rushing_tds: Optional[float] = None
    receptions: Optional[float] = None
    receiving_yards: Optional[float] = None
    receiving_tds: Optional[float] = None
    
    # Calculated points
    fantasy_points: Optional[float] = None
    
    # Confidence and variance
    confidence: Optional[float] = None
    floor: Optional[float] = None
    ceiling: Optional[float] = None

class SeasonProjection(BaseModel):
    """Season-long player projection"""
    player_id: int
    season: int
    source: str
    
    # Season totals
    games_projected: int = 17
    fantasy_points: float
    
    # Position rank
    position_rank: Optional[int] = None
    overall_rank: Optional[int] = None
    
    # Value metrics
    vor: Optional[float] = None  # Value Over Replacement
    vorp: Optional[float] = None  # Value Over Replacement Player
    tier: Optional[int] = None
    
    # Risk assessment
    injury_risk: Optional[str] = None  # "low", "medium", "high"
    bust_probability: Optional[float] = None
    breakout_probability: Optional[float] = None

class PlayerTier(BaseModel):
    """Player tier grouping"""
    tier: int
    position: str
    players: List[int]  # Player IDs
    min_vor: float
    max_vor: float
    tier_break_significance: float  # How significant the break to next tier is
    
class VORCalculation(BaseModel):
    """Value Over Replacement calculation"""
    position: str
    replacement_level: float  # Fantasy points of replacement player
    baseline_picks: Dict[str, int]  # Number of players typically drafted by position
    
    # Calculated values
    players_above_replacement: List[int]  # Player IDs
    vor_values: Dict[int, float]  # Player ID -> VOR value
