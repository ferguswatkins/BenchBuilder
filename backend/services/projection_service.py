"""
Projection data management service
"""
from typing import List, Dict, Any, Optional, Union
import logging
from datetime import datetime
import json
from pathlib import Path

from models.player import Player, PlayerProjection, Position
from models.projection import ProjectionSource, SeasonProjection
from utils.csv_parser import ProjectionCSVParser

logger = logging.getLogger(__name__)

class ProjectionService:
    """Service for managing player projection data"""
    
    def __init__(self):
        """Initialize projection service"""
        self.parser = ProjectionCSVParser()
        self.projections: Dict[int, PlayerProjection] = {}
        self.players: Dict[int, Player] = {}
        self.sources: Dict[str, ProjectionSource] = {}
        self.next_player_id = 1
        
    def upload_projections(self, 
                         file_content: Union[str, bytes],
                         source_name: str = "uploaded",
                         source_type: str = "auto") -> Dict[str, Any]:
        """
        Upload and process projection data from CSV
        
        Args:
            file_content: CSV content
            source_name: Name of the projection source
            source_type: Type/format of the CSV (auto, fantasypros, yahoo, espn)
            
        Returns:
            Dictionary with upload results
        """
        try:
            # Parse CSV data
            parsed_data = self.parser.parse_csv(file_content, source_type)
            
            # Process parsed data
            results = self._process_projection_data(parsed_data, source_name)
            
            # Update source metadata
            self.sources[source_name] = ProjectionSource(
                name=source_name,
                last_updated=datetime.now(),
                reliability_score=1.0  # Default score
            )
            
            logger.info(f"Successfully uploaded {results['players_processed']} projections from {source_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error uploading projections: {str(e)}")
            raise ValueError(f"Failed to upload projections: {str(e)}")
    
    def _process_projection_data(self, data: List[Dict[str, Any]], source: str) -> Dict[str, Any]:
        """Process parsed projection data"""
        players_created = 0
        players_updated = 0
        projections_created = 0
        errors = []
        
        for player_data in data:
            try:
                # Find or create player
                player_id = self._find_or_create_player(player_data)
                
                if player_id in self.players:
                    players_updated += 1
                else:
                    players_created += 1
                
                # Create projection
                projection = self._create_projection(player_id, player_data, source)
                self.projections[player_id] = projection
                projections_created += 1
                
            except Exception as e:
                error_msg = f"Error processing {player_data.get('name', 'unknown')}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
        
        return {
            'players_processed': len(data),
            'players_created': players_created,
            'players_updated': players_updated,
            'projections_created': projections_created,
            'errors': errors,
            'source': source
        }
    
    def _find_or_create_player(self, player_data: Dict[str, Any]) -> int:
        """Find existing player or create new one"""
        name = player_data.get('name', '').strip()
        position = player_data.get('position', '').strip()
        team = player_data.get('team', '').strip()
        
        # Try to find existing player by name and position
        for player_id, player in self.players.items():
            if (player.name.lower() == name.lower() and 
                player.position.value == position):
                # Update team if different
                if player.team != team and team:
                    player.team = team
                return player_id
        
        # Create new player
        player_id = self.next_player_id
        self.next_player_id += 1
        
        try:
            position_enum = Position(position)
        except ValueError:
            logger.warning(f"Unknown position {position} for {name}, using WR as default")
            position_enum = Position.WR
        
        player = Player(
            id=player_id,
            name=name,
            position=position_enum,
            team=team
        )
        
        self.players[player_id] = player
        return player_id
    
    def _create_projection(self, player_id: int, data: Dict[str, Any], source: str) -> PlayerProjection:
        """Create PlayerProjection from parsed data"""
        projection = PlayerProjection(
            player_id=player_id,
            passing_yards=data.get('passing_yards'),
            passing_tds=data.get('passing_tds'),
            interceptions=data.get('interceptions'),
            rushing_yards=data.get('rushing_yards'),
            rushing_tds=data.get('rushing_tds'),
            receptions=data.get('receptions'),
            receiving_yards=data.get('receiving_yards'),
            receiving_tds=data.get('receiving_tds'),
            field_goals=data.get('field_goals'),
            extra_points=data.get('extra_points'),
            fantasy_points=data.get('fantasy_points')
        )
        
        return projection
    
    def get_projections(self, 
                       position: Optional[str] = None,
                       team: Optional[str] = None,
                       limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get projections with optional filtering
        
        Args:
            position: Filter by position
            team: Filter by team
            limit: Limit number of results
            
        Returns:
            List of player projections with player info
        """
        results = []
        
        for player_id, projection in self.projections.items():
            player = self.players.get(player_id)
            if not player:
                continue
                
            # Apply filters
            if position and player.position.value != position.upper():
                continue
            if team and player.team != team.upper():
                continue
            
            # Combine player and projection data
            result = {
                'player': player.dict(),
                'projection': projection.dict()
            }
            results.append(result)
        
        # Sort by fantasy points if available
        results.sort(key=lambda x: x['projection'].get('fantasy_points') or 0, reverse=True)
        
        # Apply limit
        if limit:
            results = results[:limit]
            
        return results
    
    def get_player_projection(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get specific player's projection"""
        player = self.players.get(player_id)
        projection = self.projections.get(player_id)
        
        if not player or not projection:
            return None
            
        return {
            'player': player.dict(),
            'projection': projection.dict()
        }
    
    def search_players(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search players by name"""
        query_lower = query.lower()
        results = []
        
        for player_id, player in self.players.items():
            if query_lower in player.name.lower():
                projection = self.projections.get(player_id)
                result = {
                    'player': player.dict(),
                    'projection': projection.dict() if projection else None
                }
                results.append(result)
        
        # Sort by fantasy points
        results.sort(key=lambda x: (x['projection'] or {}).get('fantasy_points') or 0, reverse=True)
        return results[:limit]
    
    def get_sources(self) -> List[Dict[str, Any]]:
        """Get all projection sources"""
        return [source.dict() for source in self.sources.values()]
    
    def clear_projections(self, source: Optional[str] = None):
        """Clear projections, optionally for specific source"""
        if source:
            # Would need to track source per projection to implement this
            logger.warning("Source-specific clearing not implemented yet")
        else:
            self.projections.clear()
            self.players.clear()
            self.sources.clear()
            self.next_player_id = 1
        
        logger.info(f"Cleared projections{' for source: ' + source if source else ''}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get projection statistics"""
        position_counts = {}
        total_projections = len(self.projections)
        
        for player in self.players.values():
            pos = player.position.value
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        return {
            'total_players': len(self.players),
            'total_projections': total_projections,
            'position_breakdown': position_counts,
            'sources': len(self.sources),
            'last_updated': max([s.last_updated for s in self.sources.values()], default=None)
        }

# Global service instance
projection_service = ProjectionService()
