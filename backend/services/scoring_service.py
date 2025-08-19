"""
Scoring service for calculating fantasy points
"""
from typing import Dict, Any, Optional, List
import logging
from models.league import League, ScoringType
from models.player import PlayerProjection, Position
from config.league_rules import SCORING_SETTINGS

logger = logging.getLogger(__name__)

class ScoringService:
    """Service for calculating fantasy points based on league scoring rules"""
    
    # Default scoring systems
    DEFAULT_SCORING_RULES = {
        ScoringType.STANDARD: {
            # Passing
            "pass_yard": 0.04,  # 1 point per 25 yards
            "pass_td": 4.0,
            "interception": -2.0,
            
            # Rushing
            "rush_yard": 0.1,   # 1 point per 10 yards
            "rush_td": 6.0,
            
            # Receiving
            "reception": 0.0,   # No PPR
            "rec_yard": 0.1,    # 1 point per 10 yards
            "rec_td": 6.0,
            
            # Kicking
            "fg_made": 3.0,
            "xp_made": 1.0,
            
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
        },
        ScoringType.PPR: {
            # Same as standard but with reception points
            "pass_yard": 0.04,
            "pass_td": 4.0,
            "interception": -2.0,
            "rush_yard": 0.1,
            "rush_td": 6.0,
            "reception": 1.0,   # Full PPR
            "rec_yard": 0.1,
            "rec_td": 6.0,
            "fg_made": 3.0,
            "xp_made": 1.0,
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
        },
        ScoringType.HALF_PPR: {
            # Same as standard but with half reception points
            "pass_yard": 0.04,
            "pass_td": 4.0,
            "interception": -2.0,
            "rush_yard": 0.1,
            "rush_td": 6.0,
            "reception": 0.5,   # Half PPR
            "rec_yard": 0.1,
            "rec_td": 6.0,
            "fg_made": 3.0,
            "xp_made": 1.0,
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
    }
    
    # League-specific scoring rules for Friends of Joseph E Aoun
    LEAGUE_SPECIFIC_RULES = {
        "friends_of_joseph_e_aoun": {
            # Passing (25 yards per point)
            "pass_yard": 0.04,  # 1 point per 25 yards
            "pass_td": 4.0,
            "interception": -1.0,  # -1 (not -2 like default)
            "pass_2pt": 2.0,
            
            # Rushing (10 yards per point)
            "rush_yard": 0.1,   # 1 point per 10 yards
            "rush_td": 6.0,
            "rush_2pt": 2.0,
            "fumble_lost": -2.0,
            
            # Receiving (Full PPR + 10 yards per point)
            "reception": 1.0,   # Full PPR - 1 point per reception
            "rec_yard": 0.1,    # 1 point per 10 yards
            "rec_td": 6.0,
            "rec_2pt": 2.0,
            
            # Return TDs
            "return_td": 6.0,
            "offensive_fumble_return_td": 6.0,
            
            # Kicking (Distance-based FG scoring)
            "fg_0_19": 3.0,
            "fg_20_29": 3.0,
            "fg_30_39": 3.0,
            "fg_40_49": 4.0,
            "fg_50_plus": 5.0,
            "xp_made": 1.0,
            
            # Defense/Special Teams
            "def_sack": 1.0,
            "def_int": 2.0,
            "def_fumble": 2.0,
            "def_td": 6.0,
            "def_safety": 2.0,
            "def_block_kick": 2.0,
            "def_return_td": 6.0,
            "def_xp_return": 2.0,
            
            # Points Allowed (Custom scoring)
            "points_allowed_0": 10.0,
            "points_allowed_1_6": 7.0,
            "points_allowed_7_13": 4.0,
            "points_allowed_14_20": 1.0,
            "points_allowed_21_27": 0.0,
            "points_allowed_28_34": -1.0,
            "points_allowed_35_plus": -4.0
        }
    }
    
    def __init__(self):
        """Initialize scoring service"""
        self.logger = logging.getLogger(__name__)
    
    def get_league_scoring_rules(self, league_id: str = "friends_of_joseph_e_aoun") -> Dict[str, float]:
        """Get scoring rules for a specific league"""
        return self.LEAGUE_SPECIFIC_RULES.get(league_id, self.DEFAULT_SCORING_RULES[ScoringType.PPR])
    
    def calculate_fantasy_points(self, 
                               projection: PlayerProjection, 
                               league: Optional[League] = None,
                               scoring_rules: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate fantasy points for a player projection
        
        Args:
            projection: Player projection data
            league: League with scoring rules (optional)
            scoring_rules: Custom scoring rules (optional, overrides league)
            
        Returns:
            Total fantasy points projected
        """
        try:
            # Determine scoring rules to use
            if scoring_rules:
                rules = scoring_rules
            elif league:
                rules = league.scoring_rules
            else:
                # Default to league-specific rules for Friends of Joseph E Aoun
                rules = self.get_league_scoring_rules()
            
            total_points = 0.0
            
            # Passing stats
            if projection.passing_yards:
                total_points += projection.passing_yards * rules.get("pass_yard", 0)
            if projection.passing_tds:
                total_points += projection.passing_tds * rules.get("pass_td", 0)
            if projection.interceptions:
                total_points += projection.interceptions * rules.get("interception", 0)
            
            # Rushing stats
            if projection.rushing_yards:
                total_points += projection.rushing_yards * rules.get("rush_yard", 0)
            if projection.rushing_tds:
                total_points += projection.rushing_tds * rules.get("rush_td", 0)
            
            # Receiving stats
            if projection.receptions:
                total_points += projection.receptions * rules.get("reception", 0)
            if projection.receiving_yards:
                total_points += projection.receiving_yards * rules.get("rec_yard", 0)
            if projection.receiving_tds:
                total_points += projection.receiving_tds * rules.get("rec_td", 0)
            
            # Kicking stats
            if projection.field_goals:
                # Use distance-based scoring if available, otherwise use generic
                if hasattr(projection, 'field_goals_by_distance') and projection.field_goals_by_distance:
                    total_points += self._calculate_distance_based_fg_points(
                        projection.field_goals_by_distance, rules
                    )
                else:
                    # Fallback to generic field goal scoring
                    total_points += projection.field_goals * rules.get("fg_made", rules.get("fg_30_39", 3))
            if projection.extra_points:
                total_points += projection.extra_points * rules.get("xp_made", 0)
            
            # Defense stats
            if projection.def_touchdowns:
                total_points += projection.def_touchdowns * rules.get("def_td", 0)
            if projection.def_interceptions:
                total_points += projection.def_interceptions * rules.get("def_int", 0)
            if projection.def_fumbles:
                total_points += projection.def_fumbles * rules.get("def_fumble", 0)
            if projection.def_sacks:
                total_points += projection.def_sacks * rules.get("def_sack", 0)
            if projection.def_safeties:
                total_points += projection.def_safeties * rules.get("def_safety", 0)
            
            # Points allowed (for defense)
            if projection.points_allowed is not None:
                points_allowed_score = self._calculate_points_allowed_score(
                    projection.points_allowed, rules
                )
                total_points += points_allowed_score
            
            return round(total_points, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating fantasy points: {str(e)}")
            return 0.0
    
    def _calculate_points_allowed_score(self, points_allowed: float, rules: Dict[str, float]) -> float:
        """Calculate defense points based on points allowed"""
        if points_allowed == 0:
            return rules.get("points_allowed_0", 0)
        elif points_allowed <= 6:
            return rules.get("points_allowed_1_6", 0)
        elif points_allowed <= 13:
            return rules.get("points_allowed_7_13", 0)
        elif points_allowed <= 20:
            return rules.get("points_allowed_14_20", 0)
        elif points_allowed <= 27:
            return rules.get("points_allowed_21_27", 0)
        elif points_allowed <= 34:
            return rules.get("points_allowed_28_34", 0)
        else:
            return rules.get("points_allowed_35_plus", 0)
    
    def _calculate_distance_based_fg_points(self, fg_by_distance: Dict[str, int], rules: Dict[str, float]) -> float:
        """Calculate field goal points based on distance ranges"""
        total_points = 0.0
        
        # Map distance ranges to scoring rules
        distance_mapping = {
            "0-19": rules.get("fg_0_19", 3),
            "20-29": rules.get("fg_20_29", 3), 
            "30-39": rules.get("fg_30_39", 3),
            "40-49": rules.get("fg_40_49", 4),
            "50+": rules.get("fg_50_plus", 5)
        }
        
        for distance_range, made_fgs in fg_by_distance.items():
            if distance_range in distance_mapping:
                total_points += made_fgs * distance_mapping[distance_range]
        
        return total_points
    
    def calculate_points_for_multiple_players(self,
                                            projections: List[PlayerProjection],
                                            league: Optional[League] = None,
                                            scoring_rules: Optional[Dict[str, float]] = None) -> Dict[int, float]:
        """
        Calculate fantasy points for multiple players
        
        Args:
            projections: List of player projections
            league: League with scoring rules
            scoring_rules: Custom scoring rules
            
        Returns:
            Dictionary mapping player_id to fantasy points
        """
        results = {}
        
        for projection in projections:
            points = self.calculate_fantasy_points(projection, league, scoring_rules)
            results[projection.player_id] = points
        
        return results
    
    def compare_scoring_systems(self, 
                              projection: PlayerProjection) -> Dict[str, float]:
        """
        Compare how a player scores in different scoring systems
        
        Args:
            projection: Player projection
            
        Returns:
            Dictionary with points for each scoring system
        """
        comparison = {}
        
        for scoring_type in ScoringType:
            rules = self.DEFAULT_SCORING_RULES[scoring_type]
            points = self.calculate_fantasy_points(projection, scoring_rules=rules)
            comparison[scoring_type.value] = points
        
        return comparison
    
    def get_scoring_breakdown(self, 
                            projection: PlayerProjection,
                            league: Optional[League] = None,
                            scoring_rules: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Get detailed breakdown of how fantasy points are calculated
        
        Args:
            projection: Player projection
            league: League with scoring rules
            scoring_rules: Custom scoring rules
            
        Returns:
            Dictionary with breakdown by stat category
        """
        # Determine scoring rules
        if scoring_rules:
            rules = scoring_rules
        elif league:
            rules = league.scoring_rules
        else:
            rules = self.get_league_scoring_rules()
        
        breakdown = {}
        
        # Passing
        if projection.passing_yards:
            breakdown["passing_yards"] = projection.passing_yards * rules.get("pass_yard", 0)
        if projection.passing_tds:
            breakdown["passing_tds"] = projection.passing_tds * rules.get("pass_td", 0)
        if projection.interceptions:
            breakdown["interceptions"] = projection.interceptions * rules.get("interception", 0)
        
        # Rushing
        if projection.rushing_yards:
            breakdown["rushing_yards"] = projection.rushing_yards * rules.get("rush_yard", 0)
        if projection.rushing_tds:
            breakdown["rushing_tds"] = projection.rushing_tds * rules.get("rush_td", 0)
        
        # Receiving
        if projection.receptions:
            breakdown["receptions"] = projection.receptions * rules.get("reception", 0)
        if projection.receiving_yards:
            breakdown["receiving_yards"] = projection.receiving_yards * rules.get("rec_yard", 0)
        if projection.receiving_tds:
            breakdown["receiving_tds"] = projection.receiving_tds * rules.get("rec_td", 0)
        
        # Kicking
        if projection.field_goals:
            breakdown["field_goals"] = projection.field_goals * rules.get("fg_made", 0)
        if projection.extra_points:
            breakdown["extra_points"] = projection.extra_points * rules.get("xp_made", 0)
        
        # Defense
        if projection.def_touchdowns:
            breakdown["def_touchdowns"] = projection.def_touchdowns * rules.get("def_td", 0)
        if projection.def_interceptions:
            breakdown["def_interceptions"] = projection.def_interceptions * rules.get("def_int", 0)
        if projection.def_fumbles:
            breakdown["def_fumbles"] = projection.def_fumbles * rules.get("def_fumble", 0)
        if projection.def_sacks:
            breakdown["def_sacks"] = projection.def_sacks * rules.get("def_sack", 0)
        if projection.def_safeties:
            breakdown["def_safeties"] = projection.def_safeties * rules.get("def_safety", 0)
        if projection.points_allowed is not None:
            breakdown["points_allowed"] = self._calculate_points_allowed_score(
                projection.points_allowed, rules
            )
        
        # Add total
        breakdown["total"] = sum(breakdown.values())
        
        return breakdown
    
    def create_custom_league(self, 
                           league_name: str,
                           scoring_type: ScoringType = ScoringType.PPR,
                           custom_rules: Optional[Dict[str, float]] = None) -> League:
        """
        Create a league with custom scoring rules
        
        Args:
            league_name: Name of the league
            scoring_type: Base scoring type to start from
            custom_rules: Custom scoring rules to override defaults
            
        Returns:
            League object with scoring rules
        """
        # Start with default rules for the scoring type
        base_rules = self.DEFAULT_SCORING_RULES[scoring_type].copy()
        
        # Override with custom rules if provided
        if custom_rules:
            base_rules.update(custom_rules)
        
        league = League(
            id=f"custom_{league_name.lower().replace(' ', '_')}",
            name=league_name,
            scoring_type=scoring_type,
            scoring_rules=base_rules
        )
        
        return league
    
    def validate_scoring_rules(self, rules: Dict[str, float]) -> List[str]:
        """
        Validate scoring rules and return any warnings
        
        Args:
            rules: Scoring rules dictionary
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check for common rules
        required_rules = [
            "pass_yard", "pass_td", "rush_yard", "rush_td", 
            "reception", "rec_yard", "rec_td"
        ]
        
        for rule in required_rules:
            if rule not in rules:
                warnings.append(f"Missing scoring rule: {rule}")
        
        # Check for reasonable values
        if rules.get("pass_td", 0) < 1:
            warnings.append("Passing TD points seem low (< 1)")
        if rules.get("rush_td", 0) < 1:
            warnings.append("Rushing TD points seem low (< 1)")
        if rules.get("rec_td", 0) < 1:
            warnings.append("Receiving TD points seem low (< 1)")
        
        return warnings

# Global service instance
scoring_service = ScoringService()
