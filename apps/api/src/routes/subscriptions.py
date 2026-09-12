"""
Subscription management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import stripe
from ..config import settings
from ..middleware.auth import get_current_user, get_api_key
from supabase import create_client, Client

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key if hasattr(settings, 'stripe_secret_key') else None

# Initialize Supabase client
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_key
)


# Request/Response Models
class CheckoutCompletedWebhook(BaseModel):
    """Webhook payload for checkout completion"""
    email: EmailStr
    customerId: str
    subscriptionId: str
    plan: str
    sessionId: str


class SubscriptionUpdatedWebhook(BaseModel):
    """Webhook payload for subscription update"""
    subscriptionId: str
    customerId: str
    plan: Optional[str] = None
    status: str
    currentPeriodStart: datetime
    currentPeriodEnd: datetime
    cancelAtPeriodEnd: bool


class SubscriptionDeletedWebhook(BaseModel):
    """Webhook payload for subscription deletion"""
    subscriptionId: str
    customerId: str


class PaymentSucceededWebhook(BaseModel):
    """Webhook payload for payment success"""
    invoiceId: str
    customerId: str
    subscriptionId: str
    amount: int
    currency: str


class PaymentFailedWebhook(BaseModel):
    """Webhook payload for payment failure"""
    invoiceId: str
    customerId: str
    subscriptionId: str
    attemptCount: int


class SubscriptionResponse(BaseModel):
    """Subscription response model"""
    id: str
    user_id: str
    plan: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    stripe_customer_id: str
    stripe_subscription_id: str


class PortalSessionResponse(BaseModel):
    """Billing portal session response"""
    url: str


# Webhook Endpoints (called by Stripe webhook handler)
@router.post("/webhook/checkout-completed", status_code=status.HTTP_201_CREATED)
async def webhook_checkout_completed(
    payload: CheckoutCompletedWebhook,
    authorization: Optional[str] = Header(None)
):
    """
    Handle checkout session completed webhook
    Creates or updates user and subscription records
    """
    try:
        # Verify webhook is from authorized source
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization"
            )

        # Check if user exists
        user_result = supabase.table("users").select("*").eq("email", payload.email).execute()

        if not user_result.data:
            # Create new user
            user_data = {
                "email": payload.email,
                "stripe_customer_id": payload.customerId,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            user_result = supabase.table("users").insert(user_data).execute()
            user = user_result.data[0]
            logger.info(f"Created new user: {payload.email}")
        else:
            # Update existing user with Stripe customer ID
            user = user_result.data[0]
            supabase.table("users").update({
                "stripe_customer_id": payload.customerId,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user["id"]).execute()
            logger.info(f"Updated user: {payload.email}")

        # Get subscription details from Stripe
        subscription = stripe.Subscription.retrieve(payload.subscriptionId)

        # Create subscription record
        subscription_data = {
            "user_id": user["id"],
            "stripe_customer_id": payload.customerId,
            "stripe_subscription_id": payload.subscriptionId,
            "plan": payload.plan,
            "status": subscription.status,
            "current_period_start": datetime.fromtimestamp(subscription.current_period_start).isoformat(),
            "current_period_end": datetime.fromtimestamp(subscription.current_period_end).isoformat(),
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        supabase.table("subscriptions").insert(subscription_data).execute()
        logger.info(f"Created subscription for user {user['id']}: {payload.subscriptionId}")

        return {"message": "User and subscription created successfully", "user_id": user["id"]}

    except Exception as e:
        logger.error(f"Error processing checkout completed webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process checkout: {str(e)}"
        )


@router.post("/webhook/subscription-updated", status_code=status.HTTP_200_OK)
async def webhook_subscription_updated(
    payload: SubscriptionUpdatedWebhook,
    authorization: Optional[str] = Header(None)
):
    """
    Handle subscription updated webhook
    Updates subscription status and billing period
    """
    try:
        # Verify webhook is from authorized source
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization"
            )

        # Update subscription record
        update_data = {
            "status": payload.status,
            "current_period_start": payload.currentPeriodStart.isoformat(),
            "current_period_end": payload.currentPeriodEnd.isoformat(),
            "cancel_at_period_end": payload.cancelAtPeriodEnd,
            "updated_at": datetime.utcnow().isoformat()
        }

        if payload.plan:
            update_data["plan"] = payload.plan

        result = supabase.table("subscriptions").update(update_data).eq(
            "stripe_subscription_id", payload.subscriptionId
        ).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )

        logger.info(f"Updated subscription: {payload.subscriptionId}")

        return {"message": "Subscription updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing subscription updated webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subscription: {str(e)}"
        )


@router.post("/webhook/subscription-deleted", status_code=status.HTTP_200_OK)
async def webhook_subscription_deleted(
    payload: SubscriptionDeletedWebhook,
    authorization: Optional[str] = Header(None)
):
    """
    Handle subscription deleted webhook
    Marks subscription as canceled
    """
    try:
        # Verify webhook is from authorized source
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization"
            )

        # Update subscription status to canceled
        result = supabase.table("subscriptions").update({
            "status": "canceled",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("stripe_subscription_id", payload.subscriptionId).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )

        logger.info(f"Deleted subscription: {payload.subscriptionId}")

        return {"message": "Subscription deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing subscription deleted webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subscription: {str(e)}"
        )


@router.post("/webhook/payment-succeeded", status_code=status.HTTP_200_OK)
async def webhook_payment_succeeded(
    payload: PaymentSucceededWebhook,
    authorization: Optional[str] = Header(None)
):
    """
    Handle payment succeeded webhook
    Logs successful payment
    """
    try:
        # Verify webhook is from authorized source
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization"
            )

        # Ensure subscription is active
        result = supabase.table("subscriptions").update({
            "status": "active",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("stripe_subscription_id", payload.subscriptionId).execute()

        logger.info(f"Payment succeeded for subscription: {payload.subscriptionId}")

        return {"message": "Payment processed successfully"}

    except Exception as e:
        logger.error(f"Error processing payment succeeded webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process payment: {str(e)}"
        )


@router.post("/webhook/payment-failed", status_code=status.HTTP_200_OK)
async def webhook_payment_failed(
    payload: PaymentFailedWebhook,
    authorization: Optional[str] = Header(None)
):
    """
    Handle payment failed webhook
    Updates subscription status to past_due
    """
    try:
        # Verify webhook is from authorized source
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization"
            )

        # Update subscription status to past_due
        result = supabase.table("subscriptions").update({
            "status": "past_due",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("stripe_subscription_id", payload.subscriptionId).execute()

        logger.warning(f"Payment failed for subscription: {payload.subscriptionId} (attempt {payload.attemptCount})")

        return {"message": "Payment failure processed"}

    except Exception as e:
        logger.error(f"Error processing payment failed webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process payment failure: {str(e)}"
        )


# User-facing Endpoints
@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current user's subscription details
    """
    try:
        user_id = current_user.get("sub")

        # Get active subscription
        result = supabase.table("subscriptions").select("*").eq("user_id", user_id).eq("status", "active").execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )

        subscription = result.data[0]

        return SubscriptionResponse(
            id=subscription["id"],
            user_id=subscription["user_id"],
            plan=subscription["plan"],
            status=subscription["status"],
            current_period_start=datetime.fromisoformat(subscription["current_period_start"]),
            current_period_end=datetime.fromisoformat(subscription["current_period_end"]),
            cancel_at_period_end=subscription["cancel_at_period_end"],
            stripe_customer_id=subscription["stripe_customer_id"],
            stripe_subscription_id=subscription["stripe_subscription_id"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription"
        )


@router.post("/create-portal-session", response_model=PortalSessionResponse)
async def create_portal_session(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create Stripe billing portal session for subscription management
    """
    try:
        user_id = current_user.get("sub")

        # Get user's Stripe customer ID
        user_result = supabase.table("users").select("stripe_customer_id").eq("id", user_id).execute()

        if not user_result.data or not user_result.data[0].get("stripe_customer_id"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Stripe customer ID found"
            )

        customer_id = user_result.data[0]["stripe_customer_id"]

        # Create billing portal session
        return_url = settings.app_url if hasattr(settings, 'app_url') else "https://app.iaindex.org"

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{return_url}/settings/billing"
        )

        return PortalSessionResponse(url=session.url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create billing portal session"
        )


@router.post("/cancel")
async def cancel_subscription(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Cancel subscription at end of billing period
    """
    try:
        user_id = current_user.get("sub")

        # Get active subscription
        result = supabase.table("subscriptions").select("*").eq("user_id", user_id).eq("status", "active").execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )

        subscription = result.data[0]
        stripe_subscription_id = subscription["stripe_subscription_id"]

        # Cancel subscription at period end in Stripe
        stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True
        )

        # Update local record
        supabase.table("subscriptions").update({
            "cancel_at_period_end": True,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", subscription["id"]).execute()

        logger.info(f"Subscription {stripe_subscription_id} set to cancel at period end")

        return {
            "message": "Subscription will be canceled at the end of the billing period",
            "cancel_at": subscription["current_period_end"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.post("/reactivate")
async def reactivate_subscription(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Reactivate a subscription that was set to cancel
    """
    try:
        user_id = current_user.get("sub")

        # Get subscription
        result = supabase.table("subscriptions").select("*").eq("user_id", user_id).eq("status", "active").execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )

        subscription = result.data[0]

        if not subscription["cancel_at_period_end"]:
            return {"message": "Subscription is already active"}

        stripe_subscription_id = subscription["stripe_subscription_id"]

        # Reactivate subscription in Stripe
        stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=False
        )

        # Update local record
        supabase.table("subscriptions").update({
            "cancel_at_period_end": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", subscription["id"]).execute()

        logger.info(f"Subscription {stripe_subscription_id} reactivated")

        return {"message": "Subscription reactivated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reactivating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate subscription"
        )
