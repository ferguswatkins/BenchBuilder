"""
League-related API routes
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional, Dict, Any
from auth.yahoo_auth import yahoo_auth
from authlib.integrations.base_client import OAuthError

router = APIRouter(prefix="/api", tags=["leagues"])

@router.get("/leagues")
async def get_user_leagues(authorization: str = Header(..., description="Bearer {access_token}")):
    """
    Get user's fantasy leagues from Yahoo
    """
    try:
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        access_token = authorization.split(" ")[1]
        
        # Get current NFL season leagues
        leagues_data = await yahoo_auth.get_user_leagues(access_token, "nfl")
        
        return {
            "message": "Leagues retrieved successfully",
            "data": leagues_data
        }
    except OAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve leagues: {str(e)}")

@router.get("/leagues/{league_key}")
async def get_league_details(
    league_key: str,
    authorization: str = Header(..., description="Bearer {access_token}")
):
    """
    Get detailed information about a specific league
    """
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        access_token = authorization.split(" ")[1]
        
        league_data = await yahoo_auth.get_league_details(access_token, league_key)
        
        return {
            "message": "League details retrieved successfully",
            "data": league_data
        }
    except OAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve league details: {str(e)}")

@router.get("/leagues/{league_key}/players")
async def get_league_players(
    league_key: str,
    start: int = 0,
    count: int = 25,
    authorization: str = Header(..., description="Bearer {access_token}")
):
    """
    Get players available in a specific league
    """
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        access_token = authorization.split(" ")[1]
        
        players_data = await yahoo_auth.get_league_players(access_token, league_key, start, count)
        
        return {
            "message": "League players retrieved successfully",
            "data": players_data,
            "pagination": {
                "start": start,
                "count": count
            }
        }
    except OAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve league players: {str(e)}")

@router.get("/test-auth")
async def test_authentication(authorization: str = Header(..., description="Bearer {access_token}")):
    """
    Test endpoint to verify authentication is working
    """
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        access_token = authorization.split(" ")[1]
        
        # Make a simple API call to verify the token works
        result = await yahoo_auth.make_api_request("users;use_login=1", access_token)
        
        return {
            "message": "Authentication successful",
            "user_data": result
        }
    except OAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication test failed: {str(e)}")
