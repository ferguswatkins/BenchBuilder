"""
Yahoo Fantasy Data Service
Handles fetching and mapping Yahoo Fantasy API data to our internal models
"""
from typing import List, Dict, Any, Optional
from auth.yahoo_auth import yahoo_auth
from models.player import Player, PlayerProjection
from services.projection_service import projection_service
import asyncio
import logging

logger = logging.getLogger(__name__)

class YahooDataService:
    """Service for fetching and processing Yahoo Fantasy data"""
    
    def __init__(self):
        self.current_nfl_game_key = "449"  # 2024 NFL season - update annually
    
    async def fetch_and_store_player_projections(self, access_token: str, league_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch player data from Yahoo API and convert to our projection format
        """
        try:
            # Clear existing data first
            projection_service.clear_all_data()
            
            # Get current game info to ensure we have the right season
            game_info = await yahoo_auth.get_game_info(access_token, self.current_nfl_game_key)
            
            # Fetch all players in batches
            all_players = []
            start = 0
            batch_size = 25
            
            while True:
                logger.info(f"Fetching players batch starting at {start}")
                
                # Get players batch
                players_data = await yahoo_auth.get_all_players(
                    access_token, 
                    self.current_nfl_game_key, 
                    start, 
                    batch_size
                )
                
                # Extract players from Yahoo API response
                players_batch = self._extract_players_from_response(players_data)
                
                if not players_batch:
                    break
                    
                all_players.extend(players_batch)
                start += batch_size
                
                # Limit to prevent excessive API calls during development
                if len(all_players) >= 200:  # Get top 200 players
                    break
            
            logger.info(f"Fetched {len(all_players)} players from Yahoo API")
            
            # Convert Yahoo players to our projection format
            projections = []
            for yahoo_player in all_players:
                projection = self._convert_yahoo_player_to_projection(yahoo_player)
                if projection:
                    projections.append(projection)
            
            # Store projections in our system
            stored_count = 0
            for projection in projections:
                try:
                    projection_service.add_player_projection(
                        name=projection["name"],
                        position=projection["position"], 
                        team=projection["team"],
                        projections=projection["projections"]
                    )
                    stored_count += 1
                except Exception as e:
                    logger.warning(f"Failed to store projection for {projection['name']}: {e}")
            
            return {
                "success": True,
                "message": f"Successfully imported {stored_count} player projections from Yahoo Fantasy",
                "players_fetched": len(all_players),
                "projections_stored": stored_count,
                "game_info": game_info
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch Yahoo projections: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to import Yahoo Fantasy data"
            }
    
    def _extract_players_from_response(self, yahoo_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract player data from Yahoo API response structure
        Yahoo API returns nested XML-like structure converted to JSON
        """
        try:
            # Yahoo API structure: fantasy_content -> game -> players -> player[]
            fantasy_content = yahoo_response.get("fantasy_content", {})
            game = fantasy_content.get("game", {})
            players_data = game.get("players", {})
            
            if isinstance(players_data, dict):
                # Extract player array from the response
                players = []
                for key, value in players_data.items():
                    if key.isdigit():  # Yahoo uses numeric keys for players
                        if isinstance(value, dict) and "player" in value:
                            players.append(value["player"])
                return players
            
            return []
            
        except Exception as e:
            logger.error(f"Error extracting players from Yahoo response: {e}")
            return []
    
    def _convert_yahoo_player_to_projection(self, yahoo_player: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert Yahoo player data to our projection format
        """
        try:
            # Extract basic player info
            name = yahoo_player.get("name", {}).get("full", "Unknown")
            
            # Get position - Yahoo sometimes has multiple positions
            eligible_positions = yahoo_player.get("eligible_positions", {}).get("position", [])
            if isinstance(eligible_positions, list) and eligible_positions:
                position = eligible_positions[0].get("position", "UNKNOWN")
            elif isinstance(eligible_positions, dict):
                position = eligible_positions.get("position", "UNKNOWN")
            else:
                position = "UNKNOWN"
            
            # Get team
            editorial_team_abbr = yahoo_player.get("editorial_team_abbr", "FA")
            
            # Skip players without basic info
            if name == "Unknown" or position == "UNKNOWN":
                return None
            
            # Yahoo doesn't provide projections directly via basic API
            # We'll use historical stats or set default projections
            # In a real implementation, you'd need to:
            # 1. Use Yahoo's premium projection data if available
            # 2. Fetch recent season stats as proxy for projections
            # 3. Integrate with third-party projection sources
            
            # For now, create baseline projections based on position
            projections = self._create_baseline_projections(position, name, editorial_team_abbr)
            
            return {
                "name": name,
                "position": position,
                "team": editorial_team_abbr,
                "projections": projections,
                "yahoo_player_key": yahoo_player.get("player_key", ""),
                "yahoo_player_id": yahoo_player.get("player_id", "")
            }
            
        except Exception as e:
            logger.error(f"Error converting Yahoo player to projection: {e}")
            return None
    
    def _create_baseline_projections(self, position: str, name: str, team: str) -> PlayerProjection:
        """
        Create baseline projections for Yahoo players
        In production, this should fetch actual projection data
        """
        # Create conservative baseline projections based on position
        if position == "QB":
            return PlayerProjection(
                passing_yards=3500,
                passing_tds=25,
                interceptions=12,
                rushing_yards=300,
                rushing_tds=3
            )
        elif position == "RB":
            return PlayerProjection(
                rushing_yards=800,
                rushing_tds=6,
                receptions=30,
                receiving_yards=250,
                receiving_tds=2
            )
        elif position in ["WR", "WR/RB"]:
            return PlayerProjection(
                receptions=60,
                receiving_yards=800,
                receiving_tds=6,
                rushing_yards=20,
                rushing_tds=0
            )
        elif position == "TE":
            return PlayerProjection(
                receptions=45,
                receiving_yards=500,
                receiving_tds=4
            )
        elif position == "K":
            return PlayerProjection(
                field_goals=25,
                extra_points=35
            )
        elif position == "DEF":
            return PlayerProjection(
                def_touchdowns=1,
                def_interceptions=12,
                def_fumbles=8,
                def_sacks=35,
                def_safeties=1,
                points_allowed=350
            )
        else:
            # Default minimal projection
            return PlayerProjection()
    
    async def get_current_game_key(self, access_token: str) -> str:
        """
        Get the current NFL game key from Yahoo API
        """
        try:
            game_info = await yahoo_auth.get_game_info(access_token, "nfl")
            # Extract game key from response
            fantasy_content = game_info.get("fantasy_content", {})
            game = fantasy_content.get("game", {})
            return game.get("game_key", self.current_nfl_game_key)
        except Exception as e:
            logger.warning(f"Could not get current game key, using default: {e}")
            return self.current_nfl_game_key

# Global instance
yahoo_data_service = YahooDataService()
