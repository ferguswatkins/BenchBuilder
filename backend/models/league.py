"""
League data models
"""
from pydantic import BaseModel
from typing import Optional, Dict, List
from enum import Enum

class ScoringType(str, Enum):
    """Scoring system types"""
    STANDARD = "standard"
    PPR = "ppr"
    HALF_PPR = "half_ppr"

class League(BaseModel):
    """Fantasy league model"""
    id: str
    name: str
    yahoo_league_id: Optional[str] = None
    
    # League settings
    num_teams: int = 12
    scoring_type: ScoringType = ScoringType.PPR
    roster_positions: Dict[str, int] = {
        "QB": 1,
        "RB": 2, 
        "WR": 2,
        "TE": 1,
        "FLEX": 1,
        "K": 1,
        "DST": 1,
        "BENCH": 6
    }
    
    # Scoring rules
    scoring_rules: Dict[str, float] = {
        # Passing
        "pass_yard": 0.04,  # 1 point per 25 yards
        "pass_td": 4.0,
        "interception": -2.0,
        
        # Rushing
        "rush_yard": 0.1,   # 1 point per 10 yards
        "rush_td": 6.0,
        
        # Receiving
        "reception": 1.0,   # PPR
        "rec_yard": 0.1,    # 1 point per 10 yards
        "rec_td": 6.0,
        
        # Kicking
        "fg_made": 3.0,
        "xp_made": 1.0,
        "fg_miss": -1.0,
        
        # Defense
        "def_td": 6.0,
        "def_int": 2.0,
        "def_fumble": 2.0,
        "def_sack": 1.0,
        "def_safety": 2.0,
        "points_allowed_0": 10.0,
        "points_allowed_1_6": 7.0,
        "points_allowed_7_13": 4.0,
        "points_allowed_14_20": 1.0,
        "points_allowed_21_27": 0.0,
        "points_allowed_28_34": -1.0,
        "points_allowed_35_plus": -4.0
    }
    
    # Draft settings
    draft_type: str = "snake"  # "snake" or "linear"
    seconds_per_pick: int = 90
    
    class Config:
        use_enum_values = True

class Team(BaseModel):
    """Fantasy team model"""
    id: str
    name: str
    owner_name: str
    league_id: str
    draft_position: Optional[int] = None
    
class RosterSlot(BaseModel):
    """Roster slot configuration"""
    position: str
    count: int
    is_flex: bool = False
