"""
Drip campaign service for automated email sequences
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from supabase import Client

from .email_service import email_service
from ..config import settings

logger = logging.getLogger(__name__)


class DripCampaignService:
    """Service for managing automated email drip campaigns"""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.email_service = email_service

    async def create_free_scan_campaign(
        self,
        email: str,
        website_url: str,
        visibility_score: int,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new drip campaign for free scan users

        Args:
            email: User's email address
            website_url: Scanned website URL
            visibility_score: Visibility score from scan
            user_id: Optional user ID if registered

        Returns:
            Campaign details
        """
        try:
            # Check if user has email preferences set to receive marketing emails
            can_send = await self._can_send_marketing_email(email, user_id)
            if not can_send:
                logger.info(f"User {email} has opted out of marketing emails")
                return {"success": False, "reason": "user_opted_out"}

            # Check if campaign already exists for this email
            existing = self.supabase.table("drip_campaigns").select("*").eq(
                "email", email
            ).eq("campaign_type", "free_scan_conversion").eq(
                "status", "active"
            ).execute()

            if existing.data:
                logger.info(f"Active campaign already exists for {email}")
                return {
                    "success": False,
                    "reason": "campaign_exists",
                    "campaign_id": existing.data[0]["id"]
                }

            # Create campaign using database function
            result = self.supabase.rpc(
                "create_free_scan_campaign",
                {
                    "p_email": email,
                    "p_website_url": website_url,
                    "p_visibility_score": visibility_score,
                    "p_user_id": user_id
                }
            ).execute()

            campaign_id = result.data

            logger.info(f"Created drip campaign {campaign_id} for {email}")

            return {
                "success": True,
                "campaign_id": campaign_id,
                "email": email,
                "website_url": website_url,
                "visibility_score": visibility_score
            }

        except Exception as e:
            logger.error(f"Failed to create drip campaign: {e}")
            return {"success": False, "error": str(e)}

    async def process_pending_emails(self) -> Dict[str, Any]:
        """
        Process all pending drip campaign emails that are ready to send

        Returns:
            Processing statistics
        """
        try:
            # Get pending emails
            result = self.supabase.rpc("get_pending_drip_emails").execute()
            pending_emails = result.data

            if not pending_emails:
                logger.info("No pending drip emails to send")
                return {
                    "success": True,
                    "processed": 0,
                    "sent": 0,
                    "failed": 0
                }

            logger.info(f"Processing {len(pending_emails)} pending drip emails")

            sent_count = 0
            failed_count = 0

            for email_data in pending_emails:
                success = await self._send_drip_email(email_data)
                if success:
                    sent_count += 1
                else:
                    failed_count += 1

            logger.info(
                f"Processed {len(pending_emails)} emails: "
                f"{sent_count} sent, {failed_count} failed"
            )

            return {
                "success": True,
                "processed": len(pending_emails),
                "sent": sent_count,
                "failed": failed_count
            }

        except Exception as e:
            logger.error(f"Failed to process pending emails: {e}")
            return {
                "success": False,
                "error": str(e),
                "processed": 0,
                "sent": 0,
                "failed": 0
            }

    async def _send_drip_email(self, email_data: Dict[str, Any]) -> bool:
        """
        Send a single drip campaign email

        Args:
            email_data: Email data from database

        Returns:
            True if sent successfully
        """
        try:
            email_id = email_data["id"]
            email_type = email_data["email_type"]
            to_email = email_data["to_email"]
            subject = email_data["subject"]
            campaign_id = email_data["campaign_id"]

            # Check if user can receive this email
            can_send = await self._can_send_marketing_email(to_email)
            if not can_send:
                # Mark as unsubscribed
                self.supabase.table("drip_campaign_emails").update({
                    "status": "bounced",
                    "error_message": "User unsubscribed"
                }).eq("id", email_id).execute()

                # Update campaign status
                self.supabase.table("drip_campaigns").update({
                    "status": "unsubscribed"
                }).eq("id", campaign_id).execute()

                return False

            # Prepare template context
            context = {
                "user_name": to_email.split("@")[0],  # Simple extraction
                "website_url": email_data["website_url"],
                "visibility_score": email_data["visibility_score"],
                "dashboard_url": settings.app_url,
                "unsubscribe_url": await self._get_unsubscribe_url(to_email),
                "report_url": f"{settings.app_url}/reports/{email_data['website_url']}",
                "percentage_below": max(0, email_data["visibility_score"] - 10),
                "expiry_date": (datetime.now() + timedelta(days=2)).strftime("%B %d, %Y"),
                "week_start": datetime.now().strftime("%B %d"),
                "week_end": (datetime.now() + timedelta(days=7)).strftime("%B %d, %Y"),
                "competitor_count": 50,
                "competitor_avg_score": email_data["visibility_score"] + 15,
                "your_mentions": max(1, email_data["visibility_score"] // 10),
                "competitor_mentions": max(5, email_data["visibility_score"] // 5),
                "outranked_percentage": 100 - email_data["visibility_score"]
            }

            # Render and send email
            html_content = self.email_service._render_template(email_type, context)
            success = await self.email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content
            )

            if success:
                # Update email status
                self.supabase.table("drip_campaign_emails").update({
                    "status": "sent",
                    "sent_at": datetime.now().isoformat(),
                    "provider": self.email_service.provider
                }).eq("id", email_id).execute()

                # Schedule next email in sequence
                await self._schedule_next_email(email_data)

                # Track analytics
                await self._track_email_send(email_data, "sent")

                logger.info(f"Sent {email_type} email to {to_email}")
                return True
            else:
                # Update failed status
                retry_count = email_data.get("retry_count", 0) + 1
                self.supabase.table("drip_campaign_emails").update({
                    "status": "failed",
                    "error_message": "Failed to send",
                    "retry_count": retry_count
                }).eq("id", email_id).execute()

                logger.error(f"Failed to send {email_type} email to {to_email}")
                return False

        except Exception as e:
            logger.error(f"Error sending drip email: {e}")
            return False

    async def _schedule_next_email(self, current_email: Dict[str, Any]):
        """
        Schedule the next email in the drip sequence

        Args:
            current_email: Current email data
        """
        try:
            campaign_id = current_email["campaign_id"]
            step_number = current_email["step_number"]

            # Determine days until next email
            days_delay = {
                1: 2,  # Day 1 → Day 3 (2 days)
                2: 4,  # Day 3 → Day 7 (4 days)
                3: 7,  # Day 7 → Day 14 (7 days)
            }.get(step_number, 0)

            if days_delay > 0:
                self.supabase.rpc(
                    "schedule_next_drip_email",
                    {
                        "p_campaign_id": campaign_id,
                        "p_days_delay": days_delay
                    }
                ).execute()

        except Exception as e:
            logger.error(f"Failed to schedule next email: {e}")

    async def _can_send_marketing_email(
        self,
        email: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Check if user can receive marketing emails

        Args:
            email: Email address
            user_id: Optional user ID

        Returns:
            True if can send
        """
        try:
            # Check email preferences
            query = self.supabase.table("email_preferences").select("*")

            if user_id:
                query = query.eq("user_id", user_id)
            else:
                query = query.eq("email", email)

            result = query.execute()

            if not result.data:
                # No preferences set = can send
                return True

            prefs = result.data[0]

            # Check if unsubscribed from all
            if prefs.get("unsubscribed_all"):
                return False

            # Check if marketing emails are enabled
            if not prefs.get("marketing_emails", True):
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking email preferences: {e}")
            # Default to allowing email if check fails
            return True

    async def _get_unsubscribe_url(self, email: str) -> str:
        """
        Get unsubscribe URL for email

        Args:
            email: Email address

        Returns:
            Unsubscribe URL
        """
        try:
            result = self.supabase.table("email_preferences").select(
                "unsubscribe_token"
            ).eq("email", email).execute()

            if result.data:
                token = result.data[0]["unsubscribe_token"]
                return f"{settings.app_url}/unsubscribe?token={token}"
            else:
                # Create preferences with token
                new_prefs = self.supabase.table("email_preferences").insert({
                    "email": email
                }).execute()

                if new_prefs.data:
                    token = new_prefs.data[0]["unsubscribe_token"]
                    return f"{settings.app_url}/unsubscribe?token={token}"

        except Exception as e:
            logger.error(f"Error getting unsubscribe URL: {e}")

        # Fallback
        return f"{settings.app_url}/unsubscribe?email={email}"

    async def _track_email_send(self, email_data: Dict[str, Any], status: str):
        """
        Track email send in analytics

        Args:
            email_data: Email data
            status: Send status
        """
        try:
            self.supabase.table("email_analytics").insert({
                "campaign_email_id": email_data["id"],
                "email_type": email_data["email_type"],
                "to_email": email_data["to_email"],
                "subject": email_data["subject"],
                "sent_at": datetime.now().isoformat() if status == "sent" else None,
                "provider": self.email_service.provider
            }).execute()

        except Exception as e:
            logger.error(f"Failed to track email send: {e}")

    async def pause_campaign(self, campaign_id: str) -> bool:
        """
        Pause a drip campaign

        Args:
            campaign_id: Campaign ID

        Returns:
            True if paused successfully
        """
        try:
            self.supabase.table("drip_campaigns").update({
                "status": "paused",
                "paused_at": datetime.now().isoformat()
            }).eq("id", campaign_id).execute()

            logger.info(f"Paused campaign {campaign_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to pause campaign: {e}")
            return False

    async def resume_campaign(self, campaign_id: str) -> bool:
        """
        Resume a paused drip campaign

        Args:
            campaign_id: Campaign ID

        Returns:
            True if resumed successfully
        """
        try:
            self.supabase.table("drip_campaigns").update({
                "status": "active",
                "paused_at": None
            }).eq("id", campaign_id).execute()

            logger.info(f"Resumed campaign {campaign_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to resume campaign: {e}")
            return False

    async def get_campaign_stats(self) -> Dict[str, Any]:
        """
        Get drip campaign statistics

        Returns:
            Campaign statistics
        """
        try:
            # Get overall stats
            stats = self.supabase.table("drip_campaign_stats").select("*").execute()

            # Get email performance
            performance = self.supabase.table("email_performance").select("*").execute()

            return {
                "campaign_stats": stats.data,
                "email_performance": performance.data
            }

        except Exception as e:
            logger.error(f"Failed to get campaign stats: {e}")
            return {
                "campaign_stats": [],
                "email_performance": []
            }


# Background task runner
async def run_drip_campaign_scheduler(supabase_client: Client):
    """
    Background task to process drip campaign emails

    Should be run as a scheduled task (e.g., every 15 minutes)
    """
    service = DripCampaignService(supabase_client)

    while True:
        try:
            logger.info("Running drip campaign scheduler")
            result = await service.process_pending_emails()
            logger.info(f"Scheduler result: {result}")

            # Sleep for 15 minutes
            await asyncio.sleep(900)

        except Exception as e:
            logger.error(f"Error in drip campaign scheduler: {e}")
            await asyncio.sleep(60)  # Sleep for 1 minute on error
