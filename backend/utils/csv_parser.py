"""
CSV parser for projection data
"""
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from io import StringIO, BytesIO
import logging
from models.player import Player, PlayerProjection, Position

logger = logging.getLogger(__name__)

class ProjectionCSVParser:
    """Parser for various projection CSV formats"""
    
    # Common column mappings for different sources
    COLUMN_MAPPINGS = {
        'fantasypros': {
            'name': ['Player', 'Name', 'player'],
            'position': ['Pos', 'Position', 'position'],
            'team': ['Team', 'Tm', 'team'],
            'passing_yards': ['Pass Yds', 'PassYds', 'passing_yards', 'PaYds'],
            'passing_tds': ['Pass TD', 'PassTD', 'passing_tds', 'PaTD'],
            'interceptions': ['Int', 'INT', 'interceptions', 'PaInt'],
            'rushing_yards': ['Rush Yds', 'RushYds', 'rushing_yards', 'RuYds'],
            'rushing_tds': ['Rush TD', 'RushTD', 'rushing_tds', 'RuTD'],
            'receptions': ['Rec', 'REC', 'receptions', 'Receptions'],
            'receiving_yards': ['Rec Yds', 'RecYds', 'receiving_yards', 'ReYds'],
            'receiving_tds': ['Rec TD', 'RecTD', 'receiving_tds', 'ReTD'],
            'fantasy_points': ['FPTS', 'Fantasy Points', 'fantasy_points', 'Points'],
            'field_goals': ['FG', 'Field Goals', 'field_goals'],
            'extra_points': ['XP', 'Extra Points', 'extra_points'],
        },
        'yahoo': {
            'name': ['Name', 'Player Name'],
            'position': ['Position', 'Pos'],
            'team': ['Team'],
            'fantasy_points': ['Projected Points', 'Proj Pts'],
        },
        'espn': {
            'name': ['PLAYER', 'Player'],
            'position': ['POS'],
            'team': ['TEAM'],
            'fantasy_points': ['PROJ'],
        }
    }
    
    def __init__(self, source: str = 'auto'):
        """Initialize parser with source type"""
        self.source = source
        self.logger = logging.getLogger(f"{__name__}.{source}")
    
    def parse_csv(self, 
                  file_content: Union[str, bytes], 
                  source: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parse CSV content and return list of player projections
        
        Args:
            file_content: CSV content as string or bytes
            source: Override source type for column mapping
            
        Returns:
            List of dictionaries with normalized player projection data
        """
        try:
            # Handle different input types
            if isinstance(file_content, bytes):
                df = pd.read_csv(BytesIO(file_content))
            else:
                df = pd.read_csv(StringIO(file_content))
            
            # Clean up column names
            df.columns = df.columns.str.strip()
            
            # Auto-detect source if not specified
            if source is None and self.source == 'auto':
                source = self._detect_source(df.columns.tolist())
            elif source is None:
                source = self.source
            
            self.logger.info(f"Parsing CSV with {len(df)} rows using {source} format")
            
            # Normalize columns based on source
            normalized_data = self._normalize_columns(df, source)
            
            # Validate and clean data
            cleaned_data = self._clean_and_validate(normalized_data)
            
            self.logger.info(f"Successfully parsed {len(cleaned_data)} player projections")
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"Error parsing CSV: {str(e)}")
            raise ValueError(f"Failed to parse CSV: {str(e)}")
    
    def _detect_source(self, columns: List[str]) -> str:
        """Auto-detect CSV source based on column names"""
        column_lower = [col.lower() for col in columns]
        
        # Check for source-specific patterns
        if any('fantasypros' in col for col in column_lower):
            return 'fantasypros'
        elif any('yahoo' in col for col in column_lower):
            return 'yahoo'
        elif any('espn' in col for col in column_lower):
            return 'espn'
        
        # Check for characteristic column patterns
        fantasypros_indicators = ['pass yds', 'rush yds', 'rec yds']
        yahoo_indicators = ['projected points']
        espn_indicators = ['proj']
        
        if any(indicator in ' '.join(column_lower) for indicator in fantasypros_indicators):
            return 'fantasypros'
        elif any(indicator in ' '.join(column_lower) for indicator in yahoo_indicators):
            return 'yahoo'
        elif any(indicator in ' '.join(column_lower) for indicator in espn_indicators):
            return 'espn'
        
        # Default to fantasypros format
        self.logger.warning("Could not detect source, defaulting to fantasypros format")
        return 'fantasypros'
    
    def _normalize_columns(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Normalize column names based on source mapping"""
        if source not in self.COLUMN_MAPPINGS:
            raise ValueError(f"Unsupported source: {source}")
        
        mapping = self.COLUMN_MAPPINGS[source]
        normalized_df = df.copy()
        
        # Create reverse mapping from actual columns to normalized names
        column_map = {}
        for norm_col, possible_names in mapping.items():
            for col in df.columns:
                if col in possible_names or col.lower() in [name.lower() for name in possible_names]:
                    column_map[col] = norm_col
                    break
        
        # Rename columns
        normalized_df = normalized_df.rename(columns=column_map)
        
        return normalized_df
    
    def _clean_and_validate(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Clean and validate the normalized data"""
        cleaned_data = []
        
        for idx, row in df.iterrows():
            try:
                # Extract basic player info
                player_data = {
                    'name': self._clean_name(row.get('name', '')),
                    'position': self._normalize_position(row.get('position', '')),
                    'team': self._clean_team(row.get('team', '')),
                }
                
                # Skip if missing essential data
                if not player_data['name'] or not player_data['position']:
                    self.logger.warning(f"Skipping row {idx}: missing name or position")
                    continue
                
                # Extract projection stats
                projection_data = {}
                stat_fields = [
                    'passing_yards', 'passing_tds', 'interceptions',
                    'rushing_yards', 'rushing_tds',
                    'receptions', 'receiving_yards', 'receiving_tds',
                    'field_goals', 'extra_points',
                    'fantasy_points'
                ]
                
                for field in stat_fields:
                    value = row.get(field)
                    if pd.notna(value):
                        try:
                            projection_data[field] = float(value)
                        except (ValueError, TypeError):
                            self.logger.warning(f"Invalid {field} value for {player_data['name']}: {value}")
                
                # Combine player and projection data
                combined_data = {**player_data, **projection_data}
                cleaned_data.append(combined_data)
                
            except Exception as e:
                self.logger.warning(f"Error processing row {idx}: {str(e)}")
                continue
        
        return cleaned_data
    
    def _clean_name(self, name: str) -> str:
        """Clean player name"""
        if pd.isna(name):
            return ""
        
        # Remove extra whitespace and common suffixes
        name = str(name).strip()
        
        # Remove common suffixes like Jr., Sr., III
        suffixes = [' Jr.', ' Sr.', ' III', ' II', ' IV']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()
        
        return name
    
    def _normalize_position(self, position: str) -> str:
        """Normalize position to standard format"""
        if pd.isna(position):
            return ""
        
        pos = str(position).upper().strip()
        
        # Handle common variations
        position_map = {
            'QB': 'QB',
            'RB': 'RB',
            'WR': 'WR', 
            'TE': 'TE',
            'K': 'K',
            'DEF': 'DST',
            'DST': 'DST',
            'D/ST': 'DST',
            'FLEX': 'FLEX'
        }
        
        return position_map.get(pos, pos)
    
    def _clean_team(self, team: str) -> str:
        """Clean team abbreviation"""
        if pd.isna(team):
            return ""
        
        team = str(team).upper().strip()
        
        # Handle common variations
        team_map = {
            'JAX': 'JAC',
            'JAC': 'JAC',
            'WAS': 'WSH',
            'WSH': 'WSH'
        }
        
        return team_map.get(team, team)

def create_sample_csv() -> str:
    """Create a sample CSV for testing"""
    sample_data = """Player,Pos,Team,Pass Yds,Pass TD,Int,Rush Yds,Rush TD,Rec,Rec Yds,Rec TD,FPTS
Josh Allen,QB,BUF,4306,29,15,524,15,0,0,0,287.5
Lamar Jackson,QB,BAL,3678,24,7,821,5,0,0,0,276.8
Jalen Hurts,QB,PHI,3847,23,15,760,13,0,0,0,274.3
Christian McCaffrey,RB,SF,0,0,0,1459,14,85,741,7,287.0
Austin Ekeler,RB,LAC,0,0,0,915,5,107,722,5,241.7
Saquon Barkley,RB,NYG,0,0,0,1312,10,57,338,2,223.0
Cooper Kupp,WR,LAR,0,0,0,0,0,145,1947,12,294.7
Davante Adams,WR,LV,0,0,0,0,0,100,1516,14,271.6
Tyreek Hill,WR,MIA,0,0,0,35,1,119,1710,7,267.0
Travis Kelce,TE,KC,0,0,0,0,0,110,1338,12,233.8
Mark Andrews,TE,BAL,0,0,0,0,0,73,847,5,142.7
George Kittle,TE,SF,0,0,0,0,0,60,765,4,126.5"""
    
    return sample_data
