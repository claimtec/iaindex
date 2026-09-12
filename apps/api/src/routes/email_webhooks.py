"""
Email webhook handlers for SendGrid and Resend
Tracks email delivery, opens, clicks, bounces, etc.
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any, List
from datetime import datetime
import logging
import hmac
import hashlib
import json

from ..middleware.auth import get_supabase_client
from ..config import settings
from supabase import Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/webhooks", tags=["Email Webhooks"])


def verify_sendgrid_signature(request_body: bytes, signature: str, timestamp: str) -> bool:
    """
    Verify SendGrid webhook signature

    Args:
        request_body: Raw request body
        signature: Signature from headers
        timestamp: Timestamp from headers

    Returns:
        True if signature is valid
    """
    try:
        # SendGrid uses ECDSA verification, but for basic security we can use HMAC
        # In production, use SendGrid's official verification
        public_key = settings.sendgrid_webhook_verification_key
        if not public_key:
            logger.warning("SendGrid webhook verification key not configured")
            return True  # Allow in development

        # Create verification payload
        payload = timestamp.encode() + request_body

        # Compute expected signature
        expected_signature = hmac.new(
            public_key.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    except Exception as e:
        logger.error(f"Failed to verify SendGrid signature: {e}")
        return False


@router.post("/sendgrid")
async def sendgrid_webhook(
    request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Handle SendGrid event webhooks

    Processes delivery, open, click, bounce, and other email events
    """
    try:
        # Get raw body and headers
        body = await request.body()
        signature = request.headers.get("X-Twilio-Email-Event-Webhook-Signature", "")
        timestamp = request.headers.get("X-Twilio-Email-Event-Webhook-Timestamp", "")

        # Verify signature (optional in development)
        if settings.debug:
            logger.warning("Skipping signature verification in debug mode")
        else:
            if not verify_sendgrid_signature(body, signature, timestamp):
                raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse events
        events = json.loads(body)

        if not isinstance(events, list):
            events = [events]

        processed_count = 0

        for event in events:
            try:
                await process_sendgrid_event(event, supabase)
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to process SendGrid event: {e}")

        logger.info(f"Processed {processed_count} SendGrid events")

        return {
            "success": True,
            "processed": processed_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SendGrid webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_sendgrid_event(event: Dict[str, Any], supabase: Client):
    """
    Process a single SendGrid event

    Args:
        event: SendGrid event data
        supabase: Supabase client
    """
    event_type = event.get("event")
    message_id = event.get("sg_message_id", "").split(".")[0]  # Remove filter ID
    email = event.get("email")
    timestamp = event.get("timestamp")

    logger.info(f"Processing SendGrid event: {event_type} for {email}")

    # Find email analytics record
    analytics = supabase.table("email_analytics").select("*").eq(
        "provider_message_id", message_id
    ).execute()

    update_data = {}

    if event_type == "delivered":
        update_data["delivered_at"] = datetime.fromtimestamp(timestamp).isoformat()

    elif event_type == "open":
        update_data["opened_at"] = datetime.fromtimestamp(timestamp).isoformat()
        # Update drip campaign email status
        await update_drip_email_status(message_id, "opened", supabase)

    elif event_type == "click":
        update_data["clicked_at"] = datetime.fromtimestamp(timestamp).isoformat()
        update_data["click_url"] = event.get("url")
        # Update drip campaign email status
        await update_drip_email_status(message_id, "clicked", supabase)

    elif event_type == "bounce" or event_type == "dropped":
        update_data["bounced_at"] = datetime.fromtimestamp(timestamp).isoformat()
        update_data["bounce_reason"] = event.get("reason")
        # Update drip campaign email status
        await update_drip_email_status(message_id, "bounced", supabase)

    elif event_type == "spamreport":
        update_data["complained_at"] = datetime.fromtimestamp(timestamp).isoformat()

    elif event_type == "unsubscribe":
        update_data["unsubscribed_at"] = datetime.fromtimestamp(timestamp).isoformat()
        # Auto-unsubscribe user
        await auto_unsubscribe_user(email, supabase)

    if update_data:
        if analytics.data:
            # Update existing record
            supabase.table("email_analytics").update(update_data).eq(
                "id", analytics.data[0]["id"]
            ).execute()
        else:
            # Create new record
            update_data.update({
                "provider_message_id": message_id,
                "to_email": email,
                "provider": "sendgrid"
            })
            supabase.table("email_analytics").insert(update_data).execute()


@router.post("/resend")
async def resend_webhook(
    request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Handle Resend event webhooks

    Processes delivery, open, click, bounce, and other email events
    """
    try:
        # Get signature for verification
        signature = request.headers.get("svix-signature", "")
        webhook_id = request.headers.get("svix-id", "")
        timestamp = request.headers.get("svix-timestamp", "")

        body = await request.body()
        event = json.loads(body)

        # Verify webhook (Resend uses Svix for webhook signing)
        # In production, use svix library for proper verification
        if not settings.debug:
            # TODO: Implement Svix signature verification
            logger.warning("Resend webhook signature verification not implemented")

        event_type = event.get("type")
        data = event.get("data", {})

        logger.info(f"Processing Resend event: {event_type}")

        # Process based on event type
        if event_type == "email.sent":
            await process_resend_sent(data, supabase)
        elif event_type == "email.delivered":
            await process_resend_delivered(data, supabase)
        elif event_type == "email.opened":
            await process_resend_opened(data, supabase)
        elif event_type == "email.clicked":
            await process_resend_clicked(data, supabase)
        elif event_type == "email.bounced":
            await process_resend_bounced(data, supabase)
        elif event_type == "email.complained":
            await process_resend_complained(data, supabase)

        return {"success": True}

    except Exception as e:
        logger.error(f"Resend webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_resend_sent(data: Dict[str, Any], supabase: Client):
    """Process Resend sent event"""
    message_id = data.get("email_id")
    email = data.get("to")[0] if data.get("to") else None

    supabase.table("email_analytics").insert({
        "provider_message_id": message_id,
        "to_email": email,
        "subject": data.get("subject"),
        "sent_at": datetime.now().isoformat(),
        "provider": "resend"
    }).execute()


async def process_resend_delivered(data: Dict[str, Any], supabase: Client):
    """Process Resend delivered event"""
    message_id = data.get("email_id")

    supabase.table("email_analytics").update({
        "delivered_at": datetime.now().isoformat()
    }).eq("provider_message_id", message_id).execute()


async def process_resend_opened(data: Dict[str, Any], supabase: Client):
    """Process Resend opened event"""
    message_id = data.get("email_id")

    supabase.table("email_analytics").update({
        "opened_at": datetime.now().isoformat()
    }).eq("provider_message_id", message_id).execute()

    await update_drip_email_status(message_id, "opened", supabase)


async def process_resend_clicked(data: Dict[str, Any], supabase: Client):
    """Process Resend clicked event"""
    message_id = data.get("email_id")

    supabase.table("email_analytics").update({
        "clicked_at": datetime.now().isoformat(),
        "click_url": data.get("link", {}).get("url")
    }).eq("provider_message_id", message_id).execute()

    await update_drip_email_status(message_id, "clicked", supabase)


async def process_resend_bounced(data: Dict[str, Any], supabase: Client):
    """Process Resend bounced event"""
    message_id = data.get("email_id")

    supabase.table("email_analytics").update({
        "bounced_at": datetime.now().isoformat(),
        "bounce_reason": data.get("reason")
    }).eq("provider_message_id", message_id).execute()

    await update_drip_email_status(message_id, "bounced", supabase)


async def process_resend_complained(data: Dict[str, Any], supabase: Client):
    """Process Resend spam complaint event"""
    message_id = data.get("email_id")
    email = data.get("to")[0] if data.get("to") else None

    supabase.table("email_analytics").update({
        "complained_at": datetime.now().isoformat()
    }).eq("provider_message_id", message_id).execute()

    # Auto-unsubscribe user
    if email:
        await auto_unsubscribe_user(email, supabase)


async def update_drip_email_status(
    provider_message_id: str,
    status: str,
    supabase: Client
):
    """
    Update drip campaign email status based on provider message ID

    Args:
        provider_message_id: Message ID from email provider
        status: New status (opened, clicked, bounced)
        supabase: Supabase client
    """
    try:
        supabase.table("drip_campaign_emails").update({
            "status": status,
            f"{status}_at": datetime.now().isoformat()
        }).eq("provider_message_id", provider_message_id).execute()

    except Exception as e:
        logger.error(f"Failed to update drip email status: {e}")


async def auto_unsubscribe_user(email: str, supabase: Client):
    """
    Automatically unsubscribe user who marked email as spam

    Args:
        email: Email address
        supabase: Supabase client
    """
    try:
        # Update email preferences
        supabase.table("email_preferences").update({
            "unsubscribed_all": True,
            "unsubscribed_at": datetime.now().isoformat(),
            "marketing_emails": False,
            "product_updates": False,
            "weekly_reports": False,
            "visibility_alerts": False
        }).eq("email", email).execute()

        # Unsubscribe from drip campaigns
        supabase.table("drip_campaigns").update({
            "status": "unsubscribed"
        }).eq("email", email).eq("status", "active").execute()

        logger.info(f"Auto-unsubscribed {email} due to spam complaint")

    except Exception as e:
        logger.error(f"Failed to auto-unsubscribe user: {e}")


@router.get("/analytics")
async def get_email_analytics(
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get email analytics summary

    Returns overall email performance metrics
    """
    try:
        # Get overall stats
        total_sent = supabase.table("email_analytics").select(
            "id", count="exact"
        ).not_.is_("sent_at", "null").execute()

        total_delivered = supabase.table("email_analytics").select(
            "id", count="exact"
        ).not_.is_("delivered_at", "null").execute()

        total_opened = supabase.table("email_analytics").select(
            "id", count="exact"
        ).not_.is_("opened_at", "null").execute()

        total_clicked = supabase.table("email_analytics").select(
            "id", count="exact"
        ).not_.is_("clicked_at", "null").execute()

        total_bounced = supabase.table("email_analytics").select(
            "id", count="exact"
        ).not_.is_("bounced_at", "null").execute()

        total_complained = supabase.table("email_analytics").select(
            "id", count="exact"
        ).not_.is_("complained_at", "null").execute()

        sent_count = total_sent.count or 0
        delivered_count = total_delivered.count or 0
        opened_count = total_opened.count or 0
        clicked_count = total_clicked.count or 0
        bounced_count = total_bounced.count or 0
        complained_count = total_complained.count or 0

        # Calculate rates
        delivery_rate = (delivered_count / sent_count * 100) if sent_count > 0 else 0
        open_rate = (opened_count / delivered_count * 100) if delivered_count > 0 else 0
        click_rate = (clicked_count / delivered_count * 100) if delivered_count > 0 else 0
        bounce_rate = (bounced_count / sent_count * 100) if sent_count > 0 else 0
        complaint_rate = (complained_count / sent_count * 100) if sent_count > 0 else 0

        # Get performance by email type
        performance = supabase.table("email_performance").select("*").execute()

        return {
            "success": True,
            "overall": {
                "total_sent": sent_count,
                "total_delivered": delivered_count,
                "total_opened": opened_count,
                "total_clicked": clicked_count,
                "total_bounced": bounced_count,
                "total_complained": complained_count,
                "delivery_rate": round(delivery_rate, 2),
                "open_rate": round(open_rate, 2),
                "click_rate": round(click_rate, 2),
                "bounce_rate": round(bounce_rate, 2),
                "complaint_rate": round(complaint_rate, 2)
            },
            "by_type": performance.data
        }

    except Exception as e:
        logger.error(f"Failed to get email analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
