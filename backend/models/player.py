"""
Player data models
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class Position(str, Enum):
    """Player positions"""
    QB = "QB"
    RB = "RB" 
    WR = "WR"
    TE = "TE"
    K = "K"
    DST = "DST"
    FLEX = "FLEX"

class Player(BaseModel):
    """Player model"""
    id: int
    name: str
    position: Position
    team: str
    yahoo_id: Optional[str] = None
    
    # Stats and projections
    projected_points: Optional[float] = None
    adp: Optional[float] = None
    vor: Optional[float] = None
    tier: Optional[int] = None
    
    # Additional metadata
    injury_status: Optional[str] = None
    bye_week: Optional[int] = None
    
    class Config:
        use_enum_values = True

class PlayerProjection(BaseModel):
    """Player projection data"""
    player_id: int
    
    # Offensive stats
    passing_yards: Optional[float] = None
    passing_tds: Optional[float] = None
    interceptions: Optional[float] = None
    rushing_yards: Optional[float] = None
    rushing_tds: Optional[float] = None
    receptions: Optional[float] = None
    receiving_yards: Optional[float] = None
    receiving_tds: Optional[float] = None
    
    # Kicker stats
    field_goals: Optional[float] = None
    extra_points: Optional[float] = None
    
    # Defense stats
    def_touchdowns: Optional[float] = None
    def_interceptions: Optional[float] = None
    def_fumbles: Optional[float] = None
    def_sacks: Optional[float] = None
    def_safeties: Optional[float] = None
    points_allowed: Optional[float] = None
    
    # Calculated fantasy points
    fantasy_points: Optional[float] = None
    
class PlayerADP(BaseModel):
    """Average Draft Position data"""
    player_id: int
    adp: float
    min_pick: int
    max_pick: int
    times_drafted: int
    source: str  # e.g., "fantasypros", "yahoo", "espn"
