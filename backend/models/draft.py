"""
Draft data models
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class DraftStatus(str, Enum):
    """Draft status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"

class Draft(BaseModel):
    """Draft model"""
    id: str
    league_id: str
    status: DraftStatus = DraftStatus.NOT_STARTED
    
    # Draft settings
    total_rounds: int = 16
    current_round: int = 1
    current_pick: int = 1
    current_team_id: Optional[str] = None
    
    # Timing
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    seconds_per_pick: int = 90
    
    # Draft order
    draft_order: List[str] = []  # List of team IDs
    is_snake_draft: bool = True
    
    class Config:
        use_enum_values = True

class DraftPick(BaseModel):
    """Individual draft pick"""
    id: str
    draft_id: str
    round_number: int
    pick_number: int
    overall_pick: int
    team_id: str
    player_id: Optional[int] = None
    player_name: Optional[str] = None
    
    # Timing
    picked_at: Optional[datetime] = None
    time_remaining: Optional[int] = None
    
    # Auto-pick info
    is_auto_pick: bool = False
    
class DraftState(BaseModel):
    """Current draft state"""
    draft: Draft
    picks: List[DraftPick]
    available_players: List[int] = []  # Player IDs still available
    
    # Current pick info
    current_pick_info: Optional[DraftPick] = None
    next_picks: List[DraftPick] = []  # Next few picks for planning

class DraftRecommendation(BaseModel):
    """Draft pick recommendation"""
    player_id: int
    player_name: str
    position: str
    team: str
    
    # Scoring metrics
    vor_score: float
    tier: int
    projected_points: float
    adp: Optional[float] = None
    adp_delta: Optional[float] = None  # Difference from current pick
    
    # Availability prediction
    availability_next_round: Optional[float] = None
    availability_two_rounds: Optional[float] = None
    
    # Roster construction
    positional_need: str  # "high", "medium", "low"
    
    # Overall recommendation score
    recommendation_score: float
    
    # LLM explanation
    explanation: Optional[str] = None
