"""
Yahoo Fantasy Sports OAuth 2.0 Authentication
"""
import httpx
import secrets
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from authlib.integrations.base_client import OAuthError
from config import settings

class YahooAuth:
    """Yahoo OAuth 2.0 client"""
    
    def __init__(self):
        self.client_id = settings.YAHOO_CLIENT_ID
        self.client_secret = settings.YAHOO_CLIENT_SECRET
        self.redirect_uri = settings.YAHOO_REDIRECT_URI
        
        # Yahoo OAuth URLs
        self.auth_url = "https://api.login.yahoo.com/oauth2/request_auth"
        self.token_url = "https://api.login.yahoo.com/oauth2/get_token"
        self.api_base = "https://fantasysports.yahooapis.com/fantasy/v2"
        
        # In-memory storage for states and tokens (use Redis/DB in production)
        self._states: Dict[str, str] = {}
        self._tokens: Dict[str, Dict[str, Any]] = {}
    
    def get_authorization_url(self) -> tuple[str, str]:
        """
        Generate Yahoo authorization URL
        Returns: (auth_url, state)
        """
        state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "upload",  # Yahoo Fantasy Sports scope
            "state": state
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        self._states[state] = "pending"
        
        return auth_url, state
    
    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        """
        if state not in self._states:
            raise OAuthError("Invalid state parameter")
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise OAuthError(f"Token exchange failed: {response.text}")
            
            token_data = response.json()
            
            # Store token
            self._tokens[state] = token_data
            self._states[state] = "authorized"
            
            return token_data
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise OAuthError(f"Token refresh failed: {response.text}")
            
            return response.json()
    
    async def make_api_request(self, endpoint: str, access_token: str) -> Dict[str, Any]:
        """
        Make authenticated request to Yahoo Fantasy API
        """
        url = f"{self.api_base}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 401:
                raise OAuthError("Access token expired")
            elif response.status_code != 200:
                raise OAuthError(f"API request failed: {response.text}")
            
            return response.json()
    
    async def get_user_leagues(self, access_token: str, game_key: str = "nfl") -> Dict[str, Any]:
        """
        Get user's fantasy leagues
        """
        # Get current season game key (e.g., 449 for 2024 NFL)
        endpoint = f"users;use_login=1/games;game_keys={game_key}/leagues"
        return await self.make_api_request(endpoint, access_token)
    
    async def get_league_details(self, access_token: str, league_key: str) -> Dict[str, Any]:
        """
        Get detailed league information
        """
        endpoint = f"league/{league_key}"
        return await self.make_api_request(endpoint, access_token)
    
    async def get_league_players(self, access_token: str, league_key: str, start: int = 0, count: int = 25) -> Dict[str, Any]:
        """
        Get players in a league
        """
        endpoint = f"league/{league_key}/players;start={start};count={count}"
        return await self.make_api_request(endpoint, access_token)
    
    async def get_player_stats(self, access_token: str, player_key: str, stat_type: str = "season") -> Dict[str, Any]:
        """
        Get player statistics
        stat_type: 'season', 'lastweek', 'lastmonth'
        """
        endpoint = f"player/{player_key}/stats;type={stat_type}"
        return await self.make_api_request(endpoint, access_token)
    
    async def get_all_players(self, access_token: str, game_key: str = "nfl", start: int = 0, count: int = 25) -> Dict[str, Any]:
        """
        Get all available players for a game (NFL)
        """
        endpoint = f"game/{game_key}/players;start={start};count={count}"
        return await self.make_api_request(endpoint, access_token)
    
    async def get_player_ownership(self, access_token: str, league_key: str, player_keys: list) -> Dict[str, Any]:
        """
        Get player ownership information in a league
        """
        player_key_str = ",".join(player_keys)
        endpoint = f"league/{league_key}/players;player_keys={player_key_str}/ownership"
        return await self.make_api_request(endpoint, access_token)
    
    async def get_game_info(self, access_token: str, game_key: str = "nfl") -> Dict[str, Any]:
        """
        Get game information (current NFL season info)
        """
        endpoint = f"game/{game_key}"
        return await self.make_api_request(endpoint, access_token)
    
    def get_token(self, state: str) -> Optional[Dict[str, Any]]:
        """Get stored token by state"""
        return self._tokens.get(state)
    
    def is_token_valid(self, token_data: Dict[str, Any]) -> bool:
        """Check if token is still valid (simple check - could be enhanced)"""
        return "access_token" in token_data and "expires_in" in token_data

# Global instance
yahoo_auth = YahooAuth()
