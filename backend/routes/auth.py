"""
Authentication routes
"""
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any
from auth.yahoo_auth import yahoo_auth
from authlib.integrations.base_client import OAuthError

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/yahoo")
async def initiate_yahoo_auth():
    """
    Initiate Yahoo OAuth flow
    """
    try:
        auth_url, state = yahoo_auth.get_authorization_url()
        return {
            "auth_url": auth_url,
            "state": state,
            "message": "Redirect user to auth_url to complete authentication"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate auth: {str(e)}")

@router.get("/callback")
async def yahoo_callback(
    request: Request,
    code: str = Query(None, description="Authorization code from Yahoo"),
    state: str = Query(None, description="State parameter for security"),
    error: str = Query(None, description="Error from Yahoo"),
    error_description: str = Query(None, description="Error description from Yahoo")
):
    """
    Handle Yahoo OAuth callback
    """
    # Log all query parameters for debugging
    all_params = dict(request.query_params)
    print(f"DEBUG: Callback received parameters: {all_params}")
    
    # Check for errors first
    if error:
        return {
            "error": error,
            "error_description": error_description,
            "message": "OAuth authorization was denied or failed",
            "all_params": all_params
        }
    
    # Check if we have the required parameters
    if not code or not state:
        return {
            "error": "missing_parameters",
            "message": "Missing required code or state parameter",
            "received_params": all_params,
            "expected": ["code", "state"]
        }
    
    try:
        token_data = await yahoo_auth.exchange_code_for_token(code, state)
        
        return {
            "message": "Authentication successful",
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in"),
            "state": state
        }
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@router.post("/refresh")
async def refresh_access_token(refresh_token: str):
    """
    Refresh an expired access token
    """
    try:
        token_data = await yahoo_auth.refresh_token(refresh_token)
        return {
            "message": "Token refreshed successfully",
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in")
        }
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")

@router.get("/status/{state}")
async def get_auth_status(state: str):
    """
    Check authentication status for a given state
    """
    token = yahoo_auth.get_token(state)
    if not token:
        return {"authenticated": False, "message": "No token found for this state"}
    
    is_valid = yahoo_auth.is_token_valid(token)
    return {
        "authenticated": is_valid,
        "token_present": True,
        "expires_in": token.get("expires_in")
    }
