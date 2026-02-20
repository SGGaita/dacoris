from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta, datetime
import httpx
import os

from database import get_db
from models import User, AccountType, UserStatus
from auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from services.orcid_sync import OrcidSyncService

router = APIRouter(prefix="/api/auth/orcid", tags=["orcid"])

ORCID_CLIENT_ID = os.getenv("ORCID_CLIENT_ID")
ORCID_CLIENT_SECRET = os.getenv("ORCID_CLIENT_SECRET")
ORCID_REDIRECT_URI = os.getenv("ORCID_REDIRECT_URI", "http://localhost:8000/api/auth/orcid/callback")
ORCID_AUTHORIZE_URL = "https://orcid.org/oauth/authorize"
ORCID_TOKEN_URL = "https://orcid.org/oauth/token"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

@router.get("/login")
async def orcid_login():
    """Redirect user to ORCID for authentication"""
    # Request expanded scopes for profile sync and activities update
    scopes = "/authenticate /read-limited /activities/update"
    
    params = {
        "client_id": ORCID_CLIENT_ID,
        "response_type": "code",
        "scope": scopes,
        "redirect_uri": ORCID_REDIRECT_URI
    }
    
    auth_url = f"{ORCID_AUTHORIZE_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def orcid_callback(
    code: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Handle ORCID OAuth callback"""
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            ORCID_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": ORCID_CLIENT_ID,
                "client_secret": ORCID_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": ORCID_REDIRECT_URI
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get ORCID access token"
            )
        
        token_data = token_response.json()
        orcid_id = token_data.get("orcid")
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 631138518)  # ORCID tokens are long-lived
        name = token_data.get("name")
        
        # Check if user exists
        result = await db.execute(select(User).where(User.orcid_id == orcid_id))
        user = result.scalar_one_or_none()
        
        is_new_user = False
        
        if not user:
            is_new_user = True
            # Create new user with ORCID account type
            user = User(
                email=f"{orcid_id}@orcid.org",  # Temporary email, will be updated from profile
                name=name,
                orcid_id=orcid_id,
                orcid_access_token=access_token,
                orcid_refresh_token=refresh_token,
                orcid_token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
                account_type=AccountType.ORCID,
                status=UserStatus.PENDING  # Will be activated after institution selection
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            # Update existing user's tokens
            user.orcid_access_token = access_token
            user.orcid_refresh_token = refresh_token
            user.orcid_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            user.last_login = datetime.utcnow()
            if name and not user.name:
                user.name = name
            await db.commit()
        
        # Sync ORCID profile data
        try:
            await OrcidSyncService.sync_user_profile(user, db)
        except Exception as e:
            print(f"Warning: Failed to sync ORCID profile: {e}")
        
        # If new user, check for institution match
        if is_new_user:
            # Try to determine institution from email or affiliations
            institution = await OrcidSyncService.verify_email_domain(user.email, db)
            
            if institution:
                user.primary_institution_id = institution.id
                user.status = UserStatus.ACTIVE  # Auto-activate if domain matches
                await db.commit()
        
        # Generate JWT token with user_id
        jwt_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = create_access_token(
            data={
                "user_id": user.id,
                "orcid_id": user.orcid_id,
                "account_type": user.account_type.value,
                "institution_id": user.primary_institution_id
            }, 
            expires_delta=jwt_token_expires
        )
        
        # Redirect based on user status
        if is_new_user and user.status == UserStatus.PENDING:
            redirect_url = f"{FRONTEND_URL}/onboarding?token={jwt_token}"
        else:
            redirect_url = f"{FRONTEND_URL}/dashboard?token={jwt_token}"
        
        return RedirectResponse(url=redirect_url)
