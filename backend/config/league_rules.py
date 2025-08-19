"""
League Rules Configuration for Friends of Joseph E Aoun
League ID: 281565

This file contains all league-specific rules and scoring settings
that affect our draft algorithms and value calculations.
"""

from typing import Dict, List, Any

# Basic League Settings
LEAGUE_CONFIG = {
    "league_id": 281565,
    "league_name": "Friends of Joseph E Aoun",
    "max_teams": 14,
    "draft_type": "Live Standard Draft",
    "scoring_type": "Head-to-Head",
    "playoffs": {
        "teams": 6,
        "weeks": [15, 16, 17],
        "end_date": "Monday, Dec 29"
    },
    "waivers": {
        "type": "Continual rolling list",
        "time": "2 days",
        "weekly_waivers": "Game Time - Tuesday"
    },
    "trades": {
        "max_per_season": None,  # No maximum
        "end_date": "November 22, 2025",
        "review": "League Votes",
        "reject_time": "2 days"
    }
}

# Roster Configuration
ROSTER_POSITIONS = {
    "QB": 1,
    "WR": 2,
    "RB": 2, 
    "TE": 1,
    "FLEX": 1,  # W/R/T flex position
    "K": 1,
    "DEF": 1,
    "BN": 6,  # Bench spots
    "IR": 2   # Injured Reserve spots
}

# Total roster size for VOR calculations
TOTAL_ROSTER_SIZE = sum(ROSTER_POSITIONS.values()) - ROSTER_POSITIONS["IR"]  # 14 spots (excluding IR)

# Starting lineup positions (excluding bench and IR)
STARTING_POSITIONS = {
    "QB": 1,
    "WR": 2,
    "RB": 2,
    "TE": 1,
    "FLEX": 1,  # Can be WR, RB, or TE
    "K": 1,
    "DEF": 1
}

# Scoring Configuration
SCORING_SETTINGS = {
    "fractional_points": True,
    "negative_points": True,
    
    # Passing
    "passing": {
        "yards_per_point": 25,  # 1 point per 25 yards
        "touchdown": 4,
        "interception": -1,
        "two_point_conversion": 2
    },
    
    # Rushing  
    "rushing": {
        "yards_per_point": 10,  # 1 point per 10 yards
        "touchdown": 6,
        "two_point_conversion": 2,
        "fumble_lost": -2
    },
    
    # Receiving
    "receiving": {
        "reception": 1,  # Full PPR (1 point per reception)
        "yards_per_point": 10,  # 1 point per 10 yards
        "touchdown": 6,
        "two_point_conversion": 2,
        "fumble_lost": -2
    },
    
    # Return TDs
    "return_touchdown": 6,
    "offensive_fumble_return_td": 6,
    
    # Kicking
    "kicking": {
        "fg_0_19": 3,
        "fg_20_29": 3,
        "fg_30_39": 3,
        "fg_40_49": 4,
        "fg_50_plus": 5,
        "pat_made": 1
    },
    
    # Defense/Special Teams
    "defense": {
        "sack": 1,
        "interception": 2,
        "fumble_recovery": 2,
        "touchdown": 6,
        "safety": 2,
        "block_kick": 2,
        "return_touchdown": 6,
        "extra_point_returned": 2,
        
        # Points allowed scoring (key difference from standard)
        "points_allowed": {
            0: 10,      # 0 points allowed = 10 fantasy points
            1: 7,       # 1-6 points allowed = 7 fantasy points
            7: 4,       # 7-13 points allowed = 4 fantasy points
            14: 1,      # 14-20 points allowed = 1 fantasy point
            21: 0,      # 21-27 points allowed = 0 fantasy points
            28: -1,     # 28-34 points allowed = -1 fantasy point
            35: -4      # 35+ points allowed = -4 fantasy points
        }
    }
}

# Key differences from standard scoring that affect our algorithms:
SCORING_DIFFERENCES = {
    "full_ppr": True,  # 1 point per reception vs 0.5 in half-PPR
    "passing_yards": 25,  # 25 yards per point vs standard 25
    "defense_points_allowed": "custom",  # Custom PA scoring vs standard
    "roster_size": 14,  # 14 teams vs standard 10-12
    "bench_spots": 6,  # 6 bench spots vs standard 4-5
    "flex_positions": 1,  # 1 flex spot (W/R/T)
}

def get_position_scarcity_multiplier(position: str) -> float:
    """
    Calculate position scarcity multiplier based on league size and roster requirements.
    Used in VOR calculations.
    """
    if position == "QB":
        # 14 teams * 1 QB = 14 starters, but many teams carry backup QBs
        return 1.0
    elif position in ["RB", "WR"]:
        # High demand positions with flex eligibility
        # RB: 14 teams * 2 RB + flex eligibility = high scarcity
        # WR: 14 teams * 2 WR + flex eligibility = high scarcity  
        return 1.2
    elif position == "TE":
        # 14 teams * 1 TE + flex eligibility = moderate scarcity
        return 1.1
    elif position == "K":
        # 14 teams * 1 K = low scarcity, streaming position
        return 0.8
    elif position == "DEF":
        # 14 teams * 1 DEF = low scarcity, streaming position
        return 0.8
    else:
        return 1.0

def get_replacement_level_rank(position: str) -> int:
    """
    Calculate the replacement level rank for VOR calculations.
    Based on number of starters + reasonable bench depth.
    """
    if position == "QB":
        # 14 starters + ~10 quality backups = rank 24
        return 24
    elif position == "RB":
        # 14*2 starters + 14 flex + ~20 quality backups = rank 62
        return 62
    elif position == "WR": 
        # 14*2 starters + 14 flex + ~25 quality backups = rank 67
        return 67
    elif position == "TE":
        # 14 starters + 14 flex eligible + ~15 quality backups = rank 43
        return 43
    elif position == "K":
        # Streaming position, replacement level = rank 20
        return 20
    elif position == "DEF":
        # Streaming position, replacement level = rank 20  
        return 20
    else:
        return 50

# Export key configurations for easy import
__all__ = [
    'LEAGUE_CONFIG',
    'ROSTER_POSITIONS', 
    'STARTING_POSITIONS',
    'TOTAL_ROSTER_SIZE',
    'SCORING_SETTINGS',
    'SCORING_DIFFERENCES',
    'get_position_scarcity_multiplier',
    'get_replacement_level_rank'
]
