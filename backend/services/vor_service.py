"""
Value Over Replacement (VOR) calculation service
"""
from typing import Dict, List, Optional, Tuple, Any
import logging
from statistics import mean
from models.player import Player, Position
from models.league import League
from models.projection import VORCalculation
from services.projection_service import projection_service
from services.scoring_service import scoring_service
from config.league_rules import (
    ROSTER_POSITIONS, STARTING_POSITIONS, TOTAL_ROSTER_SIZE,
    get_position_scarcity_multiplier, get_replacement_level_rank
)

logger = logging.getLogger(__name__)

class VORService:
    """Service for calculating Value Over Replacement (VOR) for players"""
    
    # Default roster construction for Friends of Joseph E Aoun (14-team league)
    DEFAULT_ROSTER_CONSTRUCTION = {
        Position.QB: 14,    # 1 QB per team
        Position.RB: 28,    # 2 RB per team  
        Position.WR: 28,    # 2 WR per team
        Position.TE: 14,    # 1 TE per team
        Position.K: 14,     # 1 K per team
        Position.DST: 14,   # 1 DST per team
    }
    
    # League-specific roster construction based on actual roster positions
    LEAGUE_ROSTER_CONSTRUCTION = {
        Position.QB: 14,     # 1 QB * 14 teams
        Position.RB: 42,     # (2 RB + 1 FLEX eligible) * 14 teams  
        Position.WR: 42,     # (2 WR + 1 FLEX eligible) * 14 teams
        Position.TE: 28,     # (1 TE + 1 FLEX eligible) * 14 teams
        Position.K: 14,      # 1 K * 14 teams
        Position.DST: 14,    # 1 DST * 14 teams
    }
    
    # Flex positions that can be filled by multiple position types
    FLEX_POSITIONS = {
        'FLEX': [Position.RB, Position.WR, Position.TE],  # W/R/T flex
        'SUPERFLEX': [Position.QB, Position.RB, Position.WR, Position.TE]
        }
    
    def __init__(self):
        """Initialize VOR service"""
        self.logger = logging.getLogger(__name__)
        self.vor_cache = {}  # Cache VOR calculations
    
    def calculate_vor_rankings(self,
                             league: Optional[League] = None,
                             num_teams: int = 14,  # Default to 14 teams for our league
                             include_flex: bool = True,
                             custom_roster: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Calculate VOR for all players and return rankings
        
        Args:
            league: League with scoring rules
            num_teams: Number of teams in league
            include_flex: Whether to include flex positions
            custom_roster: Custom roster construction
            
        Returns:
            Dictionary with VOR calculations and rankings
        """
        try:
            # Get all projections with calculated fantasy points
            projections_data = projection_service.get_projections()
            if not projections_data:
                return {"error": "No projection data available"}
            
            # Calculate fantasy points for all players
            players_with_points = []
            for i, player_data in enumerate(projections_data):
                try:
                    # Player data is already a dict from projection service
                    player_dict = player_data['player']
                    self.logger.debug(f"Processing player {i}: {player_dict}")
                    
                    player = Player(
                        id=player_dict['id'],
                        name=player_dict['name'],
                        position=Position(player_dict['position']),
                        team=player_dict.get('team', '')
                    )
                    projection = player_data['projection']
                    
                    # Calculate fantasy points using scoring service
                    from models.player import PlayerProjection
                    projection_obj = PlayerProjection(**projection)
                    fantasy_points = scoring_service.calculate_fantasy_points(
                        projection=projection_obj,
                        league=league
                    )
                    
                    players_with_points.append({
                        'player': player,
                        'fantasy_points': fantasy_points,
                        'projection': projection
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error processing player {i}: {str(e)}")
                    self.logger.error(f"Player data: {player_data}")
                    raise
            
            # Sort by fantasy points within each position
            position_rankings = self._create_position_rankings(players_with_points)
            
            # Determine roster construction
            roster_construction = self._get_roster_construction(
                custom_roster, num_teams, include_flex
            )
            
            # Calculate replacement levels for each position
            replacement_levels = self._calculate_replacement_levels(
                position_rankings, roster_construction
            )
            
            # Calculate VOR for each player
            vor_results = self._calculate_vor_values(
                players_with_points, replacement_levels
            )
            
            # Create overall rankings
            overall_rankings = self._create_overall_rankings(vor_results)
            
            return {
                'vor_rankings': overall_rankings,
                'position_rankings': position_rankings,
                'replacement_levels': replacement_levels,
                'roster_construction': roster_construction,
                'total_players': len(players_with_points),
                'league_size': num_teams
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating VOR rankings: {str(e)}")
            raise ValueError(f"Failed to calculate VOR: {str(e)}")
    
    def _create_position_rankings(self, players_with_points: List[Dict]) -> Dict[str, List[Dict]]:
        """Create rankings within each position"""
        position_rankings = {}
        
        for player_data in players_with_points:
            # Handle different ways position might be stored
            if hasattr(player_data['player'], 'position'):
                if hasattr(player_data['player'].position, 'value'):
                    position = player_data['player'].position.value
                else:
                    position = str(player_data['player'].position)
            else:
                position = player_data.get('position', 'UNKNOWN')
            
            if position not in position_rankings:
                position_rankings[position] = []
            
            position_rankings[position].append(player_data)
        
        # Sort each position by fantasy points
        for position in position_rankings:
            position_rankings[position].sort(
                key=lambda x: x['fantasy_points'], 
                reverse=True
            )
            
            # Add position rank
            for i, player_data in enumerate(position_rankings[position]):
                player_data['position_rank'] = i + 1
        
        return position_rankings
    
    def _get_roster_construction(self, 
                               custom_roster: Optional[Dict[str, int]],
                               num_teams: int,
                               include_flex: bool) -> Dict[str, int]:
        """Determine roster construction for VOR calculation"""
        if custom_roster:
            return custom_roster
        
        # Use league-specific roster construction if 14 teams, otherwise scale default
        if num_teams == 14:
            roster = {}
            for position, total_starters in self.LEAGUE_ROSTER_CONSTRUCTION.items():
                roster[position.value] = total_starters
        else:
            # Scale default construction to league size
            roster = {}
            for position, per_team in self.DEFAULT_ROSTER_CONSTRUCTION.items():
                roster[position.value] = per_team * num_teams // 14  # Scale from 14-team base
        
        # Add flex positions if requested
        if include_flex:
            flex_spots = num_teams  # 1 flex per team
            roster['FLEX'] = flex_spots
        
        return roster
    
    def _calculate_replacement_levels(self, 
                                    position_rankings: Dict[str, List[Dict]],
                                    roster_construction: Dict[str, int]) -> Dict[str, float]:
        """Calculate replacement level fantasy points for each position"""
        replacement_levels = {}
        
        for position, num_drafted in roster_construction.items():
            if position == 'FLEX':
                # For flex, calculate based on worst starter among RB/WR/TE
                flex_candidates = []
                for flex_pos in ['RB', 'WR', 'TE']:
                    if flex_pos in position_rankings:
                        # Add players beyond the normal starters
                        normal_starters = roster_construction.get(flex_pos, 0)
                        remaining_players = position_rankings[flex_pos][normal_starters:]
                        flex_candidates.extend(remaining_players)
                
                if flex_candidates:
                    # Sort flex candidates and find replacement level
                    flex_candidates.sort(key=lambda x: x['fantasy_points'], reverse=True)
                    if len(flex_candidates) >= num_drafted:
                        replacement_levels[position] = flex_candidates[num_drafted - 1]['fantasy_points']
                    else:
                        replacement_levels[position] = flex_candidates[-1]['fantasy_points'] if flex_candidates else 0
                else:
                    replacement_levels[position] = 0
                    
            elif position in position_rankings:
                # For regular positions, replacement level is the last starter
                players = position_rankings[position]
                if len(players) >= num_drafted:
                    replacement_levels[position] = players[num_drafted - 1]['fantasy_points']
                elif players:
                    # If not enough players, use the worst available
                    replacement_levels[position] = players[-1]['fantasy_points']
                else:
                    replacement_levels[position] = 0
            else:
                replacement_levels[position] = 0
        
        return replacement_levels
    
    def _calculate_vor_values(self, 
                            players_with_points: List[Dict],
                            replacement_levels: Dict[str, float]) -> List[Dict]:
        """Calculate VOR for each player"""
        vor_results = []
        
        for player_data in players_with_points:
            # Handle different ways position might be stored
            if hasattr(player_data['player'], 'position'):
                if hasattr(player_data['player'].position, 'value'):
                    position = player_data['player'].position.value
                else:
                    position = str(player_data['player'].position)
            else:
                position = player_data.get('position', 'UNKNOWN')
                
            fantasy_points = player_data['fantasy_points']
            
            # Get replacement level for this position
            replacement_level = replacement_levels.get(position, 0)
            
            # Calculate VOR
            vor = fantasy_points - replacement_level
            
            # Also calculate flex VOR if applicable
            flex_vor = None
            if position in ['RB', 'WR', 'TE'] and 'FLEX' in replacement_levels:
                flex_replacement = replacement_levels['FLEX']
                flex_vor = fantasy_points - flex_replacement
                # Use the better VOR (position vs flex)
                vor = max(vor, flex_vor)
            
            # Apply position scarcity multiplier for league-specific adjustments
            scarcity_multiplier = get_position_scarcity_multiplier(position)
            adjusted_vor = vor * scarcity_multiplier
            
            result = player_data.copy()
            result.update({
                'vor': vor,
                'adjusted_vor': adjusted_vor,
                'flex_vor': flex_vor,
                'replacement_level': replacement_level,
                'scarcity_multiplier': scarcity_multiplier,
                'value_tier': self._get_value_tier(adjusted_vor)
            })
            
            vor_results.append(result)
        
        return vor_results
    
    def _get_value_tier(self, vor: float) -> str:
        """Categorize players into value tiers based on VOR"""
        if vor >= 100:
            return "Elite"
        elif vor >= 50:
            return "High"
        elif vor >= 20:
            return "Medium"
        elif vor >= 0:
            return "Low"
        else:
            return "Below Replacement"
    
    def _create_overall_rankings(self, vor_results: List[Dict]) -> List[Dict]:
        """Create overall rankings sorted by adjusted VOR"""
        # Sort by adjusted VOR descending (accounts for position scarcity)
        overall_rankings = sorted(vor_results, key=lambda x: x['adjusted_vor'], reverse=True)
        
        # Add overall rank
        for i, player_data in enumerate(overall_rankings):
            player_data['overall_rank'] = i + 1
        
        return overall_rankings
    
    def get_position_vor_rankings(self, 
                                position: str,
                                league: Optional[League] = None,
                                limit: Optional[int] = None) -> List[Dict]:
        """Get VOR rankings for a specific position"""
        try:
            # Calculate full VOR rankings
            vor_data = self.calculate_vor_rankings(league=league)
            
            # Filter by position
            position_players = []
            for player_data in vor_data['vor_rankings']:
                if player_data['player'].position.value == position.upper():
                    position_players.append(player_data)
            
            # Apply limit if specified
            if limit:
                position_players = position_players[:limit]
            
            return position_players
            
        except Exception as e:
            self.logger.error(f"Error getting position VOR rankings: {str(e)}")
            return []
    
    def compare_players_vor(self, 
                          player_ids: List[int],
                          league: Optional[League] = None) -> Dict[str, Any]:
        """Compare VOR between specific players"""
        try:
            # Calculate VOR for all players
            vor_data = self.calculate_vor_rankings(league=league)
            
            # Find requested players
            player_comparisons = []
            for player_data in vor_data['vor_rankings']:
                if player_data['player'].id in player_ids:
                    player_comparisons.append(player_data)
            
            # Sort by adjusted VOR
            player_comparisons.sort(key=lambda x: x['adjusted_vor'], reverse=True)
            
            return {
                'players': player_comparisons,
                'best_value': player_comparisons[0] if player_comparisons else None,
                'vor_differences': self._calculate_vor_differences(player_comparisons)
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing players VOR: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_vor_differences(self, players: List[Dict]) -> List[Dict]:
        """Calculate VOR differences between players"""
        if len(players) < 2:
            return []
        
        differences = []
        best_player = players[0]
        
        for i in range(1, len(players)):
            player = players[i]
            difference = {
                'player1': best_player['player'].name,
                'player2': player['player'].name,
                'vor_difference': best_player['vor'] - player['vor'],
                'adjusted_vor_difference': best_player['adjusted_vor'] - player['adjusted_vor'],
                'points_difference': best_player['fantasy_points'] - player['fantasy_points']
            }
            differences.append(difference)
        
        return differences
    
    def get_draft_targets_by_vor(self,
                               round_number: int,
                               draft_position: int,
                               league: Optional[League] = None,
                               num_teams: int = 12) -> Dict[str, Any]:
        """Get best VOR targets for a specific draft position"""
        try:
            # Calculate overall pick number
            if round_number % 2 == 1:  # Odd rounds (snake draft)
                overall_pick = (round_number - 1) * num_teams + draft_position
            else:  # Even rounds (snake draft reverses)
                overall_pick = (round_number - 1) * num_teams + (num_teams - draft_position + 1)
            
            # Get VOR rankings
            vor_data = self.calculate_vor_rankings(league=league, num_teams=num_teams)
            
            # Find players likely to be available (rough estimate)
            available_players = []
            for player_data in vor_data['vor_rankings']:
                # Simple availability heuristic based on VOR rank vs pick number
                if player_data['overall_rank'] >= overall_pick - 5:  # Some buffer
                    available_players.append(player_data)
            
            # Group by position
            targets_by_position = {}
            for player_data in available_players[:20]:  # Top 20 available
                # Handle different ways position might be stored
                if hasattr(player_data['player'], 'position'):
                    if hasattr(player_data['player'].position, 'value'):
                        position = player_data['player'].position.value
                    else:
                        position = str(player_data['player'].position)
                else:
                    position = player_data.get('position', 'UNKNOWN')
                
                if position not in targets_by_position:
                    targets_by_position[position] = []
                targets_by_position[position].append(player_data)
            
            return {
                'round': round_number,
                'pick': draft_position,
                'overall_pick': overall_pick,
                'targets_by_position': targets_by_position,
                'top_targets': available_players[:10]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting draft targets: {str(e)}")
            return {"error": str(e)}

# Global service instance
vor_service = VORService()
