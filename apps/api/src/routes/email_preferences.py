"""
Email preferences and subscription management routes
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import logging

from ..middleware.auth import get_current_user, get_supabase_client
from supabase import Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/email-preferences", tags=["Email Preferences"])


class EmailPreferencesUpdate(BaseModel):
    """Email preferences update request"""
    marketing_emails: Optional[bool] = None
    product_updates: Optional[bool] = None
    weekly_reports: Optional[bool] = None
    visibility_alerts: Optional[bool] = None


class UnsubscribeRequest(BaseModel):
    """Unsubscribe request"""
    token: Optional[str] = None
    email: Optional[EmailStr] = None
    unsubscribe_all: bool = True


@router.get("/")
async def get_email_preferences(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get current user's email preferences

    Returns email notification settings for the authenticated user
    """
    try:
        user_id = current_user["id"]

        # Get preferences
        result = supabase.table("email_preferences").select("*").eq(
            "user_id", user_id
        ).execute()

        if not result.data:
            # Create default preferences
            default_prefs = supabase.table("email_preferences").insert({
                "user_id": user_id,
                "email": current_user.get("email")
            }).execute()

            return {
                "success": True,
                "preferences": default_prefs.data[0]
            }

        return {
            "success": True,
            "preferences": result.data[0]
        }

    except Exception as e:
        logger.error(f"Failed to get email preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/")
async def update_email_preferences(
    preferences: EmailPreferencesUpdate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Update email preferences

    Allows users to control which types of emails they receive
    """
    try:
        user_id = current_user["id"]

        # Prepare update data (only include non-None values)
        update_data = {
            k: v for k, v in preferences.dict().items()
            if v is not None
        }

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No preferences provided to update"
            )

        # Update preferences
        result = supabase.table("email_preferences").update(
            update_data
        ).eq("user_id", user_id).execute()

        if not result.data:
            # Create if doesn't exist
            update_data["user_id"] = user_id
            update_data["email"] = current_user.get("email")
            result = supabase.table("email_preferences").insert(
                update_data
            ).execute()

        logger.info(f"Updated email preferences for user {user_id}")

        return {
            "success": True,
            "preferences": result.data[0],
            "message": "Email preferences updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update email preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unsubscribe")
async def unsubscribe(
    request: UnsubscribeRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Unsubscribe from emails

    Supports both token-based (one-click) and email-based unsubscribe
    """
    try:
        # Find preferences by token or email
        query = supabase.table("email_preferences").select("*")

        if request.token:
            query = query.eq("unsubscribe_token", request.token)
        elif request.email:
            query = query.eq("email", request.email)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either token or email must be provided"
            )

        result = query.execute()

        if not result.data:
            # Create new preference entry if doesn't exist
            if request.email:
                new_prefs = supabase.table("email_preferences").insert({
                    "email": request.email,
                    "unsubscribed_all": request.unsubscribe_all,
                    "unsubscribed_at": datetime.now().isoformat(),
                    "marketing_emails": False,
                    "product_updates": False,
                    "weekly_reports": False,
                    "visibility_alerts": False
                }).execute()

                logger.info(f"Created unsubscribe preferences for {request.email}")

                return {
                    "success": True,
                    "message": "Successfully unsubscribed from all emails",
                    "email": request.email
                }
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Email preferences not found"
                )

        # Update existing preferences
        prefs_id = result.data[0]["id"]
        email = result.data[0]["email"]

        update_data = {
            "unsubscribed_at": datetime.now().isoformat()
        }

        if request.unsubscribe_all:
            update_data.update({
                "unsubscribed_all": True,
                "marketing_emails": False,
                "product_updates": False,
                "weekly_reports": False,
                "visibility_alerts": False
            })
        else:
            # Partial unsubscribe (marketing only)
            update_data["marketing_emails"] = False

        supabase.table("email_preferences").update(update_data).eq(
            "id", prefs_id
        ).execute()

        # Also unsubscribe from active drip campaigns
        if request.unsubscribe_all:
            supabase.table("drip_campaigns").update({
                "status": "unsubscribed"
            }).eq("email", email).eq("status", "active").execute()

        logger.info(f"Unsubscribed {email} from emails")

        return {
            "success": True,
            "message": "Successfully unsubscribed" + (
                " from all emails" if request.unsubscribe_all
                else " from marketing emails"
            ),
            "email": email
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unsubscribe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resubscribe")
async def resubscribe(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Resubscribe to all emails

    Allows users to opt back in to email communications
    """
    try:
        user_id = current_user["id"]

        # Update preferences
        result = supabase.table("email_preferences").update({
            "unsubscribed_all": False,
            "marketing_emails": True,
            "product_updates": True,
            "weekly_reports": True,
            "visibility_alerts": True,
            "unsubscribed_at": None
        }).eq("user_id", user_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Email preferences not found"
            )

        logger.info(f"Resubscribed user {user_id} to emails")

        return {
            "success": True,
            "message": "Successfully resubscribed to emails",
            "preferences": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resubscribe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify-token")
async def verify_unsubscribe_token(
    token: str = Query(..., description="Unsubscribe token"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Verify an unsubscribe token

    Used to check if a token is valid before showing unsubscribe page
    """
    try:
        result = supabase.table("email_preferences").select(
            "email, unsubscribed_all"
        ).eq("unsubscribe_token", token).execute()

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Invalid unsubscribe token"
            )

        prefs = result.data[0]

        return {
            "success": True,
            "valid": True,
            "email": prefs["email"],
            "already_unsubscribed": prefs.get("unsubscribed_all", False)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drip-campaigns")
async def get_drip_campaigns(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get user's drip campaigns

    Returns all drip campaigns for the authenticated user
    """
    try:
        user_id = current_user["id"]

        # Get campaigns
        result = supabase.table("drip_campaigns").select(
            "*, drip_campaign_emails(*)"
        ).eq("user_id", user_id).execute()

        return {
            "success": True,
            "campaigns": result.data
        }

    except Exception as e:
        logger.error(f"Failed to get drip campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drip-campaigns/{campaign_id}/pause")
async def pause_drip_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Pause a drip campaign

    Stops future emails from being sent in the campaign
    """
    try:
        user_id = current_user["id"]

        # Verify ownership
        campaign = supabase.table("drip_campaigns").select("*").eq(
            "id", campaign_id
        ).eq("user_id", user_id).execute()

        if not campaign.data:
            raise HTTPException(
                status_code=404,
                detail="Campaign not found"
            )

        # Pause campaign
        result = supabase.table("drip_campaigns").update({
            "status": "paused",
            "paused_at": datetime.now().isoformat()
        }).eq("id", campaign_id).execute()

        logger.info(f"Paused drip campaign {campaign_id}")

        return {
            "success": True,
            "message": "Campaign paused successfully",
            "campaign": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pause campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drip-campaigns/{campaign_id}/resume")
async def resume_drip_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Resume a paused drip campaign

    Resumes sending emails in the campaign sequence
    """
    try:
        user_id = current_user["id"]

        # Verify ownership
        campaign = supabase.table("drip_campaigns").select("*").eq(
            "id", campaign_id
        ).eq("user_id", user_id).execute()

        if not campaign.data:
            raise HTTPException(
                status_code=404,
                detail="Campaign not found"
            )

        # Resume campaign
        result = supabase.table("drip_campaigns").update({
            "status": "active",
            "paused_at": None
        }).eq("id", campaign_id).execute()

        logger.info(f"Resumed drip campaign {campaign_id}")

        return {
            "success": True,
            "message": "Campaign resumed successfully",
            "campaign": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))
